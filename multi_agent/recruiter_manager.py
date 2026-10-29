import os
import json
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

class RecruiterManager:
    def __init__(self, api_key: str = None):
        if api_key is None:
            api_key = os.getenv("GROQ_API_KEY")
        self.api_key = api_key
        self.model = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
        self.client = Groq(api_key=api_key) if api_key else None

    def evaluate_candidate(self, jd: str, resume: str, tech_score: float, hr_score: float, gd_score: float) -> str:
        if not self.client:
            return "### 🛑 System Error\nAPI Key missing. Cannot evaluate candidate."

        prompt = f"""
        You are the Final Recruiter Agent in an AI-driven multi-agent interview pipeline.
        You must evaluate a candidate for the following Job Description (JD) using their provided Resume and their performance scores from 3 rigorous interview stages.

        **Job Description:**
        {jd}

        **Candidate Resume (Extracted Text):**
        {resume}

        **Candidate Pipeline Scores (0-100):**
        - Technical Interview Score: {tech_score:.1f}
        - HR/Behavioral Interview Score: {hr_score:.1f}
        - Group Discussion (Debate) Score: {gd_score:.1f}

        **Your Task:**
        Evaluate if the candidate is a strong fit for the role. Make a definitive "RECRUITED" or "NOT RECRUITED" decision.
        Write a highly professional and decorative evaluation report using Markdown.
        
        Use the following structure exactly:
        # 📊 Final Recruitment Decision
        ## 📋 Pipeline Summary
        (Briefly analyze their scores and how they map to the role)
        
        ## 🔍 Resume & JD Alignment
        (Briefly discuss if their background fits the requirements)
        
        ## 🏆 Final Verdict
        (Must clearly state **RECRUITED** or **NOT RECRUITED** with a definitive justification)

        Use emojis where appropriate. Do NOT output JSON, just pure Markdown text.
        """

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error in recruiter evaluation: {e}")
            return "### ⚠️ Error evaluating candidate.\nPlease try again."
