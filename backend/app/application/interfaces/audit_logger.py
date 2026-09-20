from abc import ABC, abstractmethod

class IAuditLogger(ABC):
    @abstractmethod
    def registar_evento(self, operador_id: str, acao: str, recurso_id: str, ip: str) -> None:
        pass
