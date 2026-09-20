# Sistema de Acolhimento

O **Sistema de Acolhimento** é uma solução para gestão e acompanhamento de crianças e adolescentes em serviços de acolhimento institucional (abrigos e casas-lares). A aplicação foi concebida com ênfase em conformidade com o **Estatuto da Criança e do Adolescente (ECA)** e a **Lei Geral de Proteção de Dados Pessoais (LGPD)**, assegurando confidencialidade de prontuários de saúde e rastreabilidade total de acessos.

---

## 🔗 Demonstração Online (Deploy em Nuvem)

- **Frontend (Web):** [https://sistema-acolhimento-web.onrender.com](https://sistema-acolhimento-web.onrender.com)
- **Backend (API Docs / Swagger):** [https://sistema-acolhimento-api.onrender.com/docs](https://sistema-acolhimento-api.onrender.com/docs)
- **Status / Health Check:** [https://sistema-acolhimento-api.onrender.com/health](https://sistema-acolhimento-api.onrender.com/health)

> **Nota sobre o plano gratuito do Render:** Caso o serviço esteja ocioso por mais de 15 minutos, a primeira requisição pode demorar de 30 a 50 segundos para inicializar o contêiner (*cold start*).

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

- **Criptografia em Repouso (AES-256-GCM):**
  - Dados médicos sensíveis (alergias, diagnósticos e histórico de saúde) são cifrados antes de serem persistidos no banco de dados.
  - Utilização de Vetor de Inicialização (IV) pseudoaleatório de 96 bits (CSPRNG) gerado por registro e verificação de integridade via tag de autenticação (MAC).
- **Autenticação Stateless via JWT:** emissão de tokens de acesso assinados digitalmente com prazo de expiração predefinido.
- **Proteção de Credenciais:** senhas processadas com algoritmo bcrypt nativo e fator de custo com salting automático.
- **Trilha de Auditoria Imutável:** cada operação cadastral e consulta a prontuário confidencial registra: identificador do operador, IP de origem, recurso acessado, ação e carimbo de data/hora UTC.
- **Controle de Acesso Baseado em Perfis (RBAC):**

| Funcionalidade                            | Coordenador | Operador / Educador |
| ----------------------------------------- | :---------: | :-----------------: |
| Autenticação no Sistema                   |     Sim     |         Sim         |
| Listagem e Busca de Acolhidos             |     Sim     |         Sim         |
| Cadastro / Admissão de Acolhido           |     Sim     |         Sim         |
| Consulta a Prontuário Médico (Decifrado)  |     Sim     |    403 Forbidden    |
| Cadastro de Novos Utilizadores do Sistema |     Sim     |    403 Forbidden    |

---

## 🛠️ Tecnologias Utilizadas

- **Backend:** Python 3.12, FastAPI, SQLAlchemy ORM, Pydantic v2, PyJWT, Cryptography, Bcrypt, SQLite.
- **Frontend:** React 18, TypeScript, Tailwind CSS, Vite.
- **DevOps & Infra:** Docker, Docker Compose, Nginx, Render Cloud.
- **Auditoria:** Registro de eventos relacional em conformidade com boas práticas de segurança.

---

## 🔑 Credenciais Padrão para Demonstração

| Perfil      | E-mail                  | Senha      | Permissões                                                          |
| ----------- | ----------------------- | ---------- | ------------------------------------------------------------------- |
| Coordenador | `admin@instituicao.org`    | `admin123` | Visualiza prontuários decifrados e cadastra novos operadores.       |
| Operador    | `educador@instituicao.org` | `user123`  | Cadastra acolhidos; acesso bloqueado ao prontuário médico sensível (403). |

---

## 🚀 Como Executar o Projeto Localmente

### Opção 1: Via Docker Compose (Recomendado)

Com o Docker instalado, execute na raiz do repositório:

```bash
docker compose up --build -d
```

- **Frontend:** http://localhost
- **API / Swagger:** http://localhost:8000/docs

(Tabelas e usuários padrão são gerados automaticamente na inicialização via evento `lifespan` do FastAPI.)

### Opção 2: Execução Manual para Desenvolvimento

**1. Backend**

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # No Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**2. Frontend**

```bash
cd frontend
npm install
npm run dev
```

---

## 📄 Licença

Este projeto é desenvolvido no âmbito acadêmico para o Projeto Integrador IV.
