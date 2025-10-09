#!/usr/bin/python3
# -*- coding: utf-8 -*-

import cgi, cgitb
import json
from datetime import datetime, timedelta
from icalendar import Calendar, Event, vRecur
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

# 曜日とタームから適切なterm_dataの辞書を返す関数
def convert_day2byday(cls_info):
  day_list = cls_info['day']
  [term1, term2] = cls_info['term']
  term_data_dict = {'月': [term_data.MONDAY1, term_data.MONDAY2], '火': [term_data.TUESDAY1, term_data.TUESDAY2], '水': [term_data.WEDNESDAY1, term_data.WEDNESDAY2], '木': [term_data.THURSDAY1, term_data.THURSDAY2], '金': [term_data.FRIDAY1, term_data.FRIDAY2]} # 曜日とタームの対応辞書
  term_data_list = []
  for d in day_list: # 曜日ごとにterm_dataをリストに追加
    if d in term_data_dict.keys():
      if term1:
        term_data_list.append(term_data_dict[d][0])
      if term2:
        term_data_list.append(term_data_dict[d][1])
  return term_data_list

BYDAY_ORDER = ['MO', 'TU', 'WE', 'TH', 'FR', 'SA', 'SU'] # 曜日の順番を定義

# term_data_listを受け取って，start, exdate, COUNTをまとめる関数
def summarize_term_data(term_data_list, cls_info):
  dtstart = min([td['start'] for td in term_data_list]) # startの最小値
  byday = set([td['BYDAY'] for td in term_data_list]) # BYDAYをまとめる
  byday = sorted(set(byday), key=BYDAY_ORDER.index) # 曜日の順番を整える
  byday_set = ','.join(byday) # BYDAYをstrに変換してまとめる
  exdate = []
  for td in term_data_list:
    exdate += td['exdate'] # td['exdate']はリストなのでそのまま足し合わせる
  exdate_str = ','.join([str(dd.astimezone(tz.gettz("Asia/Tokyo"))) for dd in exdate]) # exdateをstrに変換してまとめる
  count = term_data.COUNT * len(term_data_list) # COUNTは曜日とタームの数倍にする
  # testとnx75の情報をもとにCOUNTを調整
  if cls_info['id'][:4] == 'NX75': # スポーツ実技のときは，初回の講義が行われない
    count -= 1
    exdate_str += ',' + str(cls_info['dtstart'].astimezone(tz.gettz("Asia/Tokyo"))) # 初回の講義を繰り返しから除外する
  elif not(cls_info['test']): # 期末テストがないときは，16回目の講義がなくなる
    count -= 1
  rrule_info = {'dtstart': dtstart, 'byday': byday_set, 'exdate': exdate_str, 'COUNT': str(count)}
  return rrule_info


# RRULEを作成
def make_rrule(cls_info):
  term_data_list = convert_day2byday(cls_info) # cls_infoからterm_dataのリストを作成
  rrule_info = summarize_term_data(term_data_list, cls_info) # term_data_listからrruleを作成
  rrule = {'FREQ': term_data.FREQ} # 繰り返しの頻度
  rrule['COUNT'] = rrule_info['COUNT']
  if rrule_info['byday'] != '': # bydayが空でなければ追加
    rrule['BYDAY'] = rrule_info['byday']
  if rrule_info['exdate'] != '': # exdateが空でなければ追加
    rrule['EXDATE'] = rrule_info['exdate']
  rrule['dtstart'] = rrule_info['dtstart']
  return rrule

def create_event(cls_info, rrule):
  event = Event()
  event.add('summary', cls_info['subject'])
  description = f"{cls_info['subject']} ({cls_info['teacher']})"
  event.add('description', description)
  event.add('location', cls_info['classroom'])
  dtstart = rrule['dtstart'] + cls_info['dtstart'] # cls_infoの時刻とterm_dataの開始日を合わせる
  event.add('dtstart', dtstart.astimezone(tz.gettz("Asia/Tokyo")))
  dtend = dtstart + cls_info['cls_delta']
  event.add('dtend', dtend.astimezone(tz.gettz("Asia/Tokyo")))
  event.add('rrule', vRecur(rrule))
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
  cls_info = {'term': [term1, term2], 'subject': '', 'teacher': '', 'classroom': '', 'day': [], 'dtstart': '', 'cls_delta': timedelta(), 'id': id, 'test': test}
  try:
    day = json_dict_id['day']
    cls_info['subject'] = json_dict_id['subject']
    cls_info['teacher'] = json_dict_id['teacher']
    cls_info['classroom'] = json_dict_id['classroom']
  except IndexError:
    continue
  day = day.split(',')
  for d in day: # 開始時刻を入れたdateリストを作成
    try: # 「火3～5」の講義時間の処理
      cls_delta = (int(d[3]) - int(d[1]) + 1) * timedelta(hours=1, minutes=40) - timedelta(minutes=10)
    except IndexError: # 4文字未満は1コマ分とみなす
      cls_delta = term_data.PERIOD
    cls_info['day'].append(d[0]) # 曜日
    # 以下は強制上書きしているが問題ないとみなす
    cls_info['dtstart'] = term_data.TIMETABLE[int(d[1])-1] # 始まりのコマの時刻に変更
    cls_info['cls_delta'] = cls_delta # 授業時間

  # 1講義ずつeventを作成
  rrule = make_rrule(cls_info)
  event = create_event(cls_info, rrule)
  cal.add_component(event)

# ファイルに書き出してURLをajaxで返す
rand = random.randbytes(16).hex()
try:
  # デバッグ用にcalをprint
  print(cal)
  os.makedirs(f"../files/{rand}")
  f = open(f"../files/{rand}/{cal_name}.ics", 'wb')
  f.write(cal.to_ical())
  f.close()
  print(f'<a href="./files/{rand}/{cal_name}.ics">{rand}/{cal_name}.ics</a>')
except FileExistsError:
  print("Error: 別のファイル名を指定してください")
