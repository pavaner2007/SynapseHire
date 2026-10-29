import os
import json
import time
import re
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

class GDManager:
    def __init__(self, api_key: str = None):
        if api_key is None:
            api_key = os.getenv("GROQ_API_KEY")
        self.api_key = api_key
        # Use a fast model with JSON mode where needed
        self.model = os.getenv("GROQ_FAST_MODEL", "openai/gpt-oss-20b")
        self.client = Groq(api_key=api_key) if api_key else None
        
        self.transcript = []
        self.topic = ""
        
        self.judge = "Judge AI"
        self.competitors = ["AI Alex", "AI Jordan", "AI Taylor"]
    
    def reset(self):
        self.transcript = []
        self.topic = ""

    def format_transcript(self):
        if not self.transcript:
            return "No discussion yet."
        return "\n".join([f"{entry['speaker']}: {entry['text']}" for entry in self.transcript])

    def start_discussion(self):
        if not self.client:
            self.topic = "The Future of Artificial Intelligence"
            msg = f"Welcome everyone. Today's topic is '{self.topic}'. Let's begin the group discussion. User, what are your initial thoughts?"
            self.transcript.append({"speaker": self.judge, "text": msg})
            return msg, self.topic

        prompt = """
        You are the Judge of a technical group discussion. 
        Your task is to generate a random, thought-provoking technical topic (e.g., Remote Work vs Office, AI in Healthcare, Monolith vs Microservices).
        Then, provide a brief opening statement welcoming the 4 participants (User, AI Alex, AI Jordan, AI Taylor) and announcing the topic. End by asking the User for their initial thoughts.
        
        Output MUST be valid JSON:
        {"topic": "The chosen topic", "opening_statement": "The exact words the judge will speak."}
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                response_format={"type": "json_object"},
                messages=[{"role": "user", "content": prompt}]
            )
            content = response.choices[0].message.content
            
            # Robust JSON extraction
            match = re.search(r'\{[\s\S]*\}', content)
            if match:
                result = json.loads(match.group(0))
            else:
                result = json.loads(content)
            
            self.topic = result.get("topic", "General Tech Discussion")
            opening = result.get("opening_statement", "Welcome to the group discussion. Let's begin.")
        except Exception as e:
            print(f"Error starting GD: {e}\nContent was: {content if 'content' in locals() else 'None'}")
            self.topic = "The Future of Artificial Intelligence"
            opening = f"Welcome everyone. Today's topic is '{self.topic}'. Let's begin. User, what do you think?"

        self.transcript.append({"speaker": self.judge, "text": opening})
        return opening, self.topic

    def process_turn(self, speaker_name, text):
        self.transcript.append({"speaker": speaker_name, "text": text})
        
        if not self.client:
            reply = "I agree with your point."
            self.transcript.append({"speaker": "AI Alex", "text": reply})
            return {"speaker": "AI Alex", "reply": reply}

        transcript_str = self.format_transcript()
        
        prompt = f"""
        You are orchestrating a fierce technical group discussion.
        Topic: {self.topic}
        
        Participants:
        - User (Human)
        - AI Alex (Competitor: highly argumentative, looks for flaws in logic)
        - AI Jordan (Competitor: deeply technical, cites edge cases and performance issues)
        - AI Taylor (Competitor: pragmatic, challenges real-world feasibility and costs)
        
        Current Transcript:
        {transcript_str}
        
        Your tasks:
        1. Select the next speaker from the AI Competitors (AI Alex, AI Jordan, AI Taylor). 
           CRITICAL: You MUST pick an AI who has NOT spoken recently! Rotate the speakers so everyone participates equally.
        2. Generate a 2-3 sentence response for that AI. 
           CRITICAL: The AI MUST fiercely debate, disagree, or challenge the User's most recent point. Do NOT agree with the User. Point out flaws, bring up complex edge cases, and make the discussion very challenging. Do NOT repeat previous points.
        
        Output MUST be valid JSON:
        {{"speaker": "Name of AI", "reply": "The exact words they speak"}}
        """
        
        try:
            sys_prompt = prompt + "\n\nCRITICAL: Output ONLY valid JSON."
            response = self.client.chat.completions.create(
                model=self.model,
                response_format={"type": "json_object"},
                messages=[{"role": "user", "content": sys_prompt}]
            )
            content = response.choices[0].message.content
            
            match = re.search(r'\{[\s\S]*\}', content)
            if match:
                result = json.loads(match.group(0))
            else:
                result = json.loads(content)
                
            next_speaker = result.get("speaker", "AI Alex")
            reply = result.get("reply", "That's an interesting perspective.")
        except Exception as e:
            print(f"Error processing GD turn: {e}\nContent was: {content if 'content' in locals() else 'None'}")
            next_speaker = "AI Alex"
            reply = "I hear what you are saying, but we must also consider the performance implications."
            
        self.transcript.append({"speaker": next_speaker, "text": reply})
        return {"speaker": next_speaker, "reply": reply}

    def conclude_discussion(self):
        if not self.client:
            return "The 5 minutes are up. You all did well. The winner is the User!", 100

        transcript_str = self.format_transcript()
        
        prompt = f"""
        You are the Judge AI of a technical group discussion. The 5 minutes are up.
        Topic: {self.topic}
        
        Transcript:
        {transcript_str}
        
        Your task:
        1. Evaluate the arguments made by all participants.
        2. Announce the winner (User, AI Alex, AI Jordan, or AI Taylor).
        3. Give a brief summary of why they won and a critique of the User's performance.
        4. Give a numerical score (0-100) for the User's overall performance.
        
        Output MUST be valid JSON with the following keys:
        - "verdict": The exact words the Judge will speak. Format this beautifully using Markdown (bolding, emojis, sections).
        - "user_score": An integer from 0 to 100.
        """
        try:
            sys_prompt = prompt + "\n\nCRITICAL: Output ONLY valid JSON."
            response = self.client.chat.completions.create(
                model=self.model,
                response_format={"type": "json_object"},
                messages=[{"role": "user", "content": sys_prompt}]
            )
            content = response.choices[0].message.content
            
            match = re.search(r'\{[\s\S]*\}', content)
            if match:
                result = json.loads(match.group(0))
            else:
                result = json.loads(content)
                
            verdict = result.get("verdict", "The discussion has ended. Excellent points were made by everyone.")
            user_score = result.get("user_score", 50)
        except Exception as e:
            print(f"Error concluding GD: {e}\nContent was: {content if 'content' in locals() else 'None'}")
            verdict = "The discussion has ended. Excellent points were made by everyone. The User is the winner!"
            user_score = 100
            
        self.transcript.append({"speaker": self.judge, "text": verdict})
        return verdict, user_score
