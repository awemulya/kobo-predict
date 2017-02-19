# -*- coding: utf-8 -*-

import json
from datetime import date, timedelta
import importlib
from django.core import serializers
from django.db.models.query import QuerySet
from django.template import Library
from django.utils.safestring import mark_safe
from django.db.models import Model
from django import template
from django.contrib.auth.models import Group
from django.template.base import FilterExpression
from django.template.loader import get_template



from django.conf import settings

from onadata.apps.userrole.models import UserRole
from onadata.apps.users.models import UserProfile

register = Library()

@register.filter
def get_type(value):
    return type(value)


FORM_STATUS = {0:'Outstanding', 1: 'Rejected', 2: 'Flagged', 3: 'Approved'}

def get_status_level(status=0):
    return FORM_STATUS.get(status, "Outstanding")


@register.filter
def exceptlast(lst):
    my_list = lst[:-1]
    my_list[-1] = get_status_level(my_list[-1])
    return my_list


@register.filter
def fsmedia(data_list):
    if isinstance(data_list[-1], list):
        return data_list[-1]
    elif isinstance(data_list[-2], list):
        return data_list[-2]
    return []


@register.filter
def get_org_roles(user_id, org_id):
    if org_id is None:
        return []
    if org_id != "0":
        return UserRole.objects.filter(organization__id=org_id, user__id=user_id, ended_at__isnull=True)
    return []


@register.filter
def get_proj_roles(user_id, id):
    if id is None:
        return []
    if id != "0":
        return UserRole.objects.filter(project__id=id, user__id=user_id,ended_at__isnull=True)
    return []

@register.filter
def get_site_roles(user_id, id):
    if id is None:
        return []
    if id != "0":
        return UserRole.objects.filter(site__id=id, user__id=user_id, ended_at__isnull=True)
    return []

@register.filter
def status(status=0):
    return FORM_STATUS.get(status,"Outstanding")

@register.filter
def is_demand(obj):
    if obj.__class__.__name__ == 'DemandRow':
        return True
    return False


@register.filter
def activeness(is_active):
    if is_active:
        return "Active"
    return "In-Active"


@register.filter
def alter_status(is_active):
    if is_active:
        return "Deactivate"
    return "Activate"


@register.filter
def profile(userid):
    return UserProfile.objects.get(user__id=userid).id


# USURPERS = {
#     'Site': ['Super Admin', 'Organization Admin', 'Project Manager', 'Central Engineer', 'Site Supervisor', 'Data Entry'],
#     'Project': ['Super Admin', 'Organization Admin', 'Project Manager'],
#     'Organization': ['Super Admin', 'Organization Admin'],
#     'admin': ['Super Admin'],
# }


USURPERS = {
    'Site': ['Central Engineer', 'Site Supervisor', 'Project Manager', 'Central Engineer', 'Organization Admin',
             'Super Admin'],
    'KoboForms': ['Project Manager', 'Central Engineer', 'Organization Admin', 'Super Admin'],
    'Project': ['Project Manager', 'Organization Admin', 'Super Admin', 'Central Engineer'],
    'Organization': ['Organization Admin', 'Super Admin'],
    'admin': ['Super Admin'],
}

@register.tag
def ifrole(parser, token):
    try:
        # split_contents() knows not to split quoted strings.
        tag_name, role = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(
            "%r tag requires exactly two arguments" % token.contents.split()[0]
        )
    if not (role[0] == role[-1] and role[0] in ('"', "'")):
        raise template.TemplateSyntaxError(
            "%r tag's argument should be in quotes" % tag_name
        )
    nodelist = parser.parse('endrole', )
    parser.delete_first_token()
    return RoleInGroup(role[1:-1], nodelist)


class RoleInGroup(template.Node):
    def __init__(self, role, nodelist):
        self.role = role
        self.nodelist = nodelist

    def render(self, context):
        request = template.resolve_variable('request', context)
        if request.role and request.role.group.name in USURPERS[self.role]:
            return self.nodelist.render(context)
        else:
            return ''


def handler(obj):
    if hasattr(obj, 'isoformat'):
        return obj.isoformat()
    # elif isinstance(obj, ...):
    # return ...
    else:
        raise TypeError('Object of type %s with value of %s is not JSON serializable' % (type(obj), repr(obj)))


@register.filter
def jsonify(object):
    if isinstance(object, QuerySet):
        return serializers.serialize('json', object)
    if isinstance(object, Model):
        model_dict = object.__dict__
        del model_dict['_state']
        return mark_safe(json.dumps(model_dict))
    return mark_safe(json.dumps(object, default=handler))


@register.filter
def user_to_json(user):
    if hasattr(user, '_wrapped') and hasattr(user, '_setup'):
        if user._wrapped.__class__ == object:
            user._setup()
        user = user._wrapped
    user_dict = {'id': user.id, 'username': user.username}
    return mark_safe(json.dumps(user_dict))


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter
def if_not_none(obj):
    if obj is None:
        return ''
    return obj


