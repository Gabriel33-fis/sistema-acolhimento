import React, { useState, useEffect } from 'react';
import {
  Users,
  UserPlus,
  ShieldCheck,
  Search,
  FileSpreadsheet,
  Edit,
  Eye,
  LogOut,
  CheckCircle2,
  Lock,
  Globe,
  FileText,
  Scale,
  Calendar,
  HeartPulse,
  BookOpen,
  User,
  Trash2,
  X,
  Plus,
  BarChart3,
  Settings,
  History
} from 'lucide-react';

import { 
  admitirCrianca, 
  listarCriancas, 
  obterCriancaPorId, 
  atualizarCrianca, 
  autenticar, 
  obterToken, 
  limparSessao, 
  obterUsuarioSalvo,
  cadastrarUsuario,
  listarUtilizadores,
  alterarPerfilUtilizador,
  desligarCrianca,
  listarEvolucoes,
  adicionarEvolucao
} from './services/api';
import type { 
  CriancaEntrada, 
  CriancaResumo, 
  CriancaDetalhada, 
  DesligamentoEntrada,
  EvolucaoItem,
  EvolucaoEntrada,
  UtilizadorItem
} from './types/crianca';

interface NovoUsuarioForm {
  nome: string;
  email: string;
  senha: string;
  perfil: 'COORDENADOR' | 'OPERADOR';
}

