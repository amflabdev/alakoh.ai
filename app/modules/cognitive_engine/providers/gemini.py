# app/modules/cognitive_engine/providers/gemini.py
from langchain_google_genai import ChatGoogleGenerativeAI
from config.settings import settings

class GeminiProvider:
    """Handles direct API streaming wrappers for Google Gemini 1.5 Flash."""
    def __init__(self):
        # Bind the live API Key and target model string
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=settings.GEMINI_API_KEY,
            temperature=0.7
        )

    def generate_response(self, prompt: str) -> str:
        """Invokes the Gemini 1.5 Flash context window layer."""
        try:
            response = self.llm.invoke(prompt)
            return response.content
        except Exception as e:
            return f"Gemini Execution Error: {str(e)}"

    # ─── THE CRITICAL FIX METHOD FOR LINE 120 ───
    def run_pipeline(self, user_query: str, context_user_id: str = None) -> str:
        """
        Intercepts the pipeline call from the Streamlit UI workspace
        and routes it directly to the Gemini core generation framework.
        """
        return self.generate_response(user_query)