from single_agent.transcript import TranscriptManager

t = TranscriptManager()

t.add("Hello my name is Sachin")

t.add("I love artificial intelligence")

t.add("I am building an interview analyzer")

print(t.get_transcript())

print("Words :", t.total_words())