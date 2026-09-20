from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.entities.crianca import Crianca

class ICriancaRepository(ABC):
    @abstractmethod
    def salvar(self, crianca: Crianca) -> None:
        pass

    @abstractmethod
    def obter_por_id(self, crianca_id: str) -> Optional[Crianca]:
        pass

    @abstractmethod
    def listar_todas(self, termo_busca: Optional[str] = None) -> List[Crianca]:
        pass

# Alias para compatibilidade
CriancaRepository = ICriancaRepository
