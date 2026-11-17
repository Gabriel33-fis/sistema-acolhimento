# Evidências de Testes

Todos os testes usam somente dados fictícios (prefixo `[FICTÍCIO]`), em ambiente local (bancada), não na nuvem.

## 2026-11-17

| Arquivo | Versão | Conteúdo |
| --- | --- | --- |
| `pytest_v1.0.0-RC.txt` / `.xml` | v1.0.0-RC | Testes automatizados: 18 aprovados, 3 reprovados |
| `bancada_v1.0.0-RC.json` | v1.0.0-RC | CT-S01, CT-S02, CT-S03 e CT-D01 (carga de 30 s) antes dos ajustes |
| `pytest_v1.0.1-RC.txt` / `.xml` | v1.0.1-RC | Testes automatizados após os ajustes: 25 aprovados |
| `bancada_v1.0.1-RC.json` | v1.0.1-RC | CT-S01, CT-S02, CT-S03 e CT-D01 (carga de 60 s) após os ajustes |
| `demo_v1.0.1-RC.json` | v1.0.1-RC | Registro fictício criado e consultado na mesma versão |

Como reproduzir:

```bash
cd backend && pytest -v                      # testes automatizados
uvicorn app.main:app --port 8000             # em outro terminal
python scripts/executar_testes_bancada.py --db backend/acolhimento.db
python scripts/demo_registro_ficticio.py
```
