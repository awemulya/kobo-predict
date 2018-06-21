from __future__ import absolute_import
import time
import json
import xlwt
import datetime
from django.db import transaction
from django.contrib.gis.geos import Point
from celery import shared_task
from onadata.apps.fieldsight.models import Organization, Project, Site, Region, SiteType
from onadata.apps.userrole.models import UserRole
from onadata.apps.eventlog.models import FieldSightLog, CeleryTaskProgress
from django.contrib import messages
from channels import Group as ChannelGroup
from django.contrib.auth.models import Group
from celery import task, current_task
from onadata.apps.fieldsight.fs_exports.formParserForExcelReport import parse_form_response
from io import BytesIO
from django.shortcuts import get_object_or_404
from onadata.apps.fsforms.models import FieldSightXF, FInstance
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.db.models import Prefetch
from .generatereport import PDFReport

@task()
def bulkuploadsites(task_prog_obj_id, source_user, file, pk):
    time.sleep(2)
    project = Project.objects.get(pk=pk)
    task_id = bulkuploadsites.request.id
    task = CeleryTaskProgress.objects.get(pk=task_prog_obj_id)
    task.content_object = project
    task.status=1
    task.save()
    try:
        sites = file.get_records()
        count = len(sites)
        task.description = "Bulk Upload of "+str(count)+" Sites."
        task.save()
        
        with transaction.atomic():
            i=0
            interval = count/20
            for site in sites:
                # time.sleep(0.7)
                site = dict((k, v) for k, v in site.iteritems() if v is not '')
                lat = site.get("longitude", 85.3240)
                long = site.get("latitude", 27.7172)
                location = Point(lat, long, srid=4326)
            
                region_idf = site.get("region_id", None)
                region_id = None
            
                if region_idf is not None:
                    region, created  = Region.objects.get_or_create(identifier=str(region_idf), project = project)
                    region_id = region.id
            
                type_identifier = int(site.get("type", "0"))
            
                if type_identifier == 0:
                    _site, created = Site.objects.get_or_create(identifier=str(site.get("identifier")),
                                                                name=site.get("name"),
                                                                project=project,
                                                                region_id = region_id)
                else:

                    site_type = SiteType.objects.get(identifier=type_identifier, project=project)

                    _site, created = Site.objects.get_or_create(identifier=str(site.get("identifier")),
                                                                name=site.get("name"),
                                                                project=project,
                                                                type=site_type, region_id = region_id)
                _site.phone = site.get("phone")
                _site.address = site.get("address")
                _site.public_desc = site.get("public_desc")
                _site.additional_desc = site.get("additional_desc")
                _site.location = location
                _site.logo = "logo/default_site_image.png"

                meta_ques = project.site_meta_attributes

                myanswers = {}
                for question in meta_ques:
                    myanswers[question['question_name']]=site.get(question['question_name'], "")
                    print site.get(question['question_name'])
                
                _site.site_meta_attributes_ans = myanswers
                _site.save()
                i += 1
                
                if i > interval:
                    interval = i+interval
                    bulkuploadsites.update_state(state='PROGRESS',meta={'current': i, 'total': count})
            task.status = 2
            task.save()
            noti = project.logs.create(source=source_user, type=12, title="Bulk Sites",
                                       organization=project.organization,
                                       project=project, content_object=project,
                                       extra_message=str(count) + " Sites")
    except Exception as e:
        task.status = 3
        task.save()
        print 'Site Upload Unsuccesfull. %s' % e
        print e.__dict__
        noti = project.logs.create(source=source_user, type=412, title="Bulk Sites",
                                       content_object=project, recipient=source_user,
                                       extra_message=str(count) + " Sites @error " + u'{}'.format(e.message))
        
