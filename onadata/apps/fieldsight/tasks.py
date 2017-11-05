from __future__ import absolute_import
import time
import json
from django.db import transaction
from django.contrib.gis.geos import Point
from celery import shared_task
from onadata.apps.fieldsight.models import Organization, Project, Site
from onadata.apps.userrole.models import UserRole
from django.contrib import messages
from channels import Group as ChannelGroup

@shared_task()
def printr():
    for i in range(10):
        a=str(i) + 'rand'
        time.sleep(5)
        print a
    return ' random users created with success!'

@shared_task()
def bulkuploadsites(user, file, pk):
    time.sleep(5)
    try:
        sites = file.get_records()
        project = Project.objects.get(pk=pk)
        count = len(sites)
        with transaction.atomic():
            for site in sites:
                site = dict((k, v) for k, v in site.iteritems() if v is not '')
                lat = site.get("longitude", 85.3240)
                long = site.get("latitude", 27.7172)
                location = Point(lat, long, srid=4326)
                type_id = int(site.get("type", "1"))
                _site, created = Site.objects.get_or_create(identifier=str(site.get("id")),
                                                            name=site.get("name"),
                                                            project=project, type_id=type_id)
                _site.phone = site.get("phone")
                _site.address = site.get("address")
                _site.public_desc = site.get("public_desc"),
                _site.additional_desc = site.get("additional_desc")
                _site.location = location
                _site.logo = "logo/default-org.jpg"
                _site.save()
                # print _site
            noti = project.logs.create(source=user, type=12, title="Bulk Sites",
                                       organization=project.organization,
                                       project=project, content_object=project,
                                       extra_message=str(count) + " Sites")
            result={}
            result['id']= noti.id,
            result['source_name']= user.username,
            result['source_img']= user.user_profile.profile_picture.url,
            result['get_source_url']= noti.get_source_url(),
            result['get_event_name']= project.name,
            result['get_event_url']= noti.get_event_url(),
            result['get_extraobj_name']= None,
            result['get_extraobj_url']= None,
            result['get_absolute_url']= noti.get_absolute_url(),
            result['type']= 12,
            result['date']= str(noti.date),
            result['extra_message']= str(count)+" Sites",
            result['seen_by']= [],
            ChannelGroup("notif-user-{}".format(user.id)).send({"text": json.dumps(result)})
            # ChannelGroup("project-{}".format(project.id)).send({"text": json.dumps(result)})
            print 'sucess--------' + str(count)
    except Exception as e:
        print 'Site Upload Unsuccesfull. %s' % e
        noti = project.logs.create(source=user, type=412, title="Bulk Sites",
                                       content_object=project, recipient=user,
                                       extra_message=str(count) + " Sites")
        result={}
        result['id']= noti.id,
        result['source_name']= user.username,
        result['source_img']= user.user_profile.profile_picture.url,
        result['get_source_url']= noti.get_source_url(),
        result['get_event_name']= project.name,
        result['get_event_url']= noti.get_event_url(),
        result['get_extraobj_name']= None,
        result['get_extraobj_url']= None,
        result['get_absolute_url']= noti.get_absolute_url(),
        result['type']= 412,
        result['date']= str(noti.date),
        result['extra_message']= str(count)+" Sites",
        result['seen_by']= [],
        ChannelGroup("notif-user-{}".format(user.id)).send({"text": json.dumps(result)})
        return None

@shared_task()
def multiuserassignproject(projects, users, group_id):
    try:
        with transaction.atomic():
            for project_id in projects:
                    project = Project.objects.get(pk=project_id)
                    for user in users:
                        role, created = UserRole.objects.get_or_create(user_id=user, project_id=project_id,
                                                                       organization_id=project.organization.id,
                                                                       group_id=group_id, ended_at=None)
                        if created:
                            description = "{0} was assigned  as Project Manager in {1}".format(
                                role.user.get_full_name(), role.project)
                            # noti = role.logs.create(source=role.user, type=6, title=description, description=description,
                            #  content_object=role.project, extra_object=self.request.user)
                            # result = {}
                            # result['description'] = description
                            # result['url'] = noti.get_absolute_url()
                            # ChannelGroup("notify-{}".format(role.organization.id)).send({"text": json.dumps(result)})
                            # ChannelGroup("project-{}".format(role.project.id)).send({"text": json.dumps(result)})
                            # ChannelGroup("notify-0").send({"text": json.dumps(result)})
    except Exception as e:
        noti = role.logs.create(source=user, type=412, title="Bulk Sites",
                                       content_object=project, recipient=user,
                                       extra_message=str(count) + " Sites")
        result={}
        result['id']= noti.id,
        result['source_name']= user.username,
        result['source_img']= user.user_profile.profile_picture.url,
        result['get_source_url']= noti.get_source_url(),
        result['get_event_name']= project.name,
        result['get_event_url']= noti.get_event_url(),
        result['get_extraobj_name']= None,
        result['get_extraobj_url']= None,
        result['get_absolute_url']= noti.get_absolute_url(),
        result['type']= 412,
        result['date']= str(noti.date),
        result['extra_message']= str(count)+" Sites",
        result['seen_by']= [],
        ChannelGroup("notif-user-{}".format(user.id)).send({"text": json.dumps(result)})
        return None

@shared_task()
def multiuserassignsite(sites, users, group_id):
    try:
        with transaction.atomic():
            response = ""
            for site_id in sites:
                site = Site.objects.get(pk=site_id)
                for user in users:
                  
                    role, created = UserRole.objects.get_or_create(user_id=user, site_id=site.id,
                                                                   project__id=site.project.id, organization__id=site.project.organization_id, group_id=group_id, ended_at=None)
                    if created:
                   
                        # description = "{0} was assigned  as {1} in {2}".format(
                        #     role.user.get_full_name(), role.lgroup.name, role.project)
                        noti_type = 8

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
                    else:
                        response += "Already exists."
    except Exception as e:
        noti = role.logs.create(source=user, type=412, title="Bulk Sites",
                                       content_object=project, recipient=user,
                                       extra_message=str(count) + " Sites")
        result={}
        result['id']= noti.id,
        result['source_name']= user.username,
        result['source_img']= user.user_profile.profile_picture.url,
        result['get_source_url']= noti.get_source_url(),
        result['get_event_name']= project.name,
        result['get_event_url']= noti.get_event_url(),
        result['get_extraobj_name']= None,
        result['get_extraobj_url']= None,
        result['get_absolute_url']= noti.get_absolute_url(),
        result['type']= 412,
        result['date']= str(noti.date),
        result['extra_message']= str(count)+" Sites",
        result['seen_by']= [],
        ChannelGroup("notif-user-{}".format(user.id)).send({"text": json.dumps(result)})
        return None