from rest_framework import viewsets
from rest_framework.decorators import list_route
from rest_framework.response import Response

from models import Allowance, Transaction, Category
from serializers import TransactionSerializer, AllowanceTransactionSerializer, CategorySerializer


class TransactionViewSet(viewsets.ModelViewSet):
    '''
    Transactions not associated with an allowance
    '''
    queryset = Transaction.objects.without_allowance()
    serializer_class = TransactionSerializer

    def get_queryset(self, *args, **kwargs):
        return self.queryset.today()


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_queryset(self):
        return Category.objects.all()
    # def get_queryset(self):
        # return Category.objects.get(user=self.request.user)


class AllowanceTransactionViewSet(viewsets.ModelViewSet):
    '''
    Transactions associated with the current user's allowance
    '''
    queryset = Transaction.objects.with_allowance()
    serializer_class = AllowanceTransactionSerializer

    def get_users_allowance(self):
        return Allowance.objects.get(user=self.request.user)

    def get_queryset(self, *args, **kwargs):
        qs = super(AllowanceTransactionViewSet, self).get_queryset(*args, **
                                                                   kwargs)
        return qs.filter(allowance=self.get_users_allowance()).last_month()

    @list_route(methods=['get'])
    def total(self, *args, **kwargs):
        everything = self.queryset.filter(allowance=self.get_users_allowance())
        return Response({'balance': everything.total()})
