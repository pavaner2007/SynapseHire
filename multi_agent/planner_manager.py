import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

class PlannerManager:
    def __init__(self, api_key: str = None):
        if api_key is None:
            api_key = os.getenv("GROQ_API_KEY")
        self.api_key = api_key
        self.model = os.getenv("GROQ_FAST_MODEL", "openai/gpt-oss-20b")
        self.client = Groq(api_key=api_key) if api_key else None

    def generate_roadmap(self, jd: str, verdict_text: str) -> str:
        if not self.client:
            return "### 🛑 System Error\nAPI Key missing. Cannot generate roadmap."

        prompt = f"""
        You are the Planner Agent, a specialized AI coach focusing purely on Soft Skills and Communication.
        
        You have received the Final Recruiter Verdict for a candidate regarding the following Job Description (JD).
        
        **Job Description:**
        {jd}
        
        **Recruiter Verdict:**
        {verdict_text}
        
        **Your Task:**
        1. Analyze the verdict to determine if the candidate was RECRUITED or NOT RECRUITED.
        2. DO NOT comment on technical skills (e.g., coding, system design, databases). Focus exclusively on communication, confidence, argument structuring, body language, and debate skills.
        3. Create a Timeline Roadmap for the user:
           - If RECRUITED: Create a "Pre-Onboarding Soft-Skills Plan" (e.g., Week 1: Active Listening in Meetings, Week 2: Presenting Ideas Clearly).
           - If NOT RECRUITED: Explain strictly from a communication/soft-skills perspective why they might have fallen short, and create a "Skill Recovery Timeline" (e.g., Week 1: Confidence Building, Week 2: Structuring arguments under pressure).
           
        Format your response beautifully using Markdown.
        Use headings (##), bold text (**), bullet points, and emojis (📅, 🗣️, 💡, 🚀) to make the timeline visually appealing and highly encouraging. Do NOT output JSON.
        """

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error generating planner roadmap: {e}")
            return "### ⚠️ Error generating timeline.\nPlease try again."
