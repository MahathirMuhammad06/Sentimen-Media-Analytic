import threading
import time
from datetime import datetime
from ..database.repository import get_session, run_due_schedules
from ..utils.logger import get_logger

logger = get_logger(__name__)

_scheduler_thread = None
_stop_event = threading.Event()


def _loop(poll_interval_seconds: int = 3600):
    logger.info("Cleanup scheduler started, checking schedules every %s seconds", poll_interval_seconds)
    while not _stop_event.is_set():
        try:
            session = get_session()
            try:
                executed = run_due_schedules(session)
                if executed:
                    logger.info("Executed scheduled cleanups: %s", executed)
            finally:
                session.close()
        except Exception as e:
            logger.exception("Error while running scheduled cleanup: %s", e)
        # Sleep until next poll
        _stop_event.wait(poll_interval_seconds)


def start_scheduler(poll_interval_seconds: int = 3600):
    global _scheduler_thread
    if _scheduler_thread and _scheduler_thread.is_alive():
        logger.info("Scheduler already running")
        return
    _stop_event.clear()
    _scheduler_thread = threading.Thread(target=_loop, args=(poll_interval_seconds,), daemon=True)
    _scheduler_thread.start()


def stop_scheduler():
    _stop_event.set()
    logger.info("Scheduler stop requested")
