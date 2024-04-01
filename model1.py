import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
nltk.download('stopwords')
from pyresparser import ResumeParser
import re

augmented_data=pd.read_csv("augmented_dataset.csv")

corpus=[]
def clean_function(resumeText):
    resumeText = re.sub('http\S+\s*', ' ', resumeText)  # remove URLs
    resumeText = re.sub('RT|cc', ' ', resumeText)  # remove RT and cc
    resumeText = re.sub('#\S+', '', resumeText)  # remove hashtags
    resumeText = re.sub('@\S+', '  ', resumeText)  # remove mentions
    resumeText = re.sub('[%s]' % re.escape("""!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"""), ' ', resumeText)  # remove punctuations
    resumeText = re.sub(r'[^\x00-\x7f]',r' ', resumeText)
    resumeText = re.sub('\s+', ' ', resumeText)  # remove extra whitespace
    resumeText=resumeText.lower()
    corpus.append(resumeText)
    return resumeText

augmented_data['Resume'] = augmented_data['Resume'].apply(lambda x: clean_function(x))

def role(skills):
    cv=CountVectorizer()
    x=cv.fit_transform(corpus).toarray()
    y=augmented_data.iloc[:,0].values

    # predicting one job role using classification:
    classifier = DecisionTreeClassifier(criterion = 'entropy', random_state = 0)
    classifier.fit(x, y)
    # y_pred = classifier.predict(x)
    req=[skills.lower()]
    req=cv.transform(req)
    category=classifier.predict(req)
    return category
