from django.shortcuts import render
from rest_framework import viewsets,status
from rest_framework.views import APIView,Response
from .models import Warehouse,Supplier,InventoryItem
from .serializers import WarehouseInventorySerializer,InventoryTransferInputSerializer,SupplierSerializer,InventoryItemDetailSerializer
from .services import InventoryTransferService
# Create your views here.

class WarehouseInventoryViewSet(viewsets. ReadOnlyModelViewSet):
    serializer_class = WarehouseInventorySerializer
    def get_queryset(self):
        return Warehouse.objects.prefetch_related('stock_levels__inventory_item').all()
    

class InventoryTransferAPIView(APIView):
    def post(self,request, *args,**kwargs):
        serializer = InventoryTransferInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        message = InventoryTransferService.exectue_transfer(
            from_warehouse_id= serializer._validated_data['from_warehouse_id'],
            to_warehouse_id=serializer.validated_data['to_warehouse_id'],
            inventory_item_id=serializer.validated_data['inventory_item_id'],
            qty_to_move=serializer.validated_data['quantiry']
        )
        return Response({"Status":"Transaction Processed","detail":message},status = status.HTTP_201_CREATED)
    
class SupplierAPIViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    
class InventoryItemViewSet(viewsets.ModelViewSet):
    queryset = InventoryItem.objects.all()
    serializer_class = InventoryItemDetailSerializer
    