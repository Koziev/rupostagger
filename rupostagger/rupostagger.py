# -*- coding: utf-8 -*-
'''
'''

from __future__ import print_function
from __future__ import division  # for python2 compatibility

import os
import json
import pathlib

import pycrfsuite
import ruword2tags
import rusyllab


BEG_TOKEN = '<beg>'
END_TOKEN = '<end>'

token2tag = {BEG_TOKEN: BEG_TOKEN, END_TOKEN: END_TOKEN,
             ',': '<comma>',
             '.': '<dot>',
             '-': '<hyphen>',
             '!': '<exclam>',
             '?': '<quest>'}


class RuPosTagger(object):
    def __init__(self):
        self.winspan = -1
        self.use_w2v = -1
        self.use_syllabs = -1
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

        self.word2tags = ruword2tags.RuWord2Tags()
        self.word2tags.load()

        model_path = os.path.join(data_folder, 'rupostagger.model')
        self.tagger = pycrfsuite.Tagger()
        self.tagger.open(model_path)

    @staticmethod
    def __normalize_word(word):
        return word.replace(' - ', '-').replace(u'ё', u'е').lower()

    def get_word_features(self, word, prefix):
        features = []

        if word in token2tag:
            features.append((u'tag[{}]={}'.format(prefix, token2tag[word]), 1.0))
        else:
            nword = self.__normalize_word(word)
            if self.use_syllabs and nword[0] in u'абвгдеёжзийклмнопрстуфхцчшщъыьэюя':
                syllabs = rusyllab.split_word(nword)
                if len(syllabs) > 0:
                    if len(syllabs) == 1:
                        features.append((u'slb[{}]={}'.format(prefix, syllabs[0] + '~'), 1.0))
                    else:
                        features.append((u'slb[{}]={}'.format(prefix, syllabs[0] + '~'), 1.0))
                        for s in syllabs[1:-1]:
                            features.append((u'slb[{}]={}'.format(prefix, '~' + s + '~'), 1.0))
                        features.append((u'slb[{}]={}'.format(prefix, '~' + syllabs[-1]), 1.0))

            if self.use_gren:
                tags = set()
                for tagset in self.word2tags[nword]:
                    tags.update(tagset.split(' '))

                for tag in tags:
                    features.append((u'tag[{}]={}'.format(prefix, tag), 1.0))

            if self.use_w2v:
                raise NotImplementedError()

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


if __name__ == '__main__':
    tagger = RuPosTagger()
    tagger.load()
    for word, label in tagger.tag(u'кошки спят'.split()):
        print(u'{} -> {}'.format(word, label))
