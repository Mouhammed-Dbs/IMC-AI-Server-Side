import numpy as np
import re

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

def sentToVec(wv,X_train):
    X_train_vectors = []
    for sentence in X_train:
        sentence_vector = []
        for word in sentence:
            try:
                word_vector = wv[word]
                sentence_vector.append(word_vector)
            except KeyError:
                word_vector = np.zeros(300)
                sentence_vector.append(word_vector)
                pass

        X_train_vectors.append(sentence_vector)
    return X_train_vectors

