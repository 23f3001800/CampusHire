"""
trigger_tasks.py — Manually fire Celery tasks
==============================================

Modes:
  python trigger_tasks.py                    # SYNC — no broker needed, runs inline
  python trigger_tasks.py --async            # ASYNC — queues via worker
  python trigger_tasks.py --ping             # broker connectivity check only
  python trigger_tasks.py --async --export 42  # also queue CSV export for student 42
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def _make_app():
    import inspect
    from app import create_app
    # Works with any signature: create_app() or create_app(config_name)
    has_required = any(
        p.default is inspect.Parameter.empty
        for p in inspect.signature(create_app).parameters.values()
    )
    return create_app(os.environ.get("FLASK_ENV", "development")) if has_required else create_app()


def check_broker(verbose: bool = True) -> bool:
    flask_app = _make_app()
    celery    = flask_app.extensions["celery"]
    try:
        conn = celery.connection_for_read()
        conn.ensure_connection(max_retries=1, interval_start=0, interval_step=0)
        conn.close()
        if verbose:
            print(f"✅  Broker OK: {flask_app.config['CELERY']['broker_url']}")
        return True
    except Exception as exc:
        print(f"\n❌  Broker unreachable: {exc}")
        print("    Fix: sudo systemctl start redis && redis-cli ping\n")
        return False


def run_sync():
    print("🔧  SYNC mode — no broker needed\n")
    flask_app = _make_app()
    with flask_app.app_context():
        from tasks import send_deadline_reminders, send_monthly_activity_report

        print("▶  send_deadline_reminders ...")
        print("   ✓", send_deadline_reminders(), "\n")

        print("▶  send_monthly_activity_report ...")
        print("   ✓", send_monthly_activity_report(), "\n")

    print("✅  Done.")


def run_async(student_id=None):
    print("🚀  ASYNC mode\n")
    if not check_broker():
        sys.exit(1)

    from tasks import (
        export_applications_csv,
        health_check,
        send_deadline_reminders,
        send_monthly_activity_report,
    )

    j0 = health_check.delay()
    print(f"📡  health_check                 → {j0.id}")

    j1 = send_deadline_reminders.delay()
    print(f"📧  send_deadline_reminders      → {j1.id}")

    j2 = send_monthly_activity_report.delay()
    print(f"📊  send_monthly_activity_report → {j2.id}")

    if student_id is not None:
        j3 = export_applications_csv.delay(student_id)
        print(f"📄  export_applications_csv      → {j3.id}  (student {student_id})")

    print("\n  Monitor: celery -A celery_config.celery_app flower")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--async",   dest="async_mode", action="store_true")
    parser.add_argument("--ping",    action="store_true")
    parser.add_argument("--export",  type=int, metavar="STUDENT_ID")
    args = parser.parse_args()

    if args.ping:
        sys.exit(0 if check_broker() else 1)
    elif args.async_mode:
        run_async(student_id=args.export)
    else:
        run_sync()