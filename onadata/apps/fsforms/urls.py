from django.conf.urls import url

from onadata.apps.fsforms.viewsets.FieldSightXformViewset import GeneralFormsViewSet, SurveyFormsViewSet, FormDetailViewset
from onadata.apps.fsforms.viewsets.InstanceHistoryViewSet import SiteInstanceResponseViewSet, InstanceHistoryViewSet, InstanceResponseViewSet, InstanceHistoryDetailViewSet
from onadata.apps.fsforms.viewsets.ScheduleViewset import ScheduleViewset, DayViewset
from onadata.apps.fsforms.viewsets.AssignedXFormListApiViewSet import AssignedXFormListApi
from onadata.apps.fsforms.viewsets.FSXFormSubmissionApiViewset import FSXFormSubmissionApi, ProjectFSXFormSubmissionApi
from onadata.apps.fsforms.viewsets.SiteFormsViewset import SiteFormViewSet
from onadata.apps.fsforms.viewsets.StageViewset import SiteMainStageViewSet, \
        SubStageViewSet, StageViewSet
from onadata.apps.fsforms.viewsets.ConfigureStageViewset import StageListViewSet, SubStageListViewSet, \
    SubStageDetailViewSet, EmViewSet, DeployViewset, FInstanceViewset
from onadata.apps.fsforms.viewsets.XformsViewset import XFormViewSet
from .views import (
    LibraryFormsListView,
    XformDetailView,
    GroupListView,
    GroupCreateView,
    GroupUpdateView,
    StageListView,
    StageUpdateView,
    add_sub_stage,
    stage_details,
    stage_add_form,
    assign, fill_form_type,
    fill_details_stage,
    fill_details_schedule,
    schedule_add_form,
    AssignedFormsListView,
    InstanceKobo,
    show,
    api,
    download_jsonform,
    delete_data,
    data_view,
    site_forms,
    setup_site_stages,
    stage_add,
    site_survey,
    set_deploy_sub_stage, set_deploy_main_stage, set_deploy_all_stages,
    create_schedule, stages_reorder, substages_reorder, save_edumaterial, save_edumaterial_details,
    setup_project_stages, project_stage_add, Instance_detail, alter_answer_status, project_survey,
    project_create_schedule, project_edit_schedule, edit_main_stage, edit_sub_stage, edit_schedule, Responses,
    MyOwnFormsListView, share_level, site_general, edit_general, project_general, ProjectResponses,
    project_html_export, Deploy_survey, deploy_stages, Deploy_general, set_deploy_stages, share_stages,
    edit_share_stages, library_stages, un_deploy_general, un_deploy_survey, deploy_general_part, Setup_forms,
    Configure_forms,
    instance_status, Rearrange_stages, deploy_general_remaining_sites, delete_substage, delete_mainstage,
    save_educational_material, AlterStatusDetailView, Html_export, Project_html_export, AssignFormDefaultStatus,
    FullResponseTable, DeleteMyForm,
    DeleteFInstance,
    FormFillView, CreateKoboFormView, DeleteFieldsightXF,

    FormPreviewView)


