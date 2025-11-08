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

    words_in_job_text = job_text.lower().replace('\n', ' ').split()
    words_in_both = []

    with open(path, 'r') as file:
        lines = file.read().split('\n')
        for line in lines:
            keyword = line.strip().lower()
            if keyword and keyword in words_in_job_text:
                words_in_both.append(keyword)

    return words_in_both


if __name__ == '__main__':
    job_text = """
    Looking for a Software Engineer Intern with Python, SQL, data analysis, REST APIs, Git, and Linux.
    Experience with Pandas/Numpy preferred. Communication and teamwork are important.
    """
    resume_text = pdf_to_text('vk_main.pdf')
    df = normalize(resume_text,job_text)
    print(df)
    print(df.sum(axis=1))


    x = find_key_words = ('keywords.txt', job_text)
    print(x)



