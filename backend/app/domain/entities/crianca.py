from dataclasses import dataclass, field
from datetime import date
from typing import Optional

@dataclass
class Crianca:
    id: str
    nome_completo: str
    data_nascimento: date
    data_admissao: date = field(default_factory=date.today)
    status_acolhimento: str = "ACOLHIDO"
    alergias_cifradas: Optional[str] = None
    data_desligamento: Optional[date] = None
    motivo_desligamento: Optional[str] = None
    destino_desligamento: Optional[str] = None

    def __post_init__(self):
        nome_limpo = (self.nome_completo or "").strip()
        if len(nome_limpo) < 2:
            raise ValueError("O nome deve conter pelo menos 2 caracteres.")
        self.nome_completo = nome_limpo

        if self.data_nascimento > date.today():
            raise ValueError("A data de nascimento não pode estar no futuro.")

    def desacolher(self, data_saida: date, motivo: str, destino: str) -> None:
        if self.status_acolhimento == "DESACOLHIDO":
            raise ValueError("O acolhido já se encontra com status DESACOLHIDO.")
        
        if data_saida < self.data_admissao:
            raise ValueError("A data de desligamento não pode ser anterior à data de admissão.")

        if not motivo or len(motivo.strip()) < 3:
            raise ValueError("O motivo do desligamento deve ter no mínimo 3 caracteres.")

        if not destino or len(destino.strip()) < 3:
            raise ValueError("O destino/responsável deve ter no mínimo 3 caracteres.")

        self.status_acolhimento = "DESACOLHIDO"
        self.data_desligamento = data_saida
        self.motivo_desligamento = motivo.strip()
        self.destino_desligamento = destino.strip()

    def atualizar_dados(self, novo_nome: str, nova_data_nascimento: date, novas_alergias_cifradas: Optional[str]) -> None:
        nome_limpo = novo_nome.strip()
        if len(nome_limpo) < 2:
            raise ValueError("O nome completo deve conter no mínimo 2 caracteres.")

        if nova_data_nascimento > date.today():
            raise ValueError("A data de nascimento não pode estar no futuro.")

        self.nome_completo = nome_limpo
        self.data_nascimento = nova_data_nascimento
        self.alergias_cifradas = novas_alergias_cifradas
