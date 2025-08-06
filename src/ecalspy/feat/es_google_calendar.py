from ecalspy.core.es_config_manager import EsConfigManager
from ecalspy.core.es_utils import JsonSerializer
from ecalspy.core.es_calendar import ScheduleNode, PeriodToStr, WeekSchedule

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from pprint import pprint
from datetime import datetime, timezone

import os
import sqlite3

SCOPES = ["https://www.googleapis.com/auth/calendar"]

CALENDAR_API_SECRET_CONFIG_KEY = "GoogleCalendarApiSecret"
AUTHORIZED_INFO_CONFIG_KEY = "GoogleCalendarAuthInfo"

class GoogleCalendarApiClient:
    def __init__(self):
        apiSecret = EsConfigManager.GetConfig(CALENDAR_API_SECRET_CONFIG_KEY)
        if not apiSecret:
            EsConfigManager.PushConfig(CALENDAR_API_SECRET_CONFIG_KEY, "")
            raise Exception(f"{CALENDAR_API_SECRET_CONFIG_KEY} is not provided in {EsConfigManager.CONFIG_FILENAME}")
        userInfo = EsConfigManager.GetConfig(AUTHORIZED_INFO_CONFIG_KEY)

        self.__Creds = userInfo and Credentials.from_authorized_user_info(userInfo, SCOPES) or None
        self.__Service = None

        if not self.ValidCredentials():
            if self.CredentialsNeedRefresh():
                self.__Creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_config(
                    apiSecret, SCOPES
                )
                self.__Creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            EsConfigManager.PushConfig(AUTHORIZED_INFO_CONFIG_KEY, JsonSerializer.Deserialize(self.__Creds.to_json(),
                                                                                             decode=False))
        self.__Service = build("calendar", "v3", credentials=self.__Creds)

    @property
    def service(self):
        return self.__Service

    def ValidCredentials(self) -> bool:
        creds = self.__Creds
        return creds and creds.valid

    def CredentialsNeedRefresh(self) -> bool:
        creds = self.__Creds
        return creds and creds.expired and creds.refresh_token

    def RefreshCredentials(self) -> None:
        creds.refresh(Request())

    def CreateEvent(self, subject: str, startTime: datetime, endTime: datetime, description: str):
        event = {
            'summary': subject,
            'description': description,
            'start': {
                'dateTime': startTime.isoformat(timespec='seconds') + "+07:00",
                'timeZone': 'Asia/Ho_Chi_Minh',
            },
            'end': {
                'dateTime': endTime.isoformat(timespec='seconds') + "+07:00",
                'timeZone': 'Asia/Ho_Chi_Minh',
            },
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'popup', 'minutes': 10},
                ],
            },
        }

        pprint(event)
        return self.__Service.events().insert(calendarId='primary', body=event).execute()

    def CreateEventFromScheduleNode(self, node: ScheduleNode):
        subject = f"{PeriodToStr(node.unitPeriod)}: {node.moduleName} @ {node.room}"
        startTime = datetime.combine(node.date, node.timePeriod["start"])
        endTime = datetime.combine(node.date, node.timePeriod["end"])

        self.CreateEvent(subject, startTime, endTime, str(node))

def SyncCalendarWithWeekSchedule(client: GoogleCalendarApiClient, weekSched: WeekSchedule) -> None:
    # for sched in weekSched.schedules:
    #     client.CreateEventFromScheduleNode(sched)
    CalendarDemo()

def CalendarDemo():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    client = GoogleCalendarApiClient()

    # If there are no (valid) credentials available, let the user log in.
    try:
        service = client.service

        # Call the Calendar API
        now = datetime.now(tz=timezone.utc).isoformat()
        print("Getting the upcoming 10 events")
        events_result = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=now,
                maxResults=10,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        events = events_result.get("items", [])

        if not events:
            print("No upcoming events found.")
            return

        pprint(events[0])
        # Prints the start and name of the next 10 events
        for event in events:
            start = event["start"].get("dateTime", event["start"].get("date"))
            print(start, event["summary"])

    except HttpError as error:
        print(f"An error occurred: {error}")
