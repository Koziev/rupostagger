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

tagger = RuPosTagger()
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

