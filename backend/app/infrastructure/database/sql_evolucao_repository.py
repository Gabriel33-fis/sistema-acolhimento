from datetime import datetime, timezone
from typing import List
from sqlalchemy.orm import Session
from app.application.interfaces.evolucao_repository import EvolucaoRepository
from app.domain.entities.evolucao import Evolucao
from app.infrastructure.database.models import EvolucaoModel

class SQLEvolucaoRepository(EvolucaoRepository):
    def __init__(self, session: Session):
        self.session = session

    def salvar(self, evolucao: Evolucao, texto_para_banco: str = None) -> None:
        conteudo = texto_para_banco if texto_para_banco is not None else evolucao.texto
        model = EvolucaoModel(
            id=evolucao.id,
            crianca_id=evolucao.crianca_id,
            autor_id=evolucao.autor_id,
            autor_nome=evolucao.autor_nome,
            tipo=evolucao.tipo,
            texto_cifrado=conteudo,
            criado_em=evolucao.criado_em or datetime.now(timezone.utc)
        )
        self.session.add(model)
        self.session.commit()

    def listar_por_crianca(self, crianca_id: str) -> List[dict]:
        registros = (
            self.session.query(EvolucaoModel)
            .filter(EvolucaoModel.crianca_id == crianca_id)
            .order_by(EvolucaoModel.criado_em.desc())
            .all()
        )
        return [
            {
                "id": r.id,
                "crianca_id": r.crianca_id,
                "autor_id": r.autor_id,
                "autor_nome": r.autor_nome,
                "tipo": r.tipo,
                "texto_banco": r.texto_cifrado,
                "criado_em": r.criado_em
            }
            for r in registros
        ]
