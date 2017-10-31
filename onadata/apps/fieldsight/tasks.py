from celery import shared_task
import time
from celery import Celery
app = Celery('tasks', backend='redis://localhost:6379/', broker='amqp://guest:guest@localhost:5672/')

@app.task(name='onadata.apps.fieldsight.tasks.printrand')
#@shared_task
def printrand():
    for i in range(10):
        a=str(i) + 'rand'
        time.sleep(5)
        print a
    return ' random users created with success!'
