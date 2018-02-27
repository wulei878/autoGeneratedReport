# -*- coding: UTF-8 -*-
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
        .keywordTable, .newVersionTable {
            font-family: verdana,arial,sans-serif;
            font-size:14px;
            color:#333333;
            border-width: 1px;
            border-color: #a9c6c9;
            border-collapse: collapse;
            width:1000px;
        }
        .keywordTable tr, .newVersionTable tr{
            text-align: center !important;
        }
        .keywordTable th, .newVersionTable th {
            border-width: 1px;
            padding: 8px;
            border-style: solid;
            border-color: #a9c6c9;
        }
        .keywordTable td, .newVersionTable td {
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
    temp_df.insert(0, INDEX_NAME, range(1, len(temp_df) + 1))
    temp_df = temp_df.loc[:, INDEX_NAME:VERSION_NAME]
    html = temp_df.to_html(index=False, classes='newVersionTable')

    temp_df.set_index(INDEX_NAME)
    temp_df.to_excel(get_file_path(tail='_' + convert_to_utf8(str(version)) + '.xlsx', date=current_date()),
                     index=False)
    return convert_to_utf8(html)


# 输出关键字问题的列表
def output_keyword_table(dic, columns):
    df = pd.DataFrame(dic, columns=columns)
    df.insert(0, INDEX_NAME, range(1, len(df) + 1))
    df = df.loc[:, INDEX_NAME:VERSION_NAME]
    html = df.to_html(index=False, classes='keywordTable')
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


def current_date():
    return datetime.date.today() - datetime.tim


if __name__ == '__main__':
    output_new_version_table()
