"""from datetime import datetime, date, time, timedelta

# Create a specific date
specific_date = date(2024, 12, 25)
print(specific_date)

# Create a specific datetime
specific_datetime = datetime(2024, 12, 25, 10, 30, 0)  # 2024-12-25 10:30:00
print(specific_datetime)

# Create just a time object
meeting_time = time(14, 30)  # 2:30 PM
print(meeting_time)

# Combine date and time
combined = datetime.combine(specific_date, meeting_time)
print(combined)"""

from datetime import datetime, date, time, timedelta, timezone

specific_date = date(2024, 12, 25)

print(specific_date)

specific_date = datetime(2024, 12, 27, 10, 30, 0)

print(specific_date)

meeting_time = time(10, 30, 0)

print(f"meeting time is : {meeting_time} ")

meeting_time = time(14, 30)
print(f"meeting time is : {meeting_time} ")

meeting_time = datetime.combine(specific_date, meeting_time)
print(meeting_time)

"""now = datetime.now()

# Common formats
print(now.strftime("%Y-%m-%d"))           # 2024-01-15
print(now.strftime("%Y-%m-%d %H:%M:%S"))  # 2024-01-15 14:30:45
print(now.strftime("%I:%M %p"))            # 02:30 PM
print(now.strftime("%A, %B %d, %Y"))       # Monday, January 15, 2024

# Parse string to datetime
date_str = "2024-01-15"
parsed_date = datetime.strptime(date_str, "%Y-%m-%d")
print(parsed_date)"""

from zoneinfo import ZoneInfo

""" how to display time in a specific format  """

now = datetime.now(timezone.utc)
# printing current time  and time in specific formats
print(now.strftime("%d-%m-%y"))
print(now.strftime("%d-%m-%y %H:%M:%S"))
print(now.strftime("%I:%M %p"))  # 02:30 PM

pakistan_tz = ZoneInfo("Asia/Karachi")  # or pytz.timezone('Asia/Karachi')
now_pakistan = now.astimezone(pakistan_tz)

print(now_pakistan)


"""working with time delta for applying arthimateic operator """
"""
from datetime import datetime, timedelta

now = datetime.now(timezone.utc)

# These are all just adding numbers to timestamp:
one_day = timedelta(days=1)        # 86400 seconds
one_hour = timedelta(hours=1)      # 3600 seconds
one_minute = timedelta(minutes=1)  # 60 seconds

tomorrow = now + one_day
next_week = now + timedelta(weeks=1) 

"""

one_day = timedelta(days=1)
one_hours = timedelta(hours=1)
minute = timedelta(minutes=10)

send_notification = now_pakistan + minute

print(send_notification)


def full_date(value):
    print(value.strftime("%d %B %Y"))


date_obj = datetime(2024, 12, 25)
full_date(date_obj)
