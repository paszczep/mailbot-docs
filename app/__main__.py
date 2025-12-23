from schedule import every, run_pending
from time import sleep
from datetime import datetime, time as dt_time
from logging import getLogger, INFO, info
from app.src.run import run


logger = getLogger()
logger.setLevel(INFO)

START = dt_time(6, 0)
END = dt_time(18, 0) 

def limited_job():
    """Działanie, kiedy mają szansę powstawać nowe dokumenty."""
    now = datetime.now()
    if now.weekday() < 5 and START <= now.time() <= END:
        info(f'Running: {now}')
        run()


def job():
    every(3).hours.do(limited_job)
    while True:
        run_pending()
        sleep(1)


if __name__ == "__main__":
    job()
    # run()
