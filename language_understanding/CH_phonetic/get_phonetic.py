#coding:utf-8
from pinyin import PinYin

def get_phonetic(word):
    pinyin = PinYin()
    pinyin.load_word()
    return ''.join(pinyin.hanzipinyin(word))

if __name__ == '__main__':
    print get_phonetic('哈尔滨')
