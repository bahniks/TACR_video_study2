#! python3

from tkinter import *
from tkinter import ttk

import os
import random
import re

from common import ExperimentFrame
from gui import GUI


class Chat:
    def __init__(self, canvas, width=600, height=337):
        self.canvas = canvas
        self.width = width
        self.height = height

        self.canvas.configure(width=self.width, height=self.height)
        self.canvas.configure(background="white", highlightbackground="white", highlightcolor="white")
        self.canvas.configure(yscrollcommand=self._on_canvas_scroll)

        self.messages_frame = Frame(self.canvas, background="white")
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
        sampled = random.sample(nicknames, 2)
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

        delay_ms = 0 if initial else random.randint(3, 10) * 1000
        self.next_message_job = self.canvas.after(delay_ms, self.show_typing_indicator)

    def show_typing_indicator(self):
        self.next_message_job = None

        if not self.playing or self.current_message_index >= len(self.messages):
            return

        speaker_id, side, _ = self.messages[self.current_message_index]
        nickname = self.speaker_nicknames[speaker_id]
        self.add_typing_indicator(side, nickname)

        typing_delay_ms = random.randint(1800, 2800)
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
        row = Frame(self.messages_frame, background="white")
        row.pack(fill="x", pady=4, padx=4)

        bubble_container = Frame(row, background="white")
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
            background="white",
            foreground="#666666",
            font=("Helvetica", 9, "bold")
        )
        name_label.pack(fill="x", padx=3, pady=(0, 2))

        bubble = Label(
            bubble_container,
            text=text,
            justify="left",
            anchor="w",
            wraplength=int(self.width * 0.62),
            background="#f2f2f2",
            foreground="black",
            padx=10,
            pady=6,
            font=("Helvetica", 11)
        )

        if side == "left":
            bubble.pack(side="left", anchor="w")
        else:
            bubble.pack(side="right", anchor="e")

        self.scroll_to_bottom()

    def add_typing_indicator(self, side, nickname):
        self.clear_typing_indicator()

        row = Frame(self.messages_frame, background="white")
        row.pack(fill="x", pady=(2, 4), padx=4)

        typing_label = Label(
            row,
            text=f"{nickname} is typing...",
            justify="left",
            anchor="w",
            wraplength=int(self.width * 0.62),
            background="#fff3cd",
            foreground="#7a5200",
            padx=10,
            pady=5,
            font=("Helvetica", 10, "italic")
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
        self.canvas.itemconfigure(self.messages_window, width=max(self.canvas.winfo_width() - 16, 50))

    def hide_scrollbar(self):
        if not self.scrollbar_visible:
            return
        self.scrollbar_visible = False
        self.scrollbar.place_forget()
        self.canvas.itemconfigure(self.messages_window, width=max(self.canvas.winfo_width(), 50))

    def _on_canvas_scroll(self, first, last):
        self.scrollbar.set(first, last)


class ChatTest(ExperimentFrame):
    def __init__(self, root):
        super().__init__(root)

        canvas = Canvas(self, width=600, height=337, background="white", highlightbackground="white", highlightcolor="white")
        canvas.grid(row=0, column=0)

        self.chat = Chat(canvas, width=600, height=337)
        self.chat.play()

    def stop(self):
        self.chat.stop()


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.getcwd()))
    GUI([ChatTest])
