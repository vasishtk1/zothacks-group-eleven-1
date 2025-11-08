# from PyPDF2 import PdfReader
# from pypdf import PdfReader
# import docx
# import os

# def read_pdf(path: str) -> str:
#     text = []
#     with open(path, 'rb') as f:
#         reader = PdfReader(f)
#         for p in reader.pages:
#             t = p.extract_text() or ''
#             text.append(t)
#     return '\n'.join(text)

# def read_docx(path: str) -> str:
#     d = docx.Document(path)
#     return "\n".join(p.text for p in d.paragraphs)

# def extract_text(path: str) -pip in> str:
#     lower = path.lower()
#     if lower.endswith(".pdf"):
#         return read_pdf(path)
#     elif lower.endswith(".docx"):
#         return read_docx(path)
#     else:
#         raise ValueError("Unsupported file type (use PDF or DOCX).")
    
#---------------------------------------------------

# import sklearn
from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd
from pypdf import PdfReader
from fastapi import FastAPI, Form
import string
from openai import OpenAI
import os
from state import job_state

def pdf_to_text(path: str) -> str:
    reader = PdfReader(path)

    corpus = ["job_description"]
    for page in reader.pages:
        text = page.extract_text()
        if text:  # make sure text extraction worked
            lines = text.splitlines()  # splits on '\n'
            for line in lines:
                corpus.extend(text.splitlines())
                # print(line)  

    return '\n'.join(corpus)

def normalize(resume_text: str, job_text: str) -> None:

    list_of_all_text = [resume_text, job_text]
    
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(list_of_all_text)
    feature_names = vectorizer.get_feature_names_out()
    df_tfidf = pd.DataFrame(tfidf_matrix.toarray(),
        columns=feature_names,
        index=["Resume", "Job Description"])
    return df_tfidf

def find_key_words(path: str, job_text: str) -> None:

    table = str.maketrans({ch: ' ' for ch in string.punctuation})
    job_norm = ' ' + ' '.join(job_text.lower().replace('\n', ' ').translate(table).split()) + ' '

    words_in_both = []
    with open(path, 'r') as file:
        lines = file.read().split('\n')
        for line in lines:
            keyword = line.strip().lower()
            kw = ' '.join(keyword.split())
            if kw and f' {kw} ' in job_norm:
                words_in_both.append(kw)
    return words_in_both


def calculate_match_score(keywords_path: str, job_text: str, resume_text: str):
    jd_hits = set(find_key_words(keywords_path, job_text))
    resume_hits = set(find_key_words(keywords_path, resume_text))

    present = sorted(jd_hits & resume_hits)     
    missing = sorted(jd_hits - resume_hits)       
    extra   = sorted(resume_hits - jd_hits)       

    if jd_hits:
        score = round(100 * len(present) / len(jd_hits))
    else:
        score = 0

    return {
        "jd_keywords_found": sorted(jd_hits),
        "resume_keywords_found": sorted(resume_hits),
        "present": present,
        "missing": missing,
        "extra": extra,
        "match_score": score
    }


client = OpenAI()
def build_suggestions_prompt(job_text: str,
                             resume_text: str,
                             present: list[str],
                             missing: list[str],
                             extra: list[str]) -> str:
    prompt = f'''You are a concise, practical resume coach for tech internships. 
    JOB DESCRIPTION : {job_text.strip()}
    RESUME: {resume_text}
    KEYWORD ANALYSIS: 
    - Present (in both JD & resume): {', '.join(present) or 'None'}
    - Missing (in JD but not in resume): {', '.join(missing) or 'None'}
    - Extra (in resume but not JD): {', '.join(extra) or 'None'}
    TASK: 
    - Give 4-5 targeted bullet suggestions to improve the resume for the job description.
    - For each suggestion, show an example edit/bullet that uses metrics or outcomes
    - Prioritize covering MISSING keywords naturally in the bullets
    - Keep each bullet under 25 words action-verb first '''
    return prompt

def chat_with_gpt(job_text: str,
                            resume_text: str,
                            present: list[str],
                            missing: list[str],
                            extra: list[str]) -> str:
    prompt = build_suggestions_prompt(job_text, resume_text, present, missing, extra)
    response = client.chat.completions.create(
        model = 'gpt-4o-mini',
        messages = [
            {"role": "system", "content": "You are a precise resume coach."},
            {"role": "user", "content": prompt}],
        temperature = 0.4
    )

    return response.choices[0].message.content

if __name__ == '__main__':
    job_text = """
    Looking for a Software Engineer Intern with Python, SQL, data analysis, REST APIs, Git, and Linux.
    Experience with Pandas/Numpy preferred. Communication and teamwork are important. development activities digital marketing
    digital media distribution matrix mechanical engineering migration mobile modeling
    """
    resume_text = pdf_to_text('vk_main.pdf')
    df = normalize(resume_text,job_text)
    # print(df)
    # print(df.sum(axis=1))


    # finding the words common in between keywords file and job description
    x = find_key_words('src/keywords.txt', job_text)
    # print(x)

    y = calculate_match_score('src/keywords.txt', job_text, resume_text)
    print(y)


    print('\n GPT Suggestions \n')
    suggestions = chat_with_gpt(
        job_text=job_text,
        resume_text=resume_text,
        present=y["present"],
        missing=y["missing"],
        extra=y["extra"]
    )

    print("\n Resume Improvement Suggestions \n")
    print(suggestions)
