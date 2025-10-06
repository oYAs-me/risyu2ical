#!/usr/bin/python3
# -*- coding: utf-8 -*-

import cgi, cgitb
import json
from datetime import datetime, timedelta
from icalendar import Calendar, Event, vText
from dateutil import tz
import random
import os
from library import term_data_25_2 as term_data

# 前後期か判別するための定数
SEMESTER = [[1,2], [3,4]]
use_semester = SEMESTER[1] # この数字を変えれば学期を変えられる

# iCalの初期化とメタデータ設定
def ical_init(cal_name):
  cal = Calendar()
  cal.add('prodid', f"-//yHOP//Python//{cal_name}//ja")
  cal.add('version', '3.0')
  cal.add('calscale', 'GREGORIAN')
  cal.add('method', 'REQUEST')
  return cal

# RRULEを作成
def make_rrule(rrule_info, test=True, nx75=False):
  rrule = {'FREQ': term_data.FREQ} # 繰り返しの頻度
  rrule['BYDAY'] = rrule_info['BYDAY'] # 曜日
  rrule['exdate'] = rrule_info['exdate'] # 繰り返しから除外する日
  count = term_data.COUNT
  if nx75: # スポーツ実技のときは，初回の講義が行われない
    rrule['COUNT'] = str(count-1)
    rrule['exdate'].append(rrule_info['start']) # 初回の講義を繰り返しから除外する
  elif test: # 期末テストがあるときは，16回目の講義が期末テストになる
    rrule['COUNT'] = str(count)
  else: # 期末テストがないときは，16回目の講義がなくなる
    rrule['COUNT'] = str(count-1)
  return rrule

def create_event(subject, classroom, dtstart, cls_delta, rrule):
  event = Event()
  event.add('summary', subject)
  description = f"{subject} ({teacher})"
  event.add('description', description)
  event.add('location', classroom)
  event.add('dtstart', dtstart.astimezone(tz.gettz("Asia/Tokyo")))
  dtend = dtstart + cls_delta
  event.add('dtend', dtend.astimezone(tz.gettz("Asia/Tokyo")))
  event.add('rrule', rrule)
  return event

# ↓は情報をreturnするやつ
cgitb.enable()
storage = cgi.FieldStorage()
print("Content-type: text/html\n")

cal_name = storage.getvalue("name")
# ical形式の変数を用意
cal = ical_init(cal_name)

# detaの受信
data = storage.getvalue("sent") # sent: json形式の講義idリスト
data = json.loads(data)
test_data = storage.getvalue("test") # test: json形式の期末テスト有無リスト
test_json = json.loads(test_data)

with open('../files/cls_info.json') as f:
  json_dict = json.load(f)

for id, test in zip(data, test_json):
  if id == '':
    continue
  json_dict_id = json_dict[id]
  # タームが合っているか確認
  if json_dict_id['term'][0]  == use_semester[0]:
    term1 = True
    try:
      if json_dict_id['term'][1] == use_semester[1]:
        term2 = True
      else:
        term2 = False
    except:
      term2 = False
  else:
    term1 = False
    if json_dict_id['term'][0] == use_semester[1]:
      term2 = True
    else:
      term2 = False

  # 授業の情報を確認
  try:
    day = json_dict_id['day']
    subject = json_dict_id['subject']
    teacher = json_dict_id['teacher']
    classroom = json_dict_id['classroom']
  except IndexError:
    continue
  day = day.split(',')
  date = []
  for d in day: # 開始時刻を入れたdateリストを作成
    da = []
    try: # 「火3～5」の講義時間の処理
      cls_delta = (int(d[3]) - int(d[1]) + 1) * timedelta(hours=1, minutes=40) - timedelta(minutes=10)
    except IndexError:
      cls_delta = term_data.PERIOD

    # 時間割から実際の日時をリストアップする
    if d[0] == '月':
      if term1:
        event = create_event(subject, classroom, term_data.MONDAY1['start'] + term_data.TIMETABLE[int(d[1])-1], cls_delta, make_rrule(term_data.MONDAY1, test, id[:4]=='NX75'))
        cal.add_component(event)
      if term2:
        event = create_event(subject, classroom, term_data.MONDAY2['start'] + term_data.TIMETABLE[int(d[1])-1], cls_delta, make_rrule(term_data.MONDAY2, test, id[:4]=='NX75'))
        cal.add_component(event)
      continue
    if d[0] == '火':
      if term1:
        event = create_event(subject, classroom, term_data.TUESDAY1['start'] + term_data.TIMETABLE[int(d[1])-1], cls_delta, make_rrule(term_data.TUESDAY1, test, id[:4]=='NX75'))
        cal.add_component(event)
      if term2:
        event = create_event(subject, classroom, term_data.TUESDAY2['start'] + term_data.TIMETABLE[int(d[1])-1], cls_delta, make_rrule(term_data.TUESDAY2, test, id[:4]=='NX75'))
        cal.add_component(event)
      continue
    if d[0] == '水':
      if term1:
        event = create_event(subject, classroom, term_data.WEDNESDAY1['start'] + term_data.TIMETABLE[int(d[1])-1], cls_delta, make_rrule(term_data.WEDNESDAY1, test, id[:4]=='NX75'))
        cal.add_component(event)
      if term2:
        event = create_event(subject, classroom, term_data.WEDNESDAY2['start'] + term_data.TIMETABLE[int(d[1])-1], cls_delta, make_rrule(term_data.WEDNESDAY2, test, id[:4]=='NX75'))
        cal.add_component(event)
      continue
    if d[0] == '木':
      if term1:
        event = create_event(subject, classroom, term_data.THURSDAY1['start'] + term_data.TIMETABLE[int(d[1])-1], cls_delta, make_rrule(term_data.THURSDAY1, test, id[:4]=='NX75'))
        cal.add_component(event)
      if term2:
        event = create_event(subject, classroom, term_data.THURSDAY2['start'] + term_data.TIMETABLE[int(d[1])-1], cls_delta, make_rrule(term_data.THURSDAY2, test, id[:4]=='NX75'))
        cal.add_component(event)
      continue
    if d[0] == '金':
      if term1:
        event = create_event(subject, classroom, term_data.FRIDAY1['start'] + term_data.TIMETABLE[int(d[1])-1], cls_delta, make_rrule(term_data.FRIDAY1, test, id[:4]=='NX75'))
        cal.add_component(event)
      if term2:
        event = create_event(subject, classroom, term_data.FRIDAY2['start'] + term_data.TIMETABLE[int(d[1])-1], cls_delta, make_rrule(term_data.FRIDAY2, test, id[:4]=='NX75'))
        cal.add_component(event)
      continue

# ファイルに書き出してURLをajaxで返す
rand = random.randbytes(16).hex()
try:
  os.makedirs(f"../files/{rand}")
  f = open(f"../files/{rand}/{cal_name}.ics", 'wb')
  f.write(cal.to_ical())
  f.close()
  url = 'https://yhop.net'
  print(f'<a href="{url}/files/{rand}/{cal_name}.ics">{url}/files/{rand}/{cal_name}.ics</a>')
except FileExistsError:
  print("Error: 別のファイル名を指定してください")
