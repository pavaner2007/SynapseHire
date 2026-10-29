import os
import json
import time
from dotenv import load_dotenv
from groq import Groq

class AnswerEvaluator:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("GROQ_API_KEY")
        if self.api_key:
            self.client = Groq(api_key=self.api_key)
            self.model = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
        else:
            self.client = None

    def evaluate(self, question: str, answer: str, metrics: dict = None, retries: int = 3) -> dict:
        if not self.client:
            return {"error": "GROQ_API_KEY not found in .env"}

        if not answer.strip():
            return {"error": "No answer provided"}

        metrics_str = f"\nCandidate Live Metrics (Use this to give feedback on body language and speech delivery):\n{json.dumps(metrics, indent=2)}\n" if metrics else ""

        prompt = f"""
        You are an expert HR Interview Evaluator. Evaluate the candidate's answer to the following interview question.
        
        Question: {question}
        Candidate Answer: {answer}
        {metrics_str}
        Provide a detailed evaluation structured exactly as a JSON object with the following keys:
        "technical_score" (int 0-100),
        "communication_score" (int 0-100),
        "grammar_score" (int 0-100),
        "confidence_score" (int 0-100),
        "relevance_score" (int 0-100),
        "overall_score" (int 0-100),
        "strengths" (list of strings),
        "weaknesses" (list of strings),
        "suggestions" (list of strings),
        "conversational_reply" (string, a short spoken response back to the candidate as if you are the interviewer talking to them, under 30 words. Include brief, encouraging feedback on their body language or speech delivery based on the metrics, if provided. Keep it conversational and natural.),
        "follow_up_question" (string, a relevant follow-up technical question based on the candidate's answer to probe their understanding deeper).
        """

        for attempt in range(retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    response_format={"type": "json_object"}
                )
                result = json.loads(response.choices[0].message.content)
                return result
            except Exception as e:
                if attempt == retries - 1:
                    return {"error": f"Evaluation failed after {retries} attempts: {str(e)}"}
                time.sleep(2)
        
        return {"error": "Evaluation failed"}

    def generate_report(self, evaluations: list, retries: int = 3) -> str:
        if not self.client:
            return "GROQ_API_KEY not found in .env"

        if not evaluations:
            return "No interview data to generate a report."

        eval_summary = json.dumps(evaluations, indent=2)

        prompt = f"""
        You are an expert HR Interview Evaluator. The interview has concluded. 
        Here are the evaluations of the candidate's answers throughout the session:
        {eval_summary}
        
        Write a concise, professional, and encouraging final interview report. 
        Format it nicely with Markdown. Include:
        - Overall Impression
        - Key Strengths
        - Areas for Improvement
        - Final Recommendation (e.g., Proceed to next round, Needs more practice).
        Keep it under 300 words.
        """

        for attempt in range(retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    response_format={"type": "text"}
                )
                return response.choices[0].message.content
            except Exception as e:
                if attempt == retries - 1:
                    return f"Report generation failed: {str(e)}"
                time.sleep(2)
        
        return "Report generation failed."

    def generate_resume_questions(self, resume_text: str, num_questions: int = 5, retries: int = 3) -> list:
        if not self.client:
            return ["Tell me about yourself.", "What are your strengths?"]

        prompt = f"""
        You are an expert technical interviewer. I will provide you with a candidate's resume.
        Your task is to generate exactly {num_questions} challenging, role-specific technical interview questions based strictly on their experience, projects, and skills.
        
        Output MUST be a valid JSON object with a single key "questions" containing a list of strings.
        Example: {{"questions": ["Question 1", "Question 2"]}}
        
        Resume:
        {resume_text}
        """

        for attempt in range(retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    response_format={"type": "json_object"}
                )
                result = json.loads(response.choices[0].message.content)
                questions = result.get("questions", [])
                if questions and isinstance(questions, list):
                    return questions
            except Exception as e:
                print(f"Failed to generate resume questions: {e}")
                time.sleep(2)
        
        return ["Could you explain your past experience?", "What is your strongest technical skill?"]

