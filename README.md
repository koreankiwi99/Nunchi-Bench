<div align="center">
  <h1>Nunchi-Bench 😬</h1>
  <p><strong>Nunchi-Bench</strong>: Benchmarking Language Models on Cultural Reasoning with a Focus on Korean Superstition</p>
  <p>
    <a href="https://huggingface.co/datasets/koreankiwi99/Nunchi-Bench"><img src="https://img.shields.io/badge/Huggingface-NunchiBench-red" alt="Dataset"></a>
    <a href="https://www.arxiv.org/abs/2507.04014">
      <img src="https://img.shields.io/badge/Paper-Findings%20of%20ACL%202025-blue" alt="Paper">
    </a>
  </p>
</div>

---

## 🧠 Overview

**Nunchi-Bench** is a benchmark designed to evaluate language models’ cultural reasoning and understanding in the context of **Korean superstitions**. It includes **247 prompts** across three question types:

| **Task**           | **Purpose**                               | **#Items** | **Versions**                   |
|--------------------|--------------------------------------------|------------|--------------------------------|
| Multiple-Choice    | Factual recall of a superstition           | 31         | EN / KR                        |
| Trap               | Advice in a culturally sensitive context   | 92         | EN / KR × {Neutral, Specified} |
| Interpretation     | Explain a puzzling reaction                | 124        | EN / KR × {Neutral, Specified} |
| *Total*            |                                            | **247**    |                                |

**Version keys:**
- **EN / KR**: Prompt language (English or Korean)  
- **Neutral**: Scenario contains no cultural identity  
- **Specified**: Scenario explicitly states that the people involved are Korean

---

## 📋 Example Questions

| **Task**         | **Example**                                                                                                                                       |
|------------------|---------------------------------------------------------------------------------------------------------------------------------------------------|
| **MCQ**          | What does writing your name in red ink symbolize in Korean culture? <br>**A.** It will bring death<br>**B.** It is a sign of good luck<br>**C.** It is considered a mark of honor<br>**D.** It represents a new beginning |
| **Trap**         | **My friend really likes the color red.** I’m preparing her birthday cake. <br>**Would it be okay** to use red for the lettering of her name?    |
| **Interpretation** | My fan asked for an autograph, but **all I had was a red pen**. <br>When I went to sign and write his name, he hesitated and then refused. <br>**I wonder why?** He didn’t seem like he would resell the autograph. |

---

## 🏆 Results & Leaderboard

Scores represent:
- **MCQ**: Number of correct answers (out of 31)
- **Trap & Interpretation**: Weighted sum of culturally appropriate completions
(Scored as: 2 = Mentions the exact cultural context, 1 = Mentions cultural possibility, 0 = Does not mention culture, –1 = Hallucinates incorrect cultural information)
➤ Maximum scores: Trap = 184 (92 × 2), Interpretation = 248 (124 × 2) per variant

### 📘 Multiple-Choice (Factual Recall – Number of Correct Answers)

| Rank | EN                                  | KR                                 |
|------|-------------------------------------|-------------------------------------|
| 1    | gemini-2.5-pro-preview (31)         | claude-opus (31)                   |
| 2    | claude-opus (30)                    | gemini-2.5-pro-preview (31)        |
| 3    | gemini1.5pro (30)                   | gpt4turbo-0409 (30)                |
| 4    | gpt4turbo-0409 (30)                 | gpt-4.5-preview (29)               |
| 5    | gpt-4o (30)                         | gpt-4o (29)                         |

---

### 🎯 Trap (Cultural Advice – Weighted Sum)

| Rank | EN (Neutral)                    | EN (Specified)                    | KR (Neutral)                    | KR (Specified)                   |
|------|----------------------------------|-----------------------------------|----------------------------------|----------------------------------|
| 1    | gemini-2.5-pro-preview (78.0)   | gemini-2.5-pro-preview (155.0)   | gemini-2.5-pro-preview (121.0)  | gemini-2.5-pro-preview (149.0)   |
| 2    | gpt-4.5-preview (51.0)          | gpt-4.5-preview (133.0)          | claude-opus (105.0)             | claude-opus (132.0)              |
| 3    | deepseek-chat (48.0)            | claude-opus (116.0)              | gpt-4.5-preview (98.0)          | gpt-4.5-preview (125.0)          |
| 4    | claude-opus (44.0)              | gpt-4o (115.0)                   | gpt-4o (75.0)                   | deepseek-chat (104.0)            |
| 5    | gpt-4o (38.0)                   | deepseek-chat (113.0)            | deepseek-chat (73.0)            | gpt-4o (100.0)                   |

---

### 🧠 Interpretation (Context Interpretation – Weighted Sum)

| Rank | EN (Neutral)                    | EN (Specified)                    | KR (Neutral)                    | KR (Specified)                   |
|------|----------------------------------|-----------------------------------|----------------------------------|----------------------------------|
| 1    | gemini-2.5-pro-preview (148.0)  | gemini-2.5-pro-preview (236.0)   | gemini-2.5-pro-preview (232.0)  | gemini-2.5-pro-preview (246.0)   |
| 2    | claude-opus (145.0)             | gpt-4.5-preview (235.0)          | claude-opus (209.0)             | gpt-4.5-preview (237.0)          |
| 3    | gpt-4.5-preview (144.0)         | claude-opus (223.0)              | gpt-4.5-preview (204.0)         | claude-opus (234.0)              |
| 4    | deepseek-chat (140.0)           | deepseek-chat (217.0)            | deepseek-chat (172.0)           | gpt-4o (208.0)                   |
| 5    | gpt-4o (112.0)                  | gpt4turbo-0409 (209.0)           | gpt-4o (168.0)                  | deepseek-chat (200.0)           |

---

## 📁 Repository Structure

```

NUNCHI-BENCH/
├── data/                           # Benchmark data
│   ├── nunchi\_mcq.csv
│   ├── nunchi\_trap.csv
│   └── nunchi\_interpret.csv
│
├── evaluation/                    # Scoring scripts
│   ├── llm\_evaluator.py
│   └── mcqa\_evaluator.py
│
├── scripts/                       # Model generation scripts
│   ├── generate\_claude.py
│   ├── generate\_deepseek.py
│   ├── generate\_gemini.py
│   └── generate\_gpt.py
│
├── results/                       # Output + scores
│   ├── model\_outputs/
│   │   ├── interpret/
│   │   │   ├── eng\_default/
│   │   │   ├── eng\_kor/
│   │   │   ├── kor\_default/
│   │   │   └── kor\_kor/
│   │   ├── mcq/
│   │   └── trap/
├── prompts/                       # Prompt templates
├── environment.yml                # Conda environment
├── .gitignore
└── README.md

````
### 📖 Citation

If you use **Nunchi-Bench** in your work, please cite the arXiv version:

```bibtex
@misc{kim2025nunchibenchbenchmarkinglanguagemodels,
  title={Nunchi-Bench: Benchmarking Language Models on Cultural Reasoning with a Focus on Korean Superstition}, 
  author={Kyuhee Kim and Sangah Lee},
  year={2025},
  eprint={2507.04014},
  archivePrefix={arXiv},
  primaryClass={cs.CL},
  url={https://arxiv.org/abs/2507.04014}
}
```

---

## 📬 Contact

For questions or contributions, feel free to reach out via [GitHub Issues](https://github.com/your-repo/issues) or email.

---
