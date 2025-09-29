#!/usr/bin/python3
# -*- coding: utf-8 -*-

import cgi, cgitb
from bs4 import BeautifulSoup
import requests
import re
import json
from datetime import datetime, timedelta
import traceback

def day_sumup(table: list) -> str:
  day = ''
  day_dict = {}
  for s in table[6].split(','):
    day_s = s[0]
    period_s = s[-1]
    try:
      day_dict[day_s] = day_dict[day_s][0] + '～' + period_s # 3～4みたいに。
    except KeyError:
      day_dict[day_s] = period_s
  for k, v in day_dict.items():
    if day != '':
      day += ',' 
    day += k + v # 月3～5,火3～5になる！
  return day

# 講義idからURLに用いられる数字を帰す関数
def get_genre(id: str) -> str: 
  if id[0:2] == 'NX' or id[0:2] == 'XZ':
    return '06' # NX***** / NX******
  
  # コメントアウトは2024年度までの仕様
  # elif id[0] == 'T':
  #   if id[2] == '0':
  #     return '05' # T*0***
  #   else:
  #     return '052' + id[2] # T*****
  # elif id[0] == 'R':
  #   if len(id) > 7:
  #     return '052' + id[-1] # RT****-0x
  #   elif id[1] == 'T':
  #     if int(id[2]) <=5:
  #       return '040' + id[2] # RTx***
  #     else:
  #       return '04' # RT9001とか理学部開講科目
  #   elif id[2] == '9':
  #     return '0402'
  #   else:
  #     return '040' + id[2] # R*****
  elif id[0] == 'T':
    return '05'
  elif id[0] == 'R':
    if len(id) > 7:
      return '05' # 工学部の数学科目用
    else:
      return '04'
  # ここまで2025年度用

  elif id[0] == 'A':
    return '03'
  elif (id[0] == 'Y' or id[0] == 'P'):
    return '02'
  elif id[0] == 'F':
    return '01'
  # else:
  #   raise ValueError()

# Campus Squareに対応したはず
def get_risyu_func(id):
  try:
    output = ''
    genre = get_genre(id)
    # これね......年が変わってからシラバスが更新されるまでは動かなくなるのよね～～
    if genre == None:
      output += '一致する講義が見つかりませんでした;'
      return output
    year = datetime.now().year
    # year = 2024
    url = f'https://syllabus.risyu.saitama-u.ac.jp/syllabusHtml/{year}/{genre}/{genre}_{id}_ja_JP.html'
    # print(url)
    html = requests.get(url)
    soup = BeautifulSoup(html.content, 'html.parser')
    # print(soup.select_one('#tabs-1').select_one('table').find_all('td'))
    td = soup.select_one('#tabs-1').select_one('table').find_all('td')
    # print(td)
    # table = [bs.string.replace('\u3000','') for bs in td ] # tdタグを除き、空白文字を削除
    table = []
    for bs in td:
      try:
        table.append(bs.string.replace('\u3000',''))
      except AttributeError:
        table.append('')

    ''' -> 
    ['微分積分学基礎Ⅰ／Basic Calculus I',
    'RT1011',
    '  SE1100',
    '理学部数学科／Faculty of Science Department of Mathematics ',
    '2024年度／Academic Year第1／1st',
    '第1・2／1st & 2nd',
    '水／Wed4',
    '2.0',
    '1,2,3,4',
    '江頭信二／Egashira Shinji',
    '理-1番講義室／Faculty of Science, Lecture Room 1',
    'No']'''
    # print(table)

    subject = table[0].split('／')[0]
    term = table[5].split('／')[0] + 'ターム'
    term_numbers = re.findall(r'\d+', table[5].split('／')[1])
    # 文字列のリストを数値のリストに変換
    term_for_json = [int(num) for num in term_numbers]
    day = day_sumup(table)
    teacher = table[9].split('／')[0]
    classroom = table[10].split('／')[0] #if table[11] == 'No' else '遠隔授業'
    cls = {'timestamp': datetime.now().isoformat(), 'term': term_for_json, 'day': day, 'subject': subject, 'teacher': teacher, 'classroom': classroom}
    cls_dict[id] = cls
    print(type(str(term)))
    output += ' '.join([str(term), day, subject, teacher, classroom])
    output += ';' # 終了マーク
  except AttributeError or TypeError as e:
    # print(e)
    print(url)
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
      term = ','.join(map(str, cls['term'])) + 'ターム'
      day = cls['day']
      subject = cls['subject']
      short_teacher = cls['teacher']
      classroom = cls['classroom']
      output += '/'.join([term, day, subject, short_teacher, classroom])
      output += ';' # 終了マーク
    else:
      output += get_risyu_func(id)
  except KeyError or ValueError:
    output += get_risyu_func(id)

with open('../files/cls_info.json') as f:
  json_dict = json.load(f)
json_dict.update(cls_dict)
with open('../files/cls_info.json', mode='wt') as f:
  json.dump(json_dict, f, indent=2, ensure_ascii=False)
print(output)

# receive = data + "OK"
# print(receive)