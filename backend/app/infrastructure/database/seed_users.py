import uuid
from app.infrastructure.database.connection import SessionLocal, Base, engine
from app.infrastructure.database.models import UtilizadorModel
from app.infrastructure.security.auth_service import AuthService

def criar_utilizadores():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    utilizadores = [
        {
            "nome": "Coordenador Geral",
            "email": "admin@instituicao.org",
            "senha": "admin123",
            "perfil": "COORDENADOR"
        },
        {
            "nome": "Educador Social",
            "email": "educador@instituicao.org",
            "senha": "user123",
            "perfil": "OPERADOR"
        }
    ]

    for u in utilizadores:
        existente = db.query(UtilizadorModel).filter(UtilizadorModel.email == u["email"]).first()
        if not existente:
            novo = UtilizadorModel(
                id=str(uuid.uuid4()),
                nome=u["nome"],
                email=u["email"],
                senha_hash=AuthService.gerar_hash_senha(u["senha"]),
                perfil=u["perfil"]
            )
            db.add(novo)
            print(f"Utilizador criado: {u['email']} | Perfil: {u['perfil']}")
        else:
            print(f"Utilizador já existe: {u['email']}")

    db.commit()
    db.close()

if __name__ == "__main__":
    criar_utilizadores()
