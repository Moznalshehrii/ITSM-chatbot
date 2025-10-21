# 💡 Smart IT Helpdesk Retriever

Employees often spend too much time fixing small IT problems — printers not working, VPN disconnecting, Outlook crashing.  
They open tickets, wait for help, and repeat the same steps that others have already solved.  

This project shows how AI can make that process faster and smarter.

---

## 🎯 What It Does

The **Smart IT Helpdesk Retriever** understands what a user means when describing a problem and instantly finds the most relevant solution from a knowledge base.

It:
1. Reads the user’s issue written in plain language.  
2. Uses an **LLM** to generate a short, clear title that summarizes the issue.
3. Applies a **RAG (Retrieval-Augmented Generation)** approach that compares meaning using cosine similarity to retrieve the most relevant knowledge base articles. 
4. Returns the most relevant fix — or a helpful fallback if no match is strong enough.  

It’s a **proof of concept** that demonstrates a smarter way to access IT knowledge.

---

## 🔍 The Problem

In most organizations, support teams handle thousands of similar tickets.  
Different users describe the same issue in different ways, making keyword searches unreliable.  

This leads to:
- Repeated tickets  
- Delays in response  
- Underused knowledge bases  

The challenge is not the lack of answers — it’s finding them quickly.

---

## 💡 The Solution

This project builds an AI-powered retriever that:
- Understands meaning instead of relying on keywords.  
- Matches issues to their closest solutions.  
- Delivers instant responses that users can act on immediately.  

It’s small, clear, and built to show what’s possible when language understanding meets IT support.

---

## 🧾 Dataset

The project uses a **dummy dataset** called `ServiceNow_KB_Dummy_Articles_150.xlsx`.  
It includes about **150 sample IT issues and fixes** — artificial examples of real workplace problems like VPN errors, login issues, and software setup guides.  

This dataset is not real production data.  
It’s only used to **prove the concept** and validate how Gemini and FAISS work together.

---

## ⚙️ How It Works (Simplified)

1. 🗣 **Input**: The user describes an IT issue in plain language  
   *(for example: “My VPN keeps disconnecting.”)*  

2. ✍️ **LLM Processing**: The system uses a language model to generate a short, clear title that captures the main intent  
   *(e.g., “Reset VPN Connection on Windows 11”)*  

3. 🔎 **RAG Retrieval**: The title is embedded and compared to existing knowledge base entries using **cosine similarity** to find the most semantically related results.  

4. 💬 **Output**: The system returns the best-matched fix, along with a confidence score or a fallback message if no strong match is found.  

---

## 🧰 Tech Overview

**Core components**
- Gemini 2.5 Flash – for understanding and summarizing text  
- text-embedding-004 – for semantic embeddings  
- FAISS – for similarity search  
- Pandas & NumPy – for data handling  
- dotenv – for API key management  

The code runs locally with minimal setup and can easily be adapted for testing or integration.

---

## 🚀 Quick Start

Install dependencies:
```bash
pip install -r requirements.txt
```
Create a .env file with your Google API key:
```
GOOGLE_API_KEY=your_key_here
```
Run the example:
```
from your_module import load_dataset, build_index, get_fix

df = load_dataset("ServiceNow_KB_Dummy_Articles_150.xlsx")
index, _ = build_index(df)

result = get_fix("My Outlook keeps crashing after update", df, index)
print(result["title"])
print(result["fix"])
```
Example output:
```
title: Reset Outlook After Update
fix: Go to Control Panel > Programs > Repair Microsoft Office, then restart your device. 
```
---
## 🌱 The Goal

This project isn’t about automation for its own sake.
It’s about helping people solve problems faster — by understanding their language and connecting them with the right knowledge.

It shows how even a small, focused AI tool can reduce repetitive work and make IT self-service more human.
