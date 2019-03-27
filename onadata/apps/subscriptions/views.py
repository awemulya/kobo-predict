import stripe
import json
import time
from datetime import datetime
import dateutil.relativedelta

from django.core.exceptions import PermissionDenied
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django.contrib import messages
from django.views.generic import TemplateView

from .models import Customer, Subscription, Invoice, Package
from onadata.apps.fieldsight.models import Organization
from onadata.apps.fieldsight.mixins import LoginRequiredMixin


# @login_required()
# def subscribe_view(request, org_id):
#     """
#
#     :param request:
#     :param org_id:
#     : Create stripe customer, subscribed in selected plans using Stripe api
#     : Store in db
#
#     """
#
#     if request.method == 'POST':
#         customer_data = {
#             'email': request.POST['stripeEmail'],
#             'description': 'Some Customer Data',
#             'card': request.POST['stripeToken'],
#             'metadata': {'username': request.user.username}
#         }
#         customer = stripe.Customer.create(**customer_data)
#         cust = Customer.objects.get(user=request.user)
#         cust.stripe_cust_id = customer.id
#         cust.save()
#         period = request.POST['interval']
#         if period == 'yearly':
#             overage_plan = settings.YEARLY_PLANS_OVERRAGE[request.POST['plan_name']]
#             selected_plan = settings.YEARLY_PLANS[request.POST['plan_name']]
#         elif period == 'monthly':
#             overage_plan = settings.MONTHLY_PLANS_OVERRAGE[request.POST['plan_name']]
#             selected_plan = settings.MONTHLY_PLANS[request.POST['plan_name']]
#
#         sub = customer.subscriptions.create(
#             items=[
#                     {
#                        'plan': selected_plan,
#
#                     },
#
#                     {
#                         'plan': overage_plan,
#                     },
#
#
#                   ],
#
#         )
#         organization = get_object_or_404(Organization, id=org_id)
#
#         sub_data = {
#             'stripe_sub_id': sub.id,
#             'is_active': True,
#             'initiated_on': datetime.now(),
#             'package': Package.objects.get(plan=settings.PLANS[selected_plan]),
#             'organization': Organization.objects.get(id=organization.id)
#
#
#         }
#         try:
#             # Subscription.objects.create(**sub_data)
#             Subscription.objects.filter(stripe_customer=cust, stripe_sub_id="free_plan").update(**sub_data)
#
#         except Exception as e:
#             return JsonResponse({'error': str(e)})
#
#     messages.add_message(request, messages.SUCCESS, 'You are subscribed to selected plan')
#
#     return HttpResponseRedirect(reverse("users:profile", kwargs={'pk': request.user.pk}))

MONTHLY_PLAN_NAME = {
    'starter_plan': 'Starter Monthly Plan',
    'basic_plan': 'Basic Monthly Plan',
    'extended_plan': 'Extended Monthly Plan',
    'pro_plan': 'Pro Monthly Plan',
    'scale_plan': 'Scale Monthly Plan'
}

YEARLY_PLAN_NAME = {
    'starter_plan': 'Starter Yearly Plan',
    'basic_plan': 'Basic Yearly Plan',
    'extended_plan': 'Extended Yearly Plan',
    'pro_plan': 'Pro Yearly Plan',
    'scale_plan': 'Scale Yearly Plan'
}


INTERVAL = {
    'yearly': 2,
    'monthly': 1
}


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
        cust = Customer.objects.get(user=request.user)
        cust.stripe_cust_id = customer.id
        cust.save()
        period = request.POST['interval']
        if period == 'yearly':
            overage_plan = settings.YEARLY_PLANS_OVERRAGE[request.POST['plan_name']]
            selected_plan = settings.YEARLY_PLANS[request.POST['plan_name']]
        elif period == 'monthly':
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
            'is_active': True,
            'initiated_on': datetime.now(),
            'package': Package.objects.get(plan=settings.PLANS[selected_plan]),
            'organization': Organization.objects.get(id=organization.id)


        }
        try:
            # Subscription.objects.create(**sub_data)
            Subscription.objects.filter(stripe_customer=cust, stripe_sub_id="free_plan").update(**sub_data)

        except Exception as e:
            return JsonResponse({'error': str(e)})

    messages.add_message(request, messages.SUCCESS, 'You are subscribed to selected plan')

    return HttpResponseRedirect(reverse("subscriptions:profile", kwargs={'pk': request.user.pk}))


