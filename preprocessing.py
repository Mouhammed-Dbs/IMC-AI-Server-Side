import numpy as np
import re
import ijson
import json

def getVector(desired_key):
    for i in range(11):
        with open('data/vectors'+str(i)+'.json', 'r', encoding='utf-8') as file:
            parser = ijson.parse(file)
            for prefix, event, value in parser:
                if prefix == desired_key:
                    return np.array(json.loads(value))
        return []

def removePrefixes(word):
    if len(word)>3:
        patterns = [r'^بي',r'^ب',r'^ال', r'^بال',r'^هال',r'^وب',r'^بت']
        patterns.extend([r'^و' + pattern[1:] for pattern in patterns ])
        for pattern in patterns:
            word = re.sub(pattern, '', word)
    return removeSuffix(word)


def removeSuffix(word):
    if len(word)>3:
        patterns = [r'ني$',r'ة$',r'ه$']
        for pattern in patterns:
            word = re.sub(pattern, '', word)
    return word



def processSent(words,stopwords):
    words = [removePrefixes(word) for word in words if word not in stopwords]
    copy_words = [removePrefixes(word) for word in words.copy() if word not in stopwords]
    negative_words = ['مو', 'ما', 'لا','ماني','ماعم','مارح','مابقى','مابقا','مافي']
    negative_words.extend([ "و"+word for word in negative_words ])
    neg = 'ما'
    for i,word in enumerate(words):
        if i>1:
            if words[i-1].strip() in negative_words and words[i-2] in ['كل']:
                if words[i-2] in copy_words:
                    copy_words.remove(words[i-2])
                if words[i-1] in copy_words:
                    copy_words.remove(words[i-1])
                copy_words.insert(i-2,words[i-2]+words[i-1])
        if i>0:
            if words[i-1].strip() in negative_words:
                if words[i-1] in copy_words:
                    copy_words.remove(words[i-1])
                if word in copy_words:
                    copy_words.remove(word)
                copy_words.insert(i-1,neg+word)
    return copy_words

def sentToVec(X_train):
    X_train_vectors = []
    for sentence in X_train:
        sentence_vector = []
        for word in sentence:
            if len(getVector(word))>0:
                word_vector = getVector(word)
                sentence_vector.append(word_vector)
            else:
                word_vector = np.zeros(300)
                sentence_vector.append(word_vector)

        X_train_vectors.append(sentence_vector)
    return X_train_vectors

