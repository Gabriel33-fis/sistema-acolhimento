import pytest
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.infrastructure.database.connection import Base
from app.infrastructure.database.sql_crianca_repository import SQLCriancaRepository
from app.infrastructure.database.sql_audit_logger import SQLAuditLogger
from app.domain.entities.crianca import Crianca

@pytest.fixture
def db_session():
    # Base de dados SQLite em memória para testes isolados
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

def test_deve_persistir_e_recuperar_crianca(db_session):
    repo = SQLCriancaRepository(db_session)
    crianca = Crianca(
        id="c-001",
        nome_completo="Lucas Pereira",
        data_nascimento=date(2019, 10, 1),
        data_admissao=date.today()
    )
    
    repo.salvar(crianca, alergias_cifradas="nonce:hashfake")
    recuperada = repo.buscar_por_id("c-001")
    
    assert recuperada is not None
    assert recuperada.id == "c-001"
    assert recuperada.nome_completo == "Lucas Pereira"

def test_deve_registar_evento_de_auditoria(db_session):
    audit = SQLAuditLogger(db_session)
    audit.registar_evento(
        operador_id="user-123",
        acao="CONSULTA_FICHA",
        recurso_id="c-001",
        ip="192.168.1.10"
    )
    
    from app.infrastructure.database.models import AuditoriaModel
    evento = db_session.query(AuditoriaModel).filter_by(recurso_id="c-001").first()
    assert evento is not None
    assert evento.acao == "CONSULTA_FICHA"
    assert evento.operador_id == "user-123"
