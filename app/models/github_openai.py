from typing import Type, TypeVar

from openai import OpenAI
from pydantic import BaseModel

from app.core.config import settings, require_github_settings

StructuredModel = TypeVar("StructuredModel", bound=BaseModel)

class GPT:
    def __init__(self):
        require_github_settings()

        self.client = OpenAI(
            base_url=settings.github_endpoint,
            api_key=settings.github_token,
        )

        self.model = settings.github_model


    def generate(
            self,
            user_prompt: str,
            system_prompt: str,
            response_schema: Type[StructuredModel]
    ) -> StructuredModel:

        response = self.client.chat.completions.parse(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": user_prompt,
                },
            ],
            temperature=0.1,
            top_p=1.0,
            max_tokens=8192,
            response_format=response_schema
        )

        parsed_response = response.choices[0].message.parsed

        if parsed_response is None:
            raise ValueError("LLM did not return a valid structured response.")

        return parsed_response


    def llm_call(
        self,
        prompt: str,
        response_schema: Type[StructuredModel],
        system_prompt: str,
    ) -> StructuredModel:
        response = self.client.chat.completions.parse(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": system_prompt,
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            temperature=0.1,
            top_p=1.0,
            max_tokens=8192,
            response_format=response_schema,
        )

        parsed_response = response.choices[0].message.parsed

        if parsed_response is None:
            raise ValueError("LLM did not return a valid structured response.")

        return parsed_response