# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('legislature', '0002_action_bill'),
    ]

    operations = [
        migrations.AddField(
            model_name='bill',
            name='slug',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
    ]