@register.filter
def subtract(value, arg):
    if value is None:
        value = 0
    if arg is None:
        arg = 0
    return value - arg


@register.simple_tag
def yesterday():
    today = date.today()
    yesterday = today - timedelta(days=1)
    return yesterday


@register.tag()
def ifusergroup(parser, token):
    """ Check to see if the currently logged in user belongs to one or more groups
    Requires the Django authentication contrib app and middleware.

    Usage: {% ifusergroup Admins %} ... {% endifusergroup %}, or
           {% ifusergroup Admins Clients Programmers Managers %} ... {% else %} ... {% endifusergroup %}

    """
    try:
        tokens = token.split_contents()
        groups = []
        groups += tokens[1:]
    except ValueError:
        raise template.TemplateSyntaxError("Tag 'ifusergroup' requires at least 1 argument.")

    nodelist_true = parser.parse(('else', 'endifusergroup'))
    token = parser.next_token()

    if token.contents == 'else':
        nodelist_false = parser.parse(('endifusergroup',))
        parser.delete_first_token()
    else:
        nodelist_false = template.NodeList()

    return GroupCheckNode(groups, nodelist_true, nodelist_false)


class GroupCheckNode(template.Node):
    def __init__(self, groups, nodelist_true, nodelist_false):
        self.groups = groups
        self.nodelist_true = nodelist_true
        self.nodelist_false = nodelist_false

    def render(self, context):
        user = template.resolve_variable('user', context)

        if not user.is_authenticated():
            return self.nodelist_false.render(context)

        allowed = False
        for checkgroup in self.groups:

            if checkgroup.startswith('"') and checkgroup.endswith('"'):
                checkgroup = checkgroup[1:-1]

            if checkgroup.startswith("'") and checkgroup.endswith("'"):
                checkgroup = checkgroup[1:-1]

            try:
                group = Group.objects.get(name=checkgroup)
            except Group.DoesNotExist:
                break

            if group in user.groups.all():
                allowed = True
                break

        if allowed:
            return self.nodelist_true.render(context)
        else:
            return self.nodelist_false.render(context)


@register.filter
def setting(path):
    to_import = '.'.join(path.split('.')[:-2])
    imported = importlib.import_module(to_import)
    group_name = path.split('.')[-2:-1][0]
    group = getattr(imported, group_name)
    attr_name = path.split('.')[-1]
    val = getattr(group, attr_name)
    return val


@register.tag
def ifappexists(parser, token):
    """ Conditional Django template tag to check if one or more apps exist.

    Usage: {% ifappexists tag %} ... {% endifappexists %}, or
           {% ifappexists tag inventory %} ... {% else %} ... {% endifappexists %}

    """
    try:
        tokens = token.split_contents()
        apps = []
        apps += tokens[1:]
    except ValueError:
        raise template.TemplateSyntaxError("Tag 'ifappexists' requires at least 1 argument.")

    nodelist_true = parser.parse(('else', 'endifappexists'))
    token = parser.next_token()

    if token.contents == 'else':
        nodelist_false = parser.parse(('endifappexists',))
        parser.delete_first_token()
    else:
        nodelist_false = template.NodeList()

    return AppCheckNode(apps, nodelist_true, nodelist_false)


class AppCheckNode(template.Node):
    def __init__(self, apps, nodelist_true, nodelist_false):
        self.apps = apps
        self.nodelist_true = nodelist_true
        self.nodelist_false = nodelist_false

    def render(self, context):
        allowed = False
        for app in self.apps:

            if app.startswith('"') and app.endswith('"'):
                app = app[1:-1]

            if app.startswith("'") and app.endswith("'"):
                app = app[1:-1]

            if app in settings.INSTALLED_APPS:
                allowed = True
            else:
                break

        if allowed:
            return self.nodelist_true.render(context)
        else:
            return self.nodelist_false.render(context)


@register.filter
def linebreaks(obj):
    return mark_safe(obj.replace("\n", "<br>"))


@register.filter
def linkify(obj):
    # import pdb
    #
    # pdb.set_trace()
    if obj:
        return mark_safe('<a href="' + obj.get_absolute_url() + '">' + unicode(obj) + '</a>')


@register.filter
def is_demand(obj):
    if obj.__class__.__name__ == 'DemandRow':
        return True
    return False


@register.filter
def get_class(value):
    return value.__class__.__name__


@register.filter
def localize(text):
    text = str(text)
    dic = {
        '०': '0',
        '१': '1',
        '२': '2',
        '३': '3',
        '४': '4',
        '५': '5',
        '६': '6',
        '७': '7',
        '८': '8',
        '९': '9'
    }
    res = dict((v, k) for k, v in dic.iteritems())
    for i, j in res.iteritems():
        text = text.replace(i, j)
    return text


@register.filter
def debug(value):
    pass

