from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.db import transaction

from hr.models.employees import Employee
from hr.models.careers import CareerHistory


@receiver(post_save, sender=Employee)
def employee_post_save(sender, instance, created, **kwargs):
    """
    Signal handler to create or update CareerHistory records when an Employee is saved.
    
    When an employee is created or their organization unity/position changes, a new CareerHistory
    record is created to track these changes.
    """
    # Check if we need to create a new CareerHistory entry
    create_new_entry = False
    
    if created:
        # For newly created employees with a organization unity or position
        if instance.org_unit is not None or instance.position is not None:
            create_new_entry = True
    else:
        # For existing employees, check if  or position has changed
        try:
            # Get the latest career history for this employee
            latest_history = CareerHistory.objects.filter(
                employee=instance
            ).order_by('-start_date').first()
            
            if latest_history:
                # Check if organization unity or position changed
                org_unit_changed = latest_history.org_unit != instance.org_unit
                pos_changed = latest_history.position != instance.position
                
                if org_unit_changed or pos_changed:
                    # Close the current entry by setting end_date
                    with transaction.atomic():
                        latest_history.end_date = timezone.now().date()
                        latest_history.save()
                    create_new_entry = True
            else:
                # No history exists yet, but employee has organization unity or position
                if instance.org_unit is not None or instance.position is not None:
                    create_new_entry = True
                    
        except CareerHistory.DoesNotExist:
            # No history exists yet, but employee has organization unity or position
            if instance.org_unit is not None or instance.position is not None:
                create_new_entry = True
    
    # Create a new CareerHistory if needed
    if create_new_entry:
        with transaction.atomic():
            CareerHistory.objects.create(
                employee=instance,
                org_unit=instance.org_unit,
                position=instance.position,
                start_date=timezone.now().date(),
                end_date=None,  # Current position has no end date
                description=f"{'Nouveau(elle) Employé(e)' if created else 'Fonction/Département modifié(e)'}",
                created_by=instance.created_by,
                updated_by=instance.updated_by,
            )
