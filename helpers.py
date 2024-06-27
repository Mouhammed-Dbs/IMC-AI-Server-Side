from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
import numpy as np
import json
import pandas as pd
import random
from preprocessing import sentToVec, processSent
import pickle

# Load models and vocabulary
# model = load_model('models/seq2seq.keras')
# enc_model = load_model('models/encoder_model.keras')
# dec_model = load_model('models/decoder_model.keras')
disorder_model = load_model('models/disorder_model.keras')

with open('data/vocab.json', 'r') as file:
    vocab = json.load(file)
with open('data/inv_vocab.json', 'r') as file:
    inv_vocab = json.load(file)

df_first_stage = pd.read_csv('./data/first_stage.csv', encoding='utf-8')
syrian_ques = df_first_stage['syrian_dialect_ques']
arabic_ques = df_first_stage['arabic_ques']
df_normal_response = pd.read_csv('./data/normal_response.csv', encoding='utf-8')
normal_res = df_normal_response['sentence']

# Load stopwords once
with open('data/stopwords_ar.pkl', 'rb') as file:
    stopwords = pickle.load(file)

def generateResponse(idQues, userRes=None, typeQues='ar'):
    borderSymptom = 11
    typeQuestion = 'arabic_ques'
    if typeQues == 'sy':
        typeQuestion = 'syrian_dialect_ques'
    if idQues < borderSymptom:
        if userRes is None or userRes == '':
            category_questions = df_first_stage.loc[df_first_stage['category'] == idQues, typeQuestion]
            return {"type": "que", "result": random.choice(category_questions.values.tolist())}
        else:
            if predictDisorder(userRes) > 0:
                return {"type": "seq", "result": "generateSeq2Seq(userRes)"}
            return {"type": "sent", "result": random.choice(normal_res.values.tolist())}
    return {"type": "unknown"}

# def generateSeq2Seq(prepro1):
#     tokens = ['<PAD>', '<EOS>', '<OUT>', '<SOS>']
#     max_len = 23
#     prepro = [prepro1]

#     txt = []
#     for x in prepro:
#         lst = [vocab[word] if word in vocab else vocab['<OUT>'] for word in x.split()]
#         txt.append(lst)

#     txt = pad_sequences(txt, max_len, padding='post')
#     stat = enc_model.predict(txt)

#     empty_target_seq = np.zeros((1, 1))
#     empty_target_seq[0, 0] = vocab['<SOS>']

#     stop_condition = False
#     decoded_translation = ''

#     while not stop_condition:
#         dec_outputs, h, c = dec_model.predict([empty_target_seq] + stat)
#         decoder_concat_input = model.layers[-1](dec_outputs)
#         sampled_word_index = np.argmax(decoder_concat_input[0, -1, :])
#         sampled_word = inv_vocab[str(sampled_word_index)] + ' '

#         if sampled_word != '<EOS> ':
#             decoded_translation += sampled_word

#         if sampled_word == '<EOS> ' or len(decoded_translation.split()) > max_len:
#             stop_condition = True

#         empty_target_seq = np.zeros((1, 1))
#         empty_target_seq[0, 0] = sampled_word_index
#         stat = [h, c]
#     for token in tokens:
#         decoded_translation = decoded_translation.replace(token, "")
#     return decoded_translation

def predictDisorder(sent):
    padded_sent = pad_sequences(sentToVec([processSent(sent.split(), stopwords)]), maxlen=15, padding='post', dtype='float32')
    predictions = disorder_model.predict(padded_sent)
    print(predictions)
    return np.argmax(predictions, axis=1)[0]
