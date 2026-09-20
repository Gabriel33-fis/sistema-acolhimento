Sistema de Acolhimento Institucional
O Sistema de Acolhimento é uma solução completa para gestão de crianças e adolescentes em instituições de acolhimento (abrigos institucionais e casas-lares). Foi projetado sob rigorosos padrões de segurança da informação, conformidade com o ECA (Estatuto da Criança e do Adolescente) e conformidade com a LGPD (Lei Geral de Proteção de Dados Pessoais) no tratamento de dados altamente sensíveis.
🏛️ Arquitetura e Engenharia de Software
O backend foi construído adotando os princípios de Clean Architecture (Arquitetura Limpa), desacoplando totalmente as regras de negócio de frameworks e ferramentas de infraestrutura:
backend/
├── app/
│   ├── domain/               # Entidades de negócio puras e contratos (Interfaces)
│   │   ├── entities/         # Crianca, Utilizador, AuditLog
│   │   └── repositories/     # Interfaces ICriancaRepository, IAuditLogger
│   ├── application/          # Casos de uso (Application Use Cases)
│   │   └── use_cases/        # AdmitirCrianca, ListarCriancas, ConsultarDetalhe, Autenticar
│   ├── infrastructure/       # Implementações concretas de tecnologia
│   │   ├── database/         # Modelos SQLAlchemy, sessões SQLite e migrations
│   │   └── security/         # Criptografia AES-GCM, Bcrypt e provedores JWT
│   └── presentation/         # Camada de entrega HTTP
│       └── api/              # Routers FastAPI, Schemas Pydantic e Middleware RBAC


🔒 Camada de Segurança e Privacidade
Criptografia Simétrica de Prontuários (AES-256-GCM):
Dados de saúde, diagnósticos e alergias são cifrados antes da persistência no banco.
Cada registro utiliza um Initialization Vector (IV) pseudo-aleatório de 96 bits (CSPRNG) e gera uma tag de autenticação (MAC) para impedir adulteração de registros em repouso.
Autenticação Stateless via JWT:
Tokens com tempo de expiração determinado, assinados digitalmente com segredo institucional.
Hashing de Senhas (Bcrypt):
Hash com salting automático de 12 rounds para proteção contra ataques de dicionário e rainbow tables.
Trilhas de Auditoria Imutáveis:
Cada consulta a prontuários e cada mutação cadastral gera um registro de auditoria persistido contendo: timestamp UTC, identificador do operador, endereço IP e ação executada.
Controle de Acesso Baseado em Papéis (RBAC):
Funcionalidade
COORDENADOR
OPERADOR / EDUCADOR
Autenticação no Sistema
✅
✅
Listagem e Busca de Acolhidos
✅
✅
Cadastro / Admissão de Acolhido
✅
✅
Acesso a Prontuário Médico (Decifrado)
✅
⛔ 403 Forbidden
Cadastro de Novos Utilizadores e Operadores
✅
⛔ 403 Forbidden

💻 Stack Tecnológica
Backend: Python 3.12, FastAPI, SQLAlchemy ORM, Pydantic v2, PyJWT, Cryptography, Bcrypt, SQLite3.
Frontend: React 18, TypeScript, Tailwind CSS, Vite, Fetch API.
Auditoria e Logs: Logs estruturados e trilha de auditoria em banco de dados relacional.
🚀 Instalação e Execução
Pré-requisitos
Python 3.12+ instalado
Node.js 18+ e npm instalados
Git
1. Clonar o Repositório
git clone https://github.com/Gabriel33-fis/sistema-acolhimento.git
cd sistema-acolhimento


2. Configurar e Iniciar o Backend
Abra um terminal na raiz do projeto:
cd backend

# Criar e ativar o ambiente virtual
python -m venv .venv
source .venv/bin/activate  # No Windows: .venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt

# Executar a sementeira inicial de utilizadores de teste
python -m app.infrastructure.database.seed_users

# Iniciar o servidor HTTP
uvicorn app.main:app --reload --port 8000


O backend estará ativo em http://127.0.0.1:8000.
A documentação Swagger interativa estará acessível em http://127.0.0.1:8000/docs.
3. Configurar e Iniciar o Frontend
Abra um segundo terminal na raiz do projeto:
cd frontend

# Instalar dependências
npm install

# Iniciar o servidor de desenvolvimento Vite
npm run dev


Acesse o sistema no navegador através de: http://localhost:5173.
👥 Credenciais Pré-configuradas para Testes
O banco de dados é inicializado com duas contas para validação dos fluxos de segurança:
Usuário
E-mail
Senha
Perfil
Comportamento Esperado
Administrador
admin@instituicao.org
admin123
COORDENADOR
Acesso pleno, visualização de prontuários médicos decifrados e aba para registrar novos operadores.
Educador
educador@instituicao.org
user123
OPERADOR
Permissão apenas para listar e cadastrar acolhidos. Clique em "Ver Prontuário" resulta em HTTP 403.

🧪 Estrutura de Endpoints Principais (API v1)
Método
Rota
Descrição
Nível Mínimo
POST
/api/v1/auth/login
Autenticação com e-mail/senha e geração de JWT
Público
POST
/api/v1/auth/registar
Registro de novos operadores do sistema
COORDENADOR
GET
/api/v1/criancas/
Lista acolhidos (com suporte a busca por query param)
OPERADOR
POST
/api/v1/criancas/
Registra nova admissão e cifra dados sensíveis
OPERADOR
GET
/api/v1/criancas/{id}
Recupera prontuário e decifra dados médicos em memória
COORDENADOR

📄 Licença
Este projeto é distribuído sob a licença MIT. Consulte o arquivo LICENSE para mais detalhes.
