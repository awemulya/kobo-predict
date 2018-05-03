from datetime import date, datetime
import os
import pytz
import re
import tempfile
import traceback
from xml.dom import Node
from xml.parsers.expat import ExpatError

from dict2xml import dict2xml
from django.conf import settings
from django.core.exceptions import ValidationError, PermissionDenied
from django.core.files.storage import get_storage_class
from django.core.mail import mail_admins
from django.core.servers.basehttp import FileWrapper
from django.contrib.auth.models import User
from django.db import IntegrityError, transaction
from django.db.models.signals import pre_delete
from django.http import HttpResponse, HttpResponseNotFound, \
    StreamingHttpResponse
from django.shortcuts import get_object_or_404
from django.utils.encoding import DjangoUnicodeDecodeError
from django.utils.translation import ugettext as _
from django.utils import timezone
from modilabs.utils.subprocess_timeout import ProcessTimedOut
from pyxform.errors import PyXFormError
from pyxform.xform2json import create_survey_element_from_xml
import sys

from onadata.apps.fsforms.models import FieldSightXF, FieldSightParsedInstance, FInstance
from onadata.apps.fsforms.utils import FIELDSIGHT_XFORM_ID
from onadata.apps.main.models import UserProfile
from onadata.apps.logger.models import Attachment
from onadata.apps.logger.models import Instance
from onadata.apps.logger.models.instance import (
    FormInactiveError,
    InstanceHistory,
    get_id_string_from_xml_str)
from onadata.apps.logger.models import XForm
from onadata.apps.logger.models.xform import XLSFormError
from onadata.apps.logger.xform_instance_parser import (
    InstanceEmptyError,
    InstanceInvalidUserError,
    InstanceMultipleNodeError,
    DuplicateInstance,
    clean_and_parse_xml,
    get_uuid_from_xml,
    get_deprecated_uuid_from_xml,
    get_submission_date_from_xml)
from onadata.apps.viewer.models.data_dictionary import DataDictionary
from onadata.apps.viewer.models.parsed_instance import _remove_from_mongo,\
    xform_instances, ParsedInstance
from onadata.libs.utils import common_tags
from onadata.libs.utils.model_tools import queryset_iterator, set_uuid


OPEN_ROSA_VERSION_HEADER = 'X-OpenRosa-Version'
HTTP_OPEN_ROSA_VERSION_HEADER = 'HTTP_X_OPENROSA_VERSION'
OPEN_ROSA_VERSION = '1.0'
DEFAULT_CONTENT_TYPE = 'text/xml; charset=utf-8'
DEFAULT_CONTENT_LENGTH = settings.DEFAULT_CONTENT_LENGTH

uuid_regex = re.compile(r'<formhub>\s*<uuid>\s*([^<]+)\s*</uuid>\s*</formhub>',
                        re.DOTALL)

mongo_instances = settings.MONGO_DB.instances


def _get_instance(xml, new_uuid, submitted_by, status, xform, fxfid, project_fxf, site_id, project_id):
    # check if its an edit submission
    # old_uuid = get_deprecated_uuid_from_xml(xml)
    # instances = Instance.objects.filter(uuid=new_uuid)
    instances = None
    if instances:
        # edits
        check_edit_submission_permissions(submitted_by, xform)
        instance = instances[0]
        InstanceHistory.objects.create(
            xml=instance.xml, xform_instance=instance, uuid=new_uuid)
        instance.xml = xml
        instance.uuid = new_uuid
        instance.save()
    else:
        # new submission
        instance = Instance.objects.create(
            xml=xml, user=submitted_by, status=status, xform=xform)
        if fxfid and site_id and project_fxf and project_id and fxfid:
            FInstance.objects.create(instance=instance, site_id=site_id, project_id=project_id, site_fxf_id=fxfid,
                                 project_fxf_id=project_fxf, submitted_by=submitted_by)
        elif fxfid and site_id and project_id:
            FInstance.objects.create(instance=instance, site_id=site_id, project_id=project_id, site_fxf_id=fxfid,
                             submitted_by=submitted_by)
        elif fxfid and site_id:
            FInstance.objects.create(instance=instance, site_id=site_id,site_fxf_id=fxfid,
                             submitted_by=submitted_by)
        elif project_id and project_fxf:
            FInstance.objects.create(instance=instance, project_id=project_id,
                                 project_fxf_id=project_fxf, submitted_by=submitted_by)

        if instance:
            instance.uuid = new_uuid
            instance.save()
    return instance


