from datetime import datetime, timedelta

def d(y,m,d):
	return datetime(y,m,d)

# datetime Objectのweekday() methodは月曜日が0、日曜日が6を返す
# → そのindexに対応する情報を入れる

# 第2ターム月曜日の授業開始日を指定したいときはDATES_DATA[1][0]['start']を参照すれば良い
DATES_DATA: list[list[dict[str, str | datetime | list[datetime]]]] = [
	[
		{'BYDAY': 'MO', 'start': d(2026, 4, 13), 'exdate': [d(2026, 5, 4)]},
		{'BYDAY': 'TU', 'start': d(2026, 4, 14), 'exdate': [d(2026, 5, 5)]},
        {'BYDAY': 'WE', 'start': d(2026, 4, 15), 'exdate': [d(2026, 5, 6)]},
        {'BYDAY': 'TH', 'start': d(2026, 4, 16), 'exdate': []},
        {'BYDAY': 'FR', 'start': d(2026, 4, 17), 'exdate': []}
    ],
	[
        {'BYDAY': 'MO', 'start': d(2026, 6, 8), 'exdate': [d(2026, 7, 20)]},
        {'BYDAY': 'TU', 'start': d(2026, 6, 9), 'exdate': []},
        {'BYDAY': 'WE', 'start': d(2026, 6, 10), 'exdate': []},
        {'BYDAY': 'TH', 'start': d(2026, 6, 11), 'exdate': []},
        {'BYDAY': 'FR', 'start': d(2026, 6, 12), 'exdate': []}
    ],
	[
        {'BYDAY': 'MO', 'start': d(2026, 10, 5), 'exdate': [d(2026, 10, 12)]},
        {'BYDAY': 'TU', 'start': d(2026, 10, 6), 'exdate': [d(2026, 10, 13)]},
        {'BYDAY': 'WE', 'start': d(2026, 10, 7), 'exdate': []},
        {'BYDAY': 'TH', 'start': d(2026, 10, 8), 'exdate': []},
        {'BYDAY': 'FR', 'start': d(2026, 10, 9), 'exdate': []}
    ],
	[
        {'BYDAY': 'MO', 'start': d(2026, 12, 7), 'exdate': [d(2026, 12, 28), d(2027, 1, 11)]},
        {'BYDAY': 'TU', 'start': d(2026, 12, 8), 'exdate': [d(2026, 12, 29)]},
        {'BYDAY': 'WE', 'start': d(2026, 12, 9), 'exdate': [d(2026, 12, 30)]},
        {'BYDAY': 'TH', 'start': d(2026, 12, 10), 'exdate': [d(2026, 12, 31)]},
        {'BYDAY': 'FR', 'start': d(2026, 12, 4), 'exdate': [d(2027, 1, 1), d(2027, 1, 15)]}
    ]
]

TIMETABLE = [
	timedelta(hours=0),
	timedelta(hours=9), 
	timedelta(hours=10, minutes=40), 
	timedelta(hours=13), 
	timedelta(hours=14, minutes=40), 
	timedelta(hours=16, minutes=20), 
	timedelta(hours=18), 
	timedelta(hours=19, minutes=40)
]

PERIOD = timedelta(hours=1, minutes=30)

CLS_PER_TERM = 7