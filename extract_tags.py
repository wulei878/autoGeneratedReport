# -*- coding: UTF-8 -*-
import sys
import jieba
import jieba.analyse
from optparse import OptionParser

sys.path.append('../')


def main():
    USAGE = "usage:    python extract_tags.py [file name] -k [top k]"

    parser = OptionParser(USAGE)
    parser.add_option("-k", dest="topK")
    opt, args = parser.parse_args()

    if len(args) < 1:
        print(USAGE)
        sys.exit(1)

    file_name = args[0]

    if opt.topK is None:
        topK = 10
    else:
        topK = int(opt.topK)
    get_topK_words(file_name, topK)


def get_topK_words(file_name, topK):
    content = open(file_name, 'rb').read()
    jieba.add_word('卡顿')
    jieba.analyse.set_stop_words('stop_words.txt')
    tags = jieba.analyse.extract_tags(content, topK=topK)
    return tags
    # print ",".join(tags).encode('utf-8')


if __name__ == '__main__':
    main()
