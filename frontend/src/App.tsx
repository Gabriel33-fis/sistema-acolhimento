import React, { useState, useEffect } from 'react';
import { 
  admitirCrianca, 
  listarCriancas, 
  obterCriancaPorId, 
  autenticar, 
  obterToken, 
  limparSessao, 
  obterUsuarioSalvo,
  cadastrarUsuario
} from './services/api';
import type { CriancaEntrada, CriancaResumo, CriancaDetalhada } from './types/crianca';

interface NovoUsuarioForm {
  nome: string;
  email: string;
  senha: string;
  perfil: 'COORDENADOR' | 'OPERADOR';
}

export default function App() {
  const [token, setToken] = useState<string | null>(obterToken());
  const [usuario, setUsuario] = useState(obterUsuarioSalvo());

  // Estados de Login
  const [loginEmail, setLoginEmail] = useState('admin@instituicao.org');
  const [loginSenha, setLoginSenha] = useState('admin123');
  const [loginErro, setLoginErro] = useState<string | null>(null);
  const [loginCarregando, setLoginCarregando] = useState(false);

  // Navegação
  const [abaAtiva, setAbaAtiva] = useState<'lista' | 'admissao' | 'usuarios'>('lista');
  const [criancas, setCriancas] = useState<CriancaResumo[]>([]);
  const [busca, setBusca] = useState('');
  
  // Formulário de Criança
  const [formData, setFormData] = useState<CriancaEntrada>({
    nome_completo: '',
    data_nascimento: '',
    alergias: '',
  });

  // Formulário de Utilizador
  const [formUser, setFormUser] = useState<NovoUsuarioForm>({
    nome: '',
    email: '',
    senha: '',
    perfil: 'OPERADOR',
  });

  const [feedback, setFeedback] = useState<{ tipo: 'sucesso' | 'erro'; texto: string } | null>(null);
  const [feedbackUser, setFeedbackUser] = useState<{ tipo: 'sucesso' | 'erro'; texto: string } | null>(null);
  const [carregando, setCarregando] = useState(false);
  const [carregandoUser, setCarregandoUser] = useState(false);
  
  const [selecionada, setSelecionada] = useState<CriancaDetalhada | null>(null);
  const [carregandoDetalhe, setCarregandoDetalhe] = useState(false);

  const carregarLista = async (termoFiltro = '') => {
    if (!token) return;
    try {
      const dados = await listarCriancas(termoFiltro);
      setCriancas(dados);
    } catch (err: any) {
      if (err.message === 'SessaoExpirada') {
        handleLogout();
      }
    }
  };

  useEffect(() => {
    if (token && abaAtiva === 'lista') {
      carregarLista(busca);
    }
  }, [busca, abaAtiva, token]);

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
    setAbaAtiva('lista');
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setCarregando(true);
    setFeedback(null);

    try {
      const payload: CriancaEntrada = {
        nome_completo: formData.nome_completo,
        data_nascimento: formData.data_nascimento,
        alergias: formData.alergias?.trim() ? formData.alergias : undefined,
      };

      const resultado = await admitirCrianca(payload);
      setFeedback({
        tipo: 'sucesso',
        texto: `${resultado.mensagem}! ID: ${resultado.id}`,
      });
      setFormData({ nome_completo: '', data_nascimento: '', alergias: '' });
      carregarLista();
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

  const handleCadastrarUser = async (e: React.FormEvent) => {
    e.preventDefault();
    setCarregandoUser(true);
    setFeedbackUser(null);

    try {
      const res = await cadastrarUsuario(formUser);
      setFeedbackUser({ tipo: 'sucesso', texto: res.mensagem });
      setFormUser({ nome: '', email: '', senha: '', perfil: 'OPERADOR' });
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

  const handleVerFicha = async (id: string) => {
    setCarregandoDetalhe(true);
    try {
      const detalhe = await obterCriancaPorId(id);
      setSelecionada(detalhe);
    } catch (err: any) {
      if (err.message === 'SessaoExpirada') {
        handleLogout();
        return;
      }
      alert('Não foi possível carregar a ficha do acolhido.');
    } finally {
      setCarregandoDetalhe(false);
    }
  };

  if (!token) {
    return (
      <div className="min-h-screen bg-slate-100 flex items-center justify-center p-4">
        <div className="max-w-md w-full bg-white rounded-xl shadow-md border border-slate-200 p-8">
          <div className="text-center mb-6">
            <span className="text-xs font-bold uppercase tracking-wider text-blue-600 bg-blue-50 px-2.5 py-1 rounded">
              Acesso Seguro
            </span>
            <h2 className="text-2xl font-bold text-slate-800 mt-2">Sistema de Acolhimento</h2>
            <p className="text-xs text-slate-500 mt-1">Insira as credenciais de operador para prosseguir</p>
          </div>

          {loginErro && (
            <div className="mb-4 p-3 bg-rose-50 border border-rose-200 text-rose-700 text-sm rounded-md">
              {loginErro}
            </div>
          )}

          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">E-mail</label>
              <input
                type="email"
                required
                value={loginEmail}
                onChange={(e) => setLoginEmail(e.target.value)}
                className="w-full px-3 py-2 border border-slate-300 rounded-md text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 uppercase mb-1">Senha</label>
              <input
                type="password"
                required
                value={loginSenha}
                onChange={(e) => setLoginSenha(e.target.value)}
                className="w-full px-3 py-2 border border-slate-300 rounded-md text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <button
              type="submit"
              disabled={loginCarregando}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-2.5 rounded-md transition text-sm disabled:opacity-50 cursor-pointer"
            >
              {loginCarregando ? 'A entrar...' : 'Entrar no Sistema'}
            </button>
          </form>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 p-6 md:p-10 flex flex-col items-center">
      <div className="w-full max-w-4xl">
        <header className="mb-6 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div>
            <span className="text-xs font-semibold uppercase tracking-wider text-blue-600 bg-blue-50 px-2.5 py-1 rounded">
              Sistema de Acolhimento
            </span>
            <h1 className="text-2xl font-bold text-slate-900 mt-1">Gestão Institucional</h1>
            <p className="text-xs text-slate-500 mt-0.5">
              Operador: <span className="font-semibold text-slate-700">{usuario?.nome}</span> ({usuario?.perfil})
            </p>
          </div>

          <div className="flex items-center gap-3">
            <div className="flex bg-slate-200 p-1 rounded-lg">
              <button
                onClick={() => setAbaAtiva('lista')}
                className={`px-4 py-1.5 text-sm font-medium rounded-md transition cursor-pointer ${
                  abaAtiva === 'lista' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                Residentes
              </button>
              <button
                onClick={() => setAbaAtiva('admissao')}
                className={`px-4 py-1.5 text-sm font-medium rounded-md transition cursor-pointer ${
                  abaAtiva === 'admissao' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                Nova Admissão
              </button>
              {usuario?.perfil === 'COORDENADOR' && (
                <button
                  onClick={() => setAbaAtiva('usuarios')}
                  className={`px-4 py-1.5 text-sm font-medium rounded-md transition cursor-pointer ${
                    abaAtiva === 'usuarios' ? 'bg-white text-slate-900 shadow-sm' : 'text-slate-600 hover:text-slate-900'
                  }`}
                >
                  Registar Operador
                </button>
              )}
            </div>

            <button
              onClick={handleLogout}
              className="text-xs bg-rose-50 text-rose-700 border border-rose-200 hover:bg-rose-100 font-medium px-3 py-2 rounded-md transition cursor-pointer"
            >
              Sair
            </button>
          </div>
        </header>

        {abaAtiva === 'lista' && (
          <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
            <div className="mb-6">
              <input
                type="text"
                placeholder="Pesquisar por nome do acolhido..."
                value={busca}
                onChange={(e) => setBusca(e.target.value)}
                className="w-full px-4 py-2 border border-slate-300 rounded-lg text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            {criancas.length === 0 ? (
              <p className="text-sm text-slate-500 text-center py-8">Nenhum acolhido registado ou encontrado na pesquisa.</p>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-sm text-slate-600 border-collapse">
                  <thead className="bg-slate-50 text-xs uppercase font-semibold text-slate-500 border-b border-slate-200">
                    <tr>
                      <th className="py-3 px-4">Nome Completo</th>
                      <th className="py-3 px-4">Nascimento</th>
                      <th className="py-3 px-4">Admissão</th>
                      <th className="py-3 px-4">Estado</th>
                      <th className="py-3 px-4 text-right">Ação</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-200">
                    {criancas.map((item) => (
                      <tr key={item.id} className="hover:bg-slate-50 transition">
                        <td className="py-3 px-4 font-medium text-slate-900">{item.nome_completo}</td>
                        <td className="py-3 px-4">{item.data_nascimento}</td>
                        <td className="py-3 px-4">{item.data_admissao}</td>
                        <td className="py-3 px-4">
                          <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-emerald-100 text-emerald-800">
                            {item.status_acolhimento}
                          </span>
                        </td>
                        <td className="py-3 px-4 text-right">
                          <button
                            onClick={() => handleVerFicha(item.id)}
                            disabled={carregandoDetalhe}
                            className="text-xs bg-slate-100 hover:bg-slate-200 text-slate-700 font-medium px-3 py-1.5 rounded transition cursor-pointer"
                          >
                            Ver Prontuário
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {abaAtiva === 'admissao' && (
          <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-8 max-w-xl mx-auto">
            <h2 className="text-xl font-bold text-slate-800 mb-2">Admissão de Acolhido</h2>
            <p className="text-sm text-slate-500 mb-6">
              Preencha os dados de entrada. Campos médicos são cifrados na base de dados.
            </p>

            {feedback && (
              <div
                className={`p-4 rounded-lg mb-6 text-sm ${
                  feedback.tipo === 'sucesso'
                    ? 'bg-emerald-50 text-emerald-800 border border-emerald-200'
                    : 'bg-rose-50 text-rose-800 border border-rose-200'
                }`}
              >
                {feedback.texto}
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Nome Completo *</label>
                <input
                  type="text"
                  required
                  minLength={2}
                  value={formData.nome_completo}
                  onChange={(e) => setFormData({ ...formData, nome_completo: e.target.value })}
                  placeholder="Ex: Carlos Eduardo de Souza"
                  className="w-full px-3 py-2 border border-slate-300 rounded-md text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Data de Nascimento *</label>
                <input
                  type="date"
                  required
                  value={formData.data_nascimento}
                  onChange={(e) => setFormData({ ...formData, data_nascimento: e.target.value })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-md text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">
                  Alergias ou Observações de Saúde (Sensível)
                </label>
                <input
                  type="text"
                  value={formData.alergias}
                  onChange={(e) => setFormData({ ...formData, alergias: e.target.value })}
                  placeholder="Ex: Alergia a Amendoim"
                  className="w-full px-3 py-2 border border-slate-300 rounded-md text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <button
                type="submit"
                disabled={carregando}
                className="w-full mt-4 bg-blue-600 hover:bg-blue-700 text-white font-medium py-2.5 px-4 rounded-md transition disabled:opacity-50 cursor-pointer"
              >
                {carregando ? 'A registar...' : 'Concluir Admissão'}
              </button>
            </form>
          </div>
        )}

        {abaAtiva === 'usuarios' && usuario?.perfil === 'COORDENADOR' && (
          <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-8 max-w-xl mx-auto">
            <h2 className="text-xl font-bold text-slate-800 mb-2">Registo de Utilizador</h2>
            <p className="text-sm text-slate-500 mb-6">
              Cadastre novos colaboradores definindo o nível de acesso apropriado.
            </p>

            {feedbackUser && (
              <div
                className={`p-4 rounded-lg mb-6 text-sm ${
                  feedbackUser.tipo === 'sucesso'
                    ? 'bg-emerald-50 text-emerald-800 border border-emerald-200'
                    : 'bg-rose-50 text-rose-800 border border-rose-200'
                }`}
              >
                {feedbackUser.texto}
              </div>
            )}

            <form onSubmit={handleCadastrarUser} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Nome Completo *</label>
                <input
                  type="text"
                  required
                  value={formUser.nome}
                  onChange={(e) => setFormUser({ ...formUser, nome: e.target.value })}
                  placeholder="Ex: Maria Auxiliadora"
                  className="w-full px-3 py-2 border border-slate-300 rounded-md text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">E-mail Institucional *</label>
                <input
                  type="email"
                  required
                  value={formUser.email}
                  onChange={(e) => setFormUser({ ...formUser, email: e.target.value })}
                  placeholder="operador@instituicao.org"
                  className="w-full px-3 py-2 border border-slate-300 rounded-md text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Palavra-passe Inicial *</label>
                <input
                  type="password"
                  required
                  minLength={6}
                  value={formUser.senha}
                  onChange={(e) => setFormUser({ ...formUser, senha: e.target.value })}
                  placeholder="Mínimo 6 caracteres"
                  className="w-full px-3 py-2 border border-slate-300 rounded-md text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Perfil de Acesso *</label>
                <select
                  value={formUser.perfil}
                  onChange={(e) => setFormUser({ ...formUser, perfil: e.target.value as 'COORDENADOR' | 'OPERADOR' })}
                  className="w-full px-3 py-2 border border-slate-300 rounded-md text-slate-900 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="OPERADOR">OPERADOR (Acesso padrão - sem prontuários médicos)</option>
                  <option value="COORDENADOR">COORDENADOR (Acesso total + gestão de utilizadores)</option>
                </select>
              </div>

              <button
                type="submit"
                disabled={carregandoUser}
                className="w-full mt-4 bg-blue-600 hover:bg-blue-700 text-white font-medium py-2.5 px-4 rounded-md transition disabled:opacity-50 cursor-pointer"
              >
                {carregandoUser ? 'A criar utilizador...' : 'Registar Utilizador'}
              </button>
            </form>
          </div>
        )}

        {/* Modal de Prontuário */}
        {selecionada && (
          <div className="fixed inset-0 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-xl shadow-xl max-w-lg w-full p-6 border border-slate-200">
              <div className="flex justify-between items-start mb-4 border-b border-slate-100 pb-3">
                <div>
                  <h3 className="text-lg font-bold text-slate-900">{selecionada.nome_completo}</h3>
                  <p className="text-xs text-slate-400">ID: {selecionada.id}</p>
                </div>
                <button
                  onClick={() => setSelecionada(null)}
                  className="text-slate-400 hover:text-slate-600 text-xl font-bold px-2 cursor-pointer"
                >
                  &times;
                </button>
              </div>

              <div className="space-y-3 text-sm">
                <div>
                  <span className="font-semibold text-slate-700">Data de Nascimento:</span>{' '}
                  <span className="text-slate-600">{selecionada.data_nascimento}</span>
                </div>
                <div>
                  <span className="font-semibold text-slate-700">Data de Admissão:</span>{' '}
                  <span className="text-slate-600">{selecionada.data_admissao}</span>
                </div>
                <div>
                  <span className="font-semibold text-slate-700">Estado:</span>{' '}
                  <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-emerald-100 text-emerald-800">
                    {selecionada.status_acolhimento}
                  </span>
                </div>

                <div className="mt-4 pt-4 border-t border-slate-100">
                  <span className="font-semibold text-rose-700 flex items-center gap-1">
                    🛡️ Observações Médicas / Alergias (Decifrado):
                  </span>
                  <div className="mt-1 p-3 bg-rose-50 border border-rose-200 rounded text-rose-900 text-xs leading-relaxed">
                    {selecionada.alergias_decifradas || 'Nenhuma alergia ou restrição médica informada.'}
                  </div>
                </div>
              </div>

              <div className="mt-6 flex justify-end">
                <button
                  onClick={() => setSelecionada(null)}
                  className="bg-slate-100 hover:bg-slate-200 text-slate-800 px-4 py-2 rounded text-sm font-medium transition cursor-pointer"
                >
                  Fechar
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
