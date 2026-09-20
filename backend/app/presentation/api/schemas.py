from datetime import date
from typing import Optional, List
from pydantic import BaseModel, Field

class CriancaEntradaSchema(BaseModel):
    nome_completo: str = Field(..., min_length=2, max_length=255)
    data_nascimento: date
    alergias: Optional[str] = Field(None, max_length=500)

class DesligamentoEntradaSchema(BaseModel):
    data_desligamento: date
    motivo: str = Field(..., min_length=3, max_length=255)
    destino: str = Field(..., min_length=3, max_length=255)

class CriancaRespostaSchema(BaseModel):
    id: str
    nome_completo: str
    data_nascimento: date
    data_admissao: date
    status_acolhimento: str

class CriancaDetalheSchema(BaseModel):
    id: str
    nome_completo: str
    data_nascimento: date
    data_admissao: date
    status_acolhimento: str
    alergias_decifradas: Optional[str] = None
    data_desligamento: Optional[date] = None
    motivo_desligamento: Optional[str] = None
    destino_desligamento: Optional[str] = None

class EvolucaoEntradaSchema(BaseModel):
    tipo: str = Field(..., description="PEDAGOGICA, COMPORTAMENTAL ou MEDICA")
    texto: str = Field(..., min_length=5, max_length=2000)

class EvolucaoRespostaSchema(BaseModel):
    id: str
    autor_nome: str
    tipo: str
    texto: str
    criado_em: str
    sigilosa: bool
