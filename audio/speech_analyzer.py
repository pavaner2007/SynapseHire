import re

class SpeechAnalyzer:
    def __init__(self):
        self.speaking_duration = 0.0 # in seconds
        self.total_words = 0
        self.total_sentences = 0
        self.long_pauses = 0
        
        self.consecutive_silence_chunks = 0
        self.chunk_duration = 1.0 # seconds per chunk
        
        # To track speaking consistency
        self.words_per_chunk_history = []

    def process_chunk(self, text, fillers_count=0):
        words = text.split()
        num_words = len(words)
        
        if num_words == 0:
            self.consecutive_silence_chunks += 1
            if self.consecutive_silence_chunks == 2: 
                # e.g., > 5s of silence is considered a long pause (if 2 chunks are silent = 10s)
                # Actually, 5 seconds is a long pause in an interview. So just 1 silent chunk could be a pause.
                self.long_pauses += 1
        else:
            self.consecutive_silence_chunks = 0
            self.speaking_duration += self.chunk_duration
            self.total_words += num_words
            self.words_per_chunk_history.append(num_words)
            
            # Simple sentence calculation
            sentences = re.split(r'[.!?]+', text)
            # filter empty strings from split
            sentences = [s for s in sentences if s.strip()]
            self.total_sentences += len(sentences) if sentences else 1

        return self.get_metrics(fillers_count)

    def get_metrics(self, fillers_count=0):
        wpm = 0
        if self.speaking_duration > 0:
            wpm = int((self.total_words / self.speaking_duration) * 60)
            
        avg_sentence_len = 0
        if self.total_sentences > 0:
            avg_sentence_len = round(self.total_words / self.total_sentences, 1)

        # Speaking speed rating
        speed_rating = "Good"
        if wpm > 0:
            if wpm < 110:
                speed_rating = "Too Slow"
            elif wpm > 150:
                speed_rating = "Too Fast"

        # Consistency
        consistency = "Stable"
        if len(self.words_per_chunk_history) > 3:
            recent = self.words_per_chunk_history[-3:]
            avg_recent = sum(recent) / len(recent)
            overall_avg = sum(self.words_per_chunk_history) / len(self.words_per_chunk_history)
            if avg_recent > overall_avg * 1.5:
                consistency = "Speeding Up"
            elif avg_recent < overall_avg * 0.5:
                consistency = "Slowing Down"

        # Overall Communication Rating
        comm_score = 100
        if speed_rating != "Good":
            comm_score -= 10
        comm_score -= (fillers_count * 2)
        comm_score -= (self.long_pauses * 5)
        
        if comm_score >= 90:
            comm_rating = "Excellent"
        elif comm_score >= 75:
            comm_rating = "Good"
        elif comm_score >= 60:
            comm_rating = "Average"
        else:
            comm_rating = "Needs Improvement"

        return {
            "duration": self.speaking_duration,
            "total_words": self.total_words,
            "wpm": wpm,
            "speed_rating": speed_rating,
            "long_pauses": self.long_pauses,
            "avg_sentence_length": avg_sentence_len,
            "consistency": consistency,
            "comm_rating": comm_rating,
            "comm_score": comm_score
        }
