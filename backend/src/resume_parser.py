from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd
from pypdf import PdfReader
from fastapi import FastAPI, Form
import string
from openai import OpenAI
import os
from state import job_state, resume_state

try:
    nlp = spacy.load("en_core_web_md")
except OSError:
    import subprocess, sys
    subprocess.run([sys.executable, "-m", "spacy", "download", "en_core_web_md"])
    nlp = spacy.load("en_core_web_md")


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

    

    #-------------------------
    resume_doc = nlp(resume_text)
    semantic_present = []
    semantic_missing = []

    for keyword in missing:
        keyword_doc = nlp(keyword)
        if resume_doc.similarity(keyword_doc) > 0.75:
            semantic_present.append(keyword)
        else:
            semantic_missing.append(keyword)

    # Merge exact present with semantic matches
    final_present = present.copy()  # start with exact matches

    # Only add semantically matched keywords if they aren’t already counted
    for kw in semantic_present:
        if kw not in final_present:
            final_present.append(kw)
    final_missing = semantic_missing
    if jd_hits:
        score = round(100 * len(final_present) / len(jd_hits))
    else:
        score = 0
    return {
        "jd_keywords_found": sorted(jd_hits),
        "resume_keywords_found": sorted(resume_hits),
        "present": final_present,
        "missing": final_missing,
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
    - Tell the user the missing keywords that need to be added after commas
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

def returns_match_score_and_suggestions():
    job_text = """
    Looking for a Software Engineer Intern with Python, SQL, data analysis, REST APIs, Git, and Linux.
    Experience with Pandas/Numpy preferred. Communication and teamwork are important. development activities digital marketing
    digital media distribution matrix mechanical engineering migration mobile modeling
    """
    job_text = job_state.job_text
    # resume_text = pdf_to_text('vk_main.pdf')
    resume_text = pdf_to_text(resume_state.filename)
    df = normalize(resume_text,job_text)
    # print(df)
    # print(df.sum(axis=1))


    # finding the words common in between keywords file and job description
    x = find_key_words('src/keywords.txt', job_text)
    # print(x)

    y = calculate_match_score('src/keywords.txt', job_text, resume_text)['match_score']
    temp = calculate_match_score('src/keywords.txt', job_text, resume_text)
    # print(y)


    # print('\n GPT Suggestions \n')
    suggestions = chat_with_gpt(
        job_text=job_text,
        resume_text=resume_text,
        present=temp["present"],
        missing=temp["missing"],
        extra=temp["extra"]
    )

    return y, suggestions
    # print("\n Resume Improvement Suggestions \n")
    # print(suggestions)