@task()
def exportProjectSiteResponses(task_prog_obj_id, source_user, project_id, base_url, fs_ids, start_date, end_date):
    task = CeleryTaskProgress.objects.get(pk=task_prog_obj_id)
    task.status = 1
    project=get_object_or_404(Project, pk=project_id)
    task.content_object = project
    task.save()

    try:
        buffer = BytesIO()
        sites=project.sites.all().values('id')
        # fs_ids = FieldSightXF.objects.filter(project_id = project.id).values('id')
        # startdate="2016-05-01"
        # enddate= "2018-06-05"
        forms = FieldSightXF.objects.select_related('xf').filter(pk__in=fs_ids, is_survey=False, is_deleted=False).prefetch_related(Prefetch('site_form_instances', queryset=FInstance.objects.select_related('instance').filter(site_id__in=sites, date__range=[start_date, end_date]))).order_by('-is_staged', 'is_scheduled')
        wb = xlwt.Workbook(encoding='utf-8')
        form_id = 0
        form_names=[]
        
        for form in forms:
            form_id += 1
            form_names.append(form.xf.title)
            occurance = form_names.count(form.xf.title)

            if occurance > 1 and len(form.xf.title) > 25:
                sheet_name = form.xf.title[:25] + ".." + "(" +str(occurance)+ ")"
            elif occurance > 1 and len(form.xf.title) < 25:
                sheet_name = form.xf.title + "(" +str(occurance)+ ")"
            elif len(form.xf.title) > 29:
                sheet_name = form.xf.title[:29] + ".."
            else:
                sheet_name = form.xf.title

            ws = wb.add_sheet(sheet_name)
            row_num = 1
            font_style = xlwt.XFStyle()
            head_columns = [{'question_name':'identifier','question_label':'identifier'}, {'question_name':'name','question_label':'name'}]
            repeat_questions = []
            repeat_answers = {}


            for formresponse in form.project_form_instances.all():
                
                questions, answers, r_questions, r_answers = parse_form_response(json.loads(form.xf.json)['children'], formresponse.instance.json, base_url, form.xf.user.username)
                answers['identifier'] = formresponse.site.identifier
                answers['name'] = formresponse.site.name
                
                if r_questions:
                    if not repeat_questions:
                        repeat_questions = r_questions
                    repeat_answers[formresponse.site.identifier] = {'name': formresponse.site.name, 'answers':r_answers}

                if len([{'question_name':'identifier','question_label':'identifier'}, {'question_name':'name','question_label':'name'}] + questions) > len(head_columns):
                    head_columns = [{'question_name':'identifier','question_label':'identifier'}, {'question_name':'name','question_label':'name'}] + questions  

                for col_num in range(len(head_columns)):
                    ws.write(row_num, col_num, answers[head_columns[col_num]['question_name']], font_style)
                
                row_num += 1
            

            font_style.font.bold = True

            for col_num in range(len(head_columns)):
                ws.write(0, col_num, head_columns[col_num]['question_label'], font_style)
            
            font_style.font.bold = False
            if repeat_questions:
                max_repeats = 0
                wr = wb.add_sheet(str(form_id)+"repeated")
                row_num = 1
                font_style = xlwt.XFStyle()
                
                for k, site_r_answers in repeat_answers.items():
                    col_no = 2
                    wr.write(row_num, 1, k, font_style)
                    wr.write(row_num, 2, site_r_answers['name'], font_style)
                    
                    if max_repeats < len(site_r_answers['answers']):
                        max_repeats = len(site_r_answers['answers'])

                    for answer in site_r_answers['answers']:
                        for col_num in range(len(repeat_questions)):
                            wr.write(row_num, col_no + col_num, answer[repeat_questions[col_num]['question_name']], font_style)
                            col_no += 1

                row_num += 1
            

                font_style.font.bold = True
                wr.write(row_num, 1, 'Identifier', font_style)
                wr.write(row_num, 2, 'name', font_style)
                col_no=2

                #for loop needed.
                for m_repeats in range(max_repeats):
                    for col_num in range(len(head_columns)):
                        wr.write(0, col_num, head_columns[col_num]['question_label'], font_style)    
                        col_no += 1 
        if not forms:
            ws = wb.add_sheet('No Forms')

        
        wb.save(buffer)
        buffer.seek(0)
        xls = buffer.getvalue()
        xls_url = default_storage.save(project.name + '/xls/submissions.xls', ContentFile(xls))
        buffer.close()

        task.status = 2
        task.file.name = xls_url
        task.save()
        noti = task.logs.create(source=source_user, type=32, title="Xls Report generation in project",
                                   recipient=source_user, content_object=project,
                                   extra_message=" <a href='"+ task.file.url +"'>Xls report</a> generation in project")

    except Exception as e:
        task.status = 3
        task.save()
        print 'Report Gen Unsuccesfull. %s' % e
        print e.__dict__
        noti = task.logs.create(source=source_user, type=432, title="Xls Report generation in project",
                                       content_object=project, recipient=source_user,
                                       extra_message="@error " + u'{}'.format(e.message))


