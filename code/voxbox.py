import pandas as pd
import ast
import numpy as np
from sentence_transformers import SentenceTransformer
from numpy import dot
from numpy.linalg import norm

from phi.agent import Agent
from phi.model.google import Gemini

import tkinter as tk
from tkinter import scrolledtext, PhotoImage
from PIL import Image, ImageTk

import torch
import re
import requests
from bs4 import BeautifulSoup
import csv
import json
import os
import webbrowser

# ✅ Removed legacy inspect.getargspec patch
# ✅ Removed torch.get_default_device override — modern torch handles device selection

HISTORY_FILE = "chat_history.json"
MAX_HISTORY = 10  # keep last 10 exchanges (user+assistant)

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_history(history):
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def format_prompt(history, query):
    base_intro = "The following is a conversation between a helpful assistant and a user.\n"
    convo = ""
    for turn in history[-MAX_HISTORY:]:
        convo += f"User: {turn['user']}\nAssistant: {turn['bot']}\n"
    convo += f"User: {query}\nAssistant:"
    return base_intro + convo

# Sentence Transformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Load embeddings CSV
try:
    df = pd.read_csv("voxcinemas_with_embeddings.csv")
    df['embedding'] = df['embedding'].apply(ast.literal_eval)
except Exception as e:
    print("❌ Failed to load embeddings CSV:", e)
    df = pd.DataFrame()

def cosine_similarity(a, b):
    return dot(a, b) / (norm(a) * norm(b))

def get_all_chunks_sorted(query, df):
    query_vec = model.encode(query, normalize_embeddings=True)
    df['similarity'] = df['embedding'].apply(lambda x: cosine_similarity(query_vec, np.array(x)))
    sorted_chunks = df.sort_values(by='similarity', ascending=False)

    deduped_chunks = []
    seen_links = set()
    for chunk in sorted_chunks['chunk'].tolist():
        links = re.findall(r'https?://[^\s\],]+', chunk)
        if any(link in seen_links for link in links):
            continue
        seen_links.update(links)
        deduped_chunks.append(chunk)

    return deduped_chunks

movie_lines = """
🎬 Final Destination: Bloodlines (18+, English)
• Showtime 1: [Book Now](https://uae.voxcinemas.com/booking/0055-148214)
• Showtime 2: [Book Now](https://uae.voxcinemas.com/booking/0055-148163)

🎬 Karate Kid: Legends (PG, English)
• Showtime 1: [Book Now](https://uae.voxcinemas.com/booking/0055-148211)
• Showtime 2: [Book Now](https://uae.voxcinemas.com/booking/0055-148161)

🎬 Lilo & Stitch (PG, English)
• Showtime 1: [Book Now](https://uae.voxcinemas.com/booking/0055-147738)
• Showtime 2: [Book Now](https://uae.voxcinemas.com/booking/0055-147114)
• Showtime 3: [Book Now](https://uae.voxcinemas.com/booking/0055-148152)
• Showtime 4: [Book Now](https://uae.voxcinemas.com/booking/0055-148020)
"""

agent = Agent(
    model=Gemini(id="gemini-1.5-flash"),
    description="You are a professional and friendly movie theatre assistant chatbot for VOX Cinemas located in UAE.",
    instructions=[
        "You assist users with information about VOX Cinemas, including movies, showtimes, ticket prices, and locations.",
        "You give output in proper layout where there is only one sentence per line",
        "You help users book tickets or guide them on how to book via the official VOX Cinemas website or app.",
        "You can suggest movies based on genre preferences, popularity, or current showings.",
        "You provide details about cinema services such as Gold Class, IMAX, 4DX, or Kids' theatres.",
        "You do not give unrelated information. Give instructions for detailed bookings.",
        "If asked something outside your scope, politely inform the user and suggest creative solutions.",
        "You have to help no matter what using existing information about VOX Cinemas, UAE.",
        "Use the following live movie data to answer all questions about current movies, their languages, and booking links. Do NOT mention that you don't have live data.",
        "If the user asks what movies are playing right now or similar, list the movies from the data below:",
        "dont display the same link twice during booking",
        "show the output following this format:",
        movie_lines
    ],
    markdown=True,
)

chat_history = load_history()

class VOXApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🎬 VOX Cinemas Assistant")
        self.geometry("750x650")
        self.configure(bg="#1e1e2f")

        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)

        self.frames = {}
        for F in (StartPage, ChatPage):
            frame = F(parent=self.container, controller=self)
            self.frames[F.__name__] = frame
            frame.place(relwidth=1, relheight=1)

        self.show_frame("StartPage")

    def show_frame(self, page_name):
        self.frames[page_name].tkraise()

class StartPage(tk.Frame):
    # Exactly your code —
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#1e1e2f")
        self.controller = controller
        logo_img = Image.open("LOGO2.png").resize((500,500))
        self.logo = ImageTk.PhotoImage(logo_img)
        tk.Label(self, image=self.logo, bg="#1e1e2f").pack(pady=60)
        tk.Button(
            self, text="Start", font=("Segoe UI",14,"bold"),
            bg="#5865F2", fg="white", activebackground="#4752c4", 
            activeforeground="white", padx=20, pady=10,
            relief=tk.FLAT, cursor="hand2",
            command=lambda: controller.show_frame("ChatPage")
        ).pack()

