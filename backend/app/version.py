"""Identificação única da versão em execução.

A mesma string aparece em /health, em /api/v1/versao, no Swagger e na tela
de login do frontend, para que a demonstração e o relatório citem a mesma versão.
"""
import os

# Versão declarada no relatório. Altere somente aqui (ou via variável APP_VERSION).
VERSAO_PADRAO = "1.0.0-RC"

APP_VERSION = os.getenv("APP_VERSION", VERSAO_PADRAO)

# O Render define RENDER_GIT_COMMIT automaticamente em cada deploy.
_commit = os.getenv("RENDER_GIT_COMMIT") or os.getenv("GIT_COMMIT") or ""
APP_COMMIT = _commit[:7] if _commit else "local"

AMBIENTE = os.getenv("APP_AMBIENTE", "demonstracao-dados-ficticios")


def info_versao() -> dict:
    return {"versao": APP_VERSION, "commit": APP_COMMIT, "ambiente": AMBIENTE}
