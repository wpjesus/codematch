# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('requests', '0002_auto_20150717_0929'),
    ]

    operations = [
        migrations.RenameField(
            model_name='coderequest',
            old_name='coder',
            new_name='mentor',
        ),
    ]
