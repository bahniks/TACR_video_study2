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
        self.root.title("Video Debug - Enhanced Experiment Simulation")
        self.root.geometry("1400x800")
        
        # Test configuration
        self.use_single_instance = True  # Toggle this to test dual vs single instance
        self.simulate_boost_video = True  # Toggle BoostVideo pause/resume behavior
        self.use_gothrough_timing = True  # Toggle gothrough timing patterns
        
        self.main_player = None
        self.tiktok_player = None
        self.vlc_instance = None
        self.vlc_instance2 = None
        self.test_start_time = None
        self.freeze_detected = False
        
        # Event managers for proper cleanup
        self.main_event_manager = None
        self.tiktok_event_manager = None
        
        # Debug tracking
        self.main_state_history = []
        self.tiktok_state_history = []
        self.error_count = 0
        self.gothrough_active = False
        
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
        
        self.gothrough_btn = ttk.Button(button_frame, text="Test gothrough()", command=self.test_gothrough, state="disabled")
        self.gothrough_btn.pack(fill=X, pady=2)
        
        self.stop_btn = ttk.Button(button_frame, text="Stop Test", command=self.stop_test, state="disabled")
        self.stop_btn.pack(fill=X, pady=2)
        
        # Test mode toggles
        ttk.Label(status_frame, text="Test Modes", font=("Arial", 10, "bold")).pack(pady=(10,0))
        
        self.boost_var = BooleanVar(value=self.simulate_boost_video)
        self.boost_check = ttk.Checkbutton(status_frame, text="Simulate BoostVideo pause/resume", 
                                         variable=self.boost_var)
        self.boost_check.pack(anchor=W)
        
        self.gothrough_var = BooleanVar(value=self.use_gothrough_timing) 
        self.gothrough_timing_check = ttk.Checkbutton(status_frame, text="Use gothrough() timing patterns",
                                                    variable=self.gothrough_var)
        self.gothrough_timing_check.pack(anchor=W)
        
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
        self.gothrough_btn.config(state="normal")
        self.test_start_time = time.time()
        self.freeze_detected = False
        self.error_count = 0
        
        # Update test modes from UI
        self.simulate_boost_video = self.boost_var.get()
        self.use_gothrough_timing = self.gothrough_var.get()
        
        self.log_error(f"Starting {self.test_duration}s test...")
        self.log_error(f"BoostVideo simulation: {self.simulate_boost_video}")
        self.log_error(f"gothrough() timing: {self.use_gothrough_timing}")
        
        try:
            self.setup_main_video()
            self.setup_tiktok_video()
            self.start_monitoring()
        except Exception as e:
            self.log_error(f"✗ Test setup failed: {e}")
            self.stop_test()
            
    def test_gothrough(self):
        """Test the gothrough() method specifically"""
        if not self.main_player:
            self.log_error("No main player - start test first")
            return
            
        self.log_error("Testing gothrough() method...")
        self.gothrough_active = True
        
        # Replicate exact gothrough timing from Videos2
        from time import perf_counter, sleep
        
        deadline = perf_counter() + 4.0
        playback_started = False
        
        self.log_error("gothrough: Starting 4s deadline loop...")
        
        while perf_counter() < deadline:
            self.root.update()  # This is the key difference - GUI updates in loop
            
            try:
                state = self.main_player.get_state()
                if playback_started or state == vlc.State.Playing:
                    playback_started = True
                    self.log_error(f"gothrough: Playback started - state: {state}")
                    break
            except Exception as e:
                self.log_error(f"gothrough: Error checking state: {e}")
                
            sleep(0.05)  # 50ms sleep like real gothrough
            
        if playback_started:
            end_time = perf_counter() + 1.5
            self.log_error("gothrough: Starting 1.5s end loop...")
            
            while perf_counter() < end_time:
                self.root.update()
                sleep(0.05)
                
        self.log_error("gothrough: Complete")
        self.gothrough_active = False
            
    def setup_main_video(self):
        """Setup main video player (like Videos/BoostVideo)"""
        videos_dir = os.path.join(os.getcwd(), "Stuff", "Videos")
        video_files = [f for f in os.listdir(videos_dir) if f.endswith('.mp4')]
        
        if not video_files:
            raise Exception("No video files found")
            
        # Use boost.mp4 if simulating BoostVideo, otherwise first video
        if self.simulate_boost_video and 'boost.mp4' in video_files:
            video_file = 'boost.mp4'
            self.log_error("Using boost.mp4 (BoostVideo simulation)")
        else:
            video_file = video_files[0]
            
        video_path = os.path.join(videos_dir, video_file)
        self.log_error(f"Loading main video: {video_file}")
        
        # Exact replication of Videos.__init__ sequence
        self.root.update_idletasks()
        self.main_canvas.update_idletasks()
        
        if not self.main_canvas.winfo_ismapped():
            self.log_error("WARNING: Main canvas not mapped")
            
        # Create player
        self.main_player = self.vlc_instance.media_player_new()
        
        # Set canvas HWND
        try:
            canvas_id = int(self.main_canvas.winfo_id())
            self.main_player.set_hwnd(canvas_id)
            self.log_error("✓ Main canvas HWND set")
        except Exception as e:
            self.log_error(f"✗ Main canvas HWND failed: {e}")
            
        # Load media
        media = self.vlc_instance.media_new(video_path)
        self.main_player.set_media(media)
        
        # Bind event manager (like real Videos class)
        self.main_event_manager = self.main_player.event_manager()
        self.main_event_manager.event_attach(vlc.EventType.MediaPlayerEndReached, self.on_main_video_end)
        
        # Start playback
        result = self.main_player.play()
        self.log_error(f"Main video play() result: {result}")
        
        # BoostVideo specific behavior: pause immediately, resume after 1s
        if self.simulate_boost_video:
            self.log_error("BoostVideo: Pausing immediately after play()")
            pause_result = self.main_player.pause()
            self.log_error(f"BoostVideo: Pause result: {pause_result}")
            
            # Schedule resume after 1000ms (like real BoostVideo)
            self.root.after(1000, self.boost_video_resume)
            
    def boost_video_resume(self):
        """Resume BoostVideo playback after 1s delay"""
        if self.main_player:
            self.log_error("BoostVideo: Resuming playback after 1s delay")
            try:
                resume_result = self.main_player.play()
                state = self.main_player.get_state()
                self.log_error(f"BoostVideo: Resume result: {resume_result}, state: {state}")
            except Exception as e:
                self.log_error(f"BoostVideo: Resume failed: {e}")
                
    def on_main_video_end(self, event):
        """Main video end callback (like real Videos class)"""
        self.log_error("Main video ended via callback")
        
    def setup_tiktok_video(self):
        """Setup TikTok distraction player with proper event management"""
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
        
        # Exact replication of TikTok.__init__ sequence
        self.root.update_idletasks()
        self.tiktok_canvas.update_idletasks()
        
        # Create player
        self.tiktok_player = self.vlc_instance2.media_player_new()
        
        # Set canvas HWND
        try:
            canvas_id = int(self.tiktok_canvas.winfo_id())
            self.tiktok_player.set_hwnd(canvas_id)
            self.log_error("✓ TikTok canvas HWND set")
        except Exception as e:
            self.log_error(f"✗ TikTok canvas HWND failed: {e}")
            
        # Bind event manager (like real TikTok class)
        self.tiktok_event_manager = self.tiktok_player.event_manager()
        self.tiktok_event_manager.event_attach(vlc.EventType.MediaPlayerEndReached, self.on_tiktok_video_end)
        
        # Load media and start
        media = self.vlc_instance2.media_new(video_path)
        self.tiktok_player.set_media(media)
        self.tiktok_player.audio_set_mute(True)  # Mute like real TikTok
        
        result = self.tiktok_player.play()
        self.log_error(f"TikTok video play() result: {result}")
        
    def on_tiktok_video_end(self, event):
        """TikTok video end callback - this is where threading issues occur!"""
        current_time = time.time() - self.test_start_time
        
        # Track callback frequency to detect loops
        if not hasattr(self, 'callback_times'):
            self.callback_times = []
        self.callback_times.append(current_time)
        
        # Check for rapid callback loop (more than 3 callbacks in 2 seconds)
        recent_callbacks = [t for t in self.callback_times if current_time - t < 2.0]
        if len(recent_callbacks) > 3:
            self.log_error(f"ERROR: TikTok callback loop detected! {len(recent_callbacks)} callbacks in 2s")
            self.error_count += 1
        
        self.log_error(f"TikTok video ended via callback at {current_time:.1f}s (THREADING CONTEXT!)")
        
        # This is the exact code that causes threading issues in the real TikTok class
        try:
            # Simulate the problematic _is_widget_alive check from real TikTok
            if hasattr(self.tiktok_canvas, 'winfo_id'):
                # Schedule next video like real TikTok (this can cause threading issues)
                self.root.after(0, self.play_next_tiktok_video)
        except Exception as e:
            self.log_error(f"TikTok callback error: {e}")
            
    def play_next_tiktok_video(self):
        """Simulate playing next TikTok video (simplified)"""
        self.log_error("TikTok: Playing next video (scheduled from callback)")
        
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
        self.time_status.config(text=f"Time: {current_time:.1f}s {'(gothrough)' if self.gothrough_active else ''}")
        
        # Check main video
        if self.main_player:
            try:
                main_state = self.main_player.get_state()
                main_time = self.main_player.get_time()
                main_length = self.main_player.get_length()
                
                self.main_state_history.append((current_time, main_state, main_time))
                
                # Enhanced status with BoostVideo detection
                boost_info = " (BoostVideo)" if self.simulate_boost_video else ""
                
                if main_state == vlc.State.Playing:
                    self.main_status.config(text=f"Main: Playing ({main_time}ms){boost_info}", background="lightgreen")
                elif main_state == vlc.State.Paused:
                    self.main_status.config(text=f"Main: PAUSED ({main_time}ms){boost_info}", background="orange")
                    if current_time > 2.0:  # Only warn if not expected BoostVideo pause
                        self.log_error(f"WARNING: Main video paused at {current_time:.1f}s")
                elif main_state == vlc.State.Error:
                    self.main_status.config(text=f"Main: ERROR{boost_info}", background="red")
                    self.log_error(f"ERROR: Main video error at {current_time:.1f}s")
                else:
                    self.main_status.config(text=f"Main: {main_state}{boost_info}", background="yellow")
                    
                # Detect BoostVideo specific issues
                if self.simulate_boost_video and current_time > 1.5 and main_state == vlc.State.Paused:
                    self.log_error(f"BoostVideo: Still paused after resume time at {current_time:.1f}s")
                    
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
                    self.log_error(f"WARNING: TikTok video paused at {current_time:.1f}s")
                elif tiktok_state == vlc.State.Error:
                    self.tiktok_status.config(text="TikTok: ERROR", background="red")
                    self.log_error(f"ERROR: TikTok video error at {current_time:.1f}s")
                elif tiktok_state == vlc.State.Ended:
                    self.tiktok_status.config(text="TikTok: ENDED (testing callback)", background="cyan")
                    self.log_error(f"TikTok video ended at {current_time:.1f}s - callback should trigger")
                else:
                    self.tiktok_status.config(text=f"TikTok: {tiktok_state}", background="yellow")
                    
            except Exception as e:
                self.log_error(f"TikTok video monitor error: {e}")
        
        # Schedule next check (faster during gothrough for better detection)
        check_interval = 100 if self.gothrough_active else 200
        self.root.after(check_interval, self.monitor_videos)
        
    def stop_test(self):
        """Stop the test and cleanup"""
        self.log_error("Stopping test...")
        
        try:
            # Proper cleanup like real classes
            if self.main_event_manager and self.main_player:
                try:
                    self.main_event_manager.event_detach(vlc.EventType.MediaPlayerEndReached)
                except Exception as e:
                    self.log_error(f"Main event detach error: {e}")
                    
            if self.tiktok_event_manager and self.tiktok_player:
                try:
                    self.tiktok_event_manager.event_detach(vlc.EventType.MediaPlayerEndReached)
                except Exception as e:
                    self.log_error(f"TikTok event detach error: {e}")
            
            if self.main_player:
                self.main_player.stop()
                self.main_player = None
                
            if self.tiktok_player:
                self.tiktok_player.stop() 
                self.tiktok_player = None
                
            self.main_event_manager = None
            self.tiktok_event_manager = None
                
        except Exception as e:
            self.log_error(f"Cleanup error: {e}")
            
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.gothrough_btn.config(state="disabled")
        
        self.main_status.config(text="Main: Stopped", background="lightgray")
        self.tiktok_status.config(text="TikTok: Stopped", background="lightgray")
        
        # Generate summary
        self.generate_summary()
        
    def generate_summary(self):
        """Generate test summary with experiment-specific analysis"""
        self.log_error("\n" + "="*30)
        self.log_error("TEST SUMMARY")
        self.log_error("="*30)
        
        main_issues = sum(1 for _, state, _ in self.main_state_history 
                         if state in (vlc.State.Paused, vlc.State.Error))
        tiktok_issues = sum(1 for _, state, _ in self.tiktok_state_history 
                           if state in (vlc.State.Paused, vlc.State.Error))
        
        # Check for callback loop issues
        callback_loops = 0
        if hasattr(self, 'callback_times'):
            for i, t in enumerate(self.callback_times):
                recent = [ct for ct in self.callback_times[i:] if ct - t < 2.0]
                if len(recent) > 3:
                    callback_loops += 1
                    break
        
        self.log_error(f"Test configuration:")
        self.log_error(f"  - Single VLC instance: {self.use_single_instance}")
        self.log_error(f"  - BoostVideo simulation: {self.simulate_boost_video}")
        self.log_error(f"  - gothrough() timing: {self.use_gothrough_timing}")
        self.log_error(f"")
        self.log_error(f"Results:")
        self.log_error(f"  - Main video issues: {main_issues}")
        self.log_error(f"  - TikTok video issues: {tiktok_issues}")
        self.log_error(f"  - TikTok callback loops: {callback_loops}")
        self.log_error(f"  - Total errors logged: {self.error_count}")
        
        # Specific experimental condition analysis
        if self.simulate_boost_video:
            boost_pause_issues = sum(1 for t, state, _ in self.main_state_history 
                                   if t > 1.5 and state == vlc.State.Paused)
            self.log_error(f"  - BoostVideo pause issues: {boost_pause_issues}")
        
        if hasattr(self, 'callback_times') and self.callback_times:
            self.log_error(f"  - TikTok callbacks fired: {len(self.callback_times)}")
            
        if main_issues == 0 and tiktok_issues == 0 and callback_loops == 0:
            self.log_error("✓ No playback issues detected!")
            self.log_error("  This suggests the threading fixes are working")
        else:
            self.log_error("⚠ Issues detected - these match experiment conditions")
            self.log_error("  Try testing with different configuration toggles")
            
        self.log_error("\nRecommendations:")
        if main_issues > 0:
            self.log_error("  - Main video issues suggest VLC initialization problems")
            if self.simulate_boost_video:
                self.log_error("  - BoostVideo pause/resume pattern may be causing issues")
        if tiktok_issues > 0:
            self.log_error("  - TikTok issues suggest threading/callback problems")
            self.log_error("  - Check if shared VLC instance helps (toggle setting)")
        if callback_loops > 0:
            self.log_error("  - TikTok callback loops detected - check for short/corrupted videos")
            self.log_error("  - This explains the threading issues in the real experiment")
            
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
    """Run the enhanced video debugger that replicates experiment conditions"""
    print("Enhanced Video Debugger - Experiment Condition Replication")
    print("="*60)
    print("Features:")
    print("- BoostVideo pause/resume pattern simulation")
    print("- gothrough() timing loop replication")  
    print("- VLC event callback threading tests")
    print("- Single vs dual VLC instance comparison")
    print("- 15-second focused testing duration")
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