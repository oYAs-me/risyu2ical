#!/usr/bin/python3
# -*- coding: utf-8 -*-

import cgi, cgitb
import json
from datetime import datetime, timedelta
from icalendar import Calendar, Event, vText
from dateutil import tz
import random
import os
from library import term_data_24_2 as term_data

# ↓は情報をreturnするやつ
# cgitb.enable()
storage = cgi.FieldStorage()
print("Content-type: text/html\n")

# ical形式の変数を用意
cal_name = storage.getvalue("name")
cal = Calendar()
cal.add('prodid', f"-//yHOP//Python//{cal_name}//ja")
cal.add('version', '2.0')
cal.add('calscale', 'GREGORIAN')
cal.add('method', 'REQUEST')

# detaの受信
data = storage.getvalue("sent") # sent: json形式
data = json.loads(data)

# 
ids = data.keys()
for i in ids:
  content = data[i]
  term1 = content[0] # boolian
  term2 = content[1] # boolian
  test = content[2] # boolian
  info = content[3].split('/')
  try:
    if info[0] == '後期':
      day = info[1]
      subject = info[2]
      teacher = info[3]
      classroom = info[4:]
    else:
      continue
  except IndexError:
    continue
  if len(day) == 5: # 「火2,木2」の処理
    day = [day[0:2], day[3:5]]
  elif len(day) == 7: # 「月3～5,火3～5」の処理
    day = [day[0:3], day[4:7]]
  else:
    day = [day]
  date = []
  for d in day: # 開始時刻を入れたdateリストを作成
    da = []
    try: # 「火3～5」の講義時間の処理
      cls_delta = (int(d[3]) - int(d[1]) + 1) * timedelta(hours=1, minutes=40) - timedelta(minutes=10)
    except IndexError:
      cls_delta = term_data.PERIOD

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

  # idによる調整
  if i[:4] == 'NX75': # スポーツ実技の最初の講義を削除
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
