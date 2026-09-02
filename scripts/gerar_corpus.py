"""
CardioIA - Fase 1 | Gerador do corpus clinico sintetico (complementar)
=======================================================================
Gera dois arquivos .txt em docs/:
  - laudos_ecg_sinteticos.txt   (150 laudos de ECG)
  - anamneses_sinteticas.txt    (150 relatos de anamnese em 1a pessoa)

IMPORTANTE: este corpus e SINTETICO e COMPLEMENTAR. Ele nao substitui
os dois textos de fonte real exigidos pela Parte 2 -- serve como corpus
de treino em portugues para tarefas de extracao de sintomas e analise
de sentimento, onde textos academicos formais nao ajudam.

Semente fixa (SEED = 13) => reproduzivel.
Uso: python scripts/gerar_corpus.py
"""

import numpy as np

SEED = 13
rng = np.random.default_rng(SEED)
N = 150

RITMO = ["ritmo sinusal regular", "ritmo sinusal com arritmia respiratoria",
         "fibrilacao atrial de resposta ventricular controlada",
         "taquicardia sinusal", "bradicardia sinusal"]
ACHADO = [
    "sem alteracoes agudas da repolarizacao ventricular",
    "presenca de extrassistoles ventriculares isoladas",
    "sobrecarga ventricular esquerda pelo criterio de Sokolow-Lyon",
    "bloqueio de ramo direito incompleto",
    "alteracao inespecifica da onda T em parede inferior",
    "infradesnivelamento do segmento ST de 1 mm em V5-V6",
    "eixo eletrico desviado para a esquerda",
]
CONDUTA = [
    "Sugere-se correlacao clinica.",
    "Recomenda-se ecocardiograma transtoracico complementar.",
    "Indicado Holter de 24 horas para melhor caracterizacao.",
    "Manter seguimento ambulatorial de rotina.",
    "Encaminhar para avaliacao cardiologica em carater prioritario.",
]
SINTOMA = [
    "dor no peito ao esforco", "falta de ar ao subir escadas",
    "palpitacoes noturnas", "cansaco aos minimos esforcos",
    "inchaco nos tornozelos ao fim do dia", "tontura ao levantar",
    "aperto no peito que irradia para o braco esquerdo",
    "sensacao de coracao acelerado em repouso", "sudorese fria",
]
TEMPO = ["ha tres dias", "ha duas semanas", "ha cerca de um mes",
         "desde o inicio do ano", "ha mais de seis meses", "ha poucas horas"]
TOM_NEG = [
    "Estou muito preocupado, isso nunca tinha acontecido comigo.",
    "Tenho medo de que seja algo grave no coracao.",
    "Nao consigo mais fazer minhas atividades normais e isso me angustia.",
    "Ja procurei o pronto-socorro duas vezes e continuo sem resposta.",
    "Ando dormindo mal por causa disso.",
]
TOM_NEU = [
    "Vim apenas para a consulta de rotina.",
    "O sintoma aparece e some, nao chega a me atrapalhar.",
    "Meu medico pediu que eu retornasse para reavaliacao.",
    "Estou tomando a medicacao conforme orientado.",
]
TOM_POS = [
    "Desde que comecei a caminhar todo dia, tenho me sentido bem melhor.",
    "Melhorei bastante depois do ajuste do remedio.",
    "Estou animado com os resultados dos ultimos exames.",
]

# ------------------------------------------------------------------ laudos
laudos = ["CORPUS SINTETICO DE LAUDOS DE ECG - PROJETO CardioIA",
          "Gerado por scripts/gerar_corpus.py (dados nao reais)",
          "=" * 68, ""]
for i in range(1, N + 1):
    fc = rng.integers(42, 148)
    laudos.append(f"[LAUDO {i:03d}]")
    laudos.append(
        f"Eletrocardiograma de repouso, 12 derivacoes. Frequencia cardiaca de "
        f"{fc} bpm. Observa-se {rng.choice(RITMO)}, com "
        f"{rng.choice(ACHADO)}. {rng.choice(ACHADO)}. {rng.choice(CONDUTA)}"
    )
    laudos.append("")

with open("docs/laudos_ecg_sinteticos.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(laudos))

# --------------------------------------------------------------- anamneses
anam = ["CORPUS SINTETICO DE RELATOS DE PACIENTES - PROJETO CardioIA",
        "Gerado por scripts/gerar_corpus.py (dados nao reais)",
        "Util para analise de sentimento e extracao de sintomas.",
        "=" * 68, ""]
for i in range(1, N + 1):
    n_sint = rng.integers(1, 4)
    sintomas = rng.choice(SINTOMA, n_sint, replace=False)
    lista = sintomas[0] if n_sint == 1 else \
        ", ".join(sintomas[:-1]) + " e " + sintomas[-1]
    tom = [TOM_NEG, TOM_NEU, TOM_POS][rng.choice(3, p=[0.5, 0.35, 0.15])]
    idade = rng.integers(31, 86)
    anam.append(f"[RELATO {i:03d}]")
    anam.append(
        f"Paciente de {idade} anos relata {lista}, {rng.choice(TEMPO)}. "
        f"{rng.choice(tom)}"
    )
    anam.append("")

with open("docs/anamneses_sinteticas.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(anam))

print(f"OK  docs/laudos_ecg_sinteticos.txt   ({N} laudos)")
print(f"OK  docs/anamneses_sinteticas.txt    ({N} relatos)")
