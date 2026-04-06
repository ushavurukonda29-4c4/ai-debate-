import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from textblob import TextBlob
import speech_recognition as sr
from pydub import AudioSegment
import tempfile
import os

st.title("🎤 AI Debate Evaluator")

# --- FUNCTIONS ---

def analyze_text(text):
    blob = TextBlob(text)
    sentiment = blob.sentiment.polarity
    length = len(text.split())

    # simple keyword scoring
    strong_words = ["evidence", "data", "proof", "logic", "fact"]
    keyword_score = sum(word in text.lower() for word in strong_words)

    score = (sentiment * 2) + (length / 50) + (keyword_score * 2)

    return {
        "Sentiment": sentiment,
        "Length": length,
        "Keyword Score": keyword_score,
        "Final Score": score
    }

def audio_to_text(audio_file):
    recognizer = sr.Recognizer()

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
        audio = AudioSegment.from_file(audio_file)
        audio.export(tmp.name, format="wav")

        with sr.AudioFile(tmp.name) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data)

    os.remove(tmp.name)
    return text

# --- INPUT MODE ---

mode = st.radio("Choose Input Type:", ["Text", "Audio"])

debater1 = ""
debater2 = ""

if mode == "Text":
    debater1 = st.text_area("Debater 1 Argument")
    debater2 = st.text_area("Debater 2 Argument")

elif mode == "Audio":
    audio1 = st.file_uploader("Upload Debater 1 Audio", type=["wav", "mp3"])
    audio2 = st.file_uploader("Upload Debater 2 Audio", type=["wav", "mp3"])

    if audio1:
        debater1 = audio_to_text(audio1)
        st.write("Debater 1 Transcription:", debater1)

    if audio2:
        debater2 = audio_to_text(audio2)
        st.write("Debater 2 Transcription:", debater2)

# --- ANALYSIS ---

if st.button("Evaluate Debate"):
    if debater1 and debater2:
        result1 = analyze_text(debater1)
        result2 = analyze_text(debater2)

        df = pd.DataFrame([result1, result2], index=["Debater 1", "Debater 2"])
        st.subheader("📊 Scores Table")
        st.dataframe(df)

        # --- Plot ---
        st.subheader("📈 Score Comparison")
        fig, ax = plt.subplots()
        df["Final Score"].plot(kind="bar", ax=ax)
        ax.set_ylabel("Score")
        ax.set_title("Debate Evaluation")
        st.pyplot(fig)

        # --- Winner ---
        winner = "Debater 1" if result1["Final Score"] > result2["Final Score"] else "Debater 2"
        st.success(f"🏆 Winner: {winner}")