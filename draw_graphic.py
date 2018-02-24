# -*- coding: UTF-8 -*-
import pandas as pd
import matplotlib.figure
import os
import matplotlib.pyplot as plt

STUCK_NAME = u'直播间卡顿'
DANMU_NAME = u'弹幕问题'
CRASH_NAME = u'闪退'
TOTAL_NAME = u'总计'
TIME_NAME = u'时间'
REST_NAME = u'其他'
EXCEL_FILE_NAME = 'statistic.xlsx'
LINE_IMAGE_NAME = 'statistic_line.png'
PIE_IMAGE_NAME = 'statistic_pie.png'
LINE_IMAGE_TOTAL_NAME = 'statistic_line_total.png'

plt.style.use('ggplot')
matplotlib.rcParams['font.sans-serif'] = 'Microsoft YaHei'


# 读取卡顿等问题的统计文档
def read_data(file_name):
    return pd.read_excel(file_name)


# 输出统计的excel文档
def out_put_graphic(dic, column):
    new_df = pd.DataFrame(dic, columns=column)
    if os.path.exists(EXCEL_FILE_NAME):
        df = read_data(EXCEL_FILE_NAME)
        if df.iloc[-1][TIME_NAME] == new_df.iloc[-1][TIME_NAME]:
            df = df.drop([len(df) - 1])
        df = df.append(new_df, ignore_index=True)
    else:
        df = new_df
    print df
    df.to_excel(EXCEL_FILE_NAME)
    draw_graphic(df)


# 输出相关的统计图
def draw_graphic(df=read_data(EXCEL_FILE_NAME)):
    last_data = df.iloc[-1]
    pie_data = pd.DataFrame([last_data[STUCK_NAME], last_data[DANMU_NAME], last_data[CRASH_NAME], last_data[REST_NAME]],
                            index=[STUCK_NAME, DANMU_NAME, CRASH_NAME, REST_NAME], columns=[TOTAL_NAME])
    print pie_data
    # 饼图
    pie_data.plot(kind='pie', y=TOTAL_NAME, figsize=(6, 6))
    plt.savefig(PIE_IMAGE_NAME)

    line_data = df[[STUCK_NAME, DANMU_NAME, CRASH_NAME]]
    print line_data
    # 卡顿等问题的折线图
    line_data.plot(kind='line', figsize=(10, 8))
    plt.xticks(df.index, df[TIME_NAME], rotation=90)
    plt.savefig(LINE_IMAGE_NAME)

    total_data = df[[TOTAL_NAME]]
    print total_data
    # 所有问题总数的折线图
    total_data.plot(kind='line', figsize=(10, 8))
    plt.xticks(df.index, df[TIME_NAME], rotation=90)
    plt.savefig(LINE_IMAGE_TOTAL_NAME)
    # plt.show()


# 图片的名称列表，供发邮件时使用
def image_list():
    return [LINE_IMAGE_TOTAL_NAME, LINE_IMAGE_NAME, PIE_IMAGE_NAME]


def main():
    draw_graphic()


if __name__ == '__main__':
    main()
