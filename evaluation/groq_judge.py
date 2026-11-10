
import json
import asyncio
import time

from groq import Groq, AsyncGroq, RateLimitError
from pydantic import BaseModel
from deepeval.models import DeepEvalBaseLLM

from chatbot.config import GROQ_API_KEY, GROQ_MODEL


class GroqJudge(DeepEvalBaseLLM):

    def __init__(self):
        self.client = Groq(api_key=GROQ_API_KEY)
        self.async_client = AsyncGroq(api_key=GROQ_API_KEY)

    def load_model(self):
        return self.client

    def get_model_name(self):
        return GROQ_MODEL

    def generate(self, prompt: str, schema: BaseModel = None):

        messages = [
            {
                "role": "system",
                "content": "You are an AI evaluation judge. Follow the instructions carefully."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]

        if schema:
            messages[1]["content"] += (
                "\nReturn valid JSON matching this schema:\n"
                + json.dumps(schema.model_json_schema())
            )

        for attempt in range(3):

            try:
                response = self.client.chat.completions.create(
                    model=GROQ_MODEL,
                    messages=messages,
                    temperature=0
                )

                result = response.choices[0].message.content

                if schema:
                    return schema.model_validate_json(result)

                return result

            except RateLimitError:

                if attempt == 2:
                    raise

                delay = 15 * (attempt + 1)

                print(
                    f"Groq rate limit reached. "
                    f"Retrying in {delay} seconds..."
                )

                time.sleep(delay)

    async def a_generate(
        self,
        prompt: str,
        schema: BaseModel = None
    ):

        messages = [
            {
                "role": "system",
                "content": "You are an AI evaluation judge. Follow the instructions carefully."
            },
            {
                "role": "user",
                "content": prompt
            }
        ]

        if schema:
            messages[1]["content"] += (
                "\nReturn valid JSON matching this schema:\n"
                + json.dumps(schema.model_json_schema())
            )

        for attempt in range(3):

            try:
                response = await self.async_client.chat.completions.create(
                    model=GROQ_MODEL,
                    messages=messages,
                    temperature=0
                )

                result = response.choices[0].message.content

                if schema:
                    return schema.model_validate_json(result)

                return result

            except RateLimitError:

                if attempt == 2:
                    raise

                delay = 15 * (attempt + 1)

                print(
                    f"Groq rate limit reached. "
                    f"Retrying in {delay} seconds..."
                )

                await asyncio.sleep(delay)
