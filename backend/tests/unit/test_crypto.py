import pytest
from app.infrastructure.security.crypto_service import CryptoService

def test_cifragem_e_decifragem_sucesso():
    key_hex = "00" * 32
    service = CryptoService(key_hex=key_hex)
    dado_sensivel = "Alergia grave a penicilina e dipirona."

    cifrado = service.cifrar(dado_sensivel)
    assert cifrado != dado_sensivel
    assert len(cifrado) > 0

    decifrado = service.decifrar(cifrado)
    assert decifrado == dado_sensivel

def test_decifragem_com_chave_ou_dado_corrompido_falha():
    key_hex = "00" * 32
    service = CryptoService(key_hex=key_hex)
    cifrado = service.cifrar("Dado confidencial")

    service_chave_diferente = CryptoService(key_hex="11" * 32)
    with pytest.raises(Exception):
        service_chave_diferente.decifrar(cifrado)
