# System Architecture

This document describes the internal architecture of the **Gesture Controlled Virtual Mouse with Proton Voice Assistant**.

The system is designed to enable **hands-free human–computer interaction** using a combination of **computer vision**, **speech recognition**, and **OS-level automation**.

---

## High-Level Overview

The application consists of two primary runtime modules:

1. **Proton (Voice Assistant)**
2. **Gesture Controller (Computer Vision Engine)**

These modules operate concurrently using **thread-based execution** and interact directly with the Windows operating system.

---

## High-Level Architecture Diagram (Logical)

User input flows from the microphone and webcam into independent processing pipelines:

- Voice input is processed by Proton
- Visual input is processed by the Gesture Controller
- Both modules execute system-level actions

---

## Core Components

### Proton (Voice Assistant)

Proton is responsible for all **voice-based interactions**.

Responsibilities:
- Capture audio input via microphone
- Convert speech to text using `SpeechRecognition` (Google API)
- Generate spoken responses using `pyttsx3`
- Parse commands using deterministic string matching
- Execute file, browser, and system commands
- Launch and stop gesture recognition in a separate thread
- Gracefully handle microphone timeouts and stream resets

Proton acts as the **orchestrator**, deciding when gesture recognition should run.

---

### Gesture Controller

The Gesture Controller is responsible for **real-time hand gesture recognition**.

Responsibilities:
- Capture webcam frames using OpenCV
- Detect and track hand landmarks using MediaPipe Hands
- Interpret static and dynamic gestures
- Convert gestures into OS-level actions:
  - Cursor movement
  - Mouse clicks
  - Drag and drop
  - Scrolling
  - Volume control
  - Brightness control

Gesture recognition runs **offline** and is CPU-intensive.

---

## Concurrency Model

The application uses **threading**, not multiprocessing.

- **Main Thread**
  - Proton voice loop
  - GUI interaction (Eel)

- **Secondary Thread**
  - Gesture recognition loop

This design ensures:
- Responsive voice interaction
- Continuous gesture tracking
- No blocking caused by heavy vision processing

---

## Data Flow

1. User issues a voice command
2. Proton converts speech to text
3. Command is matched against known patterns
4. If required, the Gesture Controller is launched
5. Webcam frames are processed continuously
6. Recognized gestures trigger OS-level actions
7. Proton remains responsive during gesture execution

---

## Error Handling Strategy

The system explicitly handles common runtime failures:

- Speech recognition timeouts
- Audio stream resets (PyAudio)
- Invalid or unrecognized commands
- Graceful shutdown of gesture threads

This prevents unexpected crashes during long-running sessions.

---

## Platform Constraints

- Operating System: Windows
- Python Version: 3.8.x
- Hardware Requirements:
  - Webcam
  - Microphone

Docker support is provided only for dependency validation and CI workflows.
Hardware-dependent functionality does not run inside containers.

---

## Design Trade-offs

| Decision | Rationale |
|--------|-----------|
Threading over async | Simpler integration with existing code |
String matching | Deterministic and predictable behavior |
CPU-based CV | Avoids GPU dependency |
Windows APIs | Required for system-level automation |

---

## Architectural Goals

- Deterministic behavior
- Clear separation of responsibilities
- Educational readability
- Robust runtime stability
- Minimal external dependencies

---

> This architecture prioritizes **clarity and reliability** over abstraction, making the system suitable for learning, demonstration, and research use.
