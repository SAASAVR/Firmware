#Tasks to be produced by Faker module
import random
from faker.providers import BaseProvider
from faker import Faker
import config
import time
import requests
import json
import uuid


# Defining TaskProvider
class TaskProvider(BaseProvider):
    def task_priority(self):
        severity_levels = [
            'Low', 'Moderate', 'Major', 'Critical'
        ]
        return severity_levels[random.randint(0, len(severity_levels)-1)]
    

#Create a Faker instance and seeding to have the same results every time we execute
#Return data in english
fakeTasks = Faker('en_US')
#Seed the Faker instance to have the same results every time we run the program
fakeTasks.seed_instance(0)
#Assign the TaskProvider to the Faker instance
fakeTasks.add_provider(TaskProvider)

#Method to generate fake task
def produce_task(batchid, taskid):
    #Composing the message
    message = {
        'batchid': batchid, 'id': taskid, 'owner': fakeTasks.unique.name(), 'priority': fakeTasks.task_priority()
    }

    return message

def send_webhook(msg):
    """
    Send a webhook to a specified URL
    :param msg: task details
    :return:
    """
    try:
        #post a webhook message
        #default is a function applied to objects that are not serializable = it converts them to str
        resp = requests.post(config.WEBHOOK_RECEIVER_URL, data=json.dumps(msg, sort_keys=True, default=str), headers={'Content-Type': 'application/json'}, timeout=1.0)

        resp.raise_for_status()
    except requests.exceptions.HTTPError as err:
        #print("An HTTP Error occured",repr(err))
        pass
    except requests.exceptions.ConnectionError as err:
        #print("A Timeout Error occured", repr(err))
        pass
    except requests.exceptions.RequestException as err:
        #print("An Unknown Error occured", repr(err))
        pass
    except:
        pass
    else:
        return resp.status_code
    
    #Generate A Bunch Of Fake Tasks

def produce_bunch_tasks():
    """
    Generate a Bunch of Fake Tasks
    """

    n = random.randint(config.MIN_NBR_TASKS, config.MAX_NBR_TASKS)
    batchid = str(uuid.uuid4())
    for i in range(n):
        msg = produce_task(batchid, i)
        resp = send_webhook(msg)
        time.sleep(config.WAIT_TIME)
        print(i, "out of ", n, " -- Status", resp, " -- Message = ", msg)
        yield resp, n, msg


if __name__ == "__main__":
    for resp, total, msg in produce_bunch_tasks():
        pass


