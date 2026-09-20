import uuid
from sqlalchemy.orm import Session
from app.application.interfaces.audit_logger import IAuditLogger
from app.infrastructure.database.models import AuditoriaModel

class SQLAuditLogger(IAuditLogger):
    def __init__(self, db_session: Session):
        self._session = db_session

    def registar_evento(self, operador_id: str, acao: str, recurso_id: str, ip: str) -> None:
        evento = AuditoriaModel(
            id=str(uuid.uuid4()),
            operador_id=operador_id,
            acao=acao,
            recurso_id=recurso_id,
            ip_origem=ip
        )
        self._session.add(evento)
        self._session.commit()
