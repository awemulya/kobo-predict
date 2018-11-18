import os
import traceback
import requests
import zipfile

from tempfile import NamedTemporaryFile
from xml.dom import minidom

from django.conf import settings
from django.core.files.storage import get_storage_class
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.mail import mail_admins
from django.utils.translation import ugettext as _

from onadata.libs.utils import common_tags


SLASH = u"/"


class MyError(Exception):
    pass


class EnketoError(Exception):
    pass


def image_urls_for_form(xform):
    return sum([
        image_urls(s) for s in xform.instances.all()
    ], [])


def get_path(path, suffix):
    fileName, fileExtension = os.path.splitext(path)
    return fileName + suffix + fileExtension


def image_urls(instance):
    default_storage = get_storage_class()()
    urls = []
    suffix = settings.THUMB_CONF['medium']['suffix']
    for a in instance.attachments.all():
        if default_storage.exists(get_path(a.media_file.name, suffix)):
            url = default_storage.url(
                get_path(a.media_file.name, suffix))
        else:
            url = a.media_file.url
        urls.append(url)
    return urls


def parse_xform_instance(xml_str):
    """
    'xml_str' is a str object holding the XML of an XForm
    instance. Return a python object representation of this XML file.
    """
    xml_obj = minidom.parseString(xml_str)
    root_node = xml_obj.documentElement
    # go through the xml object creating a corresponding python object
    # NOTE: THIS WILL DESTROY ANY DATA COLLECTED WITH REPEATABLE NODES
    # THIS IS OKAY FOR OUR USE CASE, BUT OTHER USERS SHOULD BEWARE.
    survey_data = dict(_path_value_pairs(root_node))
    assert len(list(_all_attributes(root_node))) == 1, \
        _(u"There should be exactly one attribute in this document.")
    survey_data.update({
        common_tags.XFORM_ID_STRING: root_node.getAttribute(u"id"),
        common_tags.INSTANCE_DOC_NAME: root_node.nodeName,
    })
    return survey_data


def _path(node):
    n = node
    levels = []
    while n.nodeType != n.DOCUMENT_NODE:
        levels = [n.nodeName] + levels
        n = n.parentNode
    return SLASH.join(levels[1:])


def _path_value_pairs(node):
    """
    Using a depth first traversal of the xml nodes build up a python
    object in parent that holds the tree structure of the data.
    """
    if len(node.childNodes) == 0:
        # there's no data for this leaf node
        yield _path(node), None
    elif len(node.childNodes) == 1 and \
            node.childNodes[0].nodeType == node.TEXT_NODE:
        # there is data for this leaf node
        yield _path(node), node.childNodes[0].nodeValue
    else:
        # this is an internal node
        for child in node.childNodes:
            for pair in _path_value_pairs(child):
                yield pair


def _all_attributes(node):
    """
    Go through an XML document returning all the attributes we see.
    """
    if hasattr(node, "hasAttributes") and node.hasAttributes():
        for key in node.attributes.keys():
            yield key, node.getAttribute(key)
    for child in node.childNodes:
        for pair in _all_attributes(child):
            yield pair


def report_exception(subject, info, exc_info=None):
    if exc_info:
        cls, err = exc_info[:2]
        info += _(u"Exception in request: %(class)s: %(error)s") \
            % {'class': cls.__name__, 'error': err}
        info += u"".join(traceback.format_exception(*exc_info))

    if settings.DEBUG:
        print subject
        print info
    else:
        mail_admins(subject=subject, message=info)


def django_file(path, field_name, content_type):
    # adapted from here: http://groups.google.com/group/django-users/browse_th\
    # read/thread/834f988876ff3c45/
    f = open(path)
    return InMemoryUploadedFile(
        file=f,
        field_name=field_name,
        name=f.name,
        content_type=content_type,
        size=os.path.getsize(path),
        charset=None
    )