@task()
def generateCustomReportPdf(task_prog_obj_id, source_user, site_id, base_url, fs_ids, start_date, end_date):
    task = CeleryTaskProgress.objects.get(pk=task_prog_obj_id)
    task.status = 1
    site=get_object_or_404(Site, pk=site_id)
    task.content_object = site
    task.save()

    try:
        buffer = BytesIO()
        report = PDFReport(buffer, 'Letter')
        pdf = report.generateCustomSiteReport(site_id, base_url, fs_ids, start_date, end_date)
        
        buffer.seek(0)
        pdf = buffer.getvalue()
        pdf_url = default_storage.save(site.name + '/pdf/submissions.pdf', ContentFile(pdf))
        buffer.close()

        task.status = 2
        task.save()

        noti = task.logs.create(source=source_user, type=32, title="Pdf Report generation in site",
                                   recipient=source_user, content_object=project,
                                   extra_message=" <a href='"+ task.file.url +"'>Pdf report</a> generation in site")
    except Exception as e:
        task.status = 3
        task.save()
        print 'Report Gen Unsuccesfull. %s' % e
        print e.__dict__
        noti = task.logs.create(source=source_user, type=432, title="Pdf Report generation in site",
                                       content_object=site, recipient=source_user,
                                       extra_message="@error " + u'{}'.format(e.message))        


