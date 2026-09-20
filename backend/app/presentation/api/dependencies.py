from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.infrastructure.security.auth_service import AuthService

security = HTTPBearer()

def obter_utilizador_atual(credenciais: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    token = credenciais.credentials
    try:
        payload = AuthService.decifrar_token(token)
        usuario_id = payload.get("sub")
        if not usuario_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido: identificador ausente."
            )
        return {
            "id": usuario_id,
            "nome": payload.get("nome"),
            "email": payload.get("email"),
            "perfil": payload.get("perfil")
        }
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sessão inválida ou expirada. Faça login novamente."
        )
