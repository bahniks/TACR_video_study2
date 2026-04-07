#! python3

from tkinter import *
from tkinter import ttk

import os
import random
import re

from common import ExperimentFrame
from gui import GUI


class Chat:
    # Configuration parameters
    CONFIG = {
        # Timing (in milliseconds)
        "message_delay_min": 2500,
        "message_delay_max": 8000,
        "typing_delay_min": 1000,
        "typing_delay_max": 2200,
        
        # UI dimensions
        "canvas_width": 600,
        "canvas_height": 800,
        "scrollbar_width": 16,
        "bubble_wrap_ratio": 0.62,
        
        # Speaker settings
        "num_speakers": 2,
        
        # Styling - Colors
        "bg_color": "white",
        "bubble_bg_color": "#f2f2f2",
        "name_color": "#666666",
        "text_color": "black",
        "typing_bg_color": "#fff3cd",
        "typing_text_color": "#7a5200",
        
        # Styling - Fonts
        "name_font": ("Helvetica", 9, "bold"),
        "message_font": ("Helvetica", 11),
        "typing_font": ("Helvetica", 10, "italic"),
        
        # Styling - Padding
        "name_padx": 3,
        "name_pady": (0, 2),
        "bubble_padx": 10,
        "bubble_pady": 6,
        "typing_padx": 10,
        "typing_pady": 5,
        "message_row_pady": 4,
        "typing_row_pady": (2, 4),
        "message_row_padx": 4,
    }
    
    def __init__(self, canvas, width=None, height=None):
        self.canvas = canvas
        self.width = width if width is not None else self.CONFIG["canvas_width"]
        self.height = height if height is not None else self.CONFIG["canvas_height"]

        self.canvas.configure(width=self.width, height=self.height)
        self.canvas.configure(background=self.CONFIG["bg_color"], highlightbackground=self.CONFIG["bg_color"], highlightcolor=self.CONFIG["bg_color"])
        self.canvas.configure(yscrollcommand=self._on_canvas_scroll)

        self.messages_frame = Frame(self.canvas, background=self.CONFIG["bg_color"])
        self.messages_window = self.canvas.create_window(
            (0, 0),
            window=self.messages_frame,
            anchor="nw",
            width=self.width
        )

        self.scrollbar = ttk.Scrollbar(self.canvas, orient="vertical", command=self.canvas.yview)
        self.scrollbar_visible = False

        self.messages = self.load_random_chat_messages()
        self.speaker_nicknames = self.sample_speaker_nicknames()
        self.current_message_index = 0
        self.playing = False
        self.next_message_job = None
        self.typing_job = None
        self.typing_row = None

        self.canvas.bind("<Configure>", self.on_canvas_configure)
        self.messages_frame.bind("<Configure>", self.on_messages_configure)

    def stop(self):
        self.playing = False
        if self.next_message_job is not None:
            self.canvas.after_cancel(self.next_message_job)
            self.next_message_job = None
        if self.typing_job is not None:
            self.canvas.after_cancel(self.typing_job)
            self.typing_job = None
        self.clear_typing_indicator()

    def play(self):
        if self.playing:
            return
        self.playing = True
        self.schedule_next_message(initial=True)

    def sample_speaker_nicknames(self):
        nicknames = [
            "PixelFox", "NightOwl", "BlueComet", "EchoWave", "NovaByte", "MangoCat",
            "CloudRider", "LimeSpark", "VelvetMoon", "RedPanda", "OrbitKid", "SilverLeaf",
            "TinyGolem", "UrbanKoala", "NeonWolf", "SunnyCoder", "DustyRocket", "QuietStorm"
        ]
        sampled = random.sample(nicknames, self.CONFIG["num_speakers"])
        return {"s1": sampled[0], "s2": sampled[1]}

    def load_random_chat_messages(self):
        chats_path = os.path.join(os.getcwd(), "Stuff", "Chats")
        if not os.path.exists(chats_path):
            return []

        chat_files = [
            f for f in os.listdir(chats_path)
            if os.path.isfile(os.path.join(chats_path, f)) and f.lower().endswith(".txt")
        ]
        if not chat_files:
            return []

        selected_file = random.choice(chat_files)
        selected_path = os.path.join(chats_path, selected_file)

        parsed_messages = []
        with open(selected_path, "r", encoding="utf-8") as f:
            for raw_line in f:
                line = raw_line.strip()
                if not line:
                    continue
                parsed = self.parse_message_line(line)
                if parsed:
                    parsed_messages.append(parsed)
        return parsed_messages

    def parse_message_line(self, line):
        pattern = r"^\s*(S1|S2|Speaker\s*1|Speaker\s*2|Speaker1|Speaker2)\s*:\s*(.*)$"
        match = re.match(pattern, line, flags=re.IGNORECASE)
        if not match:
            return None

        speaker_label = match.group(1).replace(" ", "").lower()
        message_text = match.group(2).strip()
        if not message_text:
            return None

        if speaker_label in ["s1", "speaker1"]:
            speaker_id = "s1"
            side = "left"
        else:
            speaker_id = "s2"
            side = "right"

        return speaker_id, side, message_text

    def schedule_next_message(self, initial=False):
        if not self.playing:
            return
        if self.current_message_index >= len(self.messages):
            return

        delay_ms = 0 if initial else random.randint(self.CONFIG["message_delay_min"] // 1000, self.CONFIG["message_delay_max"] // 1000) * 1000
        self.next_message_job = self.canvas.after(delay_ms, self.show_typing_indicator)

    def show_typing_indicator(self):
        self.next_message_job = None

        if not self.playing or self.current_message_index >= len(self.messages):
            return

        speaker_id, side, _ = self.messages[self.current_message_index]
        nickname = self.speaker_nicknames[speaker_id]
        self.add_typing_indicator(side, nickname)

        typing_delay_ms = random.randint(self.CONFIG["typing_delay_min"], self.CONFIG["typing_delay_max"])
        self.typing_job = self.canvas.after(typing_delay_ms, self.show_next_message)

    def show_next_message(self):
        self.typing_job = None

        if not self.playing or self.current_message_index >= len(self.messages):
            return

        speaker_id, side, text = self.messages[self.current_message_index]
        nickname = self.speaker_nicknames[speaker_id]
        self.current_message_index += 1

        self.clear_typing_indicator()
        self.add_message_bubble(side, nickname, text)
        self.schedule_next_message()

    def add_message_bubble(self, side, nickname, text):
        row = Frame(self.messages_frame, background=self.CONFIG["bg_color"])
        row.pack(fill="x", pady=self.CONFIG["message_row_pady"], padx=self.CONFIG["message_row_padx"])

        bubble_container = Frame(row, background=self.CONFIG["bg_color"])
        if side == "left":
            bubble_container.pack(side="left", anchor="w")
        else:
            bubble_container.pack(side="right", anchor="e")

        name_anchor = "w" if side == "left" else "e"
        name_justify = "left" if side == "left" else "right"
        name_label = Label(
            bubble_container,
            text=nickname,
            justify=name_justify,
            anchor=name_anchor,
            background=self.CONFIG["bg_color"],
            foreground=self.CONFIG["name_color"],
            font=self.CONFIG["name_font"]
        )
        name_label.pack(fill="x", padx=self.CONFIG["name_padx"], pady=self.CONFIG["name_pady"])

        bubble = Label(
            bubble_container,
            text=text,
            justify="left",
            anchor="w",
            wraplength=int(self.width * self.CONFIG["bubble_wrap_ratio"]),
            background=self.CONFIG["bubble_bg_color"],
            foreground=self.CONFIG["text_color"],
            padx=self.CONFIG["bubble_padx"],
            pady=self.CONFIG["bubble_pady"],
            font=self.CONFIG["message_font"]
        )

        if side == "left":
            bubble.pack(side="left", anchor="w")
        else:
            bubble.pack(side="right", anchor="e")

        self.scroll_to_bottom()

    def add_typing_indicator(self, side, nickname):
        self.clear_typing_indicator()

        row = Frame(self.messages_frame, background=self.CONFIG["bg_color"])
        row.pack(fill="x", pady=self.CONFIG["typing_row_pady"], padx=self.CONFIG["message_row_padx"])

        typing_label = Label(
            row,
            text=f"{nickname} is typing...",
            justify="left",
            anchor="w",
            wraplength=int(self.width * self.CONFIG["bubble_wrap_ratio"]),
            background=self.CONFIG["typing_bg_color"],
            foreground=self.CONFIG["typing_text_color"],
            padx=self.CONFIG["typing_padx"],
            pady=self.CONFIG["typing_pady"],
            font=self.CONFIG["typing_font"]
        )

        if side == "left":
            typing_label.pack(side="left", anchor="w")
        else:
            typing_label.pack(side="right", anchor="e")

        self.typing_row = row
        self.scroll_to_bottom()

    def clear_typing_indicator(self):
        if self.typing_row is not None and self.typing_row.winfo_exists():
            self.typing_row.destroy()
            self.typing_row = None
            self.update_scroll_region()

    def on_messages_configure(self, event):
        self.update_scroll_region()

    def on_canvas_configure(self, event):
        available_width = event.width - (16 if self.scrollbar_visible else 0)
        self.canvas.itemconfigure(self.messages_window, width=max(available_width, 50))
        self.update_scroll_region()

    def update_scroll_region(self):
        self.canvas.update_idletasks()
        bbox = self.canvas.bbox("all")
        if bbox:
            self.canvas.configure(scrollregion=bbox)

        content_height = self.messages_frame.winfo_reqheight()
        canvas_height = self.canvas.winfo_height()
        if content_height > canvas_height:
            self.show_scrollbar()
        else:
            self.hide_scrollbar()

    def scroll_to_bottom(self):
        self.update_scroll_region()
        self.canvas.yview_moveto(1.0)

    def show_scrollbar(self):
        if self.scrollbar_visible:
            return
        self.scrollbar_visible = True
        self.scrollbar.place(relx=1.0, rely=0.0, relheight=1.0, anchor="ne")
        self.canvas.itemconfigure(self.messages_window, width=max(self.canvas.winfo_width() - self.CONFIG["scrollbar_width"], 50))

    def hide_scrollbar(self):
        if not self.scrollbar_visible:
            return
        self.scrollbar_visible = False
        self.scrollbar.place_forget()
        self.canvas.itemconfigure(self.messages_window, width=max(self.canvas.winfo_width(), 50))
        self.update_scroll_region()

    def _on_canvas_scroll(self, first, last):
        self.scrollbar.set(first, last)


class ChatTest(ExperimentFrame):
    def __init__(self, root):
        super().__init__(root)

        canvas_width = Chat.CONFIG["canvas_width"]
        canvas_height = Chat.CONFIG["canvas_height"]
        bg_color = Chat.CONFIG["bg_color"]
        canvas = Canvas(self, width=canvas_width, height=canvas_height, background=bg_color, highlightbackground=bg_color, highlightcolor=bg_color)
        canvas.grid(row=0, column=0)

        self.chat = Chat(canvas, width=canvas_width, height=canvas_height)
        self.chat.play()

    def stop(self):
        self.chat.stop()


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.getcwd()))
    GUI([ChatTest])
