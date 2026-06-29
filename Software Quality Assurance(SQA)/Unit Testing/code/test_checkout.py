import unittest
from checkout_utils import calculate_cart_final_total

class ECommerceCheckoutUnitTests(unittest.TestCase):
    def test_standard_shipping_calculation(self):
        # Arrange
        cart_price = 100.00
        tax = 0.05
        weight = 10.0
        expected_total = 110.00
        
        # ACT
        actual_total = calculate_cart_final_total(cart_price, tax, weight)
        # Assert
        self.assertEqual(actual_total, expected_total)
        
def test_heavy_weight_shipping_surcharge(self):
    cart_price = 100.00
    tax = 0.05
    weight = 25.0   
    expected_total = 125.00  
    actual_total = calculate_cart_final_total(cart_price, tax, weight)

    self.assertEqual(actual_total, expected_total)
    
def test_negative_input_safeguard(self):
    with self.assertRaises(ValueError):
        calculate_cart_final_total(items_total_price=-10.00, tax_rate=0.05, shipping_weight_lbs=5.0)

def test_invalid_tax_rate_safeguard(self):
    with self.assertRaises(ValueError):
        calculate_cart_final_total(items_total_price=50.00, tax_rate=1.50, shipping_weight_lbs=5.0)