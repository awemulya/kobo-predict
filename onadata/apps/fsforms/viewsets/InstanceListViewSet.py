from django.utils import six
from rest_framework.response import Response

from onadata.apps.api.viewsets.data_viewset import DataViewSet
from onadata.libs.serializers.data_serializer import DataListSerializer, DataSerializer

class InstanceListViewSet(DataViewSet):

    def filter_queryset(self, queryset, view=None):
        qs = super(InstanceListViewSet, self).filter_queryset(queryset)
        pk = self.kwargs.get(self.lookup_field)
        field_sight_form = self.request.query_params.get('field_sight_form', None)

        if field_sight_form and isinstance(field_sight_form, six.string_types):
            field_sight_form = field_sight_form.split(',')
            qs = qs.filter(field_sight_form__pk__in=field_sight_form).distinct()
            print(qs)

        if pk:
            try:
                int(pk)
            except ValueError:
                if pk == self.public_data_endpoint:
                    qs = self._get_public_forms_queryset()
                else:
                    raise ParseError(_(u"Invalid pk %(pk)s" % {'pk': pk}))
            else:
                qs = self._filtered_or_shared_qs(qs, pk)

        return qs

    def list(self, request, *args, **kwargs):
        lookup_field = self.lookup_field
        # lookup = self.kwargs.get(lookup_field)

        if lookup_field not in kwargs.keys() and self.request.query_params.get('field_sight_form'):
            self.object_list = self.filter_queryset(self.get_queryset())
            serializer = DataListSerializer(self.object_list, many=True)

            return Response(serializer.data)
        else:
            self.object_list = self.filter_queryset(self.get_queryset())
            serializer = self.get_serializer(self.object_list, many=True)
            return Response(serializer.data)



        # if lookup == self.public_data_endpoint:
        #     self.object_list = self._get_public_forms_queryset()
        #
        #     page = self.paginate_queryset(self.object_list)
        #     if page is not None:
        #         serializer = self.get_pagination_serializer(page)
        #     else:
        #         serializer = DataListSerializer(self.object_list, many=True)
        #
        #     return Response(serializer.data)
        #
        # xform = self.get_object()
        # query = request.GET.get("query", {})
        # export_type = kwargs.get('format')
        # if export_type is None or export_type in ['json']:
        #     # perform default viewset retrieve, no data export
        #
        #     # With DRF ListSerializer are automatically created and wraps
        #     # everything in a list. Since this returns a list
        #     # # already, we unwrap it.
        #     res = super(InstanceListViewSet, self).list(request, *args, **kwargs)
        #     res.data = res.data[0]
        #     return res
        #
        # return custom_response_handler(request, xform, query, export_type)
