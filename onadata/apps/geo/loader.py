from django.contrib.gis.gdal import DataSource
from django.contrib.gis.geos import GEOSGeometry
from django.conf import settings
from django.db.models import Q

from .models import GeoLayer, GeoArea

import os
import tempfile


def _save_geo_area(geo_layer, feature):
    title = None
    code = None

    if geo_layer.title_prop:
        title = feature.get(geo_layer.title_prop)
    if geo_layer.code_prop:
        code = feature.get(geo_layer.code_prop)

    title = title or ''

    geo_area = GeoArea.objects.filter(
        Q(code=None, title=title) | Q(code=code),
        geo_layer=geo_layer
    ).first()

    if not geo_area:
        geo_area = GeoArea()

    geo_area.title = title
    geo_area.code = code if code else title
    geo_area.geo_layer = geo_layer

    geom = feature.geom
    geom = GEOSGeometry(geom.wkt).simplify(
        tolerance=geo_layer.tolerance,
        preserve_topology=True,
    )

    geo_area.geometry = geom
    feature_names = [f.decode('utf-8') for f in feature.fields]

    geo_area.save()
    return geo_area


def load_areas(geo_layer):
    geo_shape_file = geo_layer.geo_shape_file

    if not geo_shape_file:
        geo_layer.stale_areas = False
        geo_layer.save()
        return

    # Create temporary file with same content
    # This is necessary in server where the file is
    # originally in s3 server and GDAL expects file in local
    # disk.
    # Then load data from that file
    filename, extension = os.path.splitext(geo_shape_file.file.name)
    f = tempfile.NamedTemporaryFile(suffix=extension,
                                    dir=settings.BASE_DIR)
    f.write(geo_shape_file.file.read())

    # Flush the file before reading it with GDAL
    # Otherwise, for small files, GDAL may attempt to read before
    # the write is complete and will raise an exception.
    f.flush()

    if extension == '.zip':
        with tempfile.TemporaryDirectory(
            dir=settings.BASE_DIR
        ) as tmpdirname:
            zipfile.ZipFile(f.name, 'r').extractall(tmpdirname)
            files = os.listdir(tmpdirname)
            shape_file = next((f for f in files if f.endswith('.shp')),
                              None)
            data_source = DataSource(os.path.join(tmpdirname, shape_file))
    else:
        data_source = DataSource(f.name)

    f.close()


    # If more than one layer exists, extract from the first layer
    if data_source.layer_count == 1:
        layer = data_source[0]

        added_areas = []
        for feature in layer:
            # Each feature is a geo area
            geo_area = _save_geo_area(geo_layer, feature)
            added_areas.append(geo_area.id)

        # Delete all previous geo areas that have not been added
        GeoArea.objects.filter(
            geo_layer=geo_layer,
        ).exclude(id__in=added_areas).delete()

    geo_layer.stale_areas = False
    geo_layer.save()
