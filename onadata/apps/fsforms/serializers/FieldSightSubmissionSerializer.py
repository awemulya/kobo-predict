from django.utils.translation import ugettext as _
from onadata.libs.serializers.data_serializer import SubmissionSerializer


class FieldSightSubmissionSerializer(SubmissionSerializer):
    def to_representation(self, obj):
        if not hasattr(obj, 'xform'):
            return super(FieldSightSubmissionSerializer, self).to_representation(obj)

        return {
            'message': _("Successful submission."),
            'formid': obj.xform.id_string,
            'encrypted': obj.xform.encrypted,
            'instanceID': u'uuid:%s' % obj.uuid,
            'finstanceID': u'%s' % obj.fieldsight_instance.id,
            'submissionDate': obj.date_created.isoformat(),
            'markedAsCompleteDate': obj.date_modified.isoformat()
        }
