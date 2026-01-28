"""
Recruitment caching services.

Handles caching of recruitment process queries.
"""

from django.core.cache import cache
from hr.services.cache_helpers import generate_cache_key, CacheKeys
from hr.recruitment.models import (
    JobOffer,
    Candidate,
    Application,
    Interview,
)


class RecruitmentCacheService:
    """Cache operations for recruitment module."""
    
    @staticmethod
    def get_job_offer(offer_id):
        """Get job offer by ID (longer cache - stable postings)."""
        cache_key = generate_cache_key("hr:recruitment:offer", offer_id)
        offer = cache.get(cache_key)
        
        if offer is None:
            offer = JobOffer.objects.filter(
                id=offer_id
            ).first()
            
            if offer:
                cache.set(cache_key, offer, timeout=60*60*24)  # 24h
        
        return offer
    
    @staticmethod
    def get_active_job_offers(department=None):
        """
        Get all active job offers (short cache - can change).
        
        Args:
            department: Optional Department instance to filter
        
        Returns:
            List of active JobOffer instances
        """
        department_id = None
        if department:
            department_id = department.id if hasattr(department, 'id') else department
        
        cache_key = CacheKeys.active_job_offers(department_id)
        offers = cache.get(cache_key)
        
        if offers is None:
            query = JobOffer.objects.filter(status='open')
            
            if department_id:
                query = query.filter(position__department_id=department_id)
            
            offers = list(query.order_by('-created_at'))
            cache.set(cache_key, offers, timeout=60*60*24)  # 24h
        
        return offers
    
    @staticmethod
    def get_candidate(candidate_id):
        """Get candidate by ID (short cache - volatile)."""
        cache_key = generate_cache_key("hr:recruitment:candidate", candidate_id)
        candidate = cache.get(cache_key)
        
        if candidate is None:
            candidate = Candidate.objects.filter(
                id=candidate_id
            ).first()
            
            if candidate:
                cache.set(cache_key, candidate, timeout=60*30)  # 30m
        
        return candidate
    
    @staticmethod
    def get_candidate_by_email(email):
        """Get candidate by email (short cache)."""
        cache_key = generate_cache_key("hr:recruitment:candidate_email", email)
        candidate = cache.get(cache_key)
        
        if candidate is None:
            candidate = Candidate.objects.filter(
                email=email
            ).first()
            
            if candidate:
                cache.set(cache_key, candidate, timeout=60*30)  # 30m
        
        return candidate
    
    @staticmethod
    def get_application(application_id):
        """Get application by ID (short cache)."""
        cache_key = generate_cache_key("hr:recruitment:application", application_id)
        application = cache.get(cache_key)
        
        if application is None:
            application = Application.objects.filter(
                id=application_id
            ).first()
            
            if application:
                cache.set(cache_key, application, timeout=60*30)  # 30m
        
        return application
    
    @staticmethod
    def get_applications_for_offer(job_offer, status=None):
        """
        Get applications for a job offer (short cache).
        
        Args:
            job_offer: JobOffer instance or ID
            status: Optional status filter
        
        Returns:
            List of Application instances
        """
        if isinstance(job_offer, JobOffer):
            offer_id = job_offer.id
        else:
            offer_id = job_offer
        
        cache_key = generate_cache_key(
            "hr:recruitment:applications_offer", offer_id, status
        )
        applications = cache.get(cache_key)
        
        if applications is None:
            query = Application.objects.filter(job_offer_id=offer_id)
            
            if status:
                query = query.filter(status=status)
            
            applications = list(query.order_by('-created_at'))
            cache.set(cache_key, applications, timeout=60*30)  # 30m
        
        return applications
    
    @staticmethod
    def get_qualified_candidates(job_offer):
        """
        Get qualified candidates for a job offer (short cache).
        
        Args:
            job_offer: JobOffer instance or ID
        
        Returns:
            List of qualified Candidate instances
        """
        if isinstance(job_offer, JobOffer):
            offer_id = job_offer.id
        else:
            offer_id = job_offer
        
        cache_key = CacheKeys.qualified_candidates(offer_id)
        candidates = cache.get(cache_key)
        
        if candidates is None:
            applications = Application.objects.filter(
                job_offer_id=offer_id,
                status='qualified'
            ).select_related('candidate')
            
            candidates = [a.candidate for a in applications]
            cache.set(cache_key, candidates, timeout=60*30)  # 30m
        
        return candidates
    
    @staticmethod
    def get_interview(interview_id):
        """Get interview by ID (very short cache)."""
        cache_key = generate_cache_key("hr:recruitment:interview", interview_id)
        interview = cache.get(cache_key)
        
        if interview is None:
            interview = Interview.objects.filter(
                id=interview_id
            ).first()
            
            if interview:
                cache.set(cache_key, interview, timeout=60*15)  # 15m
        
        return interview
    
    @staticmethod
    def get_interviews_for_candidate(candidate, status=None):
        """Get interviews for a candidate (very short cache)."""
        cache_key = generate_cache_key(
            "hr:recruitment:candidate_interviews", candidate.id, status
        )
        interviews = cache.get(cache_key)
        
        if interviews is None:
            query = Interview.objects.filter(application__candidate=candidate)
            
            if status:
                query = query.filter(status=status)
            
            interviews = list(query.order_by('scheduled_date'))
            cache.set(cache_key, interviews, timeout=60*15)  # 15m
        
        return interviews
    
    @staticmethod
    def get_pending_interviews():
        """Get all pending interviews (very short cache)."""
        cache_key = "hr:recruitment:pending_interviews"
        interviews = cache.get(cache_key)
        
        if interviews is None:
            from django.utils import timezone
            
            interviews = list(Interview.objects.filter(
                status='pending',
                scheduled_date__gte=timezone.now()
            ).order_by('scheduled_date'))
            
            cache.set(cache_key, interviews, timeout=60*5)  # 5m
        
        return interviews
    
    @staticmethod
    def clear_candidate_cache(candidate):
        """Clear cache for a candidate."""
        if isinstance(candidate, Candidate):
            candidate_id = candidate.id
            email = candidate.email
        else:
            candidate_id = candidate
            email = None
        
        cache.delete(generate_cache_key("hr:recruitment:candidate", candidate_id))
        
        if email:
            cache.delete(generate_cache_key("hr:recruitment:candidate_email", email))
        
        cache.delete(generate_cache_key(
            "hr:recruitment:candidate_interviews", candidate_id, None
        ))
    
    @staticmethod
    def clear_offer_cache(job_offer):
        """Clear cache for a job offer."""
        if isinstance(job_offer, JobOffer):
            offer_id = job_offer.id
        else:
            offer_id = job_offer
        
        cache.delete(generate_cache_key("hr:recruitment:offer", offer_id))
        cache.delete(generate_cache_key(
            "hr:recruitment:applications_offer", offer_id, None
        ))
        cache.delete(CacheKeys.qualified_candidates(offer_id))
