#!python

from datetime import date, timedelta
import browser_cookie3
import logging

from ecalspy.core.es_cookie_manager import CookieManager
from ecalspy.core.es_epu_api_client import EpuApiClient
from ecalspy.core.es_calendar import ParseCalendarResponse, CalendarType
from ecalspy.core.es_config_manager import ConfigManager

from ecalspy.feat.es_google_calendar import GoogleCalendarApiClient
import ecalspy.core.es_utils as Es

import requests

def main(args):
    # try:
    #     client = EpuApiClient(cookies=CookieManager.LoadCookieFromCache())
    # except FileNotFoundError as e:
    #     client = EpuApiClient(cookies=CookieManager.LoadCookieFromCommandPrompt())
    domain = ConfigManager.GetConfig("TargetDomainUrl")
    cookies = {}

    try:
        response = requests.get(f"https://{domain}", cookies=cookies)

        print("\n--- Response Status ---")
        print(f"Status Code: {response.status_code} {response.reason}")
        print("\n--- Response Headers ---")
        for header, value in response.headers.items():
            print(f"{header}: {value}")
        print("\n--- Request Information ---")
        print(f"Request URL: {response.url}")
        print("Request Headers:")
        for header, value in response.request.headers.items():
            print(f"  {header}: {value}")
        for cookie in response.cookies:
            CookieManager.AddCookie(cookie)

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        pass

if __name__ == "__main__":
    logging.basicConfig(format='[%(asctime)s] |%(levelname)s|: %(message)s', datefmt='%Y-%m-%d %I:%M:%S',
                        filename='runtine.log', filemode='a', level=logging.DEBUG)
    ConfigManager.LoadConfigsFromFile()
    main(None)
    ConfigManager.FlushConfig()
