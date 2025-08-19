import cv2
import time
import asyncio
import requests
import base64
import mediapipe as mp
import RPi.GPIO as GPIO
import pygame
from gtts import gTTS
import time
import os
import pyttsx3
import os
import subprocess
from datetime import datetime
from pocketsphinx import LiveSpeech
import speech_recognition as sr



GPIO.setmode(GPIO.BCM)
GPIO_TRIGGER = 18
GPIO_ECHO = 24
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)
pygame.mixer.init()
engine = pyttsx3.init()

def distance():
    GPIO.output(GPIO_TRIGGER, True)
    time.sleep(0.01)
    GPIO.output(GPIO_TRIGGER, False)
    StartTime = time.time()
    StopTime = time.time()
    while GPIO.input(GPIO_ECHO) == 0:
        StartTime = time.time()
    while GPIO.input(GPIO_ECHO) == 1:
        StopTime = time.time()
    TimeElapsed = StopTime - StartTime
    distance = (TimeElapsed * 34300) / 2
    #print("Distance:", distance, "cm")
    return distance

def func_voice_warning(text):
    engine.say(text)
    engine.runAndWait()

def load_song(index):
    global current_song_index
    current_song_index = index % len(playlist)
    pygame.mixer.music.load(playlist[current_song_index])


def func_take_photo():
    global last_capture_time
    global frame
    global cam_busy
    global capture_interval
    current_time = time.time()
    if current_time -  last_capture_time >= capture_interval:
        func_voice_warning("Capturing photo")
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        image_filename = f"captured_{timestamp}.png"
        cv2.imwrite(image_filename, frame)
        print(f"Captured photo: {image_filename}")
        last_capture_time = current_time

def func_take_photo_hdr():
    global last_capture_time
    global frame
    global cam_busy
    global capture_interval
    current_time = time.time()
    if current_time -  last_capture_time >= capture_interval:
        func_voice_warning("Capturing hdr photo")
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        image_filename = f"captured_{timestamp}.png"
        hdr_image = cv2.detailEnhance(frame, sigma_s=12, sigma_r=0.15)
        image_filename = "hdr"+image_filename
        cv2.imwrite(image_filename, hdr_image)
        print(f"Captured photo: {image_filename}")
        last_capture_time = current_time

def func_start_video_capture():
    global video_writer
    global is_recording
    if not is_recording :
        func_voice_warning("Video recording on")
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        video_filename = f"video_{timestamp}.avi"
        video_writer = cv2.VideoWriter(video_filename, cv2.VideoWriter_fourcc(*'XVID'), 20.0, (640, 480))
        print(f"Recording started: {video_filename}")
        is_recording = True

def func_end_video_capture():
    global video_writer
    global is_recording
    if is_recording :
        func_voice_warning("Video recording off")
        print("Recording stopped. All fingers are down.")
        is_recording = False
        video_writer.release()  # Stop recording
        video_writer = None

def func_music_play():
    global is_playing
    if not pygame.mixer.music.get_busy() and not is_playing:
        func_voice_warning("Music play")
        load_song(current_song_index)
        pygame.mixer.music.play()
        is_playing=1

def func_music_simple_pause():
    global is_playing
    if pygame.mixer.music.get_busy() and is_playing:
        pygame.mixer.music.pause()
        is_playing=0

def func_music_pause():
    if pygame.mixer.music.get_busy() and is_playing:
        func_music_simple_pause()
        func_voice_warning("Music paused")

def func_music_resume():
    global is_playing
    if not pygame.mixer.music.get_busy():
        func_voice_warning("Music resumed")
        pygame.mixer.music.unpause()
        is_playing=1
    
def func_music_next():
    global current_song_index
    global is_playing
    current_song_index = (current_song_index + 1) % len(playlist)
    func_music_simple_pause()
    func_voice_warning("Playing next music")
    load_song(current_song_index)
    pygame.mixer.music.play()
    is_playing=1

def func_music_prev():
    global current_song_index
    global is_playing
    current_song_index = (current_song_index - 1) % len(playlist)
    func_music_simple_pause()
    func_voice_warning("Playing previous music")
    load_song(current_song_index)
    pygame.mixer.music.play()
    is_playing=1

