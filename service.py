# -*- coding: UTF-8 -*-
import datetime, os, time, json, numpy
import utils
import urllib2
from optparse import OptionParser
import extract_tags
import draw_graphic

KEYWORD_STUCK = '卡'
KEYWORD_CRASH = '闪退'
KEYWORD_DANMU = '弹幕'
NEW_VERSION = 3.630
keyword_label_array = [draw_graphic.STUCK_NAME,
                       draw_graphic.DANMU_NAME,
                       draw_graphic.CRASH_NAME,
                       draw_graphic.REST_NAME,
                       draw_graphic.TOTAL_NAME,
                       draw_graphic.TIME_NAME]


# 获取所有评论信息
def get_info():
    page = 1
    max_page = 100
    f = open(utils.get_file_path(date=utils.current_date()), 'w')
    dic = utils.get_output_total_info_dic()
    while page <= max_page:
        print str(page)
        url = "http://yuqing.dz11.com/Home/Nav/getUserFeedbackList?channel=ios&startTime=" + start_time + "%2000%3A00%3A00&endTime=" + end_time + "%2023%3A59%3A59&pageNum=" \
              + str(page) + "&pageSize=20"
        print "当前请求URL: " + url
        try:
            request = urllib2.Request(url)
            response = urllib2.urlopen(request)
            result = json.loads(response.read().decode('utf-8'))
            max_page = int(result['data']['total']) / 20 + 1
            page += 1
            for record in result['data']['records']:
                utils.handle_total_info_data(dic, record)
                f.write(record['title'].encode('utf-8') + ' ')
                f.write(record['content'].encode('utf-8') + '\n')
        except urllib2.URLError, e:
            if hasattr(e, "code"):
                print e.code
            if hasattr(e, "reason"):
                print e.reason
    utils.output_total_info(dic)
    f.close()


# 获取关键词条目数
def get_key_words_count(key_words):
    url = "http://yuqing.dz11.com/Home/Nav/getUserFeedbackList?channel=ios&keywords=" + key_words + "&startTime=" + start_time + "%2000%3A00%3A00&endTime=" + end_time + "%2023%3A59%3A59&pageNum=1&pageSize=20"
    print "当前请求URL: " + url
    try:
        request = urllib2.Request(url)
        response = urllib2.urlopen(request)
        result = json.loads(response.read().decode('utf-8'))
        max_page = result['data']['total']
        print key_words + ': ' + utils.convert_to_utf8(max_page)
        return utils.convert_to_utf8(max_page)
    except urllib2.URLError, e:
        if hasattr(e, "code"):
            print e.code
        if hasattr(e, "reason"):
            print e.reason


# 获取关键词对应的内容
def get_key_words_content(key_words):
    page = 1
    max_page = 100
    max_length_content = ''
    title = ''
    device = ''
    version = ''
    max_length_id = ''

    while page <= max_page:
        url = "http://yuqing.dz11.com/Home/Nav/getUserFeedbackList?channel=ios&keywords=" + key_words + "&startTime=" + start_time + "%2000%3A00%3A00&endTime=" + end_time + "%2023%3A59%3A59&pageNum=1&pageSize=20"
        result = send_request(url)
        max_page = int(result['data']['total']) / 20 + 1
        page += 1
        for record in result['data']['records']:
            content = utils.convert_to_utf8(record['content'])
            id = utils.convert_to_utf8(record['id'])
            if len(content) > len(max_length_content) and id not in problemIDs:
                max_length_content = content
                title = utils.convert_to_utf8(record['title'])
                device = utils.convert_to_utf8(record['ua'])
                version = utils.convert_to_utf8(record['version'])
                max_length_id = id

    problemIDs.append(max_length_id)
    print title, max_length_content, device, version
    return title, max_length_content, device, version


def send_request(url):
    print "当前请求URL: " + url
    try:
        request = urllib2.Request(url)
        request.add_header('User-Agent',
                           'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.167 Safari/537.36')
        response = urllib2.urlopen(request)
        result = json.loads(response.read().decode('utf-8'))
        return result
    except urllib2.URLError, e:
        if hasattr(e, "code"):
            print e.code
        if hasattr(e, "reason"):
            print e.reason


