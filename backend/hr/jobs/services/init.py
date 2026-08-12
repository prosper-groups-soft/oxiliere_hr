"""Initialisation / reset de la grille des catégories professionnelles (jobs).

Recharge la grille légale RDC (7 classes × 4 échelons) depuis la fixture
`hr/fixtures/jobs/cd/professional_categories.json` — pattern identique au
service d'init payroll (`hr.payroll.services.init`), exécuté par tenant
(django-tenants : chaque schéma a sa propre grille).
"""
import json
import logging
from pathlib import Path

from django.conf import settings

from hr.jobs.models import ProfessionalCategory
from safedelete import HARD_DELETE


logger = logging.getLogger(__name__)


def init_professional_categories() -> int:
    """Recharge la grille des catégories professionnelles depuis la fixture.

    Hard-delete les lignes existantes puis recrée depuis le JSON
    (PK préservés — les FK de SeniorityLevel/PositionSeniority restent valides).
    """
    fixture_path = Path(settings.BASE_DIR).parent / 'hr' / 'fixtures' / 'jobs' / 'cd' / 'professional_categories.json'

    logger.info("[Jobs] Loading professional categories fixture: %s", fixture_path)

    if not fixture_path.exists():
        logger.warning("Fixture file not found: %s", fixture_path)
        return 0

    with open(fixture_path, 'r', encoding='utf-8') as f:
        data_list = json.load(f)

    # Reset complet : hard delete pour éviter les conflits de contraintes uniques
    deleted_count, _ = ProfessionalCategory.objects.all_objects().delete(force_policy=HARD_DELETE)
    if deleted_count > 0:
        logger.info("[Jobs] Hard deleted %s existing professional categories", deleted_count)

    count = 0
    for item in data_list:
        fields = item.get('fields', {})
        pk = item.get('pk')
        try:
            ProfessionalCategory.objects.create(pk=pk, **fields)
            count += 1
        except Exception as e:
            logger.error("[Jobs] Error creating professional category PK %s: %s", pk, str(e))
            raise

    logger.info("[Jobs] Professional categories reset: %s entries reloaded", count)
    return count

