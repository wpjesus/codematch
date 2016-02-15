# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('matches', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='projectcontainer',
            name='docs',
            field=models.CharField(max_length=300),
            preserve_default=True,
        ),
    ]
