# ============================================================
# AI RESUME BUILDER & JOB RECOMMENDATION SYSTEM
# Google Colab Version
# ============================================================


# ============================================================
# 1. INSTALL REQUIRED LIBRARIES
# ============================================================




# ============================================================
# 2. IMPORT LIBRARIES
# ============================================================

import os
import pandas as pd
import gradio as gr

from getpass import getpass
from groq import Groq


# ============================================================
# 3. ENTER GROQ API KEY
# ============================================================

os.environ["GROQ_API_KEY"] = getpass("Enter your Groq API Key: ")

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY")
)


# ============================================================
# 4. TEST GROQ API
# ============================================================

response = client.chat.completions.create(
    model="openai/gpt-oss-120b",
    messages=[
        {
            "role": "system",
            "content": "You are an expert career assistant."
        },
        {
            "role": "user",
            "content": "What skills are important for a Python backend developer?"
        }
    ],
    temperature=0.3
)

print(response.choices[0].message.content)


# ============================================================
# 5. REUSABLE GROQ FUNCTION
# ============================================================

def ask_groq(
    prompt,
    system_prompt="You are a helpful career assistant."
):

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3
    )

    return response.choices[0].message.content


# ============================================================
# 6. TEST GROQ FUNCTION
# ============================================================

answer = ask_groq(
    "Create a professional summary for a Python developer with 2 years of experience."
)

print(answer)


# ============================================================
# 7. SAMPLE USER PROFILE
# ============================================================

user_profile = {
    "name": "Fatima Noor",
    "email": "fatima@example.com",
    "phone": "+92 300 1234567",
    "location": "Karachi, Pakistan",
    "education": "BS Computer Science",
    "skills": [
        "Python",
        "Pandas",
        "NumPy",
        "SQL",
        "Machine Learning",
        "Scikit-learn"
    ],
    "experience": "Internship at ABC Software working on Python data processing.",
    "projects": "Customer churn prediction project using Python and Scikit-learn.",
    "certifications": "Google Data Analytics",
    "target_role": "Data Scientist",
    "years_experience": 1,
    "preferred_location": "Remote"
}


# ============================================================
# 8. RESUME GENERATOR
# ============================================================

def generate_resume(profile):

    prompt = f"""
Create a professional, ATS-friendly resume using the information below.

Candidate Name:
{profile.get("name", "")}

Email:
{profile.get("email", "")}

Phone:
{profile.get("phone", "")}

Location:
{profile.get("location", "")}

Education:
{profile.get("education", "")}

Skills:
{", ".join(profile.get("skills", []))}

Work Experience:
{profile.get("experience", "")}

Projects:
{profile.get("projects", "")}

Certifications:
{profile.get("certifications", "")}

Target Role:
{profile.get("target_role", "")}

Years of Experience:
{profile.get("years_experience", 0)}

Create the resume with these sections:

1. Professional Summary
2. Skills
3. Work Experience
4. Projects
5. Education
6. Certifications

Make the content professional and concise.

Do not invent companies, degrees, certifications, dates,
or other major facts that were not provided.

Use clean Markdown formatting.
"""

    return ask_groq(
        prompt,
        system_prompt="You are an expert professional resume writer and ATS optimization specialist."
    )


# ============================================================
# 9. TEST RESUME GENERATOR
# ============================================================

test_resume = generate_resume(user_profile)

print(test_resume)


# ============================================================
# 10. CREATE SAMPLE JOB DATASET
# ============================================================

jobs = pd.DataFrame([
    {
        "job_id": 1,
        "title": "Python Developer",
        "company": "ABC Tech",
        "location": "Remote",
        "skills": "Python,Django,SQL,Git",
        "description": "Backend application development"
    },
    {
        "job_id": 2,
        "title": "Data Analyst",
        "company": "XYZ Analytics",
        "location": "Karachi",
        "skills": "Python,SQL,Pandas,Excel",
        "description": "Data analysis and reporting"
    },
    {
        "job_id": 3,
        "title": "Machine Learning Engineer",
        "company": "AI Labs",
        "location": "Remote",
        "skills": "Python,Machine Learning,TensorFlow,SQL",
        "description": "Machine learning model development"
    }
])


# ============================================================
# 11. SAVE JOB DATASET
# ============================================================

jobs.to_csv(
    "jobs.csv",
    index=False
)

jobs = pd.read_csv("jobs.csv")

