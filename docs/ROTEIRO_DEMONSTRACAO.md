# Roteiro da Demonstração — Registro Fictício na Versão Identificada

Objetivo: mostrar, **na mesma versão citada no relatório**, um registro fictício sendo **criado** e em seguida **consultado**.

> Todos os dados usados são fictícios e marcados com o prefixo `[FICTÍCIO]`. Nenhum dado real de criança ou adolescente é utilizado.

## 1. Antes de começar (5 minutos antes)

1. Abrir `https://sistema-acolhimento-api.onrender.com/health` para "acordar" o serviço (*cold start* do plano gratuito pode levar até 50 s).
2. Conferir na resposta os campos `versao` e `commit`. A `versao` deve ser **a mesma** que aparece no relatório.
3. Abrir o frontend e conferir que o selo da tela de login mostra a mesma versão e o mesmo commit.

## 2. Demonstração pela interface (recomendada para a banca)

| Passo | Ação | O que mostrar |
| ----- | ---- | ------------- |
| 1 | Tela de login | Selo `v<versão> (<commit>)` no canto superior direito |
| 2 | Entrar como Coordenador (`admin@instituicao.org` / `admin123`) | Rodapé lateral com a versão e o aviso "Dados fictícios" |
| 3 | Admitir acolhido com nome `[FICTÍCIO] Criança Demonstração` e alergia `[FICTÍCIO] Alergia a amendoim` | Mensagem de sucesso |
| 4 | Buscar por `FICTÍCIO` na listagem | O registro recém-criado aparece |
| 5 | Abrir o detalhe do registro | Alergia exibida decifrada, igual ao que foi digitado |
| 6 | Recarregar `/health` | Mesma `versao` e mesmo `commit` do passo 1 |

## 3. Demonstração pelo script (alternativa ou evidência complementar)

```bash
python scripts/demo_registro_ficticio.py https://sistema-acolhimento-api.onrender.com
```

O script executa os mesmos passos (versão → login → criação → listagem → detalhe → versão), confere se os dados consultados são iguais aos enviados e se a versão não mudou durante o processo, e grava um arquivo JSON em `docs/evidencias/` com versão, commit, ID criado e horários UTC. Esse arquivo pode ser anexado ao relatório.

## 4. O que **não** afirmar na demonstração

- O **piloto de campo** em instituição de acolhimento está **planejado** e ainda **não foi executado**. Até existirem registros da execução (data, local, participantes, resultados), ele deve ser citado apenas como etapa futura.
- As validações realizadas até agora são **simulações com dados fictícios** e testes automatizados.
