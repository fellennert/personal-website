# Script for Creating the ML Classifiers Blog Post

This document is a step-by-step guide for producing an informative portfolio piece (blog post or project page) on the training and comparison of ML classifiers for sentiment analysis of IMDb movie reviews.

---

## 1. Purpose and Audience

**Goal:** Turn the narrative and results from the Computational Social Science course materials into a concise, accessible portfolio piece.

**Audience:** Visitors to your portfolio—researchers, practitioners, or students interested in text classification, NLP pipelines, and the trade-offs between different ML approaches.

**Tone:** Informative and concise. Emphasize findings and practical insights over pedagogical detail. Show what you built and what you learned.

---

## 2. Core Narrative Arc

The blog post should follow this arc:

1. **Hook:** Graduate teaching context—supervised classification of text for Computational Social Science students.
2. **Problem:** Demonstrate how capable different approaches are (dictionary-based → bag-of-words → BERT → LLM prompting) on a real task.
3. **Data:** Pre-labeled Kaggle IMDb movie reviews (sentiment: positive/negative).
4. **Methods:** Four (or more) classifier families with distinct paradigms.
5. **Findings:** Impact of preprocessing, effect of training set size (500 pieces for trained models), and performance vs. runtime trade-offs.
6. **Takeaways:** When to use which approach and what preprocessing choices matter.

---

## 3. Required Technical Specifications

From the INSTRUCTIONS, ensure the following:

| Requirement | Implementation |
|-------------|----------------|
| Data | `imdb-reviews.csv` (Kaggle IMDb reviews) |
| Training set size | 500 examples for all trained models (dictionary-based, bag-of-words, BERT) |
| Zero-shot | GPT/LLM approach uses zero examples (prompt-only) |
| Evaluation metrics | Accuracy, Recall, Precision, F1 Score |
| Comparison | Runtime per classifier in addition to performance metrics |
| Output format | Quarto table summarizing metrics and runtimes |
| Code execution | Published piece must contain pre-computed results (no live code execution) |

---

## 4. Section-by-Section Content Guide

### 4.1 Introduction (2–3 paragraphs)

- **Source:** INSTRUCTIONS.md summary, project_backlog.md blurb
- **Content to include:**
  - Teaching context (graduate CSS course on supervised text classification)
  - Approaches covered: dictionary-based, bag-of-words models, BERT, and LLM prompting
  - Objective: train and compare classifiers on IMDb reviews to show relative capability
  - Emphasis: impact of preprocessing and number of training examples

### 4.2 Data

- **Source:** 14_supervised_ml.qmd
- **Content to include:**
  - IMDb movie reviews, pre-labeled with sentiment (positive/negative)
  - Origin: Kaggle data set
  - Brief description of preprocessing applied (tokenization, stop words, stemming/lemmatization, TF-IDF where relevant)

### 4.3 Preprocessing Choices and Their Effect

- **Sources:** 12_text-preprocessing.qmd, 13_dictionary-based-analysis.qmd, 14_supervised_ml.qmd
- **Content to include:**
  - Tokenization (e.g., `unnest_tokens` / `step_tokenize`)
  - Stop word removal
  - Stemming vs. lemmatization (where applicable)
  - Token filtering (min/max frequency, max tokens)
  - TF vs. TF-IDF for bag-of-words
  - How these choices affected performance (highlight with short comparisons or notes)

### 4.4 Classifiers Compared

For each approach, provide: (1) brief description, (2) training setup, (3) key hyperparameters or choices.

| Classifier | Source File | Key Points |
|------------|-------------|------------|
| Dictionary-based | 13_dictionary-based-analysis.qmd | Lexicon matching (e.g., AFINN, Bing); no training; sensitive to preprocessing (stemming for AFINN) |
| Bag-of-words (e.g., penalized logistic, SVM, Naive Bayes, RF, XGBoost) | 14_supervised_ml.qmd | `tidymodels`, `textrecipes`; 500 train examples; token filtering, TF-IDF |
| BERT | 17_BERT.qmd | Fine-tuned BERT; 500 train examples; PyTorch/transformers; context-aware embeddings |
| LLM (GPT via Ollama) | 18_GPT.qmd | Zero-shot prompting; no training; local via Ollama; Qwen or similar model |

