def calculate_cart_final_total(items_total_price, tax_rate, shipping_weight_lbs):
    if items_total_price < 0 or tax_rate < 0 or shipping_weight_lbs < 0:
        return ValueError("Inputs Cannot contain negative values")
    if tax_rate > 1.0:
        raise ValueError("Tax rate must be expressed as a decimal multiplier less than or equal to 1.0.")

    # Calculate price with tax applied
    taxed_subtotal = items_total_price * (1 + tax_rate)
    
    # Calculate shipping costs based on weight thresholds
    if shipping_weight_lbs > 20.0:
        shipping_fee = 5.00 + 15.00  # Base fee + heavy surcharge
    else:
        shipping_fee = 5.00  # Standard flat fee
        
    return round(taxed_subtotal + shipping_fee, 2)