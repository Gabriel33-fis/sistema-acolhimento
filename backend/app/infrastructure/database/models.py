from datetime import datetime, timezone
from sqlalchemy import Column, String, Date, DateTime, Text, ForeignKey, Boolean
from app.infrastructure.database.connection import Base

class UtilizadorModel(Base):
    __tablename__ = "utilizadores"

    id = Column(String, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    senha_hash = Column(String, nullable=False)
    perfil = Column(String, default="OPERADOR", nullable=False)
    criado_em = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

class CriancaModel(Base):
    __tablename__ = "criancas"

    id = Column(String, primary_key=True, index=True)
    nome_completo = Column(String, nullable=False)
    data_nascimento = Column(Date, nullable=False)
    data_admissao = Column(Date, nullable=False)
    status_acolhimento = Column(String, default="ACOLHIDO", nullable=False)
    alergias_cifradas = Column(Text, nullable=True)
    data_desligamento = Column(Date, nullable=True)
    motivo_desligamento = Column(String, nullable=True)
    destino_desligamento = Column(String, nullable=True)
    criado_em = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

class EvolucaoModel(Base):
    __tablename__ = "evolucoes"

    id = Column(String, primary_key=True, index=True)
    crianca_id = Column(String, ForeignKey("criancas.id"), nullable=False, index=True)
    autor_id = Column(String, ForeignKey("utilizadores.id"), nullable=False)
    autor_nome = Column(String, nullable=False)
    tipo = Column(String, nullable=False)
    texto_cifrado = Column(Text, nullable=False)
    criado_em = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

class AuditLogModel(Base):
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True, index=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    operador_id = Column(String, nullable=False)
    acao = Column(String, nullable=False)
    recurso = Column(String, nullable=False)
    recurso_id = Column(String, nullable=True)
    ip_origem = Column(String, nullable=True)
    detalhes = Column(Text, nullable=True)

# Alias retrocompatível com testes anteriores
AuditoriaModel = AuditLogModel
