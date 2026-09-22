# Migration 0039 — Renomme la modalité GROSS en BASE pour salary_base_type.
#
# Contexte : sur EmployeeContract.salary_base_type, la valeur « GROSS » est
# recadrée sémantiquement. Le montant négocié n'est pas le « brut de période »
# (variable) mais une base de référence avant déductions. On l'appelle BASE
# pour lever l'ambiguïté avec le brut mensuel (calculé).
#
# Le calcul (orchestrator._step2_calculate_earnings) ne teste que
# `salary_base_type == NET` (brutage) ; le reste est traité comme base directe.
# → Les lignes GROSS existantes deviennent BASE sans changement de comportement.

from django.db import migrations, models


def convert_gross_to_base(apps, schema_editor):
    EmployeeContract = apps.get_model('hr_payroll', 'EmployeeContract')
    EmployeeContract.objects.filter(salary_base_type='GROSS').update(salary_base_type='BASE')


def convert_base_to_gross(apps, schema_editor):
    EmployeeContract = apps.get_model('hr_payroll', 'EmployeeContract')
    EmployeeContract.objects.filter(salary_base_type='BASE').update(salary_base_type='GROSS')


class Migration(migrations.Migration):

    dependencies = [
        ('hr_payroll', '0038_remove_professional_category'),
    ]

    operations = [
        migrations.RunPython(convert_gross_to_base, convert_base_to_gross),
        migrations.AlterField(
            model_name='employeecontract',
            name='salary_base_type',
            field=models.CharField(
                choices=[('BASE', 'Salaire de base'), ('NET', 'Salaire Net (brutage)')],
                default='BASE',
                help_text='Base de référence : NET (brutage à appliquer) ou BASE (avant déductions).',
                max_length=10,
                verbose_name='Salary Base Type',
            ),
        ),
    ]
