#!python

from ecalspy.core.es_cookie_manager import CookieManager
from ecalspy.core.es_epu_api_client import EpuApiClient
from ecalspy.core.es_calendar import ParseCalendarResponse, CalendarType
from ecalspy.core.es_config_manager import ConfigManager

from ecalspy.feat.es_google_calendar import GoogleCalendarApiClient

import requests
import browser_cookie3
import logging
import argparse
from PIL import Image

from datetime import date, timedelta

def main():
    # try:
    #     client = EpuApiClient(cookies=CookieManager.LoadCookieFromCache())
    # except FileNotFoundError as e:
    #     client = EpuApiClient(cookies=CookieManager.LoadCookieFromCommandPrompt())

    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--user", help="the username used for signing in", type=str)
    parser.add_argument("-p", "--password", help="the password used for signing in", type=str)
    args = parser.parse_args()

    if args.user:
        login_id = args.user
        password = args.password or input("Enter your password: ")
        print(password)

        domain = ConfigManager.CreateOrRetrieveConfig("TargetDomainUrl", "thanhtoanhocphi.epu.edu.vn")
        cookies = {}
        client = EpuApiClient(cookies)
        try:
            img = client.GET_LoginCaptcha()
            from ecalspy.core.es_ocr import preprocess_image_for_ocr
            preprocess_image_for_ocr(img.convert("RGB"))
        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            pass

if __name__ == "__main__":
    ConfigManager.LoadConfigsFromFile()
    main()
    ConfigManager.FlushConfig()
