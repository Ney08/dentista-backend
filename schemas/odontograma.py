from pydantic import BaseModel
from typing import Dict
from typing import Optional


class FaceData(BaseModel):

    top: Optional[str] = None

    left: Optional[str] = None

    center: Optional[str] = None

    right: Optional[str] = None

    bottom: Optional[str] = None


class OdontogramaPayload(BaseModel):

    odontograma: Dict[
        str,
        FaceData
    ]