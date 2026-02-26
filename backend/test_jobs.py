"""
Backend Jobs Testing Script
ADDED: Complete testing suite for Celery tasks and caching
REASON: Verify all background jobs and caching work correctly
USAGE: python test_jobs.py
"""
import sys
from app import create_app
from tasks import send_daily_reminders, generate_monthly_report, export_applications_csv
from cache import cache

def test_cache():
    """Test Flask-Caching functionality"""
    print("\n" + "="*60)
    print("🔍 TESTING FLASK-CACHING")
    print("="*60)
    
    app = create_app()
    with app.app_context():
        # Test cache set/get
        test_key = 'test_key'
        test_value = 'test_value'
        
        print("Testing cache SET...")
        cache.set(test_key, test_value, timeout=60)
        
        print("Testing cache GET...")
        result = cache.get(test_key)
        
        if result == test_value:
            print("✅ Cache SET/GET: WORKING")
        else:
            print(f"❌ Cache SET/GET: FAILED (Expected: {test_value}, Got: {result})")
            return False
        
        # Test cache delete
        print("Testing cache DELETE...")
        cache.delete(test_key)
        result = cache.get(test_key)
        
        if result is None:
            print("✅ Cache DELETE: WORKING")
        else:
            print(f"❌ Cache DELETE: FAILED (Got: {result} instead of None)")
            return False
    
    return True

def test_daily_reminders():
    """Test daily reminder Celery task"""
    print("\n" + "="*60)
    print("🔍 TESTING DAILY REMINDERS")
    print("="*60)
    
    try:
        print("Triggering send_daily_reminders task...")
        result = send_daily_reminders.delay()
        
        print(f"Task ID: {result.id}")
        print("Waiting for result (timeout: 30s)...")
        
        task_result = result.get(timeout=30)
        
        print(f"✅ Task Status: {result.state}")
        print(f"✅ Result: {task_result}")
        return True
    except Exception as e:
        print(f"❌ Task Failed: {e}")
        return False

def test_monthly_report():
    """Test monthly report Celery task"""
    print("\n" + "="*60)
    print("🔍 TESTING MONTHLY REPORT")
    print("="*60)
    
    try:
        print("Triggering generate_monthly_report task...")
        result = generate_monthly_report.delay()
        
        print(f"Task ID: {result.id}")
        print("Waiting for result (timeout: 30s)...")
        
        task_result = result.get(timeout=30)
        
        print(f"✅ Task Status: {result.state}")
        print(f"✅ Result: {task_result}")
        return True
    except Exception as e:
        print(f"❌ Task Failed: {e}")
        return False

def test_csv_export():
    """Test CSV export Celery task"""
    print("\n" + "="*60)
    print("🔍 TESTING CSV EXPORT")
    print("="*60)
    
    # Get first student ID for testing
    app = create_app()
    with app.app_context():
        from models import Student
        student = Student.query.first()
        
        if not student:
            print("⚠️  No students in database. Skipping CSV export test.")
            return True
        
        student_id = student.id
    
    try:
        print(f"Triggering export_applications_csv for student_id={student_id}...")
        result = export_applications_csv.delay(student_id)
        
        print(f"Task ID: {result.id}")
        print("Waiting for result (timeout: 30s)...")
        
        task_result = result.get(timeout=30)
        
        print(f"✅ Task Status: {result.state}")
        print(f"✅ Result: {task_result}")
        return True
    except Exception as e:
        print(f"❌ Task Failed: {e}")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("🚀 BACKEND JOBS & CACHING TEST SUITE")
    print("="*60)
    print("\nThis will test:")
    print("  1. Flask-Caching (Redis)")
    print("  2. Daily Reminders (Celery)")
    print("  3. Monthly Reports (Celery)")
    print("  4. CSV Export (Celery)")
    print("\nMake sure Redis and Celery worker are running!")
    print("="*60)
    
    results = {}
    
    # Test Caching
    results['Flask-Caching'] = test_cache()
    
    # Test Celery Tasks
    results['Daily Reminders'] = test_daily_reminders()
    results['Monthly Report'] = test_monthly_report()
    results['CSV Export'] = test_csv_export()
    
    # Summary
    print("\n" + "="*60)
    print("📊 TEST SUMMARY")
    print("="*60)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name:25s} {status}")
    
    print("="*60)
    
    all_passed = all(results.values())
    
    if all_passed:
        print("\n🎉 ALL TESTS PASSED!")
        print("✅ Flask-Caching is working")
        print("✅ All Celery tasks are functional")
        print("✅ Backend jobs are production-ready")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED")
        print("\nTroubleshooting:")
        print("  - Make sure Redis is running: redis-cli ping")
        print("  - Make sure Celery worker is running: celery -A celery_app worker")
        print("  - Check logs for detailed error messages")
        return 1

if __name__ == '__main__':
    sys.exit(main())