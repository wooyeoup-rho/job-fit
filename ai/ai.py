from openai import OpenAI
import os
from dotenv import load_dotenv
from ai.utils import prompt_builder

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def analyze_fit(resume_text, job_description, additional_notes=""):
    output_instructions = """Return results in the following structure:
    
    [Analysis of fit]
    - Strengths
    - Gaps
    
    [Suggestions]
    - Resume improvements
    - Key points to focus on in a cover letter
    """
    prompt = prompt_builder(resume_text, job_description, additional_notes, output_instructions)

    response = client.responses.create(
        model="gpt-5-mini",
        reasoning={"effort": "low"},
        input=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.output_text

def generate_cover_letter(resume_text, job_description, additional_notes=""):
    output_instructions = "Write a cover letter for the job description using the provided details."
    prompt = prompt_builder(resume_text, job_description, additional_notes, output_instructions)

    response = client.responses.create(
        model="gpt-5",
        input=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.output_text