@task()
def importSites(task_prog_obj_id, source_user, f_project, t_project, meta_attributes, regions, ignore_region):
    time.sleep(2)
    task = CeleryTaskProgress.objects.get(pk=task_prog_obj_id)
    task.content_object = t_project
    task.status=1
    task.save()
    
    try:
        def filterbyquestion_name(seq, value):
            for el in seq:
                if (not meta_attributes) or (meta_attributes and el.get('question_name') in meta_attributes):
                    if el.get('question_name')==value:
                        return True
            return False
        
        # migrate metas

        if t_project.site_meta_attributes:
            t_metas = t_project.site_meta_attributes
            f_metas = f_project.site_meta_attributes
            
            for f_meta in f_metas:
                # print t_metas
                # print ""
                check = filterbyquestion_name(t_metas, f_meta.get('question_name'))
                if not check:
                    t_metas.append(f_meta)
        region_map = {}      

        t_project_sites = t_project.sites.all().values_list('identifier', flat=True)

        # migrate regions
        if f_project.cluster_sites and not ignore_region:
            
            t_project_regions = t_project.project_region.all().values_list('identifier', flat=True)
            t_project.cluster_sites=True
            
            # To handle whole project or a single region migrate
            region_objs = f_project.project_region.filter(id__in=regions)

            for region in region_objs:
                f_region_id = region.id
                if region.identifier in t_project_regions:
                    t_region_id = t_project.project_region.get(identifier=region.identifier).id
                else:
                    region.id=None
                    region.project_id=t_project.id
                    region.save()
                    t_region_id = region.id
                region_map[f_region_id]=t_region_id
        
            t_project.save()

            # getting Sites
        
            sites = f_project.sites.filter(region_id__in=regions)
          
            if 0 in regions:
                unassigned_sites = f_project.sites.filter(region_id=None)
                sites = sites | unassigned_sites

        else:

            sites = f_project.sites.all()

        
        def get_t_region_id(f_region_id):
            # To get new region id without a query
            if f_region_id is not None and f_region_id in region_map:
                return region_map[f_region_id]
            else:
                return None

        # migrate sites
        for site in sites:
            site.id = None
            site.project_id = t_project.id
            
            if site.identifier in t_project_sites:
                site.identifier = str(site.identifier) + "IFP" + str(f_project.id)
        
            if f_project.cluster_sites and not ignore_region:
                site.region_id = get_t_region_id(site.region_id)
            else:
                site.region_id = None
            
            site.save()

        task.status = 2
        task.save()

        if f_project.cluster_sites and not ignore_region:
            noti = FieldSightLog.objects.create(source=source_user, type=30, title="Bulk Project import sites",
                                       content_object=t_project, recipient=source_user,
                                       extra_object=f_project, extra_message="Project Sites import from " + str(len(regions))+" Regions of ")
        else:
            noti = FieldSightLog.objects.create(source=source_user, type=29, title="Bulk Project import sites",
                                       content_object=t_project, recipient=source_user,
                                       extra_object=f_project)        
    except Exception as e:
        task.status = 3
        task.save()
        if f_project.cluster_sites and not ignore_region:
            noti = FieldSightLog.objects.create(source=source_user, type=430, title="Bulk Project import sites",
                                       content_object=t_project, recipient=source_user,
                                       extra_object=f_project, extra_message="Project Sites import from "+str(len(regions))+" Regions of ")
        else:
            
            noti = FieldSightLog.objects.create(source=source_user, type=429, title="Bulk Project import sites",
                                       content_object=t_project, recipient=source_user,
                                       extra_object=f_project)           
        

@shared_task()
def multiuserassignproject(task_prog_obj_id, source_user, org_id, projects, users, group_id):
    time.sleep(2)
    org = Organization.objects.get(pk=org_id)
    projects_count = len(projects)
    users_count = len(users)
    
    task_id = multiuserassignproject.request.id
    task = CeleryTaskProgress.objects.get(pk=task_prog_obj_id)
    task.content_object = org
    task.description = "Assign "+str(users_count)+" people in "+str(projects_count)+" projects."
    task.status=1
    task.save()
    try:
        with transaction.atomic():
            roles_created = 0
            for project_id in projects:
                    project = Project.objects.get(pk=project_id)
                    for user in users:
                        role, created = UserRole.objects.get_or_create(user_id=user, project_id=project_id,
                                                                       organization_id=org.id,
                                                                       group_id=group_id, ended_at=None)
                        if created:
                            roles_created += 1
                            # description = "{0} was assigned  as Project Manager in {1}".format(
                                # role.user.get_full_name(), role.project)
                            # noti = role.logs.create(source=role.user, type=6, title=description, description=description,
                            #  content_object=role.project, extra_object=self.request.user)
                            # result = {}
                            # result['description'] = description
                            # result['url'] = noti.get_absolute_url()
                            # ChannelGroup("notify-{}".format(role.organization.id)).send({"text": json.dumps(result)})
                            # ChannelGroup("project-{}".format(role.project.id)).send({"text": json.dumps(result)})
                            # ChannelGroup("notify-0").send({"text": json.dumps(result)})
        task.status = 2
        task.save()
        if roles_created == 0:
            noti = FieldSightLog.objects.create(source=source_user, type=23, title="Task Completed.",
                                       content_object=org, recipient=source_user,
                                       extra_message=str(roles_created) + " new Project Manager Roles in " + str(projects_count) + " projects ")
        
        else:
            noti = FieldSightLog.objects.create(source=source_user, type=21, title="Bulk Project User Assign",
                                           content_object=org, organization=org, 
                                           extra_message=str(roles_created) + " new Project Manager Roles in " + str(projects_count) + " projects ")
        
    except Exception as e:
        task.status = 3
        task.save()
        noti = FieldSightLog.objects.create(source=source_user, type=421, title="Bulk Project User Assign",
                                       content_object=org, recipient=source_user,
                                       extra_message=str(users_count)+" people in "+str(projects_count)+" projects ")

