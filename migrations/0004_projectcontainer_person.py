# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('person', '0004_auto_20150308_0440'),
        ('codematch', '0003_remove_projectcontainer_person'),
    ]

    operations = [
        migrations.AddField(
            model_name='projectcontainer',
            name='Person',
            field=models.ForeignKey(blank=True, to='person.Person', null=True),
            preserve_default=True,
        ),
    ]
