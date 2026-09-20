import os
from datetime import datetime, timedelta, timezone
from typing import Optional
import jwt
import bcrypt

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "chave-secreta-acolhimento-fatec-2026")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120

class AuthService:
    @staticmethod
    def verificar_senha(senha_plana: str, senha_hash: str) -> bool:
        senha_bytes = senha_plana.encode("utf-8")
        hash_bytes = senha_hash.encode("utf-8")
        return bcrypt.checkpw(senha_bytes, hash_bytes)

    @staticmethod
    def gerar_hash_senha(senha_plana: str) -> str:
        senha_bytes = senha_plana.encode("utf-8")
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(senha_bytes, salt).decode("utf-8")

    @staticmethod
    def criar_token_acesso(dados: dict, tempo_expiracao: Optional[timedelta] = None) -> str:
        dados_codificar = dados.copy()
        expira = datetime.now(timezone.utc) + (tempo_expiracao or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
        dados_codificar.update({"exp": expira})
        return jwt.encode(dados_codificar, SECRET_KEY, algorithm=ALGORITHM)

    @staticmethod
    def descodificar_token(token: str) -> dict:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
