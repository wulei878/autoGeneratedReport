# -*- coding: UTF-8 -*-
from optparse import OptionParser

import pandas as pd
import os, datetime

INDEX_NAME = u'序号'
TITLE_NAME = u'标题'
CONTENT_NAME = u'内容'
DEVICE_NAME = u'设备'
VERSION_NAME = u'版本'
IP_NAME = u'IP'
UID_NAME = u'UID'
TIME_NAME = u'时间'
STATUS_NAME = u'状态'
PROBLEMS_FOLLOW_UP_FILE = 'Resources/problems_follow_up.xlsx'

pd.set_option('display.max_colwidth', 0)


# 输出邮件的html
def make_email_html(sub, keywords, key_word_table, total_count, crash_count, stuck_count, danmu_count,
                    new_version_table):
    if int(crash_count) > 0:
        crash_label = """<label class="redColor">""" + crash_count + """</label>"""
    else:
        crash_label = """""" + crash_count + """"""
    if int(stuck_count) > 0:
        stuck_label = """<label class="redColor">""" + stuck_count + """</label>"""
    else:
        stuck_label = """""" + stuck_count + """"""
    if int(danmu_count) > 0:
        danmu_label = """<label class="redColor">""" + danmu_count + """</label>"""
    else:
        danmu_label = """""" + danmu_count + """"""

    # 额外内容从文件中读取
    additions = get_additions()
    additions_label = """"""
    for line in additions:
        if len(line) > 0:
            additions_label = additions_label + """<li>""" + line + """</li>"""

    basic_info = """<p><strong>""" + sub + """</strong></p>
    <i>本邮件由iOS舆情自动化平台发送</i>
    <p><strong>概况</strong></p>
        <ol>
          <li>今日关键词:""" + keywords + """</li>
          <li>平台反馈的iOS相关问题""" + total_count + """例，其中闪退""" + crash_label + """例，
          直播间卡顿""" + stuck_label + """例，弹幕问题""" + danmu_label + """例。</li>
          """ + additions_label + """
        </ol>"""

    image_info = """<p><strong>问题图表:</strong></p>
        <p>整体问题趋势图:</p>
        <p><img src="cid:image0"></p>
        <p>闪退、直播间卡顿、弹幕问题趋势图:</p>
        <p><img src="cid:image1">
        <p>闪退、直播间卡顿、弹幕问题百分比图:</p>
        <p><img src="cid:image2">
        """

    css_style = """<style type="text/css">
        .table {
            font-family: verdana,arial,sans-serif;
            font-size:14px;
            color:#333333;
            border-width: 1px;
            border-color: #a9c6c9;
            border-collapse: collapse;
            width:1000px;
        }
        .table tr{
            text-align: center !important;
        }
        .table th {
            border-width: 1px;
            padding: 8px;
            border-style: solid;
            border-color: #a9c6c9;
        }
        .table td {
            border-width: 1px;
            padding: 8px;
            border-style: solid;
            border-color: #a9c6c9;
        }
        .redColor{
            color:red;
        }
        </style>"""

    html = """\
    <html xmlns="http://www.w3.org/1999/xhtml">
    <head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <title>""" + sub + """</title>
    """ + css_style + """
    </head>
    <body>
    <div id="container">
    """ + basic_info + """
      <div id="content">
      <p><strong>新版本问题反馈</strong></p>
      """ + new_version_table + """
        <p><strong>主要问题详情</strong></p>
      """ + key_word_table + """
        <p><strong>反馈问题追踪</strong></p>
      """ + output_problems_follow_up_table() + """
        """ + image_info + """
      </div>
    </div>
    </div>
    </body>
    </html>
            """
    return html


# 输出全部舆情信息到excel表格
def output_total_info(dic):
    df = pd.DataFrame(dic, columns=[TITLE_NAME, CONTENT_NAME, IP_NAME, UID_NAME, DEVICE_NAME, VERSION_NAME, TIME_NAME],
                      index=dic[INDEX_NAME])
    df.to_excel(get_file_path(tail='.xlsx', date=current_date()))


# 处理所有的信息
def handle_total_info_data(dic, data):
    dic[INDEX_NAME].append(convert_to_utf8(data['id']))
    dic[TITLE_NAME].append(convert_to_utf8(data['title']))
    dic[CONTENT_NAME].append(convert_to_utf8(data['content']))
    dic[DEVICE_NAME].append(convert_to_utf8(data['ua']))
    dic[VERSION_NAME].append(convert_to_utf8(data['version']))
    dic[UID_NAME].append(convert_to_utf8(data['uid']))
    dic[IP_NAME].append(convert_to_utf8(data['ip']))
    dic[TIME_NAME].append(convert_to_utf8(data['time']))


# 生成所有信息的字典
def get_output_total_info_dic():
    return {INDEX_NAME: [], TITLE_NAME: [], CONTENT_NAME: [], DEVICE_NAME: [], VERSION_NAME: [], UID_NAME: [],
            IP_NAME: [],
            TIME_NAME: []}


