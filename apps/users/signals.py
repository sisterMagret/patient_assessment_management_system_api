# from django.db.models.signals import post_save
# from django.dispatch import receiver

# from .models import  VendorHistoricalPerformance
# from django.utils import timezone
# from django.apps import apps


# PurchaseOrder = apps.get_model("purchase_orders.PurchaseOrder")


# @receiver(post_save, sender=PurchaseOrder)
# def update_performance_metrics(sender, instance, created, **kwargs):
#     if instance.status == 'completed' and instance.vendor :
#         performance_metrics = instance.vendor.calculate_performance_metrics #calculate_performance_metrics(instance.vendor)
#         VendorHistoricalPerformance.objects.create(
#             vendor=instance.vendor,
#             date=timezone.now(),
#             on_time_delivery_rate=performance_metrics['on_time_delivery_rate'],
#             quality_rating_avg=performance_metrics['quality_rating_avg'],
#             average_response_time=(performance_metrics['average_response_time']),
#             fulfillment_rate=performance_metrics['fulfillment_rate']
#         )
