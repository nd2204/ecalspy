from ecalspy.core.es_utils import JsonSerializer

from datetime import datetime, date, time
from enum import Enum
from bs4 import BeautifulSoup, Tag
from textwrap import dedent

class CalendarType(Enum):
    ALL = 0
    LICH_HOC = 1
    LICH_THI = 2

class ScheduleType(Enum):
    LY_THUYET = 0
    THUC_HANH = 1
    THI = 2
    TRUC_TUYEN = 3
    TAM_NGUNG = 4

def SchedTypeToString(schedType: ScheduleType) -> str:
    match schedType:
        case ScheduleType.LY_THUYET:
            return "Lý thuyết"
    "Thực hành"
    "Thi"
    "Trực tuyến"
    "Tạm ngưng"

class ScheduleNode:
    def __init__(self):
        self.moduleName : str = ""
        self.moduleId : str = ""
        self.timePeriod : dict[str, time] = { "start": time.min, "end": time.min }
        self.unitPeriod : dict[str, int] = { "start": 0, "end": 0}
        self.room : str = ""
        self.lecturer : str = ""
        self.schedType : ScheduleType = ScheduleType.LY_THUYET
        self.date: date = date.min

    def __eq__(self, o):
        return \
            self.moduleId == o.moduleId \
            and self.unitPeriod["start"] == o.unitPeriod["start"] \
            and self.unitPeriod["end"] == o.unitPeriod["end"] \
            and self.schedType == o.schedType \
            and self.date == o.date \

    def SetSchedTypeFromColor(self, color: str):
        colorToSchedType = {
            "#71cb35": ScheduleType.THUC_HANH,
            "#fdff9a": ScheduleType.THI,
            "#92d6ff": ScheduleType.TRUC_TUYEN
        }
        if color in colorToSchedType:
            self.schedType = colorToSchedType[color]

    def __str__(self):
        return dedent(f"""
            Tên học phần: {self.moduleName}
            Mã lớp: {self.moduleId}
            Tiết: {self.unitPeriod["start"]} - {self.unitPeriod["end"]}
            Giờ: {self.timePeriod["start"]} - {self.timePeriod["end"]}
            Phòng: {self.room}
            GV: {self.lecturer}
            Loại lịch: {self.schedType.value}
            Ngày: {self.date.strftime("%d/%m/%Y")}
        """)

    def ToDict(self) -> dict:
        return {
            "moduleName": self.moduleName,
            "moduleId": self.moduleId,
            "unitPeriod": {
                "start": self.unitPeriod["start"],
                "end": self.unitPeriod["end"]
            },
            "timePeriod": {
                "start": self.timePeriod["start"].isoformat(timespec='seconds'),
                "end": self.timePeriod["end"].isoformat(timespec='seconds')
            },
            "room": self.room,
            "lecturer": self.lecturer,
            "schedType": self.schedType.value,
            "date": self.date.isoformat()
        }

    def ToJson(self):
        return JsonSerializer.Serialize(self.ToDict())

def PeriodToStr(period: dict, fnStrGetter = lambda a: a) -> str:
    assert callable(fnStrGetter)
    return f"{fnStrGetter(period["start"])}-{fnStrGetter(period["end"])}"

class WeekSchedule:
    type ScheduleNodeList = list[list[list[ScheduleNode]]]

    def __init__(self):
        self.__ScheduleNodes : ScheduleNodeList = [[None for _ in range(3)] for _ in range(7)]
        self.__ActiveCount : int = 0

    @property
    def schedules(self):
        for dayNode in self.__ScheduleNodes:
            for sessionNode in dayNode:
                if type(sessionNode) is not list:
                    continue
                for sched in sessionNode:
                    yield sched

    @property
    def count(self):
        """Return the number of active node in calendar."""
        return self.__ActiveCount

    def AddNode(self, node: ScheduleNode, session: int, dayInWeek: int):
        if not self.__ScheduleNodes[dayInWeek][session]:
            self.__ScheduleNodes[dayInWeek][session] = [];
        self.__ScheduleNodes[dayInWeek][session].append(node);
        self.__ActiveCount += 1

    def ToDict(self):
        result = {}
        isEmpty = True
        for dayInWeek, dayNode in enumerate(self.__ScheduleNodes, start=0):
            sessionDict = {}
            for session, sessionNode in enumerate(dayNode, start=0):
                sessionKey = WeekSchedule.GetSessionStr(session)
                if type(sessionNode) is list:
                    sessionDict[sessionKey] = [scheduleNode.ToDict() for scheduleNode in sessionNode]
                    isEmpty = False

            result[WeekSchedule.GetDayInWeekStr(dayInWeek)] = sessionDict

        if isEmpty:
            raise Exception("The schedule is empty!")

        return result

    def ToJson(self, encode=True):
        return JsonSerializer.Serialize(self.ToDict(), encode)

    def ToIcs():
        ...

    @staticmethod
    def GetDayInWeekStr(dayInWeek: int) -> str:
        assert dayInWeek >= 0 # Do not allow negative value
        dayInWeekStrTuple = ("mon", "tues", "wed", "thurs", "fri", "sat", "sun")
        return dayInWeekStrTuple[dayInWeek]

    @staticmethod
    def GetSessionStr(session: int) -> str:
        assert session >= 0 # Do not allow negative value
        sessionStrTuple = ("morning", "afternoon", "evening")
        return sessionStrTuple[session]

