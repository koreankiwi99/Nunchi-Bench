<div align="center">
  <h1>Nunchi-Bench 😬</h1>
  <p><strong>Nunchi-Bench</strong>: Benchmarking Language Models on Cultural Reasoning with a Focus on Korean Superstition</p>
  <p>
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


---

## 📬 Contact

For questions or contributions, feel free to reach out via [GitHub Issues](https://github.com/your-repo/issues) or email.

---
