import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from app.application.interfaces.audit_logger import AuditLogger
from app.infrastructure.database.models import AuditLogModel

class SQLAuditLogger(AuditLogger):
    def __init__(self, session: Session):
        self.session = session

    def registrar(self, operador_id: str, acao: str, recurso: str, recurso_id: str = None, ip_origem: str = None, detalhes: str = None) -> None:
        log = AuditLogModel(
            id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc),
            operador_id=operador_id,
            acao=acao,
            recurso=recurso,
            recurso_id=recurso_id,
            ip_origem=ip_origem,
            detalhes=detalhes
        )
        self.session.add(log)
        self.session.commit()

    def registar_evento(self, operador_id: str, acao: str, recurso_id: str = None, ip: str = None, detalhes: str = None) -> None:
        self.registrar(
            operador_id=operador_id,
            acao=acao,
            recurso="SISTEMA",
            recurso_id=recurso_id,
            ip_origem=ip,
            detalhes=detalhes
        )