class ChatPage(tk.Frame):
    def __init__(self, parent, controller):
        logo_img = Image.open("bot_logo.png").convert("RGBA").resize((50,50), Image.Resampling.LANCZOS)
        self.bot_logo_imgtk = ImageTk.PhotoImage(logo_img)
        super().__init__(parent, bg="#2c2f4a")
        self.controller = controller
        global chat_history

        main_frame = tk.Frame(self, bg="#2c2f4a", padx=15, pady=15)
        main_frame.pack(fill=tk.BOTH, expand=True)
        chat_frame = tk.Frame(main_frame, bg="#2c2f4a")
        chat_frame.pack(fill=tk.BOTH, expand=True)

        self.chat_display = scrolledtext.ScrolledText(
            chat_frame, wrap=tk.WORD, font=("Segoe UI",12),
            bg="#1e1e2f", fg="#e0e0e0", bd=0, relief=tk.FLAT, insertbackground="#ffffff"
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        self.chat_display.config(state='disabled')
        self.chat_display.tag_config("user_tag", foreground="#5865F2", font=("Segoe UI",13,"bold"))
        self.chat_display.tag_config("bot_tag", foreground="#43d9ad", font=("Segoe UI",13,"bold"))
        self.chat_display.tag_config("user_msg", foreground="white", font=("Segoe UI",12))
        self.chat_display.tag_config("bot_msg", foreground="#d1d1d1", font=("Segoe UI",12))

        input_frame = tk.Frame(main_frame, bg="#2c2f4a", pady=10)
        input_frame.pack(fill=tk.X)
        self.user_input_var = tk.StringVar()
        self.user_entry = tk.Entry(
            input_frame, textvariable=self.user_input_var,
            font=("Segoe UI",12), bg="#1e1e2f", fg="#888", insertbackground='white',
            relief=tk.FLAT
        )
        self.user_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,10), ipady=8)
        self.user_entry.insert(0, "Type your message here...")
        self.user_entry.bind('<FocusIn>', self.on_entry_click)
        self.user_entry.bind('<FocusOut>', self.on_focus_out)
        self.user_entry.bind('<Return>', lambda e: self.on_send())

        tk.Button(
            input_frame, text="Send", font=("Segoe UI Semibold",13),
            bg="#5865F2", fg="white", activebackground="#4752c4",
            activeforeground="white", relief=tk.FLAT,
            padx=15, pady=7, cursor="hand2", command=self.on_send
        ).pack(side=tk.RIGHT)

        self.add_message("VOXBOT", "👋 Welcome to VOX Cinemas Assistant Bot!\nAsk me anything about movies, showtimes, or bookings.")

    def on_entry_click(self, event):
        if self.user_entry.get() == "Type your message here...":
            self.user_entry.delete(0, tk.END)
            self.user_entry.config(fg="white")

    def on_focus_out(self, event):
        if self.user_entry.get() == "":
            self.user_entry.insert(0, "Type your message here...")
            self.user_entry.config(fg="#888")

    def add_message(self, sender, message):
        self.chat_display.config(state='normal')
        if sender == "You":
            self.chat_display.insert(tk.END, f"{sender}:\n", "user_tag")
            self.chat_display.insert(tk.END, f"{message}\n\n", "user_msg")
        else:
            self.chat_display.image_create(tk.END, image=self.bot_logo_imgtk)
            self.chat_display.insert(tk.END, " ",)
            self.chat_display.insert(tk.END, "\n", "bot_tag")
            words = message.split()
            for word in words:
                if re.match(r'https?://\S+', word):
                    tag = f"link_{word}"
                    self.chat_display.insert(tk.END, word, (tag, "bot_msg"))
                    self.chat_display.insert(tk.END, " ", "bot_msg")
                    self.chat_display.tag_config(tag, foreground="#1E90FF", underline=True)
                    self.chat_display.tag_bind(tag, "<Button-1>", lambda e, url=word: webbrowser.open_new(url))
                else:
                    self.chat_display.insert(tk.END, word + " ", "bot_msg")
            self.chat_display.insert(tk.END, "\n\n")
        self.chat_display.config(state='disabled')
        self.chat_display.see(tk.END)

    def on_send(self):
        global chat_history
        query = self.user_input_var.get().strip()
        if not query or query == "Type your message here...":
            return

        self.add_message("You", query)
        self.user_input_var.set("")
        self.add_message("VOXBOT", "тнїпкїпg...")
        self.update_idletasks()

        try:
            relevant = get_all_chunks_sorted(query, df)
            context_text = "\n\n".join(relevant[:5])

            prompt = format_prompt(chat_history, query) + f"""

Use the VOX Cinemas UAE movie data below to answer accurately:

{context_text}

Answer:
"""
            response = agent.run(prompt).content.strip()
            answer = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'\1: \2', response)

            self.chat_display.config(state='normal')
            self.chat_display.delete("end-4l linestart", "end-1c")
            self.chat_display.config(state='disabled')

            self.add_message("VOXBOT", answer)

            chat_history.append({"user": query, "bot": answer})
            if len(chat_history) > MAX_HISTORY:
                chat_history = chat_history[-MAX_HISTORY:]
            save_history(chat_history)

        except Exception as e:
            self.add_message("VOXBOT", f"⚠️ Error: {e}")

if __name__ == "__main__":
    app = VOXApp()
    app.mainloop()