def func_capture_on_audio():
    global is_recording, video_writer
    global is_audio_capture_on
    is_audio_capture_on = 1
    global camera_1_index
    if not is_recording and video_writer == None:
        cap = cv2.VideoCapture(camera_1_index)
        ret, frame = cap.read()
        global last_capture_time
        global cam_busy
        global capture_interval
        current_time = time.time()
        if current_time -  last_capture_time >= capture_interval and ret:
            func_voice_warning("Capturing photo")
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            image_filename = f"captured_{timestamp}.png"
            cv2.imwrite(image_filename, frame)
            print(f"Captured photo: {image_filename}")
            last_capture_time = current_time
        cap.release()
        cap = None
    is_audio_capture_on = 0

def func_capture_hdr_on_audio():
    global is_recording, video_writer
    global is_audio_capture_on
    is_audio_capture_on = 1
    global camera_1_index
    if not is_recording and video_writer == None:
        cap = cv2.VideoCapture(camera_1_index)
        ret, frame = cap.read()
        global last_capture_time
        global cam_busy
        global capture_interval
        current_time = time.time()
        if current_time -  last_capture_time >= capture_interval and ret:
            func_voice_warning("Capturing hdr photo")
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            image_filename = f"captured_{timestamp}.png"
            hdr_image = cv2.detailEnhance(frame, sigma_s=12, sigma_r=0.15)
            image_filename = "hdr"+image_filename
            cv2.imwrite(image_filename, hdr_image)
            print(f"Captured photo: {image_filename}")
            last_capture_time = current_time
        cap.release()
        cap = None
    is_audio_capture_on = 0

def func_start_video_capture_on_audio():
    global video_writer
    global is_recording
    global is_audio_capture_on
    is_audio_capture_on = 1
    camera_1_index
    if not is_recording and video_writer == None:
        cap = cv2.VideoCapture(camera_1_index)
        ret, frame = cap.read()
        func_voice_warning("Video recording on")
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        video_filename = f"video_{timestamp}.avi"
        video_writer = cv2.VideoWriter(video_filename, cv2.VideoWriter_fourcc(*'XVID'), 20.0, (640, 480))
        print(f"Recording started: {video_filename}")
        is_recording = True
        stime = time.time()
        while True:
            ret, frame = cap.read()
            video_writer.write(frame)
            if time.time() - stime > 5 :
                is_recording = False
                video_writer.release()  # Stop recording
                video_writer = None
                break
        func_voice_warning("Video recording stopped")
        cap.release()
        cap = None
    is_audio_capture_on = 0

recognizer = sr.Recognizer()

def recognize_speech():
    global camera_2_index
    mic = sr.Microphone(device_index=camera_2_index)
    with mic as source:
        print("Please say something...")
        recognizer.adjust_for_ambient_noise(source)  # Adjust for ambient noise
        audio = recognizer.listen(source)
        
        try:
            # Recognize speech using Google Web Speech API
            text = recognizer.recognize_google(audio)
            print(f"You said: {text}")
            if 'capture photo' in text:
                print("Capture photo command recognized.")
                func_capture_on_audio()
            elif 'HDR' in text:
                print("capture hdr photo")
                func_capture_hdr_on_audio()
            elif 'record video' in text:
                print("Record video command recognized.")
                func_start_video_capture_on_audio()
        except sr.UnknownValueError:
            print("Sorry, I could not understand the audio.")
        except sr.RequestError:
            print("Could not request results from Google Speech Recognition service.")
        


'''

def func_take_photo_hdr()

def func_start_video_capture()

def func_end_video_capture()



def func_light_off()

def func_voice_warning()
'''

def function_map(condition):
    if condition == '01100' :
        func_take_photo()
    elif condition == '11001' :
        func_take_photo_hdr()
    elif condition == '11000' :
        func_start_video_capture()
    elif condition == '10000' :
        func_end_video_capture()
    elif condition == '00001' :
        func_music_play()
    elif condition == '00011' :
        func_music_pause()
    elif condition == '00111' :
        func_music_resume()
    elif condition == '01111' :
        func_music_next()
    elif condition == '11111' :
        func_music_prev()


mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)
mp_drawing = mp.solutions.drawing_utils


last_capture_time = 0
capture_interval = 3
cam_busy = 0
last_capture_time = 0
capture_interval = 3
is_recording = False
video_writer = None
frame = None
current_song_index = 0
is_playing = 0
is_audio_capture_on = 0
camera_1_index = 0
camera_2_index = 2

playlist = ["/home/gesture/project0/SoundHelix-Song-1.mp3",
            "/home/gesture/project0/song2.mp3",
            "/home/gesture/project0/song3.mp3",
            "/home/gesture/project0/song4.mp3",
            "/home/gesture/project0/song5.mp3",
            "/home/gesture/project0/Mere Dholna.mp3",
            ]

