# Gesture and Voice Controlled Smart Multimedia System

##  Overview
This project integrates **computer vision, speech recognition, and IoT hardware control** to create a **gesture + voice-based smart multimedia system**.

It allows users to:
- Capture **photos (normal/HDR)**, record **videos**, and control **music playback** using **hand gestures**.
- Activate commands via **speech recognition** when gestures are not detected.
- Use an **ultrasonic sensor** for proximity-based activation.
- Receive **voice feedback** for every interaction.

The system runs on a **Raspberry Pi** with a connected camera, ultrasonic sensor, and microphone.

---

##  Features
-  **Camera Controls**: Capture normal or HDR photos, start/stop video recording.
-  **Music Controls**: Play, pause, resume, next, and previous track using gestures.
-  **Voice Commands**: Trigger photo capture, HDR photo, or video recording via speech recognition.
-  **Ultrasonic Sensor**: Enables context-aware activation based on user distance. 
-  **Voice Feedback**: Real-time audio prompts using TTS (pyttsx3, gTTS). 

---

##Tech Stack
- **Programming Language**: Python 
- **Libraries**: OpenCV, MediaPipe, SpeechRecognition, Pocketsphinx, PyGame, gTTS, pyttsx3 
- **Hardware**: Raspberry Pi, Ultrasonic Sensor (HC-SR04), Camera Module, Microphone 
- **Techniques Used**: Gesture recognition, speech-to-text processing, distance measurement, audio playback 

---