print(jobs)


# ============================================================
# 12. SKILL ALIASES
# ============================================================

SKILL_ALIASES = {
    "ml": "machine learning",
    "ai": "artificial intelligence",
    "js": "javascript",
    "postgres": "postgresql",
    "reactjs": "react",
    "node": "node.js",
    "py": "python"
}


def normalize_skill(skill):

    skill = skill.lower().strip()

    return SKILL_ALIASES.get(
        skill,
        skill
    )


# ============================================================
# 13. NORMALIZE USER SKILLS
# ============================================================

def normalize_user_skills(skills):

    return {
        normalize_skill(skill)
        for skill in skills
        if skill.strip()
    }


# ============================================================
# 14. NORMALIZE JOB SKILLS
# ============================================================

def normalize_skills(skills):

    return {
        normalize_skill(skill)
        for skill in skills.split(",")
        if skill.strip()
    }


# ============================================================
# 15. CALCULATE JOB MATCH
# ============================================================

def calculate_match(
    user_skills,
    job_skills
):

    job_skills_set = normalize_skills(
        job_skills
    )

    matched = user_skills.intersection(
        job_skills_set
    )

    if not job_skills_set:

        return (
            0,
            [],
            []
        )

    score = (
        len(matched)
        /
        len(job_skills_set)
    ) * 100

    missing = (
        job_skills_set
        -
        user_skills
    )

    return (
        round(score, 2),
        list(matched),
        list(missing)
    )


# ============================================================
# 16. RECOMMEND JOBS
# ============================================================

def recommend_jobs(
    user_skills,
    jobs,
    top_n=5
):

    recommendations = []

    for _, job in jobs.iterrows():

        score, matched, missing = calculate_match(
            user_skills,
            job["skills"]
        )

        recommendations.append({

            "title": job["title"],

            "company": job["company"],

            "location": job["location"],

            "match": score,

            "matched_skills": ", ".join(
                matched
            ),

            "missing_skills": ", ".join(
                missing
            ),

            "description": job["description"]
        })


    result = pd.DataFrame(
        recommendations
    )


    result = result.sort_values(
        by="match",
        ascending=False
    )


    return result.head(top_n)


# ============================================================
# 17. TEST JOB RECOMMENDATION
# ============================================================

test_user_skills = normalize_user_skills(
    user_profile["skills"]
)

test_recommendations = recommend_jobs(
    test_user_skills,
    jobs
)

print(test_recommendations)


# ============================================================
# 18. AI JOB RECOMMENDATION EXPLANATION
# ============================================================

def explain_job_recommendation(
    profile,
    job
):

    prompt = f"""
Analyze why this job is suitable for the candidate.

Candidate:

Target Role:
{profile.get("target_role", "")}

Skills:
{", ".join(profile.get("skills", []))}

Experience:
{profile.get("experience", "")}

Job:

Title:
{job.get("title", "")}

Company:
{job.get("company", "")}

Location:
{job.get("location", "")}

Required Skills:
{job.get("skills", "")}

Description:
{job.get("description", "")}

Explain:

1. Why this job matches
2. Candidate's relevant skills
3. Missing skills
4. What the candidate should learn

Keep the answer concise and practical.
"""

    return ask_groq(prompt)


# ============================================================
# 19. SKILL GAP ANALYSIS
# ============================================================

def generate_skill_gap(
    profile,
    recommendations
):

    prompt = f"""
Analyze the candidate's skill gaps.

Candidate Skills:
{", ".join(profile.get("skills", []))}

Target Role:
{profile.get("target_role", "")}

Recommended Jobs:

{recommendations.to_string(index=False)}

Identify:

1. Skills the candidate already has
2. Important missing skills
3. Top skills they should learn next
4. Recommended learning priorities

Keep the answer concise and useful.
"""

    return ask_groq(prompt)


# ============================================================
# 20. CAREER DOMAIN DETECTOR
# ============================================================

def detect_career_domain(
    skills
):

    prompt = f"""
Analyze these skills:

{skills}

Determine:

1. Most suitable career domain
2. Top 5 suitable job roles
3. Why these roles fit
4. Important missing skills

Return a concise answer.
"""

    return ask_groq(
        prompt,
        system_prompt="You are an expert career counselor and technology recruiter."
    )