def export_def_from_filename(filename):
    # TODO fix circular import and move to top
    from onadata.apps.viewer.models.export import Export
    path, ext = os.path.splitext(filename)
    ext = ext[1:]
    # try get the def from extension
    mime_type = Export.EXPORT_MIMES[ext]
    return ext, mime_type


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def enketo_ur_oldl(form_url, id_string, instance_xml=None,
               instance_id=None, return_url=None):
    if not hasattr(settings, 'ENKETO_URL')\
            and not hasattr(settings, 'ENKETO_API_SURVEY_PATH'):
        return False

    url = settings.ENKETO_URL + settings.ENKETO_API_SURVEY_PATH

    values = {
        'form_id': id_string,
        'server_url': form_url
    }
    if instance_id is not None and instance_xml is not None:
        url = settings.ENKETO_URL + settings.ENKETO_API_INSTANCE_PATH
        values.update({
            'instance': instance_xml,
            'instance_id': instance_id,
            'return_url': return_url
        })
    req = requests.post(url, data=values,
                        auth=(settings.ENKETO_API_TOKEN, ''), verify=False)
    if req.status_code in [200, 201]:
        try:
            response = req.json()
        except ValueError:
            pass
        else:
            if 'edit_url' in response:
                return response['edit_url']
            if settings.ENKETO_OFFLINE_SURVEYS and ('offline_url' in response):
                return response['offline_url']
            if 'url' in response:
                return response['url']
    else:
        try:
            response = req.json()
        except ValueError:
            pass
        else:
            if 'message' in response:
                raise EnketoError(response['message'])
    return False


