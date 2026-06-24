from fastapi import APIRouter
from pydantic import BaseModel

from openai import OpenAI

import os

router = APIRouter(
    prefix="/ai",
    tags=["AI"]
)

client = OpenAI(
    api_key=os.getenv(
        "OPENAI_API_KEY"
    )
)

"""
==========================================
SCHEMA
==========================================
"""

class ClinicalNoteRequest(
    BaseModel
):

    text: str

"""
==========================================
AI NOTE
==========================================
"""

@router.post(
    "/clinical-note"
)

def clinical_note(

    payload:
    ClinicalNoteRequest

):

    prompt = f"""

Convierte la siguiente nota
en una observación clínica
profesional odontológica.

Texto:

{payload.text}

"""

    response = client.chat.completions.create(

        model="gpt-4.1-mini",

        messages=[

            {

                "role": "system",

                "content":

                """
Eres un asistente clínico
odontológico profesional.
Usa lenguaje médico claro,
conciso y profesional.
                """

            },

            {

                "role": "user",

                "content": prompt

            }

        ]

    )

    return {

        "result":

        response
        .choices[0]
        .message
        .content

    }