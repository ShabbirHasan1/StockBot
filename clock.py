from apscheduler.schedulers.blocking import BlockingScheduler
import MovingAverage
import os
import logging
import sell
import buy
import storeRatios
import Median
import ScoreBuyStocks
import storeFinancials
import generate_token
import holdings
logging.basicConfig()

sched = BlockingScheduler()


#@sched.scheduled_job('interval', minutes=10)


#@sched.scheduled_job('cron', day_of_week='mon-fri', hour=4, minute=55)
#def scheduled_job():
#	sell.main()
#	print 'This job is run every weekday at 10:25 am.'

@sched.scheduled_job('interval', minutes=60)
def timed_job():
	holdings.main()
	print('This job is run every sixty minutes.')

@sched.scheduled_job('interval', minutes=10)
def timed_job():
	sell.main()
	print('This job is run every ten minutes.')


@sched.scheduled_job('cron', day_of_week='mon-sun', hour=14, minute=05)
def scheduled_job1():
	generate_token.main()
	print 'This job is run every weekday at 22:05.'


@sched.scheduled_job('cron', day_of_week='mon-sun', hour=14, minute=30)
def scheduled_job1():
	storeFinancials.main()
	print 'This job is run every weekday at 22:30.'

#@sched.scheduled_job('cron', day_of_week='mon-fri', hour=13, minute=30)
#def scheduled_job1():
#	ScoreBuyStocks.main()
#	print 'This job is run every weekday at 19:00 pm IST.'
	
#@sched.scheduled_job('cron', day_of_week='mon-sun', hour=17, minute=00)
#def scheduled_job3():
#	storeRatios.main()
#	print 'This job is run every weekday at 22:30.'
	
@sched.scheduled_job('cron', day_of_week='mon-sun', hour=21, minute=00)
def scheduled_job4():
	Median.main()
	print 'This job is run every weekday at 5:00 am.'
	
@sched.scheduled_job('cron', day_of_week='mon-sun', hour=22, minute=00)
def scheduled_job2():
	ScoreBuyStocks.main()
	print 'This job is run every weekday at 06:00 am.'

@sched.scheduled_job('cron', day_of_week='mon-fri', hour=5, minute=00)
def scheduled_job():
	buy.main()
	print('This job is run every weekday at 13:00 PM')

print 'Job is running now'
sched.start()
