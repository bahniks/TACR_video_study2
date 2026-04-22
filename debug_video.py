#! python3
"""
Enhanced debug script to test Videos2 scenario with dual video playback
Focus on startup/ending issues and threading problems
"""

import os
import sys
import time
import random
import threading
from tkinter import *
from tkinter import ttk

sys.path.append(os.path.join(os.getcwd(), "Stuff"))
import vlc

class VideoDebugger:
    def __init__(self, test_duration=15):
        self.test_duration = test_duration  # Test for only 15 seconds
        self.root = Tk()
        self.root.title("Video Debug - Dual Playback Test")
        self.root.geometry("1400x800")
        
        # Test configuration
        self.use_single_instance = True  # Toggle this to test dual vs single instance
        self.main_player = None
        self.tiktok_player = None
        self.vlc_instance = None
        self.vlc_instance2 = None
        self.test_start_time = None
        self.freeze_detected = False
        
        # Debug tracking
        self.main_state_history = []
        self.tiktok_state_history = []
        self.error_count = 0
        
        self.setup_ui()
        self.setup_vlc()
        
    def setup_ui(self):
        """Create UI similar to Videos2 layout"""
        # Title
        title = ttk.Label(self.root, text=f"Debug: Dual Video Test ({self.test_duration}s)", font=("Arial", 16))
        title.pack(pady=10)
        
        # Main content frame
        content_frame = Frame(self.root)
        content_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        # Left side - Main video (like Videos2)
        left_frame = Frame(content_frame)
        left_frame.pack(side=LEFT, padx=5)
        
        ttk.Label(left_frame, text="Main Video (Videos2)", font=("Arial", 12)).pack()
        self.main_canvas = Canvas(left_frame, width=int(854*0.9), height=int(480*0.9), 
                                 background="white", highlightbackground="white")
        self.main_canvas.pack(pady=5)
        
        # Right side - TikTok distraction (like TikTok)
        right_frame = Frame(content_frame)
        right_frame.pack(side=LEFT, padx=5)
        
        ttk.Label(right_frame, text="TikTok Distraction", font=("Arial", 12)).pack()
        self.tiktok_canvas = Canvas(right_frame, width=480, height=854,
                                   background="black", highlightbackground="black")
        self.tiktok_canvas.pack(pady=5)
        
        # Status frame
        status_frame = Frame(content_frame)
        status_frame.pack(side=LEFT, fill=Y, padx=10)
        
        # Status labels
        ttk.Label(status_frame, text="Status Monitor", font=("Arial", 12, "bold")).pack()
        
        self.main_status = ttk.Label(status_frame, text="Main: Initializing", 
                                   background="yellow", relief="sunken")
        self.main_status.pack(fill=X, pady=2)
        
        self.tiktok_status = ttk.Label(status_frame, text="TikTok: Initializing", 
                                     background="yellow", relief="sunken")
        self.tiktok_status.pack(fill=X, pady=2)
        
        self.time_status = ttk.Label(status_frame, text="Time: 0s", 
                                   background="lightblue", relief="sunken")
        self.time_status.pack(fill=X, pady=2)
        
        self.instance_status = ttk.Label(status_frame, 
                                       text=f"Mode: {'Single' if self.use_single_instance else 'Dual'} Instance",
                                       background="lightgray", relief="sunken")
        self.instance_status.pack(fill=X, pady=2)
        
        # Error log
        ttk.Label(status_frame, text="Error Log", font=("Arial", 10, "bold")).pack(pady=(10,0))
        self.error_text = Text(status_frame, width=40, height=10, font=("Consolas", 8))
        self.error_text.pack(fill=BOTH, expand=True, pady=2)
        
        # Control buttons
        button_frame = Frame(status_frame)
        button_frame.pack(fill=X, pady=5)
        
        self.start_btn = ttk.Button(button_frame, text="Start Test", command=self.start_test)
        self.start_btn.pack(fill=X, pady=2)
        
        self.stop_btn = ttk.Button(button_frame, text="Stop Test", command=self.stop_test, state="disabled")
        self.stop_btn.pack(fill=X, pady=2)
        
        ttk.Button(button_frame, text="Close", command=self.cleanup_and_exit).pack(fill=X, pady=2)
        
    def setup_vlc(self):
        """Initialize VLC instances"""
        try:
            if self.use_single_instance:
                # Single shared instance
                self.vlc_instance = vlc.Instance(
                    '--aout=directsound',
                    '--avcodec-hw=none',
                    '--no-video-title-show',
                    '--drop-late-frames',
                    '--skip-frames',
                    '--verbose=2',
                    '--intf=dummy',
                    '--vout=directx'
                )
                self.vlc_instance2 = self.vlc_instance  # Share the instance
                self.log_error("✓ Single VLC instance created")
            else:
                # Separate instances (original approach)
                self.vlc_instance = vlc.Instance(
                    '--aout=directsound',
                    '--avcodec-hw=none',
                    '--no-video-title-show',
                    '--verbose=2',
                    '--intf=dummy'
                )
                self.vlc_instance2 = vlc.Instance(
                    '--avcodec-hw=none',
                    '--no-video-title-show',
                    '--no-audio',
                    '--verbose=2',
                    '--intf=dummy'
                )
                self.log_error("✓ Dual VLC instances created")
                
        except Exception as e:
            self.log_error(f"✗ VLC setup failed: {e}")
            
    def start_test(self):
        """Start the dual video test"""
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        self.test_start_time = time.time()
        self.freeze_detected = False
        self.error_count = 0
        
        self.log_error(f"Starting {self.test_duration}s test...")
        
        try:
            self.setup_main_video()
            self.setup_tiktok_video()
            self.start_monitoring()
        except Exception as e:
            self.log_error(f"✗ Test setup failed: {e}")
            self.stop_test()
            
    def setup_main_video(self):
        """Setup main video player (like Videos2)"""
        videos_dir = os.path.join(os.getcwd(), "Stuff", "Videos")
        video_files = [f for f in os.listdir(videos_dir) if f.endswith('.mp4')]
        
        if not video_files:
            raise Exception("No video files found")
            
        video_path = os.path.join(videos_dir, video_files[0])
        self.log_error(f"Loading main video: {video_files[0]}")
        
        # Wait for canvas to be ready
        self.root.update_idletasks()
        self.main_canvas.update_idletasks()
        
        if not self.main_canvas.winfo_ismapped():
            self.log_error("WARNING: Main canvas not mapped")
            
        # Create player
        self.main_player = self.vlc_instance.media_player_new()
        
        # Set canvas
        try:
            self.main_player.set_hwnd(int(self.main_canvas.winfo_id()))
            self.log_error("✓ Main canvas HWND set")
        except Exception as e:
            self.log_error(f"✗ Main canvas HWND failed: {e}")
            
        # Load media
        media = self.vlc_instance.media_new(video_path)
        self.main_player.set_media(media)
        
        # Start playback
        result = self.main_player.play()
        self.log_error(f"Main video play() result: {result}")
        
    def setup_tiktok_video(self):
        """Setup TikTok distraction player"""
        distractions_dir = os.path.join(os.getcwd(), "Stuff", "Distractions") 
        
        if not os.path.exists(distractions_dir):
            self.log_error("No distractions directory - creating dummy TikTok")
            return
            
        video_files = [f for f in os.listdir(distractions_dir) 
                      if f.lower().endswith(('.mp4', '.avi', '.mov'))]
        
        if not video_files:
            self.log_error("No TikTok videos found - skipping TikTok test")
            return
            
        video_path = os.path.join(distractions_dir, random.choice(video_files))
        self.log_error(f"Loading TikTok video: {os.path.basename(video_path)}")
        
        # Wait for canvas
        self.root.update_idletasks()
        self.tiktok_canvas.update_idletasks()
        
        # Create player
        self.tiktok_player = self.vlc_instance2.media_player_new()
        
        # Set canvas
        try:
            self.tiktok_player.set_hwnd(int(self.tiktok_canvas.winfo_id()))
            self.log_error("✓ TikTok canvas HWND set")
        except Exception as e:
            self.log_error(f"✗ TikTok canvas HWND failed: {e}")
            
        # Load media and start
        media = self.vlc_instance2.media_new(video_path)
        self.tiktok_player.set_media(media)
        self.tiktok_player.audio_set_mute(True)  # Mute like real TikTok
        
        result = self.tiktok_player.play()
        self.log_error(f"TikTok video play() result: {result}")
        
    def start_monitoring(self):
        """Start monitoring video states"""
        self.monitor_videos()
        
    def monitor_videos(self):
        """Monitor video states for freezing/issues"""
        current_time = time.time() - self.test_start_time
        
        if current_time >= self.test_duration:
            self.log_error(f"✓ Test completed after {self.test_duration}s")
            self.stop_test()
            return
            
        # Update time display
        self.time_status.config(text=f"Time: {current_time:.1f}s")
        
        # Check main video
        if self.main_player:
            try:
                main_state = self.main_player.get_state()
                main_time = self.main_player.get_time()
                main_length = self.main_player.get_length()
                
                self.main_state_history.append((current_time, main_state, main_time))
                
                # Update status
                if main_state == vlc.State.Playing:
                    self.main_status.config(text=f"Main: Playing ({main_time}ms)", background="lightgreen")
                elif main_state == vlc.State.Paused:
                    self.main_status.config(text=f"Main: PAUSED ({main_time}ms)", background="orange")
                    self.log_error(f"WARNING: Main video paused at {current_time:.1f}s")
                elif main_state == vlc.State.Error:
                    self.main_status.config(text="Main: ERROR", background="red")
                    self.log_error(f"ERROR: Main video error at {current_time:.1f}s")
                else:
                    self.main_status.config(text=f"Main: {main_state}", background="yellow")
                    
            except Exception as e:
                self.log_error(f"Main video monitor error: {e}")
                
        # Check TikTok video  
        if self.tiktok_player:
            try:
                tiktok_state = self.tiktok_player.get_state()
                tiktok_time = self.tiktok_player.get_time()
                
                self.tiktok_state_history.append((current_time, tiktok_state, tiktok_time))
                
                # Update status
                if tiktok_state == vlc.State.Playing:
                    self.tiktok_status.config(text=f"TikTok: Playing ({tiktok_time}ms)", background="lightgreen")
                elif tiktok_state == vlc.State.Paused:
                    self.tiktok_status.config(text=f"TikTok: PAUSED ({tiktok_time}ms)", background="orange")
                elif tiktok_state == vlc.State.Error:
                    self.tiktok_status.config(text="TikTok: ERROR", background="red")
                    self.log_error(f"ERROR: TikTok video error at {current_time:.1f}s")
                else:
                    self.tiktok_status.config(text=f"TikTok: {tiktok_state}", background="yellow")
                    
            except Exception as e:
                self.log_error(f"TikTok video monitor error: {e}")
        
        # Schedule next check
        self.root.after(200, self.monitor_videos)  # Check every 200ms
        
    def stop_test(self):
        """Stop the test and cleanup"""
        self.log_error("Stopping test...")
        
        try:
            if self.main_player:
                self.main_player.stop()
                self.main_player = None
                
            if self.tiktok_player:
                self.tiktok_player.stop() 
                self.tiktok_player = None
                
        except Exception as e:
            self.log_error(f"Cleanup error: {e}")
            
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        
        self.main_status.config(text="Main: Stopped", background="lightgray")
        self.tiktok_status.config(text="TikTok: Stopped", background="lightgray")
        
        # Generate summary
        self.generate_summary()
        
    def generate_summary(self):
        """Generate test summary"""
        self.log_error("\n" + "="*30)
        self.log_error("TEST SUMMARY")
        self.log_error("="*30)
        
        main_issues = sum(1 for _, state, _ in self.main_state_history 
                         if state in (vlc.State.Paused, vlc.State.Error))
        tiktok_issues = sum(1 for _, state, _ in self.tiktok_state_history 
                           if state in (vlc.State.Paused, vlc.State.Error))
        
        self.log_error(f"Main video issues: {main_issues}")
        self.log_error(f"TikTok video issues: {tiktok_issues}")
        self.log_error(f"Total errors logged: {self.error_count}")
        
        if main_issues == 0 and tiktok_issues == 0:
            self.log_error("✓ No playback issues detected!")
        else:
            self.log_error("⚠ Issues detected - check logs above")
            
    def log_error(self, message):
        """Log error/debug message"""
        timestamp = time.strftime("%H:%M:%S")
        full_message = f"[{timestamp}] {message}\n"
        
        self.error_text.insert(END, full_message)
        self.error_text.see(END)
        self.root.update_idletasks()
        
        print(f"DEBUG: {message}")  # Also print to console
        
        if "ERROR" in message or "WARNING" in message:
            self.error_count += 1
            
    def cleanup_and_exit(self):
        """Clean up and exit"""
        self.stop_test()
        time.sleep(0.2)  # Give cleanup time
        self.root.destroy()


def main():
    """Run the enhanced video debugger"""
    print("Enhanced Video Debugger - Videos2 Scenario")
    print("Testing dual video playback with 15-second duration")
    print("Focus on startup/ending issues and threading problems")
    print("="*60)
    
    debugger = VideoDebugger(test_duration=15)
    
    try:
        debugger.root.mainloop()
    except KeyboardInterrupt:
        print("Test interrupted by user")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        try:
            debugger.cleanup_and_exit()
        except:
            pass


if __name__ == "__main__":
    main()