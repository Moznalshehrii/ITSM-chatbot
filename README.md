# 💡 Smart IT Helpdesk Retriever

Employees often spend too much time fixing small IT problems — printers not working, VPN disconnecting, Outlook crashing.  
They open tickets, wait for help, and repeat the same steps that others have already solved.  

This project shows how AI can make that process faster and smarter.

---

## 🎯 What It Does

The **Smart IT Helpdesk Retriever** understands what a user means when describing a problem and instantly finds the most relevant solution from a knowledge base.

It:
1. Reads the user’s issue written in plain language.  
2. Uses **Gemini AI** to generate a short, clear title.  
3. Searches the stored articles using **FAISS** similarity search.  
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

1. 🗣 **Input**: The user writes a problem (e.g., “My VPN keeps disconnecting”).  
2. ✍️ **Gemini AI**: Summarizes it into a short title (“Reset VPN Connection on Windows 11”).  
3. 🔎 **FAISS Search**: Finds the most similar record from the knowledge base.  
4. 💬 **Output**: Returns the fix text with a similarity score.  

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
pip install numpy pandas faiss-cpu python-dotenv google-genai
GOOGLE_API_KEY=your_key_here
from your_module import load_dataset, build_index, get_fix

df = load_dataset("ServiceNow_KB_Dummy_Articles_150.xlsx")
index, _ = build_index(df)

result = get_fix("My Outlook keeps crashing after update", df, index)
print(result["title"])
print(result["fix"])
title: Reset Outlook After Update
fix: Go to Control Panel > Programs > Repair Microsoft Office, then restart your device.


