from django.db.models.signals import post_save
from django.dispatch import receiver
from pos_engine.models import Order
from inventory_supply.models import StockItem
from marketing_engagement.models import Campaign

@receiver(post_save, sender=Order)
def trigger_ecosystem_chain_reaction(sender, instance, created, **kwargs):
    if instance.status == 'PAID':
        print(f"💰 [FINANCIAL TRIGGER] Order {instance.id} paid. Syncing inventory stats...")
        
        # Check stock positions for low inventory warnings across applications
        for line_item in instance.items.all():
            item = line_item.menu_item
            if item.current_stock <= item.minimum_required:
                print(f"⚠️ [INVENTORY ALERT] {item.name} stock low ({item.current_stock} left).")
                
                # Automate marketing engagement lists adjustments on the fly
                Campaign.objects.create(
                    title=f"Restock Notice Campaign: Need more {item.name} supplies."
                )