urlpatterns = [
        url(r'^$', LibraryFormsListView.as_view(), name='library-forms-list'),

        url(r'^preview/(?P<id_string>[^/]+)/$', FormPreviewView.as_view(), name='preview'),
        url(r'^new-submission/(?P<fsxf_id>\d+)/$', FormFillView.as_view(), name='new-submission'),
        url(r'^new-submission/(?P<fsxf_id>\d+)/(?P<site_id>\d+)/$', FormFillView.as_view(), name='new-submission'),
        url(r'^edit-submission/(?P<fsxf_id>\d+)/(?P<instance_pk>\d+)/$', FormFillView.as_view(), name='edit-submission'),

        url(r'^assigned/$', MyOwnFormsListView.as_view(), name='forms-list'),
        url(r'^create/$', CreateKoboFormView.as_view(), name='forms-create'),
        url(r'^xform/(?P<pk>\d+)/$', XformDetailView.as_view(), name='xform-detail'),
        url(r'^xform/delete/(?P<xf_id>\d+)/$', DeleteMyForm.as_view(), name='xform-delete'),
        url(r'^assigned-form-list/$', AssignedFormsListView.as_view(), name='assigned-form-list'),

        url(r'^group/$', GroupListView.as_view(), name='group-list'),
        url(r'^group/add/$', GroupCreateView.as_view(), name='group-add'),
        url(r'^group/(?P<pk>\d+)/$', GroupUpdateView.as_view(), name='group-edit'),

        url(r'^stage/$', StageListView.as_view(), name='stages-list'),
        url(r'^stage/add/(?P<site_id>\d+)/$', stage_add, name='stage-add'),
        url(r'^responses/(?P<pk>\d+)/$', Responses.as_view(), name='site-responses'),
        url(r'^project-responses/(?P<pk>\d+)/$', ProjectResponses.as_view(), name='project-responses'),
        url(r'^project-stage/add/(?P<id>\d+)/$', project_stage_add, name='project-stage-add'),
        url(r'^stage/(?P<pk>\d+)/$', StageUpdateView.as_view(), name='stage-edit'),
        url(r'^stage-add-sub-stage/(?P<pk>\d+)/$', add_sub_stage, name='stage-add-sub-stage'),
        url(r'^stage-detail/(?P<pk>\d+)/$', stage_details, name='stages-detail'),
        url(r'^stage-add-form/(?P<pk>\d+)/$', stage_add_form, name='stage-add-form'),
        url(r'^stage-edit/(?P<stage>\d+)/(?P<id>\d+)/(?P<is_project>\d)/$', edit_main_stage, name='edit-main-stage'),
        url(r'^sub-stage-edit/(?P<stage>\d+)/(?P<id>\d+)/(?P<is_project>\d)/$', edit_sub_stage, name='edit-sub-stage'),

        url(r'^schedule/add/(?P<site_id>\d+)/$', create_schedule, name='schedule-add'),
        url(r'^schedule/(?P<id>\d+)/$', edit_schedule, name='schedule-edit'),
        url(r'^schedule-add-form/(?P<pk>\d+)/$', schedule_add_form, name='schedule-add-form'),
        url(r'^general/(?P<fxf_id>\d+)/$', edit_general, name='edit-general'),

        url(r'^deploy-stages/(?P<id>\d+)/$', deploy_stages, name='deploy-stages'),
        url(r'^change-share-stages/(?P<id>\d+)/$', edit_share_stages, name='edit-share-stages'),
        url(r'^share-stages/(?P<id>\d+)/(?P<is_project>\d)/$', share_stages, name='share-stages'),

        url(r'^set-deploy-stages/(?P<is_project>\d)/(?P<pk>\d+)$', set_deploy_stages, name='set-deploy-stages'),
        url(r'^deploy-general/(?P<is_project>\d)/(?P<pk>\d+)$', Deploy_general.as_view(), name='deploy-general'),
        url(r'^deploy-general-remaining/(?P<is_project>\d)/(?P<pk>\d+)$'
            , deploy_general_remaining_sites
            , name='deploy-general-remaining'),
        url(r'^deploy-survey/(?P<is_project>\d)/(?P<pk>\d+)$', Deploy_survey.as_view(), name='deploy-survey'),

        url(r'^api/stage-rearrange/(?P<is_project>\d)/(?P<pk>\d+)$', Rearrange_stages.as_view()),


        url(r'^un_deploy-survey/(?P<id>\d+)/$', un_deploy_survey, name='undeploy-survey'),
        url(r'^deploy-general-remaining/(?P<fxf_id>\d+)/$', deploy_general_part, name='deploy-general-remaining-sites'),
        url(r'^undeploy-general/(?P<fxf_id>\d+)/$', un_deploy_general, name='undeploy-general'),
        url(r'^project/schedule/add/(?P<id>\d+)/$', project_create_schedule, name='project-schedule-add'),
        url(r'^project/schedule/edit/(?P<id>\d+)/$', project_edit_schedule, name='project-schedule-edit'),
        url(r'^library-stage/(?P<id>\d+)$', library_stages, name='view-stages-of-library'),
        url(r'^setup-site-stage/(?P<site_id>\d+)$', setup_site_stages, name='setup-site-stages'),
        url(r'^setup-project-stage/(?P<id>\d+)$', setup_project_stages, name='setup-project-stages'),
        url(r'^site-survey/(?P<site_id>\d+)$', site_survey, name='site-survey'),
        url(r'^site-general/(?P<site_id>\d+)$', site_general, name='site-general'),
        url(r'^project-general/(?P<project_id>\d+)$', project_general, name='project-general'),
        url(r'^project-survey/(?P<project_id>\d+)$', project_survey, name='project-survey'),

        url(r'^assign/(?P<pk>\d+)/$', assign, name='assign'),
        url(r'^fill-form-type/(?P<pk>\d+)/$', fill_form_type, name='fill_form_type'),
        url(r'^fill-details-stage/(?P<pk>\d+)/$', fill_details_stage, name='fill_details_stage'),
        url(r'^fill-details-schedule/(?P<pk>\d+)/$', fill_details_schedule, name='fill_details_schedule'),
        #setup forms UI urls
        url(r'^setup-forms/(?P<is_project>\d)/(?P<pk>\d+)$', Setup_forms.as_view(), name='setup-forms'),
        url(r'^configure-stages/(?P<is_project>\d)/(?P<pk>\d+)$', Configure_forms.as_view(), name='configure_stages'),

        url(r'^last-submissions/$', FInstanceViewset.as_view({'get': 'list'}), name='finstance-lastsubmission'),

        url(r'^delete-fieldsightxf/(?P<fsxf_id>\d+)/$', DeleteFieldsightXF.as_view(), name='delete-fsform'),
        url(r'^delete-submission/(?P<instance_pk>\d+)/$', DeleteFInstance.as_view(), name='delete-finstance')
]


