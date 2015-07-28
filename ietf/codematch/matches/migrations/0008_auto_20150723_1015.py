# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('matches', '0007_auto_20150723_0752'),
    ]

    operations = [
        migrations.AlterField(
            model_name='codingproject',
            name='coder',
            field=models.CharField(max_length=80, null=True, blank=True),
            preserve_default=True,
        ),
    ]
