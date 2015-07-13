# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.files.storage
import ietf.nomcom.models


class Migration(migrations.Migration):

    dependencies = [
        ('nomcom', '0002_auto_20150430_0909'),
    ]

    operations = [
        migrations.AlterField(
            model_name='nomcom',
            name='public_key',
            field=models.FileField(storage=django.core.files.storage.FileSystemStorage(location=b'<local path to where you want to keep the files below>/nomcom_keys/public_keys'), null=True, upload_to=ietf.nomcom.models.upload_path_handler, blank=True),
            preserve_default=True,
        ),
    ]
