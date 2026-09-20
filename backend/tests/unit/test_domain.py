import pytest
from datetime import date
from app.domain.entities.crianca import Crianca
from app.domain.entities.evolucao import Evolucao

def test_desacolhimento_com_sucesso():
    crianca = Crianca(
        id="c1",
        nome_completo="Acolhido Teste",
        data_nascimento=date(2015, 5, 20),
        data_admissao=date(2023, 1, 10),
        status_acolhimento="ACOLHIDO"
    )

    crianca.desacolher(
        data_saida=date(2023, 6, 15),
        motivo="Reintegração Familiar",
        destino="Família Extensa"
    )

    assert crianca.status_acolhimento == "DESACOLHIDO"
    assert crianca.data_desligamento == date(2023, 6, 15)
    assert crianca.motivo_desligamento == "Reintegração Familiar"
    assert crianca.destino_desligamento == "Família Extensa"

def test_desacolhimento_com_data_anterior_a_admissao_deve_falhar():
    crianca = Crianca(
        id="c1",
        nome_completo="Acolhido Teste",
        data_nascimento=date(2015, 5, 20),
        data_admissao=date(2023, 5, 10),
        status_acolhimento="ACOLHIDO"
    )

    with pytest.raises(ValueError, match="não pode ser anterior à data de admissão"):
        crianca.desacolher(
            data_saida=date(2023, 1, 1),
            motivo="Motivo qualquer",
            destino="Destino qualquer"
        )

def test_desacolhimento_de_acolhido_ja_desligado_deve_falhar():
    crianca = Crianca(
        id="c1",
        nome_completo="Acolhido Teste",
        data_nascimento=date(2015, 5, 20),
        data_admissao=date(2023, 1, 10),
        status_acolhimento="DESACOLHIDO"
    )

    with pytest.raises(ValueError, match="já se encontra com status DESACOLHIDO"):
        crianca.desacolher(
            data_saida=date(2023, 6, 1),
            motivo="Novo motivo",
            destino="Novo destino"
        )

def test_atualizar_dados_validos():
    crianca = Crianca(
        id="c1",
        nome_completo="Nome Antigo",
        data_nascimento=date(2015, 5, 20),
        data_admissao=date(2023, 1, 10),
        status_acolhimento="ACOLHIDO"
    )

    crianca.atualizar_dados(
        novo_nome="Nome Corrigido",
        nova_data_nascimento=date(2015, 5, 25),
        novas_alergias_cifradas="cifrado123"
    )

    assert crianca.nome_completo == "Nome Corrigido"
    assert crianca.data_nascimento == date(2015, 5, 25)
    assert crianca.alergias_cifradas == "cifrado123"

def test_criar_evolucao_com_tipo_invalido_deve_falhar():
    with pytest.raises(ValueError, match="Tipo de evolução inválido"):
        Evolucao.criar(
            id="e1",
            crianca_id="c1",
            autor_id="op1",
            autor_nome="Operador",
            tipo="TIPO_INEXISTENTE",
            texto="Texto com tamanho suficiente para validar."
        )

def test_criar_evolucao_com_texto_curto_deve_falhar():
    with pytest.raises(ValueError, match="no mínimo 5 caracteres"):
        Evolucao.criar(
            id="e1",
            crianca_id="c1",
            autor_id="op1",
            autor_nome="Operador",
            tipo="PEDAGOGICA",
            texto="Oi"
        )
