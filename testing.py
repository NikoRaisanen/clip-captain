from datetime import datetime
from typing import final

mytime = datetime.now().isoformat()
print(mytime)
print(type(mytime))

# initial_timestr = "2021-07-01T07:20:50.52Z"
# initial_time = datetime.strptime(initial_timestr)
final_time = mytime + "Z"
print(final_time)

# print(initial_time)

# 2021-07-01T07:20:50.52Z