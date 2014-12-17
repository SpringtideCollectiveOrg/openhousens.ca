# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Action',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('description', models.TextField()),
                ('date', models.DateField(null=True, blank=True)),
                ('text', models.TextField(null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Bill',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('identifier', models.PositiveIntegerField()),
                ('title', models.TextField()),
                ('description', models.TextField()),
                ('classification', models.TextField()),
                ('modified', models.DateField()),
                ('status', models.CharField(choices=[('1st', 'First Reading'), ('2nd', 'Second Reading'), ('LA', 'Law Amendments Committee'), ('PL', 'Private & Local Bills Committee'), ('WH', 'Committee of the Whole House'), ('3rd', 'Third Reading'), ('RA', 'Royal Assent')], max_length=3)),
                ('url', models.URLField()),
                ('law_amendments_committee_submissions_url', models.URLField()),
                ('creator', models.ForeignKey(to='speeches.Speaker', null=True, on_delete=django.db.models.deletion.SET_NULL, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