# 批量获取所有关键词的内容
def get_all_key_word_content(keyword_count, additon_key_word=''):
    global problemIDs
    problemIDs = []
    # 使用结巴分词得到关键词
    tags = extract_tags.get_topK_words(utils.get_file_path(date=utils.current_date()), keyword_count)

    titles = []
    contents = []
    device = []
    version = []
    # 循环获取关键词内容
    if len(additon_key_word) > 0:
        tags.insert(0, additon_key_word)

    keywords = ",".join(tags).encode('utf-8')
    for tag in tags:
        title, content, dev, ver = get_key_words_content(utils.convert_to_utf8(tag))
        if content is None or len(content) == 0:
            continue
        titles.append(title)
        contents.append(content)
        device.append(dev)
        version.append(ver)

    label_array = [utils.TITLE_NAME, utils.CONTENT_NAME, utils.DEVICE_NAME, utils.VERSION_NAME]
    key_word_table = utils.output_keyword_table(
        {label_array[0]: titles, label_array[1]: contents, label_array[2]: device, label_array[3]: version},
        label_array)
    return key_word_table, keywords


# 获取查询时的开始时间和结束时间
def get_start_time(date=None):
    if date is None:
        date = datetime.date.today().strftime("%Y-%m-%d")
    else:
        date = date.strftime("%Y-%m-%d")
    global start_time
    global end_time
    # 计算开始时间和结束时间
    start_time = date
    end_time = date
    if start_time > end_time:
        print "开始时间不能大于结束时间！"
        return


# 所有问题的excel表格文件名
def totoal_info_excel_file_name():
    tail = '.xlsx'
    date = utils.current_date()
    return utils.get_file_path(tail, date), utils.get_file_prefix_name(tail, date)


# 输出指定日期内的舆情关键词统计数据
def out_put_all_statistic(begin, end):
    array = [[], [], [], [], [], []]
    for i in range((end - begin).days + 1):
        day = begin + datetime.timedelta(days=i)
        get_start_time(day)
        stuck = int(get_key_words_count(KEYWORD_STUCK))
        danmu = int(get_key_words_count(KEYWORD_DANMU))
        crash = int(get_key_words_count(KEYWORD_CRASH))
        total = int(get_key_words_count(''))
        rest = total - stuck - danmu - crash
        array[0].append(stuck)
        array[1].append(danmu)
        array[2].append(crash)
        array[3].append(rest)
        array[4].append(total)
        array[5].append(day.strftime('%m-%d'))

    draw_graphic.out_put_graphic(dict(zip(keyword_label_array, array)), keyword_label_array)


# 输出指定日期的舆情关键词统计数据
def out_put_today_statistic(today):
    stuck = int(get_key_words_count(KEYWORD_STUCK))
    danmu = int(get_key_words_count(KEYWORD_DANMU))
    crash = int(get_key_words_count(KEYWORD_CRASH))
    total = int(get_key_words_count(''))
    time = today.strftime('%m-%d')
    rest = total - stuck - danmu - crash

    draw_graphic.out_put_graphic(dict(zip(keyword_label_array, [[stuck], [danmu], [crash], [rest], [total], [time]])),
                                 keyword_label_array)
    return stuck, danmu, crash, total


# 开始统计工作
def make_statistic(topK, is_test=False):
    # 获得开始时间参数
    get_start_time(utils.current_date())
    # 获取全部信息，保存为xlsx表格用于附件发送，保存标题和内容信息用于提取关键词
    get_info()
    # 输出卡顿等特征值表格和图表，返回卡顿等数目
    stuck, danmu, crash, total = out_put_today_statistic(utils.current_date())
    # 添加额外关键词
    additon_keyword = ''
    # 如果有闪退的反馈，增加闪退关键词
    if crash > 0:
        additon_keyword = u'闪退'
    # 获取所有关键词的推荐内容
    key_word_table, key_words = get_all_key_word_content(topK, additon_keyword)
    # 获取最新版本的问题反馈
    new_version_html = utils.output_new_version_table(NEW_VERSION)
    # 邮件主题
    sub = 'iOS组-舆情平台日报'
    # 邮件的内容html文件
    html = utils.make_email_html(sub + utils.current_date().strftime(" %Y.%m.%d"), key_words, key_word_table,
                                 str(total),
                                 str(crash), str(stuck), str(danmu), new_version_table=new_version_html)
    # 生成明日的额外概要内容文件
    utils.create_next_day_additions_file()
    return sub, html


if __name__ == '__main__':
    get_start_time(utils.current_date())
    get_all_key_word_content(8)
