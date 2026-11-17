import pytest
import os
from app.infrastructure.security.crypto_service import CryptoService

def test_deve_cifrar_e_decifrar_texto_corretamente():
    chave_aleatoria = os.urandom(32).hex()
    servico = CryptoService(key_hex=chave_aleatoria)
    
    texto_original = "Informação confidencial de saúde"
    texto_cifrado = servico.encrypt(texto_original)
    
    assert texto_cifrado != texto_original
    assert ":" in texto_cifrado  # nonce:payload
    
    texto_recuperado = servico.decrypt(texto_cifrado)
    assert texto_recuperado == texto_original

def test_deve_falhar_ao_tentar_decifrar_com_chave_invalida():
    chave_a = os.urandom(32).hex()
    chave_b = os.urandom(32).hex()
    
    servico_a = CryptoService(key_hex=chave_a)
    servico_b = CryptoService(key_hex=chave_b)
    
    texto_cifrado = servico_a.encrypt("Dado sensível")
    
    with pytest.raises(Exception):
        servico_b.decrypt(texto_cifrado)


def test_dado_adulterado_e_detectado():
    servico = CryptoService(key_hex=os.urandom(32).hex())
    nonce, cifrado = servico.encrypt("Alergia a dipirona").split(":", 1)
    adulterado = nonce + ":" + ("A" if cifrado[0] != "A" else "B") + cifrado[1:]
    with pytest.raises(ValueError):
        servico.decrypt(adulterado)


def test_registro_legado_em_texto_continua_legivel():
    servico = CryptoService(key_hex=os.urandom(32).hex())
    assert servico.decrypt("Sem alergias") == "Sem alergias"
