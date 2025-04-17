from bson import ObjectId
import os
import re
import secrets
import jwt
import bcrypt
import string
from datetime import datetime, timedelta
from models.user import User
from config import Config
from datetime import datetime
from extensions import mongo
import logging
logging.basicConfig(level=logging.DEBUG)
logging.getLogger("pymongo").setLevel(logging.CRITICAL)
def translate_text(text, target_lang="en"):
    try:
        return GoogleTranslator(source="auto", target=target_lang).translate(text)
    except Exception as e:
        try:

            sentences = re.split(r"(?<=[.!?]) +", text)

            if len(sentences) == 1:
                words = text.split()
                mid_index = len(words) // 2
                part1 = " ".join(words[:mid_index])
                part2 = " ".join(words[mid_index:])

                translated_part1 = GoogleTranslator(
                    source="auto", target=target_lang
                ).translate(part1)
                translated_part2 = GoogleTranslator(
                    source="auto", target=target_lang
                ).translate(part2)

                return translated_part1 + " " + translated_part2

            translated_sentences = []
            for sentence in sentences:
                translated_sentence = GoogleTranslator(
                    source="auto", target=target_lang
                ).translate(sentence)
                translated_sentences.append(translated_sentence)
            return " ".join(translated_sentences)
        except Exception as e:
            return "Translation failed."


def hash_password(password: str) -> str:
    try:
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")
    except (ValueError, TypeError) as e:
        raise ValueError("Invalid password format") from e


def check_password(password: str, hashed_password: str) -> bool:
    try:
        if not password or not hashed_password:
            return False
        return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))
    except (ValueError, TypeError):
        return False


def load_json(file_path):
    with open(file_path, "r", encoding="UTF-8") as file:
        data = json.load(file)
    return data


def save_json(data, file_path):
    with open(file_path, "w", encoding="UTF-8") as file:
        file.write(data)


def obj_to_json(data, file_path):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def ask_to_llama3_70b(system_prompt, user_message, temperature=0.0, input_print=True):
    try:
        client = Config.create_groq_client()
        if system_prompt == "Aspect":
            system_prompt = Config.SYSTEM_PROMPT_ASPECT
        elif system_prompt == "Response":
            system_prompt = Config.SYSTEM_PROMPT_RESPONSE
        elif system_prompt == "Debug":
            system_prompt = Config.SYSTEM_PROMPT_DEBUG
        else:
            raise ValueError("Invalid system prompt. Must be 'Aspect' or 'Response'.")

        messages = [
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_message,
            },
        ]

        chat_completion = client.chat.completions.create(
            messages=messages, model="llama3-70b-8192", temperature=temperature
        )

        system_response = chat_completion.choices[0].message.content
        return system_response

    except Exception as e:
        raise Exception(
            "API key is worn off. Please wait 5 minutes to continue."
        ) from e


def ask_to_gpt_4o_mini(system_prompt, user_message, temperature=0.0, input_print=True):
    try:
        client = Config.create_openai_client()
        if system_prompt == "Aspect":
            system_prompt = Config.SYSTEM_PROMPT_ASPECT
        elif system_prompt == "Response":
            system_prompt = Config.SYSTEM_PROMPT_RESPONSE
        elif system_prompt == "Debug":
            system_prompt = Config.SYSTEM_PROMPT_DEBUG
        elif system_prompt == "Persona":
            system_prompt = Config.SYSTEM_PROMPT_PERSONA
        else:
            raise ValueError("Invalid system prompt. Must be 'Aspect' or 'Response'.")
        messages = [
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_message,
            },
        ]

        chat_completion = client.chat.completions.create(
            messages=messages, model="gpt-4o-mini", temperature=temperature
        )

        system_response = chat_completion.choices[0].message.content
        return system_response

    except Exception as e:
        raise Exception(
            "API key is worn off. Please wait 5 minutes to continue."
        ) from e


def ask_to_gpt_4o_positive(
    system_prompt, user_message, temperature=0.0, input_print=True
):
    try:
        client = Config.create_openai_client()
        if system_prompt == "Aspect":
            system_prompt = Config.SYSTEM_PROMPT_ASPECT
        elif system_prompt == "Response":
            system_prompt = Config.SYSTEM_PROMPT_RESPONSE_POSITIVE
        elif system_prompt == "Debug":
            system_prompt = Config.SYSTEM_PROMPT_DEBUG
        else:
            raise ValueError("Invalid system prompt. Must be 'Aspect' or 'Response'.")
        messages = [
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_message,
            },
        ]

        chat_completion = client.chat.completions.create(
            messages=messages,
            model="gpt-4o",
            response_format={"type": "json_object"},
            temperature=temperature,
        )

        system_response = chat_completion.choices[0].message.content
        return system_response

    except Exception as e:
        raise Exception(
            "API key is worn off. Please wait 5 minutes to continue."
        ) from e


def ask_to_gpt_4o_negative(
    system_prompt, user_message, temperature=0.0, input_print=True
):
    try:
        client = Config.create_openai_client()
        if system_prompt == "Aspect":
            system_prompt = Config.SYSTEM_PROMPT_ASPECT
        elif system_prompt == "Response":
            system_prompt = Config.SYSTEM_PROMPT_RESPONSE_NEGATIVE
        elif system_prompt == "Debug":
            system_prompt = Config.SYSTEM_PROMPT_DEBUG
        else:
            raise ValueError("Invalid system prompt. Must be 'Aspect' or 'Response'.")
        messages = [
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": user_message,
            },
        ]

        chat_completion = client.chat.completions.create(
            messages=messages,
            model="gpt-4o",
            response_format={"type": "json_object"},
            temperature=temperature,
        )

        system_response = chat_completion.choices[0].message.content
        return system_response

    except Exception as e:
        raise Exception(
            "API key is worn off. Please wait 5 minutes to continue."
        ) from e


def detect_persona(text):
    try:
        client = Config.create_openai_client()
        system_prompt = Config.SYSTEM_PROMPT_PERSONA
        messages = [
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": text,
            },
        ]

        chat_completion = client.chat.completions.create(
            messages=messages,
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            temperature=0.0,
        )

        system_response = chat_completion.choices[0].message.content
        return system_response

    except Exception as e:
        print(e)
        raise Exception(
            "API key is worn off. Please wait 5 minutes to continue."
        ) from e


def save_to_mongodb(reviews: list) -> None:
    try:
        if reviews:
            for review in reviews:
                review["deleted"] = False
                review["is_flagged"] = False
                if review.get("source") == "Yandex":
                    result = mongo.db[Config.REVIEW_COLLECTION].update_one(
                        {"date": review["date"]}, {"$set": review}, upsert=True
                    )
                else:
                    result = mongo.db[Config.REVIEW_COLLECTION].update_one(
                        {"review_id": review["review_id"]}, {"$set": review}, upsert=True
                    )
    except Exception as e:
        logging.error(f"Error saving to MongoDB: {e}")
        raise Exception(e) from e

def convert_objectid(data):
    if isinstance(data, list):
        for item in data:
            if '_id' in item:
                item['_id'] = str(item['_id'])
    elif isinstance(data, dict):
        if '_id' in data:
            data['_id'] = str(data['_id'])
    return data