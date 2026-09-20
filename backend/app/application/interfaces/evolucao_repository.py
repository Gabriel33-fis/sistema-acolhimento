from abc import ABC, abstractmethod
from typing import List
from app.domain.entities.evolucao import Evolucao

class IEvolucaoRepository(ABC):
    @abstractmethod
    def salvar(self, evolucao: Evolucao, texto_para_banco: str) -> None:
        pass

    @abstractmethod
    def listar_por_crianca(self, crianca_id: str) -> List[dict]:
        pass

EvolucaoRepository = IEvolucaoRepository
