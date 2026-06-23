import json
from typing import Type, TypeVar

from google import genai
from google.genai import types
from pydantic import BaseModel

from app.core.config import settings, require_gemini_settings


StructuredModel = TypeVar("StructuredModel", bound=BaseModel)


class Gemini:
    def __init__(self):
        require_gemini_settings()

        self.client = genai.Client(
            api_key=settings.gemini_token,
        )

        self.model = "gemini-3.5-flash"

    def generate(
        self,
        user_prompt: str,
        system_prompt: str,
        response_schema: Type[StructuredModel],
    ) -> StructuredModel:
        schema_json = json.dumps(
            response_schema.model_json_schema(),
            ensure_ascii=False,
            indent=2,
        )

        final_prompt = f"""
{user_prompt}

Return ONLY valid JSON.
Do not include markdown.
Do not include explanations.
Do not wrap the JSON in ```json.

The JSON must match this schema:
{schema_json}
"""

        response = self.client.models.generate_content(
            model=self.model,
            contents=final_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.1,
                top_p=1.0,
                max_output_tokens=8192,
                response_mime_type="application/json",
            ),
        )

        if not response.text:
            raise ValueError("LLM did not return a valid structured response.")

        return response_schema.model_validate_json(response.text)
