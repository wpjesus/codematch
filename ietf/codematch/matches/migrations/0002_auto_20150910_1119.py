# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('matches', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='codingproject',
            name='links',
            field=models.ManyToManyField(to='matches.Implementation', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='projectcontainer',
            name='description',
            field=models.TextField(),
            preserve_default=True,
        ),
    ]