def ParseCalendarResponse(htmlText) -> WeekSchedule:
    soup = BeautifulSoup(htmlText, 'html.parser')

    headerRow = soup.select(".table-responsive table thead tr")
    ths = headerRow[0].find_all("th")[1:]
    datesInWeek = [ParseTableHeaderCell(th) for th in ths]

    rows = soup.select(".table-responsive table tbody tr")
    schedule = WeekSchedule()
    for row in rows:
        tds = row.find_all("td")

        if "lichtheotuan-buoisang" in tds[0]["lang"]:
            session = 0
        elif "lichtheotuan-buoichieu" in tds[0]["lang"]:
            session = 1
        elif "lichtheotuan-buoitoi" in tds[0]["lang"]:
            session = 2
        else:
            raise Exception("Unsupported operation")

        for dayInWeek, td in enumerate(tds[1:], start=0):
            # Extract plain text or inner HTML
            for div in td.select("div.content"):
                node = ParseCalendarNodeFromHtml(div)
                node.date = datesInWeek[dayInWeek]
                schedule.AddNode(node, session, dayInWeek)

    return schedule

def ParseTableHeaderCell(th: Tag) -> date:
    if th.span:
        th.span.decompose()
    return datetime.strptime(th.get_text(strip=True), "%d/%m/%Y").date()

def ParseCalendarNodeFromHtml(htmlNode: Tag) -> ScheduleNode:
    # assume a html node is in this form:
    # <div class="content color-lichhoc text-left" style="text-align:left">
    #   <b><a ...>Ngôn ngữ kịch bản</a></b>
    #   <p>D17CNPM5 - 010100475705</p>
    #   <p><span lang="lichtheotuan-tiet">Tiết</span>: 6 - 10<br/></p>
    #   <p><span lang="lichtheotuan-gio">Giờ</span>: 12:30 - 17:00<br/></p>
    #   <p><span lang="giang-duong">Phòng</span>: <font>E203</font></p>
    #   <p><span lang="lichtheotuan-gv">GV</span>: <font>Đỗ Đức Cường</font></p>
    # </div>
    # TODO: detect schedType base on color
    pTags = htmlNode.find_all("p");

    node = ScheduleNode()
    node.moduleName = htmlNode.find("b").get_text(strip=True)
    node.moduleId = pTags[0].get_text(strip=True)

    # Set node schedule type
    style = htmlNode["style"]
    klass = htmlNode.get_attribute_list("class")
    if style:
        styleDict = ParseStyleAttribToDict(style)
        if "background-color" in styleDict:
            # background-color property only exist for tag with color-lichhoc class
            node.SetSchedTypeFromColor(styleDict["background-color"])
        elif not "color-lichhoc" in klass:
            # 'color-lichhoc' indicate it is not ScheduleType.THI or ScheduleNode.TAM_NGUNG
            # so without it only those two are the possible
            # NOTE: right now we don't have any info for ScheduleNode.TAM_NGUNG so we'll
            # assume schedType = ScheduleType.THI by default
            node.schedType = ScheduleType.THI

    parseTimeStr = lambda timeStr: datetime.strptime(timeStr, "%H:%M").timetz()

    for span in htmlNode.find_all("span"):
        parent = span.parent
        lang = span["lang"]
        span.decompose()
        strippedContent = parent.get_text()[1:].strip()
        if "lichtheotuan-tiet" in lang:
            period = strippedContent.split("-")
            node.unitPeriod["start"] = int(period[0].strip())
            node.unitPeriod["end"] = int(period[1].strip())
        elif "lichtheotuan-gio" in lang:
            period = strippedContent.split("-")
            node.timePeriod["start"] = parseTimeStr(period[0].strip())
            node.timePeriod["end"] = parseTimeStr(period[1].strip())
        elif "giang-duong" in lang:
            node.room = strippedContent
        elif "lichtheotuan-gv" in lang:
            node.lecturer = strippedContent

    return node
    ...

def ParseStyleAttribToDict(styleStr: str) -> dict:
    styleDict = {}
    if styleStr:
        rules = styleStr.split(';')
        for rule in rules:
            if ':' in rule:
                key, value = rule.split(':', 1)
                styleDict[key.strip()] = value.strip()
    return styleDict

