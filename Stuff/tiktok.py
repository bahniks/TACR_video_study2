#! python3

from tkinter import *

import os
import random
import threading
import vlc
import time

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
        self._stopped = False
        self._last_callback_time = 0  # Initialize callback cooldown timer
        self._video_play_count = 0  # Track rapid video switching
        self._video_play_start_time = 0  # Track callback loop timing

        # Create separate VLC instance for TikTok to avoid conflicts with main video
        self.instance2 = vlc.Instance(
            '--aout=directsound',
            '--avcodec-hw=none',  # Disable hardware acceleration for TikTok to avoid conflicts
            '--no-video-title-show',
            '--drop-late-frames',
            '--skip-frames',
            '--verbose=0',  # Reduce logging for TikTok
            '--intf=dummy',
            '--vout=win32',  # Use Win32 GDI instead of DirectX to avoid conflicts
            '--avcodec-skiploopfilter=all',
            '--network-caching=300',
            '--file-caching=300',
        )
        print("DEBUG: TikTok using separate VLC instance (Win32 output, no HW accel)")
        
        self.player2 = self.instance2.media_player_new()
        self.player2.set_hwnd(self.canvas.winfo_id())

        self.event_manager2 = self.player2.event_manager()
        self.event_manager2.event_attach(vlc.EventType.MediaPlayerEndReached, self.on_distraction_video_end)

        # Don't start playing immediately - wait for explicit play() call
        print("DEBUG: TikTok initialized, waiting for play() call")

    def play(self):
        """Start TikTok playback when called (delayed from main video startup)"""
        print("DEBUG: TikTok play() called, starting first video")
        self.play_next_distraction_video()

    def _is_widget_alive(self, widget):
        if widget is None:
            return False
        try:
            # Use a simple existence check instead of Tkinter calls
            return hasattr(widget, 'winfo_id') and not self._stopped
        except (TclError, RuntimeError, AttributeError):
            return False


    def on_distraction_video_end(self, event):
        # Thread-safe check using simple boolean flags
        if self._stopped or not self.running:
            return
        
        # Add cooldown to prevent rapid callback loops
        current_time = time.time()
        if hasattr(self, '_last_callback_time'):
            if current_time - self._last_callback_time < 1.0:  # Minimum 1s between callbacks
                print(f"DEBUG: TikTok callback too soon, ignoring ({current_time - self._last_callback_time:.2f}s)")
                return
        
        self._last_callback_time = current_time
        print(f"DEBUG: TikTok video ended, scheduling next video")
        
        try:
            # Schedule the next video in the main thread
            if hasattr(self.canvas, 'after'):
                self.canvas.after(500, self.play_next_distraction_video)  # 500ms delay for stability
        except (TclError, RuntimeError, AttributeError):
            return

    def play_next_distraction_video(self):
        if self._stopped or not self.running or not self.distraction_videos or self.player2 is None:
            print("DEBUG: TikTok playback stopped or invalid state")
            return

        # Additional safety check for GUI state
        try:
            if not hasattr(self.canvas, 'winfo_id'):
                print("DEBUG: Canvas not ready for video playback")
                return
        except (TclError, RuntimeError, AttributeError):
            print("DEBUG: Canvas unavailable, stopping TikTok playback")
            return

        # Check if we're in a callback loop (too many videos played recently)
        if hasattr(self, '_video_play_count'):
            current_time = time.time()
            if not hasattr(self, '_video_play_start_time'):
                self._video_play_start_time = current_time
            elif current_time - self._video_play_start_time < 10 and self._video_play_count > 5:
                print(f"DEBUG: TikTok callback loop detected ({self._video_play_count} videos in {current_time - self._video_play_start_time:.1f}s), slowing down")
                # Reset counters and add longer delay
                self._video_play_count = 0
                self._video_play_start_time = current_time
                self.canvas.after(3000, self.play_next_distraction_video)  # 3s delay to break loop
                return
        else:
            self._video_play_count = 0
            self._video_play_start_time = time.time()

        self._video_play_count += 1

        try:
            # Stop previous video with timeout protection
            current_state = self.player2.get_state()
            if current_state not in (vlc.State.NothingSpecial, vlc.State.Stopped):
                self.player2.stop()
        except Exception as e:
            print(f"DEBUG: Error stopping TikTok player: {e}")
            return

        video_path = self.distraction_videos[self.current_distraction_index % len(self.distraction_videos)]
        print(f"DEBUG: Playing TikTok video: {video_path} (index: {self.current_distraction_index}, count: {self._video_play_count})")
        
        try:
            media2 = self.instance2.media_new(video_path)
            self.player2.set_media(media2)
            self.player2.audio_set_mute(True)
            
            # Ensure canvas is still valid before playing
            if hasattr(self.canvas, 'winfo_id'):
                self.player2.set_hwnd(self.canvas.winfo_id())
            else:
                print("DEBUG: Canvas no longer available")
                return
                
            play_result = self.player2.play()
            
            # Check if playback started successfully
            state = self.player2.get_state()
            print(f"DEBUG: TikTok video state after play(): {state}, play result: {play_result}")
            
            # Validate video length to detect very short/corrupted videos
            def check_video_validity():
                try:
                    length = self.player2.get_length()
                    if length > 0 and length < 2000:  # Less than 2 seconds
                        print(f"WARNING: Very short TikTok video ({length}ms), may cause callback loops")
                        # Skip to next video immediately
                        self.current_distraction_index += 2  # Skip this problematic video
                        self._save_index(self.current_distraction_index)
                        self.canvas.after(2000, self.play_next_distraction_video)
                        return
                except Exception:
                    pass
                    
            # Check video validity after a short delay
            self.canvas.after(1000, check_video_validity)
            
            self.current_distraction_index += 1
            self._save_index(self.current_distraction_index)
        except Exception as e:
            print(f"ERROR: Failed to play TikTok video: {e}")
            # Try to recover by moving to next video
            self.current_distraction_index += 1
            self._save_index(self.current_distraction_index)
            if self.current_distraction_index < len(self.distraction_videos):
                # Use longer delay for recovery
                try:
                    self.canvas.after(2000, self.play_next_distraction_video)
                except (TclError, RuntimeError, AttributeError):
                    print("DEBUG: Cannot schedule recovery, stopping TikTok playback")
                    self._stopped = True

    def stop(self):
        if self._stopped:
            return

        print("DEBUG: Stopping TikTok playback")
        self._stopped = True
        self.running = False
        self.current_distraction_index += 1
        self._save_index(self.current_distraction_index)
        
        if self.player2 is not None:
            # Detach event handlers immediately on the main thread to prevent
            # any further callbacks from firing during shutdown.
            try:
                if hasattr(self, 'event_manager2') and self.event_manager2:
                    self.event_manager2.event_detach(vlc.EventType.MediaPlayerEndReached)
            except Exception:
                pass

            # Capture references and clear instance attributes so no other code
            # can reach the player / instance while they are being torn down.
            player2 = self.player2
            instance2 = getattr(self, 'instance2', None)
            self.player2 = None
            self.event_manager2 = None
            self.instance2 = None

            # All blocking VLC calls (stop + release) run in a daemon thread so
            # they never stall the Tkinter event loop.
            threading.Thread(
                target=self._vlc_cleanup_thread,
                args=(player2, instance2),
                daemon=True,
            ).start()

    @staticmethod
    def _vlc_cleanup_thread(player2, instance2):
        """Background worker: stop VLC player then release the instance."""
        try:
            state = player2.get_state()
            if state not in (vlc.State.NothingSpecial, vlc.State.Stopped):
                print(f"DEBUG: Stopping TikTok player from state: {state} (background thread)")
                player2.stop()
            # Brief pause to let VLC finish flushing internal buffers before
            # releasing the instance; this is safe here because we are off the
            # main thread.
            time.sleep(0.25)
        except Exception as e:
            print(f"DEBUG: Error stopping TikTok player (background): {e}")
        try:
            if instance2 is not None:
                print("DEBUG: Releasing TikTok VLC instance (background thread)...")
                instance2.release()
                print("DEBUG: TikTok VLC instance released")
        except Exception as e:
            print(f"DEBUG: Error releasing TikTok VLC instance (background): {e}")

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
