from __future__ import absolute_import, unicode_literals
from celery import shared_task

import time
from celery import Celery
from .models import Organization, Project, Site
from onadata.apps.userrole.models import UserRole
app = Celery('tasks', backend='redis://localhost:6379/', broker='amqp://guest:guest@localhost:5672/')

@app.task(name='onadata.apps.fieldsight.tasks.printrand')
#@shared_task
def printrand():
    for i in range(10):
        a=str(i) + 'rand'
        time.sleep(5)
        print a
    return ' random users created with success!'

@app.task(name='onadata.apps.fieldsight.tasks.multiuserassignproject')
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
