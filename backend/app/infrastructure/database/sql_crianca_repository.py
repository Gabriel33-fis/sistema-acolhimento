from typing import Optional, List
from sqlalchemy.orm import Session
from app.application.interfaces.crianca_repository import ICriancaRepository
from app.domain.entities.crianca import Crianca
from app.infrastructure.database.models import CriancaModel

class SQLCriancaRepository(ICriancaRepository):
    def __init__(self, db_session: Session):
        self._session = db_session

    def salvar(self, crianca: Crianca, alergias_cifradas: Optional[str]) -> None:
        model = CriancaModel(
            id=crianca.id,
            nome_completo=crianca.nome_completo,
            data_nascimento=crianca.data_nascimento,
            data_admissao=crianca.data_admissao,
            status_acolhimento=crianca.status_acolhimento,
            alergias_cifradas=alergias_cifradas
        )
        self._session.merge(model)
        self._session.commit()

    def buscar_por_id(self, crianca_id: str) -> Optional[Crianca]:
        model = self._session.query(CriancaModel).filter(CriancaModel.id == crianca_id).first()
        if not model:
            return None
        return Crianca(
            id=model.id,
            nome_completo=model.nome_completo,
            data_nascimento=model.data_nascimento,
            data_admissao=model.data_admissao,
            status_acolhimento=model.status_acolhimento,
            alergias=None
        )

    def listar(self, termo_busca: Optional[str] = None) -> List[Crianca]:
        query = self._session.query(CriancaModel)
        if termo_busca:
            query = query.filter(CriancaModel.nome_completo.ilike(f"%{termo_busca}%"))
        
        registos = query.order_by(CriancaModel.data_admissao.desc()).all()
        return [
            Crianca(
                id=m.id,
                nome_completo=m.nome_completo,
                data_nascimento=m.data_nascimento,
                data_admissao=m.data_admissao,
                status_acolhimento=m.status_acolhimento,
                alergias=None
            )
            for m in registos
        ]
