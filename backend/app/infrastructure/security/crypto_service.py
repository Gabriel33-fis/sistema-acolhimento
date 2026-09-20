import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

class CryptoService:
    def __init__(self, key_hex: str):
        if len(key_hex) != 64:
            raise ValueError("A chave deve possuir 32 bytes (64 caracteres hexadecimais).")
        self._key = bytes.fromhex(key_hex)
        self._aesgcm = AESGCM(self._key)

    def encrypt(self, plain_text: str) -> str:
        nonce = os.urandom(12)  # 96-bit nonce
        encrypted_bytes = self._aesgcm.encrypt(nonce, plain_text.encode("utf-8"), None)
        return f"{nonce.hex()}:{encrypted_bytes.hex()}"

    def decrypt(self, encrypted_payload: str) -> str:
        try:
            nonce_hex, cipher_hex = encrypted_payload.split(":")
            nonce = bytes.fromhex(nonce_hex)
            cipher_bytes = bytes.fromhex(cipher_hex)
            decrypted = self._aesgcm.decrypt(nonce, cipher_bytes, None)
            return decrypted.decode("utf-8")
        except Exception as exc:
            raise ValueError("Falha ao decifrar o registo. Carga corrompida ou chave incorreta.") from exc
