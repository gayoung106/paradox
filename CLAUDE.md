# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an academic research project investigating the **paradox of inclusive organizational culture** — how DEI-oriented climates can indirectly increase Unethical Pro-organizational Behavior (UPB) through organizational identification. The project combines:

1. **Data Analysis Pipeline** (`code/`) — Python scripts for empirical statistical analysis
2. **Multi-Agent Manuscript System** (`.claude/`) — AI-assisted academic paper writing orchestration

### Research Model
```
Equity Climate (Y8_1~5)    ┐
                            ├─→ Organizational Identification (Y1_1~6) ─→ UPB (Y20_1~5)
Inclusion Climate (Y8_6~9) ┘         ↑ moderated by Ethical Leadership (Y11_1~5)

Also: OI → OCB (Y19_1~4)  [positive side of dual mechanism]
```

### Hypotheses (`.claude/memory/project/hypotheses.md`)
- H1/H2: Equity & inclusion climate → OI (positive)
- H3: OI → UPB (positive)
- H4/H5: OI mediates DEI → UPB
- H6: Ethical leadership moderates OI → UPB (attenuates)

## Data Analysis

### Setup

```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### Running Analysis Scripts

Scripts in `code/` are numbered and must be run sequentially. Each script reads from `raw/` or `processed/` and writes results to `results/`.

```powershell
cd code
python 00_data_read.py          # Load raw SPSS file
python 02_preprocessing.py      # Create composite variables
python 03_reliability.py        # Cronbach's alpha
python 12_cfa_dei.py            # CFA for DEI subscales
python 04_correlation.py        # Correlation matrix (HC3 SEs)
python 05_regression_upb.py     # Main OLS regression (UPB)
python 06_mediation.py          # Bootstrap mediation (5000 iter)
python 07_moderation.py         # Moderation analysis
python 08_moderated_mediation.py # Conditional indirect effects
python 11_regression_ocb.py     # OCB regression
python 14_common_method_bias.py # Harman single factor test
```

### Data Files
- `raw/raw_data.sav` — Original SPSS survey data (n≈2,020, Korean organizational sample)
- `processed/analysis_data.csv` — Preprocessed composite variables
- `results/` — All analysis outputs in Markdown format

### Key Statistical Methods
- OLS regression with **HC3 robust standard errors** (used throughout)
- Bootstrap mediation with **5,000 iterations**
- **EFA + CFA** for construct validation (2-factor DEI model: CFI=.962, TLI=.947)
- Harman Single Factor Test for common method bias

## Multi-Agent Manuscript System

### Architecture (`.claude/`)

```
.claude/
├── agents/
│   ├── director/        # Research director: orchestrates manuscript, approve/reject decisions
│   ├── writers/         # Section writers: intro, theory, methods, results, discussion
│   ├── reviewers/       # Peer reviewers: SSCI, methodology, contribution, logic, theory, writing
│   ├── methods/         # Statistical agents: measurement, statistics, interpretation
│   ├── orchestration/   # Workflow management: routing, revision control, escalation
│   └── integration/     # Cross-section consistency checkers
├── config/
│   ├── agent_rules.md        # Universal rules for all agents
│   ├── orchestration_rules.md
│   └── *.json               # Scoring schemas, thresholds, review policies
├── memory/project/
│   ├── contribution.md  # Core contributions — must not be diluted
│   ├── hypotheses.md    # Canonical hypothesis statements
│   └── theory_map.md    # Theoretical framework
└── workflows/
    └── reviewer_iteration_workflow.md
```

### Section Workflow
Writer → Reviewer → Revision → Rewrite → Re-review → Approve → next section

Section order: intro → theory → methods → results → discussion → conclusion → abstract

Approval requires: score threshold met, major concerns resolved, contribution maintained.

### Agent Rules (`.claude/config/agent_rules.md`)
These apply to ALL agents writing manuscript content:

- **All writing must be in Korean** (SSCI/KCI academic style)
- **No hallucination** — all claims must match actual analysis results in `results/`
- **No fake citations** — only cite real, verifiable prior literature
- **No unsupported causal claims**
- Maintain consistency across sections; reviewer comments must be addressed
- Do not exaggerate contributions; do not shift framing away from the paradox

### Core Framing to Preserve (`.claude/memory/project/contribution.md`)
- Paradox / duality / dark side of loyalty / indirect mechanism
- Do NOT reduce to a simple DEI effects study
- Do NOT shift focus to become primarily a leadership study

## Key Variable Reference

| Variable | Items | Construct |
|----------|-------|-----------|
| Equity Climate | Y8_1~Y8_5 | Independent variable |
| Inclusion Climate | Y8_6~Y8_9 | Independent variable |
| Organizational Identification (OI) | Y1_1~Y1_6 | Mediator |
| Ethical Leadership | Y11_1~Y11_5 | Moderator |
| OCB | Y19_1~Y19_4 | Dependent variable (positive) |
| UPB | Y20_1~Y20_5 | Dependent variable (dark side) |

Control variables: Gender, Age, Education, Income, Sector (public/private), Org type, Company size
