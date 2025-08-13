from ecalspy.core.es_config_manager import ConfigManager
from ecalspy.core.es_epu_api_client import EpuApiClient, EpuCredentials
from ecalspy.core.es_calendar import ParseCalendarResponse, CalendarType

from ecalspy.feat.es_google_calendar import GoogleCalendarApiClient

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from fastapi import FastAPI, Response, Cookie
import uvicorn

import datetime as dt
import logging
import sys

app = FastAPI()
scheduler = BackgroundScheduler()
epuClient = EpuApiClient()

from pydantic import BaseModel

class Cookies(BaseModel):
    pass

# Define a route at the root web address ("/")
@app.get("/")
def ReadRoot():
    client = EpuApiClient()
    for key, val in client.cookies.items():
        response.set_cookie(key=f"{key}", value=f"{val}")

@app.get("/api/v1/calendar")
def GetThisWeekCalendar():
    epuClient = EpuApiClient() 
    # todayDate = dt.date.today()
    # nextWeekDate = todayDate + dt.timedelta(weeks=1)
    # response = epuClient.POST_GetDanhSachLichTheoTuan(nextWeekDate)
    # if response.ok:
    #     sched = ParseCalendarResponse(response.text)
    #     return sched.ToDict()
    return {}

@app.get("/api/v1/captcha")
def GetLoginCaptcha(response: Response):
    return {"message": "Come to the dark side, we have cookies"}

@app.post("/api/v1/login")
def Login():
    pass

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
            events = calendarClient.QueryEventsFromSchedNodes(schedNode)
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

    # ScheduleSyncToGoogleCalendar()

    scheduler.add_job(
        ScheduleSyncToGoogleCalendar,
        trigger=CronTrigger(day_of_week='mon', hour=9, minute=0,),
        id='GoogleCalendarSync'
    )
    scheduler.start()

    uvicorn.run(app, host="127.0.0.1", port=9999)

    ConfigManager.FlushConfig()
