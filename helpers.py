from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
import numpy as np
import json
import pandas as pd
import random
from preprocessing import sentToVec, processSent
import pickle
from gensim.models import KeyedVectors

# Load models and vocabulary
wv = KeyedVectors.load("models/word2vec_data.wordvectors", mmap='r')
model = load_model('models/seq2seq.keras')
enc_model = load_model('models/encoder_model.keras')
dec_model = load_model('models/decoder_model.keras')
disorder_model = load_model('models/disorder_model.keras')
symptoms_model = load_model('models/symptoms_model.keras')

with open('data/vocab.json', 'r') as file:
    vocab = json.load(file)
with open('data/inv_vocab.json', 'r') as file:
    inv_vocab = json.load(file)

DISORDERS = {'1':'depression','2':'anxiety'}
df_symptoms = pd.read_csv('./data/symptoms.csv', encoding='utf-8')

df_first_stage = pd.read_csv('./data/ques/first_stage.csv', encoding='utf-8')
syrian_ques = df_first_stage['syrian_dialect_ques']
arabic_ques = df_first_stage['arabic_ques']

######## SECOND STAGE #######
df_second_stage_depression = pd.read_csv('./data/ques/second_stage_depression.csv', encoding='utf-8')
syrian_ques = df_second_stage_depression['syrian_dialect_ques']
arabic_ques = df_second_stage_depression['arabic_ques']
df_second_stage_anxiety = pd.read_csv('./data/ques/second_stage_anxiety.csv', encoding='utf-8')
syrian_ques = df_second_stage_anxiety['syrian_dialect_ques']
arabic_ques = df_second_stage_anxiety['arabic_ques']
#############################

######## THIRD STAGE #######
df_third_stage_depression = pd.read_csv('./data/ques/third_stage_depression.csv', encoding='utf-8')
syrian_ques = df_third_stage_depression['syrian_dialect_ques']
arabic_ques = df_third_stage_depression['arabic_ques']
df_third_stage_anxiety = pd.read_csv('./data/ques/third_stage_anxiety.csv', encoding='utf-8')
syrian_ques = df_third_stage_anxiety['syrian_dialect_ques']
arabic_ques = df_third_stage_anxiety['arabic_ques']
#############################

stageLimits = {
    'firstStageLimit':max(df_first_stage['category']),
    'secondStageLimit':{'2':max(df_second_stage_anxiety['category']),
                        '1':max(df_second_stage_depression['category'])},
    'thirdStageLimit':{'2':max(df_third_stage_anxiety['category']),
                       '1':max(df_third_stage_depression['category'])}
}

def getStageLimits():
    return stageLimits

quesVocab = {
    'syrian_dialect_ques': {"2": [], '1': []},
    'arabic_ques': {"2": [], '1': []}
}

def getQuesByCategorey(category,disorder='1',typeQuestion='arabic_ques'):
    return [row['que'] for row in quesVocab[typeQuestion][disorder] if row['category']==category]

def collect_ques(stage_df,prev=0, category_col='category', ques_col='arabic_ques'):
    return [{'category': row[category_col]+prev, 'que': row[ques_col]} for index, row in stage_df.iterrows()]

quesVocab['arabic_ques']['2'].extend(collect_ques(df_first_stage))
quesVocab['arabic_ques']['2'].extend(collect_ques(df_second_stage_anxiety,prev=getStageLimits()['firstStageLimit']))
quesVocab['arabic_ques']['2'].extend(collect_ques(df_third_stage_anxiety,prev=getStageLimits()['firstStageLimit']+getStageLimits()['secondStageLimit']['2']))

quesVocab['arabic_ques']['1'].extend(collect_ques(df_first_stage))
quesVocab['arabic_ques']['1'].extend(collect_ques(df_second_stage_depression,prev=getStageLimits()['firstStageLimit']))
quesVocab['arabic_ques']['1'].extend(collect_ques(df_third_stage_depression,prev=getStageLimits()['firstStageLimit']+getStageLimits()['secondStageLimit']['1']))

quesVocab['syrian_dialect_ques']['2'].extend(collect_ques(df_first_stage, ques_col='syrian_dialect_ques'))
quesVocab['syrian_dialect_ques']['2'].extend(collect_ques(df_second_stage_anxiety,prev=getStageLimits()['firstStageLimit'], ques_col='syrian_dialect_ques'))
quesVocab['syrian_dialect_ques']['2'].extend(collect_ques(df_third_stage_anxiety,prev=getStageLimits()['firstStageLimit']+getStageLimits()['secondStageLimit']['2'], ques_col='syrian_dialect_ques'))

quesVocab['syrian_dialect_ques']['1'].extend(collect_ques(df_first_stage, ques_col='syrian_dialect_ques'))
quesVocab['syrian_dialect_ques']['1'].extend(collect_ques(df_second_stage_depression,prev=getStageLimits()['firstStageLimit'], ques_col='syrian_dialect_ques'))
quesVocab['syrian_dialect_ques']['1'].extend(collect_ques(df_third_stage_depression,prev=getStageLimits()['firstStageLimit']+getStageLimits()['secondStageLimit']['1'], ques_col='syrian_dialect_ques'))

df_normal_response = pd.read_csv('./data/normal_response.csv', encoding='utf-8')
normal_res = df_normal_response['sentence']