@shared_task()
def multiuserassignsite(task_prog_obj_id, source_user, project_id, sites, users, group_id):
    time.sleep(2)
    project = Project.objects.get(pk=project_id)
    group_name = Group.objects.get(pk=group_id).name
    sites_count = len(sites)
    users_count = len(users)

    task_id = multiuserassignsite.request.id
    task = CeleryTaskProgress.objects.get(pk=task_prog_obj_id)
    task.content_object = project
    task.description = "Assign "+str(users_count)+" people in "+str(sites_count)+" sites."
    task.status=1
    task.save()
    try:
        with transaction.atomic():
            roles_created = 0            
            for site_id in sites:
                site = Site.objects.get(pk=site_id)
                for user in users:
                  
                    role, created = UserRole.objects.get_or_create(user_id=user, site_id=site.id,
                                                                   project__id=project.id, organization__id=site.project.organization_id, group_id=group_id, ended_at=None)
                    if created:
                        roles_created += 1
                   
                        # description = "{0} was assigned  as {1} in {2}".format(
                        #     role.user.get_full_name(), role.lgroup.name, role.project)
                        # noti_type = 8

                        # if data.get('group') == "Reviewer":
                        #     noti_type =7
                        
                        # noti = role.logs.create(source=role.user, type=noti_type, title=description,
                        #                         description=description, content_type=site, extra_object=self.request.user,
                        #                         site=role.site)
                        # result = {}
                        # result['description'] = description
                        # result['url'] = noti.get_absolute_url()
                        # ChannelGroup("notify-{}".format(role.organization.id)).send({"text": json.dumps(result)})
                        # ChannelGroup("project-{}".format(role.project.id)).send({"text": json.dumps(result)})
                        # ChannelGroup("site-{}".format(role.site.id)).send({"text": json.dumps(result)})
                        # ChannelGroup("notify-0").send({"text": json.dumps(result)})

                        # Device = get_device_model()
                        # if Device.objects.filter(name=role.user.email).exists():
                        #     message = {'notify_type':'Assign Site', 'site':{'name': site.name, 'id': site.id}}
                        #     Device.objects.filter(name=role.user.email).send_message(message)
        task.status = 2
        task.save()
        if roles_created == 0:
            noti = FieldSightLog.objects.create(source=source_user, type=23, title="Task Completed.",
                                       content_object=project, recipient=source_user, 
                                       extra_message="All "+str(users_count) +" users were already assigned as "+ group_name +" in " + str(sites_count) + " selected sites ")
        
        else:

            noti = FieldSightLog.objects.create(source=source_user, type=22, title="Bulk site User Assign",
                                           content_object=project, organization=project.organization, project=project, 
                                           extra_message=str(roles_created) + " new "+ group_name +" Roles in " + str(sites_count) + " sites ")
        
    except Exception as e:
        task.status = 3
        task.save()
        noti = FieldSightLog.objects.create(source=source_user, type=422, title="Bulk Sites User Assign",
                                       content_object=project, recipient=source_user,
                                       extra_message=group_name +" for "+str(users_count)+" people in "+str(sites_count)+" sites ")
        
