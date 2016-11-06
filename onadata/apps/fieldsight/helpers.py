from django.http import JsonResponse

def json_from_object(obj):
    data = {
        'id': obj.id
    }

    if hasattr(obj, 'name'):
        data['name'] = obj.name
    elif hasattr(obj, 'address'):
        data['address'] = obj.address
    else:
        data['name'] = str(obj)

    if hasattr(obj, 'phone'):
        data['phone'] = obj.percent
    return JsonResponse(data)
