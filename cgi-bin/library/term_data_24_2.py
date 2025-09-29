from datetime import datetime, timedelta

MONDAY1    = [datetime(2024,  9, 30), datetime(2024, 10,  7), datetime(2024, 10, 14), datetime(2024, 10, 21), datetime(2024, 10, 28), datetime(2024, 11,  4), datetime(2024, 11, 11), datetime(2024, 11, 18)]
TUESDAY1   = [datetime(2024, 10,  1), datetime(2024, 10,  8), datetime(2024, 10, 15), datetime(2024, 10, 22), datetime(2024, 10, 29), datetime(2024, 11,  5), datetime(2024, 11, 12), datetime(2024, 11, 19)]
WEDNESDAY1 = [datetime(2024, 10,  2), datetime(2024, 10,  9), datetime(2024, 10, 16), datetime(2024, 10, 23), datetime(2024, 10, 30), datetime(2024, 11,  6), datetime(2024, 11, 13), datetime(2024, 11, 20)]
THURSDAY1  = [datetime(2024, 10,  3), datetime(2024, 10, 10), datetime(2024, 10, 17), datetime(2024, 10, 24), datetime(2024, 10, 31), datetime(2024, 11,  7), datetime(2024, 11, 14), datetime(2024, 11, 21)]
FRIDAY1    = [datetime(2024,  9, 27), datetime(2024, 10,  4), datetime(2024, 10, 11), datetime(2024, 10, 18), datetime(2024, 10, 25), datetime(2024, 11,  1), datetime(2024, 11,  8), datetime(2024, 11, 15)]

MONDAY2    = [datetime(2024, 12,  2), datetime(2024, 12,  9), datetime(2024, 12, 16), datetime(2024, 12, 23), datetime(2025,  1,  6), datetime(2025,  1, 20), datetime(2025,  1, 27), datetime(2025,  2,  3)]
TUESDAY2   = [datetime(2024, 12,  3), datetime(2024, 12, 10), datetime(2024, 12, 17), datetime(2025,  1,  7), datetime(2025,  1, 14), datetime(2025,  1, 21), datetime(2025,  1, 28), datetime(2025,  2,  4)]
WEDNESDAY2 = [datetime(2024, 12,  4), datetime(2024, 12, 11), datetime(2024, 12, 18), datetime(2025,  1,  8), datetime(2025,  1, 15), datetime(2025,  1, 22), datetime(2025,  1, 29), datetime(2025,  2,  5)]
THURSDAY2  = [datetime(2024, 12,  5), datetime(2024, 12, 12), datetime(2024, 12, 19), datetime(2025,  1,  9), datetime(2025,  1, 16), datetime(2025,  1, 23), datetime(2025,  1, 30), datetime(2025,  2,  6)]
FRIDAY2    = [datetime(2024, 11, 29), datetime(2024, 12,  6), datetime(2024, 12, 13), datetime(2024, 12, 20), datetime(2025,  1, 10), datetime(2025,  1, 24), datetime(2025,  1, 31), datetime(2025,  2,  7)]

# 以下は変更なし

TIMETABLE = [timedelta(hours=9), timedelta(hours=10, minutes=40), timedelta(hours=13), timedelta(hours=14, minutes=40), timedelta(hours=16, minutes=20), timedelta(hours=18), timedelta(hours=19, minutes=40)]
PERIOD = timedelta(hours=1, minutes=30)