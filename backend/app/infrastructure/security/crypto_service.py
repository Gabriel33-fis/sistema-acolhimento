import os
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

class CryptoService:
    def __init__(self, key_hex: str = None):
        if not key_hex:
            key_hex = os.getenv("CRYPTO_KEY_HEX", "00" * 32)
        self.key = bytes.fromhex(key_hex)
        self.aesgcm = AESGCM(self.key)

    @staticmethod
    def _corrigir_padding_b64(dado: str) -> bytes:
        dado_str = dado.strip()
        faltantes = len(dado_str) % 4
        if faltantes != 0:
            dado_str += "=" * (4 - faltantes)
        return base64.b64decode(dado_str.encode("utf-8"))

    def cifrar(self, dado: str) -> str:
        if not dado:
            return ""
        nonce = os.urandom(12)
        dado_bytes = dado.encode("utf-8")
        cifrado = self.aesgcm.encrypt(nonce, dado_bytes, None)
        nonce_b64 = base64.b64encode(nonce).decode("utf-8")
        cifrado_b64 = base64.b64encode(cifrado).decode("utf-8")
        return f"{nonce_b64}:{cifrado_b64}"

    def decifrar(self, dado_cifrado: str) -> str:
        if not dado_cifrado:
            return ""
        
        try:
            if ":" in dado_cifrado:
                nonce_b64, cifrado_b64 = dado_cifrado.split(":", 1)
                nonce = self._corrigir_padding_b64(nonce_b64)
                cifrado = self._corrigir_padding_b64(cifrado_b64)
            else:
                dados_bytes = self._corrigir_padding_b64(dado_cifrado)
                if len(dados_bytes) < 13:
                    # Dado não é um payload cifrado válido (ex: texto curto antigo)
                    return dado_cifrado
                nonce = dados_bytes[:12]
                cifrado = dados_bytes[12:]

            return self.aesgcm.decrypt(nonce, cifrado, None).decode("utf-8")
        except Exception:
            # Fallback seguro: se falhar a decifragem por ser registro legado, retorna como texto
            return dado_cifrado

    # Aliases
    cifrar_dado = cifrar
    decifrar_dado = decifrar
    encrypt = cifrar
    decrypt = decifrar
