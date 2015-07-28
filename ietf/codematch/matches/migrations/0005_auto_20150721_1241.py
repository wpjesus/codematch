# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('matches', '0004_auto_20150721_1229'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='projectcontainer',
            name='code_project',
        ),
        migrations.AddField(
            model_name='codingproject',
            name='project_container',
            field=models.ForeignKey(blank=True, to='matches.ProjectContainer', null=True),
            preserve_default=True,
        ),
    ]
