from flask import Flask, request, jsonify, render_template,render_template_string,send_file
from flask_cors import CORS
import spacy
from spacy.matcher import Matcher
from models.resume import Resume
from werkzeug.utils import secure_filename
import os
from PyPDF2 import PdfReader
import nltk
nltk.download('stopwords')
from pyresparser import ResumeParser
import model1 as m
import model2 as m2

app = Flask(__name__)
CORS(app)

spacy_model = spacy.load("en_core_web_sm")
matcher = Matcher(spacy_model.vocab)

yake_extractor = Resume.load_yake_extractor()

ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

app.config['UPLOAD_FOLDER'] = 'uploads'

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/score')
def get_resume_score():
    return render_template('score.html')

@app.route('/resume_builder')
def get_resume():
    return render_template('resume_builder.html')

@app.route('/process_files', methods=['POST'])
def process_files():
    if 'resume' not in request.files or 'job_description' not in request.files:
        return jsonify({"error": "Please upload both resume and job description files."})

    resume_file = request.files['resume']
    job_description_file = request.files['job_description']

    if resume_file.filename == '' or job_description_file.filename == '':
        return jsonify({"error": "Please select both resume and job description files."})
    if allowed_file(resume_file.filename) and allowed_file(job_description_file.filename):
        # Save uploaded files
        resume_filename = secure_filename(resume_file.filename)
        job_description_filename = secure_filename(job_description_file.filename)
        resume_path = os.path.join(app.config['UPLOAD_FOLDER'], resume_filename)
        job_description_path = os.path.join(app.config['UPLOAD_FOLDER'], job_description_filename)
        resume_file.save(resume_path)
        job_description_file.save(job_description_path)

        # Extract text from PDF files
        resume_text = extract_text_from_pdf(resume_path)
        job_description_text = extract_text_from_pdf(job_description_path)
        resume = Resume(jd=job_description_text,res=resume_text)
        all_keywords, all_skills = resume.extract_all_job_keywords(yake_extractor=yake_extractor)
        # print(all_keywords)
        reskey=resume.extract_all_resume_keywords(yake_extractor=yake_extractor)
        resumekeywords,included_keywords, missing_keywords = resume.extract_included_and_missing_keywords(
            matcher=matcher, spacy_model=spacy_model ,yake_extractor=yake_extractor
        )
        if 'R' in all_keywords:
            all_keywords.remove('R')
        if 'R' in included_keywords:
            included_keywords.remove('R')
        if 'R' in all_skills:
            all_skills.remove('R')
        included_keywords=set(included_keywords)
        missing_keywords=set(missing_keywords)
        all_keywords=set(all_keywords)
        all_skills=set(all_skills)
        # print("included")
        # print(included_keywords)
        # print("excluded")
        # print(missing_keywords)
        # print(all_keywords)
        # print(all_skills)
    #     highlighted_job_description = Resume.get_highlighted_keywords_in_job_description(
    #     job_description=job_description_text,
    #     job_keywords=all_keywords,
    # )
        with open(resume_path, 'rb') as file:
            data = ResumeParser(file.name).get_extracted_data()
        score,keyscore=resume.get_resume_keyword_score(data)
        # if(data['total_experience']>0 or (data['experience']!=None)):
        #     keyscore=keyscore+(.4*len(data['experience']))
        #     print(keyscore)
        high_job_description=highlight_keywords(job_description_text,missing_keywords)

        #job role prediction
        pred=m.role(resume_text)
        print(pred)


        return render_template('scoreout.html',extracted_jd_words=all_keywords,common_keywords=included_keywords,job_description=high_job_description,score=(score*100),keyscore=int(keyscore*100),skills=all_skills,pred=pred)
    
@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    jd=request.form['jd']
    if file and file.filename.endswith('.csv'):
        newname="res.csv"
        filename = os.path.join(app.config['UPLOAD_FOLDER'], newname)
        file.save(filename)
    df = pd.read_csv("uploads/res.csv", encoding='ISO-8859-1')
    new_column_names = ['name', 'resumes']
    df.columns = new_column_names
    df.to_csv("uploads/res.csv", index=False)
    m.process(jd)
    sortedcsv=pd.read_csv('sorted.csv', encoding='ISO-8859-1')
    return render_template('result.html',data=sortedcsv.to_html())

@app.route('/download', methods=['GET'])
def download_file():
    # Assuming your CSV file name is 'output.csv' in the 'uploads' folder
    file_path = 'sorted.csv'

    # Send the CSV file to the user for download
    return send_file(file_path, as_attachment=True)    



def highlight_keywords(job_description, missing_keywords):
    highlighted_description = job_description
    for keyword in missing_keywords:
        highlighted_description = highlighted_description.replace(keyword, f'<span class="highlight">{keyword}</span>')
    return highlighted_description

def extract_text_from_pdf(file_path):
    pdf_reader = PdfReader(file_path)
    pdf_text = ''
    for page in pdf_reader.pages:
        pdf_text += page.extract_text()
    return pdf_text



if __name__ == '__main__':
    app.run(debug=True)