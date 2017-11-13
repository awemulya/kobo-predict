import json
from bson import json_util
from onadata.libs.utils.decorators import apply_form_field_names
from django.conf import settings
from formpack import FormPack
from onadata.apps.viewer.models.parsed_instance import dict_for_mongo, _encode_for_mongo, xform_instances
DEFAULT_LIMIT = 30000


def get_instances_for_field_sight_form(fieldsight_form_id, submission=None):
    query = {"$or":[{"_uuid":fieldsight_form_id}, {"fs_uuid":fieldsight_form_id}, {"_uuid":str(fieldsight_form_id)}, {"fs_uuid":str(fieldsight_form_id)}]}
    return settings.MONGO_DB.instances.find(query)
