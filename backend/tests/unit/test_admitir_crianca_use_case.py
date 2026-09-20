import pytest
import os
from datetime import date
from app.application.use_cases.admitir_crianca import AdmitirCriancaUseCase, AdmitirCriancaInput
from app.application.interfaces.crianca_repository import ICriancaRepository
from app.application.interfaces.audit_logger import IAuditLogger
from app.infrastructure.security.crypto_service import CryptoService

class InMemoryCriancaRepository(ICriancaRepository):
    def __init__(self):
        self.registos = {}

    def salvar(self, crianca, alergias_cifradas):
        self.registos[crianca.id] = {
            "crianca": crianca,
            "alergias_cifradas": alergias_cifradas
        }

    def buscar_por_id(self, crianca_id):
        registo = self.registos.get(crianca_id)
        return registo["crianca"] if registo else None

class InMemoryAuditLogger(IAuditLogger):
    def __init__(self):
        self.eventos = []

    def registar_evento(self, operador_id, acao, recurso_id, ip):
        self.eventos.append({
            "operador_id": operador_id,
            "acao": acao,
            "recurso_id": recurso_id,
            "ip": ip
        })

def test_deve_admitir_crianca_e_registar_auditoria():
    repo = InMemoryCriancaRepository()
    audit = InMemoryAuditLogger()
    crypto = CryptoService(key_hex=os.urandom(32).hex())
    
    use_case = AdmitirCriancaUseCase(
        crianca_repository=repo,
        audit_logger=audit,
        crypto_service=crypto
    )
    
    dados_entrada = AdmitirCriancaInput(
        nome_completo="Ana Clara Santos",
        data_nascimento=date(2018, 5, 20),
        alergias="Dipirona",
        operador_id="user-admin-1",
        ip_origem="127.0.0.1"
    )
    
    crianca_id = use_case.execute(dados_entrada)
    
    assert crianca_id is not None
    assert crianca_id in repo.registos
    
    registo_guardado = repo.registos[crianca_id]
    assert registo_guardado["crianca"].nome_completo == "Ana Clara Santos"
    assert registo_guardado["alergias_cifradas"] != "Dipirona"
    assert crypto.decrypt(registo_guardado["alergias_cifradas"]) == "Dipirona"
    
    assert len(audit.eventos) == 1
    assert audit.eventos[0]["acao"] == "ADMISSAO_CRIANCA"
    assert audit.eventos[0]["operador_id"] == "user-admin-1"
