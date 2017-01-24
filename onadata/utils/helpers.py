from django.http import JsonResponse
import json


def save_model(model, values):
    for key, value in values.items():
        setattr(model, key, value)
    model.save()
    return model


def invalid(row, required_fields):
    invalid_attrs = []
    for attr in required_fields:
        # if one of the required attributes isn't received or is an empty string
        if not attr in row or row.get(attr) == "":
            invalid_attrs.append(attr)
    if len(invalid_attrs) is 0:
        return False
    return invalid_attrs


def empty_to_none(o):
    if o == '':
        return None
    return o


def empty_to_zero(o):
    if o == '' or o == None:
        return 0
    return o


def get_discount_with_percent(total, discount):
    try:
        if str(discount)[-1] == '%':
            _discount = discount[:-1]
            return float((float(_discount) / 100) * total)
        else:
            return float(empty_to_zero(discount))
    except IndexError:
        return empty_to_zero(discount)


def zero_for_none(obj):
    if obj is None:
        return 0
    else:
        return obj


def none_for_zero(obj):
    if not obj:
        return None
    else:
        return obj


def write_error(dct, e):
    if hasattr(e, 'messages'):
        dct['error_message'] = '; '.join(e.messages)
    elif str(e) != '':
        dct['error_message'] = str(e)
    else:
        dct['error_message'] = 'Error in form data!'
    return dct


# def get_next_voucher_no(cls, attr):
#     from django.db.models import Max

#     max_voucher_no = cls.objects.all().aggregate(Max(attr))[attr + '__max']
#     if max_voucher_no:
#         return max_voucher_no + 1
#     else:
#         return 1

def calculate_tax(tax_choice, total, percent):
    _sum = 0
    if tax_choice == "inclusive":
        _sum = total * (percent / (100 + percent))
    elif tax_choice == "exclusive":
        _sum = total * (percent / 100)
    return _sum


def json_from_object(obj):
    data = {
        'id': obj.id
    }

    if hasattr(obj, 'name'):
        data['name'] = obj.name
    elif hasattr(obj, 'title'):
        data['name'] = obj.title
    else:
        data['name'] = str(obj)

    if hasattr(obj, 'percent'):
        data['percent'] = obj.percent  # Percent attr for tax scheme
    return JsonResponse(data)


def get_next_voucher_no(cls, company_id=None, attr='voucher_no'):
    from django.db.models import Max

    qs = cls.objects.all()
    if company_id:
        qs = qs.filter(company_id=company_id)
    max_voucher_no = qs.aggregate(Max(attr))[attr + '__max']
    if max_voucher_no:
        return int(max_voucher_no) + 1
    else:
        return 1


def delete_rows(rows, model):
    for row in rows:
        if row.get('id'):
            instance = model.objects.get(id=row.get('id'))
            # TODO is journalentry deleted on row deletion?
            # JournalEntry.objects.get(content_type=ContentType.objects.get_for_model(model),
            #                         model_id=instance.id).delete()
            instance.delete()


def save_model(model, values):
    for key, value in values.items():
        setattr(model, key, value)
    model.clean()
    model.save()
    return model


def invalid(row, required_fields):
    invalid_attrs = []
    for attr in required_fields:
        # if one of the required attributes isn't received or is an empty string
        if not attr in row or row.get(attr) == "":
            invalid_attrs.append(attr)
    if len(invalid_attrs) is 0:
        return False
    return invalid_attrs


def save_qs_from_ko(model, filter_kwargs, request_body):
    qs = model.objects.filter(**filter_kwargs)
    params = json.loads(request_body)
    try:
        del params['__ko_mapping__']
    except KeyError:
        pass
    try:
        qs.update(**params)
        return {}
    except Exception as e:
        return {'error': str(e)}