def enketo_url(form_url, id_string, instance_xml=None,
               instance_id=None, return_url=None, instance_attachments=None):
    if not hasattr(settings, 'ENKETO_URL')\
            and not hasattr(settings, 'ENKETO_API_SURVEY_PATH'):
        return False

    if instance_attachments is None:
        instance_attachments = {}

    url = settings.ENKETO_URL + settings.ENKETO_API_SURVEY_PATH

    values = {
        'form_id': id_string,
        'server_url': form_url
    }
    if instance_id is not None and instance_xml is not None:
        url = settings.ENKETO_URL + '/api/v2/instance'
        print(url)
        print(settings.KOBOCAT_URL)
        # url = settings.ENKETO_URL + settings.ENKETO_API_INSTANCE_PATH
        values.update({
            'instance': instance_xml,
            'instance_id': instance_id,
            'return_url': return_url
        })
        for key, value in instance_attachments.iteritems():
            values.update({
                'instance_attachments[' + key + ']': value
            })
    print(values)
    raw_values = {u'instance_attachments[Screenshot from 2018-04-04 12-54-06_T0uwOcu.png]': 'http://localhost:8001/media/Promisha/attachments/Screenshot%20from%202018-04-04%2012-54-06_T0uwOcu.png', u'instance_attachments[farcry.webp]': 'http://localhost:8001/media/Promisha/attachments/farcry.webp', 'form_id': u'aq6BX3GMavXWWv5NdCcapK', u'instance_attachments[Screenshot from 2018-03-21 08-45-51_aOl5e6q.png]': 'http://localhost:8001/media/Promisha/attachments/Screenshot%20from%202018-03-21%2008-45-51_aOl5e6q.png', 'server_url': u'http://localhost:8001/Promisha', 'instance_id': u'5e5692d1-39eb-4284-859c-b67f1b0814f6', 'instance': u'<aq6BX3GMavXWWv5NdCcapK_qkk70Ya xmlns:jr="http://openrosa.org/javarosa" xmlns:orx="http://openrosa.org/xforms" id="aq6BX3GMavXWWv5NdCcapK" version="7960">\r\n          <formhub>\r\n            <uuid>fa12a6544eed4a84ae548ebfafd4e2d6</uuid>\r\n          </formhub>\r\n          <group_ringbeam_common>\r\n            <date>2018-09-05</date>\r\n            <name_of_data_collector>eee</name_of_data_collector>\r\n            <is_ring_beam_well_leveled_using_stone_and_sand_cement_1_5_mortar_throughout_the_building_>no</is_ring_beam_well_leveled_using_stone_and_sand_cement_1_5_mortar_throughout_the_building_>\r\n            <the_gable_should_be_demolished_upto_bottom_of_ring_beam_level_need_to_check_the_position_of_eaves_and_also_sometime_the_slope_of_rafter_if_it_allows_us_to_cast_6inch_deep_ring_beam_/>\r\n            <check_whether_the_rafter_is_6_higher_than_the_levelled_surface_or_not_if_not_we_need_to_raise_the_rafter_>no</check_whether_the_rafter_is_6_higher_than_the_levelled_surface_or_not_if_not_we_need_to_raise_the_rafter_>\r\n            <for_the_proper_hold_of_cgi_strap_and_rafter_we_sometimes_need_to_add_an_extra_piece_of_7mm_rebar_in_accordance_to_the_rafter_width/>\r\n            <is_there_4_nos_of_12mm_rebar_at_edges_and_2_nos_of_10mm_rebar_at_the_centre_as_longitudinal_reinforcement_with_7mm_rebar_stirrups_on_ring_beam_>no</is_there_4_nos_of_12mm_rebar_at_edges_and_2_nos_of_10mm_rebar_at_the_centre_as_longitudinal_reinforcement_with_7mm_rebar_stirrups_on_ring_beam_>\r\n            <is_there12mm_threaded_rod_spaced_at_2_feet_c_c_>no</is_there12mm_threaded_rod_spaced_at_2_feet_c_c_>\r\n            <the_threaded_rod_to_be_placed_at_the_inner_side_of_the_longitudinal_wall_and_outer_side_of_the_transverse_wall_/>\r\n            <please_upload_photos_depicting_rebar_arrangement/>\r\n            <photo_mandatory_ type="file">Screenshot from 2018-04-30 09-43-32-10_23_17.png</photo_mandatory_>\r\n            <photo type="file">Screenshot from 2018-04-10 14-46-53-10_23_21.png</photo>\r\n            <photo_0 type="file">farcry-10_23_24.webp</photo_0>\r\n            <is_the_concrete_at_least_m20_grade_or_mix_ratio_1_1_5_3_>no</is_the_concrete_at_least_m20_grade_or_mix_ratio_1_1_5_3_>\r\n            <is_the_concrete_cover_maintained_>no</is_the_concrete_cover_maintained_>\r\n            <is_the_concrete_smooth_without_honeycombing_without_any_exposed_rebars_>no</is_the_concrete_smooth_without_honeycombing_without_any_exposed_rebars_>\r\n            <is_the_rebar_high_strength_deformed_bars_with_fy_415mpa_500mpa_with_overlap_lengths_60_>no</is_the_rebar_high_strength_deformed_bars_with_fy_415mpa_500mpa_with_overlap_lengths_60_>\r\n            <Which_Retofit_types_is_being_i>light_weight_retrofit</Which_Retofit_types_is_being_i>\r\n          </group_ringbeam_common>\r\n          <group_ringbeam1>\r\n            <is_there_presence_of_one_12_mm_dia_u_hook_dowel_bar_at_mid_and_2_nos_at_corner_strongback_connecting_ring_beam_/>\r\n            <need_to_predetermine_the_position_of_strongback_and_also_position_of_u_hook_to_connect_with_strong_back_s_reinforcement_/>\r\n            <is_there_a_16mm_dia_threaded_rod_placed_in_the_ringbeam_connecting_wooden_strongback_>no</is_there_a_16mm_dia_threaded_rod_placed_in_the_ringbeam_connecting_wooden_strongback_>\r\n            <need_to_predetermine_the_position_of_threaded_rod_so_that_it_is_aligned_to_the_centre_of_strongback_/>\r\n          </group_ringbeam1>\r\n          <photos_for_ring_beam_inspection type="file">Screenshot from 2018-04-04 12-54-06-10_23_36.png</photos_for_ring_beam_inspection>\r\n          <Photo_1 type="file">Screenshot from 2018-03-21 08-46-09-10_23_39.png</Photo_1>\r\n          <Photo_1_001 type="file">Screenshot from 2018-03-21 08-45-51-10_23_42.png</Photo_1_001>\r\n          <Photo_1_001_001 type="file">Screenshot from 2018-03-21 08-46-09-10_23_46.png</Photo_1_001_001>\r\n          <comments>eeee</comments>\r\n          <start>2018-09-28T10:23:02.544+06:45</start>\r\n          <end>2018-09-28T10:23:02.547+06:45</end>\r\n          <__version__>7960</__version__>\r\n          <meta>\r\n            <instanceID>uuid:d26e7e81-b04c-470e-aae7-d8425b329726</instanceID>\r\n          </meta>\r\n        </aq6BX3GMavXWWv5NdCcapK_qkk70Ya>', u'instance_attachments[Screenshot from 2018-04-10 14-46-53_WabHsLu.png]': 'http://localhost:8001/media/Promisha/attachments/Screenshot%20from%202018-04-10%2014-46-53_WabHsLu.png', u'instance_attachments[Screenshot from 2018-03-21 08-46-09.png]': 'http://localhost:8001/media/Promisha/attachments/Screenshot%20from%202018-03-21%2008-46-09.png', u'instance_attachments[Screenshot from 2018-04-30 09-43-32_ydLWZl8.png]': 'http://localhost:8001/media/Promisha/attachments/Screenshot%20from%202018-04-30%2009-43-32_ydLWZl8.png', 'return_url': 'http://localhost:8001/Promisha/forms/aq6BX3GMavXWWv5NdCcapK/instance#/42126', u'instance_attachments[Screenshot from 2018-03-21 08-46-09_d0ContT.png]': 'http://localhost:8001/media/Promisha/attachments/Screenshot%20from%202018-03-21%2008-46-09_d0ContT.png'}

    values =  {u'instance_attachments[Screenshot from 2018-04-04 12-54-06_T0uwOcu.png]': 'http://localhost:8001/media/Promisha/attachments/Screenshot%20from%202018-04-04%2012-54-06_T0uwOcu.png', u'instance_attachments[farcry.webp]': 'http://localhost:8001/media/Promisha/attachments/farcry.webp', 'form_id': u'aq6BX3GMavXWWv5NdCcapK', u'instance_attachments[Screenshot from 2018-03-21 08-45-51_aOl5e6q.png]': 'http://localhost:8001/media/Promisha/attachments/Screenshot%20from%202018-03-21%2008-45-51_aOl5e6q.png', 'server_url': u'http://localhost:8001/Promisha', 'instance_id': u'5e5692d1-39eb-4284-859c-b67f1b0814f6', 'instance': u'<aq6BX3GMavXWWv5NdCcapK_qkk70Ya xmlns:jr="http://openrosa.org/javarosa" xmlns:orx="http://openrosa.org/xforms" id="aq6BX3GMavXWWv5NdCcapK" version="7960">\r\n          <formhub>\r\n            <uuid>fa12a6544eed4a84ae548ebfafd4e2d6</uuid>\r\n          </formhub>\r\n          <group_ringbeam_common>\r\n            <date>2018-09-05</date>\r\n            <name_of_data_collector>eee</name_of_data_collector>\r\n            <is_ring_beam_well_leveled_using_stone_and_sand_cement_1_5_mortar_throughout_the_building_>no</is_ring_beam_well_leveled_using_stone_and_sand_cement_1_5_mortar_throughout_the_building_>\r\n            <the_gable_should_be_demolished_upto_bottom_of_ring_beam_level_need_to_check_the_position_of_eaves_and_also_sometime_the_slope_of_rafter_if_it_allows_us_to_cast_6inch_deep_ring_beam_/>\r\n            <check_whether_the_rafter_is_6_higher_than_the_levelled_surface_or_not_if_not_we_need_to_raise_the_rafter_>no</check_whether_the_rafter_is_6_higher_than_the_levelled_surface_or_not_if_not_we_need_to_raise_the_rafter_>\r\n            <for_the_proper_hold_of_cgi_strap_and_rafter_we_sometimes_need_to_add_an_extra_piece_of_7mm_rebar_in_accordance_to_the_rafter_width/>\r\n            <is_there_4_nos_of_12mm_rebar_at_edges_and_2_nos_of_10mm_rebar_at_the_centre_as_longitudinal_reinforcement_with_7mm_rebar_stirrups_on_ring_beam_>no</is_there_4_nos_of_12mm_rebar_at_edges_and_2_nos_of_10mm_rebar_at_the_centre_as_longitudinal_reinforcement_with_7mm_rebar_stirrups_on_ring_beam_>\r\n            <is_there12mm_threaded_rod_spaced_at_2_feet_c_c_>no</is_there12mm_threaded_rod_spaced_at_2_feet_c_c_>\r\n            <the_threaded_rod_to_be_placed_at_the_inner_side_of_the_longitudinal_wall_and_outer_side_of_the_transverse_wall_/>\r\n            <please_upload_photos_depicting_rebar_arrangement/>\r\n            <photo_mandatory_ type="file">Screenshot from 2018-04-30 09-43-32_ydLWZl8.png</photo_mandatory_>\r\n            <photo type="file">Screenshot from 2018-04-10 14-46-53_WabHsLu.png</photo>\r\n            <photo_0 type="file">farcry.webp</photo_0>\r\n            <is_the_concrete_at_least_m20_grade_or_mix_ratio_1_1_5_3_>no</is_the_concrete_at_least_m20_grade_or_mix_ratio_1_1_5_3_>\r\n            <is_the_concrete_cover_maintained_>no</is_the_concrete_cover_maintained_>\r\n            <is_the_concrete_smooth_without_honeycombing_without_any_exposed_rebars_>no</is_the_concrete_smooth_without_honeycombing_without_any_exposed_rebars_>\r\n            <is_the_rebar_high_strength_deformed_bars_with_fy_415mpa_500mpa_with_overlap_lengths_60_>no</is_the_rebar_high_strength_deformed_bars_with_fy_415mpa_500mpa_with_overlap_lengths_60_>\r\n            <Which_Retofit_types_is_being_i>light_weight_retrofit</Which_Retofit_types_is_being_i>\r\n          </group_ringbeam_common>\r\n          <group_ringbeam1>\r\n            <is_there_presence_of_one_12_mm_dia_u_hook_dowel_bar_at_mid_and_2_nos_at_corner_strongback_connecting_ring_beam_/>\r\n            <need_to_predetermine_the_position_of_strongback_and_also_position_of_u_hook_to_connect_with_strong_back_s_reinforcement_/>\r\n            <is_there_a_16mm_dia_threaded_rod_placed_in_the_ringbeam_connecting_wooden_strongback_>no</is_there_a_16mm_dia_threaded_rod_placed_in_the_ringbeam_connecting_wooden_strongback_>\r\n            <need_to_predetermine_the_position_of_threaded_rod_so_that_it_is_aligned_to_the_centre_of_strongback_/>\r\n          </group_ringbeam1>\r\n          <photos_for_ring_beam_inspection type="file">Screenshot from 2018-04-04 12-54-06_T0uwOcu.png</photos_for_ring_beam_inspection>\r\n          <Photo_1 type="file">Screenshot from 2018-03-21 08-46-09_d0ContT.png</Photo_1>\r\n          <Photo_1_001 type="file">Screenshot from 2018-03-21 08-45-51_aOl5e6q.png</Photo_1_001>\r\n          <Photo_1_001_001 type="file">Screenshot from 2018-03-21 08-46-09_d0ContT.png</Photo_1_001_001>\r\n          <comments>eeee</comments>\r\n          <start>2018-09-28T10:23:02.544+06:45</start>\r\n          <end>2018-09-28T10:23:02.547+06:45</end>\r\n          <__version__>7960</__version__>\r\n          <meta>\r\n            <instanceID>uuid:d26e7e81-b04c-470e-aae7-d8425b329726</instanceID>\r\n          </meta>\r\n        </aq6BX3GMavXWWv5NdCcapK_qkk70Ya>', u'instance_attachments[Screenshot from 2018-04-10 14-46-53_WabHsLu.png]': 'http://localhost:8001/media/Promisha/attachments/Screenshot%20from%202018-04-10%2014-46-53_WabHsLu.png', u'instance_attachments[Screenshot from 2018-03-21 08-46-09.png]': 'http://localhost:8001/media/Promisha/attachments/Screenshot%20from%202018-03-21%2008-46-09.png', u'instance_attachments[Screenshot from 2018-04-30 09-43-32_ydLWZl8.png]': 'http://localhost:8001/media/Promisha/attachments/Screenshot%20from%202018-04-30%2009-43-32_ydLWZl8.png', 'return_url': 'http://localhost:8001/Promisha/forms/aq6BX3GMavXWWv5NdCcapK/instance#/42126', u'instance_attachments[Screenshot from 2018-03-21 08-46-09_d0ContT.png]': 'http://localhost:8001/media/Promisha/attachments/Screenshot%20from%202018-03-21%2008-46-09_d0ContT.png'}

    req = requests.post(url, data=values,
                        auth=(settings.ENKETO_API_TOKEN, ''), verify=False)
    if req.status_code in [200, 201]:
        try:
            response = req.json()
        except ValueError:
            pass
        else:
            if 'edit_url' in response:
                print(response['edit_url'])
                return response['edit_url']
            if settings.ENKETO_OFFLINE_SURVEYS and ('offline_url' in response):
                return response['offline_url']
            if 'url' in response:
                return response['url']
    else:
        try:
            response = req.json()
        except ValueError:
            pass
        else:
            if 'message' in response:
                raise EnketoError(response['message'])
    return False


