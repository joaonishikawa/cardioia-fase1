"""
CardioIA - Fase 1 | Gerador do dataset de imagens de ECG sintetico
===================================================================
Gera 120 imagens .png em imagens/, divididas em 4 classes:
  normal (30) | taquicardia (30) | bradicardia (30) | arritmia (30)

Cada imagem simula uma tira de ritmo de ECG (derivacao II) desenhada
sobre papel milimetrado padrao (25 mm/s, 10 mm/mV). O sinal e construido
somando as ondas P, Q, R, S e T como gaussianas, com jitter de intervalo
RR, variacao de amplitude, deriva de linha de base e ruido branco --
para que o dataset nao seja trivialmente separavel por um unico pixel.

NENHUM exame real de paciente foi utilizado: todas as imagens sao
sinteticas e nao contem dado identificavel.

Semente fixa (SEED = 7) => o dataset e reproduzivel.
Uso: python scripts/gerar_ecg.py
"""

import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

SEED = 7
rng = np.random.default_rng(SEED)

FS = 250          # taxa de amostragem (Hz)
DUR = 5.0         # duracao da tira (segundos)
POR_CLASSE = 30

CLASSES = {
    # nome:        (bpm_min, bpm_max, jitter_RR, prob_batimento_ectopico)
    "normal":      (62, 92, 0.020, 0.00),
    "taquicardia": (105, 165, 0.025, 0.00),
    "bradicardia": (38, 55, 0.030, 0.00),
    "arritmia":    (58, 105, 0.180, 0.22),
}


def gaussiana(t, centro, amplitude, largura):
    return amplitude * np.exp(-((t - centro) ** 2) / (2 * largura ** 2))


def batimento(t, t0, escala=1.0, ectopico=False):
    """Monta um complexo P-QRS-T centrado em t0 (em segundos)."""
    s = np.zeros_like(t)
    if ectopico:
        # Extrassistole ventricular: sem onda P, QRS alargado e T invertido
        s += gaussiana(t, t0, -0.10 * escala, 0.020)
        s += gaussiana(t, t0 + 0.02, 1.35 * escala, 0.032)
        s += gaussiana(t, t0 + 0.07, -0.32 * escala, 0.030)
        s += gaussiana(t, t0 + 0.20, -0.28 * escala, 0.070)
        return s
    s += gaussiana(t, t0 - 0.16, 0.13 * escala, 0.026)   # P
    s += gaussiana(t, t0 - 0.02, -0.09 * escala, 0.010)  # Q
    s += gaussiana(t, t0, 1.05 * escala, 0.011)          # R
    s += gaussiana(t, t0 + 0.025, -0.22 * escala, 0.012) # S
    s += gaussiana(t, t0 + 0.19, 0.26 * escala, 0.045)   # T
    return s


def gerar_sinal(classe):
    bpm_min, bpm_max, jitter, p_ect = CLASSES[classe]
    t = np.arange(0, DUR, 1 / FS)
    sinal = np.zeros_like(t)

    bpm = rng.uniform(bpm_min, bpm_max)
    rr = 60.0 / bpm
    t0 = rng.uniform(0.25, 0.55)
    while t0 < DUR - 0.25:
        ect = rng.random() < p_ect
        escala = rng.normal(1.0, 0.07)
        sinal += batimento(t, t0, escala, ect)
        passo = rr * rng.normal(1.0, jitter)
        if ect:
            passo *= 1.45  # pausa compensatoria
        t0 += max(passo, 0.28)

    # deriva de linha de base (respiracao) + ruido de captacao
    sinal += 0.055 * np.sin(2 * np.pi * rng.uniform(0.15, 0.35) * t + rng.uniform(0, 6))
    sinal += rng.normal(0, 0.016, t.size)
    return t, sinal, bpm


def salvar(t, sinal, caminho):
    fig, ax = plt.subplots(figsize=(8, 2.6), dpi=110)

    # papel milimetrado: 0,04 s (1 mm) fino / 0,20 s (5 mm) grosso
    ax.set_facecolor("#fdf3f2")
    for x in np.arange(0, DUR + 0.001, 0.04):
        ax.axvline(x, color="#f3c9c4", lw=0.4, zorder=0)
    for x in np.arange(0, DUR + 0.001, 0.20):
        ax.axvline(x, color="#e08b82", lw=0.7, zorder=0)
    for y in np.arange(-1.5, 1.81, 0.1):
        ax.axhline(y, color="#f3c9c4", lw=0.4, zorder=0)
    for y in np.arange(-1.5, 1.81, 0.5):
        ax.axhline(y, color="#e08b82", lw=0.7, zorder=0)

    ax.plot(t, sinal, color="#101418", lw=1.05, zorder=2)
    ax.set_xlim(0, DUR)
    ax.set_ylim(-1.0, 1.7)
    ax.set_xticks([])
    ax.set_yticks([])
    for lado in ax.spines.values():
        lado.set_visible(False)
    fig.tight_layout(pad=0.1)
    fig.savefig(caminho, facecolor="#fdf3f2")
    plt.close(fig)


os.makedirs("imagens", exist_ok=True)
linhas = ["arquivo,classe,bpm_estimado"]

for classe in CLASSES:
    for i in range(1, POR_CLASSE + 1):
        t, sinal, bpm = gerar_sinal(classe)
        nome = f"ecg_{classe}_{i:03d}.png"
        salvar(t, sinal, os.path.join("imagens", nome))
        linhas.append(f"{nome},{classe},{bpm:.0f}")

with open("imagens/rotulos.csv", "w", encoding="utf-8") as f:
    f.write("\n".join(linhas) + "\n")

print(f"OK  imagens/  ({POR_CLASSE * len(CLASSES)} imagens + rotulos.csv)")
