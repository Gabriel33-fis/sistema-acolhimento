from sqlalchemy import Column, String, Date, DateTime
from sqlalchemy.sql import func
from app.infrastructure.database.connection import Base

class CriancaModel(Base):
    __tablename__ = "criancas"

    id = Column(String, primary_key=True, index=True)
    nome_completo = Column(String, nullable=False)
    data_nascimento = Column(Date, nullable=False)
    data_admissao = Column(Date, nullable=False)
    status_acolhimento = Column(String, nullable=False)
    alergias_cifradas = Column(String, nullable=True)

class AuditoriaModel(Base):
    __tablename__ = "auditoria_acessos"

    id = Column(String, primary_key=True, index=True)
    data_hora = Column(DateTime(timezone=True), server_default=func.now())
    operador_id = Column(String, nullable=False)
    acao = Column(String, nullable=False)
    recurso_id = Column(String, nullable=False)
    ip_origem = Column(String, nullable=False)

class UtilizadorModel(Base):
    __tablename__ = "utilizadores"

    id = Column(String, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    senha_hash = Column(String, nullable=False)
    perfil = Column(String, default="OPERADOR", nullable=False)
