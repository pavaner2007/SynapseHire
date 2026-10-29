import random

class QuestionManager:
    def __init__(self, mode="sequential"):
        self.mode = mode
        
        self.hr_questions = [
            "Tell me about yourself.",
            "Why do you want to work here?",
            "Where do you see yourself in five years?",
            "What are your greatest strengths and weaknesses?",
            "Describe a challenge you faced and how you handled it."
        ]
        
        self.tech_questions = [
            "Can you explain the difference between processes and threads?",
            "What is a REST API?",
            "Explain the concept of object-oriented programming.",
            "How do you handle error logging and debugging?",
            "What is version control and why is it important?"
        ]
        
        self.behavioral_questions = [
            "Tell me about a time you made a mistake at work.",
            "How do you prioritize multiple deadlines?",
            "Describe a situation where you had to work with a difficult team member.",
            "Give an example of a time you showed leadership.",
            "How do you handle constructive criticism?"
        ]
        
        self.all_questions = self.hr_questions + self.tech_questions + self.behavioral_questions
        self.active_questions = self.all_questions.copy()
        
        self.current_index = 0
        
        if self.mode == "random":
            random.shuffle(self.active_questions)

    def current_question(self):
        if not self.active_questions:
            return "No questions available."
        
        if self.current_index >= len(self.active_questions):
            return "Interview Complete."
            
        return self.active_questions[self.current_index]

    def next_question(self):
        self.current_index += 1
        return self.current_question()

    def previous_question(self):
        if self.current_index > 0:
            self.current_index -= 1
        return self.current_question()

    def reset(self, mode=None, category="all"):
        if mode:
            self.mode = mode
            
        if category == "hr":
            self.active_questions = self.hr_questions + self.behavioral_questions
        elif category == "tech":
            self.active_questions = self.tech_questions.copy()
        else:
            self.active_questions = self.all_questions.copy()
            
        self.current_index = 0
        
        if self.mode == "random":
            random.shuffle(self.active_questions)

    def add_follow_up(self, question: str):
        # Insert the follow up immediately after the current question
        if self.current_index + 1 < len(self.active_questions):
            self.active_questions.insert(self.current_index + 1, question)
        else:
            self.active_questions.append(question)
