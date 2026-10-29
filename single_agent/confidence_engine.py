class ConfidenceEngine:
    def __init__(self):
        pass

    def calculate(self, video_data, speech_data, latest_eval):
        # Base confidence starts strong, assuming good behavior until proven otherwise
        score = 80.0
        
        # 1. Eye Contact
        eye_data = video_data.get("eye_contact", {})
        eye_perc = eye_data.get("percentage", 0)
        if eye_perc > 80:
            score += 5
        elif eye_perc < 50:
            score -= 10
            
        # 2. Smile
        smile_data = video_data.get("smile", {})
        if smile_data.get("expression") == "Smile":
            score += 5
            
        # 3. Posture
        posture_data = video_data.get("posture", {})
        if posture_data.get("posture") == "Good":
            score += 5
        else:
            score -= 5
            
        # 4. Speech Speed (WPM)
        wpm = speech_data.get("wpm", 0)
        if 110 <= wpm <= 150:
            score += 5
        elif wpm > 0 and (wpm < 100 or wpm > 160):
            score -= 5
            
        # 5. Fillers
        fillers = speech_data.get("fillers", 0)
        if fillers > 2:
            score -= (fillers * 1.5)
            
        # 6. Long Pauses
        pauses = speech_data.get("long_pauses", 0)
        if pauses > 0:
            score -= (pauses * 3)
            
        # 7. Gemini Communication Score
        if latest_eval and "communication_score" in latest_eval:
            gemini_score = latest_eval["communication_score"]
            if gemini_score >= 85:
                score += 5
            elif gemini_score < 60:
                score -= 10
                
        # Clamp score between 0 and 100
        score = max(0.0, min(100.0, score))
        
        rating = "Needs Improvement"
        if score >= 85:
            rating = "Excellent"
        elif score >= 70:
            rating = "Good"
        elif score >= 50:
            rating = "Average"
            
        return round(score, 1), rating