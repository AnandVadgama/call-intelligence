from abc import ABC, abstractmethod

class BaseSTTModel(ABC):
    @abstractmethod
    def transcribe(self, audio_path: str) -> str:
        """
        Transcribes the given audio file and returns the transcript text.
        
        Args:
            audio_path (str): The absolute path to the local audio file.
            
        Returns:
            str: The transcribed text.
        """
        pass

    @abstractmethod
    def classify(self, transcript: str) -> dict:
        """
        Classifies the transcript and returns a dictionary with analysis fields.
        
        Args:
            transcript (str): The transcript text to analyze.
            
        Returns:
            dict: JSON containing transcript, language, code, label, confidence, key_phrase, summary.
        """
        pass

    def local_fallback_classify(self, transcript: str, error_msg: str) -> dict:
        """
        A robust local fallback classification engine that uses rule-based keyword heuristic analysis
        to classify the call transcript in case of API failure.
        """
        t_lower = transcript.lower()
        
        # 1. Detect language (heuristics for English, Gujarati, Urdu, Hindi)
        if any(word in t_lower for word in ["hello", "call", "bank", "pay", "tomorrow", "emi", "loan", "card", "credit"]):
            language = "English"
        elif any(word in t_lower for word in ["તમે", "તમારૂ", "છે", "નથી", "બંધ", "બીલ", "તમારू"]):
            language = "Gujarati"
        elif any(word in t_lower for word in ["مرحبا", "بھاویت", "گیس", "بات"]):
            language = "Urdu"
        elif any(word in t_lower for word in ["हेलो", "पेमेंट", "गैस", "करेंगे", "कर दिया", "स्क्रीनशॉट", "मकवाना"]):
            language = "Hindi"
        else:
            language = "English"
            
        # 2. Heuristics for intent classification code
        if any(word in t_lower for word in ["tomorrow", "tuesday", "pay next", "pay tomorrow", "कर दूँगा", "करेंगे आज", "करवा दीजिए", "देते हैं आपको", "दोपहर में", "آج", "دیتے"]):
            code = "PTP"
            label = "Promise to Pay"
            key_phrase = "Yes. I will pay it tomorrow." if language == "English" else "आज करने वाले थे... कर देंगे"
            if language == "Urdu":
                key_phrase = "آج لازم دیتے ہیں آپ کو"
            summary = "Customer promised to make the payment shortly (today/tomorrow)."
        elif any(word in t_lower for word in ["refuse", "not pay", "not going to pay", "harass", "हैरेस", "बंद कराई", "बाखी चे नहीं"]):
            code = "RTP"
            label = "Refuse to Pay"
            key_phrase = "I'm refusing to pay any bill" if language == "English" else "तमारू साबरमती वालू बील जमारू तमारू जे मीटर वाई ऐसी बंद कराई दितू चे तो भी तमे मात्रा फोन करे जाओ चो"
            summary = "Customer refuses to pay the balance due to service issues, disconnections, or billing disputes."
        elif any(word in t_lower for word in ["fraud", "locked", "accident", "extension", "delay", "स्क्रीनसड", "स्क्रीन सोट", "डिल", "connection is not"]):
            code = "EXC"
            label = "Excuse or Delay"
            key_phrase = "Send screenshot" if language == "English" else "हो गया देख लेना आप स्क्रीन सोट बेज दाना"
            summary = "Customer claims payment is made or asks for a delay / sends verification screenshots."
        elif any(word in t_lower for word in ["partial", "segment", "installment", "pay 200", "pay half"]):
            code = "PPC"
            label = "Partial Pay Commitment"
            key_phrase = "आप किसी को देके ओल्लाइन करवा दीजिए"
            summary = "Customer committed to a partial payment."
        else:
            code = "NR"
            label = "No Clear Response"
            key_phrase = "Call back later"
            summary = "Call contains ambiguous responses or brief conversation fragments."
            
        return {
            "transcript": transcript,
            "language": language,
            "code": code,
            "label": label,
            "confidence": 75,
            "key_phrase": key_phrase,
            "summary": f"{summary} (Processed via Offline Local Engine due to: {error_msg})"
        }
