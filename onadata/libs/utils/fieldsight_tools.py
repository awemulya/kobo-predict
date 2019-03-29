import requests
import json
from django.conf import settings
from onadata.apps.eventlog.models import CeleryTaskProgress


class KPIError(Exception):
    pass


def deploy_kpi_form(id_string, headers):
    if not hasattr(settings, 'KPI_ASSET_URL'):
        return False

    url = settings.KPI_ASSET_URL+id_string+"/deployment/"
    values = {
        'active': True,
        'server_url': url
    }
    req = requests.post(url, data=json.dumps(values),
                        headers=headers, verify=False)
    if req.status_code in [200, 201]:
        return True
    else:
        try:
            response = req.json()
            print(req.json(), "*NOt 200 code*")
        except ValueError:
            print('Not deployed', req.status_code)
            pass
        else:
            if 'error' in response:
                raise KPIError(response['message'])
        return False


def clone_kpi_form(id_string, token, task_id, name="Default Form Mahabharat"):
    if not hasattr(settings, 'KPI_ASSET_URL'):
        return False

    url = settings.KPI_ASSET_URL
    values = {
        'clone_from': id_string,
        'name': name,
        'server_url': url
    }
    headers = {'content-type': 'application/json',
               'Authorization': 'Token ' + token}
    req = requests.post(url, data=json.dumps(values),
                        headers=headers, verify=False)
    print(req.status_code, "status code")
    if req.status_code in [200, 201]:
        try:
            id_string = req.__dict__['headers']['location'].split("/")[-2]
            print("kpi response  to clone")
        except Exception as e:
            print(str(e), "error occured")
        else:
            print("id string from kpi clone", id_string)
            deploy = deploy_kpi_form(id_string, headers)
            if not deploy:
                task_obj = CeleryTaskProgress.objects.get(id=task_id)
                task_obj.other_fields.update({'Deploy Default Form': req.status_code})
                task_obj.save()
            else:
                return True, id_string
    else:
        task_obj = CeleryTaskProgress.objects.get(id=task_id)
        task_obj.other_fields.update({'Clone Defualt Form': req.status_code})
        task_obj.save()
        try:
            # import ipdb
            # ipdb.set_trace()
            response = req.json()
            print(req.json(), "*NOt 200 code*")
        except ValueError:
            pass
        else:
            if 'error' in response:
                raise KPIError(response['message'])
    return False, None