@csrf_exempt
def stripe_webhook(request):
    """

    :param request:
    :listening events from stripe webhook, events are 'invoice.created' and 'invoice.payment_succeeded'
    """

    try:
        event_json = json.loads(request.body)
        print('...........Event occurs..................', event_json['type'])

        # timestamp = int(event_json['data']['object']['period_start'])
        sub_obj = Subscription.objects.get(stripe_customer__stripe_cust_id=event_json['data']['object']['customer'])
        subscription_date = sub_obj.initiated_on.strftime('%Y-%m-%d')
        now = datetime.now()
        timestamp = int(time.mktime(now.timetuple()))

        if event_json['type'] == 'invoice.created':

            def metered_usage_api(quantity):
                """

                :param quantity:
                :call stripe UsageRecord for overage plan
                """

                stripe.UsageRecord.create(
                    quantity=quantity,
                    timestamp=timestamp,
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

            if subscription_date == datetime.now().strftime('%Y-%m-%d'):
                """

                First Payment after subscribed to plans in stripe, create invoice object
                """
                print('....................First Invoice Object..................')

                # after payment succeeded, create Invoice object in first month or year
                package = Subscription.objects.get(stripe_customer=stripe_cust_id).package
                invoice_data = {
                    'customer': stripe_cust_id,
                    'created': datetime.utcfromtimestamp(int(event_json['data']['object']['date'])),
                    'amount': package.total_charge,
                    'quantity': package.submissions,
                    'overage': 0,
                    'roll_over': 0
                }
                Invoice.objects.create(**invoice_data)

            elif subscription_date != datetime.now().strftime('%Y-%m-%d'):
                """

                Executed in last day of subscribed period(month/year), updating Invoice in stripe for the next month/year 
                """

                print('...........Execute from the first month/year/day last day '
                      '(creating invoice object from second month)............')
                outstanding, flagged, approved, rejected = org.get_submissions_count_by_date(start_date=start_date)

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

        # elif event_json['type'] == 'invoice.payment_succeeded' and timestamp_to_date == datetime.now().strftime('%Y-%m-%d'):
        #     """
        #
        #     First Payment after subscribed to plans in stripe, create invoice object
        #     """
        #     print('Firsttttttttttttttttt payment success')
        #
        #     # after payment succeeded, create Invoice object in first month or year
        #     stripe_cust_id = Customer.objects.get(stripe_cust_id=event_json['data']['object']['customer'])
        #     package = Subscription.objects.get(stripe_customer=stripe_cust_id).package
        #     invoice_data = {
        #         'customer': stripe_cust_id,
        #         'created': datetime.utcfromtimestamp(int(event_json['data']['object']['date'])),
        #         'amount': event_json['data']['object']['amount_paid']/100,
        #         'quantity': package.submissions,
        #         'overage': 0,
        #         'roll_over': 0
        #     }
        #     Invoice.objects.create(**invoice_data)

        return HttpResponse(status=200)

    except Exception as e:
        return JsonResponse({'error': str(e)})


def finish_subscription(request, org_id):

    if request.method == 'POST':
        organization = get_object_or_404(Organization, id=org_id)
        customer_data = {
            'email': request.user.email,
            'description': 'Some Customer Data',
            'card': request.POST['stripeToken'],
            'metadata': {'username': request.user.username}
        }

        customer = stripe.Customer.create(**customer_data)
        cust = Customer.objects.get(user=request.user)
        cust.stripe_cust_id = customer.id
        cust.save()

        stripe_customer = stripe.Customer.retrieve(cust.stripe_cust_id)
        card = stripe_customer.sources.data[0].last4

        period = request.POST['interval']

        starting_date = datetime.now().strftime('%A, %B %d, %Y')
        if period == 'yearly':
            overage_plan = settings.YEARLY_PLANS_OVERRAGE[request.POST['plan_name']]
            selected_plan = settings.YEARLY_PLANS[request.POST['plan_name']]
            package = Package.objects.get(plan=settings.PLANS[selected_plan], period_type=2)
            ending_date = datetime.now() + dateutil.relativedelta.relativedelta(months=12)
            plan_name = YEARLY_PLAN_NAME[request.POST['plan_name']]

        elif period == 'monthly':
            overage_plan = settings.MONTHLY_PLANS_OVERRAGE[request.POST['plan_name']]
            selected_plan = settings.MONTHLY_PLANS[request.POST['plan_name']]
            package = Package.objects.get(plan=settings.PLANS[selected_plan], period_type=1)
            ending_date = datetime.now() + dateutil.relativedelta.relativedelta(months=1)
            plan_name = MONTHLY_PLAN_NAME[request.POST['plan_name']]

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
            'is_active': True,
            'initiated_on': datetime.now(),
            'package': Package.objects.get(plan=settings.PLANS[selected_plan]),
            'organization': Organization.objects.get(id=organization.id)

        }
        try:
            # Subscription.objects.create(**sub_data)
            Subscription.objects.filter(stripe_customer=cust, stripe_sub_id="free_plan").update(**sub_data)

        except Exception as e:
            return JsonResponse({'error': str(e)})

        return render(request, 'fieldsight/pricing_step_3.html', {'organization': organization,
                                                                  'submissions': package.submissions,
                                                                  'amount': package.total_charge,
                                                                  'starting_date': starting_date,
                                                                  'ending_date': ending_date.strftime('%A, %B %d, %Y'),
                                                                  'card': card,
                                                                  'plan_name': plan_name,
                                                                  })

    else:
        return JsonResponse({'error': 'get method not allowed'})


