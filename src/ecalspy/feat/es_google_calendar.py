from ecalspy.core.es_config_manager import ConfigManager
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
import logging

SCOPES = ["https://www.googleapis.com/auth/calendar"]

CALENDAR_API_SECRET_CONFIG_KEY = "GoogleCalendarApiSecret"
AUTHORIZED_INFO_CONFIG_KEY = "GoogleCalendarAuthInfo"

class GoogleCalendarApiClient:
    def __init__(self):
        apiSecret = ConfigManager.GetConfig(CALENDAR_API_SECRET_CONFIG_KEY)
        if not apiSecret:
            ConfigManager.PushConfig(CALENDAR_API_SECRET_CONFIG_KEY, "")
            raise Exception(f"{CALENDAR_API_SECRET_CONFIG_KEY} is not provided in {ConfigManager.CONFIG_FILENAME}")
        userInfo = ConfigManager.GetConfig(AUTHORIZED_INFO_CONFIG_KEY)

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
            ConfigManager.PushConfig(AUTHORIZED_INFO_CONFIG_KEY, JsonSerializer.Deserialize(self.__Creds.to_json(),
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

    def QueryEventsFromSchedNodes(self, node: ScheduleNode):
        startTime = datetime.combine(node.date, node.timePeriod["start"])
        endTime = datetime.combine(node.date, node.timePeriod["end"])

        return self.QueryEvents(startTime, endTime)

    def QueryEvents(self, startTime: datetime, endTime: datetime):
        events_result = self.__Service.events().list(
            calendarId="primary",
            timeMin=startTime.isoformat() + "+07:00",
            timeMax=endTime.isoformat() + "+07:00",
            timeZone="UTC",
            singleEvents=True,
            orderBy="startTime"
        ).execute()

        events = events_result.get("items", [])
        return events;

    def IsTimeSlotAvail(self, startTime: datetime, endTime: datetime) -> bool:
        events = self.QueryEvents(startTime, endTime)
        return len(events) == 0

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

        return self.__Service.events().insert(calendarId='primary', body=event).execute()

    def CreateEventFromScheduleNode(self, node: ScheduleNode) -> int:
        subject = f"{PeriodToStr(node.unitPeriod)}: {node.moduleName} @ {node.room}"
        startTime = datetime.combine(node.date, node.timePeriod["start"])
        endTime = datetime.combine(node.date, node.timePeriod["end"])
        return self.CreateEvent(subject, startTime, endTime, description=str(node))
