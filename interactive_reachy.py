import asyncio
import time
import random
import requests
import pyttsx3
import speech_recognition as sr
import numpy as np
from reachy_mini import ReachyMini
from reachy_mini.utils import create_head_pose

# --- Constants & Configuration ---
HOST = '127.0.0.1'
PORT = 8000
NEUTRAL_Z = 20  # Lowered from 30 to prevent IK collisions during tilts
MIN_Z = 0
IDLE_TIMEOUT = 60 

class AssistantPersonality:
    def get_response(self, text):
        text = text.lower()
        
        # New: Explicit "Wake up" / "Hello" intents
        if any(k in text for k in ["hello", "wake", "hi", "hey"]):
            return "wake", "Hello! I am awake and ready to help."
            
        # New: Explicit "Sleep" / "Hide" intents
        elif any(k in text for k in ["sleep", "hide", "retract", "goodnight"]):
            return "sleep", "I am going to take a nap now. Goodbye!"
            
        elif "tired" in text:
            return "sigh", "Oh, I understand. Life as a robot is also exhausting sometimes."
            
        elif "happy" in text:
            return "happy", "I am feeling wonderful today! Thank you for asking."
            
        elif any(k in text for k in ["look over there", "around", "where", "scan"]):
            return "look_away", "Checking that out now!"
            
        elif "listen" in text:
            return "listen", "I am all ears. Tell me everything."
            
        elif "status" in text:
            return "status", "Everything is functioning within normal parameters."
            
        else:
            return "chat", f"You said {text}. That's interesting!"

class ReachyAssistant:
    def __init__(self):
        self.personality = AssistantPersonality()
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 160)
        self.is_active = True
        self.is_speaking = False
        self.current_z = NEUTRAL_Z
        self.last_voice_time = time.time()

    def speak(self, text):
        """Vocalizes text without blocking the main event loop too much."""
        print(f"Reachy: {text}")
        self.is_speaking = True
        self.engine.say(text)
        self.engine.runAndWait()
        self.is_speaking = False

    async def idle_breathing(self, mini):
        """Bio-inspired micro-movements with safety constraints."""
        while self.is_active:
            if not self.is_speaking and self.current_z > 5:
                dr = random.uniform(-1.0, 1.0)
                dp = random.uniform(-1.0, 1.0)
                dy = random.uniform(-1.5, 1.5)
                dz = self.current_z + np.sin(time.time() * 0.4) * 0.5
                
                try:
                    pose = create_head_pose(roll=dr, pitch=dp, yaw=dy, z=dz, degrees=True, mm=True)
                    mini.goto_target(head=pose, duration=2.5, method="minjerk")
                    mini.goto_target(antennas=[random.uniform(-0.03, 0.03), random.uniform(-0.03, 0.03)], duration=1.0)
                except:
                    pass
            await asyncio.sleep(2.5)

    async def check_inactivity(self, mini):
        """Monitors silence and retracts the robot if ignored."""
        while self.is_active:
            if time.time() - self.last_voice_time > IDLE_TIMEOUT and self.current_z > 5:
                print("System: Idle timeout reached. Power saving mode.")
                self.speak("I'm getting a bit sleepy. See you later.")
                self.current_z = 0
                pose = create_head_pose(roll=0, pitch=0, yaw=0, z=0, degrees=True, mm=True)
                mini.goto_target(head=pose, duration=2.0)
            await asyncio.sleep(5)

    def process_command(self, mini, command):
        self.last_voice_time = time.time()
        intent, response = self.personality.get_response(command)
        
        self.speak(response)

        # Logic mapping with safety-tuned values
        if intent == "sleep":
            self.current_z = 0
            pose = create_head_pose(roll=0, pitch=0, yaw=0, z=0, degrees=True, mm=True)
            mini.goto_target(head=pose, duration=2.0)

        elif intent == "wake" or (intent == "chat" and self.current_z < 5):
            self.current_z = NEUTRAL_Z
            pose = create_head_pose(roll=0, pitch=0, yaw=0, z=NEUTRAL_Z, degrees=True, mm=True)
            mini.goto_target(head=pose, duration=1.5)
            # Add antenna wiggle for greeting
            mini.goto_target(antennas=[0.5, -0.5], duration=0.3)
            time.sleep(0.3)
            mini.goto_target(antennas=[0, 0], duration=0.3)

        elif intent == "sigh":
            self.current_z = 15
            pose = create_head_pose(pitch=15, z=15, degrees=True, mm=True)
            mini.goto_target(head=pose, duration=1.5, method="minjerk")
            
        elif intent == "happy":
            mini.goto_target(antennas=[0.5, -0.5], duration=0.3)
            pose = create_head_pose(pitch=-10, roll=8, z=NEUTRAL_Z, degrees=True, mm=True)
            mini.goto_target(head=pose, duration=1.0, method="cartoon")
            time.sleep(1.0)
            mini.goto_target(antennas=[0, 0], duration=0.5)

        elif intent == "look_away":
            mini.look_at(x=random.uniform(0.3, 0.5), y=random.uniform(-0.3, 0.3), z=0.1, duration=1.5)

        elif intent == "listen":
            self.current_z = NEUTRAL_Z
            pose = create_head_pose(roll=12, pitch=0, yaw=0, z=NEUTRAL_Z, degrees=True, mm=True)
            mini.goto_target(head=pose, antennas=[0.7, 0.7], duration=1.2, method="minjerk")
            
        elif intent == "status" and self.current_z < 5:
            # Wake up if it was sleeping
            self.current_z = NEUTRAL_Z
            pose = create_head_pose(roll=0, pitch=0, yaw=0, z=NEUTRAL_Z, degrees=True, mm=True)
            mini.goto_target(head=pose, duration=1.5)

    async def run(self):
        recognizer = sr.Recognizer()
        mic = sr.Microphone()
        
        try:
            with ReachyMini(host=HOST, port=PORT, media_backend='no_media') as mini:
                asyncio.create_task(self.idle_breathing(mini))
                asyncio.create_task(self.check_inactivity(mini))

                self.speak("System initialized. I am ready.")

                while self.is_active:
                    with mic as source:
                        recognizer.adjust_for_ambient_noise(source, duration=0.5)
                        try:
                            audio = await asyncio.get_event_loop().run_in_executor(
                                None, lambda: recognizer.listen(source, timeout=5, phrase_time_limit=4)
                            )
                            command = recognizer.recognize_google(audio)
                            print(f"User: {command}")
                            self.process_command(mini, command)
                            
                        except sr.WaitTimeoutError:
                            continue
                        except Exception as e:
                            pass
        except Exception as e:
            print(f"Critical Error: {e}")

if __name__ == "__main__":
    assistant = ReachyAssistant()
    try:
        asyncio.run(assistant.run())
    except KeyboardInterrupt:
        print("Assistant shutting down.")
