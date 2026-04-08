import cgi, cgitb
import json, os, random, re

from collections import defaultdict

from bs4 import BeautifulSoup
import requests

from datetime import datetime, timedelta
from icalendar import Calendar, Event, vText
from dateutil import tz

from library import term_data_2026 as term_data

def read_RSReferCsv(file_path):
    """CampusSquareからダウンロードしたRSReferCsvファイルを読み込む関数。講義名、年度、学期、履修情報を返す。"""
    with open(file_path, 'r', encoding='cp932') as f:
        lines = f.readlines()
        name, year, semester = None, None, None
        risyu: list[list[str]] = []

        for i, line in enumerate(lines):
            if i == 0:
                name = line.strip().split(',')[1]
                continue
            if i == 2:
                # "2026年度・第1"という文字列から、年度と学期を抽出
                match = re.match(r'\"(\d{4})年度・第(\d)\"', line.strip().split(',')[1])
                if match:
                    year = int(match.group(1))
                    semester = int(match.group(2))
                else:
                    print(line)
                    raise ValueError("ファイルの形式が正しくありません。")
                continue
            if i <= 7:
                continue
            if (i - 8) % 5 == 0:
                ids = [s if s != '未登録' else '' for s in line.strip().split(',')[1:]] # ここで未登録を空文字列に変換
                risyu.append(ids)
    
    return name, year, semester, risyu

def get_genre(id: str): 
    """講義idからURLに用いられる数字を返す関数"""
    if id[0:2] == 'NX' or id[0:2] == 'XZ':
        return '06' # NX***** / NX******
    if id[0] == 'T':
        return '05'
    if id[0] == 'R':
        if len(id) > 7:
            return '05' # 工学部の数学科目用
        else:
            return '04'
    # ここまで2025年度用

    if id[0] == 'A':
        return '03'
    if (id[0] == 'Y' or id[0] == 'P'):
        return '02'
    if id[0] == 'F':
        return '01'
    if id[0:2] == 'G':
        return '27' # 人文社会科学研究科博士後期
    if id[0] == 'D':
        return '25' # 理工学研究科博士後期
    if id[0:2] == 'MM':
        return '24' # 理工学研究科博士前期
    if id[0:3] == 'BMD':
        return '19' # 人文社会科学研究科修士
    if id[0] == 'W':
        return '18' # 教育学研究科専門職
    if id[0:2] == 'B':
        return '17' # 人文社会科学研究科博士前期
    else:
        print(id)
        raise ValueError("genreを特定できませんでした。")

def get_cls_info_from_syllabus(cls_id, year) -> dict[str, str | list[str]]:
    try:
        genre = get_genre(cls_id)
    except ValueError as e:
        print(f"Error occurred while getting genre for {cls_id}: {e}")
        raise
    url = f'https://syllabus.risyu.saitama-u.ac.jp/syllabusHtml/{year}/{genre}/{genre}_{year}_ja_JP.html'
    html = requests.get(url)
    soup = BeautifulSoup(html.content, 'html.parser')
    try:
        td = soup.select_one('#tabs-1').select_one('table').find_all('td')
    except AttributeError:
        raise ValueError("講義情報が見つかりませんでした。")
    table = []
    for bs in td:
      try:
        table.append(bs.string.replace('\u3000',''))
      except AttributeError:
        table.append('')
    """
    eg.
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
    'No']
    """
    subject = str(table[0].split('／')[0])
    term_numbers = re.findall(r'\d+', table[5].split('／')[1])
    term_for_json = [str(num) for num in term_numbers]
    teacher = str(table[9].split('／')[0])
    classroom = str(table[10].split('／')[0]) if table[11] == 'No' else 'オンデマンド'

    cls: defaultdict[str, str | list[str]] = defaultdict(lambda: '')
    cls['timestamp'] = datetime.now().isoformat()
    cls['term'] = term_for_json
    cls['subject'] = subject
    cls['teacher'] = teacher
    cls['classroom'] = classroom
    return cls

def get_cls_info(cls_ids: list[str], year: int) -> dict[str, dict[str, str | list[str]]]:
    """cls_idsに対応する講義情報を辞書形式で返す関数。キャッシュがあればそれを使い、なければシラバスから情報を取得する。"""
    # cls_info.jsonの存在確認
    if not os.path.exists('../files/cls_info.json'):
        with open('../files/cls_info.json', 'w') as f:
            json.dump({}, f) # 空の辞書を保存してファイルを作成
    with open('../files/cls_info.json') as f:
        json_dict = defaultdict(lambda: None, json.load(f)) # 存在しないキーにアクセスしたときにNoneを返すようにする
    # cls_idに対応する情報をjson_dictから取得し、1日以内の情報であれば返す
    cls_info = {}
    for cls_id in cls_ids:
        if cls_id == '' or cls_id == '未登録':
            continue
        info = json_dict[cls_id]
        if info is not None and datetime.fromisoformat(info['timestamp']) > datetime.now() - timedelta(days=1):
            cls_info[cls_id] = info
        else:
            try:
                cls_info[cls_id] = get_cls_info_from_syllabus(cls_id, year)
            except ValueError:
                print(f"{cls_id}の情報が見つかりませんでした。")
                cls_info[cls_id] = None # 講義情報が見つからなかった場合はNoneを入れる
    return cls_info

