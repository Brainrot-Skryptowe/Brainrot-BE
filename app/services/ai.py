import os

import openai

from app.models.shared.language import Language

openai.api_key = os.getenv("OPENAI_API_KEY")


def generate_reel_text(
    description: str, duration: int, target_lang: Language
) -> str:
    prompt = (
        "Tell me ONLY about given topic"
        f"It should last around {duration} seconds. "
        f"Topic: {description}."
        f"Respond in {target_lang.name}."
    )
    response = openai.chat.completions.create(
        model="gpt-4.1-nano",
        messages=[
            {
                "role": "system",
                "content": (
                    "You assist in responding only to topics provided by users."
                ),
            },
            {"role": "user", "content": prompt},
        ],
    )
    return response.choices[0].message.content.strip()


def translate_text(
    text: str, source_lang: Language, target_lang: Language
) -> dict[str, str]:
    prompt = (
        f"Translate given text from {source_lang.name}"
        f" to {target_lang.name}: {text}"
    )
    response = openai.chat.completions.create(
        model="gpt-4.1-nano",
        messages=[
            {
                "role": "system",
                "content": (
                    "You translate user-provided text from source to target language."
                ),
            },
            {"role": "user", "content": prompt},
        ],
    )
    return {
        source_lang.name.lower(): text,
        target_lang.name.lower(): response.choices[0].message.content.strip(),
    }
