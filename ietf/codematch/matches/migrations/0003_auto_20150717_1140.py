# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('matches', '0002_auto_20150717_0919'),
    ]

    operations = [
        migrations.AlterField(
            model_name='projectcontainer',
            name='title',
            field=models.CharField(max_length=80, verbose_name='Title'),
            preserve_default=True,
        ),
    ]
