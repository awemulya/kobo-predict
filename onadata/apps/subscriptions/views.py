import stripe
import json
from datetime import datetime

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.conf import settings


from .models import Customer, Subscription


@login_required()
def subscribe_view(request):

    if request.method == 'POST':
        customer_data = {
            'email': request.POST['stripeEmail'],
            'description': 'Some Customer Data',
            'card': request.POST['stripeToken'],
            'metadata': {'username': request.user.username}
        }
        customer = stripe.Customer.create(**customer_data)
        try:
            cust = Customer.objects.create(user=request.user, stripe_cust_id=customer.id)
        except Exception as e:
            return JsonResponse({'error': 'User has already registered to Stripe.'})
        period = request.POST['interval']
        if period == 'Yearly':
            selected_plan = settings.YEARLY_PLANS[request.POST['plan_name']]
        elif period == 'Monthly':
            selected_plan = settings.MONTHLY_PLANS[request.POST['plan_name']]

        sub = customer.subscriptions.create(
            items=[
                    {
                       'plan': selected_plan,

                    },

                  ],

        )
        sub_data = {
            'stripe_sub_id': sub.id,
            'stripe_customer': cust,
            'is_active': True,
            'initiated_on': datetime.now()

        }
        Subscription.objects.create(**sub_data)

    return render(request, 'fieldsight/test_stripe_charge.html')


@csrf_exempt
def stripe_webhook(request):
 # Retrieve the request's body and parse it as JSON:
    try:
        event_json = json.loads(request.body)
        if event_json['type'] == 'invoice.created':
            stripe.UsageRecord.create(
                 quantity=816,
                 timestamp=event_json['data']['object']['period_start'],
                 subscription_item=event_json['data']['object']['lines']['data'][0]['subscription_item'],
                 action='set'
         )

        return HttpResponse(status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)})
