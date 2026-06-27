"""
Performance module permission scopes.

Source of truth for all performance-related permissions.
Used by controllers and aggregated for frontend permission system.
"""

READ_REVIEW = 'performance:r'
WRITE_REVIEW = 'performance:w'
UPDATE_REVIEW = 'performance:u'
DELETE_REVIEW = 'performance:d'


# Registry for frontend permission system
# Aggregated at root level to expose all available permissions to the UI
PERFORMANCE_PERMISSIONS = [
    READ_REVIEW,
    WRITE_REVIEW,
    UPDATE_REVIEW,
    DELETE_REVIEW,
]

__all__ = [
    'READ_REVIEW',
    'WRITE_REVIEW',
    'UPDATE_REVIEW',
    'DELETE_REVIEW',
    'PERFORMANCE_PERMISSIONS',
]

