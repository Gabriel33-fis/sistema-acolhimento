from datetime import date
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.infrastructure.database.connection import Base, get_db
from app.infrastructure.database.models import UtilizadorModel
from app.infrastructure.security.auth_service import AuthService

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine_test = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine_test)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

client = TestClient(app)

@pytest.fixture(autouse=True)
def preparar_banco():
    app.dependency_overrides[get_db] = override_get_db
    Base.metadata.create_all(bind=engine_test)
    db = TestingSessionLocal()
    
    admin = UtilizadorModel(
        id="coord-01",
        nome="Coordenador Teste",
        email="admin@teste.org",
        senha_hash=AuthService.gerar_hash_senha("senha123"),
        perfil="COORDENADOR"
    )
    operador = UtilizadorModel(
        id="oper-01",
        nome="Operador Teste",
        email="operador@teste.org",
        senha_hash=AuthService.gerar_hash_senha("senha123"),
        perfil="OPERADOR"
    )
    db.add(admin)
    db.add(operador)
    db.commit()
    db.close()
    
    yield
    
    Base.metadata.drop_all(bind=engine_test)
    app.dependency_overrides.pop(get_db, None)

def obter_token(email, senha):
    resp = client.post("/api/v1/auth/login", json={"email": email, "senha": senha})
    assert resp.status_code == 200
    return resp.json()["access_token"]

def test_fluxo_completo_acolhimento():
    token_coord = obter_token("admin@teste.org", "senha123")
    headers_coord = {"Authorization": f"Bearer {token_coord}"}

    token_oper = obter_token("operador@teste.org", "senha123")
    headers_oper = {"Authorization": f"Bearer {token_oper}"}

    # 1. Admitir uma criança
    payload_admissao = {
        "nome_completo": "Crianca Teste Integracao",
        "data_nascimento": "2016-04-10",
        "alergias": "Intolerância à lactose"
    }
    resp_adm = client.post("/api/v1/criancas/", json=payload_admissao, headers=headers_coord)
    assert resp_adm.status_code == 201
    crianca_id = resp_adm.json()["id"]

    # 2. Listar crianças
    resp_list = client.get("/api/v1/criancas/", headers=headers_oper)
    assert resp_list.status_code == 200
    assert any(c["id"] == crianca_id for c in resp_list.json())

    # 3. RBAC: Operador NÃO acessa prontuário confidencial (403 Forbidden)
    resp_det_oper = client.get(f"/api/v1/criancas/{crianca_id}", headers=headers_oper)
    assert resp_det_oper.status_code == 403

    # 4. Coordenador acessa e decifra o prontuário
    resp_det_coord = client.get(f"/api/v1/criancas/{crianca_id}", headers=headers_coord)
    assert resp_det_coord.status_code == 200
    assert resp_det_coord.json()["alergias_decifradas"] == "Intolerância à lactose"

    # 5. Adicionar evolução médica confidencial
    resp_ev = client.post(
        f"/api/v1/criancas/{crianca_id}/evolucoes",
        json={"tipo": "MEDICA", "texto": "Exame cardiológico normal."},
        headers=headers_coord
    )
    assert resp_ev.status_code == 201

    # 6. Desligamento pelo coordenador
    resp_deslig = client.post(
        f"/api/v1/criancas/{crianca_id}/desligamento",
        json={
            "data_desligamento": date.today().isoformat(),
            "motivo": "Guarda definitiva deferida",
            "destino": "Genitora"
        },
        headers=headers_coord
    )
    assert resp_deslig.status_code == 200

    # 7. Verificar estado final
    resp_final = client.get(f"/api/v1/criancas/{crianca_id}", headers=headers_coord)
    assert resp_final.json()["status_acolhimento"] == "DESACOLHIDO"


def test_versao_identificada_e_registro_ficticio_criado_e_consultado():
    """Roteiro da demonstração: mesma versão do início ao fim, criação e consulta."""
    from app.version import APP_VERSION

    v_antes = client.get("/health").json()
    assert v_antes["versao"] == APP_VERSION
    assert client.get("/api/v1/versao").json()["versao"] == APP_VERSION

    headers = {"Authorization": f"Bearer {obter_token('admin@teste.org', 'senha123')}"}
    registro = {
        "nome_completo": "[FICTÍCIO] Criança Demonstração",
        "data_nascimento": "2015-03-10",
        "alergias": "[FICTÍCIO] Alergia a amendoim",
    }
    resp = client.post("/api/v1/criancas/", json=registro, headers=headers)
    assert resp.status_code == 201
    crianca_id = resp.json()["id"]

    lista = client.get("/api/v1/criancas/?busca=FICTÍCIO", headers=headers).json()
    assert any(item["id"] == crianca_id for item in lista)

    detalhe = client.get(f"/api/v1/criancas/{crianca_id}", headers=headers).json()
    assert detalhe["nome_completo"] == registro["nome_completo"]
    assert detalhe["alergias_decifradas"] == registro["alergias"]

    assert client.get("/health").json() == v_antes


def test_listagem_de_evolucoes_por_perfil():
    """Defeito encontrado em 17/11/2026: listagem de evoluções retornava 500."""
    h_coord = {"Authorization": f"Bearer {obter_token('admin@teste.org', 'senha123')}"}
    h_oper = {"Authorization": f"Bearer {obter_token('operador@teste.org', 'senha123')}"}
    cid = client.post("/api/v1/criancas/", json={"nome_completo": "[FICTÍCIO] Evolução",
                      "data_nascimento": "2015-01-01"}, headers=h_coord).json()["id"]
    client.post(f"/api/v1/criancas/{cid}/evolucoes", json={"tipo": "MEDICA", "texto": "Consulta fictícia"}, headers=h_coord)
    client.post(f"/api/v1/criancas/{cid}/evolucoes", json={"tipo": "PEDAGOGICA", "texto": "Leitura em dia"}, headers=h_oper)

    r_coord = client.get(f"/api/v1/criancas/{cid}/evolucoes", headers=h_coord)
    r_oper = client.get(f"/api/v1/criancas/{cid}/evolucoes", headers=h_oper)
    assert r_coord.status_code == 200 and r_oper.status_code == 200
    medica_coord = next(e for e in r_coord.json() if e["tipo"] == "MEDICA")
    medica_oper = next(e for e in r_oper.json() if e["tipo"] == "MEDICA")
    assert medica_coord["texto"] == "Consulta fictícia"
    assert "Consulta fictícia" not in medica_oper["texto"]
    assert any(e["texto"] == "Leitura em dia" for e in r_oper.json())


def test_acesso_negado_e_registrado_na_auditoria():
    from app.infrastructure.database.models import AuditLogModel
    h_coord = {"Authorization": f"Bearer {obter_token('admin@teste.org', 'senha123')}"}
    h_oper = {"Authorization": f"Bearer {obter_token('operador@teste.org', 'senha123')}"}
    cid = client.post("/api/v1/criancas/", json={"nome_completo": "[FICTÍCIO] Auditoria",
                      "data_nascimento": "2015-01-01"}, headers=h_coord).json()["id"]
    assert client.get(f"/api/v1/criancas/{cid}", headers=h_oper).status_code == 403
    db = TestingSessionLocal()
    negados = db.query(AuditLogModel).filter(AuditLogModel.acao == "ACESSO_NEGADO",
                                             AuditLogModel.recurso_id == cid).all()
    db.close()
    assert len(negados) == 1 and negados[0].operador_id == "oper-01"
