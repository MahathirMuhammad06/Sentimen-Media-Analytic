from apscheduler.schedulers.blocking import BlockingScheduler
from crawler.news_crawler import NewsCrawler
from config import config
from database.repository import init_db
from utils.logger import get_logger

logger = get_logger(__name__)

def start_scheduler():
    init_db()
    crawler = NewsCrawler()
    sched = BlockingScheduler()
    # run immediately and then every CRAWL_INTERVAL seconds
    sched.add_job(crawler.crawl_all, "interval", seconds=config.CRAWL_INTERVAL, next_run_time=None)
    logger.info("Scheduler started with interval %s seconds", config.CRAWL_INTERVAL)
    try:
        crawler.crawl_all() # initial run (optional)
        sched.start()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler stopped")

if __name__ == "__main__":
    start_scheduler()