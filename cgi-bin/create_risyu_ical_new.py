#!/usr/bin/python3
# -*- coding: utf-8 -*-

import cgi, cgitb
import json
from datetime import datetime, timedelta
from icalendar import Calendar, Event, vText
from dateutil import tz
import random
import os
from library import term_data_25_1 as term_data

# 前後期か判別するための定数
SEMESTER = [[1,2], [3,4]]
use_semester = SEMESTER[0] # この数字を変えれば学期を変えられる


def ical_init(cal_name):
  cal = Calendar()
  cal.add('prodid', f"-//yHOP//Python//{cal_name}//ja")
  cal.add('version', '2.0')
  cal.add('calscale', 'GREGORIAN')
  cal.add('method', 'REQUEST')
  return cal

# ↓は情報をreturnするやつ
cgitb.enable()
storage = cgi.FieldStorage()
print("Content-type: text/html\n")

cal_name = storage.getvalue("name")
# ical形式の変数を用意
cal = ical_init(cal_name)

# detaの受信
data = storage.getvalue("sent") # sent: json形式
data = json.loads(data)
test_data = storage.getvalue("test")
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
        da += term_data.MONDAY1
      if term2:
        da += term_data.MONDAY2
      delta = term_data.TIMETABLE[int(d[1])-1]
      date += [cls + delta for cls in da]
      continue
    if d[0] == '火':
      if term1:
        da += term_data.TUESDAY1
      if term2:
        da += term_data.TUESDAY2
      delta = term_data.TIMETABLE[int(d[1])-1]
      date += [cls + delta for cls in da]
      continue
    if d[0] == '水':
      if term1:
        da += term_data.WEDNESDAY1
      if term2:
        da += term_data.WEDNESDAY2
      delta = term_data.TIMETABLE[int(d[1])-1]
      date += [cls + delta for cls in da]
      continue
    if d[0] == '木':
      if term1:
        da += term_data.THURSDAY1
      if term2:
        da += term_data.THURSDAY2
      delta = term_data.TIMETABLE[int(d[1])-1]
      date += [cls + delta for cls in da]
      continue
    if d[0] == '金':
      if term1:
        da += term_data.FRIDAY1
      if term2:
        da += term_data.FRIDAY2
      delta = term_data.TIMETABLE[int(d[1])-1]
      date += [cls + delta for cls in da]
      continue

  # dateを時間順に整列
  date = sorted(date)
  # print(date)

  # idによる調整
  if id[:4] == 'NX75': # スポーツ実技の最初の講義を削除
    del date[0]
  if not(test) and (len(date) == 16): # 16回講義で期末テストがない講義の最終講義を削除
    del date[-1]

  # icalデータの作成
  summary = subject
  description = f"{subject} ({teacher})"
  location = classroom
  while date: # イベント作成
    dtstart = date.pop(0)
    event = Event()
    if (test and not(date)): # 期末テストの書き換え
      summary += ' 期末テスト'
      description += ' の期末テスト日'
    event.add('summary', summary)
    event.add('description', description)
    event.add('location', location)
    event.add('dtstart', dtstart.astimezone(tz.gettz("Asia/Tokyo")))
    dtend = dtstart + cls_delta
    event.add('dtend', dtend.astimezone(tz.gettz("Asia/Tokyo")))
    cal.add_component(event)

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
