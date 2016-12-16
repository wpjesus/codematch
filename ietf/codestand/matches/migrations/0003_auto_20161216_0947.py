# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('matches', '0002_auto_20161129_0833'),
    ]

    operations = [
        migrations.AddField(
            model_name='projectcontainer',
            name='is_deleted',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='projectcontainer',
            name='status',
            field=models.IntegerField(default=0),
            preserve_default=True,
        ),
    ]
