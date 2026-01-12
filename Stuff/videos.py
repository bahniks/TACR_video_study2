#! python3

from tkinter import *
from tkinter import ttk

import os
import vlc
import random

from common import ExperimentFrame, Measure, InstructionsFrame, InstructionsAndUnderstanding
from questionnaire import Questionnaire
from gui import GUI
from login import Login
from constants import LIMIT, TESTING



imiInstructions = """Nyní Vás prosíme o hodnocení zhlédnutého videa. 
U každého z následujících tvrzení uveďte, nakolik je pro vás pravdivé."""

imiInstructions2 = """Skvělé! Dokončili jste všech 5 videí. Můžete si sundat sluchátka, nebudete je již potřebovat.

Nyní Vás prosíme o hodnocení této série videí.
U každého z následujících tvrzení uveďte, nakolik je pro vás pravdivé.
"""

imiScale = ["zcela nepravdivé", "spíše nepravdivé", "do jisté míry pravdivé", "spíše pravdivé", "zcela pravdivé"]

quizInstructions1 = """
Nyní odpovězte na následující otázky týkající se obsahu právě zhlédnutého videa na Prokletí znalosti. U každé otázky jsou uvedeny čtyři odpovědi, vždy jen jedna z nich je správná. (Výsledek tohoto kvízu nemá vliv na výši odměny.)
"""

quizInstructions2 = """
Nyní odpovězte na následující otázky týkající se obsahu právě zhlédnutého videa na Chybu Statutu Quo. U každé otázky jsou uvedeny čtyři odpovědi, vždy jen jedna z nich je správná. (Výsledek tohoto kvízu nemá vliv na výši odměny.)
"""

braces = "{}"
quizInstructions3 = f"""
Nyní Vás čeká závěrečný kvíz, který ověří, co jste si z videí zapamatovali.
Za každou správnou odpověď získáte 1 bod. 
U každé otázky je vždy jedna správná odpověď.

Připomínáme, že pokud v závěrečném kvízu obdržíte alespoň {LIMIT} bodů z 25, obdržíte dodatečnou finanční odměnu ve výši {braces} Kč.
"""



class Videos(ExperimentFrame):
    def __init__(self, root):
        super().__init__(root)
        self.root = root
        self.video_path = self.getVideo()

        # Create tkinter canvas for video
        self.canvas = Canvas(self, width=1200, height=674, background = "white", highlightbackground = "white", highlightcolor = "white")
        self.canvas.grid(column = 1, row = 1, sticky=(N, S, E, W))

        self.columnconfigure(0, weight = 1)
        self.columnconfigure(2, weight = 1)
        self.rowconfigure(0, weight = 1)
        self.rowconfigure(2, weight = 1)

        # Initialize VLC player
        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()

        # Set the video output to the tkinter canvas
        self.player.set_hwnd(self.canvas.winfo_id())

        # Load the video file
        media = self.instance.media_new(self.video_path)
        self.player.set_media(media)

        # Bind the VLC event manager to detect when the video ends
        self.event_manager = self.player.event_manager()
        self.event_manager.event_attach(vlc.EventType.MediaPlayerEndReached, self.on_video_end)

        # Play the video
        self.player.play()

        ttk.Style().configure("TButton", font="helvetica 15")
        self.next = ttk.Button(self, text="Pokračovat", command=self.stop)
        self.next.grid(row=2, column=1)
        if not TESTING:
            self.next["state"] = "disabled"

    def on_video_end(self, event):
        """Callback for when the video ends."""
        self.next["state"] = "normal"

    def stop(self):
        self.player.stop()
        self.root.status["videoNumber"] += 1
        self.nextFun()

    def getVideo(self):
        trial = self.root.status["videoNumber"]
        version = self.root.status["versions"][trial - 1]
        file = [f for f in os.listdir(os.path.join(os.getcwd(), "Stuff", "Videos")) if f.startswith(f"{trial}{version}")]
        return os.path.join(os.getcwd(), "Stuff", "Videos", file[0])


