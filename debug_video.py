#! python3
"""
Debug script to test video playback and identify freezing issues
"""

import os
import sys
import time
sys.path.append(os.path.join(os.getcwd(), "Stuff"))

import vlc
from tkinter import *
from tkinter import ttk

def test_vlc_playback():
    """Test basic VLC playback functionality"""
    print("=" * 50)
    print("VLC Playback Diagnostic Test")
    print("=" * 50)
    
    # Check available video files
    videos_dir = os.path.join(os.getcwd(), "Stuff", "Videos")
    if not os.path.exists(videos_dir):
        print(f"ERROR: Videos directory not found: {videos_dir}")
        return False
        
    video_files = [f for f in os.listdir(videos_dir) if f.endswith('.mp4')]
    if not video_files:
        print(f"ERROR: No MP4 files found in {videos_dir}")
        return False
        
    print(f"Found video files: {video_files}")
    
    # Test VLC instance creation
    try:
        vlc_instance = vlc.Instance(
            '--aout=directsound',
            '--avcodec-hw=none',
            '--no-video-title-show',
            '--drop-late-frames',
            '--skip-frames',
            '--verbose=2',
            '--intf=dummy'
        )
        print("✓ VLC instance created successfully")
    except Exception as e:
        print(f"✗ Failed to create VLC instance: {e}")
        return False
    
    # Test media player creation
    try:
        player = vlc_instance.media_player_new()
        print("✓ Media player created successfully")
    except Exception as e:
        print(f"✗ Failed to create media player: {e}")
        return False
    
    # Test media loading
    test_video = os.path.join(videos_dir, video_files[0])
    try:
        media = vlc_instance.media_new(test_video)
        player.set_media(media)
        print(f"✓ Media loaded: {test_video}")
    except Exception as e:
        print(f"✗ Failed to load media: {e}")
        return False
    
    return True

def test_canvas_integration():
    """Test VLC integration with Tkinter canvas"""
    print("\n" + "=" * 50)
    print("Canvas Integration Test")
    print("=" * 50)
    
    root = Tk()
    root.title("Video Playback Test")
    root.geometry("800x600")
    
    # Create canvas similar to Videos2
    canvas = Canvas(root, width=400, height=300, background="black")
    canvas.pack(pady=20)
    
    # Status label
    status_label = ttk.Label(root, text="Initializing...")
    status_label.pack()
    
    # Close button
    close_button = ttk.Button(root, text="Close", command=root.quit)
    close_button.pack(pady=10)
    
    # Test VLC with canvas
    try:
        vlc_instance = vlc.Instance('--verbose=2', '--intf=dummy')
        player = vlc_instance.media_player_new()
        
        # Wait for canvas to be mapped
        root.update_idletasks()
        canvas.update_idletasks()
        
        if canvas.winfo_ismapped():
            player.set_hwnd(int(canvas.winfo_id()))
            print("✓ Canvas HWND set successfully")
            status_label.config(text="Canvas ready for video")
        else:
            print("✗ Canvas not mapped")
            status_label.config(text="ERROR: Canvas not mapped")
            
    except Exception as e:
        print(f"✗ Canvas integration failed: {e}")
        status_label.config(text=f"ERROR: {e}")
    
    # Test with actual video
    videos_dir = os.path.join(os.getcwd(), "Stuff", "Videos")
    video_files = [f for f in os.listdir(videos_dir) if f.endswith('.mp4')]
    
    if video_files:
        test_video = os.path.join(videos_dir, video_files[0])
        try:
            media = vlc_instance.media_new(test_video)
            player.set_media(media)
            player.play()
            status_label.config(text=f"Playing: {video_files[0]}")
            print(f"✓ Started playback of {test_video}")
            
            # Monitor playback state
            def check_state():
                state = player.get_state()
                length = player.get_length()
                time_pos = player.get_time()
                status_text = f"State: {state}, Time: {time_pos}/{length}ms"
                status_label.config(text=status_text)
                print(f"DEBUG: {status_text}")
                root.after(1000, check_state)
            
            root.after(1000, check_state)
            
        except Exception as e:
            print(f"✗ Video playback failed: {e}")
            status_label.config(text=f"ERROR: Video playback failed")
    
    root.mainloop()

def check_system_resources():
    """Check system resources that might affect video playback"""
    print("\n" + "=" * 50)
    print("System Resource Check")
    print("=" * 50)
    
    try:
        import psutil
        
        # Memory usage
        memory = psutil.virtual_memory()
        print(f"Memory usage: {memory.percent}% ({memory.used / (1024**3):.1f}GB used / {memory.total / (1024**3):.1f}GB total)")
        
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        print(f"CPU usage: {cpu_percent}%")
        
        # Disk usage
        disk = psutil.disk_usage('.')
        print(f"Disk usage: {disk.percent}% ({disk.free / (1024**3):.1f}GB free)")
        
    except ImportError:
        print("psutil not available - install with: pip install psutil")
        print("Manual check recommended:")
        print("- Check Task Manager for memory usage")
        print("- Check for other video applications running")
        print("- Verify disk space is adequate")

def main():
    """Run all diagnostic tests"""
    print("Video Playback Diagnostic Tool")
    print("This script will help identify causes of video freezing")
    print()
    
    # Basic VLC test
    if not test_vlc_playback():
        print("\nBasic VLC test failed. Check VLC installation.")
        return
    
    # System resources
    check_system_resources()
    
    # Interactive canvas test
    print("\n" + "=" * 50)
    print("Starting interactive canvas test...")
    print("Watch for freeze issues and check terminal output")
    print("=" * 50)
    
    test_canvas_integration()

if __name__ == "__main__":
    main()