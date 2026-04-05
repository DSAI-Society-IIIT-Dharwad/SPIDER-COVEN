from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import subprocess, os

TRACKED_ASINS = os.getenv("TRACKED_ASINS", "B07SKKG51W,B07PQKK9FB").split(",")
PIN_CODES     = os.getenv("PIN_CODES", "600001,110001").split(",")

def crawl_job():
    for asin in TRACKED_ASINS:
        for pin in PIN_CODES:
            cmd = (
                f"cd scraper && "
                f"scrapy crawl offers_spider -a asin={asin} -a pin_code={pin} "
                f"-s LOG_LEVEL=WARNING"
            )
            subprocess.Popen(cmd, shell=True)

scheduler = BackgroundScheduler()
scheduler.add_job(crawl_job, IntervalTrigger(minutes=90))
scheduler.start()

if __name__ == "__main__":
    import time
    print("Scheduler running — crawling every 90 min. Ctrl+C to stop.")
    crawl_job()   # run immediately on start
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        scheduler.shutdown()
