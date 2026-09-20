from datetime import date, timedelta
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.infrastructure.database.connection import engine, Base
from app.infrastructure.security.auth_service import AuthService

client = TestClient(app)

@pytest.fixture(autouse=True, scope="module")
def setup_database():
    Base.metadata.create_all(bind=engine)

def obter_headers_auth():
    token = AuthService.criar_token_acesso({
        "sub": "test-admin-api",
        "nome": "Test Admin",
        "email": "test@admin.org",
        "perfil": "COORDENADOR"
    })
    return {"Authorization": f"Bearer {token}"}

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_deve_registar_crianca_via_api():
    nascimento = (date.today() - timedelta(days=365 * 6)).isoformat()
    payload = {
        "nome_completo": "Beatriz Oliveira",
        "data_nascimento": nascimento,
        "alergias": "Amoxicilina"
    }

    response = client.post("/api/v1/criancas/", json=payload, headers=obter_headers_auth())
    assert response.status_code == 201
    assert "id" in response.json()

def test_deve_rejeitar_nome_invalido_via_api():
    nascimento = date.today().isoformat()
    payload = {
        "nome_completo": "A",
        "data_nascimento": nascimento
    }

    response = client.post("/api/v1/criancas/", json=payload, headers=obter_headers_auth())
    assert response.status_code == 422
