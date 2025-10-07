from datetime import datetime, timedelta

def d(y,m,d):
	return datetime(y,m,d)

# もしかしてendは必要ない？

MONDAY1		 = {'BYDAY': 'MO', 'start': d(2025,9,29), 'end': d(2025,11,17), 'exdate': []}
TUESDAY1	 = {'BYDAY': 'TU', 'start': d(2025,9,30), 'end': d(2025,11,18), 'exdate': []}
WEDNESDAY1 = {'BYDAY': 'WE', 'start': d(2025,10,1), 'end': d(2025,11,19), 'exdate': []}
THURSDAY1	 = {'BYDAY': 'TH', 'start': d(2025,10,2), 'end': d(2025,11,20), 'exdate': []}
FRIDAY1		 = {'BYDAY': 'FR', 'start': d(2025,9,26), 'end': d(2025,11,14), 'exdate': []}

MONDAY2		 = {'BYDAY': 'MO', 'start': d(2025,12,1), 'end': d(2026,2,2), 'exdate': [d(2025,12,29), d(2026,1,12)]}
TUESDAY2	 = {'BYDAY': 'TU', 'start': d(2025,12,2), 'end': d(2026,2,3), 'exdate': [d(2025,12,23), d(2025,12,30)]}
WEDNESDAY2 = {'BYDAY': 'WE', 'start': d(2025,12,3), 'end': d(2026,2,4), 'exdate': [d(2025,12,24), d(2025,12,31)]}
THURSDAY2	 = {'BYDAY': 'TH', 'start': d(2025,12,4), 'end': d(2026,2,5), 'exdate': [d(2025,12,25), d(2026,1,1)]}
FRIDAY2		 = {'BYDAY': 'FR', 'start': d(2025,11,28), 'end': d(2026,2,6), 'exdate': [d(2025,12,26), d(2026,1,2), d(2026,1,16)]}

# 以下は変更なし

TIMETABLE = [timedelta(hours=9), timedelta(hours=10, minutes=40), timedelta(hours=13), timedelta(hours=14, minutes=40), timedelta(hours=16, minutes=20), timedelta(hours=18), timedelta(hours=19, minutes=40)]
PERIOD = timedelta(hours=1, minutes=30)

FREQ = 'WEEKLY' # 繰り返しの頻度
COUNT = 8 # 一タームあたりの講義数(0なら無限)
