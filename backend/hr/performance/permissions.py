"""
Performance module permission scopes.

Source of truth for all performance-related permissions.
Used by controllers and aggregated for frontend permission system.
Pattern: performance:r (read), performance:w (write), performance:u (update),
         performance:d (delete), performance:a (admin/approve)
"""

READ_REVIEW = 'performance:r'
WRITE_REVIEW = 'performance:w'
UPDATE_REVIEW = 'performance:u'
DELETE_REVIEW = 'performance:d'
APPROVE_REVIEW = 'performance:a'


# Registry for frontend permission system
# Aggregated at root level to expose all available permissions to the UI
PERFORMANCE_PERMISSIONS = [
    READ_REVIEW,
    WRITE_REVIEW,
    UPDATE_REVIEW,
    DELETE_REVIEW,
    APPROVE_REVIEW,
]


__all__ = [
    'READ_REVIEW',
    'WRITE_REVIEW',
    'UPDATE_REVIEW',
    'DELETE_REVIEW',
    'APPROVE_REVIEW',
    'PERFORMANCE_PERMISSIONS',
]


