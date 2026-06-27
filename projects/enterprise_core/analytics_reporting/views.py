from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum, Count
from pos_engine.models import Order
from inventory_supply.models import WastageLog

class DashboardAnalyticsView(APIView):
    def get(self, request):
        # Perform arithmetic and mathematical aggregation purely at the database storage level
        sales_summary = Order.objects.filter(status='PAID').aggregate(
            total_revenue=Sum('items__quantity' * 'items__unit_price'),
            total_orders_processed=Count('id', distinct=True)
        )
        return Response(sales_summary)