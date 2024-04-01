import yake
from yake.highlight import TextHighlighter
from find_job_titles import FinderAcora
from typing import Union, Tuple
import re
from common.utils import load_programming_languages, load_stopwords, load_design_tools, load_business_analyst_skills
from acora import AcoraBuilder
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class Resume:
    def __init__(self,jd,res):
        self.job_description=jd
        self.job_titles=None
        self.raw_resume=res
        self.included_keywords=None
        self.missing_keywords=None
        self.experience_metadata=None
        self.job_keywords=None
        self.job_skills=None
        self.final_resume=None
        self.job_yake_keywords=None
        self.resume_keywords=None
        self.resume_skills=None

    def load_yake_extractor(
        language="en",
        max_ngram_size=2,
        deduplication_threshold=0.9,
        deduplication_algo="seqm",
        num_keywords=10,
    ) -> yake.KeywordExtractor:
        # hardcode parameters into yake extractor (change if needed later)
        return yake.KeywordExtractor(
            lan=language,
            n=max_ngram_size,
            dedupLim=deduplication_threshold,
            dedupFunc=deduplication_algo,
            top=num_keywords,
            features=None,
        )
    def extract_job_description_yake_keywords(self, yake_extractor):
        stopwords = load_stopwords()
        raw_yake_output = yake_extractor.extract_keywords(self.job_description)
        yake_keywords = [
            keyword_tuple[0] for keyword_tuple in raw_yake_output
        ]  
        punctuation_chars = "!\"#$%&'()*+,-./:;<=>?@[]^_`{|}~\\"
        all_keywords = [m for m in yake_keywords if m not in stopwords and m[0] not in punctuation_chars]
        self.job_yake_keywords = list(set(all_keywords))
        return self.job_yake_keywords
    
    def extract_job_description_skills(self):
        skills_base_dict = {
            "programming_languages": load_programming_languages(),
            "design_tools": load_design_tools(),
            "business_analyst_skills": load_business_analyst_skills()
        }
        found_skills_dict = dict()
        found_skills_list = list() 
        for skill_type, skill_list in skills_base_dict.items():
            acora_search_engine = AcoraBuilder(skill_list).build()
            found_skills_dict[skill_type] = list(set([k[0] for k in acora_search_engine.findall(self.job_description)]))
            found_skills_list += found_skills_dict[skill_type]
        self.job_skills = found_skills_dict
        return found_skills_list
    
    def extract_all_job_keywords(self,yake_extractor):

        yake_keywords = self.extract_job_description_yake_keywords(yake_extractor)
        skills_keywords = self.extract_job_description_skills()
        self.job_keywords = yake_keywords + skills_keywords
        self.job_keywords=list(set(self.job_keywords))
        return self.job_keywords, skills_keywords
    
    def extract_resume_yake_keywords(self,yake_extractor):
        stopwords = load_stopwords()
        raw_yake_output = yake_extractor.extract_keywords(self.raw_resume)
        yake_keywords = [
            keyword_tuple[0] for keyword_tuple in raw_yake_output
        ]  # not including score in tuple

        # removing duplicates, stopwords, and target company name (if exists)
        punctuation_chars = "!\"#$%&'()*+,-./:;<=>?@[]^_`{|}~\\"
        all_keywords = [m for m in yake_keywords if m not in stopwords and m[0] not in punctuation_chars]
        self.resume_keywords = list(set(all_keywords))

        return self.resume_keywords
    
    def extract_resume_skills(self):
        skills_base_dict = {
            "programming_languages": load_programming_languages(),
            "design_tools": load_design_tools(),
            "business_analyst_skills": load_business_analyst_skills()
        }
        found_skills_dict = dict()
        found_skills_list = list()  # easy to add to yake keywords in final function
        for skill_type, skill_list in skills_base_dict.items():
            acora_search_engine = AcoraBuilder(skill_list).build()
            found_skills_dict[skill_type] = list(set([k[0] for k in acora_search_engine.findall(self.raw_resume)]))
            found_skills_list += found_skills_dict[skill_type]
        self.resume_skills = found_skills_dict
        return found_skills_list
    
    def extract_all_resume_keywords(self,yake_extractor):

        yake_keywords = self.extract_resume_yake_keywords(yake_extractor)
        skills_keywords = self.extract_resume_skills()
        self.resume_keywords= yake_keywords + skills_keywords
        # print(self.job_keywords)
        self.resume_keywords=list(set(self.resume_keywords))
        return self.resume_keywords

    def extract_included_and_missing_keywords(self, matcher, spacy_model,yake_extractor):
        rules = [[{"TEXT": keyword}] for keyword in self.job_keywords]
        matcher.add("keyword_matcher", rules)
        resume_str = self.raw_resume
        if type(self.raw_resume) is list:
            resume_str = " ".join(
                [experience["description"] for experience in self.raw_resume]
            )
        raw_resume_doc = spacy_model(resume_str)
        raw_phrase_matches = matcher(raw_resume_doc)
        phrase_matches_list = []
        for match_id, start, end in raw_phrase_matches:
            span = raw_resume_doc[start:end]  
            phrase_matches_list.append(span.text)

        # yake_keywords = self.extract_resume_yake_keywords(yake_extractor)
        # skills_keywords = self.extract_resume_skills()
        # print(phrase_matches_list)
        inc=list(set([n for n in self.resume_keywords if n in self.job_keywords]))
        phrase_matches_list.extend(inc)
        # print(phrase_matches_list)
        # phrase_matches_list.extend(skills_keywords)
        # print(phrase_matches_list)
        # removing duplicates from matched (included) keywords and assigning included/missing keyword lists
        self.included_keywords =list(set([k for k in phrase_matches_list if k in self.job_keywords]))
        self.missing_keywords = [
            n for n in self.job_keywords if n not in self.included_keywords
        ]
        return phrase_matches_list,self.included_keywords, self.missing_keywords
    
    def get_highlighted_keywords_in_job_description(
        job_description: str, job_keywords: list, highlight_tag: str = "b"
    ):
        max_ngram_keyword_len = int(
            max([len(keyword.split()) for keyword in job_keywords])
        )

        # using yake custom highlighter to return job_description with highlighted keywords
        custom_highlighter = TextHighlighter(
            max_ngram_size=max_ngram_keyword_len,
            highlight_pre=f"<{highlight_tag}>",
            highlight_post=f"</{highlight_tag}>",
        )
        highlighted_description = custom_highlighter.highlight(
            job_description, job_keywords
        )

        return highlighted_description
    
    def get_resume_keyword_score(self,data):
        keyscore=len(self.included_keywords)/len(self.job_keywords)
        keyscore=.7*keyscore
        if(data['total_experience']>=1 or data['experience']!=None and len(data['experience'])>=1):
            keyscore=keyscore+.3
        print(data['experience'])
        vectorizer = TfidfVectorizer(max_features=500)
        tfidf_matrix = vectorizer.fit_transform([self.raw_resume, self.job_description])
        cosine_sim = cosine_similarity(tfidf_matrix[0], tfidf_matrix[1])
        similarity_score = cosine_sim[0][0]
        return similarity_score,keyscore
    