def dict2xform(jsform, form_id):
    dd = {'form_id': form_id}
    xml_head = u"<?xml version='1.0' ?>\n<%(form_id)s id='%(form_id)s'>\n" % dd
    xml_tail = u"\n</%(form_id)s>" % dd

    return xml_head + dict2xml(jsform) + xml_tail


def get_uuid_from_submission(xml):
    # parse UUID from uploaded XML
    split_xml = uuid_regex.split(xml)

    # check that xml has UUID
    return len(split_xml) > 1 and split_xml[1] or None



def _has_edit_xform_permission(xform, user):
    if isinstance(xform, XForm) and isinstance(user, User):
        return user.has_perm('logger.change_xform', xform)

    return False


def check_edit_submission_permissions(request_user, xform):
    if xform and request_user and request_user.is_authenticated():
        requires_auth = UserProfile.objects.get_or_create(user=xform.user
            )[0].require_auth
        has_edit_perms = _has_edit_xform_permission(xform, request_user)

        if requires_auth and not has_edit_perms:
            raise PermissionDenied(
                _(u"%(request_user)s is not allowed to make edit submissions "
                  u"to %(form_user)s's %(form_title)s form." % {
                      'request_user': request_user,
                      'form_user': xform.user,
                      'form_title': xform.title}))


def check_submission_permissions(request, xform):
    """Check that permission is required and the request user has permission.

    The user does no have permissions iff:
        * the user is authed,
        * either the profile or the form require auth,
        * the xform user is not submitting.

    Since we have a username, the Instance creation logic will
    handle checking for the forms existence by its id_string.

    :returns: None.
    :raises: PermissionDenied based on the above criteria.
    """
    profile = UserProfile.objects.get_or_create(user=xform.user)[0]
    if request and (profile.require_auth or xform.require_auth
                    or request.path == '/submission')\
            and xform.user != request.user\
            and not request.user.has_perm('report_xform', xform):
        raise PermissionDenied(
            _(u"%(request_user)s is not allowed to make submissions "
              u"to %(form_user)s's %(form_title)s form." % {
                  'request_user': request.user,
                  'form_user': xform.user,
                  'form_title': xform.title}))


def save_submission(xform, xml, media_files, new_uuid, submitted_by, status,
                    date_created_override, fxid, site, fs_poj_id=None, project=None):
    if not date_created_override:
        date_created_override = get_submission_date_from_xml(xml)

    instance = _get_instance(xml, new_uuid, submitted_by, status, xform, fxid, fs_poj_id, site, project)

    for f in media_files:
        Attachment.objects.get_or_create(
            instance=instance, media_file=f, mimetype=f.content_type)

    # override date created if required
    if date_created_override:
        if not timezone.is_aware(date_created_override):
            # default to utc?
            date_created_override = timezone.make_aware(
                date_created_override, timezone.utc)
        instance.date_created = date_created_override
        instance.save()
    if instance.xform is not None:
        if fs_poj_id:
            fs_poj_id = str(fs_poj_id)
        pi, created = FieldSightParsedInstance.get_or_create(instance,
                                                             update_data={'fs_uuid': fxid, 'fs_status': 0,
                                                                          'fs_site':site, 'fs_project':project,
                                                                          'fs_project_uuid':fs_poj_id})
    if not created:
        pi.save(async=False)
    return instance


def same_form_submitted_again_without_schedule(fsxform):
    if fsxform.is_scheduled:
        return False
    return True


