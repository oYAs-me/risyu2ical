#!/usr/bin/python3
# -*- coding: utf-8 -*-

import cgi, cgitb
from bs4 import BeautifulSoup
import requests
import re
import json
from datetime import datetime, timedelta

def get_risyu_func(id):
  output = ''
  url = 'https://risyu.saitama-u.ac.jp/Portal/Public/Syllabus/DetailMain.aspx?lct_year=2024&lct_cd=' + id
  try: 
    html = requests.get(url)
    soup = BeautifulSoup(html.text, 'html.parser')
    term = soup.select_one('#ctl00_phContents_sylSummary_txtTerm_lbl').get_text()
    subject = soup.select_one('#ctl00_phContents_sylSummary_txtSbjName_lbl').get_text()
    teacher_raw = soup.select_one('#ctl00_phContents_sylSummary_txtStaffNameLinkDouble_lbl').get_text()
    teacher = ''.join(re.findall(r'[^a-zA-Z0-9[,\]　]', teacher_raw))
    split_teacher = teacher.split(' ')
    try:
      check = split_teacher[1]
      short_teacher = split_teacher[0] + '他'
    except IndexError:
      short_teacher = split_teacher[0]
    ## ↑で，複数人の場合は一人だけ抽出するようにしたい（eg. 前田公憲 他）
    day = soup.select_one('#ctl00_phContents_sylSummary_txtDayPeriod_lbl').get_text()
    classroom = soup.select_one('#ctl00_phContents_sylSummary_txtClassroomName_lbl').get_text()
    cls = {'timestamp': datetime.now().isoformat(), 'term': term, 'day': day, 'subject': subject, 'teacher': short_teacher, 'classroom': classroom}
    cls_dict[id] = cls
    output += ' '.join([term, day, subject, short_teacher, classroom])
    output += ';' # 終了マーク
  except AttributeError:
    output += '一致する講義が見つかりませんでした;'
  return output

cgitb.enable()
storage = cgi.FieldStorage()
print("Content-type: text/html\n")

# output = {}
output = ''
data = storage.getvalue("sent") # sent: json形式
data = eval(data)
cls_dict = {}

for id in data:
  if id == '': # 空白行の処理を最初に
    output += ';' # 終了マーク
    continue
  with open('../files/cls_info.json') as f:
    json_dict = json.load(f)
  try:
    cls = json_dict[id]
    delta = datetime.now() - datetime.fromisoformat(cls['timestamp'])
    if delta < timedelta(days=1):
      term = cls['term']
      day = cls['day']
      subject = cls['subject']
      short_teacher = cls['teacher']
      classroom = cls['classroom']
      output += '/'.join([term, day, subject, short_teacher, classroom])
      output += ';' # 終了マーク
    else:
      output += get_risyu_func(id)
  except KeyError:
    output += get_risyu_func(id)

with open('../files/cls_info.json') as f:
  json_dict = json.load(f)
json_dict.update(cls_dict)
with open('../files/cls_info.json', mode='wt') as f:
  json.dump(json_dict, f, indent=2, ensure_ascii=False)
print(output)

# receive = data + "OK"
# print(receive)