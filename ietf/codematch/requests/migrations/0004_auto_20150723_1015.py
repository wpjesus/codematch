# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('requests', '0003_auto_20150721_1143'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coderequest',
            name='mentor',
            field=models.CharField(max_length=80),
            preserve_default=True,
        ),
    ]
