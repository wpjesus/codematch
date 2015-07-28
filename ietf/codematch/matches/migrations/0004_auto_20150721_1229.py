# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('matches', '0003_auto_20150717_1140'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='codingproject',
            name='project_container',
        ),
        migrations.AddField(
            model_name='projectcontainer',
            name='code_project',
            field=models.ManyToManyField(to='matches.CodingProject'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='projectcontainer',
            name='title',
            field=models.CharField(max_length=80),
            preserve_default=True,
        ),
    ]
