import requests
import json
from django.conf import settings


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
        try:
            response = req.json()
            print("kpi response to deploy ", response)
        except ValueError:
            pass
        else:
            print("try catch else ", response)
        return True

    else:
        try:
            response = req.json()
            print(req.json(), "*NOt 200 code*")
        except ValueError:
            pass
        else:
            if 'error' in response:
                raise KPIError(response['message'])
        return False


def clone_kpi_form(id_string, token, , name="Default Form"):
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
        except ValueError:
            pass
        else:
            print("id string from kpi clone", )
            deploy_kpi_form(id_string, headers)
            return True
    else:
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
    return False