def make_ical_init(cal_name: str) -> Calendar:
    """icalendarのCalendarオブジェクトを初期化する関数。"""
    cal = Calendar()
    cal.add('prodid', f"-//yhop.net//risyu2ical-v2//ja")
    cal.add('version', '2.0')
    cal.add('calscale', 'GREGORIAN')
    cal.add('method', 'REQUEST')
    return cal

def update_ical(cls_info: dict[str, dict[str, str | list[str]]], dates: list[list[tuple[int, int]]], cal: Calendar) -> Calendar:
    """cls_infoとdatesをもとにicalendarのCalendarオブジェクトを更新する関数。"""
    for term, date_list in enumerate(dates):
        # その場合は同一曜日であれば結合して1つのイベントにする
        date_dict: defaultdict[int, list[int]] = defaultdict(list) # 曜日をキー、時限のリストを値とする辞書
        for day, period in date_list:
            date_dict[day].append(period)
        
        # すべての曜日で同じ時限に授業がある場合は、曜日を結合してよいというフラグを立てる
        if all(periods == date_dict[0] for periods in date_dict.values()):
            BYDAY = ','.join(term_data.DATES_DATA[term][day]['BYDAY'] for day in date_dict.keys()) # MO,TUのような文字列
            flag = True
        else:
            flag = False

        for day, periods in date_dict.items(): # term, dayは0-indexed、periodは1-indexed
            periods.sort() # 時限を昇順にソート
            start_time = term_data.TIMETABLE[periods[0]] # 最初の時限の開始時刻
            end_time = term_data.TIMETABLE[periods[-1]] + term_data.PERIOD # 最後の時限の終了時刻
            event = Event()

            event.add('dtstart', start_time)
            event.add('dtend', end_time)
            event.add('summary', vText(str(cls_info['subject'])))
            event.add('location', vText(str(cls_info['classroom'])))
            event.add('description', vText(f"担当教員: {cls_info['teacher']}"))

            # 曜日指定で繰り返しルールを設定
            event.add('rrule', {'freq': 'weekly', 'byday': term_data.DATES_DATA[term][day]['BYDAY'], 'count': term_data.CLS_PER_TERM})

            # 休講日を除外
            for exdate in term_data.DATES_DATA[term][day]['exdate']:
                event.add('exdate', exdate)
            
            cal.add_component(event)
            if flag:
                break # 曜日を結合している場合は最初の曜日のイベントを作成して終了
    return cal



def main(name, file_path='RSReferCsv.csv'):
    # CGI処理

    # 講義情報の取得
    cls_info = {}
    loop_length = 1
    risyu_tables = []
    for i in range(loop_length):
        name, year, semester, risyu_table_cls_id = read_RSReferCsv(file_path)
        risyu_tables.append(risyu_table_cls_id)
        if name is None or year is None or semester is None:
            # print("Content-type: text/html\n")
            print("RSReferCsvファイルの形式が正しくありません。")
            return
        cls_ids = list(set(str(id) for row in risyu_table_cls_id for id in row if id)) # 空文字列を除く
        cls_info |= get_cls_info(cls_ids, year)

    # icalendarの作成
    cal = make_ical_init(name)

    for cls_id, info in cls_info.items():
        subject = info['subject'] if info is not None else '情報なし'
        teacher = info['teacher'] if info is not None else '情報なし'
        classroom = info['classroom'] if info is not None else '情報なし'
        print(f"{cls_id}: {subject}, {teacher}, {classroom}")

        dates: list[list[tuple[int, int]]] = [[], [], [], []] # タームごとに分けて保存するためのリスト
        # どの曜日・どの時限に存在するか
        for i, table in enumerate(risyu_tables):
            for j, row in enumerate(table):
                for k, id in enumerate(row):
                    if cls_id == id:
                        dates[i].append((j, k+1)) # タームごとに曜日(0-indexed)、時限(1-indexed)の順で保存
        
        cal = update_ical(info, dates, cal)

if __name__ == "__main__":
    # pwdを見たい
    print(os.getcwd())
    # pwdを変更
    os.chdir('./cgi-bin')
    main("テストカレンダー", '../RSReferCsv.csv')