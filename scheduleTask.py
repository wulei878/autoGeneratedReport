#! /usr/bin/env python
# -*- coding: UTF-8 -*-
import time
import sched
import smtplib
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import draw_graphic
import service
from email.mime.application import MIMEApplication
from optparse import OptionParser
import config

SECONDS_PER_DAY = 24 * 60 * 60

schedule = sched.scheduler(time.time, time.sleep)
TEST_MAIL_LIST = config.test_mail_list  # 测试邮箱地址
MAILTO_LIST = config.mailto_list  # 正式邮箱地址
MAIL_HOST = config.mail_host  # 设置服务器
MAIL_USER = config.mail_user  # 用户名
MAIL_PASS = config.mail_pass  # 口令
MAIL_POSTFIX = config.mail_postfix  # 发件箱的后缀
CC_MAIL_LIST = config.cc_mail_list  # 抄送邮箱地址


def perform_command(cmd, inc):
    # 安排inc秒后再次运行自己，即周期运行
    schedule.enter(inc, 0, perform_command, (cmd, inc))
    schedule_job()


def timming_exe(cmd, inc=60):
    # enter用来安排某事件的发生时间，从现在起第n秒开始启动
    schedule.enter(inc, 0, perform_command, (cmd, inc))
    # 持续运行，直到计划时间队列变成空为止
    schedule.run()


def send_mail_with_html(sub, html, is_test=False):
    me = "吴磊" + "<" + MAIL_USER + "@" + MAIL_POSTFIX + ">"
    msg = MIMEMultipart()
    msg['Subject'] = sub
    msg['From'] = me
    if is_test:
        to_list = TEST_MAIL_LIST
    else:
        to_list = MAILTO_LIST
        msg['Cc'] = ";".join(CC_MAIL_LIST)
    msg['To'] = ";".join(to_list)
    msg.attach(MIMEText(html, 'html', 'utf-8'))
    image_list = draw_graphic.image_list()
    for index in range(len(image_list)):
        name = image_list[index]
        fp = open(name, 'rb')
        msg_image = MIMEImage(fp.read())
        fp.close()
        msg_image.add_header('Content-ID', '<image' + str(index) + '>')
        msg.attach(msg_image)

    file_path, file_name = service.totoal_info_excel_file_name()
    excel_file_part = MIMEApplication(open(file_path, 'rb').read())
    excel_file_part.add_header('Content-Disposition', 'attachment', filename=file_name)
    msg.attach(excel_file_part)
    try:
        server = smtplib.SMTP()
        server.connect(MAIL_HOST)
        server.login(MAIL_USER + "@" + MAIL_POSTFIX, MAIL_PASS)
        server.sendmail(me, to_list, msg.as_string())
        server.close()
        return True
    except Exception as e:
        print('' + str(e))
        return False


def time_to_sleep():
    from datetime import datetime
    cur_time = datetime.now()
    des_time = cur_time.replace(hour=20, minute=0, second=0, microsecond=0)
    delta = (des_time - cur_time).total_seconds()
    if delta > 0:
        skip_seconds = delta
    else:
        skip_seconds = SECONDS_PER_DAY + delta
    hour = skip_seconds / 60 / 60
    minute = skip_seconds % 3600 / 60
    seconds = skip_seconds % 3600 % 60
    print(skip_seconds)
    print("Must sleep %d hour %d minute %d second" % (hour, minute, seconds))
    return skip_seconds


def schedule_job(cmd, inc):
    send_yuqing_mail(is_test=False)
    schedule.enter(inc, 0, schedule_job, (cmd, inc))
    schedule.run()


def send_yuqing_mail(is_test):
    sub, html = service.make_statistic(8)
    send_mail_with_html(sub, html, is_test=is_test)


def main():
    USAGE = "usage:    python scheduleTask.py -t [is test]"

    parser = OptionParser(USAGE)
    parser.add_option("-t", dest="is_test")
    opt, args = parser.parse_args()
    if opt.is_test is None:
        is_test = 1
    else:
        is_test = opt.is_test

    is_test = is_test == 1
    if is_test:
        send_yuqing_mail(is_test)
    else:
        time.sleep(time_to_sleep())
        schedule_job('', SECONDS_PER_DAY)


if __name__ == '__main__':
    main()
