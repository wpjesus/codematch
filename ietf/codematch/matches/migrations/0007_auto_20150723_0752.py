# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('matches', '0006_auto_20150722_0822'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='projectcontainer',
            name='coder',
        ),
        migrations.AddField(
            model_name='codingproject',
            name='reputation',
            field=models.IntegerField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
