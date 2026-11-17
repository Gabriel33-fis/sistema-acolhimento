#!/usr/bin/env python3
"""Executa os testes de bancada do Plano de Testes e grava evidências datadas.

Casos cobertos (adaptados ao que existe na versão avaliada):
  CT-S01  Barreira RBAC: Operador e requisições sem token
  CT-S02  Cifragem em repouso: leitura direta do banco SQLite
  CT-S03  Trilha de auditoria: registros gerados pelas ações do teste
  CT-D01  Carga concorrente: 10 conexões por 60 s em endpoints de leitura

Uso:
    python scripts/executar_testes_bancada.py --api http://localhost:8000 --db backend/data/acolhimento.db

Somente dados fictícios são usados (prefixo [FICTÍCIO]).
"""
import argparse
import json
import sqlite3
import statistics
import threading
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

COORD = ("admin@instituicao.org", "admin123")
OPER = ("educador@instituicao.org", "user123")


def chamar(base, metodo, caminho, corpo=None, token=None):
    dados = json.dumps(corpo).encode() if corpo is not None else None
    req = urllib.request.Request(base + caminho, data=dados, method=metodo)
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    inicio = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            corpo_resp = resp.read()
            status = resp.status
    except urllib.error.HTTPError as err:
        corpo_resp = err.read()
        status = err.code
    except Exception:
        return 0, None, (time.perf_counter() - inicio) * 1000
    ms = (time.perf_counter() - inicio) * 1000
    try:
        return status, json.loads(corpo_resp or b"null"), ms
    except ValueError:
        return status, None, ms


def login(base, cred):
    st, r, _ = chamar(base, "POST", "/api/v1/auth/login", {"email": cred[0], "senha": cred[1]})
    assert st == 200, f"login falhou: {st}"
    return r["access_token"]


