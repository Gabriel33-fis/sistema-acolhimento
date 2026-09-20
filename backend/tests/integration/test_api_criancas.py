from fastapi.testclient import TestClient
from datetime import date, timedelta
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "operacional"}

def test_deve_registar_crianca_via_api():
    nascimento = (date.today() - timedelta(days=365 * 6)).isoformat()
    payload = {
        "nome_completo": "Beatriz Oliveira",
        "data_nascimento": nascimento,
        "alergias": "Amoxicilina"
    }
    
    response = client.post("/api/v1/criancas/", json=payload)
    assert response.status_code == 201
    dados = response.json()
    assert "id" in dados
    assert dados["mensagem"] == "Acolhido registado com sucesso"

def test_deve_rejeitar_nome_invalido_via_api():
    nascimento = date.today().isoformat()
    payload = {
        "nome_completo": "A",
        "data_nascimento": nascimento
    }
    
    response = client.post("/api/v1/criancas/", json=payload)
    assert response.status_code == 422  # Erro de validação do Pydantic