class ArkanoidGame:
    def __init__(self, canvas, width=600, height=337):
        self.canvas = canvas
        self.width = width
        self.height = height
        self.game_over = False
        self.running = True
        
        # Paddle settings
        self.paddle_width = 80
        self.paddle_height = 10
        self.paddle_x = (width - self.paddle_width) // 2
        self.paddle_y = height - 30
        self.paddle_speed = 8
        self.paddle = self.canvas.create_rectangle(
            self.paddle_x, self.paddle_y, 
            self.paddle_x + self.paddle_width, self.paddle_y + self.paddle_height,
            fill="blue"
        )
        
        # Ball settings
        self.ball_size = 10
        self.ball_x = width // 2
        self.ball_y = height // 2
        self.ball_dx = 3
        self.ball_dy = -3
        self.ball = self.canvas.create_oval(
            self.ball_x, self.ball_y,
            self.ball_x + self.ball_size, self.ball_y + self.ball_size,
            fill="red"
        )
        
        # Bricks settings
        self.bricks = []
        self.brick_rows = 5
        self.brick_cols = 8
        self.brick_width = width // self.brick_cols - 5
        self.brick_height = 20
        self.create_bricks()
        
        # Key bindings
        self.keys_pressed = set()
        self.canvas.bind_all("<KeyPress>", self.key_press)
        self.canvas.bind_all("<KeyRelease>", self.key_release)
        
        # Start game loop
        self.update_game()
    
    def create_bricks(self):
        colors = ["red", "orange", "yellow", "green", "blue"]
        for row in range(self.brick_rows):
            for col in range(self.brick_cols):
                x1 = col * (self.brick_width + 5) + 5
                y1 = row * (self.brick_height + 5) + 30
                x2 = x1 + self.brick_width
                y2 = y1 + self.brick_height
                brick = self.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill=colors[row % len(colors)],
                    outline="white"
                )
                self.bricks.append(brick)
    
    def key_press(self, event):
        self.keys_pressed.add(event.keysym)
    
    def key_release(self, event):
        self.keys_pressed.discard(event.keysym)
    
    def move_paddle(self):
        if "Left" in self.keys_pressed or "a" in self.keys_pressed:
            if self.paddle_x > 0:
                self.paddle_x -= self.paddle_speed
        if "Right" in self.keys_pressed or "d" in self.keys_pressed:
            if self.paddle_x < self.width - self.paddle_width:
                self.paddle_x += self.paddle_speed
        
        self.canvas.coords(
            self.paddle,
            self.paddle_x, self.paddle_y,
            self.paddle_x + self.paddle_width, self.paddle_y + self.paddle_height
        )
    
    def update_game(self):
        if not self.running:
            return
            
        if self.game_over:
            return
        
        # Move paddle
        self.move_paddle()
        
        # Move ball
        self.ball_x += self.ball_dx
        self.ball_y += self.ball_dy
        
        # Ball collision with walls
        if self.ball_x <= 0 or self.ball_x >= self.width - self.ball_size:
            self.ball_dx = -self.ball_dx
        if self.ball_y <= 0:
            self.ball_dy = -self.ball_dy
        
        # Ball collision with paddle
        if (self.ball_y + self.ball_size >= self.paddle_y and
            self.ball_x + self.ball_size >= self.paddle_x and
            self.ball_x <= self.paddle_x + self.paddle_width and
            self.ball_dy > 0):
            self.ball_dy = -self.ball_dy
        
        # Ball collision with bricks
        for brick in self.bricks[:]:
            brick_coords = self.canvas.coords(brick)
            if brick_coords:
                if (self.ball_x + self.ball_size >= brick_coords[0] and
                    self.ball_x <= brick_coords[2] and
                    self.ball_y + self.ball_size >= brick_coords[1] and
                    self.ball_y <= brick_coords[3]):
                    self.canvas.delete(brick)
                    self.bricks.remove(brick)
                    self.ball_dy = -self.ball_dy
                    break
        
        # Check win condition
        if not self.bricks:
            self.game_over = True
            self.canvas.create_text(
                self.width // 2, self.height // 2,
                text="YOU WIN!", font=("Helvetica", 30), fill="green"
            )
        
        # Check lose condition (ball falls off bottom)
        if self.ball_y > self.height:
            self.game_over = True
            self.canvas.create_text(
                self.width // 2, self.height // 2,
                text="GAME OVER", font=("Helvetica", 30), fill="red"
            )
        
        # Update ball position
        self.canvas.coords(
            self.ball,
            self.ball_x, self.ball_y,
            self.ball_x + self.ball_size, self.ball_y + self.ball_size
        )
        
        # Schedule next update
        self.canvas.after(16, self.update_game)  # ~60 FPS
    
    def stop(self):
        self.running = False
        self.canvas.unbind_all("<KeyPress>")
        self.canvas.unbind_all("<KeyRelease>")


