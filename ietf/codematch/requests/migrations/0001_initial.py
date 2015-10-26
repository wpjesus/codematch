# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('person', '0004_auto_20150308_0440'),
    ]

    operations = [
        migrations.CreateModel(
            name='CodeRequest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('estimated_lof', models.FloatField(null=True, blank=True)),
                ('additional_information', models.CharField(max_length=255, null=True, blank=True)),
                ('creation_date', models.DateTimeField(auto_now_add=True)),
                ('mentor', models.ForeignKey(blank=True, to='person.Person', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
