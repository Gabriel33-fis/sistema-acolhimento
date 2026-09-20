export interface CriancaEntrada {
  nome_completo: string;
  data_nascimento: string;
  alergias?: string;
}

export interface CriancaResumo {
  id: string;
  nome_completo: string;
  data_nascimento: string;
  data_admissao: string;
  status_acolhimento: string;
}

export interface CriancaDetalhada extends CriancaResumo {
  alergias_decifradas?: string | null;
}

export interface RespostaAdmissao {
  id: string;
  mensagem: string;
}
