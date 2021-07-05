import time
from datetime import datetime, timedelta

# Get current time in RFC3339 format with T and Z
timeNow = datetime.now().isoformat()
timeNow = timeNow.split('.')[0]
timeNow = timeNow + "Z"
timeNow = datetime.strptime(timeNow, '%Y-%m-%dT%H:%M:%SZ')

# Subtract current time by 7 days to get startDate (lower bounds of date to look for clips)
startDate = timeNow - timedelta(days=7)
startDate = startDate.isoformat()
startDate = startDate + "Z"
# Example of startDate variable:
# 2021-06-28T10:53:47Z
# Use startData var for started_at query parameter for twitch clip api calls