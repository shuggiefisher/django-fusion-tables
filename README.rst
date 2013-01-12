===========
Django Fusion Tables
===========

Django Fusion Tables exports your django models to Google Fusion Tables.

To install in your virtual environment:

    pip install -e git+git@github.com:shuggiefisher/django-fusion-tables.git#egg=django-fusion-tables

Install the dependencies:

    pip install -e git+git@github.com:shuggiefisher/python-fusiontables@97983cea0f1e8c3bed6549212f39035cd3a32b31#egg=python-fusiontables
    pip install -e git+git@github.com:shuggiefisher/python-fusion-tables-client@bc89c03181ac800b20073a5ad2724c104aea0e68#egg=python-fusion-tables-client

and add 'djangofusiontables' to your INSTALLED_APPS in settings.py

Add a file named pyftconfig.py to the root of your project containing:

    PYFT_GOOGLE_USERNAME="myaccount@gmail.com"
    PYFT_GOOGLE_PASSWORD="mypassword"

To export a model to a Google Fusion Table

 1. Find the FusionTableExport model in the admin interface.
 2. Use the admin interface a choose a model from your django application and on save it will be exported to a fusion table.
 3. When the export has finished, a link to the fusion table will appear in the admin interface.

Any changes to your django model will now be reflected in the fusion table.