def schedule_uuid_value(fsxform):
    if not fsxform.is_scheduled or not fsxform.schedule:
        return ""
    return str(fsxform.schedule.id)


def create_instance(fsxfid, xml_file, media_files,
                    status=u'submitted_via_web', uuid=None,
                    date_created_override=None, request=None, site=None, fs_proj_xf=None, proj_id=None, xform=None):

    with transaction.atomic():
        instance = None
        submitted_by = request.user \
            if request and request.user.is_authenticated() else None
        xml = xml_file.read()
        # fsxform = FieldSightXF.objects.get(pk=fsxfid)
        # xform = fsxform.xf
        # existing_instance_count = fsxform.fs_instances.count()

        # if(existing_instance_count and same_form_submitted_again_without_schedule(fsxform)):
        #         raise DuplicateInstance()

        # new_uuid = get_uuid_from_xml(xml) + str(fsxfid)+ schedule_uuid_value(fsxform)
        # duplicate_instances = Instance.objects.filter(uuid=new_uuid)

        # if duplicate_instances:
        #     # ensure we have saved the extra attachments
        #     for f in media_files:
        #         Attachment.objects.get_or_create(
        #             instance=duplicate_instances[0],
        #             media_file=f, mimetype=f.content_type)
        # else:
        if fsxfid is None:
            fsxfid = ""
        if site is None:
            site = ""
        instance = save_submission(xform, xml, media_files, uuid,
                                       submitted_by, status,
                                       date_created_override, str(fsxfid), str(site), fs_proj_xf, proj_id)
        return instance

    # if duplicate_instances:
    #     # We are now outside the atomic block, so we can raise an exception
    #     # without rolling back the extra attachments we created earlier
    #     # NB: Since `ATOMIC_REQUESTS` is set at the database level, everything
    #     # could still be rolled back if the calling view fails to handle an
    #     # exception
    #     raise DuplicateInstance()


def safe_create_instance(fsxfid, xml_file, media_files, uuid, request, site, fs_proj_xf, proj_id, xform):
    """Create an instance and catch exceptions.

    :returns: A list [error, instance] where error is None if there was no
        error.
    """
    error = instance = None

    try:
        instance = create_instance(
            fsxfid, xml_file, media_files, uuid=uuid, request=request, site=site, fs_proj_xf=fs_proj_xf,
            proj_id=proj_id, xform=xform)
    except InstanceInvalidUserError:
        error = OpenRosaResponseBadRequest(_(u"Username or ID required."))
    except InstanceEmptyError:
        error = OpenRosaResponseBadRequest(
            _(u"Received empty submission. No instance was created")
        )
    except FormInactiveError:
        error = OpenRosaResponseNotAllowed(_(u"Form is not active"))
    except XForm.DoesNotExist:
        error = OpenRosaResponseNotFound(
            _(u"Form does not exist on this account")
        )
    except ExpatError as e:
        error = OpenRosaResponseBadRequest(_(u"Improperly formatted XML."))
    except AttributeError as e:
        error = OpenRosaResponseBadRequest(_(u"NO xml_submission_file."))
    except DuplicateInstance:
        response = OpenRosaResponse(_(u"Duplicate submission"))
        response.status_code = 202
        response['Location'] = request.build_absolute_uri(request.path)
        error = response
    except PermissionDenied as e:
        error = OpenRosaResponseForbidden(e)
    except InstanceMultipleNodeError as e:
        error = OpenRosaResponseBadRequest(e)
    except DjangoUnicodeDecodeError:
        error = OpenRosaResponseBadRequest(_(u"File likely corrupted during "
                                             u"transmission, please try later."
                                             ))

    return [error, instance]


