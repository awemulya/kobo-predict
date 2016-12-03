from rest_framework import serializers
from rest_framework.reverse import reverse

from onadata.apps.fsforms.models import FieldSightXF
from onadata.apps.logger.models import XForm
from onadata.libs.utils.decorators import check_obj


class XFormListSerializer(serializers.ModelSerializer):

    class Meta:
        model = XForm
        fields = ('id', 'title')
