from abc import ABC, abstractmethod
from typing import Optional, List
from app.domain.entities.crianca import Crianca

class ICriancaRepository(ABC):
    @abstractmethod
    def salvar(self, crianca: Crianca, alergias_cifradas: Optional[str]) -> None:
        pass

    @abstractmethod
    def buscar_por_id(self, crianca_id: str) -> Optional[Crianca]:
        pass

    @abstractmethod
    def listar(self, termo_busca: Optional[str] = None) -> List[Crianca]:
        pass
