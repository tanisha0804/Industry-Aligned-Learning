# Industry-Aligned-Learning

A personalized learning recommendation system that aligns **student skills**, **academic courses**, and **industry job market demands** using NLP, skill ontology mapping, and adaptive Bayesian learning.

This project aims to help students identify skill gaps relative to industry expectations and receive explainable, adaptive course recommendations that evolve with learner feedback.

---

## 🎯 Problem Statement

Traditional academic course recommendation systems focus primarily on:
- Student interests
- Historical course enrollments
- Static curricula

However, they often **fail to account for real-time industry skill demand** and **do not adapt dynamically to learner feedback**.

This project bridges that gap by:
- Extracting skills from student resumes
- Modeling industry-required skills from job descriptions
- Performing skill gap analysis
- Recommending academic courses to bridge these gaps
- Adapting recommendations based on learner feedback using Bayesian updating

---

## 🧠 Core Contributions

- **Industry-aligned personalization** using job descriptions
- **Skill ontology normalization** for consistent skill representation
- **Time-aware industry skill weighting** (Extension A)
- **Skill gap analysis with explainability** (Extension B)
- **Human-in-the-loop adaptive learning** using Bayesian belief updates
- **University-deployable system architecture**

---

## 🏗️ System Architecture

The system consists of:
- **Backend**: Python + FastAPI (NLP, skill modeling, recommendations)
- **Frontend**: Next.js + Tailwind CSS (planned)
- **Data Sources**:
  - Student resumes
  - Industry job descriptions
  - University course catalogs

High-level diagrams are available in the `docs/` folder.

---