def get_package(request):

    plan = request.GET.get('plan', None)
    interval = request.GET.get('interval', None)

    period = INTERVAL[interval]
    if interval == 'yearly':
        ending_date = datetime.now()+dateutil.relativedelta.relativedelta(months=12)
        submissions = Package.objects.get(plan=settings.PLANS[settings.YEARLY_PLANS[plan]], period_type=period).submissions
        selected_plan = YEARLY_PLAN_NAME[plan]

    elif interval == 'monthly':
        ending_date = datetime.now()+dateutil.relativedelta.relativedelta(months=1)
        submissions = Package.objects.get(plan=settings.PLANS[settings.MONTHLY_PLANS[plan]], period_type=period).submissions
        selected_plan = MONTHLY_PLAN_NAME[plan]

    data = {
        'selected_plan': selected_plan,
        'starting_date': datetime.now().strftime('%A, %B %d, %Y'),
        'ending_date': ending_date.strftime('%A, %B %d, %Y'),
        'submissions': submissions
    }
    return JsonResponse(data)


class FinishSubscriptionView(LoginRequiredMixin, TemplateView):
    template_name = 'fieldsight/pricing_step_3.html'

    # def dispatch(self, request, *args, **kwargs):
    #     organization = get_object_or_404(Organization, id=self.kwargs['org_id'])
    #     if request.user == organization.owner:
    #         return super(FinishSubscriptionView, self).dispatch(request, *args, **kwargs)
    #
    #     raise PermissionDenied()

    def get_context_data(self, **kwargs):
        context = super(FinishSubscriptionView, self).get_context_data(**kwargs)

        context['organization'] = get_object_or_404(Organization, id=self.kwargs['org_id'])

        return context


class TeamSettingsView(LoginRequiredMixin, TemplateView):
    template_name = 'subscriptions/team_owner.html'

    def dispatch(self, request, *args, **kwargs):
        organization = get_object_or_404(Organization, id=self.kwargs['org_id'])
        if request.user == organization.owner:
            return super(TeamSettingsView, self).dispatch(request, *args, **kwargs)

        raise PermissionDenied()

    def get_context_data(self, **kwargs):
        context = super(TeamSettingsView, self).get_context_data(**kwargs)

        context['organization'] = get_object_or_404(Organization, id=self.kwargs['org_id'])
        if not self.request.user.is_superuser:
            customer = Customer.objects.get(user=self.request.user)
            context['customer'] = customer
            if not customer.stripe_cust_id == 'free_cust_id':
                stripe_customer = stripe.Customer.retrieve(customer.stripe_cust_id)
                context['card'] = stripe_customer.sources.data[0].last4
            context['subscribed_package'] = Subscription.objects.select_related().get(stripe_customer=customer).package
            context['has_user_free_package'] = Subscription.objects.filter(stripe_sub_id="free_plan", stripe_customer__user=self.request.user).exists()
            context['key'] = settings.STRIPE_PUBLISHABLE_KEY

        return context


@login_required
def update_card(request):
    if request.method == 'POST':
        """
            replace old card with new
        """

        customer = Customer.objects.get(user=request.user).stripe_cust_id

        stripe.Customer.modify(
            customer,
            source=request.POST['stripeToken'],
        )

        messages.success(request, 'You have been successfully updated your card.')
    return HttpResponseRedirect(reverse("subscriptions:team_settings", kwargs={'org_id': request.user.organizations.all()[0].pk}))




