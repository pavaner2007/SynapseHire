import threading
import queue
from single_agent.answer_evaluator import AnswerEvaluator

class AIWorker(threading.Thread):
    def __init__(self, in_queue, out_queue):
        super().__init__()
        self.daemon = True
        self.running = False
        self.in_queue = in_queue
        self.out_queue = out_queue
        self.evaluator = AnswerEvaluator()

    def run(self):
        self.running = True
        while self.running:
            try:
                # Wait for a request with a timeout so we can check self.running
                request = self.in_queue.get(timeout=0.5)
                question_text, answer_text = request
                
                if answer_text.strip():
                    eval_data = self.evaluator.evaluate(question_text, answer_text)
                    self.out_queue.put((question_text, answer_text, eval_data))
                    
                self.in_queue.task_done()
            except queue.Empty:
                continue

    def stop(self):
        self.running = False
