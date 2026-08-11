"""
Calculateur de score automatique pour les evaluations de performance.

Formule documentee dans semantics.md :
    overall_score = (score_objectifs x goal_weight) + (score_competences x skill_weight)

    score_objectifs = (manager_rating_i x weight_i) / (weight_i)
    score_competences = (manager_level_i x weight_i) / (weight_i)

Regles :
- Les objectifs CANCELLED sont exclus du calcul
- Si manager_rating absent -> fallback sur employee_rating
- Si manager_level absent -> fallback sur employee_level
- Si aucun objectif note -> score_objectifs = 0
- Si aucune competence evaluee -> score_competences = 0
- Si goal_weight + skill_weight != 1 -> normalisation automatique
"""

import logging
from typing import Optional

from hr.performance.models import PerformanceReview


logger = logging.getLogger(__name__)


class ScoreCalculator:
    """Calcule le score final d'une evaluation selon la formule documentee."""

    GOAL_DEFAULT_WEIGHT = 0.6
    SKILL_DEFAULT_WEIGHT = 0.4

    @classmethod
    def calculate_overall_score(cls, review: PerformanceReview) -> Optional[float]:
        """
        Calcule et met a jour le overall_score d'une evaluation.

        Appele automatiquement apres soumission manager (MANAGER_DRAFT -> SUBMITTED).
        Retourne None si aucun calcul possible (aucun objectif ni competence evalue).
        """
        goal_weight = review.campaign.goal_weight if review.campaign else cls.GOAL_DEFAULT_WEIGHT
        skill_weight = review.campaign.skill_weight if review.campaign else cls.SKILL_DEFAULT_WEIGHT

        # Normalisation des poids si somme != 1
        total_weight = goal_weight + skill_weight
        if total_weight > 0 and abs(total_weight - 1.0) > 0.001:
            goal_weight /= total_weight
            skill_weight /= total_weight

        goals_score = cls._calculate_goals_score(review)
        skills_score = cls._calculate_skills_score(review)

        if goals_score is None and skills_score is None:
            return None

        goals_score = goals_score or 0.0
        skills_score = skills_score or 0.0

        overall = round((goals_score * goal_weight) + (skills_score * skill_weight), 2)

        logger.info(
            "Score calculated for review",
            extra={
                "review_id": review.id,
                "goals_score": goals_score,
                "skills_score": skills_score,
                "goal_weight": goal_weight,
                "skill_weight": skill_weight,
                "overall": overall,
            },
        )
        return overall

    @classmethod
    def _calculate_goals_score(cls, review: PerformanceReview) -> Optional[float]:
        """
        Calcule le score des objectifs.

        score_objectifs = (manager_rating_i x weight_i) / (weight_i)

        Fallback : employee_rating si manager_rating absent.
        Exclut les objectifs CANCELLED.
        """
        # On prend d'abord les goals_manager (evaluation manager), puis fallback goals (employe)
        manager_goals = review.goals_manager or []
        employee_goals = review.goals or []

        # Si le manager a evalue, utiliser goals_manager
        if manager_goals:
            goals_source = manager_goals
            rating_key = 'manager_rating'
        else:
            goals_source = employee_goals
            rating_key = 'employee_rating'

        # Filtrer les objectifs non CANCELLED et avec rating
        active_goals = [
            g for g in goals_source
            if g.get('status') != 'CANCELLED' and g.get(rating_key) is not None
        ]

        if not active_goals:
            return None

        total_weighted = 0.0
        total_weights = 0.0

        for goal in active_goals:
            rating = goal.get(rating_key) or goal.get('employee_rating')  # fallback
            if rating is None:
                continue

            weight = goal.get('weight') or (1.0 / len(active_goals))
            total_weighted += float(rating) * weight
            total_weights += weight

        if total_weights == 0:
            return None

        return round(total_weighted / total_weights, 2)

    @classmethod
    def _calculate_skills_score(cls, review: PerformanceReview) -> Optional[float]:
        """
        Calcule le score des competences.

        score_competences = (manager_level_i x weight_i) / (weight_i)

        Fallback : employee_level si manager_level absent.
        Si aucun weight -> moyenne simple (1/N).
        """
        manager_skills = review.skills_manager or []
        employee_skills = review.skills or []

        if manager_skills:
            skills_source = manager_skills
            level_key = 'manager_level'
        else:
            skills_source = employee_skills
            level_key = 'employee_level'

        total_weighted = 0.0
        total_weights = 0.0
        count = 0

        for skill in skills_source:
            level = skill.get(level_key) or skill.get('employee_level')
            if level is None:
                continue
            weight = skill.get('weight')
            if weight is not None:
                total_weighted += float(level) * weight
                total_weights += weight
            else:
                total_weighted += float(level)
            count += 1

        if count == 0:
            return None

        if total_weights > 0:
            return round(total_weighted / total_weights, 2)
        else:
            return round(total_weighted / count, 2)
