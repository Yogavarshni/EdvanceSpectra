# 📚 Sahayak-Edusphere: A One-Stop Multimodal Assistant for Multi-Grade Classrooms

Welcome to **Sahayak-Edusphere**, a unified solution designed to support teachers managing **multiple grades** within a single classroom. Powered entirely by **Google technologies**, Sahayak delivers a seamless experience by combining backend AI orchestration with an intuitive frontend built for real-world educational needs.

---

## 🧱 Architecture Overview

> The system is architected using Google's full technology stack:

- **Backend AI Orchestration**: Built using [Google ADK](https://cloud.google.com/agents/docs/adk) (Agent Developer Kit), handling multimodal and multi-agent LLM workflows.
- **Frontend UI**: Developed with [Firebase Studio](https://firebase.google.com/products/extensions/studio), offering a clean and interactive interface.
- **Deployment**: Hosted on **Google Cloud Run**, enabling scalable serverless deployment.
- **Data Storage**: Utilizes **Firebase Firestore** for storing persistent user data and configurations.

🖼️ *Refer to the architecture diagram included in the project for a detailed technical flow.*

---

## 🌐 Live App Link

> 🎯 [Click here to explore the live app] https://studio--edsphere-ai.us-central1.hosted.app  

---

## 🚀 Features

### 1. 🗣️ Language Preference
- Users can set their **preferred language**.
- Input is accepted via **text or audio**.

### 2. 💬 General Chatbot (Powered by Orchestration Agent)
- Teachers can ask **general queries**.
- Prompts are routed to a **central orchestration agent** backed by Google ADK.

### 3. 🧩 Features Page (No Prompt Engineering Needed)
- A user-friendly page showcasing available features.
- Teachers can simply **click buttons** or provide **keywords**.
- These are internally passed to a **Rephraser LLM**, which generates a clean prompt and sends it to the orchestration agent.

### 4. 📦 Modular Agents (in progress and future development)
- `✅ Material Generator`: Generates teaching materials (beta – functionality present but refining underway).
- `🚧 Class Performance Agent`: Under development.
- `🚧 Video Generation Agent`: Under development.

---

## 🛠 Deployment Overview

- Backend deployed on Google Cloud Run using gcloud CLI
- Complete integration and UI built with Firebase Studio
- Frontend–Backend connection via Firebase Studio's inbuilt endpoint management

