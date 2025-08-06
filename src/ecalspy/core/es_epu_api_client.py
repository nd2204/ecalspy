from ecalspy.core.es_calendar import CalendarType

import requests
from datetime import date
import zstandard as zstd

"""
@brief handle all requests related operation
"""
class EpuApiClient:
    DOMAIN_NAME = "thanhtoanhocphi.epu.edu.vn"
    CALENDAR_ENDPOINT = f"https://{DOMAIN_NAME}/SinhVien/GetDanhSachLichTheoTuan"

    def __init__(self):
        self.__RequestHeaders = {
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

        self.__Cookies = {}

    @property
    def cookies(self):
        """The cookies property."""
        return self.__Cookies

    @cookies.setter
    def cookies(self, value):
        self.__Cookies = value

    def POST_GetDanhSachLichTheoTuan(self, formData):
        return requests.post(EpuApiClient.CALENDAR_ENDPOINT, headers=self.__RequestHeaders, cookies=self.__Cookies,
                             data=formData)

    @staticmethod
    def BuildCalendarQueryForm(date: date, calendarType: CalendarType) -> dict:
        assert calendarType
        assert date

        def FormatDateForFormData(date: date):
            return date.strftime("%d/%m/%Y")

        return {
            "pNgayHienTai": FormatDateForFormData(date),
            "pLoaiLich": str(calendarType)
        }

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
