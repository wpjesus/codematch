# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('requests', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='coderequest',
            old_name='Additional_information',
            new_name='additional_information',
        ),
        migrations.RenameField(
            model_name='coderequest',
            old_name='user',
            new_name='coder',
        ),
        migrations.RenameField(
            model_name='coderequest',
            old_name='time',
            new_name='creation_date',
        ),
        migrations.RenameField(
            model_name='coderequest',
            old_name='Estimated_LoF',
            new_name='estimated_lof',
        ),
    ]
