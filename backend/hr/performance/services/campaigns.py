import logging
from uuid import UUID
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError

from hr.performance.models import Campaign, CampaignParticipation, CampaignEvaluator, PerformanceReview
from hr.performance.enums import CampaignStatus, ReviewStatus


logger = logging.getLogger(__name__)


class CampaignService:

    @classmethod
    @transaction.atomic
    def create_campaign(cls, data: dict, actor=None) -> Campaign:
        """Crée une campagne en statut DRAFT avec ses participants et évaluateurs."""
        participant_ids = data.pop('participant_ids', [])
        evaluator_ids = data.pop('evaluator_ids', [])
        campaign = Campaign.objects.create(
            name=data['name'],
            description=data.get('description', ''),
            campaign_type=data['campaign_type'],
            start_date=data['start_date'],
            end_date=data['end_date'],
            submission_deadline=data['submission_deadline'],
            goal_weight=data.get('goal_weight', 0.6),
            skill_weight=data.get('skill_weight', 0.4),
            default_goals=data.get('default_goals', []),
            default_skills=data.get('default_skills', []),
            created_by=actor,
        )
        if participant_ids:
            CampaignParticipation.objects.bulk_create([
                CampaignParticipation(campaign=campaign, employee_id=uid)
                for uid in participant_ids
            ], ignore_conflicts=True)
        if evaluator_ids:
            CampaignEvaluator.objects.bulk_create([
                CampaignEvaluator(campaign=campaign, employee_id=uid)
                for uid in evaluator_ids
            ], ignore_conflicts=True)
        logger.info(
            "Campaign created",
            extra={"campaign_id": campaign.id, "campaign_name": campaign.name, "actor": str(actor)},
        )
        return campaign

    @classmethod
    @transaction.atomic
    def update_campaign(cls, campaign_id: UUID, data: dict, actor=None) -> Campaign:
        """Met à jour une campagne (DRAFT uniquement) et synchronise ses participants et évaluateurs."""
        campaign = Campaign.objects.get(id=campaign_id)

        if campaign.status != CampaignStatus.DRAFT:
            raise ValidationError("Seules les campagnes en statut DRAFT peuvent être modifiées.")

        participant_ids = data.pop('participant_ids', None)
        evaluator_ids = data.pop('evaluator_ids', None)

        for field in ['name', 'description', 'campaign_type', 'start_date', 'end_date',
                       'submission_deadline', 'goal_weight', 'skill_weight',
                       'default_goals', 'default_skills']:
            if field in data:
                setattr(campaign, field, data[field])

        campaign.updated_by = actor
        campaign.save()

        if participant_ids is not None:
            current_ids = set(
                CampaignParticipation.objects.filter(campaign=campaign)
                .values_list('employee_id', flat=True)
            )
            new_ids = set(participant_ids)

            to_add = new_ids - current_ids
            to_remove = current_ids - new_ids

            if to_remove:
                CampaignParticipation.objects.filter(
                    campaign=campaign, employee_id__in=list(to_remove)
                ).delete()
            if to_add:
                CampaignParticipation.objects.bulk_create([
                    CampaignParticipation(campaign=campaign, employee_id=uid)
                    for uid in to_add
                ], ignore_conflicts=True)

            # Rafraîchir l'objet pour que le ManyToMany cache soit à jour
            campaign.refresh_from_db()

        if evaluator_ids is not None:
            current_evaluator_ids = set(
                CampaignEvaluator.objects.filter(campaign=campaign)
                .values_list('employee_id', flat=True)
            )
            new_evaluator_ids = set(evaluator_ids)

            to_add_eval = new_evaluator_ids - current_evaluator_ids
            to_remove_eval = current_evaluator_ids - new_evaluator_ids

            if to_remove_eval:
                CampaignEvaluator.objects.filter(
                    campaign=campaign, employee_id__in=list(to_remove_eval)
                ).delete()
            if to_add_eval:
                CampaignEvaluator.objects.bulk_create([
                    CampaignEvaluator(campaign=campaign, employee_id=uid)
                    for uid in to_add_eval
                ], ignore_conflicts=True)

            campaign.refresh_from_db()

        return campaign

    @classmethod
    @transaction.atomic
    def activate_campaign(cls, campaign_id: UUID, actor=None) -> Campaign:
        """Active une campagne : DRAFT → ACTIVE avec création auto des évaluations."""
        campaign = Campaign.objects.get(id=campaign_id)

        if campaign.status != CampaignStatus.DRAFT:
            raise ValidationError(
                f"Impossible d'activer une campagne avec le statut '{campaign.status}'."
            )

        campaign.status = CampaignStatus.ACTIVE
        campaign.updated_by = actor
        campaign.save()

        # Création automatique des évaluations pour chaque participant
        participations = CampaignParticipation.objects.filter(campaign=campaign)
        created_count = 0
        for participation in participations:
            _, was_created = PerformanceReview.objects.get_or_create(
                campaign=campaign,
                employee=participation.employee,
                defaults={
                    'manager': participation.employee.manager if hasattr(participation.employee, 'manager') else None,
                    'status': ReviewStatus.EMPLOYEE_DRAFT,
                    'goals': [dict(g) for g in campaign.default_goals],  # snapshot
                    'skills': [dict(s) for s in campaign.default_skills],  # snapshot
                },
            )
            if was_created:
                created_count += 1

        logger.info(
            "Campaign activated",
            extra={
                "campaign_id": campaign.id,
                "participants": participations.count(),
                "reviews_created": created_count,
                "actor": str(actor),
            },
        )
        return campaign

    @classmethod
    @transaction.atomic
    def close_campaign(cls, campaign_id: UUID, actor=None) -> Campaign:
        """Clôture une campagne : ACTIVE → CLOSED."""
        campaign = Campaign.objects.get(id=campaign_id)

        if campaign.status != CampaignStatus.ACTIVE:
            raise ValidationError(
                f"Impossible de clôturer une campagne avec le statut '{campaign.status}'."
            )

        campaign.status = CampaignStatus.CLOSED
        campaign.updated_by = actor
        campaign.save()

        logger.info(
            "Campaign closed",
            extra={"campaign_id": campaign.id, "actor": str(actor)},
        )
        return campaign

    @classmethod
    def delete_campaign(cls, campaign_id: UUID, actor=None) -> None:
        """Supprime une campagne (DRAFT uniquement, sans évaluations)."""
        campaign = Campaign.objects.get(id=campaign_id)

        if campaign.status != CampaignStatus.DRAFT:
            raise ValidationError("Seules les campagnes en statut DRAFT peuvent être supprimées.")

        if campaign.reviews.exists():
            raise ValidationError(
                "Impossible de supprimer une campagne qui contient des évaluations."
            )

        campaign.delete()

        logger.info(
            "Campaign deleted",
            extra={"campaign_id": campaign.id, "actor": str(actor)},
        )

    @classmethod
    @transaction.atomic
    def add_participant(cls, campaign_id: UUID, employee_id: UUID, actor=None) -> CampaignParticipation:
        """Ajoute un participant à une campagne."""
        campaign = Campaign.objects.get(id=campaign_id)

        if campaign.status == CampaignStatus.CLOSED:
            raise ValidationError("Impossible d'ajouter un participant à une campagne clôturée.")

        participation, created = CampaignParticipation.objects.get_or_create(
            campaign=campaign,
            employee_id=employee_id,
        )

        if created and campaign.status == CampaignStatus.ACTIVE:
            # Si la campagne est active, créer directement l'évaluation
            PerformanceReview.objects.get_or_create(
                campaign=campaign,
                employee_id=employee_id,
                defaults={
                    'status': ReviewStatus.EMPLOYEE_DRAFT,
                    'goals': [dict(g) for g in campaign.default_goals],  # snapshot
                    'skills': [dict(s) for s in campaign.default_skills],  # snapshot
                },
            )

        logger.info(
            "Participant added to campaign",
            extra={
                "campaign_id": campaign.id,
                "employee_id": employee_id,
                "actor": str(actor),
            },
        )
        return participation

    @classmethod
    @transaction.atomic
    def remove_participant(cls, campaign_id: UUID, employee_id: UUID, actor=None) -> None:
        """Retire un participant d'une campagne."""
        campaign = Campaign.objects.get(id=campaign_id)

        if campaign.status != CampaignStatus.DRAFT:
            raise ValidationError(
                "Impossible de retirer un participant d'une campagne qui n'est plus en DRAFT."
            )

        CampaignParticipation.objects.filter(
            campaign=campaign,
            employee_id=employee_id,
        ).delete()

        logger.info(
            "Participant removed from campaign",
            extra={"campaign_id": campaign.id, "employee_id": employee_id, "actor": str(actor)},
        )
