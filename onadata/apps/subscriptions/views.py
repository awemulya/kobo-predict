import stripe
import json
from datetime import datetime

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.shortcuts import get_object_or_404

from .models import Customer, Subscription, Invoice, Package
from onadata.apps.fieldsight.models import Organization


@login_required()
def subscribe_view(request, org_id):

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
            overage_plan = settings.YEARLY_PLANS_OVERRAGE[request.POST['plan_name']]
            selected_plan = settings.YEARLY_PLANS[request.POST['plan_name']]
        elif period == 'Monthly':
            overage_plan = settings.MONTHLY_PLANS_OVERRAGE[request.POST['plan_name']]
            selected_plan = settings.MONTHLY_PLANS[request.POST['plan_name']]

        sub = customer.subscriptions.create(
            items=[
                    {
                       'plan': selected_plan,

                    },

                    {
                        'plan': overage_plan,
                    },


                  ],

        )
        organization = get_object_or_404(Organization, id=org_id)

        sub_data = {
            'stripe_sub_id': sub.id,
            'stripe_customer': cust,
            'is_active': True,
            'initiated_on': datetime.now(),
            'package': Package.objects.get(plan=settings.PLANS[selected_plan]),
            'organization': Organization.objects.get(id=organization.id)


        }
        Subscription.objects.create(**sub_data)

    return render(request, 'fieldsight/test_stripe_charge.html')


@csrf_exempt
def stripe_webhook(request):

    try:
        event_json = json.loads(request.body)
        print('Event occursssssssssssssssssssssssss', event_json['type'])

        timestamp = int(event_json['data']['object']['period_start'])
        timestamp_to_date = datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d')

        if event_json['type'] == 'invoice.created' and timestamp_to_date != datetime.now().strftime('%Y-%m-%d'):
            print('Not to executeeeeeeeeeeeeeeeeeeeeeeeeeeeeee invoice.created')
            # update invoice for next month

            def metered_usage_api(quantity):

                stripe.UsageRecord.create(
                    quantity=quantity,
                    timestamp=event_json['data']['object']['period_start'],
                    subscription_item=event_json['data']['object']['lines']['data'][2]['subscription_item'],
                    action='set'
                )

            submission_count = 'calculate submission up to this date'
            previous_roll_over = 'get the roll_over from previous month'
            stripe_cust_id = Customer.objects.get(stripe_cust_id=event_json['data']['object']['customer'])

            package = Subscription.objects.get(stripe_customer=stripe_cust_id).package

            if previous_roll_over > 0 and submission_count > package.submissions:
                # if there is previous roll over and there is overage case in this month
                available_submissions = previous_roll_over + package.submissions - submission_count

                if available_submissions >= 0:
                    metered_usage_api(quantity=0)
                else:
                    metered_usage_api(quantity=submission_count)

            elif previous_roll_over == 0 and submission_count > package.submissions:
                metered_usage_api(quantity=submission_count)

            elif previous_roll_over > 0 and submission_count < package.submissions:
                available_submissions = previous_roll_over + package.submissions + (package.submissions-submission_count)

                metered_usage_api(quantity=0)

            elif previous_roll_over == 0 and submission_count < package.submissions:
                metered_usage_api(quantity=0)

        if event_json['type'] == 'invoice.payment_succeeded' and timestamp_to_date != datetime.now().strftime('%Y-%m-%d'):
            print('Not to executeeeeeeeeeeeeeeeeeeeeeeeeeeeeee invoice.payment.succeded')
            # after payment succeeded, create Invoice object in next month
            invoice_data = {
                'customer': Customer.objects.get(stripe_cust_id=event_json['data']['object']['customer']),
                'created': event_json['data']['object']['date'],
                'amount': event_json['data']['object']['amount_paid'],
                'quantity': '',
                'overage': 12,
                'roll_over': 0
            }
            Invoice.objects.create(**invoice_data)

        elif event_json['type'] == 'invoice.payment_succeeded' and timestamp_to_date == datetime.now().strftime('%Y-%m-%d'):
            print('Firsttttttttttttttttt payment success')
            # after payment succeeded, create Invoice object in first month or year
            stripe_cust_id = Customer.objects.get(stripe_cust_id=event_json['data']['object']['customer'])
            package = Subscription.objects.get(stripe_customer=stripe_cust_id).package
            invoice_data = {
                'customer': stripe_cust_id,
                'created': datetime.utcfromtimestamp(int(event_json['data']['object']['date'])),
                'amount': event_json['data']['object']['amount_paid'],
                'quantity': package.submissions,
                'overage': 0,
                'roll_over': 0
            }
            Invoice.objects.create(**invoice_data)

        return HttpResponse(status=200)

    except Exception as e:
        return JsonResponse({'error': str(e)})
