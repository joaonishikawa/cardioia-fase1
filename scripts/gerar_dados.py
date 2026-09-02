"""
CardioIA - Fase 1 | Gerador do dataset numerico simulado
=========================================================
Gera dados/pacientes_cardio.csv com 300 pacientes sinteticos.

As distribuicoes foram calibradas para se aproximar de faixas
epidemiologicas tipicas da populacao adulta brasileira atendida em
ambulatorio de cardiologia. NENHUM dado real de paciente foi usado:
o arquivo e 100% sintetico e nao contem informacao identificavel.

Semente fixa (SEED = 42) => o dataset e reproduzivel.
Uso: python scripts/gerar_dados.py
"""

import numpy as np
import pandas as pd

SEED = 42
N = 300
rng = np.random.default_rng(SEED)


def clip(v, lo, hi):
    return np.clip(v, lo, hi)


# ---------------------------------------------------------------- demografia
idade = clip(rng.normal(58, 13, N), 29, 89).round().astype(int)
sexo = rng.choice(["M", "F"], N, p=[0.52, 0.48])

# --------------------------------------------------------- fatores de risco
# Pressao arterial cresce com a idade
pas = clip(rng.normal(118 + 0.45 * (idade - 45), 16, N), 90, 205).round().astype(int)
pad = clip(pas * 0.62 + rng.normal(0, 6, N), 55, 125).round().astype(int)

colesterol = clip(rng.normal(198 + 0.35 * (idade - 50), 38, N), 110, 400).round().astype(int)
hdl_base = np.where(sexo == "F", 56, 46)
hdl = clip(rng.normal(hdl_base, 12, N), 20, 100).round().astype(int)
ldl = clip(colesterol - hdl - rng.normal(28, 9, N), 50, 300).round().astype(int)

glicemia = clip(rng.normal(99, 24, N), 65, 300).round().astype(int)
imc = clip(rng.normal(27.4, 4.6, N), 16.5, 47.0).round(1)
fc_repouso = clip(rng.normal(76, 12, N), 45, 130).round().astype(int)

tabagismo = rng.choice(["nunca", "ex-fumante", "atual"], N, p=[0.55, 0.27, 0.18])
diabetes = (glicemia > 126).astype(int) | (rng.random(N) < 0.06).astype(int)
hist_familiar = (rng.random(N) < 0.34).astype(int)
atividade_min = clip(rng.gamma(2.0, 55, N), 0, 600).round().astype(int)

dor_toracica = rng.choice(
    ["assintomatico", "atipica", "tipica", "nao_anginosa"],
    N, p=[0.34, 0.28, 0.22, 0.16],
)
dispneia = (rng.random(N) < 0.31).astype(int)
fadiga = (rng.random(N) < 0.38).astype(int)
edema_mmii = (rng.random(N) < 0.19).astype(int)

# -------------------------------------------------- desfecho (modelo logistico)
# Coeficientes escolhidos para refletir o peso clinico relativo conhecido
# dos fatores de risco. Serve para que o dataset tenha sinal aprendivel
# nas fases seguintes do projeto, sem ser trivialmente separavel.
z = (
    -1.85
    + 0.048 * (idade - 55)
    + 0.020 * (pas - 125)
    + 0.006 * (ldl - 120)
    - 0.022 * (hdl - 50)
    + 0.85 * diabetes
    + 0.62 * hist_familiar
    + 0.70 * (tabagismo == "atual")
    + 0.28 * (tabagismo == "ex-fumante")
    + 0.055 * (imc - 25)
    - 0.0022 * atividade_min
    + 0.95 * (dor_toracica == "tipica")
    + 0.40 * (dor_toracica == "atipica")
    + 0.45 * dispneia
    + 0.35 * edema_mmii
    + 0.30 * (sexo == "M")
)
prob = 1 / (1 + np.exp(-z))
evento = (rng.random(N) < prob).astype(int)

classe_risco = pd.cut(
    prob, bins=[-0.01, 0.20, 0.55, 1.01], labels=["baixo", "moderado", "alto"]
)

df = pd.DataFrame(
    {
        "id_paciente": [f"CIA-{i:04d}" for i in range(1, N + 1)],
        "idade": idade,
        "sexo": sexo,
        "pressao_sistolica": pas,
        "pressao_diastolica": pad,
        "colesterol_total": colesterol,
        "hdl": hdl,
        "ldl": ldl,
        "glicemia_jejum": glicemia,
        "imc": imc,
        "frequencia_cardiaca_repouso": fc_repouso,
        "tabagismo": tabagismo,
        "diabetes": diabetes,
        "historico_familiar_dac": hist_familiar,
        "atividade_fisica_min_semana": atividade_min,
        "dor_toracica": dor_toracica,
        "dispneia": dispneia,
        "fadiga": fadiga,
        "edema_mmii": edema_mmii,
        "classe_risco": classe_risco,
        "evento_cardiaco_12m": evento,
    }
)

# ------------------------------------------------------ dados faltantes (3%)
# Introduzidos de proposito: prontuarios reais tem lacunas e a Fase 2
# precisara tratar isso. Documentado no README.
for col in ["colesterol_total", "hdl", "ldl", "imc", "atividade_fisica_min_semana"]:
    mask = rng.random(N) < 0.03
    df.loc[mask, col] = np.nan

df.to_csv("dados/pacientes_cardio.csv", index=False, encoding="utf-8")

print(f"OK  dados/pacientes_cardio.csv  ({len(df)} linhas, {len(df.columns)} colunas)")
print(f"    eventos positivos: {evento.sum()} ({evento.mean():.1%})")
print(f"    distribuicao de risco: {df.classe_risco.value_counts().to_dict()}")
