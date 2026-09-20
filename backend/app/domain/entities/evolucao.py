from dataclasses import dataclass
from datetime import datetime
from typing import Optional

TIPOS_VALIDOS = {"PEDAGOGICA", "COMPORTAMENTAL", "MEDICA"}

@dataclass
class Evolucao:
    id: str
    crianca_id: str
    autor_id: str
    autor_nome: str
    tipo: str
    texto: str
    criado_em: datetime

    @classmethod
    def criar(cls, id: str, crianca_id: str, autor_id: str, autor_nome: str, tipo: str, texto: str, criado_em: Optional[datetime] = None) -> "Evolucao":
        tipo_normalizado = tipo.upper().strip()
        if tipo_normalizado not in TIPOS_VALIDOS:
            raise ValueError(f"Tipo de evolução inválido: {tipo}. Deve ser PEDAGOGICA, COMPORTAMENTAL ou MEDICA.")
        
        texto_limpo = texto.strip()
        if len(texto_limpo) < 5:
            raise ValueError("O relatório de evolução deve conter no mínimo 5 caracteres.")

        return cls(
            id=id,
            crianca_id=crianca_id,
            autor_id=autor_id,
            autor_nome=autor_nome,
            tipo=tipo_normalizado,
            texto=texto_limpo,
            criado_em=criado_em or datetime.now()
        )
