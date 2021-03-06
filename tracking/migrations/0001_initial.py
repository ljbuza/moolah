# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-07-04 04:43
from __future__ import unicode_literals

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Allowance',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=8)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Rate',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('description', models.CharField(max_length=120)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=8)),
                ('days', models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1)])),
                ('amount_per_day', models.DecimalField(blank=True, decimal_places=3, editable=False, max_digits=8)),
            ],
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('description', models.CharField(max_length=120)),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=8)),
                ('allowance', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='tracking.Allowance')),
            ],
            options={
                'ordering': ['-timestamp'],
            },
        ),
    ]
