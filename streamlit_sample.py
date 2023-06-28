import streamlit as st
from gtts import gTTS
import os


st.sidebar.header('Input')

def t2s(text, lang, slow_audio_speed):
    speech = gTTS(text = text, lang = lang, slow = slow_audio_speed)
    speech.save("t2s.mp3")
    return "t2s.mp3"

def main():
    st.title('Google Text 2 Speech')
    text = st.text_input("Enter somthing", "Type Here ...")
    lang = st.selectbox("Select Language", ['en', 'jp', 'hi', 'gu', 'mr'])
    slow_audio_speed = st.checkbox("Slow Audio Speed")

    if st.button("Convert"):
        audio_file = t2s(text, lang, slow_audio_speed)
        st.audio(audio_file, format = 'audio/mp3')

if __name__ == "__main__":
    main()