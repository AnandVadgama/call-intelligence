import os
import json
from groq import Groq
import google.generativeai as genai
from .base import BaseSTTModel

class WhisperModel(BaseSTTModel):
    def __init__(self, model_size: str = "whisper-large-v3"):
        """
        Initialize the WhisperModel powered by Groq.
        
        Args:
            model_size (str): The Groq Whisper model ID. Defaults to 'whisper-large-v3'.
        """
        self.model_size = model_size

    def transcribe(self, audio_path: str) -> str:
        """
        Transcribes the audio file using Groq's Whisper API.
        """
        print(f"[WhisperModel-Groq] Initializing Groq client for model '{self.model_size}'...")
        api_key = os.getenv("GROQ_API_KEY", "").strip()
        if not api_key or "your_" in api_key.lower() or "placeholder" in api_key.lower():
            raise ValueError("GROQ_API_KEY is missing or invalid. Please check your sidebar or .env file.")
        
        try:
            client = Groq(api_key=api_key)
            
            print(f"[WhisperModel-Groq] Uploading and transcribing audio file: {audio_path}...")
            with open(audio_path, "rb") as audio_file:
                transcription = client.audio.transcriptions.create(
                    file=(os.path.basename(audio_path), audio_file.read()),
                    model=self.model_size
                )
            
            transcript = transcription.text.strip()
            print(f"[WhisperModel-Groq] Transcription complete: '{transcript[:100]}...'")
            return transcript
        except Exception as e:
            print(f"[WhisperModel-Groq] Error during Whisper transcription: {str(e)}")
            raise e

    def classify(self, transcript: str) -> dict:
        """
        Classifies the transcript.
        Tries to use Groq Llama-3 first (Single-API mode) if GROQ_API_KEY is available.
        Otherwise falls back to Gemini, and finally falls back to our local rule engine.
        """
        # Try Groq First (Single API Key Mode!)
        groq_api_key = os.getenv("GROQ_API_KEY", "").strip()
        if groq_api_key and "your_" not in groq_api_key.lower() and "placeholder" not in groq_api_key.lower():
            print("[WhisperModel-Groq] Performing text classification using Groq Llama-3 (Single API Mode)...")
            try:
                client = Groq(api_key=groq_api_key)
                
                prompt = (
                    "You are a payment collection AI. Analyze this call transcript and return ONLY a JSON object with fields: "
                    "transcript, language, code, label, confidence, key_phrase, summary. "
                    "Codes: PTP=Promise to Pay, RTP=Refuse to Pay, EXC=Excuse or Delay, "
                    "PPC=Partial Pay Commitment, NR=No Clear Response. "
                    "Return ONLY raw JSON, no markdown backticks, no extra text.\n\n"
                    f"Transcript:\n{transcript}"
                )
                
                chat_completion = client.chat.completions.create(
                    messages=[
                        {
                            "role": "user",
                            "content": prompt,
                        }
                    ],
                    model="llama3-70b-8192",
                    response_format={"type": "json_object"},
                    temperature=0.0
                )
                
                raw_text = chat_completion.choices[0].message.content.strip()
                result = json.loads(raw_text)
                
                # Make sure the transcript field is populated
                if "transcript" not in result or not result["transcript"]:
                    result["transcript"] = transcript
                
                print("[WhisperModel-Groq] Groq Llama-3 classification successful!")
                return result
                
            except Exception as e:
                print(f"[WhisperModel-Groq] Groq Llama-3 classification failed: {str(e)}. Trying Gemini fallback...")

        # Try Gemini Fallback
        gemini_api_key = os.getenv("GEMINI_API_KEY", "").strip()
        if gemini_api_key and "your_" not in gemini_api_key.lower() and "placeholder" not in gemini_api_key.lower():
            print("[WhisperModel-Groq] Performing text-based classification with Gemini...")
            try:
                genai.configure(api_key=gemini_api_key)
                model = genai.GenerativeModel("gemini-1.5-pro")
                
                prompt = (
                    "You are a payment collection AI. Analyze this call transcript and return ONLY a JSON object with fields: "
                    "transcript, language, code, label, confidence, key_phrase, summary. "
                    "Codes: PTP=Promise to Pay, RTP=Refuse to Pay, EXC=Excuse or Delay, "
                    "PPC=Partial Pay Commitment, NR=No Clear Response. "
                    "Return ONLY raw JSON, no markdown, no extra text.\n\n"
                    f"Transcript:\n{transcript}"
                )
                
                response = model.generate_content(
                    prompt,
                    generation_config={"response_mime_type": "application/json"}
                )
                
                raw_text = response.text.strip()
                if raw_text.startswith("```json"):
                    raw_text = raw_text.replace("```json", "", 1)
                if raw_text.endswith("```"):
                    raw_text = raw_text[:-3]
                raw_text = raw_text.strip()
                
                result = json.loads(raw_text)
                if "transcript" not in result or not result["transcript"]:
                    result["transcript"] = transcript
                    
                print("[WhisperModel-Groq] Gemini classification successful!")
                return result
            except Exception as e:
                print(f"[WhisperModel-Groq] Gemini classification failed: {str(e)}.")
        
        # Local Offline Engine Fallback (Zero crash guarantee!)
        print("[WhisperModel-Groq] API classification unavailable. Engaging local fallback heuristics engine...")
        return self.local_fallback_classify(transcript, "Groq/Gemini API issue or invalid keys")
