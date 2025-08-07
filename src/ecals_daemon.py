from ecalspy.core.es_config_manager import ConfigManager
from ecalspy.core.es_epu_api_client import EpuApiClient, EpuCredentials
from ecalspy.core.es_calendar import ParseCalendarResponse, CalendarType

from ecalspy.feat.es_google_calendar import GoogleCalendarApiClient

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from fastapi import FastAPI
import uvicorn

import datetime as dt
import logging
import sys

app = FastAPI()
scheduler = BackgroundScheduler()
epuClient = EpuApiClient()

# Define a route at the root web address ("/")
@app.get("/")
def ReadRoot():
    return {"message": "Hello, FastAPI!"}

@app.get("/api/calendar")
def GetThisWeekCalendar():
    todayDate = dt.date.today()
    nextWeekDate = todayDate + dt.timedelta(weeks=1)
    response = epuClient.POST_GetDanhSachLichTheoTuan(nextWeekDate)
    if response.ok:
        sched = ParseCalendarResponse(response.text)
        return sched.ToDict()

def ScheduleSyncToGoogleCalendar():
    calendarClient = GoogleCalendarApiClient()

    todayDate = dt.date.today()
    nextWeekDate = todayDate + dt.timedelta(weeks=1)

    response = epuClient.POST_GetDanhSachLichTheoTuan(nextWeekDate)
    if response.ok:
        sched = ParseCalendarResponse(response.text)

        total = sched.count
        succeeded = 0
        for schedNode in sched.schedules:
            events = calendarClient.QueryEvents(startTime, endTime)
            if len(events) == 0:
                event = calendarClient.CreateEventFromScheduleNode(schedNode)
                succeeded += 1
        logging.info(f"ScheduleSyncToGoogleCalendar:  {total} total, {succeeded} succeeded, {total - succeeded} failed")
    else:
        logging.warn("Failed to load page:", response.status_code)

if __name__ == "__main__":
    ConfigManager.LoadConfigsFromFile()

    # Only one log file for each day
    iso_today = dt.date.today().isoformat()
    logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
    logging.basicConfig(
        format='[%(asctime)s] |%(levelname)s|: %(message)s',
        datefmt='%Y-%m-%d %I:%M:%S',
        filename=f'daemon_{iso_today}.log',
        filemode='a',
        level=logging.DEBUG
    )

    scheduler.add_job(
        ScheduleSyncToGoogleCalendar,
        trigger=CronTrigger(day_of_week='mon', hour=9, minute=0,),
        id='GoogleCalendarSync'
    )
    scheduler.start()
    uvicorn.run(app, host="127.0.0.1", port=9999)

    ConfigManager.FlushConfig()
