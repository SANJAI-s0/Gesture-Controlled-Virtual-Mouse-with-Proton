# ---------------- Base Image ----------------
FROM python:3.8-slim

# ---------------- Environment ----------------
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# ---------------- System Dependencies ----------------
RUN apt-get update && apt-get install -y \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    portaudio19-dev \
    libsndfile1 \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

# ---------------- Working Directory ----------------
WORKDIR /app

# ---------------- Copy Project ----------------
COPY . /app

# ---------------- Python Dependencies ----------------
RUN pip install --upgrade pip && \
    pip install \
        mediapipe==0.10.11 \
        opencv-python==4.5.3.56 \
        pyttsx3==2.71 \
        SpeechRecognition==3.8.1 \
        pynput==1.7.3 \
        pyautogui==0.9.53 \
        wikipedia==1.4.0 \
        comtypes==1.1.11 \
        pycaw==20181226 \
        screen-brightness-control==0.9.0 \
        eel==0.14.0 \
        gevent==21.12.0 \
        gevent-websocket==0.10.1 \
        pyaudio==0.2.11

# ---------------- Default Command ----------------
CMD ["python", "src/Proton.py"]
