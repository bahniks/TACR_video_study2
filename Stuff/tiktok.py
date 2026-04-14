#! python3

from tkinter import *

import os
import random
import vlc

from common import ExperimentFrame
from gui import GUI


class TikTok:
    def __init__(self, canvas, width=600, height=337, owner=None):
        self.canvas = canvas
        self.width = width
        self.height = height
        self.owner = owner

        self.canvas.configure(width=self.width, height=self.height)
        self.canvas.configure(background="black", highlightbackground="black", highlightcolor="black")

        self.distraction_videos = self.get_distraction_videos()
        self.current_distraction_index = self._get_saved_index()
        self.player2 = None
        self.running = True

        self.instance2 = vlc.Instance('--vout=direct3d9')
        self.player2 = self.instance2.media_player_new()
        self.player2.set_hwnd(self.canvas.winfo_id())

        self.event_manager2 = self.player2.event_manager()
        self.event_manager2.event_attach(vlc.EventType.MediaPlayerEndReached, self.on_distraction_video_end)

        self.play_next_distraction_video()


    def on_distraction_video_end(self, event):
        if not self.running:
            return
        self.canvas.after(0, self.play_next_distraction_video)

    def play_next_distraction_video(self):
        if not self.running or not self.distraction_videos or self.player2 is None:
            return

        self.player2.stop()

        video_path = self.distraction_videos[self.current_distraction_index % len(self.distraction_videos)]
        media2 = self.instance2.media_new(video_path)
        self.player2.set_media(media2)
        self.player2.audio_set_mute(True)
        self.player2.play()
        self.current_distraction_index += 1
        self._save_index(self.current_distraction_index)

    def stop(self):
        if not self.running:
            return

        self.running = False
        self.current_distraction_index += 1
        self._save_index(self.current_distraction_index)
        if self.player2 is not None:
            self.player2.stop()

    def play(self):
        return

    def get_distraction_videos(self):
        distractions_path = os.path.join(os.getcwd(), "Stuff", "Distractions")
        allowed_extensions = {".mp4", ".avi", ".mov", ".mkv"}
        videos = [
            f for f in os.listdir(distractions_path)
            if os.path.splitext(f)[1].lower() in allowed_extensions
        ]
        status = self._get_status()
        if status is not None and "tiktok_video_order" in status:
            saved_order = status["tiktok_video_order"]
            if (
                isinstance(saved_order, list)
                and saved_order
                and all(os.path.splitext(path)[1].lower() in allowed_extensions for path in saved_order)
            ):
                return saved_order

        full_paths = [os.path.join(distractions_path, v) for v in videos]
        random.shuffle(full_paths)
        if status is not None:
            status["tiktok_video_order"] = full_paths
        return full_paths

    def _get_status(self):
        if self.owner is None:
            return None
        root = getattr(self.owner, "root", None)
        if root is None:
            return None
        status = getattr(root, "status", None)
        if isinstance(status, dict):
            return status
        return None

    def _get_saved_index(self):
        status = self._get_status()
        if status is None:
            return 0
        return int(status.get("tiktok_index", 0))

    def _save_index(self, index):
        status = self._get_status()
        if status is not None:
            status["tiktok_index"] = int(index)


class TikTokTest(ExperimentFrame):
    def __init__(self, root):
        super().__init__(root)

        canvas = Canvas(self, width=600, height=337, background="black", highlightbackground="black", highlightcolor="black")
        canvas.grid(row=0, column=0)

        self.tiktok = TikTok(canvas, width=600, height=337, owner=self)
        self.tiktok.play()

    def stop(self):
        self.tiktok.stop()


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.getcwd()))
    GUI([TikTokTest])
