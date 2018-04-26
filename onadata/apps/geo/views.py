from __future__ import unicode_literals
from django.shortcuts import get_object_or_404
from django.views.generic import ListView, View
from django.views.generic.edit import CreateView, UpdateView
from django.http import JsonResponse
from django.core.serializers import serialize
from django.core.urlresolvers import reverse
from onadata.apps.fieldsight.models import Organization
from .models import GeoLayer

import json


class GeoLayersView(ListView):
    model = GeoLayer
    paginate_by = 51

    def get_queryset(self):
        organization = get_object_or_404(Organization, id=self.kwargs['org_pk'])
        return GeoLayer.objects.filter(organization=organization)

    def get_context_data(self, **kwargs):
        context = super(GeoLayersView, self).get_context_data(**kwargs)
        context['organization'] = get_object_or_404(Organization, id=self.kwargs['org_pk'])
        return context


class GeoLayerFormView(object):
    model = GeoLayer
    fields = ['title', 'level', 'title_prop', 'code_prop', 'geo_shape_file',
              'tolerance']

    def get_context_data(self, **kwargs):
        context = super(GeoLayerFormView, self).get_context_data(**kwargs)
        context['organization'] = get_object_or_404(Organization, id=self.kwargs['org_pk'])
        return context

    def get_success_url(self):
        return reverse('fieldsight:geo-layers', kwargs={'org_pk': self.kwargs['org_pk']})

    def form_valid(self, form):
        organization = get_object_or_404(Organization, id=self.kwargs['org_pk'])
        form.instance.organization = organization
        form.instance.stale_areas = True
        return super(GeoLayerFormView, self).form_valid(form)


class GeoLayerCreateView(GeoLayerFormView, CreateView):
    pass


class GeoLayerUpdateView(GeoLayerFormView, UpdateView):
    pass


class GeoJsonView(View):
    def get(self, request, pk):
        geo_layer = get_object_or_404(GeoLayer, id=pk)
        return JsonResponse(json.loads(serialize(
            'geojson',
            geo_layer.geo_areas.all(),
            geometry_field='geometry',
            fields=('id', 'title', 'code', 'geometry'),
        )))