urlpatterns = urlpatterns + [
        url(r'^assignedFormList/(?P<site_id>\d+)$', AssignedXFormListApi.as_view({'get': 'list'}), name='form-list'),
        url(r'^assignedFormList/project/(?P<project_id>\d+)$', AssignedXFormListApi.as_view(
            {'get': 'project_forms'}), name='project-form-list'),
        url(r'^assignedFormList/siteLevel/(?P<project_id>\d+)$', AssignedXFormListApi.as_view(
            {'get': 'site_overide_forms'}), name='site-overide-form-list'),
        url(r'^(?P<pk>\d+)/form\.xml$',
                'onadata.apps.fsforms.views.download_xform', name='download_xform'),

        url(r'^(?P<pk>\d+)/(?P<site_id>\d+)$', AssignedXFormListApi.as_view({'get': 'manifest'}), name='manifest-url'),

        url(r'^submission/(?P<pk>\d+)/(?P<site_id>\d+)$',
            FSXFormSubmissionApi.as_view({'post': 'create', 'head': 'create'}),
                                                        name='submissions'),
        url(r'^submission/project/(?P<pk>\d+)/(?P<site_id>\d+)$',
            ProjectFSXFormSubmissionApi.as_view({'post': 'create', 'head': 'create'}),
                                                        name='psubmissions'),
        url(r'^assigndefaultformstatus/(?P<fsxf_id>\d+)/(?P<status_code>\d)$', AssignFormDefaultStatus.as_view(), name='assign_default_form_status'),
]

urlpatterns = urlpatterns + [
        url(r'site-submissions/(?P<fsxf_id>\d+)/$', Html_export.as_view(), name='html_export'),
        url(r'site-submissions/(?P<fsxf_id>\d+)/(?P<site_id>\d+)/$', Html_export.as_view(), name='html_export'),
        url(r'project-submissions/(?P<fsxf_id>\d+)$', Project_html_export.as_view(), name='project_html_export'),
        url(r'^forms/(?P<fsxf_id>\d+)$', InstanceKobo.as_view(), name='instance' ),
        url(r'^forms/(?P<fsxf_id>\d+)/(?P<site_id>\d+)$', InstanceKobo.as_view(), name='instance' ),
        url(r'^forms/(?P<fsxf_id>\d+)/(?P<instance_id>\d+)$', Instance_detail.as_view(), name='instance_detail'),
        url(r'^forms/alter-answer-status/(?P<instance_id>\d+)/(?P<status>\d)/(?P<fsid>\d+)$', alter_answer_status, name='alter-answer-status'),
        url(r'submissions/detailed/(?P<fsxf_id>\d+)$', FullResponseTable.as_view(), name='project_html_table_export'),
]

urlpatterns = urlpatterns + [
    # kobo main urls

    url(r'^mongo_view_api/(?P<fsxf_id>\d+)/api$', api, name='mongo_view_api'),
    url(r'^mongo_view_api/(?P<fsxf_id>\d+)/(?P<site_id>\d+)/api$', api, name='mongo_view_api'),
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

]

urlpatterns = urlpatterns + [
            # urls for angular forms

    url(r'^site-forms/(?P<site_id>\d+)$', site_forms, name='site-forms'),
    url(r'^api/xform$', XFormViewSet.as_view({'get': 'list'}), name='xform-list'),

]

