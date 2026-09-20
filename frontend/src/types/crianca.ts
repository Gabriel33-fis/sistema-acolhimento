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

export interface CriancaDetalhada {
  id: string;
  nome_completo: string;
  data_nascimento: string;
  data_admissao: string;
  status_acolhimento: string;
  alergias_decifradas?: string | null;
  data_desligamento?: string | null;
  motivo_desligamento?: string | null;
  destino_desligamento?: string | null;
}

export interface RespostaAdmissao {
  id: string;
  mensagem: string;
}

export interface DesligamentoEntrada {
  data_desligamento: string;
  motivo: string;
  destino: string;
}

export interface EvolucaoEntrada {
  tipo: 'PEDAGOGICA' | 'COMPORTAMENTAL' | 'MEDICA';
  texto: string;
}

export interface EvolucaoItem {
  id: string;
  autor_nome: string;
  tipo: string;
  texto: string;
  criado_em: string;
  sigilosa: boolean;
}

export interface UtilizadorItem {
  id: string;
  nome: string;
  email: string;
  perfil: 'COORDENADOR' | 'OPERADOR';
}
