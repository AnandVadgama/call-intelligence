import os
import json
import google.generativeai as genai
from .base import BaseSTTModel

class GeminiModel(BaseSTTModel):
    def __init__(self):
        self._last_result = None
        self._last_audio_path = None

    def transcribe(self, audio_path: str) -> str:
        """
        Transcribes the audio file using Gemini 1.5 Pro.
        In GeminiModel, this performs BOTH transcription and classification in a single API call.
        """
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key or "your_" in api_key.lower() or "placeholder" in api_key.lower():
            raise ValueError("GEMINI_API_KEY is missing or contains an invalid placeholder. Please enter a valid key in the sidebar or update your .env file.")
        
        genai.configure(api_key=api_key)
        
        # Upload the audio file to the Gemini File API
        print(f"[GeminiModel] Uploading audio file: {audio_path}...")
        audio_file = genai.upload_file(path=audio_path)
        print(f"[GeminiModel] Upload completed. File URI: {audio_file.uri}")
        
        # Define the combined prompt
        prompt = (
            "You are a payment collection AI. Listen to the provided audio, transcribe it fully, "
            "analyze this call transcript and return ONLY a JSON object with fields: "
            "transcript, language, code, label, confidence, key_phrase, summary. "
            "Codes: PTP=Promise to Pay, RTP=Refuse to Pay, EXC=Excuse or Delay, "
            "PPC=Partial Pay Commitment, NR=No Clear Response. "
            "Return ONLY raw JSON, no markdown, no extra text."
        )
        
        try:
            model = genai.GenerativeModel("gemini-1.5-pro")
            print("[GeminiModel] Requesting Gemini 1.5 Pro for transcription and classification...")
            
            response = model.generate_content(
                [audio_file, prompt],
                generation_config={"response_mime_type": "application/json"}
            )
            
            # Clean up the file from the Gemini API as it's no longer needed
            print(f"[GeminiModel] Cleaning up API file: {audio_file.name}")
            genai.delete_file(audio_file.name)
            
            # Parse the JSON response
            raw_text = response.text.strip()
            # If the model wrapped it in markdown code blocks, strip them
            if raw_text.startswith("```json"):
                raw_text = raw_text.replace("```json", "", 1)
            if raw_text.endswith("```"):
                raw_text = raw_text[:-3]
            raw_text = raw_text.strip()
            
            result = json.loads(raw_text)
            
            # Cache the full result and the path to avoid duplicate calls during the cycle
            self._last_result = result
            self._last_audio_path = audio_path
            
            return result.get("transcript", "")
            
        except Exception as e:
            # Attempt cleanup in case of failure
            try:
                genai.delete_file(audio_file.name)
            except Exception:
                pass
            print(f"[GeminiModel] Error during execution: {str(e)}")
            raise e

    def classify(self, transcript: str) -> dict:
        """
        Returns the classification result. If we just transcribed this file,
        we return the cached result. Otherwise, we perform a fallback API call on the text.
        """
        # If we have a cached result and the transcript matches (or is highly similar), return it
        if self._last_result and self._last_result.get("transcript") == transcript:
            print("[GeminiModel] Using cached classification from the single API call.")
            return self._last_result
        
        # Fallback: Perform text-only classification
        print("[GeminiModel] Cache miss. Performing separate classification API call...")
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key or "your_" in api_key.lower() or "placeholder" in api_key.lower():
            raise ValueError("GEMINI_API_KEY not found or invalid in environment.")
            
        genai.configure(api_key=api_key)
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
        
        return json.loads(raw_text)
