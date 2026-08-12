from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('hr_payroll', '0037_remove_employeecontract_negotiated_salary_usd'),
        # La copie des données vers hr_jobs (RunPython dans 0018) doit précéder
        # la suppression de la table payroll.
        ('hr_jobs', '0018_professional_category_grid'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='professionalcategory',
            name='unique_professional_category_class_echelon',
        ),
        migrations.DeleteModel(
            name='ProfessionalCategory',
        ),
    ]
