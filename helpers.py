import pandas as pd
import random

df_first_stage = pd.read_csv('./data/first_stage.csv',encoding='utf-8')
syrian_ques = df_first_stage['syrian_dialect_ques']
arabic_ques = df_first_stage['arabic_ques']


# df_symptoms = pd.read_csv('./data/symptoms.csv',encoding='utf-8')


def generateQuesForFirstStage(idQues,typeQues):
    typeQuestion = 'arabic_ques'
    if typeQues == 'sy':
        typeQuestion = 'syrian_dialect_ques'

    category_questions = df_first_stage.loc[df_first_stage['category'] == idQues, typeQuestion]
    return random.choice(category_questions.values.tolist())



def generateQuesForSymptom():
    return ''
