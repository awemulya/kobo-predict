from __future__ import absolute_import
import time
from celery import shared_task
from onadata.apps.fieldsight.models import Organization, Project, Site
from onadata.apps.userrole.models import UserRole


@shared_task()
def printr():
    for i in range(10):
        a=str(i) + 'rand'
        # time.sleep(5)
        print a
    return ' random users created with success!'


@shared_task()
def multiuserassignproject(projects, users, group_id):
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