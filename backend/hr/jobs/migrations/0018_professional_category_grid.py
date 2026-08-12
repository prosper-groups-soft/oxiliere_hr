import django.core.validators
import django.db.models.deletion
import oxutils.models.fields
import uuid6
from django.conf import settings
from django.db import migrations, models


def copy_professional_categories(apps, schema_editor):
    """Copie la grille depuis hr_payroll.professionalcategory vers hr_jobs.

    La table payroll existe encore à ce stade (sa suppression est dans la
    migration hr_payroll suivante, qui dépend de celle-ci).

    Les PK SOURCES sont préservés : la fixture de reset (professional_categories.json)
    utilise des PK fixes (uuid 019c04a1...) — garder les mêmes PK garantit que
    les FK de SeniorityLevel/PositionSeniority vers la grille restent valides
    après un reset.

    NB : les anciens champs `SeniorityLevel.classe`/`PositionSeniority.echelon`
    de jobs n'ont jamais été alimentés (NULL) par les services — aucun mapping
    rétroactif n'est nécessaire, la grille jobs est la source de vérité.
    """
    PayrollCat = apps.get_model('hr_payroll', 'ProfessionalCategory')
    JobsCat = apps.get_model('hr_jobs', 'ProfessionalCategory')

    for src in PayrollCat.objects.all().order_by('classe', 'echelon'):
        JobsCat.objects.create(
            pk=src.pk,  # Préserver le PK — cohérent avec la fixture de reset
            classe=src.classe,
            echelon=src.echelon,
            label=src.label,
            application=src.application,
            is_active=src.is_active,
        )


def noop(apps, schema_editor):
    """Reverse : rien à faire (les données payroll sont conservées)."""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('hr_jobs', '0017_positionseniority_echelon_senioritylevel_classe'),
        ('hr_payroll', '0035_professionalcategory'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='senioritylevel',
            name='classe',
        ),
        migrations.CreateModel(
            name='ProfessionalCategory',
            fields=[
                ('deleted', models.DateTimeField(db_index=True, editable=False, null=True)),
                ('deleted_by_cascade', models.BooleanField(default=False, editable=False)),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='Date and time when this record was created')),
                ('updated_at', models.DateTimeField(auto_now=True, help_text='Date and time when this record was last updated')),
                ('_masked_backup', oxutils.models.fields.MaskedBackupField(default=dict, editable=False)),
                ('id', models.UUIDField(default=uuid6.uuid7, editable=False, primary_key=True, serialize=False)),
                ('classe', models.PositiveSmallIntegerField(help_text='Classe professionnelle RDC (1-7).', validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(7)], verbose_name='Classe')),
                ('echelon', models.PositiveSmallIntegerField(help_text='Échelon dans la classe (1-4).', validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(4)], verbose_name='Échelon')),
                ('label', models.CharField(help_text='Libellé de la classe (ex. Manœuvre ordinaire, Cadre moyen).', max_length=120, verbose_name='Libellé')),
                ('application', models.TextField(blank=True, default='', help_text='Profil de personnel concerné (ex. Personnel non qualifié).', verbose_name='Application')),
                ('is_active', models.BooleanField(default=True, help_text='La classe/échelon est applicable pour les nouveaux contrats.', verbose_name='Active')),
                ('created_by', models.ForeignKey(blank=True, help_text='User who created this record', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_created', to=settings.AUTH_USER_MODEL)),
                ('updated_by', models.ForeignKey(blank=True, help_text='User who last updated this record', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='%(app_label)s_%(class)s_updated', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Catégorie professionnelle',
                'verbose_name_plural': 'Catégories professionnelles',
                'db_table': 'jobs_professional_category',
                'ordering': ['classe', 'echelon'],
            },
        ),
        migrations.AddField(
            model_name='positionseniority',
            name='professional_category',
            field=models.ForeignKey(blank=True, help_text='Ligne (classe, échelon) de la grille des catégories professionnelles.', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='position_seniorities', to='hr_jobs.professionalcategory', verbose_name='Catégorie professionnelle'),
        ),
        migrations.AddField(
            model_name='senioritylevel',
            name='professional_category',
            field=models.ForeignKey(blank=True, help_text='Classe RDC (1-7) de la grille des catégories professionnelles.', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='seniority_levels', to='hr_jobs.professionalcategory', verbose_name='Catégorie professionnelle'),
        ),
        migrations.AddConstraint(
            model_name='professionalcategory',
            constraint=models.UniqueConstraint(condition=models.Q(('deleted__isnull', True)), fields=('classe', 'echelon'), name='unique_jobs_professional_category_class_echelon'),
        ),
        migrations.RunPython(copy_professional_categories, noop),
    ]