# ============================================================
# 21. MAIN APPLICATION FUNCTION
#
# IMPORTANT:
# This function is defined BEFORE the Gradio Blocks.
# ============================================================

def process_application(
    name,
    email,
    phone,
    location,
    education,
    skills,
    experience,
    projects,
    certifications,
    target_role,
    years_experience
):

    # --------------------------------------------------------
    # Convert skills text into a list
    # --------------------------------------------------------

    skill_list = [
        x.strip()
        for x in skills.split(",")
        if x.strip()
    ]


    # --------------------------------------------------------
    # Create candidate profile
    # --------------------------------------------------------

    profile = {

        "name": name,

        "email": email,

        "phone": phone,

        "location": location,

        "education": education,

        "skills": skill_list,

        "experience": experience,

        "projects": projects,

        "certifications": certifications,

        "target_role": target_role,

        "years_experience": years_experience
    }


    # --------------------------------------------------------
    # Generate Resume
    # --------------------------------------------------------

    resume = generate_resume(
        profile
    )


    # --------------------------------------------------------
    # Normalize Skills
    # --------------------------------------------------------

    user_skills = normalize_user_skills(
        skill_list
    )


    # --------------------------------------------------------
    # Find Recommended Jobs
    # --------------------------------------------------------

    recommendations = recommend_jobs(
        user_skills,
        jobs,
        top_n=5
    )


    # --------------------------------------------------------
    # Return results
    # --------------------------------------------------------

    return (
        resume,
        recommendations
    )


# ============================================================
# 22. GRADIO APPLICATION
# ============================================================

with gr.Blocks(
    title="AI Resume Builder & Job Finder"
) as demo:


    # --------------------------------------------------------
    # HEADER
    # --------------------------------------------------------

    gr.Markdown(
        """
        # 🚀 AI Resume Builder & Job Finder

        Build an AI-powered ATS-friendly resume
        and discover suitable job opportunities.
        """
    )


    # --------------------------------------------------------
    # INPUT SECTION
    # --------------------------------------------------------

    with gr.Row():


        # ====================================================
        # LEFT COLUMN
        # ====================================================

        with gr.Column():

            name = gr.Textbox(
                label="Full Name",
                placeholder="Enter your full name"
            )


            email = gr.Textbox(
                label="Email",
                placeholder="example@email.com"
            )


            phone = gr.Textbox(
                label="Phone",
                placeholder="+92 300 1234567"
            )


            location = gr.Textbox(
                label="Location",
                placeholder="Karachi, Pakistan"
            )


            education = gr.Textbox(
                label="Education",
                placeholder="BS Computer Science",
                lines=3
            )


            skills = gr.Textbox(
                label="Skills",
                placeholder="Python, SQL, Pandas, Machine Learning",
                lines=3
            )


        # ====================================================
        # RIGHT COLUMN
        # ====================================================

        with gr.Column():

            experience = gr.Textbox(
                label="Work Experience",
                placeholder="Describe your work experience",
                lines=6
            )


            projects = gr.Textbox(
                label="Projects",
                placeholder="Describe your projects",
                lines=6
            )


            certifications = gr.Textbox(
                label="Certifications",
                placeholder="Enter certifications",
                lines=3
            )


            target_role = gr.Textbox(
                label="Target Job Role",
                placeholder="Data Scientist"
            )


            years_experience = gr.Number(
                label="Years of Experience",
                value=0
            )


    # --------------------------------------------------------
    # BUTTON
    # --------------------------------------------------------

    generate_btn = gr.Button(
        "🚀 Generate Resume & Find Jobs",
        variant="primary"
    )


    # --------------------------------------------------------
    # OUTPUTS
    # --------------------------------------------------------

    resume_output = gr.Markdown(
        label="Generated Resume"
    )


    job_output = gr.Dataframe(
        label="Recommended Jobs",
        interactive=False
    )


    # ========================================================
    # IMPORTANT:
    # BUTTON EVENT MUST BE INSIDE THE BLOCK
    # ========================================================

    generate_btn.click(

        fn=process_application,

        inputs=[

            name,

            email,

            phone,

            location,

            education,

            skills,

            experience,

            projects,

            certifications,

            target_role,

            years_experience
        ],

        outputs=[

            resume_output,

            job_output
        ]
    )


# ============================================================
# 23. LAUNCH APPLICATION
#
# This can be OUTSIDE the Blocks context.
# ============================================================

demo.launch(
    share=True
)