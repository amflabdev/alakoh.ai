# app/modules/cognitive_engine/__init__.py
import os
import sys

# Defensive path injection to ensure subfolder structures are globally accessible
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from providers.gemini import GeminiProvider

class AICognitiveAgent:
    """
    Unified architectural facade wrapper.
    Routes downstream calls straight to our dedicated Gemini Provider.
    """
    def __init__(self):
        self.provider = GeminiProvider()

    def ask(self, prompt: str) -> str:
        """Forwards conversational telemetry context straight to Gemini 1.5 Flash."""
        return self.provider.generate_response(prompt)