export default function App() {
  const [token, setToken] = useState<string | null>(obterToken());
  const [usuario, setUsuario] = useState(obterUsuarioSalvo());

  const perfilNormalizado = (usuario?.perfil || '').toUpperCase().trim();

  // Login
  const [loginEmail, setLoginEmail] = useState('admin@instituicao.org');
  const [loginSenha, setLoginSenha] = useState('admin123');
  const [loginErro, setLoginErro] = useState<string | null>(null);
  const [loginCarregando, setLoginCarregando] = useState(false);

  // Módulo Ativo
  const [moduloAtivo, setModuloAtivo] = useState<'acolhidos' | 'admissao' | 'equipe'>('acolhidos');
  
  // Abas do formulário
  const [abaFormAdmissao, setAbaFormAdmissao] = useState<'geral' | 'saude' | 'processual'>('geral');

  // Dados
  const [criancas, setCriancas] = useState<CriancaResumo[]>([]);
  const [busca, setBusca] = useState('');
  const [utilizadores, setUtilizadores] = useState<UtilizadorItem[]>([]);
  const [carregandoEquipe, setCarregandoEquipe] = useState(false);

  // Admissão Form
  const [formData, setFormData] = useState<CriancaEntrada>({
    nome_completo: '',
    data_nascimento: '',
    alergias: '',
  });

  // Edição Modal
  const [criancaEditando, setCriancaEditando] = useState<CriancaDetalhada | null>(null);
  const [formEdicao, setFormEdicao] = useState<CriancaEntrada>({
    nome_completo: '',
    data_nascimento: '',
    alergias: '',
  });
  const [salvandoEdicao, setSalvandoEdicao] = useState(false);
  const [erroEdicao, setErroEdicao] = useState<string | null>(null);

  // Equipe Form
  const [formUser, setFormUser] = useState<NovoUsuarioForm>({
    nome: '',
    email: '',
    senha: '',
    perfil: 'OPERADOR',
  });
  const [feedbackUser, setFeedbackUser] = useState<{ tipo: 'sucesso' | 'erro'; texto: string } | null>(null);
  const [carregandoUser, setCarregandoUser] = useState(false);

  // Desligamento Modal
  const [criancaParaDesligar, setCriancaParaDesligar] = useState<CriancaResumo | null>(null);
  const [formDesligamento, setFormDesligamento] = useState<DesligamentoEntrada>({
    data_desligamento: new Date().toISOString().split('T')[0],
    motivo: '',
    destino: '',
  });
  const [carregandoDesligamento, setCarregandoDesligamento] = useState(false);
  const [erroDesligamento, setErroDesligamento] = useState<string | null>(null);

  // Ficha & Evoluções Modal
  const [selecionada, setSelecionada] = useState<CriancaDetalhada | null>(null);
  const [carregandoDetalhe, setCarregandoDetalhe] = useState(false);
  const [evolucoes, setEvolucoes] = useState<EvolucaoItem[]>([]);
  const [carregandoEvolucoes, setCarregandoEvolucoes] = useState(false);
  const [formEvolucao, setFormEvolucao] = useState<EvolucaoEntrada>({
    tipo: 'COMPORTAMENTAL',
    texto: '',
  });
  const [salvandoEvolucao, setSalvandoEvolucao] = useState(false);
  const [erroEvolucao, setErroEvolucao] = useState<string | null>(null);

  const [feedback, setFeedback] = useState<{ tipo: 'sucesso' | 'erro'; texto: string } | null>(null);
  const [carregando, setCarregando] = useState(false);

  const carregarLista = async (termoFiltro = '') => {
    if (!token) return;
    try {
      const dados = await listarCriancas(termoFiltro);
      setCriancas(dados);
    } catch (err: any) {
      if (err.message === 'SessaoExpirada') handleLogout();
    }
  };

  const carregarEquipe = async () => {
    if (!token) return;
    setCarregandoEquipe(true);
    try {
      const lista = await listarUtilizadores();
      setUtilizadores(lista);
    } catch (err: any) {
      if (err.message === 'SessaoExpirada') handleLogout();
    } finally {
      setCarregandoEquipe(false);
    }
  };

  useEffect(() => {
    if (token) {
      if (moduloAtivo === 'acolhidos') {
        carregarLista(busca);
      } else if (moduloAtivo === 'equipe') {
        carregarEquipe();
      }
    }
  }, [busca, moduloAtivo, token]);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoginCarregando(true);
    setLoginErro(null);
    try {
      const resposta = await autenticar(loginEmail, loginSenha);
      setToken(resposta.access_token);
      setUsuario({ nome: resposta.nome, perfil: resposta.perfil });
    } catch (err: any) {
      setLoginErro(err.message);
    } finally {
      setLoginCarregando(false);
    }
  };

  const handleLogout = () => {
    limparSessao();
    setToken(null);
    setUsuario(null);
    setModuloAtivo('acolhidos');
    setSelecionada(null);
    setCriancaParaDesligar(null);
    setCriancaEditando(null);
  };

  const handleSubmitAdmissao = async (e: React.FormEvent) => {
    e.preventDefault();
    setCarregando(true);
    setFeedback(null);
    try {
      const payload: CriancaEntrada = {
        nome_completo: formData.nome_completo,
        data_nascimento: formData.data_nascimento,
        alergias: formData.alergias?.trim() ? formData.alergias : undefined,
      };
      const res = await admitirCrianca(payload);
      setFeedback({ tipo: 'sucesso', texto: `${res.mensagem} ID: ${res.id}` });
      setFormData({ nome_completo: '', data_nascimento: '', alergias: '' });
      await carregarLista();
    } catch (err: any) {
      if (err.message === 'SessaoExpirada') {
        handleLogout();
        return;
      }
      setFeedback({ tipo: 'erro', texto: err.message });
    } finally {
      setCarregando(false);
    }
  };

  const handleAbrirEdicao = async (id: string) => {
    try {
      const detalhe = await obterCriancaPorId(id);
      setCriancaEditando(detalhe);
      setFormEdicao({
        nome_completo: detalhe.nome_completo,
        data_nascimento: detalhe.data_nascimento,
        alergias: detalhe.alergias_decifradas || '',
      });
      setErroEdicao(null);
    } catch (err: any) {
      alert('Acesso negado ou erro ao carregar os dados para edição.');
    }
  };

  const handleSalvarEdicao = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!criancaEditando) return;
    setSalvandoEdicao(true);
    setErroEdicao(null);
    try {
      await atualizarCrianca(criancaEditando.id, formEdicao);
      setCriancaEditando(null);
      await carregarLista(busca);
    } catch (err: any) {
      if (err.message === 'SessaoExpirada') {
        handleLogout();
        return;
      }
      setErroEdicao(err.message);
    } finally {
      setSalvandoEdicao(false);
    }
  };

  const handleCadastrarUser = async (e: React.FormEvent) => {
    e.preventDefault();
    setCarregandoUser(true);
    setFeedbackUser(null);
    try {
      const res = await cadastrarUsuario(formUser);
      setFeedbackUser({ tipo: 'sucesso', texto: res.mensagem });
      setFormUser({ nome: '', email: '', senha: '', perfil: 'OPERADOR' });
      await carregarEquipe();
    } catch (err: any) {
      if (err.message === 'SessaoExpirada') {
        handleLogout();
        return;
      }
      setFeedbackUser({ tipo: 'erro', texto: err.message });
    } finally {
      setCarregandoUser(false);
    }
  };

  const handleAlternarPerfil = async (id: string, perfilAtual: 'COORDENADOR' | 'OPERADOR') => {
    const novoPerfil = perfilAtual === 'COORDENADOR' ? 'OPERADOR' : 'COORDENADOR';
    try {
      await alterarPerfilUtilizador(id, novoPerfil);
      await carregarEquipe();
    } catch (err: any) {
      alert(err.message || 'Erro ao alterar perfil');
    }
  };

  const handleConfirmarDesligamento = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!criancaParaDesligar) return;
    setCarregandoDesligamento(true);
    setErroDesligamento(null);
    try {
      await desligarCrianca(criancaParaDesligar.id, formDesligamento);
      setCriancaParaDesligar(null);
      setFormDesligamento({
        data_desligamento: new Date().toISOString().split('T')[0],
        motivo: '',
        destino: '',
      });
      await carregarLista(busca);
    } catch (err: any) {
      if (err.message === 'SessaoExpirada') {
        handleLogout();
        return;
      }
      setErroDesligamento(err.message);
    } finally {
      setCarregandoDesligamento(false);
    }
  };

  const carregarHistoricoEvolucoes = async (id: string) => {
    setCarregandoEvolucoes(true);
    try {
      const lista = await listarEvolucoes(id);
      setEvolucoes(lista);
    } catch (err: any) {
      console.error(err);
    } finally {
      setCarregandoEvolucoes(false);
    }
  };

  const handleVerFicha = async (id: string) => {
    setCarregandoDetalhe(true);
    try {
      const detalhe = await obterCriancaPorId(id);
      setSelecionada(detalhe);
      await carregarHistoricoEvolucoes(id);
    } catch (err: any) {
      if (err.message === 'SessaoExpirada') {
        handleLogout();
        return;
      }
      alert('Não foi possível carregar o prontuário.');
    } finally {
      setCarregandoDetalhe(false);
    }
  };

  const handleSalvarEvolucao = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selecionada) return;
    setSalvandoEvolucao(true);
    setErroEvolucao(null);
    try {
      await adicionarEvolucao(selecionada.id, formEvolucao);
      setFormEvolucao({ tipo: 'COMPORTAMENTAL', texto: '' });
      await carregarHistoricoEvolucoes(selecionada.id);
    } catch (err: any) {
      if (err.message === 'SessaoExpirada') {
        handleLogout();
        return;
      }
      setErroEvolucao(err.message);
    } finally {
      setSalvandoEvolucao(false);
    }
  };

  // TELA DE LOGIN
  if (!token) {
    return (
      <div className="min-h-screen bg-[#f0f4f7] flex items-center justify-center p-4 font-sans">
        <div className="max-w-md w-full bg-white rounded-lg shadow-lg border border-slate-300 overflow-hidden">
          <div className="bg-[#007b99] px-6 py-5 text-white flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-full bg-white flex items-center justify-center text-[#007b99] shadow-xs">
                <CheckCircle2 className="w-5 h-5 text-[#007b99]" />
              </div>
              <span className="text-xl font-bold tracking-tight">Acolhimento<span className="font-light">Gestão</span></span>
            </div>
            <span className="text-xs bg-[#005f77] px-2.5 py-1 rounded font-semibold flex items-center gap-1">
              <Lock className="w-3.5 h-3.5" /> v1.0
            </span>
          </div>

          <div className="p-8">
            <div className="mb-6">
              <h2 className="text-lg font-bold text-slate-800 uppercase tracking-wide">Acesso ao Sistema</h2>
              <p className="text-xs text-slate-500 mt-0.5">Informe suas credenciais institucionais para iniciar a sessão</p>
            </div>

            {loginErro && (
              <div className="mb-4 p-3 bg-red-50 border-l-4 border-red-500 text-red-700 text-xs font-medium">
                {loginErro}
              </div>
            )}

            <form onSubmit={handleLogin} className="space-y-4 text-xs">
              <div>
                <label className="block text-slate-700 font-bold uppercase mb-1">E-mail Corporativo</label>
                <input
                  type="email"
                  required
                  value={loginEmail}
                  onChange={(e) => setLoginEmail(e.target.value)}
                  className="w-full px-3 py-2.5 border border-slate-300 rounded text-sm text-slate-800 focus:outline-none focus:border-[#00a887]"
                />
              </div>

              <div>
                <label className="block text-slate-700 font-bold uppercase mb-1">Senha de Acesso</label>
                <input
                  type="password"
                  required
                  value={loginSenha}
                  onChange={(e) => setLoginSenha(e.target.value)}
                  className="w-full px-3 py-2.5 border border-slate-300 rounded text-sm text-slate-800 focus:outline-none focus:border-[#00a887]"
                />
              </div>

              <button
                type="submit"
                disabled={loginCarregando}
                className="w-full mt-2 bg-[#00a887] hover:bg-[#008f73] text-white font-bold py-2.5 rounded text-sm transition cursor-pointer disabled:opacity-50 uppercase tracking-wider flex items-center justify-center gap-2"
              >
                <Lock className="w-4 h-4" />
                {loginCarregando ? 'Autenticando...' : 'Entrar no Sistema'}
              </button>
            </form>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#f4f6f9] text-slate-800 flex flex-col font-sans">
      {/* 1. TOP NAVBAR */}
      <header className="h-14 bg-[#007b99] text-white flex items-center justify-between px-4 sm:px-6 shadow-md z-20">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-white flex items-center justify-center text-[#007b99] shadow-xs">
            <CheckCircle2 className="w-5 h-5 text-[#007b99]" />
          </div>
          <span className="text-xl font-bold tracking-tight">
            Acolhimento<span className="font-light text-slate-200">Gestão</span>
          </span>
          <span className="hidden md:inline-block ml-4 text-xs font-normal text-slate-200 border-l border-white/20 pl-4">
            Gestão Institucional de Acolhimento e Prontuários Seguros
          </span>
        </div>

        <div className="flex items-center gap-4 text-xs">
          <span className="hidden sm:inline-flex items-center gap-1.5 bg-[#005f77] px-2.5 py-1 rounded text-slate-200">
            <ShieldCheck className="w-4 h-4 text-emerald-300" />
            AES-GCM 256-bit
          </span>
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-full bg-slate-200 text-slate-800 font-bold flex items-center justify-center uppercase text-xs">
              {usuario?.nome?.charAt(0) || 'U'}
            </div>
            <div className="text-right">
              <span className="block font-bold leading-tight">{usuario?.nome || 'Operador'}</span>
              <span className="text-[10px] text-slate-200 block uppercase font-medium">
                {perfilNormalizado || 'COORDENADOR'}
              </span>
            </div>
          </div>
          <button
            onClick={handleLogout}
            title="Encerrar Sessão"
            className="bg-[#005f77] hover:bg-[#004b5e] px-2.5 py-1.5 rounded transition cursor-pointer text-white flex items-center gap-1 font-medium"
          >
            <LogOut className="w-3.5 h-3.5" />
            <span>Sair</span>
          </button>
        </div>
      </header>

      {/* CORPO: SIDEBAR + MAIN */}
      <div className="flex flex-1 overflow-hidden">
        {/* 2. SIDEBAR COM ÍCONES OUTLINE */}
        <aside className="w-60 bg-white border-r border-slate-200 flex flex-col justify-between shrink-0 shadow-xs">
          <div className="py-2">
            <nav className="space-y-0.5">
              <button
                onClick={() => setModuloAtivo('acolhidos')}
                className={`w-full flex items-center justify-between px-4 py-2.5 text-xs font-semibold transition cursor-pointer ${
                  moduloAtivo === 'acolhidos'
                    ? 'bg-[#00a887] text-white'
                    : 'text-slate-600 hover:bg-slate-50'
                }`}
              >
                <div className="flex items-center gap-3">
                  <Users className="w-4 h-4" />
                  <span>Acolhidos / Residentes</span>
                </div>
                <span className="text-[10px] opacity-75">&gt;</span>
              </button>

              <button
                onClick={() => {
                  setModuloAtivo('admissao');
                  setFeedback(null);
                }}
                className={`w-full flex items-center justify-between px-4 py-2.5 text-xs font-semibold transition cursor-pointer ${
                  moduloAtivo === 'admissao'
                    ? 'bg-[#00a887] text-white'
                    : 'text-slate-600 hover:bg-slate-50'
                }`}
              >
                <div className="flex items-center gap-3">
                  <UserPlus className="w-4 h-4" />
                  <span>Nova Admissão</span>
                </div>
                <span className="text-[10px] opacity-75">&gt;</span>
              </button>

              <button
                onClick={() => setModuloAtivo('equipe')}
                className={`w-full flex items-center justify-between px-4 py-2.5 text-xs font-semibold transition cursor-pointer ${
                  moduloAtivo === 'equipe'
                    ? 'bg-[#00a887] text-white'
                    : 'text-slate-600 hover:bg-slate-50'
                }`}
              >
                <div className="flex items-center gap-3">
                  <ShieldCheck className="w-4 h-4" />
                  <span>Equipe & Acessos</span>
                </div>
                <span className="text-[10px] opacity-75">&gt;</span>
              </button>

              <div className="pt-4 px-4 pb-1">
                <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Administrativo</span>
              </div>

              <div className="px-4 py-2 text-xs text-slate-400 flex items-center gap-3 cursor-not-allowed">
                <BarChart3 className="w-4 h-4 text-slate-400" />
                <span>Análise e Estatísticas</span>
              </div>
              <div className="px-4 py-2 text-xs text-slate-400 flex items-center gap-3 cursor-not-allowed">
                <History className="w-4 h-4 text-slate-400" />
                <span>Auditoria do Sistema</span>
              </div>
              <div className="px-4 py-2 text-xs text-slate-400 flex items-center gap-3 cursor-not-allowed">
                <Settings className="w-4 h-4 text-slate-400" />
                <span>Configurações Gerais</span>
              </div>
            </nav>
          </div>

          <div className="p-4 border-t border-slate-100 text-[11px] text-slate-400">
            Fatec Shunji Nishimura<br />
            Projeto Integrador IV
          </div>
        </aside>

        {/* 3. CONTEÚDO PRINCIPAL */}
        <main className="flex-1 p-6 overflow-y-auto">
          {/* MÓDULO 1: ACOLHIDOS */}
          {moduloAtivo === 'acolhidos' && (
            <div className="space-y-6">
              {/* Barra de Ações Rápidas */}
              <div className="bg-white rounded-sm border border-slate-200 p-5 shadow-xs">
                <h2 className="text-base font-bold text-[#007b99] uppercase tracking-wide mb-4">
                  Acolhidos & Residentes
                </h2>

                <div className="flex flex-col lg:flex-row items-stretch lg:items-center gap-3 text-xs">
                  <button
                    onClick={() => {
                      setModuloAtivo('admissao');
                      setFeedback(null);
                    }}
                    className="bg-[#0088cc] hover:bg-[#0077b3] text-white font-bold px-4 py-2 rounded flex items-center justify-center gap-2 uppercase tracking-wide cursor-pointer"
                  >
                    <Plus className="w-4 h-4" /> NOVO ACOLHIDO
                  </button>

                  <div className="flex-1 flex items-center gap-0">
                    <input
                      type="text"
                      placeholder="Pesquisar por nome do acolhido..."
                      value={busca}
                      onChange={(e) => setBusca(e.target.value)}
                      className="w-full px-3 py-2 border border-slate-300 border-r-0 rounded-l text-xs text-slate-800 focus:outline-none focus:border-[#00a887]"
                    />
                    <button
                      onClick={() => carregarLista(busca)}
                      className="bg-[#00a887] hover:bg-[#008f73] text-white font-bold px-4 py-2 rounded-r flex items-center gap-1.5 uppercase tracking-wide cursor-pointer"
                    >
                      <Search className="w-3.5 h-3.5" /> PESQUISAR
                    </button>
                  </div>

                  <button
                    onClick={() => {
                      const csvHeader = "ID,Nome,Nascimento,Admissao,Status\n";
                      const csvRows = criancas.map(c => `"${c.id}","${c.nome_completo}","${c.data_nascimento}","${c.data_admissao}","${c.status_acolhimento}"`).join("\n");
                      const blob = new Blob([csvHeader + csvRows], { type: 'text/csv;charset=utf-8;' });
                      const url = URL.createObjectURL(blob);
                      const link = document.createElement("a");
                      link.setAttribute("href", url);
                      link.setAttribute("download", `relatorio_acolhidos_${new Date().toISOString().split('T')[0]}.csv`);
                      document.body.appendChild(link);
                      link.click();
                      document.body.removeChild(link);
                    }}
                    className="bg-[#2f3d4a] hover:bg-[#232e38] text-white font-semibold px-3 py-2 rounded flex items-center justify-center gap-1.5 uppercase cursor-pointer"
                  >
                    <FileSpreadsheet className="w-4 h-4" /> EXPORTAR EXCEL / CSV
                  </button>

                  <div className="flex items-center bg-[#2f3d4a] text-white rounded overflow-hidden">
                    <span className="bg-[#1f2933] px-2.5 py-2 font-bold uppercase text-[10px] tracking-wider">
                      TOTAL
                    </span>
                    <span className="px-3 py-2 font-bold text-slate-100">
                      {criancas.length} acolhido(s)
                    </span>
                  </div>
                </div>
              </div>

              {/* Tabela de Acolhidos */}
              <div className="bg-white rounded-sm border border-slate-200 shadow-xs">
                <div className="px-5 py-4 border-b border-slate-100 flex items-center justify-between">
                  <h3 className="text-xs font-bold text-slate-700 uppercase tracking-wide">
                    Listagem de Residentes Cadastrados
                  </h3>
                </div>

                {criancas.length === 0 ? (
                  <div className="p-8 text-center text-xs text-slate-400">
                    Nenhum residente cadastrado no momento ou encontrado para o termo pesquisado.
                  </div>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="w-full text-left text-xs text-slate-600 border-collapse">
                      <thead className="bg-[#f9fafb] text-slate-700 font-bold uppercase border-b border-slate-200">
                        <tr>
                          <th className="py-3 px-4">Nome Completo</th>
                          <th className="py-3 px-4">Data de Nascimento</th>
                          <th className="py-3 px-4">Data de Admissão</th>
                          <th className="py-3 px-4">Estado Atual</th>
                          <th className="py-3 px-4 text-right">Ações Cadastrais</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-100">
                        {criancas.map((item) => (
                          <tr key={item.id} className="hover:bg-slate-50 transition">
                            <td className="py-3 px-4 font-semibold text-slate-900 flex items-center gap-2">
                              <span className="w-6 h-6 rounded-full bg-slate-200 text-slate-700 font-bold text-[10px] flex items-center justify-center">
                                {item.nome_completo.charAt(0)}
                              </span>
                              {item.nome_completo}
                            </td>
                            <td className="py-3 px-4">{item.data_nascimento}</td>
                            <td className="py-3 px-4">{item.data_admissao}</td>
                            <td className="py-3 px-4">
                              {item.status_acolhimento === 'ACOLHIDO' ? (
                                <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-bold bg-emerald-100 text-emerald-800">
                                  ● Acolhido
                                </span>
                              ) : (
                                <span className="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-bold bg-slate-200 text-slate-700">
                                  ○ Desacolhido
                                </span>
                              )}
                            </td>
                            <td className="py-3 px-4 text-right space-x-1">
                              <button
                                onClick={() => handleVerFicha(item.id)}
                                disabled={carregandoDetalhe}
                                className="bg-slate-100 hover:bg-slate-200 text-slate-700 font-semibold px-2.5 py-1.5 rounded transition cursor-pointer inline-flex items-center gap-1"
                              >
                                <Eye className="w-3.5 h-3.5 text-slate-600" />
                                Ficha & Evoluções
                              </button>

                              <button
                                onClick={() => handleAbrirEdicao(item.id)}
                                className="bg-[#0088cc] hover:bg-[#0077b3] text-white font-semibold px-3 py-1.5 rounded transition cursor-pointer inline-flex items-center gap-1"
                              >
                                <Edit className="w-3.5 h-3.5 text-white" />
                                Editar
                              </button>

                              {item.status_acolhimento === 'ACOLHIDO' && (
                                <button
                                  onClick={() => {
                                    setCriancaParaDesligar(item);
                                    setErroDesligamento(null);
                                  }}
                                  className="bg-amber-100 hover:bg-amber-200 text-amber-900 font-semibold px-2.5 py-1.5 rounded transition cursor-pointer inline-flex items-center gap-1"
                                >
                                  <LogOut className="w-3.5 h-3.5 text-amber-800" />
                                  Dar Saída
                                </button>
                              )}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* MÓDULO 2: CADASTRO COM ABAS E ÍCONES OUTLINE */}
          {moduloAtivo === 'admissao' && (
            <div className="bg-white rounded-sm border border-slate-200 shadow-xs">
              <div className="p-5 border-b border-slate-200">
                <h2 className="text-base font-bold text-[#007b99] uppercase tracking-wide">
                  Cadastro de Acolhidos
                </h2>
              </div>

              {/* Abas com Ícones Outline */}
              <div className="flex border-b border-slate-200 bg-[#f9fafb] px-4 text-xs font-semibold">
                <button
                  type="button"
                  onClick={() => setAbaFormAdmissao('geral')}
                  className={`py-3 px-4 flex items-center gap-2 cursor-pointer border-t-2 ${
                    abaFormAdmissao === 'geral'
                      ? 'border-red-500 bg-white text-slate-800 font-bold -mb-[1px] border-x border-slate-200'
                      : 'border-transparent text-slate-500 hover:text-slate-800'
                  }`}
                >
                  <Globe className="w-4 h-4 text-slate-600" />
                  Geral
                </button>
                <button
                  type="button"
                  onClick={() => setAbaFormAdmissao('saude')}
                  className={`py-3 px-4 flex items-center gap-2 cursor-pointer border-t-2 ${
                    abaFormAdmissao === 'saude'
                      ? 'border-red-500 bg-white text-slate-800 font-bold -mb-[1px] border-x border-slate-200'
                      : 'border-transparent text-slate-500 hover:text-slate-800'
                  }`}
                >
                  <ShieldCheck className="w-4 h-4 text-emerald-600" />
                  Prontuário & Saúde (Cifrado)
                </button>
                <button
                  type="button"
                  onClick={() => setAbaFormAdmissao('processual')}
                  className={`py-3 px-4 flex items-center gap-2 cursor-pointer border-t-2 ${
                    abaFormAdmissao === 'processual'
                      ? 'border-red-500 bg-white text-slate-800 font-bold -mb-[1px] border-x border-slate-200'
                      : 'border-transparent text-slate-500 hover:text-slate-800'
                  }`}
                >
                  <Scale className="w-4 h-4 text-slate-600" />
                  Processual / Vara da Infância
                </button>
              </div>

              <div className="p-6">
                {feedback && (
                  <div
                    className={`p-3 rounded mb-6 text-xs font-medium ${
                      feedback.tipo === 'sucesso'
                        ? 'bg-emerald-50 text-emerald-800 border-l-4 border-emerald-500'
                        : 'bg-red-50 text-red-800 border-l-4 border-red-500'
                    }`}
                  >
                    {feedback.texto}
                  </div>
                )}

                <form onSubmit={handleSubmitAdmissao}>
                  {abaFormAdmissao === 'geral' && (
                    <div className="space-y-4 text-xs">
                      <div>
                        <label className="block text-slate-700 font-bold uppercase mb-1">Nome Completo *</label>
                        <input
                          type="text"
                          required
                          minLength={2}
                          value={formData.nome_completo}
                          onChange={(e) => setFormData({ ...formData, nome_completo: e.target.value })}
                          placeholder="Informe o nome completo da criança ou adolescente..."
                          className="w-full px-3 py-2 border border-slate-300 rounded text-slate-800 focus:outline-none focus:border-[#00a887]"
                        />
                      </div>

                      <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
                        <div>
                          <label className="block text-slate-700 font-bold uppercase mb-1">CPF</label>
                          <input
                            type="text"
                            placeholder="000.000.000-00"
                            className="w-full px-3 py-2 border border-slate-300 rounded text-slate-800 focus:outline-none focus:border-[#00a887]"
                          />
                        </div>
                        <div>
                          <label className="block text-slate-700 font-bold uppercase mb-1">RG</label>
                          <input
                            type="text"
                            placeholder="00.000.000-0"
                            className="w-full px-3 py-2 border border-slate-300 rounded text-slate-800 focus:outline-none focus:border-[#00a887]"
                          />
                        </div>
                        <div>
                          <label className="block text-slate-700 font-bold uppercase mb-1">Certidão de Nascimento</label>
                          <input
                            type="text"
                            placeholder="Matrícula do Registro Civil"
                            className="w-full px-3 py-2 border border-slate-300 rounded text-slate-800 focus:outline-none focus:border-[#00a887]"
                          />
                        </div>
                        <div>
                          <label className="block text-slate-700 font-bold uppercase mb-1">Data Nascimento *</label>
                          <input
                            type="date"
                            required
                            value={formData.data_nascimento}
                            onChange={(e) => setFormData({ ...formData, data_nascimento: e.target.value })}
                            className="w-full px-3 py-2 border border-slate-300 rounded text-slate-800 focus:outline-none focus:border-[#00a887]"
                          />
                        </div>
                      </div>
                    </div>
                  )}

                  {abaFormAdmissao === 'saude' && (
                    <div className="space-y-4 text-xs">
                      <div className="p-3 bg-blue-50 border border-blue-200 rounded text-blue-900 flex items-start gap-2.5">
                        <ShieldCheck className="w-5 h-5 text-blue-700 shrink-0 mt-0.5" />
                        <div>
                          <strong>Proteção Criptográfica Ativa (AES-GCM):</strong>
                          <p className="mt-0.5 text-[11px] text-blue-700">
                            Os dados clínicos são cifrados no banco de dados. Apenas Coordenadores autorizados podem decifrá-los e visualizá-los.
                          </p>
                        </div>
                      </div>

                      <div>
                        <label className="block text-slate-700 font-bold uppercase mb-1">
                          Alergias Alimentares, Medicamentosas ou Restrições Clínicas
                        </label>
                        <textarea
                          rows={3}
                          value={formData.alergias}
                          onChange={(e) => setFormData({ ...formData, alergias: e.target.value })}
                          placeholder="Ex: Alergia a derivados de leite (lactose), histórico de asma brônquica ou necessidade de medicação contínua..."
                          className="w-full px-3 py-2 border border-slate-300 rounded text-slate-800 focus:outline-none focus:border-[#00a887]"
                        />
                      </div>
                    </div>
                  )}

                  {abaFormAdmissao === 'processual' && (
                    <div className="space-y-4 text-xs">
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        <div>
                          <label className="block text-slate-700 font-bold uppercase mb-1">Vara da Infância e Juventude</label>
                          <input
                            type="text"
                            placeholder="Ex: 1ª Vara da Família e Sucessões"
                            className="w-full px-3 py-2 border border-slate-300 rounded text-slate-800 focus:outline-none focus:border-[#00a887]"
                          />
                        </div>
                        <div>
                          <label className="block text-slate-700 font-bold uppercase mb-1">Número da Guia de Acolhimento</label>
                          <input
                            type="text"
                            placeholder="Ex: GUIA-2026/0091"
                            className="w-full px-3 py-2 border border-slate-300 rounded text-slate-800 focus:outline-none focus:border-[#00a887]"
                          />
                        </div>
                      </div>
                      <div>
                        <label className="block text-slate-700 font-bold uppercase mb-1">Histórico Familiar / Medida Protetiva</label>
                        <textarea
                          rows={2}
                          placeholder="Medida protetiva de urgência aplicada com base no Art. 101 do ECA..."
                          className="w-full px-3 py-2 border border-slate-300 rounded text-slate-800 focus:outline-none focus:border-[#00a887]"
                        />
                      </div>
                    </div>
                  )}

                  {/* Rodapé Form */}
                  <div className="mt-8 pt-4 border-t border-slate-200 flex items-center gap-3">
                    <button
                      type="submit"
                      disabled={carregando}
                      className="bg-[#00a887] hover:bg-[#008f73] text-white font-bold px-5 py-2.5 rounded text-xs transition cursor-pointer flex items-center gap-2 uppercase tracking-wide disabled:opacity-50"
                    >
                      <CheckCircle2 className="w-4 h-4" />
                      {carregando ? 'Salvando...' : 'SALVAR'}
                    </button>

                    <button
                      type="button"
                      onClick={() => {
                        setFormData({ nome_completo: '', data_nascimento: '', alergias: '' });
                        setFeedback(null);
                      }}
                      className="bg-[#0088cc] hover:bg-[#0077b3] text-white font-bold px-4 py-2.5 rounded text-xs transition cursor-pointer flex items-center gap-1.5 uppercase tracking-wide"
                    >
                      <Plus className="w-4 h-4" /> LIMPAR CAMPOS
                    </button>
                  </div>
                </form>
              </div>
            </div>
          )}

          {/* MÓDULO 3: EQUIPE */}
          {moduloAtivo === 'equipe' && (
            <div className="space-y-6">
              <div className="bg-white rounded-sm border border-slate-200 p-5 shadow-xs">
                <h2 className="text-base font-bold text-[#007b99] uppercase tracking-wide mb-1">
                  Equipe & Controle de Acesso (RBAC)
                </h2>
                <p className="text-xs text-slate-500 mb-6">
                  Cadastre novos operadores e gerencie permissões institucionais.
                </p>

                {feedbackUser && (
                  <div
                    className={`p-3 rounded mb-4 text-xs font-medium ${
                      feedbackUser.tipo === 'sucesso'
                        ? 'bg-emerald-50 text-emerald-800 border-l-4 border-emerald-500'
                        : 'bg-red-50 text-red-800 border-l-4 border-red-500'
                    }`}
                  >
                    {feedbackUser.texto}
                  </div>
                )}

                <form onSubmit={handleCadastrarUser} className="space-y-4 text-xs max-w-2xl">
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-slate-700 font-bold uppercase mb-1">Nome do Colaborador *</label>
                      <input
                        type="text"
                        required
                        value={formUser.nome}
                        onChange={(e) => setFormUser({ ...formUser, nome: e.target.value })}
                        placeholder="Ex: Juliana Santos"
                        className="w-full px-3 py-2 border border-slate-300 rounded text-slate-800 focus:outline-none focus:border-[#00a887]"
                      />
                    </div>
                    <div>
                      <label className="block text-slate-700 font-bold uppercase mb-1">E-mail Institucional *</label>
                      <input
                        type="email"
                        required
                        value={formUser.email}
                        onChange={(e) => setFormUser({ ...formUser, email: e.target.value })}
                        placeholder="operador@instituicao.org"
                        className="w-full px-3 py-2 border border-slate-300 rounded text-slate-800 focus:outline-none focus:border-[#00a887]"
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-slate-700 font-bold uppercase mb-1">Senha Inicial *</label>
                      <input
                        type="password"
                        required
                        minLength={6}
                        value={formUser.senha}
                        onChange={(e) => setFormUser({ ...formUser, senha: e.target.value })}
                        placeholder="Mínimo 6 caracteres"
                        className="w-full px-3 py-2 border border-slate-300 rounded text-slate-800 focus:outline-none focus:border-[#00a887]"
                      />
                    </div>
                    <div>
                      <label className="block text-slate-700 font-bold uppercase mb-1">Perfil de Acesso *</label>
                      <select
                        value={formUser.perfil}
                        onChange={(e) => setFormUser({ ...formUser, perfil: e.target.value as any })}
                        className="w-full px-3 py-2 border border-slate-300 rounded text-slate-800 bg-white focus:outline-none focus:border-[#00a887]"
                      >
                        <option value="OPERADOR">OPERADOR (Acesso Padrão)</option>
                        <option value="COORDENADOR">COORDENADOR (Acesso Total + Prontuários)</option>
                      </select>
                    </div>
                  </div>

                  <button
                    type="submit"
                    disabled={carregandoUser}
                    className="bg-[#00a887] hover:bg-[#008f73] text-white font-bold px-4 py-2 rounded transition cursor-pointer uppercase text-xs disabled:opacity-50 inline-flex items-center gap-1.5"
                  >
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    {carregandoUser ? 'Cadastrando...' : 'REGISTAR UTILIZADOR'}
                  </button>
                </form>
              </div>

              {/* Tabela de Utilizadores */}
              <div className="bg-white rounded-sm border border-slate-200 shadow-xs">
                <div className="px-5 py-4 border-b border-slate-100 flex items-center justify-between">
                  <h3 className="text-xs font-bold text-slate-700 uppercase tracking-wide">
                    Operadores e Níveis de Permissão
                  </h3>
                </div>

                {carregandoEquipe ? (
                  <div className="p-8 text-center text-xs text-slate-400">Carregando lista de operadores...</div>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="w-full text-left text-xs text-slate-600 border-collapse">
                      <thead className="bg-[#f9fafb] text-slate-700 font-bold uppercase border-b border-slate-200">
                        <tr>
                          <th className="py-3 px-4">Nome</th>
                          <th className="py-3 px-4">E-mail Institucional</th>
                          <th className="py-3 px-4">Perfil Ativo</th>
                          <th className="py-3 px-4 text-right">Controle RBAC</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-100">
                        {utilizadores.map((u) => (
                          <tr key={u.id} className="hover:bg-slate-50 transition">
                            <td className="py-3 px-4 font-semibold text-slate-900">{u.nome}</td>
                            <td className="py-3 px-4">{u.email}</td>
                            <td className="py-3 px-4">
                              <span
                                className={`inline-flex items-center px-2 py-0.5 rounded text-[11px] font-bold ${
                                  u.perfil === 'COORDENADOR'
                                    ? 'bg-purple-100 text-purple-800'
                                    : 'bg-slate-100 text-slate-700'
                                }`}
                              >
                                {u.perfil}
                              </span>
                            </td>
                            <td className="py-3 px-4 text-right">
                              <button
                                onClick={() => handleAlternarPerfil(u.id, u.perfil)}
                                className="text-[#0088cc] hover:text-[#005580] font-bold underline cursor-pointer"
                              >
                                Alternar para {u.perfil === 'COORDENADOR' ? 'OPERADOR' : 'COORDENADOR'}
                              </button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            </div>
          )}
        </main>
      </div>

      {/* MODAL DE EDIÇÃO */}
      {criancaEditando && (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-xs flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-sm shadow-xl max-w-lg w-full p-6 border border-slate-300">
            <div className="flex justify-between items-center mb-1">
              <h3 className="text-base font-bold text-[#007b99] uppercase tracking-wide">
                Editar Cadastro do Acolhido
              </h3>
              <button onClick={() => setCriancaEditando(null)} className="text-slate-400 hover:text-slate-700 cursor-pointer">
                <X className="w-5 h-5" />
              </button>
            </div>
            <p className="text-xs text-slate-500 mb-4">Atualize as informações cadastrais e dados de saúde.</p>

            {erroEdicao && (
              <div className="mb-4 p-3 bg-red-50 border-l-4 border-red-500 text-red-700 text-xs font-medium">
                {erroEdicao}
              </div>
            )}

            <form onSubmit={handleSalvarEdicao} className="space-y-4 text-xs">
              <div>
                <label className="block text-slate-700 font-bold uppercase mb-1">Nome Completo *</label>
                <input
                  type="text"
                  required
                  minLength={2}
                  value={formEdicao.nome_completo}
                  onChange={(e) => setFormEdicao({ ...formEdicao, nome_completo: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded text-slate-800 focus:outline-none focus:border-[#00a887]"
                />
              </div>

              <div>
                <label className="block text-slate-700 font-bold uppercase mb-1">Data de Nascimento *</label>
                <input
                  type="date"
                  required
                  value={formEdicao.data_nascimento}
                  onChange={(e) => setFormEdicao({ ...formEdicao, data_nascimento: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded text-slate-800 focus:outline-none focus:border-[#00a887]"
                />
              </div>

              <div>
                <label className="block text-slate-700 font-bold uppercase mb-1">
                  Alergias ou Observações Clínicas (Sensível)
                </label>
                <textarea
                  rows={2}
                  value={formEdicao.alergias}
                  onChange={(e) => setFormEdicao({ ...formEdicao, alergias: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded text-slate-800 focus:outline-none focus:border-[#00a887]"
                />
              </div>

              <div className="mt-6 flex justify-end gap-2 pt-3 border-t border-slate-200">
                <button
                  type="button"
                  onClick={() => setCriancaEditando(null)}
                  className="bg-slate-200 hover:bg-slate-300 text-slate-700 px-4 py-2 rounded font-semibold cursor-pointer"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  disabled={salvandoEdicao}
                  className="bg-[#00a887] hover:bg-[#008f73] text-white px-4 py-2 rounded font-bold transition disabled:opacity-50 cursor-pointer uppercase inline-flex items-center gap-1.5"
                >
                  <CheckCircle2 className="w-4 h-4" />
                  {salvandoEdicao ? 'Salvando...' : 'Salvar Alterações'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* MODAL DE PRONTUÁRIO & EVOLUÇÕES */}
      {selecionada && (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-xs flex items-center justify-center p-4 z-50 overflow-y-auto">
          <div className="bg-white rounded-sm shadow-xl max-w-2xl w-full p-6 border border-slate-300 my-8 max-h-[90vh] flex flex-col">
            <div className="flex justify-between items-start mb-4 border-b border-slate-200 pb-3">
              <div>
                <span className="text-[10px] font-bold uppercase text-[#007b99] tracking-wider flex items-center gap-1">
                  <FileText className="w-3.5 h-3.5" /> Prontuário Institucional
                </span>
                <h3 className="text-lg font-bold text-slate-900">{selecionada.nome_completo}</h3>
                <p className="text-[11px] text-slate-400">ID de Registro: {selecionada.id}</p>
              </div>
              <button
                onClick={() => setSelecionada(null)}
                className="text-slate-400 hover:text-slate-700 cursor-pointer"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="overflow-y-auto pr-1 space-y-5 flex-1 text-xs">
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 bg-slate-50 p-3 border border-slate-200 rounded">
                <div>
                  <span className="font-bold text-slate-500 uppercase block text-[10px]">Data de Nascimento</span>
                  <span className="text-slate-800 font-semibold">{selecionada.data_nascimento}</span>
                </div>
                <div>
                  <span className="font-bold text-slate-500 uppercase block text-[10px]">Data de Admissão</span>
                  <span className="text-slate-800 font-semibold">{selecionada.data_admissao}</span>
                </div>
                <div>
                  <span className="font-bold text-slate-500 uppercase block text-[10px]">Estado de Acolhimento</span>
                  {selecionada.status_acolhimento === 'ACOLHIDO' ? (
                    <span className="text-emerald-700 font-bold">● Acolhido Ativo</span>
                  ) : (
                    <span className="text-slate-600 font-bold">● Desacolhido</span>
                  )}
                </div>
              </div>

              {selecionada.status_acolhimento === 'DESACOLHIDO' && (
                <div className="p-3 bg-amber-50 border border-amber-200 rounded text-amber-900 space-y-1">
                  <p className="font-bold text-amber-800">Histórico de Desligamento:</p>
                  <p><strong>Data de Saída:</strong> {selecionada.data_desligamento}</p>
                  <p><strong>Motivo:</strong> {selecionada.motivo_desligamento}</p>
                  <p><strong>Destino / Responsável:</strong> {selecionada.destino_desligamento}</p>
                </div>
              )}

              <div>
                <span className="font-bold uppercase tracking-wide text-red-700 flex items-center gap-1.5 mb-1">
                  <ShieldCheck className="w-4 h-4 text-red-600" />
                  Dados Clínicos e Alergias (Decifrado AES-GCM)
                </span>
                <div className="p-3 bg-red-50/70 border border-red-200 rounded text-red-950 font-medium leading-relaxed">
                  {selecionada.alergias_decifradas || 'Nenhuma restrição clínica ou alergia informada.'}
                </div>
              </div>

              {/* Registro de Nova Evolução */}
              <div className="border-t border-slate-200 pt-4">
                <h4 className="font-bold text-slate-800 uppercase tracking-wide mb-2 flex items-center gap-1.5">
                  <Plus className="w-4 h-4 text-slate-600" />
                  Registrar Nova Evolução / Ocorrência
                </h4>

                {erroEvolucao && (
                  <div className="mb-2 p-2 bg-red-50 border-l-4 border-red-500 text-red-700 text-xs">
                    {erroEvolucao}
                  </div>
                )}

                <form onSubmit={handleSalvarEvolucao} className="space-y-3">
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                    <div>
                      <label className="block font-bold text-slate-600 uppercase text-[10px] mb-1">Tipo de Evolução</label>
                      <select
                        value={formEvolucao.tipo}
                        onChange={(e) => setFormEvolucao({ ...formEvolucao, tipo: e.target.value as any })}
                        className="w-full px-2.5 py-2 border border-slate-300 rounded bg-white text-slate-800 focus:border-[#00a887]"
                      >
                        <option value="COMPORTAMENTAL">Comportamental</option>
                        <option value="PEDAGOGICA">Pedagógica</option>
                        <option value="MEDICA">Médica / Saúde (Sigilosa)</option>
                      </select>
                    </div>

                    <div className="sm:col-span-2">
                      <label className="block font-bold text-slate-600 uppercase text-[10px] mb-1">Relatório da Ocorrência *</label>
                      <textarea
                        required
                        minLength={5}
                        rows={2}
                        value={formEvolucao.texto}
                        onChange={(e) => setFormEvolucao({ ...formEvolucao, texto: e.target.value })}
                        placeholder="Relate os fatos, intervenções ou observações relevantes..."
                        className="w-full px-3 py-2 border border-slate-300 rounded text-slate-800 focus:outline-none focus:border-[#00a887]"
                      />
                    </div>
                  </div>

                  <div className="flex justify-end">
                    <button
                      type="submit"
                      disabled={salvandoEvolucao}
                      className="bg-[#00a887] hover:bg-[#008f73] text-white font-bold px-4 py-2 rounded uppercase tracking-wide cursor-pointer disabled:opacity-50 inline-flex items-center gap-1.5"
                    >
                      <CheckCircle2 className="w-4 h-4" />
                      {salvandoEvolucao ? 'Gravando...' : 'Inserir no Prontuário'}
                    </button>
                  </div>
                </form>
              </div>

              {/* Histórico */}
              <div className="border-t border-slate-200 pt-4">
                <h4 className="font-bold text-slate-800 uppercase tracking-wide mb-3 flex items-center gap-1.5">
                  <History className="w-4 h-4 text-slate-600" />
                  Histórico de Evoluções
                </h4>
                {carregandoEvolucoes ? (
                  <p className="text-slate-400 py-3 text-center">Carregando anotações...</p>
                ) : evolucoes.length === 0 ? (
                  <p className="text-slate-400 py-3 text-center bg-slate-50 border border-slate-200 rounded">
                    Nenhuma evolução registrada até o momento.
                  </p>
                ) : (
                  <div className="space-y-2">
                    {evolucoes.map((ev) => (
                      <div
                        key={ev.id}
                        className={`p-3 rounded border leading-relaxed ${
                          ev.sigilosa
                            ? 'bg-amber-50 border-amber-200 text-amber-950'
                            : 'bg-slate-50 border-slate-200 text-slate-800'
                        }`}
                      >
                        <div className="flex items-center justify-between mb-1 border-b border-black/5 pb-1">
                          <span className="font-bold flex items-center gap-1.5">
                            {ev.tipo === 'MEDICA' && <HeartPulse className="w-3.5 h-3.5 text-red-600" />}
                            {ev.tipo === 'PEDAGOGICA' && <BookOpen className="w-3.5 h-3.5 text-blue-600" />}
                            {ev.tipo === 'COMPORTAMENTAL' && <User className="w-3.5 h-3.5 text-purple-600" />}
                            {ev.tipo}
                          </span>
                          <span className="text-[10px] text-slate-500">
                            Por <strong>{ev.autor_nome}</strong> em {ev.criado_em}
                          </span>
                        </div>
                        <p className="whitespace-pre-line">{ev.texto}</p>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>

            <div className="mt-4 pt-3 border-t border-slate-200 flex justify-end">
              <button
                onClick={() => setSelecionada(null)}
                className="bg-slate-200 hover:bg-slate-300 text-slate-700 px-4 py-2 rounded font-semibold cursor-pointer text-xs"
              >
                Fechar Ficha
              </button>
            </div>
          </div>
        </div>
      )}

      {/* MODAL DE DESLIGAMENTO */}
      {criancaParaDesligar && (
        <div className="fixed inset-0 bg-black/40 backdrop-blur-xs flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-sm shadow-xl max-w-md w-full p-6 border border-slate-300">
            <div className="flex justify-between items-center mb-1">
              <h3 className="text-base font-bold text-amber-800 uppercase tracking-wide">
                Registrar Saída / Desligamento
              </h3>
              <button onClick={() => setCriancaParaDesligar(null)} className="text-slate-400 hover:text-slate-700 cursor-pointer">
                <X className="w-5 h-5" />
              </button>
            </div>
            <p className="text-xs text-slate-500 mb-4">
              Acolhido: <span className="font-bold text-slate-800">{criancaParaDesligar.nome_completo}</span>
            </p>

            {erroDesligamento && (
              <div className="mb-4 p-3 bg-red-50 border-l-4 border-red-500 text-red-700 text-xs font-medium">
                {erroDesligamento}
              </div>
            )}

            <form onSubmit={handleConfirmarDesligamento} className="space-y-4 text-xs">
              <div>
                <label className="block text-slate-700 font-bold uppercase mb-1">Data de Saída *</label>
                <input
                  type="date"
                  required
                  value={formDesligamento.data_desligamento}
                  onChange={(e) => setFormDesligamento({ ...formDesligamento, data_desligamento: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded text-slate-800 focus:outline-none focus:border-[#00a887]"
                />
              </div>

              <div>
                <label className="block text-slate-700 font-bold uppercase mb-1">Motivo do Desligamento *</label>
                <input
                  type="text"
                  required
                  minLength={3}
                  placeholder="Ex: Reintegração à família biológica / Adoção"
                  value={formDesligamento.motivo}
                  onChange={(e) => setFormDesligamento({ ...formDesligamento, motivo: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded text-slate-800 focus:outline-none focus:border-[#00a887]"
                />
              </div>

              <div>
                <label className="block text-slate-700 font-bold uppercase mb-1">Destino ou Responsável Legal *</label>
                <input
                  type="text"
                  required
                  minLength={3}
                  placeholder="Ex: Genitora / Avós maternos"
                  value={formDesligamento.destino}
                  onChange={(e) => setFormDesligamento({ ...formDesligamento, destino: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded text-slate-800 focus:outline-none focus:border-[#00a887]"
                />
              </div>

              <div className="mt-6 flex justify-end gap-2 pt-3 border-t border-slate-200">
                <button
                  type="button"
                  onClick={() => setCriancaParaDesligar(null)}
                  className="bg-slate-200 hover:bg-slate-300 text-slate-700 px-4 py-2 rounded font-semibold cursor-pointer"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  disabled={carregandoDesligamento}
                  className="bg-amber-600 hover:bg-amber-700 text-white px-4 py-2 rounded font-bold transition disabled:opacity-50 cursor-pointer uppercase inline-flex items-center gap-1.5"
                >
                  <LogOut className="w-3.5 h-3.5" />
                  {carregandoDesligamento ? 'Gravando...' : 'Confirmar Saída'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
