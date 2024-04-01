import pandas as pd
import nltk
import re
import string
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def process(jd):
    resume = pd.read_csv('uploads/res.csv', encoding='ISO-8859-1')
    corpus=[]
    for i in range(len(resume)):
        ret= re.sub('[^a-zA-Z]', ' ', resume['resumes'][i])
        ret=ret.lower()
        corpus.append(ret)

    resume['resumes']=corpus
    # jd="Proven work experience as a Front-end developer Hands on experience with markup languages Experience with JavaScript, CSS and jQuery Familiarity with browser testing and debugging In-depth understanding of the entire web development process (design, development and  deployment"
    pun=str.maketrans("", "", string.punctuation)
    jd= jd.translate(pun)

    vectorizer = TfidfVectorizer(max_features=500)
    sim=[]
    for i in range(len(resume)):
        resumetext=resume.iloc[i,1]
        # print(jd)
        # print(resumetext)
        resumevect = vectorizer.fit_transform([resumetext, jd])
        cosine_similarities = cosine_similarity(resumevect[0], resumevect[1])
        similarity_score = cosine_similarities[0][0]
        sim.append(similarity_score)
        # print(similarity_score)

    result_df = pd.DataFrame({'Similarity': sim})
    resume['Similarity'] = result_df['Similarity']
    resume.to_csv('output.csv', index=False)
    resume=pd.read_csv('output.csv')
    sorted_df = resume.sort_values(by='Similarity', ascending=False)
    sorted_df.to_csv('sorted.csv', index=False)