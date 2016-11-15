# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from onadata.apps.logger.models import XForm
#
# from onadata.apps.fsforms.models import FieldSightXF
#
#
# @receiver(post_save, sender=XForm)
# def save_to_fieldsight_form(sender, instance, **kwargs):
#     FieldSightXF.objects.create(xf=instance)