def report_exception(subject, info, exc_info=None):
    if exc_info:
        cls, err = exc_info[:2]
        message = _(u"Exception in request:"
                    u" %(class)s: %(error)s")\
            % {'class': cls.__name__, 'error': err}
        message += u"".join(traceback.format_exception(*exc_info))
    else:
        message = u"%s" % info

    if settings.DEBUG or settings.TESTING_MODE:
        sys.stdout.write("Subject: %s\n" % subject)
        sys.stdout.write("Message: %s\n" % message)
    else:
        mail_admins(subject=subject, message=message)


def response_with_mimetype_and_name(
        mimetype, name, extension=None, show_date=True, file_path=None,
        use_local_filesystem=False, full_mime=False):
    if extension is None:
        extension = mimetype
    if not full_mime:
        mimetype = "application/%s" % mimetype
    if file_path:
        try:
            if not use_local_filesystem:
                default_storage = get_storage_class()()
                wrapper = FileWrapper(default_storage.open(file_path))
                response = StreamingHttpResponse(wrapper,
                                                 content_type=mimetype)
                response['Content-Length'] = default_storage.size(file_path)
            else:
                wrapper = FileWrapper(open(file_path))
                response = StreamingHttpResponse(wrapper,
                                                 content_type=mimetype)
                response['Content-Length'] = os.path.getsize(file_path)
        except IOError:
            response = HttpResponseNotFound(
                _(u"The requested file could not be found."))
    else:
        response = HttpResponse(content_type=mimetype)
    response['Content-Disposition'] = disposition_ext_and_date(
        name, extension, show_date)
    return response


def disposition_ext_and_date(name, extension, show_date=True):
    if name is None:
        return 'attachment;'
    if show_date:
        name = "%s_%s" % (name, date.today().strftime("%Y_%m_%d"))
    return 'attachment; filename=%s.%s' % (name, extension)


def store_temp_file(data):
    tmp = tempfile.TemporaryFile()
    ret = None
    try:
        tmp.write(data)
        tmp.seek(0)
        ret = tmp
    finally:
        tmp.close()
    return ret


def publish_form(callback):
    try:
        return callback()
    except (PyXFormError, XLSFormError) as e:
        return {
            'type': 'alert-error',
            'text': unicode(e)
        }
    except IntegrityError as e:
        return {
            'type': 'alert-error',
            'text': _(u'Form with this id or SMS-keyword already exists.'),
        }
    except ValidationError as e:
        # on clone invalid URL
        return {
            'type': 'alert-error',
            'text': _(u'Invalid URL format.'),
        }
    except AttributeError as e:
        # form.publish returned None, not sure why...
        return {
            'type': 'alert-error',
            'text': unicode(e)
        }
    except ProcessTimedOut as e:
        # catch timeout errors
        return {
            'type': 'alert-error',
            'text': _(u'Form validation timeout, please try again.'),
        }
    except Exception as e:
        # TODO: Something less horrible. This masks storage backend
        # `ImportError`s and who knows what else

        # ODK validation errors are vanilla errors and it masks a lot of regular
        # errors if we try to catch it so let's catch it, BUT reraise it
        # if we don't see typical ODK validation error messages in it.
        if u"ODK Validate Errors" not in e.message:
            raise

        # error in the XLS file; show an error to the user
        return {
            'type': 'alert-error',
            'text': unicode(e)
        }


def publish_xls_form(xls_file, user, id_string=None):
    """ Creates or updates a DataDictionary with supplied xls_file,
        user and optional id_string - if updating
    """
    # get or create DataDictionary based on user and id string
    if id_string:
        dd = DataDictionary.objects.get(
            user=user, id_string=id_string)
        dd.xls = xls_file
        dd.save()
        return dd
    else:
        return DataDictionary.objects.create(
            user=user,
            xls=xls_file
        )


def publish_xml_form(xml_file, user, id_string=None):
    xml = xml_file.read()
    survey = create_survey_element_from_xml(xml)
    form_json = survey.to_json()
    if id_string:
        dd = DataDictionary.objects.get(user=user, id_string=id_string)
        dd.xml = xml
        dd.json = form_json
        dd._mark_start_time_boolean()
        set_uuid(dd)
        dd._set_uuid_in_xml()
        dd.save()
        return dd
    else:
        dd = DataDictionary(user=user, xml=xml, json=form_json)
        dd._mark_start_time_boolean()
        set_uuid(dd)
        dd._set_uuid_in_xml(file_name=xml_file.name)
        dd.save()
        return dd


