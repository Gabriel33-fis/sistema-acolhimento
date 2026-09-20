import uuid
from dataclasses import dataclass
from app.domain.entities.evolucao import Evolucao
from app.application.interfaces.evolucao_repository import EvolucaoRepository
from app.application.interfaces.crianca_repository import CriancaRepository
from app.application.interfaces.audit_logger import AuditLogger
from app.infrastructure.security.crypto_service import CryptoService

@dataclass
class AdicionarEvolucaoInput:
    crianca_id: str
    autor_id: str
    autor_nome: str
    tipo: str
    texto: str
    ip_origem: str

class AdicionarEvolucaoUseCase:
    def __init__(
        self,
        evolucao_repo: EvolucaoRepository,
        crianca_repo: CriancaRepository,
        audit_logger: AuditLogger,
        crypto_service: CryptoService
    ):
        self.evolucao_repo = evolucao_repo
        self.crianca_repo = crianca_repo
        self.audit_logger = audit_logger
        self.crypto_service = crypto_service

    def execute(self, dados: AdicionarEvolucaoInput) -> str:
        crianca = self.crianca_repo.obter_por_id(dados.crianca_id)
        if not crianca:
            raise ValueError("Acolhido não encontrado.")

        evolucao_id = str(uuid.uuid4())
        evolucao = Evolucao.criar(
            id=evolucao_id,
            crianca_id=dados.crianca_id,
            autor_id=dados.autor_id,
            autor_nome=dados.autor_nome,
            tipo=dados.tipo,
            texto=dados.texto
        )

        # Se for nota médica, cifra em repouso
        if evolucao.tipo == "MEDICA":
            texto_para_banco = self.crypto_service.cifrar(evolucao.texto)
        else:
            texto_para_banco = evolucao.texto

        self.evolucao_repo.salvar(evolucao, texto_para_banco)

        self.audit_logger.registrar(
            operador_id=dados.autor_id,
            acao="CRIAR_EVOLUCAO",
            recurso="EVOLUCAO",
            recurso_id=evolucao_id,
            ip_origem=dados.ip_origem,
            detalhes=f"Registro de evolução do tipo '{evolucao.tipo}' inserido no prontuário."
        )

        return evolucao_id
