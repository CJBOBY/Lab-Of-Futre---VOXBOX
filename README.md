🎬 VOX Cinemas Assistant Chatbot
A smart, conversational AI chatbot for VOX Cinemas UAE that provides real-time movie showtimes, booking links, cast, and genre information using live web scraping, TMDb API, and Google’s Gemini model.

Built with Python, Tkinter GUI, semantic search, and Gemini-powered language understanding.

📌 Table of Contents
🔍 Overview

✨ Features

🧠 How It Works

🖥️ GUI Preview

🚀 Installation

🛠️ Tech Stack

📈 Results

🔮 Future Work

📚 References

🔍 Overview
This project presents an intelligent chatbot designed for VOX Cinemas UAE, capable of providing:

🎟️ Movie showtimes

📅 Booking links

🎥 Cast & genre information

💬 Natural conversational responses

The chatbot uses live web scraping (BeautifulSoup) to extract real-time data from the VOX Cinemas website, and enriches movie details with the TMDb API. It uses sentence embeddings and cosine similarity for semantic search and is powered by Google’s Gemini model via the google-generativeai SDK.

✨ Features
🔎 Real-time movie listings via web scraping

🎭 Movie details including cast and genre (from TMDb)

🧠 Semantic search using Sentence Transformers

💬 Conversational chatbot powered by Gemini

🖥️ Custom GUI built with Python and Tkinter

💾 Local chat history persistence

📎 Clickable booking links

🧠 How It Works
🕸️ 1. Web Scraping (VOX Site)
Extracts movie titles, showtimes, and links using BeautifulSoup

Regularly updates data for accurate results

🧠 2. Chunking & Embedding
Text from scraped data is chunked and embedded using SentenceTransformer

Embeddings are saved and reused for fast semantic search

🔍 3. Semantic Search
User queries are embedded and matched to relevant chunks

Cosine similarity is used to return the most relevant information

💬 4. Gemini Prompt Generation
Instructions + top context chunks + chat history = final prompt

Gemini generates context-aware natural language replies

🖥️ 5. GUI (Tkinter)
Start screen + chat interface with styled conversation flow

Clickable movie booking links

🖥️ GUI Preview
(Add a screenshot here)
Example: chatbot_home.png and chatbot_conversation.png

🚀 Installation
🔧 1. Clone the repository
bash
Copy
Edit
git clone https://github.com/yourusername/vox-cinemas-chatbot.git
cd vox-cinemas-chatbot
📦 2. Install dependencies
bash
Copy
Edit
pip install -r requirements.txt
🔑 3. Set your Gemini API Key
Option 1: In your environment

bash
Copy
Edit
export GOOGLE_API_KEY="your-key"      # macOS/Linux
set GOOGLE_API_KEY=your-key           # Windows
Option 2: Inside voxbox.py

python
Copy
Edit
import os
os.environ["GOOGLE_API_KEY"] = "your-key"
▶️ 4. Run the application
bash
Copy
Edit
python voxbox.py
🛠️ Tech Stack
Component	Technology
Language Model	Google Gemini 1.5 Flash
Embedding Model	SentenceTransformer
GUI	Tkinter (Python)
Web Scraping	BeautifulSoup, requests
Movie Metadata	TMDb API
AI Integration	google-generativeai SDK
Language	Python 3.x

📈 Results
🎯 High relevance in responses via cosine similarity matching

🧠 Gemini produces fluent and context-aware replies

✅ Real-time showtimes and booking links work reliably

👥 Tested with diverse movie-related user queries

🔮 Future Work
🌐 Web version using Flask or Streamlit

📱 Convert into a mobile app using Flutter

🗣️ Voice input and text-to-speech

🈂️ Add multilingual support

💳 Integrate real ticket booking via VOX APIs (if available)

📚 References
VOX Cinemas UAE

TMDb API Docs

Beautiful Soup Docs

Google Gemini AI

Sentence Transformers

Google Generative AI SDK

👨‍💻 Authors
Cyriac James Boby

Dev Sebastian Joseph

Dana Shein Rebello

🔬 Lab of Future, Rajagiri School of Engineering and Technology