class BaseOpenRosaResponse(HttpResponse):
    status_code = 201

    def __init__(self, *args, **kwargs):
        super(BaseOpenRosaResponse, self).__init__(*args, **kwargs)

        self[OPEN_ROSA_VERSION_HEADER] = OPEN_ROSA_VERSION
        tz = pytz.timezone(settings.TIME_ZONE)
        dt = datetime.now(tz).strftime('%a, %d %b %Y %H:%M:%S %Z')
        self['Date'] = dt
        self['X-OpenRosa-Accept-Content-Length'] = DEFAULT_CONTENT_LENGTH
        self['Content-Type'] = DEFAULT_CONTENT_TYPE


class OpenRosaResponse(BaseOpenRosaResponse):
    status_code = 201

    def __init__(self, *args, **kwargs):
        super(OpenRosaResponse, self).__init__(*args, **kwargs)
        # wrap content around xml
        self.content = '''<?xml version='1.0' encoding='UTF-8' ?>
<OpenRosaResponse xmlns="http://openrosa.org/http/response">
        <message nature="">%s</message>
</OpenRosaResponse>''' % self.content


class OpenRosaResponseNotFound(OpenRosaResponse):
    status_code = 404


class OpenRosaResponseBadRequest(OpenRosaResponse):
    status_code = 400


class OpenRosaResponseNotAllowed(OpenRosaResponse):
    status_code = 405


class OpenRosaResponseForbidden(OpenRosaResponse):
    status_code = 403


def inject_instanceid(xml_str, uuid):
    if get_uuid_from_xml(xml_str) is None:
        xml = clean_and_parse_xml(xml_str)
        children = xml.childNodes
        if children.length == 0:
            raise ValueError(_("XML string must have a survey element."))

        # check if we have a meta tag
        survey_node = children.item(0)
        meta_tags = [
            n for n in survey_node.childNodes
            if n.nodeType == Node.ELEMENT_NODE
            and n.tagName.lower() == "meta"]
        if len(meta_tags) == 0:
            meta_tag = xml.createElement("meta")
            xml.documentElement.appendChild(meta_tag)
        else:
            meta_tag = meta_tags[0]

        # check if we have an instanceID tag
        uuid_tags = [
            n for n in meta_tag.childNodes
            if n.nodeType == Node.ELEMENT_NODE
            and n.tagName == "instanceID"]
        if len(uuid_tags) == 0:
            uuid_tag = xml.createElement("instanceID")
            meta_tag.appendChild(uuid_tag)
        else:
            uuid_tag = uuid_tags[0]
        # insert meta and instanceID
        text_node = xml.createTextNode(u"uuid:%s" % uuid)
        uuid_tag.appendChild(text_node)
        return xml.toxml()
    return xml_str


