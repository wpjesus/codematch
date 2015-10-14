# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('matches', '0002_auto_20150910_1119'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProjectMail',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
                ('type', models.CharField(max_length=50, choices=[(b'twitter', b'Twitter'), (b'facebook', b'Facebook'), (b'jabber', b'Jabber'), (b'mail', b'Email')])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='projectcontainer',
            name='mails',
            field=models.ManyToManyField(to='matches.ProjectMail', null=True, blank=True),
            preserve_default=True,
        ),
    ]