@shared_task()
def multiuserassignregion(task_prog_obj_id, source_user, project_id, regions, users, group_id):
    time.sleep(2)
    project = Project.objects.get(pk=project_id)
    group_name = Group.objects.get(pk=group_id).name
    sites_count = len(regions)
    users_count = len(users)

    task_id = multiuserassignregion.request.id
    print task_id
    task = CeleryTaskProgress.objects.get(pk=task_prog_obj_id)
    print task
    task.content_object = project
    task.description = "Assign "+str(users_count)+" people in "+str(sites_count)+" regions."
    task.status=1
    task.save()
    try:
        with transaction.atomic():
            roles_created = 0            
            for region_id in regions:
                if region_id == "0":
                    sites = Site.objects.filter(region__isnull=True, project_id=project_id).values('id')
                else: 
                    sites = Site.objects.filter(region_id = region_id, project_id=project_id).values('id')
                for site_id in sites:
                    print "Assigning to site : " + str(site_id)
                    for user in users:
                        site = Site.objects.filter(pk=site_id['id']).first()
                        if site and site.project_id == project.id: 
                            role, created = UserRole.objects.get_or_create(user_id=user, site_id=site_id['id'],
                                                                           project__id=project.id, organization__id=project.organization_id, group_id=group_id, ended_at=None)
                            if created:
                                roles_created += 1
                           
                                # description = "{0} was assigned  as {1} in {2}".format(
                                #     role.user.get_full_name(), role.lgroup.name, role.project)
                                # noti_type = 8

                                # if data.get('group') == "Reviewer":
                                #     noti_type =7
                                
                                # noti = role.logs.create(source=role.user, type=noti_type, title=description,
                                #                         description=description, content_type=site, extra_object=self.request.user,
                                #                         site=role.site)
                                # result = {}
                                # result['description'] = description
                                # result['url'] = noti.get_absolute_url()
                                # ChannelGroup("notify-{}".format(role.organization.id)).send({"text": json.dumps(result)})
                                # ChannelGroup("project-{}".format(role.project.id)).send({"text": json.dumps(result)})
                                # ChannelGroup("site-{}".format(role.site.id)).send({"text": json.dumps(result)})
                                # ChannelGroup("notify-0").send({"text": json.dumps(result)})

                                # Device = get_device_model()
                                # if Device.objects.filter(name=role.user.email).exists():
                                #     message = {'notify_type':'Assign Site', 'site':{'name': site.name, 'id': site.id}}
                                #     Device.objects.filter(name=role.user.email).send_message(message)
        task.status = 2
        task.save()
        if roles_created == 0:
            noti = FieldSightLog.objects.create(source=source_user, type=23, title="Task Completed.",
                                       content_object=project, recipient=source_user, 
                                       extra_message="All "+str(users_count) +" users were already assigned as "+ group_name +" in " + str(sites_count) + " selected regions ")
        
        else:

            noti = FieldSightLog.objects.create(source=source_user, type=22, title="Bulk site User Assign",
                                           content_object=project, organization=project.organization, project=project, 
                                           extra_message=str(roles_created) + " new "+ group_name +" Roles in " + str(sites_count) + " regions ")
        
    except Exception as e:
        print 'Bulk role assign Unsuccesfull. ------------------------------------------%s' % e
        task.description = "Assign "+str(users_count)+" people in "+str(sites_count)+" regions. ERROR: " + str(e) 
        task.status = 3
        task.save()
        noti = FieldSightLog.objects.create(source=source_user, type=422, title="Bulk Region User Assign",
                                       content_object=project, recipient=source_user,
                                       extra_message=group_name +" for "+str(users_count)+" people in "+str(sites_count)+" regions ")

def sendNotification(notification, recipient):
    result={}
    result['id']= noti.id,
    result['source_uid']= source_user.id,
    result['source_name']= source_user.username,
    result['source_img']= source_user.user_profile.profile_picture.url,
    result['get_source_url']= noti.get_source_url(),
    result['get_event_name']= project.name,
    result['get_event_url']= noti.get_event_url(),
    result['get_extraobj_name']= None,
    result['get_extraobj_url']= None,
    result['get_absolute_url']= noti.get_absolute_url(),
    result['type']= 412,
    result['date']= str(noti.date),
    result['extra_message']= str(count) + " Sites @error " + u'{}'.format(e.message),
    result['seen_by']= [],
    ChannelGroup("notif-user-{}".format(recipient.id)).send({"text": json.dumps(result)})