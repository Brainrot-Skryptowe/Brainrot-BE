import os

import openai

from app.models.shared.language import Language

openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_reel_text(description: str, duration: int) -> str:
    prompt = (
        "Tell me ONLY about given topic"
        f"It should last around {duration} seconds. "
        f"Topic: {description}."
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


LANGUAGE_CODE_MAP = {
    Language.English: "english",
    Language.Spanish: "spanish",
    Language.French: "french",
    Language.Italian: "italian",
    Language.Portuguese: "portuguese",
    Language.Polish: "polish",
}

def translate_text(
    text: str, source_lang: Language, target_lang: Language
) -> dict[str, str]:
    prompt = (
        f"Translate given text from {LANGUAGE_CODE_MAP[source_lang]}"
        f" to {LANGUAGE_CODE_MAP[target_lang]}: {text}"
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
        target_lang.name.lower(): response.choices[0].message.content.strip()
    }