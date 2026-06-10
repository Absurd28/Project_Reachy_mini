from transformers import pipeline
import logging

# Disable heavy logging from transformers
logging.getLogger("transformers").setLevel(logging.ERROR)

class NLPIntentParser:
    def __init__(self, model_name="valhalla/distilbart-mnli-12-1"):
        """
        Initializes a Zero-Shot Classification pipeline.
        Defaulting to a distilled model for better performance on Edge devices.
        """
        print(f"[*] Loading NLP Intent Classifier ({model_name})...")
        try:
            self.classifier = pipeline("zero-shot-classification", model=model_name)
            self.candidate_labels = ["medical distress", "routine confirmation", "casual greeting"]
            print("[+] NLP Classifier Ready.")
        except Exception as e:
            print(f"[!] NLP Classifier Failed to load: {e}")
            self.classifier = None

    def parse_intent(self, text):
        """
        Classifies the intent of the transcribed text.
        Returns the top label and its confidence score.
        """
        if not self.classifier:
            return "unknown", 0.0

        try:
            result = self.classifier(text, self.candidate_labels)
            top_label = result['labels'][0]
            score = result['scores'][0]
            return top_label, score
        except Exception as e:
            print(f"[!] Classification Error: {e}")
            return "error", 0.0

if __name__ == "__main__":
    # Quick Test
    parser = NLPIntentParser()
    test_phrases = [
        "I am in a lot of pain",
        "Yes, I took my medication",
        "Hello Reachy, how are you today?"
    ]
    for p in test_phrases:
        label, score = parser.parse_intent(p)
        print(f"Text: '{p}' | Intent: {label} ({score:.2f})")
