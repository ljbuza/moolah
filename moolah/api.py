from rest_framework.routers import DefaultRouter

from tracking.views import TransactionViewSet, AllowanceTransactionViewSet
from reporting.views import ReportViewSet
from tracking.views import CategoryViewSet


ROUTER = DefaultRouter()
ROUTER.register('transactions', TransactionViewSet)
ROUTER.register('purchases', AllowanceTransactionViewSet, 'purchase')
ROUTER.register('reports', ReportViewSet, 'reports')
ROUTER.register('categories', CategoryViewSet, 'category')
