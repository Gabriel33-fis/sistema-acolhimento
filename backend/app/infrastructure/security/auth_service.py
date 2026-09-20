import os
import bcrypt
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
import jwt

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "super_secret_jwt_key_acolhimento_2026")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 8  # 8 horas

class AuthService:
    @staticmethod
    def gerar_hash_senha(senha: str) -> str:
        # Bcrypt tem limite de 72 bytes
        senha_bytes = senha.encode("utf-8")[:72]
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(senha_bytes, salt)
        return hashed.decode("utf-8")

    @staticmethod
    def verificar_senha(senha_plana: str, senha_hash: str) -> bool:
        try:
            senha_bytes = senha_plana.encode("utf-8")[:72]
            hash_bytes = senha_hash.encode("utf-8")
            return bcrypt.checkpw(senha_bytes, hash_bytes)
        except Exception:
            return False

    @staticmethod
    def criar_token_acesso(payload: Dict[str, Any], expira_em: Optional[timedelta] = None) -> str:
        dados_para_codificar = payload.copy()
        expiracao = datetime.now(timezone.utc) + (expira_em or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
        dados_para_codificar.update({"exp": expiracao})
        return jwt.encode(dados_para_codificar, SECRET_KEY, algorithm=ALGORITHM)

    # Alias para compatibilidade
    gerar_token_acesso = criar_token_acesso

    @staticmethod
    def decifrar_token(token: str) -> Dict[str, Any]:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
