# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('matches', '0003_auto_20151014_0829'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='projectmail',
            name='name',
        ),
        migrations.AddField(
            model_name='projectmail',
            name='mail',
            field=models.CharField(max_length=80, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='projectmail',
            name='type',
            field=models.CharField(blank=True, max_length=50, null=True, choices=[(b'twitter', b'Twitter'), (b'facebook', b'Facebook'), (b'jabber', b'Jabber'), (b'mail', b'Email')]),
            preserve_default=True,
        ),
    ]