def update_mongo_for_xform(xform, only_update_missing=True):
    instance_ids = set(
        [i.id for i in Instance.objects.only('id').filter(xform=xform)])
    sys.stdout.write("Total no of instances: %d\n" % len(instance_ids))
    mongo_ids = set()
    user = xform.user
    userform_id = "%s_%s" % (user.username, xform.id_string)
    if only_update_missing:
        sys.stdout.write("Only updating missing mongo instances\n")
        mongo_ids = set(
            [rec[common_tags.ID] for rec in mongo_instances.find(
                {common_tags.USERFORM_ID: userform_id},
                {common_tags.ID: 1})])
        sys.stdout.write("Total no of mongo instances: %d\n" % len(mongo_ids))
        # get the difference
        instance_ids = instance_ids.difference(mongo_ids)
    else:
        # clear mongo records
        mongo_instances.remove({common_tags.USERFORM_ID: userform_id})
    # get instances
    sys.stdout.write(
        "Total no of instances to update: %d\n" % len(instance_ids))
    instances = Instance.objects.only('id').in_bulk(
        [id for id in instance_ids])
    total = len(instances)
    done = 0
    for id, instance in instances.items():
        (pi, created) = ParsedInstance.objects.get_or_create(instance=instance)
        pi.save(async=False)
        done += 1
        # if 1000 records are done, flush mongo
        if (done % 1000) == 0:
            sys.stdout.write(
                'Updated %d records, flushing MongoDB...\n' % done)
        settings.MONGO_CONNECTION.admin.command({'fsync': 1})
        progress = "\r%.2f %% done..." % ((float(done) / float(total)) * 100)
        sys.stdout.write(progress)
        sys.stdout.flush()
    # flush mongo again when done
    settings.MONGO_CONNECTION.admin.command({'fsync': 1})
    sys.stdout.write(
        "\nUpdated %s\n------------------------------------------\n"
        % xform.id_string)


def mongo_sync_status(remongo=False, update_all=False, user=None, xform=None):
    """Check the status of records in the mysql db versus mongodb. At a
    minimum, return a report (string) of the results.

    Optionally, take action to correct the differences, based on these
    parameters, if present and defined:

    remongo    -> if True, update the records missing in mongodb
                  (default: False)
    update_all -> if True, update all the relevant records (default: False)
    user       -> if specified, apply only to the forms for the given user
                  (default: None)
    xform      -> if specified, apply only to the given form (default: None)

    """

    qs = XForm.objects.only('id_string', 'user').select_related('user')
    if user and not xform:
        qs = qs.filter(user=user)
    elif user and xform:
        qs = qs.filter(user=user, id_string=xform.id_string)
    else:
        qs = qs.all()

    total = qs.count()
    found = 0
    done = 0
    total_to_remongo = 0
    report_string = ""
    for xform in queryset_iterator(qs, 100):
        # get the count
        user = xform.user
        instance_count = Instance.objects.filter(xform=xform).count()
        userform_id = "%s_%s" % (user.username, xform.id_string)
        mongo_count = mongo_instances.find(
            {common_tags.USERFORM_ID: userform_id}).count()

        if instance_count != mongo_count or update_all:
            line = "user: %s, id_string: %s\nInstance count: %d\t"\
                   "Mongo count: %d\n---------------------------------"\
                   "-----\n" % (
                       user.username, xform.id_string, instance_count,
                       mongo_count)
            report_string += line
            found += 1
            total_to_remongo += (instance_count - mongo_count)

            # should we remongo
            if remongo or (remongo and update_all):
                if update_all:
                    sys.stdout.write(
                        "Updating all records for %s\n--------------------"
                        "---------------------------\n" % xform.id_string)
                else:
                    sys.stdout.write(
                        "Updating missing records for %s\n----------------"
                        "-------------------------------\n"
                        % xform.id_string)
                update_mongo_for_xform(
                    xform, only_update_missing=not update_all)
        done += 1
        sys.stdout.write(
            "%.2f %% done ...\r" % ((float(done) / float(total)) * 100))
    # only show stats if we are not updating mongo, the update function
    # will show progress
    if not remongo:
        line = "Total # of forms out of sync: %d\n" \
            "Total # of records to remongo: %d\n" % (found, total_to_remongo)
        report_string += line
    return report_string


def remove_xform(xform):
    # disconnect parsed instance pre delete signal
    pre_delete.disconnect(_remove_from_mongo, sender=ParsedInstance)

    # delete instances from mongo db
    query = {
        ParsedInstance.USERFORM_ID:
        "%s_%s" % (xform.user.username, xform.id_string)}
    xform_instances.remove(query, j=True)

    # delete xform, and all related models
    xform.delete()

    # reconnect parsed instance pre delete signal?
    pre_delete.connect(_remove_from_mongo, sender=ParsedInstance)