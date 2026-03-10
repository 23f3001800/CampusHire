"""
trigger_tasks.py — Manually trigger Celery tasks for testing
=============================================================

Two modes:
  --async   Uses .delay() — requires Redis to be running
  --direct  Calls task functions directly — NO Redis needed (default)

Usage:
    python trigger_tasks.py           # direct mode, no Redis needed
    python trigger_tasks.py --async   # async mode, Redis must be running
"""

import sys

from app import create_app
from tasks import (
    send_deadline_reminders,
    send_monthly_activity_report,
    export_applications_csv,
)

app = create_app()

USE_ASYNC = '--async' in sys.argv

with app.app_context():

    if USE_ASYNC:
        # ── Async mode: tasks go to Celery worker via Redis ───────────────────
        # Requires: redis-server running + celery worker running
        print("🚀 Queueing tasks via Celery worker (Redis required)...")

        j1 = send_deadline_reminders.delay()
        print(f"  ✅ send_deadline_reminders     queued → task_id: {j1.id}")

        j2 = send_monthly_activity_report.delay()
        print(f"  ✅ send_monthly_activity_report queued → task_id: {j2.id}")

        j3 = export_applications_csv.delay(student_id=1)
        print(f"  ✅ export_applications_csv      queued → task_id: {j3.id}")

        print("\n📋 Watch your Celery worker terminal for results.")
        print("📧 Check http://localhost:8025 (Mailpit) for emails.")

    else:
        # ── Direct mode: tasks run right here, no Redis/worker needed ─────────
        print("⚡ Running tasks directly (no Redis needed)...\n")

        print("▶ send_deadline_reminders...")
        r1 = send_deadline_reminders()
        print(f"  Result: {r1}\n")

        print("▶ send_monthly_activity_report...")
        r2 = send_monthly_activity_report()
        print(f"  Result: {r2}\n")

        print("▶ export_applications_csv(student_id=1)...")
        r3 = export_applications_csv(student_id=1)   # change student_id as needed
        print(f"  Result: {r3}\n")

        print("✅ All tasks completed.")
        print("📧 Check http://localhost:8025 (Mailpit) for emails.")