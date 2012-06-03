===========
Django Jamboree
===========

Django jamboree exports your django models to Google Fusion Tables.

To install in your virtual environment:

    pip install -e git+git@github.com:shuggiefisher/django-jamboree.git#egg=django-jamboree

and add 'jamboree' to your INSTALLED_APPS in settings.py

Add a file named pyftconfig.py to the root of your project containing:

    PYFT_GOOGLE_USERNAME="myaccount@gmail.com"
    PYFT_GOOGLE_PASSWORD="mypassword"

To export a model to a Google Fusion Table, find the FusionTableExport model in the admin interface.
Use the admin interface a choose a model from your django application and it will be exported to a fusion table.
When the export has finished, a link to the fusion table will appear in the admin interface.
Any changes to you django model will now be reflected in the fusion table.