### 4.5 Results: Performance and Runtime

- **Format:** Quarto table(s)
- **Columns:** Classifier | Accuracy | Precision | Recall | F1 Score | Runtime
- **Content:** Pre-computed values from running the full pipeline. No live execution in the published post.
- **Visuals (optional):** Bar chart or small multiples comparing metrics; runtime comparison chart.

### 4.6 Discussion

- **Content to include:**
  - Trade-offs: accuracy vs. runtime, training data requirements vs. zero-shot capability
  - When to prefer each approach (e.g., BERT for large labeled data; LLM prompting for few labels and complex categories)
  - Lessons on preprocessing (which choices helped, which hurt)
  - Limitations (IMDb domain, binary sentiment, single run vs. repeated runs)

### 4.7 Conclusion

- Short recap of main findings
- Link to code or project files if applicable

---

## 5. Informative Blurb (for projects.qmd)

The blurb should be 2–4 sentences suitable for a project listing. Current draft from project_backlog.md:

> One topic of a graduate class I taught on Computational Social Science was supervised classification of text. I showed the students different approaches for doing this (simple, dictionary-based; more advanced, using bag-of-words-based models; and advanced, using BERT). To show the students how capable these different models are, I decided to train and compare several machine learning classifiers. Due to time constraints, I resorted to a pre-labeled data set that was available on Kaggle, containing IMDb reviews of movies. Here's a little report on my results, with an emphasis on the impact of preprocessing and the number of training examples.

**Refinement suggestions:** Add mention of LLM prompting (Ollama) for completeness. Optionally add one line on the key takeaway (e.g., "The comparison highlights trade-offs between simplicity, speed, and accuracy.")

---

## 6. Implementation Checklist

- [ ] Repurpose code from 12_*.qmd through 18_*.qmd into Python and R scripts
- [ ] Use `imdb-reviews.csv` as data source
- [ ] Train all classifiers with 500 training examples (except GPT, zero-shot)
- [ ] Run full pipeline; record runtime per classifier
- [ ] Compute Accuracy, Precision, Recall, F1 for each classifier
- [ ] Create Quarto table(s) with metrics and runtimes
- [ ] Write narrative sections following the structure above
- [ ] Freeze output (no code execution in published piece)
- [ ] Save final piece as `projects/ml_classifiers.qmd`
- [ ] Link from `projects.qmd` with informative blurb
- [ ] Include `figures/workflow.png` if relevant (from 14_supervised_ml.qmd)

---

## 7. File References

| File | Content |
|-----|---------|
| 12_text-preprocessing.qmd | Preprocessing pipeline (tokenization, stop words, stemming, lemmatization) |
| 13_dictionary-based-analysis.qmd | Dictionary-based sentiment (AFINN, Bing, etc.) |
| 14_supervised_ml.qmd | Bag-of-words classifiers, tidymodels workflow, IMDb example |
| 17_BERT.qmd | BERT fine-tuning for sentiment |
| 18_GPT.qmd | LLM prompting with Ollama (zero-shot) |
| figures/workflow.png | Workflow diagram |
| literature.bib, ASA.csl | Citations and style |

---

## 8. Suggested Quarto YAML (projects/ml_classifiers.qmd)

```yaml
---
title: "Training and Comparing ML Classifiers on IMDb Reviews"
author: "Felix Lennert"
date: today
format:
  html:
    code-fold: true
    code-summary: "Show code"
    toc: true
    theme: cosmo
jupyter: [appropriate env if using Python]
freeze: true
---
```

Adjust `jupyter` and `theme` to match your site’s conventions.