def agora():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def percentil(valores, p):
    v = sorted(valores)
    k = max(0, min(len(v) - 1, round(p / 100 * len(v) + 0.5) - 1))
    return v[k]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--api", default="http://localhost:8000")
    ap.add_argument("--db", default=None, help="caminho do arquivo SQLite (para CT-S02 e CT-S03)")
    ap.add_argument("--registros", type=int, default=50)
    ap.add_argument("--conexoes", type=int, default=10)
    ap.add_argument("--segundos", type=int, default=60)
    ap.add_argument("--saida", default=None)
    a = ap.parse_args()
    base = a.api.rstrip("/")

    _, versao, _ = chamar(base, "GET", "/health")
    ev = {"executado_em_utc": agora(), "api": base, "versao": versao, "casos": {}}
    t_coord, t_oper = login(base, COORD), login(base, OPER)

    # Massa de dados fictícia
    ids = []
    for i in range(a.registros):
        st, r, _ = chamar(base, "POST", "/api/v1/criancas/", {
            "nome_completo": f"[FICTÍCIO] Acolhido Teste {i:02d}",
            "data_nascimento": "2014-05-20",
            "alergias": f"[FICTÍCIO] Alergia de teste {i:02d}",
        }, t_coord)
        if st == 201:
            ids.append(r["id"])
    ev["massa_ficticia_criada"] = len(ids)
    alvo = ids[0]

    # CT-S01 RBAC
    checagens = [
        ("Operador: detalhe com dados de saúde", "GET", f"/api/v1/criancas/{alvo}", None, t_oper, 403),
        ("Operador: edição cadastral", "PUT", f"/api/v1/criancas/{alvo}",
         {"nome_completo": "[FICTÍCIO] X", "data_nascimento": "2014-05-20"}, t_oper, 403),
        ("Operador: desligamento", "POST", f"/api/v1/criancas/{alvo}/desligamento",
         {"data_desligamento": datetime.now().date().isoformat(), "motivo": "Teste", "destino": "Teste"}, t_oper, 403),
        ("Operador: cadastro de usuário", "POST", "/api/v1/auth/registar",
         {"nome": "X", "email": "x@teste.org", "senha": "x12345", "perfil": "COORDENADOR"}, t_oper, 403),
        ("Operador: listar equipe", "GET", "/api/v1/auth/utilizadores", None, t_oper, 403),
        ("Sem token: listagem", "GET", "/api/v1/criancas/", None, None, 401),
        ("Sem token: detalhe", "GET", f"/api/v1/criancas/{alvo}", None, None, 401),
        ("Coordenador: detalhe (controle positivo)", "GET", f"/api/v1/criancas/{alvo}", None, t_coord, 200),
    ]
    res = []
    for nome, m, c, corpo, tok, esperado in checagens:
        st, r, _ = chamar(base, m, c, corpo, tok)
        res.append({"verificacao": nome, "esperado": esperado, "obtido": st,
                    "passou": st == esperado, "detalhe": (r or {}).get("detail") if isinstance(r, dict) else None})
    # Evolução médica deve vir oculta para o Operador
    chamar(base, "POST", f"/api/v1/criancas/{alvo}/evolucoes",
           {"tipo": "MEDICA", "texto": "[FICTÍCIO] Consulta de rotina"}, t_coord)
    _, evs, _ = chamar(base, "GET", f"/api/v1/criancas/{alvo}/evolucoes", token=t_oper)
    oculto = bool(evs) and all("[FICTÍCIO]" not in e["texto"] for e in evs if e["tipo"] == "MEDICA")
    res.append({"verificacao": "Operador: texto de evolução médica oculto", "esperado": "oculto",
                "obtido": "oculto" if oculto else "visível", "passou": oculto})
    ev["casos"]["CT-S01"] = {"verificacoes": res, "passou": all(x["passou"] for x in res)}

    # CT-S02 e CT-S03 (leitura direta do banco)
    if a.db and Path(a.db).exists():
        con = sqlite3.connect(a.db)
        linhas = con.execute("SELECT id, alergias_cifradas FROM criancas WHERE id = ?", (alvo,)).fetchall()
        valor = linhas[0][1] if linhas else ""
        med = con.execute("SELECT texto_cifrado FROM evolucoes WHERE crianca_id = ? AND tipo='MEDICA'", (alvo,)).fetchall()
        texto_claro = "FICTÍCIO" in (valor or "") or any("FICTÍCIO" in (m[0] or "") for m in med)
        ev["casos"]["CT-S02"] = {
            "valor_armazenado_alergia": valor,
            "valores_armazenados_evolucao_medica": [m[0] for m in med],
            "texto_original_encontrado_no_banco": texto_claro,
            "passou": bool(valor) and not texto_claro,
        }
        acoes = con.execute(
            "SELECT acao, COUNT(*) FROM audit_logs WHERE timestamp >= ? GROUP BY acao",
            (ev["executado_em_utc"].replace("T", " ").replace("+00:00", ""),)).fetchall()
        exemplo = con.execute(
            "SELECT timestamp, operador_id, acao, recurso, recurso_id, ip_origem FROM audit_logs ORDER BY timestamp DESC LIMIT 5").fetchall()
        negadas_criancas = [x for x in res if x["obtido"] == 403 and not x["verificacao"].startswith(("Operador: cadastro", "Operador: listar"))]
        registros_negados = acoes_dict = dict(acoes)
        n_negados = acoes_dict.get("ACESSO_NEGADO", 0)
        ev["casos"]["CT-S03"] = {
            "registros_por_acao_desde_o_inicio": acoes_dict,
            "ultimos_registros": [list(map(str, e)) for e in exemplo],
            "tentativas_403_em_rotas_de_acolhidos": len(negadas_criancas),
            "registros_ACESSO_NEGADO_na_auditoria": n_negados,
            "campos_registrados": ["timestamp (UTC)", "operador_id", "acao", "recurso", "recurso_id", "ip_origem", "detalhes"],
            "observacao": "As rotas de gestão de usuários (auth) ainda não registram tentativas negadas.",
            "passou": n_negados == len(negadas_criancas) and n_negados > 0,
        }
        con.close()

    # CT-D01 carga
    tempos, codigos, fim = [], [], time.time() + a.segundos
    trava = threading.Lock()

    def trabalhador(n):
        i = n
        while time.time() < fim:
            caminho = "/api/v1/criancas/" if i % 2 == 0 else f"/api/v1/criancas/{ids[i % len(ids)]}"
            st, _, ms = chamar(base, "GET", caminho, token=t_coord)
            with trava:
                tempos.append(ms)
                codigos.append(st)
            i += 1

    threads = [threading.Thread(target=trabalhador, args=(n,)) for n in range(a.conexoes)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    total = len(codigos)
    ok = sum(1 for c in codigos if c == 200)
    erros5xx = sum(1 for c in codigos if c >= 500 or c == 0)
    p95 = percentil(tempos, 95)
    ev["casos"]["CT-D01"] = {
        "conexoes": a.conexoes, "duracao_s": a.segundos, "requisicoes": total,
        "sucesso_200_pct": round(100 * ok / total, 2), "erros_5xx_ou_conexao_pct": round(100 * erros5xx / total, 2),
        "latencia_ms": {"media": round(statistics.mean(tempos), 1), "p50": round(percentil(tempos, 50), 1),
                        "p90": round(percentil(tempos, 90), 1), "p95": round(p95, 1), "max": round(max(tempos), 1)},
        "criterio": "p95 < 1500 ms e 0% de erros 5xx",
        "passou": p95 < 1500 and erros5xx == 0,
    }

    saida = Path(a.saida) if a.saida else Path("docs/evidencias") / f"bancada_{datetime.now():%Y%m%d-%H%M%S}.json"
    saida.parent.mkdir(parents=True, exist_ok=True)
    saida.write_text(json.dumps(ev, ensure_ascii=False, indent=2), encoding="utf-8")
    for cid, c in ev["casos"].items():
        print(f"{cid}: {'PASSOU' if c['passou'] else 'FALHOU'}")
    print(json.dumps(ev["casos"].get("CT-D01"), ensure_ascii=False))
    print(f"Evidência: {saida}")


if __name__ == "__main__":
    main()
