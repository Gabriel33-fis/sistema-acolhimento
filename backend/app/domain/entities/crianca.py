from datetime import date
from typing import Optional

class Crianca:
    def __init__(
        self,
        id: str,
        nome_completo: str,
        data_nascimento: date,
        data_admissao: date,
        status_acolhimento: str = "ACOLHIDO",
        alergias: Optional[str] = None
    ):
        self._id = id
        self._nome_completo = self._validar_nome(nome_completo)
        self._data_nascimento = self._validar_nascimento(data_nascimento)
        self._data_admissao = data_admissao
        self._status_acolhimento = status_acolhimento
        self._alergias = alergias

    @property
    def id(self) -> str:
        return self._id

    @property
    def nome_completo(self) -> str:
        return self._nome_completo

    @property
    def data_nascimento(self) -> date:
        return self._data_nascimento

    @property
    def data_admissao(self) -> date:
        return self._data_admissao

    @property
    def status_acolhimento(self) -> str:
        return self._status_acolhimento

    @property
    def alergias(self) -> Optional[str]:
        return self._alergias

    def _validar_nome(self, nome: str) -> str:
        nome_limpo = nome.strip()
        if len(nome_limpo) < 2:
            raise ValueError("O nome deve conter pelo menos 2 caracteres.")
        return nome_limpo

    def _validar_nascimento(self, nascimento: date) -> date:
        if nascimento > date.today():
            raise ValueError("A data de nascimento não pode estar no futuro.")
        return nascimento

    def registrar_desligamento(self) -> None:
        if self._status_acolhimento == "DESLIGADO":
            raise ValueError("A criança já consta como desligada da instituição.")
        self._status_acolhimento = "DESLIGADO"