# Load stopwords once
with open('data/stopwords_ar.pkl', 'rb') as file:
    stopwords = pickle.load(file)

def generateResponse(idQues, userRes=None, typeQues='ar',idDisorder=1):
    # borderSymptom = getStageLimits()["firstStageLimit"]
    typeQuestion = 'arabic_ques'
    if typeQues == 'sy':
        typeQuestion = 'syrian_dialect_ques'
    # if idQues <= borderSymptom:
    if userRes is None or userRes == '':
        category_questions = getQuesByCategorey(idQues,idDisorder,typeQuestion)
        return {"type": "que", "result": random.choice(category_questions)}
    else:
        if isGenerateSeq2Seq(userRes):
            print("seq2seq")
            return {"type": "seq", "result": generateSeq2Seq(userRes)}
        print("normal")
        return {"type": "sent", "result": random.choice(normal_res.values.tolist())}
    # return {"type": "unknown"}

def generateSeq2Seq(prepro1):
    tokens = ['<PAD>', '<EOS>', '<OUT>', '<SOS>']
    max_len = 23
    prepro = [prepro1]

    txt = []
    for x in prepro:
        lst = [vocab[word] if word in vocab else vocab['<OUT>'] for word in x.split()]
        txt.append(lst)

    txt = pad_sequences(txt, max_len, padding='post')
    stat = enc_model.predict(txt)

    empty_target_seq = np.zeros((1, 1))
    empty_target_seq[0, 0] = vocab['<SOS>']

    stop_condition = False
    decoded_translation = ''

    while not stop_condition:
        dec_outputs, h, c = dec_model.predict([empty_target_seq] + stat)
        decoder_concat_input = model.layers[-1](dec_outputs)
        sampled_word_index = np.argmax(decoder_concat_input[0, -1, :])
        sampled_word = inv_vocab[str(sampled_word_index)] + ' '

        if sampled_word != '<EOS> ':
            decoded_translation += sampled_word

        if sampled_word == '<EOS> ' or len(decoded_translation.split()) > max_len:
            stop_condition = True

        empty_target_seq = np.zeros((1, 1))
        empty_target_seq[0, 0] = sampled_word_index
        stat = [h, c]
    for token in tokens:
        decoded_translation = decoded_translation.replace(token, "")
    return decoded_translation

def isGenerateSeq2Seq(sent):
    padded_sent = pad_sequences(sentToVec(wv,[processSent(sent.split(), stopwords)]), maxlen=15, padding='post', dtype='float32')
    predictions = disorder_model.predict(padded_sent)
    d = np.argmax(predictions, axis=1)[0]
    padded_sent = pad_sequences(sentToVec(wv,[processSent(sent.split(), stopwords)]), maxlen=13, padding='post', dtype='float32')
    predictions = symptoms_model.predict(padded_sent)
    s = np.argmax(predictions, axis=1)[0]
    print('s:'+str(s)+'  d:'+str(d))
    if d+s==0 :
        return False
    return True

def predictDisorderForUserAnswers(sentences):
    meanPredictions = np.zeros((1, 3))
    sum_5_6 = 0
    sum_7_8 = 0

    for sent_dict in sentences:
        sent = sent_dict['content']
        idQue = sent_dict['idQue']

        padded_sent_disorder = pad_sequences(sentToVec(wv, [processSent(sent.split(), stopwords)]), maxlen=15, padding='post', dtype='float32')
        padded_sent_symptom = pad_sequences(sentToVec(wv,[processSent(sent.split(), stopwords)]), maxlen=13, padding='post', dtype='float32')
        predictions = disorder_model.predict(padded_sent_disorder)
        meanPredictions += predictions

        if 5 <= idQue < 9:
            symptom_predictions = symptoms_model.predict(padded_sent_symptom)
            if idQue in [5, 6]:
                sum_5_6 += symptom_predictions[0, 31]
            elif idQue in [7, 8]:
                sum_7_8 += symptom_predictions[0, 19]
    meanPredictions = meanPredictions / len(sentences)

    result_5_6 = sum_5_6 * meanPredictions[0, 1]
    result_7_8 = sum_7_8 * meanPredictions[0, 2]
    print('anxiety:',result_5_6)
    print('depression',result_7_8)
    if result_5_6 > result_7_8:
        return 2
    else:
        return 1


def extractSymptomsForUserAnswers(sentences,idDisorder):
    symptoms = []
    label = 0
    for sent in sentences:
        labels = []
        for s in symptoms:
            labels.append(s['label'])
        padded_sent = pad_sequences(sentToVec(wv,[processSent(sent.split(), stopwords)]), maxlen=13, padding='post', dtype='float32')
        predictions = symptoms_model.predict(padded_sent)
        label = np.argmax(predictions, axis=1)[0]
        filtered_row = df_symptoms[(df_symptoms['label'] == label) & (df_symptoms['class'] == DISORDERS[idDisorder])]
        if len(filtered_row['sentence'].values)>0:
            name_symptom = filtered_row['sentence'].values[0]
            if label not in labels:
                symptoms.append({'name':name_symptom,'label':int(label),'prob':float(predictions[0][label])})
            else:
                for i,d in enumerate(symptoms):
                    if d['label'] == label:
                        symptoms[i]['prob'] = max(symptoms[i]['label'],float(predictions[0][label]))
    return symptoms