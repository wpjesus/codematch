# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('matches', '0003_auto_20161216_0947'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='projectcontainer',
            name='status',
        ),
    ]
