import os
import json
import io
import ecalspy.core.es_utils as Es

class CookieManager:
    COOKIE_CACHE_FILENAME = ".cookie-cache"

    @staticmethod
    def LoadCookiesFromBrowsers():
        browserDict = {
            # "Edge": lambda: browser_cookie3.edge(),
            "All" : lambda: browser_cookie3.load()
            # "Chrome": lambda: browser_cookie3.chrome()
        }
        for browserName, cookieGetterFn in browserDict.items():
            try:
                cookies = cookieGetterFn()
                print(f"[+] Loaded cookies from {browserName}", cookies)
                break;
            except Exception as e:
                print(f"[-] Failed to load from {browserName}:", e)
                cookies = None

    @staticmethod
    def LoadCookieFromCommandPrompt() -> dict:
        print("[*] Using manually provided cookie")
        raw_cookie = input("Enter your session cookie (e.g., sessionid=abc123): ")
        return CookieManager.ParseCookies(raw_cookie)

    @staticmethod
    def ParseCookies(cookiesStr: str) -> dict:
        print(cookiesStr)
        return dict(pair.split('=') for pair in cookiesStr.split(';'))

    @staticmethod
    def SaveCookies(cookieDict) -> None:
        # Only save if not already exist
        if Es.FileExists(CookieManager.COOKIE_CACHE_FILENAME):
            return

        cookies = ""
        with open(CookieManager.COOKIE_CACHE_FILENAME, "w") as fp:
            for key, value in cookieDict.items():
                cookies += f"{key}={value};"  
            fp.write(cookies.rstrip(";"))
            fp.flush()
            print("[+] Saved cookies to ./cookie-cache")

    @staticmethod
    def LoadCookieFromCache() -> dict:
        with open(CookieManager.COOKIE_CACHE_FILENAME, "r") as fp:
            cookies = fp.read();
            cookieDict = CookieManager.ParseCookies(cookies)
            print(f"[*] Loaded cookies from {CookieManager.COOKIE_CACHE_FILENAME}")
            return cookieDict;
