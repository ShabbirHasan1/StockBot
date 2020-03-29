from apscheduler.schedulers.blocking import BlockingScheduler
import MovingAverage
import os
import logging
import sell
import buy
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

@sched.scheduled_job('interval', minutes=59)
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


@sched.scheduled_job('cron', day_of_week='mon-sun', hour=11, minute=40)
def scheduled_job1():
	storeFinancials.main()
	print 'This job is run every weekday at 19:40.'
	
	
@sched.scheduled_job('cron', day_of_week='mon-sun', hour=19, minute=00)
def scheduled_job4():
	Median.main()
	print 'This job is run every weekday at 3:00 am.'
	
@sched.scheduled_job('cron', day_of_week='mon-sun', hour=7, minute=00)
def scheduled_job2():
	ScoreBuyStocks.main()
	print 'This job is run every weekday at 15:00.'

@sched.scheduled_job('cron', day_of_week='mon-fri', hour=6, minute=00)
def scheduled_job():
	buy.main()
	print('This job is run every weekday at 14:00 PM')

print 'Job is running now'
sched.start()
