*****
FieldSight
*****
FieldSight is a platform, built on top of  `KoBoToolbox <https://fieldsight.org>`_.It enables field-based staff to collect information and communicate directly with project managers and engineers to track construction progress in real-time and identify and fix errors as they occur. Designed to work off-line and at scale, FieldSight is specifically targeted for humanitarian and development projects.

*****
Learn more about FieldSight
*****
FieldSight website: `https://fieldsight.org <https://fieldsight.org>`_

Code Structure
--------------
* **fieldsight** - This app is the base for organization project sites hierarchy, and people involved in them.


* **fsforms** - This app is the base for forms Categories like Stages, Survey, General, Schedules forms.


* **logger** - This app serves XForms to and receives submissions from
  ODK Collect and Enketo.

* **viewer** - This app provides a csv and xls export of the data stored in
  logger. This app uses a data dictionary as produced by pyxform. It also
  provides a map and single survey view.

* **main** - This app is the glue that brings logger and viewer
  together.

Localization
------------

To generate a locale from scratch (ex. Spanish)

.. code-block:: sh

    $ django-admin.py makemessages -l es -e py,html,email,txt ;
    $ for app in {main,viewer} ; do cd kobocat/apps/${app} && django-admin.py makemessages -d djangojs -l es && cd - ; done

To update PO files

.. code-block:: sh

    $ django-admin.py makemessages -a ;
    $ for app in {main,viewer} ; do cd kobocat/apps/${app} && django-admin.py makemessages -d djangojs -a && cd - ; done

To compile MO files and update live translations

.. code-block:: sh

    $ django-admin.py compilemessages ;
    $ for app in {main,viewer} ; do cd kobocat/apps/${app} && django-admin.py compilemessages && cd - ; done
    
