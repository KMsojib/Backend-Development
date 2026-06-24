from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Supplier, Warehouse, InventoryItem, StockLevel, StockMovementLog

class InventoryIntegrationTestCase(APITestCase):
    
    def setUp(self):
        # 1. Create Supplier
        self.supplier = Supplier.objects.create(
            name="Logistics Corp",
            contact_email="test@corp.com",
        )
        
        # 2. Create Warehouses
        self.dhaka_wh = Warehouse.objects.create(
            name="Dhaka Hub",
            location_city="Dhaka",
            max_cubic_meters_capacity=1000
        )
        self.ctg_wh = Warehouse.objects.create(
            name="Chittagong Hub",
            location_city="Chittagong",
            max_cubic_meters_capacity=2000
        )
        
        # 3. Create Inventory Item
        self.item = InventoryItem.objects.create(
            title="Industrial Bolts",
            sku="BOLT-001",
            unit_cost=2.50,
            supplier=self.supplier
        )
        
        # 4. Set Initial Stock Level at Dhaka (Fix: Spelled threshold correctly)
        self.stock_dhaka = StockLevel.objects.create(
            warehouse=self.dhaka_wh,
            inventory_item=self.item,
            quantity=100,
            low_stock_threshold=10  
        )
        self.transfer_url = reverse('inventory-transfer')
        
    # All test methods below are now cleanly indented with 4 spaces inside the class
    def test_successful_inventory_transfer_integration(self):
        payload = {
            "from_warehouse_id": self.dhaka_wh.id,
            "to_warehouse_id": self.ctg_wh.id,
            "inventory_item_id": self.item.id,
            "quantity": 40
        }
        
        response = self.client.post(self.transfer_url, payload, format='json')
        
        # Assert Correct HTTP code
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Assert database updates executed correctly
        self.stock_dhaka.refresh_from_db()
        self.assertEqual(self.stock_dhaka.quantity, 60)
        
        # Assert destination stock was dynamically built and updated
        stock_ctg = StockLevel.objects.get(warehouse=self.ctg_wh, inventory_item=self.item)
        self.assertEqual(stock_ctg.quantity, 40)
        
        # Assert unalterable Audit Log entry ledger was generated
        log_exists = StockMovementLog.objects.filter(
            inventory_item=self.item,
            from_warehouse=self.dhaka_wh,
            to_warehouse=self.ctg_wh,
            quantity_moved=40
        ).exists()
        self.assertTrue(log_exists)
        
    def test_transfer_fails_on_matching_warehouses(self):
        payload = {
            "from_warehouse_id": self.dhaka_wh.id,
            "to_warehouse_id": self.dhaka_wh.id,  # Matching ID
            "inventory_item_id": self.item.id,
            "quantity": 10
        }
        response = self.client.post(self.transfer_url, payload, format='json')

        # Assert the request was blocked at the validation gate
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('destination_error', response.data)
        
    def test_transfer_fails_due_to_insufficient_stock(self):
        payload = {
            "from_warehouse_id": self.dhaka_wh.id,
            "to_warehouse_id": self.ctg_wh.id,
            "inventory_item_id": self.item.id,
            "quantity": 500
        }
        response = self.client.post(self.transfer_url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)