speech = LiveSpeech(
    lm='7740.lm',        # Path to your language model
    dic='7740.dic',      # Path to your dictionary
    kws_threshold=1e-20  # Adjust for sensitivity
)


def main():
    global last_capture_time
    global function_map
    global frame
    global speech, camera_1_index
    frame_count=0
    c=0
    final_id=[0,0,0,0,0]
    prev_condition = "#####"
    ultra_distance = 80
    lastTime = time.time()
    while True:
        dist = distance()
        time.sleep(0.05)
        #print("Hello")
        if dist < ultra_distance and is_audio_capture_on == 0:
            cap = cv2.VideoCapture(camera_1_index) # 0 for middle bottom usb port and 1 for left bottom
            print("Camera activated")
            c=0
            final_id=[0,0,0,0,0]
            while dist<ultra_distance or is_recording:
                ret, frame = cap.read()
                frame_count+=1
                #if not ret:
                #   break
                if is_recording and video_writer is not None:  #for recording video according to condition
                    video_writer.write(frame)
                if(frame_count % 5 != 0) :
                    continue
                img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = hands.process(img_rgb)
                if results.multi_hand_landmarks:

                    for hand_landmarks in results.multi_hand_landmarks:
                        #mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                        fingertip_ids = [4, 8, 12, 16, 20]

                        
                        id = []
                        if ((hand_landmarks.landmark[9].x < hand_landmarks.landmark[2].x and hand_landmarks.landmark[2].x < hand_landmarks.landmark[4].x) or (hand_landmarks.landmark[9].x > hand_landmarks.landmark[2].x and hand_landmarks.landmark[2].x > hand_landmarks.landmark[4].x)) :
                            #print("Thumb is up ")
                            id.append(1);
                        else :
                            #print("Thumb is down ")
                            id.append(0);
                        if  hand_landmarks.landmark[8].y < hand_landmarks.landmark[6].y:
                            #print("Index is up ")
                            id.append(1);
                        else :
                            #print("Index is down ")
                            id.append(0);
                        if  hand_landmarks.landmark[12].y < hand_landmarks.landmark[10].y:
                            #print("Middle is up ")
                            id.append(1);
                        else :
                            #print("Middle is down ")
                            id.append(0);
                        if  hand_landmarks.landmark[16].y < hand_landmarks.landmark[14].y:
                            #print("Ring is up ")
                            id.append(1);
                        else :
                            #print("Ring is down ")
                            id.append(0);
                        if  hand_landmarks.landmark[20].y < hand_landmarks.landmark[18].y:
                            #print("Little is up ")
                            id.append(1);
                        else :
                            #print("Little is down ")
                            id.append(0);
                    c=c+1
                    #print(final_id)
                    print("....")
                    for i in range(5):
                        final_id[i] = final_id[i] + id[i]
                    if c==5: # for getting fast response with camera
                        for i in range(5):
                            final_id[i] = final_id[i]/c
                        for i in range(5):
                            if final_id[i] >= 0.5:
                                final_id[i] = 1
                            else :
                                final_id[i] = 0
                        print(final_id)
                        condition = "".join(map(str, final_id))
                        currentTime = time.time()
                        #print(lastTime - currentTime)
                        if prev_condition != condition or (currentTime - lastTime > 3):
                            if dist < ultra_distance:
                                function_map(condition)
                            prev_condition = condition
                            lastTime = time.time()
                        #function call here
                        print(final_id)
                        final_id = [0,0,0,0,0]
                        c=0
                    #print("\n")
                    #print(id)
                    #print(c)
                dist = distance()
                time.sleep(0.05)
            if cap is not None:
                cap.release()
                cap = None
                print("Camera deactivated")
        
        else :
            print("Distance is greater than 50 cm. Activating microphone...")
            recognize_speech() 
            '''
            print("Listening for commands...")
            stime = time.time()
            for phrase in speech:
                print(f"Detected: {phrase.hypothesis()}")
                if 'capture photo' in phrase.hypothesis():
                    print("Capture photo command recognized.")
                    func_capture_on_audio()
                    break
                elif 'capture high quality photo' in phrase.hypothesis():
                    print("Record video command recognized.")
                    func_capture_hdr_on_audio()
                    break
                elif 'capture video' in phrase.hypothesis():
                    print("Record video command recognized.")
                    func_start_video_capture_on_audio()
                    break
                if time.time() - stime > 2:
                    break
                    '''


if __name__ == "__main__":
    main()