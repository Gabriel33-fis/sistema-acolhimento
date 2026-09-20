from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt

from app.infrastructure.security.auth_service import AuthService

security = HTTPBearer()

def obter_utilizador_atual(credenciais: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    token = credenciais.credentials
    try:
        payload = AuthService.descodificar_token(token)
        return {
            "id": payload.get("sub"),
            "email": payload.get("email"),
            "perfil": payload.get("perfil")
        }
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sessão expirada. Faça login novamente."
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de acesso inválido ou malformado."
        )
