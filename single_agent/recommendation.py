class RecommendationEngine:

    def process(
        self,
        confidence,
        eye,
        posture,
        smile,
        speech,
        fillers,
    ):

        strengths = []
        improvements = []

        # ---------------- Eye Contact ----------------
        if eye["percentage"] >= 90:
            strengths.append("Excellent eye contact throughout the interview.")
        elif eye["percentage"] >= 75:
            strengths.append("Good eye contact.")
        else:
            improvements.append("Maintain eye contact with the interviewer.")

        # ---------------- Smile ----------------
        if smile["expression"] == "Natural Smile":
            strengths.append("Natural smile creates a positive impression.")
        else:
            improvements.append("Smile naturally while answering.")

        # ---------------- Posture ----------------
        if posture["posture"] == "Good":
            strengths.append("Professional sitting posture.")
        else:
            improvements.append("Sit straight and avoid leaning.")

        # ---------------- Speech ----------------
        if speech["status"] == "Good":
            strengths.append("Speaking speed is appropriate.")
        else:
            improvements.append("Maintain a moderate speaking speed.")

        # ---------------- Fillers ----------------
        if fillers["rating"] in ["Excellent", "Good"]:
            strengths.append("Very few filler words.")
        else:
            improvements.append("Reduce filler words such as 'um', 'like', and 'actually'.")

        # ---------------- Overall ----------------
        if confidence["rating"] == "Excellent":
            strengths.append("Excellent overall interview confidence.")
        elif confidence["rating"] == "Good":
            strengths.append("Good overall interview confidence.")
        else:
            improvements.append("Practice mock interviews regularly.")

        return {
            "strengths": strengths,
            "improvements": improvements
        }