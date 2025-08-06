#!python

from datetime import date, timedelta
import browser_cookie3

from ecalspy.core.es_cookie_manager import CookieManager
from ecalspy.core.es_epu_api_client import EpuApiClient
from ecalspy.core.es_calendar import ParseCalendarResponse, CalendarType
from ecalspy.core.es_config_manager import EsConfigManager

from ecalspy.feat.es_google_calendar import GoogleCalendarApiClient, SyncCalendarWithWeekSchedule
import ecalspy.core.es_utils as Es

def main(args):
    client = EpuApiClient()

    try:
        client.cookies = CookieManager.LoadCookieFromCache()
    except FileNotFoundError as e:
        client.cookies = CookieManager.LoadCookieFromCommandPrompt()

    todayDate = date.today()
    nextWeekDate = todayDate + timedelta(weeks=1)
    requestData = EpuApiClient.BuildCalendarQueryForm(nextWeekDate, CalendarType.ALL)
    response = client.POST_GetDanhSachLichTheoTuan(requestData)

    if response.ok:
        CookieManager.SaveCookies(client.cookies)

        print(response.url)
        print("[+] Page loaded successfully")
        print("Content-Encoding:", response.headers.get("Content-Encoding"))
        sched = ParseCalendarResponse(response.text)

        SyncCalendarWithWeekSchedule(GoogleCalendarApiClient(), sched)

    else:
        print("[-] Failed to load page:", response.status_code)

if __name__ == "__main__":
    EsConfigManager.LoadConfigsFromFile()
    # TODO: implement args
    main(None)
    # CalendarDemo()
    EsConfigManager.FlushConfig()