class Videos2(ExperimentFrame):
    def __init__(self, root):
        super().__init__(root)
        self.root = root
        self.video_path = self.getVideo()

        self.distraction = "video"

        # Create video canvas on the left
        self.canvas1 = Canvas(self, width=600, height=337, background="white", highlightbackground="white", highlightcolor="white")
        self.canvas1.grid(column=1, row=1, sticky=(N, S, E, W), padx=5)

        # Create game canvas on the right
        if self.distraction != "none":
            self.canvas2 = Canvas(self, width=600, height=337, background="black", highlightbackground="black", highlightcolor="black")
            self.canvas2.grid(column=2, row=1, sticky=(N, S, E, W), padx=5)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)
        self.columnconfigure(3, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        # Initialize VLC player for left video with audio output
        self.instance = vlc.Instance('--aout=waveout')
        self.player = self.instance.media_player_new()
        self.player.set_hwnd(self.canvas1.winfo_id())

        # Load the video file
        media = self.instance.media_new(self.video_path)
        self.player.set_media(media)

        # Track video end
        self.video_ended = False

        # Bind the VLC event manager to detect when video ends
        self.event_manager = self.player.event_manager()
        self.event_manager.event_attach(vlc.EventType.MediaPlayerEndReached, self.on_video_end)

        # Play the video
        self.player.play()

        # Initialize distraction on the right
        if self.distraction == "arkanoid":            
            self.game = ArkanoidGame(self.canvas2, width=600, height=337)
        elif self.distraction == "video":
            self.distraction_videos = self.getDistractionVideos()
            self.current_distraction_index = 0
            self.instance2 = vlc.Instance()
            self.player2 = self.instance2.media_player_new()
            self.player2.set_hwnd(self.canvas2.winfo_id())
            
            # Set up event manager for distraction video player
            self.event_manager2 = self.player2.event_manager()
            self.event_manager2.event_attach(vlc.EventType.MediaPlayerEndReached, self.on_distraction_video_end)
            
            # Play first distraction video
            self.play_next_distraction_video()

        ttk.Style().configure("TButton", font="helvetica 15")
        self.next = ttk.Button(self, text="Pokračovat", command=self.stop)
        self.next.grid(row=2, column=1, columnspan=2)
        if not TESTING:
            self.next["state"] = "disabled"

    def on_video_end(self, event):
        """Callback for when main video ends."""
        self.video_ended = True
        self.next["state"] = "normal"

    def on_distraction_video_end(self, event):
        """Callback for when distraction video ends - play the next one."""
        if not self.video_ended:
            # Main video is still playing, play next distraction video
            self.play_next_distraction_video()

    def play_next_distraction_video(self):
        """Load and play the next distraction video from the shuffled list."""
        if len(self.distraction_videos) > 0:
            # Stop current playback
            self.player2.stop()
            
            # Loop through videos, wrapping around if needed
            video_path = self.distraction_videos[self.current_distraction_index % len(self.distraction_videos)]
            media2 = self.instance2.media_new(video_path)
            self.player2.set_media(media2)
            self.player2.audio_set_mute(True)
            self.player2.play()
            self.current_distraction_index += 1

    def stop(self):
        self.player.stop()
        if self.distraction == "arkanoid":
            self.game.stop()
        elif self.distraction == "video":
            self.player2.stop()
        self.root.status["videoNumber"] += 1
        self.nextFun()

    def getVideo(self):
        trial = self.root.status["videoNumber"]
        version = self.root.status["versions"][trial - 1]
        file = [f for f in os.listdir(os.path.join(os.getcwd(), "Stuff", "Videos")) if f.startswith(f"{trial}{version}")]
        return os.path.join(os.getcwd(), "Stuff", "Videos", file[0])

    def getDistractionVideos(self):
        """Get list of distraction videos from Stuff/Distractions folder, shuffled."""
        distractions_path = os.path.join(os.getcwd(), "Stuff", "Distractions")
        if not os.path.exists(distractions_path):
            return []
        
        # Get all video files
        video_extensions = ['.mp4', '.mkv', '.avi', '.mov', '.flv', '.wmv']
        videos = [f for f in os.listdir(distractions_path) 
                  if os.path.isfile(os.path.join(distractions_path, f)) 
                  and os.path.splitext(f)[1].lower() in video_extensions]
        
        # Create full paths and shuffle
        full_paths = [os.path.join(distractions_path, v) for v in videos]
        random.shuffle(full_paths)
        return full_paths


class JOL(InstructionsFrame):
    def __init__(self, root):
        super().__init__(root, text = "", proceed = True, savedata = True)

        self.root = root

        q = "Kolik informací z videa si myslíte, že si budete schopni vybavit přibližně za 2-3 minuty?"
        options = ["0 % (nic z toho)", "20 %", "40 %", "60 %", "80 %", "100 % (vše)"]

        self.measure = Measure(self, text = q, values = options, left = "", right = "", questionPosition = "above", filler = 700, function=self.enable)
        self.measure.grid(row = 1, column = 1)

        self.next["state"] = "disabled"

    def enable(self):
        self.next["state"] = "normal"

    def write(self):
        trial = self.root.status["videoNumber"] - 1
        version = self.root.status["versions"][trial - 1]
        self.file.write("JOL\n")
        self.file.write(self.id + "\t" + str(trial) + "\t" + version + "\t" + self.measure.answer.get() + "\n\n")


class Quiz(InstructionsAndUnderstanding):
    def __init__(self, root, name, **kwargs):
        super().__init__(root, width = 80, name = name, randomize = True, showFeedback = False, fillerheight = 300, finalButton = "Pokračovat", **kwargs)

        self.name = name
        self.correct = 0

        self.rowconfigure(0, weight = 5)
        self.rowconfigure(1, weight = 1)
        self.rowconfigure(2, weight = 1) 
        self.rowconfigure(3, weight = 1)   
        self.rowconfigure(4, weight = 5)

    def nextFun(self):  
        if self.controlQuestion.getAnswer() == self.controlTexts[self.controlNum - 1][1][0]:
            thisCorrect = "1"
            self.correct += 1
        else:
            thisCorrect = "0"
            
        self.file.write(self.id + "\t" + str(self.controlNum) + "\t" + self.controlTexts[self.controlNum - 1][0] + "\t" + self.controlQuestion.getAnswer() + "\t" + thisCorrect + "\t" + str(self.correct) + "\t" + self.root.status["condition"] + "\t" + self.root.status["versions"][int(self.name[-1])-1] + "\n")

        if self.controlNum == len(self.controlTexts):
            self.file.write("\n")
            if self.name == "Quiz3":
                self.root.texts["quizcorrect"] = str(self.correct)
                if self.correct >= LIMIT:
                    self.root.status["quizwin"] = int(self.root.texts["condition"])
                else:
                    self.root.status["quizwin"] = 0
                self.root.texts["quizwin"] = str(self.root.status["quizwin"])
            InstructionsFrame.nextFun(self)   
        else:
            self.createQuestion()     


IMI1 = (Questionnaire,
                {"words": "imi.txt",
                 "question": imiInstructions,
                 "labels": imiScale,
                 "values": 5,
                 "labelwidth": 11,
                 "text": False,
                 "fontsize": 13,
                 "blocksize": 5,
                 "wraplength": 700,
                 "filetext": "IMI1",
                 "fixedlines": 0,
                 "pady": 3})

IMI2 = (Questionnaire,
                {"words": "imi.txt",
                 "question": imiInstructions,
                 "labels": imiScale,
                 "values": 5,
                 "labelwidth": 11,
                 "text": False,
                 "fontsize": 13,
                 "blocksize": 5,
                 "wraplength": 700,
                 "filetext": "IMI2",
                 "fixedlines": 0,
                 "pady": 3})

IMI3 = (Questionnaire,
                {"words": "imi2.txt",
                 "question": imiInstructions2,
                 "labels": imiScale,
                 "values": 5,
                 "labelwidth": 11,
                 "text": False,
                 "fontsize": 13,
                 "blocksize": 5,
                 "wraplength": 700,
                 "filetext": "IMI3",
                 "fixedlines": 0,
                 "pady": 3})


def getQuestions(filename):
    with open(os.path.join(os.path.dirname(__file__), filename), "r", encoding = "utf-8") as f:
        questions = []        
        q = ["", [], ""]
        count = 0
        for line in f:      
            if count == 0:
                q[0] = line.strip().replace("\\n", "\n")
            elif count == 5:                    
                questions.append(q)
                q = ["", [], ""]
                count = -1
            else:
                q[1].append(line.strip())               
            count += 1
    questions.append(q)
    random.shuffle(questions)
    return questions


Quiz1 = (Quiz, {"text": quizInstructions1, "height": 5, "name": "Quiz1", "controlTexts": getQuestions("quiz1.txt")})
Quiz2 = (Quiz, {"text": quizInstructions2, "height": 5, "name": "Quiz2", "controlTexts": getQuestions("quiz2.txt")})
Quiz3 = (Quiz, {"text": quizInstructions3, "height": 8, "name": "Quiz3", "controlTexts": getQuestions("quiz3.txt"), "update": ["condition"]})


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.getcwd()))
    GUI([Login, Videos2, Videos, IMI2,
         JOL, IMI1, Quiz1])