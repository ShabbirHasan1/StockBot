from apscheduler.schedulers.blocking import BlockingScheduler

sched = BlockingScheduler()

@sched.scheduled_job('cron', day_of_week='mon-fri', hour=4)
def scheduled_job():
    print('This job is run every weekday at 5pm.')
	python MovingAverage.py
sched.start()