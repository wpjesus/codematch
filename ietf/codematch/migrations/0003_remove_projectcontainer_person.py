# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('codematch', '0002_projectcontainer_person'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='projectcontainer',
            name='Person',
        ),
    ]
