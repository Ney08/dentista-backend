from pydantic import BaseModel


class ClinicalNoteRequest(
    BaseModel
):

    text: str
