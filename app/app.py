import re
from random import uniform
from collections import defaultdict

r_alphabet = re.compile(u'[а-яА-Я0-9-]+|[.,:;?!]+')

def generate_lines(corpus):
    data = open(corpus)
    for line in data:
        yield line.lower()

def generate_tokens(lines):
    for line in lines:
        for token in r_alphabet.findall(line):
            yield token

#Символы '$' используются для маркировки начала предложения. В дальнейшем, это делает проще выбор первого слова генерируемой фразы. В целом, метод действует следующим образом: он возвращает три подряд идущих токена, на каждой итерации сдвигаясь на один токен.
def generate_trigrams(tokens):
    t0, t1 = '$', '$'
    for t2 in tokens:
        yield t0, t1, t2
        if t2 in '.!?':
            yield t1, t2, '$'
            yield t2, '$','$'
            t0, t1 = '$', '$'
        else:
            t0, t1 = t1, t2

#Данный метод рассчитывает триграммную модель.
def train(corpus):
    lines = generate_lines(corpus)
    tokens = generate_tokens(lines)
    trigrams = generate_trigrams(tokens)

    bi, tri = defaultdict(lambda: 0.0), defaultdict(lambda: 0.0)

    for t0, t1, t2 in trigrams:
        bi[t0, t1] += 1
        tri[t0, t1, t2] += 1

    model = {}
    for (t0, t1, t2), freq in tri.items():
        if (t0, t1) in model:
            model[t0, t1].append((t2, freq/bi[t0, t1]))
        else:
            model[t0, t1] = [(t2, freq/bi[t0, t1])]
    return model

#Суть этого метода в том, что мы последовательно выбираем наиболее вероятные слова или знаки препинания до тех пор, пока не встречаем признак начала следующей фразы (символа $). Первое слово выбирается как наиболее вероятное для начала предложения из набора model['$', '$'].
def generate_sentence(model):
    phrase = ''
    t0, t1 = '$', '$'
    while 1:
        t0, t1 = t1, unirand(model[t0, t1])
        if t1 == '$': break
        if t1 in ('.!?,;:') or t0 == '$':
            phrase += t1
        else:
            phrase += ' ' + t1
    return phrase.capitalize()

def unirand(seq):
    sum_, freq_ = 0, 0
    for item, freq in seq:
        sum_ += freq
    rnd = uniform(0, sum_)
    for token, freq in seq:
        freq_ += freq
        if rnd < freq_:
            return token

if __name__ == '__main__':
    model = train('azimov.txt')
    for i in range(10):
        print(generate_sentence(model))
