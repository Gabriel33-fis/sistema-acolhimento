from abc import ABC, abstractmethod
from typing import Optional

class IAuditLogger(ABC):
    @abstractmethod
    def registrar(
        self,
        operador_id: str,
        acao: str,
        recurso: str,
        recurso_id: Optional[str] = None,
        ip_origem: Optional[str] = None,
        detalhes: Optional[str] = None
    ) -> None:
        pass

# Alias para compatibilidade com use cases que usam AuditLogger
AuditLogger = IAuditLogger
