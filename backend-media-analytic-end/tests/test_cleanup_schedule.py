from src.database.repository import get_session, create_cleanup_schedule, get_cleanup_schedules, run_cleanup_for_schedule

s = get_session()
try:
    sched = create_cleanup_schedule(s, name='test-daily-cleanup', days_threshold=1, interval_minutes=1)
    print('Created schedule id=', sched.id)
    print('Running schedule now...')
    res = run_cleanup_for_schedule(s, sched.id)
    print('Run result:', res)
    all_s = get_cleanup_schedules(s)
    print('Total schedules:', len(all_s))
finally:
    s.close()
