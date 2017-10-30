from celery import shared_task
from celery import Celery
app = Celery('tasks', backend='redis://localhost:6379/', broker='amqp://guest:guest@localhost:5672/')

@app.task(name='onadata.apps.fieldsight.tasks.printrand')
#@shared_task
def printrand():
    for i in range(100):
        a=str(i) + 'rand'
        print a
    return ' random users created with success!'
