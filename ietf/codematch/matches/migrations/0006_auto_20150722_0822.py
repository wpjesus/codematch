# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('matches', '0005_auto_20150721_1241'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='codingproject',
            name='project_container',
        ),
        migrations.AddField(
            model_name='projectcontainer',
            name='codings',
            field=models.ManyToManyField(to='matches.CodingProject'),
            preserve_default=True,
        ),
    ]
