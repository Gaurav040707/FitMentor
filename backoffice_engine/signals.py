from django.db.models.signals import post_migrate
from django.dispatch import receiver
from backoffice_engine.models import PlanDetails


@receiver(post_migrate)
def create_default_plans(sender, **kwargs):
    if sender.name != 'backoffice_engine':
        return

    default_plans = [
        {"name": "Free Plan", "description": "Basic access", "price": 0, "duration_days": 30},
       
        {"name": "Gold Plan", "description": "Extended features and support", "price": 999, "duration_days": 90},
        

    ]

    for plan in default_plans:
        print(f"{plan['name']}")
        PlanDetails.objects.get_or_create(name=plan["name"], defaults=plan)
