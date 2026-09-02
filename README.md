# CardioIA — Fase 1: Batimentos de Dados

> Levantamento, organização e documentação das três bases que vão alimentar os
> módulos inteligentes do CardioIA nas fases seguintes: **dados numéricos (IoT)**,
> **dados textuais (NLP)** e **dados visuais (Visão Computacional)**.

**FIAP — Graduação em Inteligência Artificial · 2º ano · 2TIAOA**
**Fase 1 — Batimentos de Dados**

### Integrantes

<!-- EDITAR: o pessoal do grupo completa as linhas abaixo -->

| Nome | RM |
|------|----|
| Guilherme Filartiga Pereira da Silva | RM568034 |
| João Pedro Nishikawa Alves | RM562376 |
| Gustavo Trindade Soares | RM567848 |

---

## 📦 Links dos dados hospedados

🔗 [LINK DO REPOSITÓRIO NO GITHUB](https://github.com/joaonishikawa/cardioia-fase1)
🔗 [LINK DA PASTA NO DRIVE](https://drive.google.com/drive/folders/16TdNh6JD8L_jr3J-mNYy032C7hcGvhqM?usp=sharing)

| Base | Formato | Volume | Link público |
|------|---------|--------|--------------|
| Dados numéricos | `.csv` | 300 pacientes × 21 variáveis | `COLAR_LINK_AQUI` |
| Dados textuais | `.txt` | 4 arquivos (2 reais + 2 sintéticos) | `COLAR_LINK_AQUI` |
| Dados visuais | `.png` | 120 imagens de ECG | `COLAR_LINK_AQUI` |

> ⚠️ Os arquivos também estão versionados neste repositório (`dados/`, `docs/`,
> `imagens/`). Os links acima são a cópia em armazenamento público exigida pelo
> enunciado — confira que estão abertos para *qualquer pessoa com o link*.

---

## 🗂 Estrutura do repositório

```
cardioia-fase1/
├── README.md                        ← este arquivo
├── dados/
│   └── pacientes_cardio.csv         ← Parte 1: 300 pacientes, 21 variáveis
├── docs/
│   ├── laudos_ecg_sinteticos.txt    ← Parte 2: 150 laudos (corpus técnico)
│   ├── anamneses_sinteticas.txt     ← Parte 2: 150 relatos (corpus subjetivo)
│   ├── texto_real_01_opas_doencas_cardiovasculares.txt   ← Parte 2: OPAS/OMS
│   └── texto_real_02_ms_hipertensao.txt                  ← Parte 2: Min. da Saúde
├── imagens/
│   ├── ecg_normal_001.png … ecg_arritmia_030.png   ← Parte 3: 120 imagens
│   └── rotulos.csv                  ← arquivo → classe → bpm estimado
└── scripts/
    ├── gerar_dados.py               ← gera o CSV (seed 42)
    ├── gerar_ecg.py                 ← gera as imagens (seed 7)
    └── gerar_corpus.py              ← gera o corpus clínico (seed 13)
```

**Reprodutibilidade.** As três bases são geradas por script com semente fixa.
Qualquer pessoa reproduz exatamente os mesmos arquivos:

```bash
pip install numpy pandas matplotlib
python scripts/gerar_dados.py
python scripts/gerar_corpus.py
python scripts/gerar_ecg.py
```

---

## 🩺 Parte 1 — Dados numéricos (IoT)

**Arquivo:** `dados/pacientes_cardio.csv` · **300 linhas × 21 colunas**

### Origem dos dados

Os dados são **simulados**, gerados por `scripts/gerar_dados.py`. Essa foi uma
decisão consciente, não uma saída fácil:

1. **Privacidade por construção.** Dados cardiológicos reais são dados pessoais
   sensíveis (LGPD, art. 5º, II). Bases públicas de pacientes reais exigem termo
   de uso e, em geral, processo de autorização — inviável no prazo da fase e
   desnecessário para o objetivo, que é *montar o laboratório*.
2. **Controle das distribuições.** Simulando, sabemos exatamente qual é a
   estrutura causal por trás do desfecho — o que permite, na Fase 2, verificar se
   o modelo aprendeu o padrão certo ou apenas decorou ruído.
3. **Calibração realista.** As distribuições foram ajustadas para se aproximar de
   faixas conhecidas da população adulta em seguimento cardiológico: idade média
   ~58 anos, IMC médio ~27, ~18% de fumantes ativos, pressão sistólica crescendo
   com a idade, HDL mais alto em mulheres.

**O que o CSV contém**

| Grupo | Variáveis |
|-------|-----------|
| Identificação | `id_paciente` (pseudônimo, sem vínculo com pessoa real) |
| Demografia | `idade`, `sexo` |
| Hemodinâmica | `pressao_sistolica`, `pressao_diastolica`, `frequencia_cardiaca_repouso` |
| Laboratório | `colesterol_total`, `hdl`, `ldl`, `glicemia_jejum` |
| Antropometria | `imc` |
| Hábitos e história | `tabagismo`, `diabetes`, `historico_familiar_dac`, `atividade_fisica_min_semana` |
| Sintomas | `dor_toracica`, `dispneia`, `fadiga`, `edema_mmii` |
| Alvos | `classe_risco` (baixo/moderado/alto), `evento_cardiaco_12m` (0/1) |

**Distribuição do desfecho:** 115 eventos positivos em 300 pacientes (38,3%) —
proporção compatível com um ambulatório de cardiologia, não com a população geral.
Isso importa: um modelo treinado aqui **não** pode ser aplicado a triagem populacional
sem recalibração.

### Variáveis mais relevantes clinicamente — e por quê

| Variável | Por que importa para a IA |
|----------|---------------------------|
| **`idade`** | O preditor isolado mais forte de risco cardiovascular. Serve de linha de base: qualquer modelo precisa superar a predição feita só com idade, senão não está agregando nada. |
| **`pressao_sistolica`** | Hipertensão é o principal fator de risco modificável. É contínua, medida rotineiramente e — crucial para o CardioIA — **capturável por sensor IoT**, o que a torna candidata natural ao monitoramento contínuo da Fase 4. |
| **`ldl` e `hdl`** | O colesterol total isolado engana: um total alto com HDL alto tem significado oposto ao de um total alto com LDL alto. Separar as frações evita que o modelo aprenda uma relação invertida. |
| **`dor_toracica`** (tipo) | Variável categórica de alto valor discriminativo. Dor **típica** (anginosa) tem probabilidade pré-teste muito maior que dor atípica — é o tipo de nuance que o NLP da Parte 2 pode extrair de texto livre. |
| **`diabetes` + `glicemia_jejum`** | Diabetes é considerado equivalente de doença coronariana. Manter as duas permite testar redundância e vazamento (`diabetes` é derivada parcialmente da glicemia — documentado no script). |
| **`frequencia_cardiaca_repouso`** | FC de repouso elevada é preditor independente de mortalidade e é a variável mais barata de coletar por wearable — ponte direta com o módulo IoT. |
| **`atividade_fisica_min_semana`** | Único fator claramente **protetor** do conjunto. Sem ele, o modelo só aprende o que aumenta risco, e a saída fica clinicamente inútil para recomendação. |

### Qualidade e limpeza

O CSV tem **~3% de valores ausentes** em `colesterol_total`, `hdl`, `ldl`, `imc` e
`atividade_fisica_min_semana` — **introduzidos de propósito**. Prontuários reais
têm lacunas, e a Fase 2 precisa exercitar imputação em vez de receber um dataset
artificialmente perfeito. O tratamento (imputação por mediana, por grupo, ou
descarte) é decisão a ser tomada e justificada na próxima fase.

---

## 📄 Parte 2 — Dados textuais (NLP)

**Arquivos:** `docs/*.txt` — quatro arquivos, em duas naturezas distintas.

### Textos de fonte real

Dois documentos institucionais em português, de acesso público, reproduzidos na
íntegra em UTF-8. Cada arquivo traz um cabeçalho com **fonte, URL, data de acesso e
natureza do material** — rastreabilidade é item de governança, não burocracia.

| Arquivo | Título | Fonte | Acesso |
|---------|--------|-------|--------|
| `texto_real_01_opas_doencas_cardiovasculares.txt` | Doenças cardiovasculares | OPAS/OMS — Organização Pan-Americana da Saúde | 25/08/2026 |
| `texto_real_02_ms_hipertensao.txt` | Hipertensão (pressão alta) | Ministério da Saúde — Saúde de A a Z | 25/08/2026 |

**Por que estas duas fontes.** Elas se complementam em escala e em registro. A da
OPAS traz o panorama **global e epidemiológico** — números de mortalidade,
determinantes sociais, política pública, terminologia técnica (hiperlipidemia,
prevenção secundária, doença cerebrovascular). A do Ministério da Saúde traz o
recorte **nacional e assistencial**, em linguagem voltada ao cidadão brasileiro —
como o SUS trata, o que a Farmácia Popular oferece, quais sintomas procurar. Um
modelo treinado só no registro técnico não entende a queixa do paciente; treinado só
no registro leigo, não lê o laudo. O corpus precisa dos dois.

Ambos citam explicitamente sintomas em texto corrido (*"dor ou desconforto no centro
do peito"*, *"dores no peito, dor de cabeça, tonturas, zumbido no ouvido"*), o que os
torna material direto para as tarefas de extração descritas abaixo.

### Corpus sintético (complementar)

| Arquivo | Conteúdo | Serve para |
|---------|----------|------------|
| `laudos_ecg_sinteticos.txt` | 150 laudos de ECG em linguagem técnica | Extração de entidades clínicas, classificação de achados |
| `anamneses_sinteticas.txt` | 150 relatos de paciente em 1ª pessoa | Análise de sentimento, extração de sintomas em linguagem leiga |

Gerados por `scripts/gerar_corpus.py`. São **sintéticos e complementares** — não
substituem as fontes reais, mas resolvem um problema concreto: artigos científicos
não ensinam o modelo a entender como um paciente *descreve* o próprio sintoma.

### Como esses textos serão explorados por algoritmos de NLP

**1. Extração de sintomas (Information Extraction).**
Tokenização e reconhecimento de entidades nomeadas para transformar texto livre em
estrutura. *"Sinto um aperto no peito que irradia para o braço esquerdo há três
dias"* vira `{sintoma: dor_torácica_típica, irradiação: braço_esquerdo, duração: 3d}`.
É a ponte entre a Parte 2 e a Parte 1: o texto vira coluna de dataset.
Ferramentas: **spaCy** (`pt_core_news_sm`) e **NLTK** para o pré-processamento.

**2. Análise de sentimento e triagem de urgência.**
Os relatos de `anamneses_sinteticas.txt` carregam carga emocional variável
(preocupação, neutralidade, melhora). Um classificador de sentimento pode servir de
**sinal auxiliar de priorização** — não para diagnosticar, mas para ordenar a fila
de atendimento remoto. Relato ansioso + sintoma típico é combinação que merece
subir na fila.

**3. Classificação de tópicos.**
Separar automaticamente o corpus em prevenção, diagnóstico, tratamento e prognóstico
permite alimentar o agente conversacional da fase futura com o trecho certo, em vez
de com o documento inteiro.

**4. Normalização de vocabulário.**
O mesmo conceito aparece como *"infarto"*, *"IAM"*, *"ataque cardíaco"* e
*"síndrome coronariana aguda"*. Mapear sinônimos para um termo canônico é
pré-requisito para qualquer busca semântica funcionar.

### Por que isso é relevante para IA em saúde

Porque a maior parte da informação clínica **não está em tabela**. Está em evolução
médica, laudo, queixa de paciente — texto não estruturado. Um sistema que só lê CSV
enxerga uma fração do prontuário. O NLP é o que permite recuperar o resto, e é o que
viabiliza a assistência remota prevista para as próximas fases do CardioIA.

---

## 🖼 Parte 3 — Dados visuais (Visão Computacional)

**Arquivos:** `imagens/` — **120 imagens `.png`** + `rotulos.csv`

### Origem e composição

Imagens **sintéticas** de tiras de ritmo de ECG (derivação II), geradas por
`scripts/gerar_ecg.py`, desenhadas sobre papel milimetrado padrão
(25 mm/s, 10 mm/mV), em quatro classes balanceadas:

| Classe | Imagens | Característica simulada |
|--------|---------|-------------------------|
| `normal` | 30 | Ritmo sinusal, 62–92 bpm |
| `taquicardia` | 30 | 105–165 bpm |
| `bradicardia` | 30 | 38–55 bpm |
| `arritmia` | 30 | RR irregular + extrassístoles ventriculares (QRS alargado, sem onda P, pausa compensatória) |

O sinal é construído somando as ondas **P, Q, R, S e T** como gaussianas, com
variação de intervalo RR, variação de amplitude batimento a batimento, deriva de
linha de base (respiração) e ruído de captação. Isso é intencional: um dataset
limpo demais produziria um classificador que colapsa no primeiro exame real.

O arquivo `rotulos.csv` traz `arquivo, classe, bpm_estimado` — pronto para
carregamento supervisionado.

### Como serão analisadas por algoritmos de Visão Computacional

**1. Pré-processamento e isolamento do traçado.**
Conversão para escala de cinza (`cv2.cvtColor` com `COLOR_BGR2GRAY`), suavização
gaussiana para atenuar o ruído e **limiarização** (Otsu) para separar o traçado
preto do papel milimetrado avermelhado. É a etapa que transforma "foto de exame"
em "sinal analisável".

**2. Detecção de bordas e contornos.**
O detector **Canny** identifica as transições abruptas de intensidade que marcam o
traçado. Operações morfológicas (abertura para remover resíduo da grade, fechamento
para reconectar segmentos) limpam o resultado.

**3. Detecção de padrões — os picos R.**
Localizados os picos R, calcula-se o **intervalo RR** e daí a frequência cardíaca e
sua variabilidade. Aqui a Visão Computacional vira medida clínica: RR regular e
curto → taquicardia; RR irregular → suspeita de fibrilação atrial.

**4. Classificação por CNN.**
Com as 120 imagens rotuladas, treina-se uma rede convolucional (ou aplica-se
transfer learning sobre ResNet/VGG) para classificar a tira. As convoluções
aprendem sozinhas os filtros que detectam morfologia de QRS — sem engenharia manual
de atributos.

**5. Reconhecimento de anomalias.**
Como as classes são conhecidas, dá para treinar tanto um classificador supervisionado
quanto um autoencoder que aprende só o `normal` e sinaliza como anômalo tudo que
reconstruir mal — abordagem útil quando a anomalia é rara.

### Por que isso é relevante para IA em saúde

O ECG é o exame cardiológico mais realizado do mundo e, em boa parte da rede pública,
ainda circula **em papel**. Um modelo que lê a imagem do traçado — e não apenas o
sinal digital — funciona onde o equipamento é antigo e onde não há cardiologista de
plantão. Isso é acesso, não só automação: triagem automática em unidade básica com
encaminhamento do que for alterado.

---

## 🛡 Governança de dados e viés

Não dá para montar a base sem já decidir como ela será governada. Registro do que
foi decidido nesta fase:

### Privacidade e conformidade

- **Nenhum dado pessoal real foi coletado, processado ou armazenado.** As três bases
  são sintéticas. Não há, portanto, tratamento de dado pessoal sensível na acepção
  da LGPD (art. 11) — o que não isenta o projeto de aplicar os princípios desde já.
- **Identificadores são pseudônimos sequenciais** (`CIA-0001`), sem qualquer vínculo
  com pessoa real.
- **Decisão registrada:** ao migrar para dados reais em fases futuras, será
  obrigatório termo de consentimento, anonimização e definição de política de
  retenção e descarte — as etapas 1 e 7 do ciclo de vida de dados (DAMA-DMBOK2).

### Rastreabilidade

Cada base tem **script de geração versionado, com semente fixa e comentado**.
Qualquer pessoa consegue responder: quais dados foram usados, como foram produzidos,
com que parâmetros, em qual versão. É exatamente o que a governança exige registrar —
e o que quase nunca existe em projeto acadêmico.

### Vieses identificados — e assumidos

Nenhuma base é neutra. Os desta são:

| Viés | Descrição | Mitigação prevista |
|------|-----------|--------------------|
| **Viés de prevalência** | 38,3% de eventos positivos reflete ambulatório de cardiologia, não a população geral. | Recalibrar limiar de decisão antes de qualquer uso em triagem populacional. |
| **Viés do gerador** | Os dados vêm de um modelo logístico *que nós escrevemos*. O modelo da Fase 2 tende a "acertar" porque a estrutura causal foi plantada por nós. | Tratar métricas da Fase 2 como validação de pipeline, **não** como evidência de desempenho clínico. |
| **Viés de sexo** | Sintomas de infarto em mulheres frequentemente diferem do padrão clássico (mais dispneia e fadiga, menos dor torácica típica). O gerador **não** modela essa diferença. | Limitação declarada. Ao usar dados reais, avaliar métricas estratificadas por sexo — não só a média. |
| **Viés de representatividade** | Sem variáveis de raça, renda ou acesso a serviço de saúde — determinantes sociais com peso real no desfecho cardiovascular. | Documentado como lacuna. O caso do algoritmo que usou "gasto médico prévio" como proxy de necessidade — e excluiu 17% dos pacientes negros que deveriam ser prioritários — é o alerta de por que proxies aparentemente neutros são perigosos. |
| **Viés linguístico** | O corpus textual é só em português e de registro relativamente formal. | Ampliar com linguagem coloquial e regionalismos antes de treinar chatbot voltado ao público. |

### Limitação principal, dita sem rodeio

**Estes dados servem para construir e testar o pipeline. Não servem para tirar
conclusão clínica alguma.** Qualquer métrica obtida sobre eles mede a corretude da
engenharia, não a validade médica do modelo. Confundir as duas coisas é o erro que
transforma projeto de IA em saúde em risco para paciente.

---

## 🚀 Próximos passos (Fase 2)

- Análise exploratória do CSV: correlações, outliers, tratamento dos 3% ausentes.
- Baseline de classificação para `evento_cardiaco_12m`, comparado ao baseline trivial
  "só idade".
- Pipeline de pré-processamento NLP sobre os quatro `.txt` (tokenização, stopwords,
  lematização, frequência).
- Pré-processamento das imagens: escala de cinza → Otsu → Canny → detecção de picos R.
- Substituição gradual das bases sintéticas por fontes reais, com a documentação de
  origem e licença exigida pela governança.

---

## 📚 Como publicar (passo a passo)

1. Criar o repositório no GitHub como **público** — nome sugerido: `cardioia-fase1`.
2. Subir todo o conteúdo desta pasta (`README.md`, `dados/`, `docs/`, `imagens/`, `scripts/`).
3. Subir as mesmas pastas para o Google Drive ou OneDrive, em uma pasta única.
4. Compartilhar essa pasta como **"qualquer pessoa com o link pode visualizar"**.
5. Colar os links na tabela do topo deste README e fazer commit.
6. Completar a tabela de integrantes e os dois textos reais da Parte 2.
7. Testar o link em uma **janela anônima** antes de entregar — é o erro mais comum.

---

*Projeto acadêmico desenvolvido para a disciplina de PBL da FIAP. Todos os dados são
sintéticos e destinados exclusivamente a fins educacionais. Nenhuma informação contida
neste repositório deve ser utilizada para decisão clínica.*
