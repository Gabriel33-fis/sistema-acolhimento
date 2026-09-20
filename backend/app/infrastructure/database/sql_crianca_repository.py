from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.orm import Session
from app.application.interfaces.crianca_repository import CriancaRepository
from app.domain.entities.crianca import Crianca
from app.infrastructure.database.models import CriancaModel

class SQLCriancaRepository(CriancaRepository):
    def __init__(self, session: Session):
        self.session = session

    def salvar(self, crianca: Crianca, alergias_cifradas: Optional[str] = None) -> None:
        cifradas = alergias_cifradas if alergias_cifradas is not None else crianca.alergias_cifradas

        model = self.session.query(CriancaModel).filter(CriancaModel.id == crianca.id).first()
        if model:
            model.nome_completo = crianca.nome_completo
            model.data_nascimento = crianca.data_nascimento
            model.data_admissao = crianca.data_admissao
            model.status_acolhimento = crianca.status_acolhimento
            model.alergias_cifradas = cifradas
            model.data_desligamento = crianca.data_desligamento
            model.motivo_desligamento = crianca.motivo_desligamento
            model.destino_desligamento = crianca.destino_desligamento
        else:
            model = CriancaModel(
                id=crianca.id,
                nome_completo=crianca.nome_completo,
                data_nascimento=crianca.data_nascimento,
                data_admissao=crianca.data_admissao,
                status_acolhimento=crianca.status_acolhimento,
                alergias_cifradas=cifradas,
                data_desligamento=crianca.data_desligamento,
                motivo_desligamento=crianca.motivo_desligamento,
                destino_desligamento=crianca.destino_desligamento,
                criado_em=datetime.now(timezone.utc)
            )
            self.session.add(model)
        self.session.commit()

    def obter_por_id(self, id: str) -> Optional[Crianca]:
        model = self.session.query(CriancaModel).filter(CriancaModel.id == id).first()
        if not model:
            return None
        return Crianca(
            id=model.id,
            nome_completo=model.nome_completo,
            data_nascimento=model.data_nascimento,
            data_admissao=model.data_admissao,
            status_acolhimento=model.status_acolhimento,
            alergias_cifradas=model.alergias_cifradas,
            data_desligamento=model.data_desligamento,
            motivo_desligamento=model.motivo_desligamento,
            destino_desligamento=model.destino_desligamento
        )

    buscar_por_id = obter_por_id

    def listar_todas(self, termo_busca: Optional[str] = None) -> List[Crianca]:
        query = self.session.query(CriancaModel)
        if termo_busca:
            query = query.filter(CriancaModel.nome_completo.ilike(f"%{termo_busca}%"))
        models = query.all()
        return [
            Crianca(
                id=m.id,
                nome_completo=m.nome_completo,
                data_nascimento=m.data_nascimento,
                data_admissao=m.data_admissao,
                status_acolhimento=m.status_acolhimento,
                alergias_cifradas=m.alergias_cifradas,
                data_desligamento=m.data_desligamento,
                motivo_desligamento=m.motivo_desligamento,
                destino_desligamento=m.destino_desligamento
            )
            for m in models
        ]