urlpatterns = urlpatterns + [

    url(r'^api/days/', DayViewset.as_view({'get': 'list'}), name='days'),
    url(r'^instance/status/(?P<instance>\d+)$', instance_status, name='instance_status'),
    url(r'^api/instance/status-history/(?P<pk>\d+)$', InstanceHistoryViewSet.as_view({'get': 'list'}), name='instance_history'),
    url(r'^api/instance/change_status-detail/(?P<pk>\d+)$', InstanceHistoryDetailViewSet.as_view({'get': 'retrieve'}), name='instance_status_change_detail'),
    url(r'^api/instance/status-detail/(?P<pk>\d+)$', AlterStatusDetailView.as_view(), name='alter-status-detail'),
    url(r'^api/survey/(?P<is_project>\d)/(?P<pk>\d+)$', SurveyFormsViewSet.as_view({'get': 'list'}), name='survey_forms'),
    url(r'^api/general/(?P<is_project>\d)/(?P<pk>\d+)$', GeneralFormsViewSet.as_view({'get': 'list'}), name='general_forms'),
    url(r'^api/schedule/$', ScheduleViewset.as_view({'post': 'create','put': 'update','get': 'list'})),
    url(r'^api/stage/(?P<is_project>\d)/(?P<pk>\d+)$', StageViewSet.as_view({'post': 'create','get': 'list'})),
    url(r'^api/fxf/', GeneralFormsViewSet.as_view({'post': 'create','put': 'update','get': 'list'})),
    url(r'^api/xf/(?P<is_project>\d)/(?P<pk>\d+)$', XFormViewSet.as_view({'get': 'list'})),
    url(r'^api/site-main-stages/(?P<site_id>\d+)$', SiteMainStageViewSet.as_view({'get': 'list'}), name='main-stage-list'),
    url(r'^api/schedules/(?P<is_project>\d)/(?P<pk>\d+)$', ScheduleViewset.as_view({'get': 'list'}), name='schedule-list'),
    url(r'^api/sub-stages/(?P<main_stage>\d+)$', SubStageViewSet.as_view({'get': 'list'}), name='sub-stage-list'),
    url(r'^share/(?P<id>[\w-]+)/(?P<counter>\d+)$', share_level, name='share'),
    url(r'^api/delete-substage/(?P<id>\d+)/$', delete_substage, name='delete_substage_api'),
    url(r'^api/delete-mainstage/(?P<id>\d+)/$', delete_mainstage, name='delete_mainstage_api'),
    url(r'^api/save_educational_material/$', save_educational_material),
    url(r'^api/responses/(?P<pk>\d+)/$', InstanceResponseViewSet.as_view({'get': 'list'})),
    url(r'^api/responses/(?P<form_pk>\d+)/(?P<site_pk>\d+)/$', SiteInstanceResponseViewSet.as_view({'get': 'list'})),
    url(r'^api/form-detail/(?P<pk>\d+)/$', FormDetailViewset.as_view({'get': 'retrieve'})),

    url(r'^api/stage-list/(?P<is_project>\d)/(?P<pk>\d+)/$', StageListViewSet.as_view({'post': 'create','get': 'list'})),
    url(r'^api/configure-stage-update/(?P<pk>\d+)/$', StageListViewSet.as_view({'put': 'update','get': 'retrieve_by_id'})),
    url(r'^api/sub-stage-list/(?P<stage_id>\d+)/$', SubStageListViewSet.as_view({'get': 'list'})),
    url(r'^api/sub-stage-detail/(?P<pk>\d+)/$', SubStageDetailViewSet.as_view({'get': 'retrieve', 'put': 'update'})),
    url(r'^api/sub-stage-detail-create/(?P<stage_id>\d+)/$', SubStageDetailViewSet.as_view({'post': 'create'})),
    url(r'^api/xforms/$', XFormViewSet.as_view({'get': 'list'})),
    url(r'^api/get_em/(?P<pk>\d+).$', EmViewSet.as_view({'get': 'retrieve_by_id'})),
    url(r'^api/stages-reorder/$', stages_reorder),
    url(r'^api/substages-reorder/$', substages_reorder),

    url(r'^api/em/files/(?P<stageid>\d+).$', save_edumaterial),
    url(r'^api/em/(?P<stageid>\d+).$', save_edumaterial_details),


    url(r'^api/set-deploy-all-stages/(?P<is_project>\d)/(?P<pk>\d+)/$', set_deploy_all_stages, name="sdas"),
    url(r'^api/set-deploy-main-stage/(?P<is_project>\d)/(?P<pk>\d+)/(?P<stage_id>\d+)/$', set_deploy_main_stage, name="sdms"),
    url(r'^api/set-deploy-sub-stage/(?P<is_project>\d)/(?P<pk>\d+)/(?P<stage_id>\d+)/$', set_deploy_sub_stage, name="sdss"),


    url(r'^api/get-deploy-data/(?P<pk>\d+)/$', DeployViewset.as_view({'get': 'retrieve'})),


]



# urlpatterns += router.urls



