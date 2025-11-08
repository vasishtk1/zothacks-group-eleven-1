"""
This file defines the FastAPI app for the API and all of its routes.
To run this API, use the FastAPI CLI
$ fastapi dev src/api.py
"""

import random

from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel
from state import job_state
from resume_parser import y, suggestions



# The app which manages all of the API routes
app = FastAPI()

class jobDescription(BaseModel):
    job_description: str
@app.post("/job-description/")
async def receive_description(job:jobDescription):
    job_state.job_text = job.job_description
    print("Received job description: ", job_state.job_text)
    return {"message":"Job description received"}



@app.get("/response")
async def get_response():
    
    return{"Score: ": y,
           "Suggestions: ": suggestions}

@app.post("/upload")
async def upload_resume(file: UploadFile = File(...)):
    """Receive a resume PDF upload."""
    contents = await file.read()
    # For now, just return a confirmation
    return {"filename": file.filename, "size": len(contents)}
