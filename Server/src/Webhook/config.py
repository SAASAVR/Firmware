#All code from this directory based on: 
# https://www.thepythoncode.com/article/webhooks-in-python-with-flask

SECRET_KEY = 'SECRET_KEY'

#Minimum number of generatable tasks
MIN_NBR_TASKS = 1
#Maximum number of generatable tasks
MAX_NBR_TASKS = 100
#Time to wait when producing tasks
WAIT_TIME = 1
#Webhook endpoint mapping to the listener
WEBHOOK_RECEIVER_URL = 'http://localhost:5001/consumetasks'

#Map to the REDIS Server Port
BROKER_URL = 'redis://localhost:6379'