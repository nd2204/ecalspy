from ecalspy.core.es_calendar import CalendarType
from ecalspy.core.es_cookie_manager import CookieManager
from ecalspy.core.es_config_manager import ConfigManager

import requests

from io import BytesIO
from datetime import date
from PIL import Image, UnidentifiedImageError
import zstandard as zstd

class EpuResponse:
    pass

"""
handle the lifetime and validity of the credentials
like refresh token or auth
"""
class EpuCredentials:
    def __init__(self):
        self.__AuthSecret: str = ""

    @property
    def valid(self):
        return self.__AuthSecret

    @property
    def auth(self) -> str:
        return self.__AuthSecret

    @auth.setter
    def auth(self, secret: str):
        self.__AuthSecret = secret

    @staticmethod
    def FromCookies(cookies: dict) -> "EpuCredentials":
        if cookies and ("ASC.AUTH" in cookies):
            creds = EpuCredentials()
            creds.auth = cookies["ASC.AUTH"]
            return creds
        return None

"""
@brief handle all requests related operation
"""
class EpuApiClient:
    DOMAIN_NAME = ConfigManager.CreateOrRetrieveConfig("TargetDomainUrl", "thanhtoanhocphi.epu.edu.vn")
    CALENDAR_ENDPOINT = f"https://{DOMAIN_NAME}/SinhVien/GetDanhSachLichTheoTuan"
    CAPTCHA_ENDPOINT = f"https://{DOMAIN_NAME}/WebCommon/GetCaptcha"
    LOGIN_ENDPOINT = f"https://{DOMAIN_NAME}/sinh-vien-dang-nhap.html"

    def __init__(self, cookies={}):
        if not cookies:
            try:
                self.__Cookies = CookieManager.LoadCookieFromCache()
            except Exception as e:
                self.__Cookies = None
        else:
            self.__Cookies = cookies

        try:
            response = requests.get(f"https://{EpuApiClient.DOMAIN_NAME}", cookies=cookies)

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

            request_headers = response.request.headers
            if "Cookie" in request_headers:
                for cookie in request_headers["Cookie"].split(";"):
                    name, value = [c.strip() for c in cookie.split("=")]
                    cookies[name]= value
            for cookie in response.cookies:
                cookies[cookie.name] = cookie.value

            print(cookies)

        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            pass

    @property
    def cookies(self):
        """The cookies property."""
        return self.__Cookies

    @cookies.setter
    def cookies(self, value):
        self.__Cookies = value

    @property
    def creds(self) -> EpuCredentials:
        return EpuCredentials.FromCookies(self.__Cookies)

    def POST_GetDanhSachLichTheoTuan(self, date: date = date.today(), calendarType: CalendarType = CalendarType.ALL):
        def FormatDateForFormData(date: date):
            return date.strftime("%d/%m/%Y")

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:141.0) Gecko/20100101 Firefox/141.0",
            "Accept": "text/html, */*; q=0.01",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-Requested-With": "XMLHttpRequest",
            "Origin": "https://thanhtoanhocphi.epu.edu.vn",
            "Connection": "keep-alive",
            "Referer": "https://thanhtoanhocphi.epu.edu.vn/lich-theo-tuan.html",
            "Sec-GPC": "1",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "Priority": "u=0",
            "TE": "trailers",
        }

        formData = {
            "pNgayHienTai": FormatDateForFormData(date),
            "pLoaiLich": calendarType
        }

        return requests.post(
            EpuApiClient.CALENDAR_ENDPOINT,
            headers=headers,
            cookies=self.__Cookies,
            data=formData
        )

    def GET_LoginCaptcha(self):
        response = requests.get(EpuApiClient.CAPTCHA_ENDPOINT, cookies=self.__Cookies)
        if response.ok:
            for cookie in response.cookies:
                self.__Cookies[cookie.name] = cookie.value

            print("\n--- Response Status ---")
            print(f"Status Code: {response.status_code} {response.reason}")
            print("\n--- Response Headers ---")
            for header, value in response.headers.items():
                print(f"{header}: {value}")
            if response.headers.get("Content-Type", "").startswith("image/"):
                try:
                    # Try opening as image
                    img = Image.open(BytesIO(response.content))
                    img.verify()  # Ensures file is complete & not truncated

                    # If verify() passes, re-open to actually work with it
                    img = Image.open(BytesIO(response.content))
                    return img

                except UnidentifiedImageError:
                    print("Not a valid image file.")
                    return None
                except Exception as e:
                    print(f"Image validation failed: {e}")
                    return None
            else:
                raise ValueError("Response is not an image")
        return None

    def POST_Login(username, password, captcha):
        pass

def ProcessResponse(response: requests.Response) -> str:
    def IsZstd(content: bytes):
        # Zstandard magic number = 0x28B52FFD (little-endian)
        return content.startswith(b'\x28\xb5\x2f\xfd')

    if response.headers.get("Content-Encoding") == "zstd" and IsZstd(response.content):
        dctx = zstd.ZstdDecompressor()
        with dctx.stream_reader(io.BytesIO(response.content)) as reader:
            decoded_bytes = reader.read()
            return decoded_bytes.decode("utf-8")
    else:
        return response.text
