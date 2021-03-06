import time
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor


from app import api
from app.config import website, database, task_cycle
from app.database.insert import Session
from app.logger import logs


executor = ThreadPoolExecutor(max_workers=25)
scheduler = BackgroundScheduler(executors={'default': executor})
hour = task_cycle["hour"]
second = task_cycle["second"]


def schedule(website_name):
    session = Session(**database)
    web = website[website_name]
    for k, v in web.items():
        for section in v:
            logs.info(f"{datetime.now().strftime('%Y-%m-%d %H:%M')}  执行任务<{website_name} {section['section']}>")
            for i in range(1, 3):
                section["page"] = i
                try:
                    news = getattr(api, website_name)(**section)
                except Exception as e:
                    logs.error(e)
                    break
                for n in news:
                    n = api.revise(n)
                    if n:
                        session.insert_one(n)

    session.close()


def schedule_special():
    session = Session(**database)
    news = api.special_eastmoney()
    for n in news:
        session.insert_one(n)
    session.close()


def schedule_special_search_api():
    session = Session(**database)
    news = api.special_eastmoney_search_api()
    for n in news:
        session.insert_one(n)
    session.close()


def schedule_special_hibor():
    session = Session(**database)
    news = api.special_hibor()
    for n in news:
        session.insert_one(n)
    logs.info("慧博资讯导入数据库完成")
    print("慧博资讯导入数据库完成")
    session.close()


def start_schedule():
    logs.info(f"开始执行爬虫任务，当前任务执行周期为@{hour}hours")
    print(f"开始执行爬虫任务，当前任务执行周期为@{hour}hours")
    for name in website.keys():
        schedule(name)
        scheduler.add_job(schedule, 'interval', hours=hour, seconds=second, args=(name,))

    scheduler.add_job(schedule_special, 'interval', hours=hour, seconds=second, )

    scheduler.add_job(schedule_special_search_api, 'interval', hours=hour, seconds=second, )

    scheduler.add_job(schedule_special_hibor, 'interval', hours=6, seconds=second, )
    try:
        schedule_special_hibor()
    except Exception as e:
        print(e)

    schedule_special()

    scheduler.start()

    while True:
        time.sleep(1*60*60)
