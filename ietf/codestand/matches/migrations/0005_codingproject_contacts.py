# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('matches', '0004_remove_projectcontainer_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='codingproject',
            name='contacts',
            field=models.ManyToManyField(to='matches.ProjectContact', null=True, blank=True),
            preserve_default=True,
        ),
    ]
