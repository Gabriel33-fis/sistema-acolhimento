import type { CriancaEntrada, CriancaResumo, CriancaDetalhada, RespostaAdmissao } from '../types/crianca';

const API_BASE_URL = 'http://127.0.0.1:8000/api/v1';

export interface RespostaLogin {
  access_token: string;
  token_type: string;
  nome: string;
  perfil: string;
}

export interface NovoUsuarioEntrada {
  nome: string;
  email: string;
  senha: string;
  perfil: 'COORDENADOR' | 'OPERADOR';
}

export function obterToken(): string | null {
  return localStorage.getItem('token_acolhimento');
}

export function salvarSessao(dados: RespostaLogin): void {
  localStorage.setItem('token_acolhimento', dados.access_token);
  localStorage.setItem('usuario_acolhimento', JSON.stringify({ nome: dados.nome, perfil: dados.perfil }));
}

export function limparSessao(): void {
  localStorage.removeItem('token_acolhimento');
  localStorage.removeItem('usuario_acolhimento');
}

export function obterUsuarioSalvo(): { nome: string; perfil: string } | null {
  const data = localStorage.getItem('usuario_acolhimento');
  return data ? JSON.parse(data) : null;
}

function obterCabecalhosAutenticados(): HeadersInit {
  const token = obterToken();
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
}

export async function autenticar(email: string, senha: string): Promise<RespostaLogin> {
  const resposta = await fetch(`${API_BASE_URL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, senha }),
  });

  if (!resposta.ok) {
    const erro = await resposta.json().catch(() => ({}));
    throw new Error(erro.detail || 'Falha ao autenticar.');
  }

  const dados = await resposta.json();
  salvarSessao(dados);
  return dados;
}

export async function cadastrarUsuario(dados: NovoUsuarioEntrada): Promise<{ mensagem: string; id: string }> {
  const resposta = await fetch(`${API_BASE_URL}/auth/registar`, {
    method: 'POST',
    headers: obterCabecalhosAutenticados(),
    body: JSON.stringify(dados),
  });

  if (!resposta.ok) {
    if (resposta.status === 401) {
      limparSessao();
      throw new Error('SessaoExpirada');
    }
    const erro = await resposta.json().catch(() => ({}));
    throw new Error(erro.detail || 'Erro ao registar utilizador.');
  }

  return resposta.json();
}

export async function admitirCrianca(dados: CriancaEntrada): Promise<RespostaAdmissao> {
  const resposta = await fetch(`${API_BASE_URL}/criancas/`, {
    method: 'POST',
    headers: obterCabecalhosAutenticados(),
    body: JSON.stringify(dados),
  });

  if (!resposta.ok) {
    const erro = await resposta.json().catch(() => ({}));
    throw new Error(erro.detail || 'Erro ao admitir acolhido');
  }

  return resposta.json();
}

export async function listarCriancas(termo?: string): Promise<CriancaResumo[]> {
  const url = termo 
    ? `${API_BASE_URL}/criancas/?busca=${encodeURIComponent(termo)}` 
    : `${API_BASE_URL}/criancas/`;

  const resposta = await fetch(url, {
    headers: obterCabecalhosAutenticados(),
  });

  if (!resposta.ok) {
    if (resposta.status === 401) {
      limparSessao();
      throw new Error('SessaoExpirada');
    }
    throw new Error('Erro ao listar acolhidos');
  }

  return resposta.json();
}

export async function obterCriancaPorId(id: string): Promise<CriancaDetalhada> {
  const resposta = await fetch(`${API_BASE_URL}/criancas/${id}`, {
    headers: obterCabecalhosAutenticados(),
  });

  if (!resposta.ok) {
    if (resposta.status === 401) {
      limparSessao();
      throw new Error('SessaoExpirada');
    }
    throw new Error('Erro ao obter dados do acolhido');
  }

  return resposta.json();
}
