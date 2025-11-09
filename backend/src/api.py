"""
This file defines the FastAPI app for the API and all of its routes.
To run this API, use the FastAPI CLI
$ fastapi dev src/api.py
"""


import random,tempfile

from fastapi import FastAPI, File, UploadFile, Form
from pydantic import BaseModel
from state import job_state, resume_state
from resume_parser import returns_match_score_and_suggestions



# The app which manages all of the API routes
app = FastAPI()

class jobDescription(BaseModel):
    job_description: str
# @app.post("/job-description")
# async def receive_description(job:jobDescription):
#     job_state.job_text = job.job_description
#     print("Received job description: ", job_state.job_text)
#     return {"message":"Job description received"}

# @app.get("/response")
# async def get_response():
#     y, suggestions = returns_match_score_and_suggestions()
#     return{"Score: ": y,
#            "Suggestions: ": suggestions}



#Receives and saves file and job description text
@app.post("/upload")
async def upload_resume(file: UploadFile = File(...), job_description: str = Form(...)):
    job_state.job_text = job_description
    """Receive a resume PDF upload."""
    contents = await file.read()

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(contents)
        tmp_path = tmp.name
    resume_state.filename=tmp_path
    
    y, suggestions = returns_match_score_and_suggestions()
    return {"Score ": y,
           "Suggestions ": suggestions}

