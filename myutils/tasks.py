import time
from celery import shared_task


@shared_task
def simulate_long_task():
    time.sleep(3)
    return "I've completed simulating a long task"
