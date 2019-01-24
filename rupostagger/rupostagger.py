# -*- coding: utf-8 -*-
'''
'''

from __future__ import print_function
from __future__ import division  # for python2 compatibility

import os
import json
import pathlib
import re

import pycrfsuite
import ruword2tags
import rusyllab


BEG_TOKEN = '<beg>'
END_TOKEN = '<end>'

token2tag = {BEG_TOKEN: BEG_TOKEN, END_TOKEN: END_TOKEN}


def is_num(token):
    return re.match('^[0-9]+$', token)


class RuPosTagger(object):
    def __init__(self):
        self.winspan = -1
        self.use_w2v = -1
        self.use_syllabs = -1
        self.ending_len = -1
        self.word2tags = None

    def load(self):
        module_folder = str(pathlib.Path(__file__).resolve().parent)
        data_folder = os.path.join(module_folder, '../tmp')
        if not os.path.exists(data_folder):
            data_folder = module_folder

        config_path = os.path.join(data_folder, 'rupostagger.config')
        with open(config_path, 'r') as wrt:
            self.config = json.load(wrt)
            self.winspan = self.config['winspan']
            self.use_gren = self.config['use_gren']
            self.use_w2v = self.config['use_w2v']
            self.use_syllabs = self.config['use_syllabs']
            self.ending_len = self.config['ending_len']

        self.word2tags = ruword2tags.RuWord2Tags()
        self.word2tags.load()

        model_path = os.path.join(data_folder, 'rupostagger.model')
        self.tagger = pycrfsuite.Tagger()
        self.tagger.open(model_path)

    @staticmethod
    def __normalize_word(word):
        return word.replace(' - ', '-').replace(u'ё', u'е').lower()

    def get_word_features(self, word, prefix):
        assert(len(word) > 0)
        features = []

        if word in token2tag:
            features.append((u'tag[{}]={}'.format(prefix, token2tag[word]), 1.0))
        elif is_num(word):
            features.append((u'tag[{}]=<num> tag[{}]=<num_{}>'.format(prefix, prefix, word[-1]), 1.0))
        elif len(word) == 1 and word[0] in u'‼≠™®•·[¡+<>`~;.,‚?!-…№”“„{}|‹›/\'"–—_:«»*]()‘’≈':
            features.append((u'tag[{}]=punct_{}'.format(prefix, ord(word[0])), 1.0))
        else:
            uword = self.__normalize_word(word)
            first_char = uword[0]
            if first_char in 'abcdefghijklmnopqrstuvwxyz':
                features.append((u'word[{}]=<latin>'.format(prefix), 1.0))
            else:
                if first_char in u'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ':
                    features.append((u'word[{}]=<upper1>'.format(prefix), 1.0))

                if self.ending_len > 0:
                    ending = '~' + uword[-self.ending_len:] if len(uword) > self.ending_len else uword
                    features.append((u'ending[{}]={}'.format(prefix, ending), 1.0))

                if self.use_syllabs and first_char in u'абвгдеёжзийклмнопрстуфхцчшщъыьэюя':
                    syllabs = rusyllab.split_word(uword)
                    if len(syllabs) > 0:
                        if len(syllabs) == 1:
                            features.append((u'slb[{}]={}'.format(prefix, syllabs[0] + '~'), 1.0))
                        else:
                            features.append((u'slb[{}]={}'.format(prefix, syllabs[0]+'~'), 1.0))
                            for s in syllabs[1:-1]:
                                features.append((u'slb[{}]={}'.format(prefix, '~'+s+'~'), 1.0))
                            features.append((u'slb[{}]={}'.format(prefix, '~'+syllabs[-1]), 1.0))

                if self.use_gren:
                    tags = set()
                    for tagset in self.word2tags[word.lower()]:
                        tags.update(tagset.split(' '))

                    for tag in tags:
                        features.append((u'tag[{}]={}'.format(prefix, tag), 1.0))

        return features

    def vectorize_sample(self, words):
        lines2 = []
        nb_words = len(words)
        for iword, word in enumerate(words):
            word_features = dict()
            for j in range(-self.winspan, self.winspan + 1):
                iword2 = iword + j
                if nb_words > iword2 >= 0:
                    features = self.get_word_features(words[iword2], str(j))
                    word_features.update(features)

            lines2.append(word_features)

        return lines2

    def tag(self, words):
        X = self.vectorize_sample([BEG_TOKEN]+words+[END_TOKEN])
        y_pred = self.tagger.tag(X)
        return zip(words, y_pred[1: -1])


def test1(tagger, phrase, required_labels):
    pred_labels = list(tagger.tag(phrase.split()))
    assert(len(required_labels.split()) == len(pred_labels))
    for required_label, (word, pred_label) in zip(required_labels.split(), pred_labels):
        for tag in required_label.split('|'):
            if tag not in pred_label:
                print(u'Error: phrase={} word={} required_label={} pred_label={}'.format(phrase, word, required_label, pred_label))
                return False

    return True

def run_tests():
    tagger = RuPosTagger()
    tagger.load()

    for phrase, required_labels in [(u'кошки спят', u'NOUN|Number=Plur|Case=Nom VERB|Mood=Ind|Number=Plur|Person=3|Tense=Notpast|VerbForm=Fin'),
                                    (u'я рою колодец', u'PRON VERB NOUN|Number=Sing|Case=Acc'),
                                    (u'я мою окно', u'PRON VERB NOUN|Number=Sing|Case=Acc'),
                                    (u'Ира мыла окно', u'NOUN|Case=Nom VERB NOUN|Number=Sing|Case=Acc'),
                                    (u'Возьми мою пилу', u'VERB ADJ|Case=Acc NOUN|Case=Acc'),
                                    (u'рой колодец', u'VERB NOUN|Number=Sing|Case=Acc')]:
        if not test1(tagger, phrase, required_labels):
            print('Tests FAILED')
            return

    print('Tests PASSED OK')


if __name__ == '__main__':
    run_tests()




