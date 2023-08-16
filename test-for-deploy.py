import schedule
import time
import datetime

def my_job():
    # Replace this with the actual code for your job
    print("Running my_job at", datetime.datetime.now())

def schedule_job():
    # Schedule the job to run every 10 to 48 minutes between 8 am and 10 pm
    schedule.every(2).to(48).seconds.do(my_job)

    while True:
        now = datetime.datetime.now()
        if now.hour >= 8 and now.hour <= 22 :
            print(schedule.idle_seconds())
            schedule.run_pending()
        time.sleep(1)  # Sleep for a second to avoid high CPU usage

if __name__ == "__main__":
    schedule_job()