def create_attachments_zipfile(attachments, temporary_file=None):
    if not temporary_file:
        temporary_file = NamedTemporaryFile()

    storage = get_storage_class()()
    with zipfile.ZipFile(temporary_file, 'w', zipfile.ZIP_STORED, allowZip64=True) as zip_file:
        for attachment in attachments:
            if storage.exists(attachment.media_file.name):
                try:
                    with storage.open(attachment.media_file.name, 'rb') as source_file:
                        zip_file.writestr(attachment.media_file.name, source_file.read())
                except Exception, e:
                    report_exception("Error adding file \"{}\" to archive.".format(attachment.media_file.name), e)

    # Be kind; rewind.
    temporary_file.seek(0)

    return temporary_file


def _get_form_url(request, username, protocol='https'):
    if settings.TESTING_MODE:
        http_host = settings.TEST_HTTP_HOST
        username = settings.TEST_USERNAME
    else:
        http_host = request.META.get('HTTP_HOST', 'ona.io')

    # In case INTERNAL_DOMAIN_NAME is equal to PUBLIC_DOMAIN_NAME,
    # configuration doesn't use docker internal network.
    # Don't overwrite `protocol.
    is_call_internal = settings.KOBOCAT_INTERNAL_HOSTNAME == http_host and \
                       settings.KOBOCAT_PUBLIC_HOSTNAME != http_host

    # Make sure protocol is enforced to `http` when calling `kc` internally
    protocol = "http" #if is_call_internal else protocol

    return '%s://%s/%s' % (protocol, http_host, username)


def get_enketo_edit_url(request, instance, return_url):
    form_url = _get_form_url(request,
                             request.user.username,
                             settings.ENKETO_PROTOCOL)
    url = enketo_url(
        form_url, instance.xform.id_string, instance_xml=instance.xml,
        instance_id=instance.uuid, return_url=return_url)
    return url
