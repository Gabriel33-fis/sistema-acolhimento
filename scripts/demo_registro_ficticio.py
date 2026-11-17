#!/usr/bin/env python3
"""Demonstração: cria e consulta um registro FICTÍCIO na mesma versão em execução.

Uso:
    python scripts/demo_registro_ficticio.py                                   # local (http://localhost:8000)
    python scripts/demo_registro_ficticio.py https://sistema-acolhimento-api.onrender.com

O script usa apenas a biblioteca padrão do Python. Ao final, grava um arquivo
JSON em docs/evidencias/ com a versão, o commit, o ID criado e os horários,
que pode ser anexado ao relatório como evidência da demonstração.
"""
import json
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

BASE = (sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000").rstrip("/")
EMAIL = "admin@instituicao.org"
SENHA = "admin123"


def chamar(metodo, caminho, corpo=None, token=None):
    dados = json.dumps(corpo).encode() if corpo is not None else None
    req = urllib.request.Request(BASE + caminho, data=dados, method=metodo)
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(req, timeout=90) as resp:  # 90 s cobre o cold start do Render
            return resp.status, json.loads(resp.read() or b"null")
    except urllib.error.HTTPError as err:
        return err.code, json.loads(err.read() or b"null")


def agora():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def passo(n, texto):
    print(f"\n[{n}] {texto}")


def main():
    evidencia = {"api": BASE, "inicio_utc": agora()}

    passo(1, "Versão em execução")
    st, versao_antes = chamar("GET", "/health")
    print(f"    HTTP {st} -> {versao_antes}")
    if st != 200:
        sys.exit("API indisponível.")
    evidencia["versao_antes"] = versao_antes

    passo(2, f"Login como Coordenador ({EMAIL})")
    st, login = chamar("POST", "/api/v1/auth/login", {"email": EMAIL, "senha": SENHA})
    print(f"    HTTP {st} -> perfil {login.get('perfil') if login else None}")
    if st != 200:
        sys.exit("Falha no login.")
    token = login["access_token"]

    marcador = datetime.now().strftime("%Y%m%d-%H%M%S")
    registro = {
        "nome_completo": f"[FICTÍCIO] Criança Demonstração {marcador}",
        "data_nascimento": "2015-03-10",
        "alergias": "[FICTÍCIO] Alergia a amendoim (dado de teste)",
    }

    passo(3, "Criação do registro fictício")
    print(f"    Enviado: {registro}")
    st, criado = chamar("POST", "/api/v1/criancas/", registro, token)
    print(f"    HTTP {st} -> {criado}")
    if st != 201:
        sys.exit("Falha na criação.")
    crianca_id = criado["id"]
    evidencia.update({"registro_enviado": registro, "id_criado": crianca_id, "criado_utc": agora()})

    passo(4, "Consulta na listagem (busca pelo marcador)")
    st, lista = chamar("GET", f"/api/v1/criancas/?busca={marcador}", token=token)
    encontrado = any(item["id"] == crianca_id for item in (lista or []))
    print(f"    HTTP {st} -> {len(lista or [])} resultado(s); ID criado presente: {encontrado}")

    passo(5, "Consulta do detalhe (prontuário decifrado)")
    st, detalhe = chamar("GET", f"/api/v1/criancas/{crianca_id}", token=token)
    print(f"    HTTP {st} -> {detalhe}")
    confere = (
        st == 200
        and detalhe["nome_completo"] == registro["nome_completo"]
        and detalhe["alergias_decifradas"] == registro["alergias"]
    )
    evidencia.update({"consultado_utc": agora(), "detalhe_consultado": detalhe})

    passo(6, "Versão após a consulta")
    _, versao_depois = chamar("GET", "/health")
    print(f"    {versao_depois}")
    mesma_versao = (
        versao_antes.get("versao") == versao_depois.get("versao")
        and versao_antes.get("commit") == versao_depois.get("commit")
    )
    evidencia["versao_depois"] = versao_depois

    evidencia["resultado"] = {
        "encontrado_na_listagem": encontrado,
        "dados_conferem": confere,
        "mesma_versao_do_inicio_ao_fim": mesma_versao,
    }
    ok = encontrado and confere and mesma_versao

    pasta = Path(__file__).resolve().parent.parent / "docs" / "evidencias"
    pasta.mkdir(parents=True, exist_ok=True)
    arquivo = pasta / f"demo_{marcador}.json"
    arquivo.write_text(json.dumps(evidencia, ensure_ascii=False, indent=2), encoding="utf-8")

    print("\n" + "=" * 60)
    print(f"Versão: {versao_antes.get('versao')} | commit: {versao_antes.get('commit')}")
    print(f"Registro criado e consultado: {'SIM' if ok else 'NÃO'}")
    print(f"Evidência gravada em: {arquivo}")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
