#!/usr/bin/env python
# -*- coding:utf-8 -*-

__version__ = '0.9'
__all__ = ["PinYin"]

import os.path


class PinYin(object):
    def __init__(self, dict_file='word.data'):
        DIR_PATH = os.path.dirname(__file__)
        self.word_dict = {}
        self.dict_file = os.path.join(DIR_PATH,dict_file)


    def load_word(self):
        if not os.path.exists(self.dict_file):
            raise IOError("NotFoundFile")

        with file(self.dict_file) as f_obj:
            for f_line in f_obj.readlines():
                try:
                    line = f_line.split('    ')
                    self.word_dict[line[0]] = line[1]
                except:
                    line = f_line.split('   ')
                    self.word_dict[line[0]] = line[1]


    def hanzipinyin(self, string=""):
        result = []
        if not isinstance(string, unicode):
            string = string.decode("utf-8")
        
        for char in string:
            key = '%X' % ord(char)
            result.append(self.word_dict.get(key, char).split()[0][:-1].lower())

        return result


    def hanzipinyin_split(self, string="", split=""):
        result = self.hanzipinyin(string=string)
        if split == "":
            return result
        else:
            return split.join(result)


if __name__ == "__main__":
    test = PinYin()
    test.load_word()
    string = "哈尔滨"
    print "in: %s" % string
    print "out: %s" % str(test.hanzipinyin(string=string))
    print "out: %s" % test.hanzipinyin_split(string=string, split="-")
