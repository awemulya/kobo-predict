import stripe
import json
from datetime import datetime
import dateutil.relativedelta

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django.contrib import messages

from .models import Customer, Subscription, Invoice, Package
from onadata.apps.fieldsight.models import Organization


@login_required()
def subscribe_view(request, org_id):
    """

    :param request:
    :param org_id:
    : Create stripe customer, subscribed in selected plans using Stripe api
    : Store in db

    """

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
        try:
            Subscription.objects.create(**sub_data)
        except Exception as e:
            return JsonResponse({'error': str(e)})

    messages.add_message(request, messages.SUCCESS, 'You are subscribed to selected plan')

    return HttpResponseRedirect(reverse("users:profile", kwargs={'pk': request.user.pk}))


@csrf_exempt
def stripe_webhook(request):
    """

    :param request:
    :listening events from stripe webhook, events are 'invoice.created' and 'invoice.payment_succeeded'
    """

    try:
        event_json = json.loads(request.body)
        print('Event occursssssssssssssssssssssssss', event_json['type'])

        timestamp = int(event_json['data']['object']['period_start'])
        timestamp_to_date = datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d')

        if event_json['type'] == 'invoice.created' and timestamp_to_date != datetime.now().strftime('%Y-%m-%d'):
            """
            
            Executed in last day of subscribed period(month/year), updating Invoice in stripe for the next month/year 
            """
            print('Execute from the first month/year/day last day')

            def metered_usage_api(quantity):
                """

                :param quantity:
                :call stripe UsageRecord for overage plan
                """

                stripe.UsageRecord.create(
                    quantity=quantity,
                    timestamp=event_json['data']['object']['period_start'],
                    subscription_item=event_json['data']['object']['lines']['data'][2]['subscription_item'],
                    action='set'
                )

            def invoice_obj(amount, quantity, overage, roll_over):
                """

                :param amount:
                :param quantity:
                :param overage:
                :param roll_over:
                :return:
                """
                Invoice.objects.create(
                    customer=stripe_cust_id,
                    created=datetime.now(),
                    amount=amount,
                    quantity=quantity,
                    overage=overage,
                    roll_over=roll_over
                )
            subscriber = Subscription.objects.get(stripe_customer__stripe_cust_id=event_json['data']['object']['customer'])
            org = subscriber.organization
            stripe_cust_id = Customer.objects.get(stripe_cust_id=event_json['data']['object']['customer'])

            package_period = subscriber.package.period_type
            if package_period == 1:
                start_date = datetime.now()+dateutil.relativedelta.relativedelta(days=-1)
            elif package_period == 2:
                start_date = datetime.now()+dateutil.relativedelta.relativedelta(days=-2)

            outstanding, flagged, approved, rejected = org.get_submissions_count_by_date(date=start_date)

            submission_count = outstanding+flagged+approved+rejected

            # filtering for test day
            previous_day = datetime.now()+dateutil.relativedelta.relativedelta(days=-1)
            invoice = Invoice.objects.filter(customer__stripe_cust_id=event_json['data']['object']['customer'],
                                             created__year=previous_day.year, created__month=previous_day.month,
                                             created__day=previous_day.day).get()
            previous_roll_over = invoice.roll_over

            package = Subscription.objects.get(stripe_customer=stripe_cust_id).package

            if previous_roll_over > 0 and submission_count > package.submissions:
                """
                
                if previous roll over and there is overage case in this month
                """

                available_submissions = previous_roll_over + package.submissions - submission_count

                if available_submissions >= 0:
                    """
                    
                    roll over or equal to 0
                    """

                    metered_usage_api(quantity=0)
                    invoice_obj(amount=package.total_charge, quantity=package.submissions, overage=0,
                                roll_over=available_submissions)

                else:
                    """
                    
                    not roll over
                    """
                    metered_usage_api(quantity=submission_count)
                    invoice_obj(amount=package.total_charge, quantity=package.total_charge+(abs(available_submissions)*package.extra_submissions_charge)
                            , overage=abs(available_submissions), roll_over=0)

            elif previous_roll_over == 0 and submission_count > package.submissions:
                metered_usage_api(quantity=submission_count)

                invoice_obj(amount=package.total_charge+((submission_count-package.submissions)*package.extra_submissions_charge),
                        quantity=submission_count, overage=submission_count-package.submissions, roll_over=0)

            elif previous_roll_over > 0 and submission_count < package.submissions:
                available_submissions = previous_roll_over + package.submissions + (package.submissions-submission_count)

                metered_usage_api(quantity=0)

                invoice_obj(amount=package.total_charge, quantity=package.submissions, overage=0, roll_over=available_submissions)

            elif previous_roll_over == 0 and submission_count < package.submissions:
                metered_usage_api(quantity=0)

                invoice_obj(amount=package.total_charge, quantity=submission_count, overage=0, roll_over=package.submissions-submission_count)

            elif previous_roll_over == 0 and submission_count == package.submissions:
                metered_usage_api(quantity=submission_count)

                invoice_obj(amount=package.total_charge, quantity=submission_count, overage=0, roll_over=0)


        # if event_json['type'] == 'invoice.payment_succeeded' and timestamp_to_date != datetime.now().strftime('%Y-%m-%d'):
        #     """
        #
        #     Payment success in second month/year.
        #     """
        #     print('Not to executeeeeeeeeeeeeeeeeeeeeeeeeeeeeee invoice.payment.succeded')
        #     # after payment succeeded, create Invoice object in next month
        #     invoice_data = {
        #         'customer': Customer.objects.get(stripe_cust_id=event_json['data']['object']['customer']),
        #         'created': event_json['data']['object']['date'],
        #         'amount': event_json['data']['object']['amount_paid'],
        #         'quantity': '',
        #         'overage': 12,
        #         'roll_over': 0
        #     }
        #     Invoice.objects.create(**invoice_data)

        elif event_json['type'] == 'invoice.payment_succeeded' and timestamp_to_date == datetime.now().strftime('%Y-%m-%d'):
            """
            
            First Payment after subscribed to plans in stripe, create invoice object
            """
            print('Firsttttttttttttttttt payment success')

            # after payment succeeded, create Invoice object in first month or year
            stripe_cust_id = Customer.objects.get(stripe_cust_id=event_json['data']['object']['customer'])
            package = Subscription.objects.get(stripe_customer=stripe_cust_id).package
            invoice_data = {
                'customer': stripe_cust_id,
                'created': datetime.utcfromtimestamp(int(event_json['data']['object']['date'])),
                'amount': event_json['data']['object']['amount_paid']/100,
                'quantity': package.submissions,
                'overage': 0,
                'roll_over': 0
            }
            Invoice.objects.create(**invoice_data)

        return HttpResponse(status=200)

    except Exception as e:
        return JsonResponse({'error': str(e)})
