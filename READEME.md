# Sistema de Acolhimento Institucional

O **Sistema de Acolhimento** é uma solução para gestão e acompanhamento de crianças e adolescentes em serviços de acolhimento institucional (abrigos e casas-lares). A aplicação foi concebida com ênfase em conformidade com o **Estatuto da Criança e do Adolescente (ECA)** e a **Lei Geral de Proteção de Dados Pessoais (LGPD)**, assegurando confidencialidade de prontuários de saúde e rastreabilidade total de acessos.

---

## 🏛️ Arquitetura do Sistema

O backend adota os princípios de **Clean Architecture**, isolando as regras de negócio de frameworks e detalhes de persistência:

```text
backend/
├── app/
│   ├── domain/               # Entidades de negócio puras e contratos (Interfaces)
│   │   ├── entities/         # Crianca, Utilizador, AuditLog
│   │   └── repositories/     # ICriancaRepository, IAuditLogger
│   ├── application/          # Casos de uso de aplicação (Use Cases)
│   │   └── use_cases/        # AdmitirCrianca, ListarCriancas, ConsultarDetalhe
│   ├── infrastructure/       # Implementações concretas e adaptadores
│   │   ├── database/         # Modelos SQLAlchemy, sessões e repositórios SQL
│   │   └── security/         # Criptografia AES-256-GCM, Bcrypt e JWT
│   └── presentation/         # Camada de entrega HTTP
│       └── api/              # Routers FastAPI, Schemas Pydantic e Middleware RBAC
```

---

## 🔒 Segurança, Privacidade e LGPD

1. **Criptografia em Repouso (AES-256-GCM):**
   * Dados médicos sensíveis (alergias, diagnósticos e histórico de saúde) são cifrados antes de serem persistidos no banco de dados.
   * Utilização de Vetor de Inicialização (IV) pseudoaleatório de 96 bits (`CSPRNG`) gerado por registro e verificação de integridade via tag de autenticação (`MAC`).

2. **Autenticação Stateless via JWT:**
   * Emissão de tokens de acesso assinados digitalmente com prazo de expiração predefinido.

3. **Proteção de Credenciais:**
   * Senhas processadas com algoritmo `bcrypt` nativo e fator de custo com salting automático.

4. **Trilha de Auditoria Imutável:**
   * Cada operação cadastral e consulta a prontuário confidencial registra de forma persistente: identificador do operador, IP de origem, recurso acessado, ação e carimbo de data/hora UTC.

5. **Controle de Acesso Baseado em Perfis (RBAC):**

| Funcionalidade | Coordenador | Operador / Educador |
| :--- | :---: | :---: |
| Autenticação no Sistema | Sim | Sim |
| Listagem e Busca de Acolhidos | Sim | Sim |
| Cadastro / Admissão de Acolhido | Sim | Sim |
| Consulta a Prontuário Médico (Decifrado) | Sim | **403 Forbidden** |
| Cadastro de Novos Utilizadores do Sistema | Sim | **403 Forbidden** |

---

## 🛠️ Tecnologias Utilizadas

Backend: Python 3.12, FastAPI, SQLAlchemy ORM, Pydantic v2, PyJWT, Cryptography (AES-GCM), Bcrypt, SQLite.

Frontend: React 18, TypeScript, Vite, Tailwind CSS, Lucide React (Outline Icons).

Testes: Pytest, HTTPX (20 testes automatizados cobrindo domínio, criptografia e rotas).

Containerização: Docker, Docker Compose, Nginx Alpi

---

## 🚀 Como Executar o Projeto

### Pré-requisitos
- Python 3.12 ou superior
- Node.js 18 ou superior e npm
- Git

---

### 1. Inicializar o Backend

Abra um terminal na raiz do projeto:

```bash
cd backend

# Criar e ativar o ambiente virtual
python -m venv .venv
source .venv/bin/activate  # No Windows: .venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt

# Executar a sementeira inicial de usuários de teste
python -m app.infrastructure.database.seed_users

# Executar o servidor FastAPI
uvicorn app.main:app --reload --port 8000
```

* API ativa em: `http://127.0.0.1:8000`
* Documentação Swagger OpenAPI: `http://127.0.0.1:8000/docs`

---

### 2. Inicializar o Frontend

Abra outro terminal na raiz do projeto:

```bash
cd frontend

# Instalar pacotes
npm install

# Iniciar servidor de desenvolvimento
npm run dev
```

* Interface Web ativa em: `http://localhost:5173`

---

## 🔑 Credenciais Padrão para Demonstração

| Perfil | E-mail | Senha | Permissões |
| :--- | :--- | :--- | :--- |
| **Coordenador** | `admin@instituicao.org` | `admin123` | Visualiza prontuários decifrados e cadastra novos operadores. |
| **Operador** | `educador@instituicao.org` | `user123` | Cadastra acolhidos; acesso bloqueado ao prontuário médico sensível (403). |

---

## 📄 Licença

Este projeto é desenvolvido no âmbito acadêmico para o **Projeto Integrador IV**.