# 输出新版本的问题列表
def output_new_version_table(version):
    df = pd.read_excel(get_file_path(tail='.xlsx', date=current_date()))
    temp_df = df[df[VERSION_NAME] == version]
    temp_df = temp_df.loc[:, [TITLE_NAME, CONTENT_NAME, DEVICE_NAME, VERSION_NAME]]
    length_array = []
    for ix, row in temp_df.iterrows():
        length_array.append(len(row[CONTENT_NAME]))

    temp_df.insert(4, 'length', length_array)
    temp_df = temp_df.nlargest(10, 'length')
    temp_df = temp_df.loc[:, TITLE_NAME:VERSION_NAME]
    html = temp_df.to_html(classes='table')
    temp_df.to_excel(get_file_path(tail='_' + convert_to_utf8(str(version)) + '.xlsx', date=current_date()))
    return convert_to_utf8(html), temp_df.index.values


# 输出关键字问题的列表
def output_keyword_table(dic, columns, index):
    df = pd.DataFrame(dic, columns=columns, index=index)
    df = df.loc[:, TITLE_NAME:VERSION_NAME]
    html = df.to_html(classes='table')
    df.to_excel(get_file_path(tail='_keywords' + '.xlsx', date=current_date()))
    return convert_to_utf8(html)


# 输出问题追踪的列表
def output_problems_follow_up_table(file_path=PROBLEMS_FOLLOW_UP_FILE):
    df = pd.read_excel(file_path)
    html = df.to_html(classes='table')
    return convert_to_utf8(html)


# 转换utf-8字符的通用方法
def convert_to_utf8(string):
    return string.encode('utf-8')


# 获取指定日期的文件夹路径
def get_file_path(tail='.txt', date=datetime.datetime.today()):
    year = date.strftime('%Y')
    month = date.strftime('%m')
    day = date.strftime('%d')
    if not os.path.exists(year):
        os.mkdir(year)
    month_path = os.path.join(year, month)
    if not os.path.exists(month_path):
        os.mkdir(month_path)
    day_path = os.path.join(month_path, day)
    if not os.path.exists(day_path):
        os.mkdir(day_path)
    file_name = get_file_prefix_name(tail, date)
    return os.path.join(day_path, file_name)


# 获取默认的文件名前缀
def get_file_prefix_name(tail='.txt', date=datetime.datetime.today()):
    return date.strftime("%Y-%m-%d_iOS_yuqing" + tail)


# 获取概要内容的额外信息，手动输入的
def get_additions():
    path = get_file_path('_additions.txt', current_date())
    if not os.path.exists(path):
        print '今日无额外的概要内容！！！'
        additions = []
        f = open(path, 'w')
        f.close()
    else:
        f = open(path, 'r')
        additions = f.readlines()
        f.close()

    return additions


# 创建明天的额外信息文档
def create_next_day_additions_file():
    path = get_file_path('_additions.txt', current_date() + datetime.timedelta(days=1))
    if not os.path.exists(path):
        f = open(path, 'w')
        f.close()


def gci(path, file_names):
    parents = os.listdir(path)
    for parent in parents:
        child = os.path.join(path, parent)
        if os.path.isdir(child):
            gci(child, file_names)
        else:
            file_names.append(child)


def add_problems_follow_up(index_id, folder_path='2018'):
    file_names = []
    gci(folder_path, file_names)
    for file_name in file_names:
        if file_name.find('_yuqing.xlsx') > 0:
            df = pd.read_excel(file_name)
            try:
                problems_df = pd.read_excel(PROBLEMS_FOLLOW_UP_FILE)
                df = df.loc[index_id]
            except:
                continue

            try:
                problems_df = problems_df.append(df[[CONTENT_NAME, VERSION_NAME]], verify_integrity=True)
                problems_df.loc[index_id, [STATUS_NAME]] = '排查中'
                problems_df.to_excel(PROBLEMS_FOLLOW_UP_FILE)
            except:
                print '相同的问题已存在！'
                break


def add_problems_follow_up_status(index_id,status):
    problems_df = pd.read_excel(PROBLEMS_FOLLOW_UP_FILE)
    problems_df.loc[index_id,[STATUS_NAME]] = status
    problems_df.to_excel(PROBLEMS_FOLLOW_UP_FILE)
    print problems_df


def current_date():
    return datetime.date.today()


def main():
    USAGE = "usage:    python utils.py -i [index] -a [status]"
    parser = OptionParser(USAGE)
    parser.add_option("-i", dest="index")
    parser.add_option("-a", dest="status")
    opt, args = parser.parse_args()
    if opt.status is not None and opt.index is not None:
        index = int(opt.index)
        status = opt.status
        add_problems_follow_up_status(index,status)
    elif opt.index is not None:
        index = int(opt.index)
        add_problems_follow_up(index)


if __name__ == '__main__':
    main()
    # output_new_version_table(3.630)
