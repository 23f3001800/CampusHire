"""
Flask-Caching configuration for the placement portal.
Provides server-side caching for API responses.
"""
from flask_caching import Cache

cache = Cache()

# ─── TTL Constants ────────────────────────────────────────────────────────────

TTL_SHORT  = 60        #  1 minute  — frequently changing data
TTL_MEDIUM = 5 * 60    #  5 minutes — moderately changing data
TTL_LONG   = 15 * 60   # 15 minutes — rarely changing data


# ─── Cache Key Constants ──────────────────────────────────────────────────────
# Defined once here so api.py imports and uses them — no magic strings

def key_student_profile(sid):        return f'student_profile_{sid}'
def key_student_applications(sid):   return f'student_applications_{sid}'
def key_student_eligible_drives(sid):return f'student_eligible_drives_{sid}'
def key_student_placements(sid):     return f'student_placements_{sid}'
def key_student_interview(app_id):   return f'student_interview_{app_id}'  # NEW

def key_company_profile(cid):        return f'company_profile_{cid}'
def key_company_drives(cid):         return f'company_drives_{cid}'

def key_drive(did):                  return f'drive_{did}'
def key_drive_applicants(did):       return f'drive_applicants_{did}'

KEY_ALL_DRIVES    = 'all_drives'
KEY_ADMIN_DRIVES  = 'admin_drives'
KEY_ADMIN_STUDENTS = 'admin_students'
KEY_ADMIN_COMPANIES = 'admin_companies'
KEY_ADMIN_STATS   = 'admin_stats'    # NEW — expensive aggregation query


# ─── Cache Invalidation Helpers ───────────────────────────────────────────────


def clear_student_cache(student_id):
    """Clear all cache entries related to a specific student."""
    cache.delete(key_student_profile(student_id))
    cache.delete(key_student_applications(student_id))
    cache.delete(key_student_eligible_drives(student_id))
    cache.delete(key_student_placements(student_id))
    cache.delete(KEY_ADMIN_STUDENTS)
    cache.delete(KEY_ADMIN_STATS)


def clear_company_cache(company_id):
    """Clear all cache entries related to a specific company."""
    cache.delete(key_company_profile(company_id))
    cache.delete(key_company_drives(company_id))
    cache.delete(KEY_ADMIN_COMPANIES)
    cache.delete(KEY_ADMIN_STATS)


def clear_drive_cache(drive_id=None, company_id=None):
    """Clear all cache entries related to drives."""
    if drive_id:
        cache.delete(key_drive(drive_id))
        cache.delete(key_drive_applicants(drive_id))
    if company_id:
        cache.delete(key_company_drives(company_id))
    cache.delete(KEY_ALL_DRIVES)
    cache.delete(KEY_ADMIN_DRIVES)
    cache.delete(KEY_ADMIN_STATS)


def clear_application_cache(student_id=None, drive_id=None):
    """Clear all cache entries related to applications."""
    if student_id:
        cache.delete(key_student_applications(student_id))
        cache.delete(key_student_eligible_drives(student_id))
        cache.delete(key_student_placements(student_id))
    if drive_id:
        cache.delete(key_drive_applicants(drive_id))
    cache.delete(KEY_ADMIN_STATS)


def clear_interview_cache(application_id):
    """Clear interview cache for a specific application."""  # NEW
    cache.delete(key_student_interview(application_id))


def clear_all_cache():
    """Clear entire cache (use with caution)."""
    cache.clear()
