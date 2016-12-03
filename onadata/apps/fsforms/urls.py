from django.conf.urls import url, include
from rest_framework import routers

from onadata.apps.fsforms.viewsets.FieldSightXformViewset import FieldSightXFormViewSet
from onadata.apps.fsforms.viewsets.ScheduleViewset import ScheduleViewset
from onadata.apps.fsforms.viewsets.AssignedXFormListApiViewSet import AssignedXFormListApi
from onadata.apps.fsforms.viewsets.FSXFormSubmissionApiViewset import FSXFormSubmissionApi
from onadata.apps.fsforms.viewsets.GroupsViewset import GroupViewSet
from onadata.apps.fsforms.viewsets.SiteFormsViewset import SiteFormViewSet
from onadata.apps.fsforms.viewsets.StageViewset import StageViewSet
from onadata.apps.fsforms.viewsets.XformsViewset import XFormViewSet
from .views import (
        LibraryFormsListView,
        FormsListView,
        GroupListView,
        GroupCreateView,
        GroupUpdateView,
        StageListView,
        StageUpdateView,
        StageCreateView,
        add_sub_stage,
        stage_details,
        stage_add_form,
        ScheduleListView,
        ScheduleCreateView,
        ScheduleUpdateView,
        assign, fill_form_type,
        fill_details_stage,
        fill_details_schedule,
        schedule_add_form,
        AssignedFormsListView,
        html_export, instance, show, api, download_jsonform, delete_data, data_view)

# router = MultiLookupRouter(trailing_slash=False)
router = routers.DefaultRouter()
router.register(r'api/groups', GroupViewSet)
router.register(r'api/stage', StageViewSet)
router.register(r'api/schedule', ScheduleViewset)
router.register(r'api/fsxform', FieldSightXFormViewSet)


urlpatterns = [
        url(r'^$', LibraryFormsListView.as_view(), name='library-forms-list'),
        # url(r'^$', LibraryFormsListView.as_view(), name='library-forms-list'),
        url(r'^assigned/$', FormsListView.as_view(), name='forms-list'),
        # assigned form list to a user(site supervisor)
        url(r'^assigned-form-list/$', AssignedFormsListView.as_view(), name='assigned-form-list'),

        url(r'^group/$', GroupListView.as_view(), name='group-list'),
        url(r'^group/add/$', GroupCreateView.as_view(), name='group-add'),
        url(r'^group/(?P<pk>\d+)/$', GroupUpdateView.as_view(), name='group-edit'),

        url(r'^stage/$', StageListView.as_view(), name='stage-list'),
        url(r'^stage/add/$', StageCreateView.as_view(), name='stage-add'),
        url(r'^stage/(?P<pk>\d+)/$', StageUpdateView.as_view(), name='stage-edit'),
        url(r'^stage-add-sub-stage/(?P<pk>\d+)/$', add_sub_stage, name='stage-add-sub-stage'),
        url(r'^stage-detail/(?P<pk>\d+)/$', stage_details, name='stage-detail'),
        url(r'^stage-add-form/(?P<pk>\d+)/$', stage_add_form, name='stage-add-form'),

        url(r'^schedule/$', ScheduleListView.as_view(), name='schedule-list'),
        url(r'^schedule/add/$', ScheduleCreateView.as_view(), name='schedule-add'),
        url(r'^schedule/(?P<pk>\d+)/$', ScheduleUpdateView.as_view(), name='schedule-edit'),
        url(r'^schedule-add-form/(?P<pk>\d+)/$', schedule_add_form, name='schedule-add-form'),

        url(r'^assign/(?P<pk>\d+)/$', assign, name='assign'),
        url(r'^fill-form-type/(?P<pk>\d+)/$', fill_form_type, name='fill_form_type'),
        url(r'^fill-details-stage/(?P<pk>\d+)/$', fill_details_stage, name='fill_details_stage'),
        url(r'^fill-details-schedule/(?P<pk>\d+)/$', fill_details_schedule, name='fill_details_schedule'),
]


urlpatterns = urlpatterns + [
        url(r'^assignedFormList/(?P<site_id>\d+)$', AssignedXFormListApi.as_view({'get': 'list'}), name='form-list'),
        # url(r'^(?P<pk>[\d+^/]+)/form\.xml$',
        #         AssignedXFormListApi.as_view({'get': 'retrieve'}),
        #         name='download_xform'),
        url(r'^(?P<pk>\d+)/form\.xml$',
                'onadata.apps.fsforms.views.download_xform', name='download_xform'),

        url(r'^(?P<pk>\d+)/(?P<site_id>\d+)$', AssignedXFormListApi.as_view({'get': 'manifest'}), name='manifest-url'),

        url(r'^submission/(?P<pk>\d+)/(?P<site_id>\d+)$',
            FSXFormSubmissionApi.as_view({'post': 'create', 'head': 'create'}),
                                                        name='submissions'),
]

urlpatterns = urlpatterns + [
        url(r'reports/(?P<fsxf_id>\d+)$', html_export, name='formpack_html_export'),
        url(r'^forms/(?P<fsxf_id>\d+)/instance', instance, name='instance'),
]

urlpatterns = urlpatterns + [
    # kobo main urls

    url(r'^mongo_view_api/(?P<fsxf_id>\d+)/api$', api, name='mongo_view_api'),
    #  kobo main view
    url(r'^show/(?P<fsxf_id>\d+)$', show, name='show'),
    url(r'^forms/(?P<fsxf_id>\d+)/delete_data$', delete_data, name='delete_data'),
#
]

urlpatterns = urlpatterns + [
            # kobo main urls logger vies

    url(r'^forms/(?P<fsxf_id>\d+)/form\.json',  download_jsonform,  name='download_jsonform'),

]

urlpatterns = urlpatterns + [
            # kobo main urls viewer vies

    url(r'^data-view/(?P<fsxf_id>\d+)$',  data_view,  name='data_view'),

]
urlpatterns = urlpatterns + [
            # urls for api

    url(r'^api/site/(?P<site_id>\d+)$', SiteFormViewSet.as_view({'get': 'list'}), name='form-list'),
    url(r'^api/xform$', XFormViewSet.as_view({'get': 'list'}), name='xform-list'),

]

urlpatterns += router.urls


