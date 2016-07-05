from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.reverse import reverse_lazy
from rest_framework.decorators import list_route
from dateutil.relativedelta import relativedelta, MO
from django.utils import timezone

from tracking.models import Transaction, Rate


class ReportViewSet(ViewSet):
    def list(self, *args, **kwargs):
        return Response({
            'summary': reverse_lazy('reports-summary', request=self.request),
            'savings': reverse_lazy('reports-savings', request=self.request),
            'rates': reverse_lazy('reports-rates', request=self.request),
            'week': reverse_lazy('reports-week', request=self.request),
        })

    @list_route(methods=['get'], url_path='summary')
    def summary(self, *args, **kwargs):
        transactions = Transaction.objects.without_allowance()
        return Response({
            'today': transactions.today().total(),
            'week': transactions.last_week().total(),
            'month': transactions.last_month().total(),
            'year': transactions.last_year().total(),
            'daily': Rate.objects.total()
        })

    @list_route(methods=['get'], url_path='savings')
    def savings(self, *args, **kwargs):
        transactions = Transaction.objects.without_allowance()
        today = timezone.now()
        labels = range(100, -1, -1)
        year_before_then = timezone.timedelta(days=-365)
        dates = [today + timezone.timedelta(days=-n) for n in labels]
        data = [transactions.date_range((d + year_before_then), d).total() for d in dates]
        return Response({
            'labels': labels,
            'data': [data],
            'series': []
        })

    @list_route(methods=['get'], url_path='week')
    def week_breakdown(self, *args, **kwargs):
        today = timezone.now()

        def get_week_dates(weeks=-1):
            monday = today + relativedelta(weekday=MO(weeks))
            return [
                monday + timezone.timedelta(days=n)
                for n in range(7)
            ]

        t = Transaction.objects.without_allowance()

        labels = [
            'Monday',
            'Tuesday',
            'Wednesday',
            'Thursday',
            'Friday',
            'Saturday',
            'Sunday'
        ]

        this_week = [
            t.date(d).total()
            for d in get_week_dates()
        ]

        last_week = [
            t.date(d).total()
            for d in get_week_dates(-2)
        ]

        return Response({
            'labels': labels,
            'data': [this_week, last_week],
            'series': ['This Week', 'Last Week']
        })

    @list_route(methods=['get'], url_path='rates')
    def rates_breakdown(self, *args, **kwargs):
        data = []
        labels = []
        for rate in Rate.objects.all():
            data.append(rate.amount_per_day)
            labels.append(rate.description)
        return Response({
            'labels': labels,
            'data': data
        })