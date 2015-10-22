# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('matches', '0004_auto_20151014_1202'),
    ]

    operations = [
        migrations.AlterField(
            model_name='projectmail',
            name='mail',
            field=models.CharField(max_length=80),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='projectmail',
            name='type',
            field=models.CharField(max_length=50, choices=[(b'Twitter', b'Twitter'), (b'Facebook', b'Facebook'), (b'Jabber', b'Jabber'), (b'Mail', b'Email')]),
            preserve_default=True,
        ),
    ]
