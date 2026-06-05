from fastapi import FastAPI, UploadFile, File
from pypdf import PdfReader
import google.generativeai as genai
import shutil
import os
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-2.5-flash")

app = FastAPI()

# Upload folder create if not exists
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.get("/")
def home():
    return {"message": "AI Interview Assistant Running"}


@app.post("/upload-resume/")
async def upload_resume(file: UploadFile = File(...)):

    # Save PDF
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Read PDF
    reader = PdfReader(file_path)

    resume_text = ""

    for page in reader.pages:
        text = page.extract_text()
        if text:
            resume_text += text

    return {
        "resume_pdf": file.filename,
        "message": "Resume uploaded successfully",
        "resume_text": resume_text[:2000]
    }

@app.post("/analyze-resume/")
async def analyze_resume(file: UploadFile = File(...)):

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    reader = PdfReader(file_path)

    resume_text = ""

    for page in reader.pages:
        text = page.extract_text()
        if text:
            resume_text += text

    skills = []

    skill_keywords = [
        "Python",
        "SQL",
        "Django",
        "FastAPI",
        "Machine Learning",
        "TensorFlow",
        "Scikit-learn",
        "Power BI",
        "Tableau",
        "Git",
        "GitHub",
        "REST API"
    ]

    for skill in skill_keywords:
        if skill.lower() in resume_text.lower():
            skills.append(skill)

    return {
        "skills_found": skills,
        "total_skills": len(skills)
    }

@app.post("/ai-resume-analysis/")
async def ai_resume_analysis(file: UploadFile = File(...)):

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    reader = PdfReader(file_path)

    resume_text = ""

    for page in reader.pages:
        text = page.extract_text()
        if text:
            resume_text += text

    prompt = f"""
    Analyze the following resume and provide:

    1. Professional Summary
    2. Top Strengths
    3. Weaknesses / Improvement Areas
    4. Recommended Job Roles
    5. 5 Interview Questions

    Resume:
    {resume_text}
    """

    response = model.generate_content(prompt)

    return {
        "analysis": response.text
    }

@app.post("/generate-interview-questions/")
async def generate_interview_questions(file: UploadFile = File(...)):

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    reader = PdfReader(file_path)

    resume_text = ""

    for page in reader.pages:
        text = page.extract_text()
        if text:
            resume_text += text

    prompt = f"""
    Based on the following resume, generate:

    1. 5 Python Interview Questions
    2. 5 SQL Interview Questions
    3. 5 Machine Learning Interview Questions
    4. 5 HR Interview Questions

    Resume:
    {resume_text}
    """

    response = model.generate_content(prompt)

    return {
        "interview_questions": response.text
    }

@app.post("/job-match-score/")
async def job_match_score(file: UploadFile = File(...)):

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    reader = PdfReader(file_path)

    resume_text = ""

    for page in reader.pages:
        text = page.extract_text()
        if text:
            resume_text += text

    prompt = f"""
    Analyze this resume and provide:

    1. Top 5 suitable job roles
    2. Job match score out of 100
    3. Missing skills
    4. Career improvement suggestions

    Resume:
    {resume_text}
    """

    response = model.generate_content(prompt)

    return {
        "job_analysis": response.text
    }

from pydantic import BaseModel
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base
from database import engine, SessionLocal

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    password = Column(String)

Base.metadata.create_all(bind=engine)

class UserRegister(BaseModel):
    username: str
    email: str
    password: str


@app.post("/register/")
def register(user: UserRegister):

    db = SessionLocal()

    new_user = User(
        username=user.username,
        email=user.email,
        password=user.password
    )

    db.add(new_user)
    db.commit()

    return {
        "message": "User Registered Successfully"
    }