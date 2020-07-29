# rupostagger - частеречная разметка для русского языка

Пакет позволяет распознать части речи и некоторую другую грамматическую
информацию (падеж, число, род и так далее) для слов в предложении.

# Установка

Наберите в консоли, возможно потребуется sudo:

```
pip install git+https://github.com/Koziev/rupostagger
```

Для работы пакета необходимо установить [rusyllab](https://github.com/Koziev/rusyllab)
и [ruword2tags](https://github.com/Koziev/ruword2tags), а также [python-crfsuite](https://python-crfsuite.readthedocs.io/en/latest/).
Для установки этих пакетов выполните:

```
pip install -r requirements.txt
```


# Использование

Для использования необходимо создать экземпляр класса RuPosTagger, затем
выполнить загрузку словарной базы и языковой модели вызовом метода load().
Затем можно делать распознавание списка слов методом tag, который принимает
список слов. Разбивку предложения на слова необходимо выполнять сторонними
средствами заранее, я для прототипирования NLP решений использую свой [пакет rutokenizer](https://github.com/Koziev/rutokenizer).

Пример:

```
import rupostagger

tagger = rupostagger.RuPosTagger()
tagger.load()
for word, label in tagger.tag(u'кошки спят'.split()):
	print(u'{} -> {}'.format(word, label))
```

Результат работы:

```
кошки -> NOUN|Case=Nom|Gender=Fem|Number=Plur
спят -> VERB|Mood=Ind|Number=Plur|Person=3|Tense=Notpast|VerbForm=Fin|Voice=Act
```

Для каждого слова возвращается строка, содержащая набор тегов, разделенных символом вертикальной черты. Первый
тэг это всегда наименование части речи, остальные теги имеют формат название_тега=значение. Наименования частей
речи и значения остальных тегов соответствуют соглашениям [Universal Dependencies](https://universaldependencies.org/).

# Тренировочный датасет

В архиве [samples.gz](https://github.com/Koziev/rupostagger/tmp/samples.gz) находится полный датасет для обучения модели. Морфологическая разметка в основном следует стандарту
Universal Dependencies, за исключением некоторых второстепенных деталей. В частности, не используется класс DET, вместо
него указывается ADJ.

# Оценки точности

Для объективной оценки использован [размеченный корпус из проекта OpenCorpora](http://opencorpora.org/files/export/annot/annot.opcorpora.no_ambig.xml.bz2).
Оцениваются отдельно метрики для существительных (классы NOUN, PROPN, LATN, ROMN),
прилагательных (ADJ), глаголов (VERB). По каждой части речи собирается статистика корректности
как метки грамматического класса (recall и precision), так и пары из класса
и морфологических тегов (соответственно NOUN+tags,
ADJ+tags, VERB+tags).  Из-за немного разных принципов морфологической
разметки точное сопоставление всех тегов невозможно. Поэтому оценивается
только совпадение ключевых тегов для каждого
из вышеперечисленных классов.  Для существительных проверялись теги Case и Number.
Для прилагательных проверялись теги Case, Number и Gender. Для глаголов
сравливались теги Number и Gender.

Метрики:

```
NOUN support=29790
NOUN recall=0.9828801611278952
NOUN precision=0.9949031600407747
NOUN+tags precision=0.9626024590163934

ADJ support=8156
ADJ recall=0.9776851397743992
ADJ precision=0.9032623470774808
ADJ+tags precision=0.9653875094055681

VERB support=8908
VERB recall=0.995958688819039
VERB precision=0.9678193520235627
VERB+tags precision=0.9994364292155095
```
