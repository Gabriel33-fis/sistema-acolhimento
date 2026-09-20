from typing import List, Optional
from dataclasses import dataclass
from datetime import datetime
from app.application.interfaces.evolucao_repository import EvolucaoRepository
from app.infrastructure.security.crypto_service import CryptoService

@dataclass
class EvolucaoOutput:
    id: str
    autor_nome: str
    tipo: str
    texto: str
    criado_em: str
    sigilosa: bool

class ListarEvolucoesUseCase:
    def __init__(self, evolucao_repo: EvolucaoRepository, crypto_service: CryptoService):
        self.evolucao_repo = evolucao_repo
        self.crypto_service = crypto_service

    def execute(self, crianca_id: str, perfil_operador: str) -> List[EvolucaoOutput]:
        registros = self.evolucao_repo.listar_por_crianca(crianca_id)
        resultado: List[EvolucaoOutput] = []

        eh_coordenador = perfil_operador in ("COORDENADOR", "MEDICO")

        for r in registros:
            tipo = r["tipo"]
            conteudo_bruto = r["texto_ou_cifrado"]

            if tipo == "MEDICA":
                if eh_coordenador:
                    texto = self.crypto_service.decifrar(conteudo_bruto)
                else:
                    texto = "[CONTEÚDO SIGILOSO: Acesso restrito a profissionais médicos ou à coordenação]"
                sigilosa = True
            else:
                texto = conteudo_bruto
                sigilosa = False

            data_formatada = r["criado_em"].strftime("%d/%m/%Y %H:%M") if isinstance(r["criado_em"], datetime) else str(r["criado_em"])

            resultado.append(
                EvolucaoOutput(
                    id=r["id"],
                    autor_nome=r["autor_nome"],
                    tipo=tipo,
                    texto=texto,
                    criado_em=data_formatada,
                    sigilosa=sigilosa
                )
            )

        return resultado
