from pydantic import BaseModel, Field, ConfigDict
from datetime import date
from typing import Optional

class CriancaEntradaSchema(BaseModel):
    nome_completo: str = Field(
        ...,
        min_length=2,
        json_schema_extra={"example": "Ana Clara Santos"}
    )
    data_nascimento: date = Field(
        ...,
        json_schema_extra={"example": "2018-05-20"}
    )
    alergias: Optional[str] = Field(
        None,
        json_schema_extra={"example": "Dipirona e amendoim"}
    )

class CriancaRespostaSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    nome_completo: str
    data_nascimento: date
    data_admissao: date
    status_acolhimento: str

class CriancaDetalheSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    nome_completo: str
    data_nascimento: date
    data_admissao: date
    status_acolhimento: str
    alergias_decifradas: Optional[str] = None
