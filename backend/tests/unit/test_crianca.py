import pytest
from datetime import date, timedelta
from app.domain.entities.crianca import Crianca

def test_deve_criar_crianca_com_dados_validos():
    hoje = date.today()
    nascimento = hoje - timedelta(days=365 * 5)  # 5 anos atrás
    
    crianca = Crianca(
        id="uuid-123",
        nome_completo="João da Silva",
        data_nascimento=nascimento,
        data_admissao=hoje
    )
    
    assert crianca.id == "uuid-123"
    assert crianca.nome_completo == "João da Silva"
    assert crianca.status_acolhimento == "ACOLHIDO"

def test_deve_rejeitar_nome_com_menos_de_dois_caracteres():
    hoje = date.today()
    with pytest.raises(ValueError, match="O nome deve conter pelo menos 2 caracteres."):
        Crianca(
            id="uuid-123",
            nome_completo=" A ",
            data_nascimento=hoje,
            data_admissao=hoje
        )

def test_deve_rejeitar_data_de_nascimento_no_futuro():
    hoje = date.today()
    futuro = hoje + timedelta(days=1)
    with pytest.raises(ValueError, match="A data de nascimento não pode estar no futuro."):
        Crianca(
            id="uuid-123",
            nome_completo="Maria Souza",
            data_nascimento=futuro,
            data_admissao=hoje
        )
