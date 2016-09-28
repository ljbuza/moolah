from __future__ import unicode_literals

import datetime
from decimal import Decimal
from uuid import uuid4

from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone
from django.db import connections


class RateQuerySet(models.QuerySet):
    def total(self):
        return self.aggregate(models.Sum('amount_per_day'))[
            'amount_per_day__sum']


class Rate(models.Model):
    objects = RateQuerySet.as_manager()

    id = models.UUIDField(
        primary_key=True, editable=False, default=uuid4, unique=True)

    description = models.CharField(max_length=120)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    days = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    amount_per_day = models.DecimalField(
        max_digits=8, decimal_places=3, editable=False, blank=True)

    def rount_amount_per_day(self, place='0.01'):
        return Decimal(self.amount_per_day).quantize(Decimal(place))

    def save(self, *args, **kwargs):
        self.amount_per_day = self.amount / Decimal(self.days)
        return super(Rate, self).save(*args, **kwargs)

    def __unicode__(self):
        return '{0} ({1})'.format(self.description,
                                  self.rount_amount_per_day())


class Category(models.Model):
    id = models.UUIDField(
        primary_key=True, editable=False, default=uuid4, unique=True)
    user = models.ForeignKey(User)
    name = models.CharField(max_length=20)
    description = models.CharField(max_length=50)
    


class Allowance(models.Model):
    id = models.UUIDField(
        primary_key=True, editable=False, default=uuid4, unique=True)

    user = models.OneToOneField(User)
    amount = models.DecimalField(max_digits=8, decimal_places=2)

    def round_amount(self, place='0.01'):
        return Decimal(self.amount).quantize(Decimal(place))

    def __unicode__(self):
        return '{} - {}'.format(self.user.username, self.round_amount())


class TransactionQuerySet(models.QuerySet):
    def date(self, date):
        return self.filter(
            timestamp__month=date.month,
            timestamp__day=date.day,
            timestamp__year=date.year)

    def date_range(self, start_of_day, end_of_day):
        query_set = self

        if start_of_day:
            start_of_day = start_of_day.replace(hour=0, minute=0, second=59)
            query_set = query_set.filter(timestamp__gte=start_of_day)

        if end_of_day:
            end_of_day = end_of_day.replace(hour=23, minute=59, second=59)
            query_set = query_set.filter(timestamp__lte=end_of_day)

        return query_set

    def days_from_today(self, days):
        end = timezone.now()
        start = end - timezone.timedelta(days=days)
        return self.date_range(start, end)

    def today(self):
        now = timezone.localtime(timezone.now())
        now = datetime.datetime(now.year, now.month, now.day)
        tomorrow = now + datetime.timedelta(days=1)
        now, tomorrow = [timezone.make_aware(d) for d in [now, tomorrow]]
        return self.filter(timestamp__gte=now, timestamp__lt=tomorrow)

    def last_week(self):
        return self.days_from_today(7)

    def last_month(self):
        return self.days_from_today(30)

    def last_year(self):
        return self.days_from_today(365)

    def with_allowance(self):
        return self.filter(allowance__isnull=False)

    def without_allowance(self):
        return self.filter(allowance__isnull=True)

    def total(self):
        return self.aggregate(models.Sum('amount'))['amount__sum'] or 0


class TransactionCategory(models.Model):
    transaction = models.ForeignKey('Transaction', null=False)
    category = models.ForeignKey('Category', null=False)


class Transaction(models.Model):
    objects = TransactionQuerySet.as_manager()

    id = models.UUIDField(
        primary_key=True, editable=False, default=uuid4, unique=True)

    description = models.CharField(max_length=120)
    timestamp = models.DateTimeField(default=timezone.now)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    allowance = models.ForeignKey(Allowance, blank=True, null=True)
    categories = models.ManyToManyField('Category', through='TransactionCategory', blank=True)

    def round_amount(self, place='0.01'):
        return Decimal(self.amount).quantize(Decimal(place))

    def __unicode__(self):
        return '{} ({})'.format(self.description, self.round_amount())

    class Meta:
        ordering = ['-timestamp']