@register.filter
def mailto(email, linktext=None):
    if not email:
        return ''
    if linktext is None: linktext = email
    return mark_safe('<a href="mailto:%s">%s</a>' % (email, linktext))


@register.filter
def to_class_name(value):
    return value.__class__.__name__


@register.simple_tag()
def multiply(a, b):
    if a and b:
        return a * b
    return ''


@register.filter
def dr_or_cr(val):
    if val < 0:
        return str(val * -1) + ' (Cr)'
    else:
        return str(val) + ' (Dr)'





def _setup_macros_dict(parser):
    ## Metadata of each macro are stored in a new attribute
    ## of 'parser' class. That way we can access it later
    ## in the template when processing 'usemacro' tags.
    try:
        ## Only try to access it to eventually trigger an exception
        parser._macros
    except AttributeError:
        parser._macros = {}


class DefineMacroNode(template.Node):
    def __init__(self, name, nodelist, args):

        self.name = name
        self.nodelist = nodelist
        self.args = []
        self.kwargs = {}
        for a in args:
            if "=" not in a:
                self.args.append(a)
            else:
                name, value = a.split("=")
                self.kwargs[name] = value

    def render(self, context):
        ## empty string - {% macro %} tag does no output
        return ''


@register.tag(name="kwacro")
def do_macro(parser, token):
    try:
        args = token.split_contents()
        tag_name, macro_name, args = args[0], args[1], args[2:]
    except IndexError:
        m = ("'%s' tag requires at least one argument (macro name)"
             % token.contents.split()[0])
        raise template.TemplateSyntaxError(m)
    # TODO: could do some validations here,
    # for now, "blow your head clean off"
    nodelist = parser.parse(('endkwacro',))
    parser.delete_first_token()

    ## Metadata of each macro are stored in a new attribute
    ## of 'parser' class. That way we can access it later
    ## in the template when processing 'usemacro' tags.
    _setup_macros_dict(parser)
    parser._macros[macro_name] = DefineMacroNode(macro_name, nodelist, args)
    return parser._macros[macro_name]


class LoadMacrosNode(template.Node):
    def render(self, context):
        ## empty string - {% loadmacros %} tag does no output
        return ''


@register.tag(name="loadkwacros")
def do_loadmacros(parser, token):
    try:
        tag_name, filename = token.split_contents()
    except IndexError:
        m = ("'%s' tag requires at least one argument (macro name)"
             % token.contents.split()[0])
        raise template.TemplateSyntaxError(m)
    if filename[0] in ('"', "'") and filename[-1] == filename[0]:
        filename = filename[1:-1]
    t = get_template(filename)
    macros = t.nodelist.get_nodes_by_type(DefineMacroNode)
    ## Metadata of each macro are stored in a new attribute
    ## of 'parser' class. That way we can access it later
    ## in the template when processing 'usemacro' tags.
    _setup_macros_dict(parser)
    for macro in macros:
        parser._macros[macro.name] = macro
    return LoadMacrosNode()


class UseMacroNode(template.Node):
    def __init__(self, macro, fe_args, fe_kwargs):
        self.macro = macro
        self.fe_args = fe_args
        self.fe_kwargs = fe_kwargs

    def render(self, context):

        for i, arg in enumerate(self.macro.args):
            try:
                fe = self.fe_args[i]
                context[arg] = fe.resolve(context)
            except IndexError:
                context[arg] = ""

        for name, default in iter(self.macro.kwargs.items()):
            if name in self.fe_kwargs:
                context[name] = self.fe_kwargs[name].resolve(context)
            else:
                context[name] = FilterExpression(default,
                                                 self.macro.parser
                                                 ).resolve(context)

        return self.macro.nodelist.render(context)


@register.tag(name="usekwacro")
def do_usemacro(parser, token):
    try:
        args = token.split_contents()
        tag_name, macro_name, values = args[0], args[1], args[2:]
    except IndexError:
        m = ("'%s' tag requires at least one argument (macro name)"
             % token.contents.split()[0])
        raise template.TemplateSyntaxError(m)
    try:
        macro = parser._macros[macro_name]
    except (AttributeError, KeyError):
        m = "Macro '%s' is not defined" % macro_name
        raise template.TemplateSyntaxError(m)

    fe_kwargs = {}
    fe_args = []

    for val in values:
        if "=" in val:
            # kwarg
            name, value = val.split("=")
            fe_kwargs[name] = FilterExpression(value, parser)
        else:  # arg
            # no validation, go for it ...
            fe_args.append(FilterExpression(val, parser))

    macro.parser = parser
    return UseMacroNode(macro, fe_args, fe_kwargs)


@register.filter
def tel(no):
    return mark_safe('<a href="tel:%s">%s</a>' % (no, no))


@register.filter
def remove_lines(string):
    return str(string).replace('\n', '')


@register.filter
def last_word(string):
    return str(string).split()[-1]
