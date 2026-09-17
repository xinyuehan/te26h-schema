from datetime import datetime
from datetime import timedelta
from datetime import timezone
from zoneinfo import ZoneInfo

from icalendar import Calendar
from icalendar import Event

from skola24 import Skola24

api = Skola24()

school_year = api.get_school_year()

unit_guid = api.get_unit_guid()

class_guid = api.get_class_guid(unit_guid)

start_date = datetime.fromisoformat(
    school_year["from"]
).date()

end_date = datetime.fromisoformat(
    school_year["to"]
).date()

weeks = set()

d = start_date

while d <= end_date:

    iso = d.isocalendar()

    weeks.add(
        (
            iso.year,
            iso.week
        )
    )

    d += timedelta(days=7)

calendar = Calendar()

all_lessons = []

for year, week in sorted(weeks):

    print(
        f"Hämtar vecka {week} {year}"
    )

    try:

        lessons = api.fetch_week(
            unit_guid,
            school_year["guid"],
            class_guid,
            year,
            week
        )

        all_lessons.extend(
            lessons
        )

    except Exception as ex:
        print(ex)

sweden = ZoneInfo("Europe/Stockholm")

for lesson in all_lessons:

    start_dt = datetime.strptime(
        f"{lesson['date']} {lesson['start']}",
        "%Y-%m-%d %H:%M"
    ).replace(tzinfo=sweden)

    end_dt = datetime.strptime(
        f"{lesson['date']} {lesson['end']}",
        "%Y-%m-%d %H:%M"
    ).replace(tzinfo=sweden)

    start_dt = start_dt.astimezone(timezone.utc)
    end_dt = end_dt.astimezone(timezone.utc)
    
    event = Event()

    event.add(
        "summary",
        lesson["subject"]
    )

    event.add(
        "location",
        lesson["room"]
    )

    event.add(
        "description",
        lesson["teacher"]
    )

    event.add(
        "dtstart",
        start_dt
    )

    event.add(
        "dtend",
        end_dt
    )

    calendar.add_component(
        event
    )

with open(
    "calendar.ics",
    "wb"
) as f:

    f.write(
        calendar.to_ical()
    )

print()
print(
    f"Calendar created with "
    f"{len(all_lessons)} lessons"
)
print("calendar.ics")
