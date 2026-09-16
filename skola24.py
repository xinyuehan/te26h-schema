from datetime import date, timedelta
import requests

from config import (
    HOST,
    SCHOOL_NAME,
    CLASS_NAME,
    X_SCOPE
)

HEADERS = {
    "X-Scope": X_SCOPE,
    "X-Requested-With": "XMLHttpRequest",
    "Content-Type": "application/json",
}


class Skola24:

    def __init__(self):
        self.session = requests.Session()

    def post(self, path, payload=None):
        r = self.session.post(
            f"https://web.skola24.se/api{path}",
            headers=HEADERS,
            json=payload
        )

        r.raise_for_status()
        return r.json()

    def get_school_year(self):

        data = self.post(
            "/get/active/school/years",
            {
                "hostName": HOST,
                "checkSchoolYearsFeatures": False
            }
        )

        return data["data"]["activeSchoolYears"][0]

    def get_unit_guid(self):

        data = self.post(
            "/services/skola24/get/timetable/viewer/units",
            {
                "getTimetableViewerUnitsRequest": {
                    "hostName": HOST
                }
            }
        )

        units = (
            data["data"]
            ["getTimetableViewerUnitsResponse"]
            ["units"]
        )

        for unit in units:
            if unit["unitId"] == SCHOOL_NAME:
                return unit["unitGuid"]

        raise Exception(
            f"School not found: {SCHOOL_NAME}"
        )

    def get_class_guid(self, unit_guid):

        data = self.post(
            "/get/timetable/selection",
            {
                "hostName": HOST,
                "unitGuid": unit_guid,
                "filters": {
                    "class": True,
                    "course": False,
                    "group": False,
                    "period": False,
                    "room": False,
                    "student": False,
                    "subject": False,
                    "teacher": False
                }
            }
        )

        classes = data["data"]["classes"]

        for cls in classes:
            if cls["groupName"] == CLASS_NAME:
                return cls["groupGuid"]

        raise Exception(
            f"Class not found: {CLASS_NAME}"
        )

    def get_render_key(self):

        data = self.post(
            "/get/timetable/render/key",
            None
        )

        return data["data"]["key"]

    def fetch_week(
        self,
        unit_guid,
        school_year,
        class_guid,
        year,
        week
    ):

        render_key = self.get_render_key()

        data = self.post(
            "/render/timetable",
            {
                "renderKey": render_key,
                "host": HOST,
                "unitGuid": unit_guid,
                "schoolYear": school_year,
                "startDate": None,
                "endDate": None,
                "scheduleDay": 0,
                "blackAndWhite": False,
                "width": 1280,
                "height": 720,
                "selectionType": 0,
                "selection": class_guid,
                "showHeader": False,
                "periodText": "",
                "week": week,
                "year": year,
                "privateFreeTextMode": False,
                "privateSelectionMode": None,
                "customerKey": "",
                "personalTimetable": False
            }
        )

        monday = date.fromisocalendar(
            year,
            week,
            1
        )

        lessons = []

        for lesson in (
            data["data"]["lessonInfo"] or []
        ):

            lesson_date = monday + timedelta(
                days=lesson["dayOfWeekNumber"] - 1
            )

            texts = lesson["texts"]

            lessons.append(
                {
                    "date": lesson_date,
                    "start": lesson["timeStart"][:5],
                    "end": lesson["timeEnd"][:5],
                    "subject": (
                        texts[0]
                        if len(texts) > 0 else ""
                    ),
                    "teacher": (
                        texts[1]
                        if len(texts) > 1 else ""
                    ),
                    "room": (
                        texts[2]
                        if len(texts) > 2 else ""
                    ),
                }
            )

        return lessons
