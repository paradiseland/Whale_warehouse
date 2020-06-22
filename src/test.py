# coding=utf-8
# /usr/bin/Python3.6

"""
Author: Xingwei CHEN
Email:cxw19@mails.tsinghua.edu.cn
"""
import logging


if __name__ == "__main__":
    logging.basicConfig(filename='test0622.log', level=logging.DEBUG)
    for i in range(10):
        logging.debug('what fuck! \n')
