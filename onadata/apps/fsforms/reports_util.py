from django.conf import settings
from formpack import FormPack
from onadata.apps.fsforms.models import FieldsightInstance, FieldSightXF


def get_instances_for_field_sight_form(fieldsight_form_id, submission=None):

    # instance_id = FieldsightInstance.objects.filter(fsxform__id=fieldsight_form_id)[0].instance.id\
    #     if FieldsightInstance.objects.filter(fsxform__id=fieldsight_form_id).exists() else None

    query = {'_uuid': fieldsight_form_id, '_deleted_at': {'$exists': False}}
    if submission:
        query['_id'] = submission
    return settings.MONGO_DB.instances.find(query)


def get_instance_form_data(fieldsight_form_id, instance_id):

    query = {'_id': instance_id, '_deleted_at': {'$exists': False}}
    return settings.MONGO_DB.instances.find(query)


def build_formpack(id_string, xform):
    schema = {
        "id_string": id_string,
        "version": 'v1',
        "content": xform.to_kpi_content_schema(),
    }
    return  xform, FormPack([schema], xform.title)


def build_export_context(request,xform, id_string):

    hierarchy_in_labels = request.REQUEST.get('hierarchy_in_labels', None)
    group_sep = request.REQUEST.get('group_sep', '/')

    xform, formpack = build_formpack(id_string, xform)

    translations = formpack.available_translations
    lang = request.REQUEST.get('lang', None) or next(iter(translations), None)

    options = {'versions': 'v1',
               'group_sep': group_sep,
               'lang': lang,
               'hierarchy_in_labels': hierarchy_in_labels,
               # 'copy_fields': ('_id', '_uuid', '_submission_time''),
               'copy_fields': ('_id','_submission_time','medias'),
               # 'force_index': True
               'force_index': False
               }

    return {
        'id_string': id_string,
        'languages': translations,
        'headers_lang': lang,
        'formpack': formpack,
        'xform': xform,
        'group_sep': group_sep,
        'lang': lang,
        'hierarchy_in_labels': hierarchy_in_labels,
        'export': formpack.export(**options)
    }



def get_xform_and_perms(fsxf_id, request):
    fs_xform = FieldSightXF.objects.get(pk=fsxf_id)
    xform = fs_xform.xf
    is_owner = xform.user == request.user
    can_edit = True
    can_view = can_edit or\
        request.user.has_perm('logger.view_xform', xform)
    return [xform, is_owner, can_edit, can_view]