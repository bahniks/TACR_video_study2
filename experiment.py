#! python3

import sys
import os

# Ensure we're in the correct directory regardless of how the script is executed
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# Add the Stuff directory to Python path for imports
stuff_path = os.path.join(script_dir, "Stuff")
if stuff_path not in sys.path:
    sys.path.insert(0, stuff_path)

# Redirect stdout and stderr to log file for debugging when run from double-click
log_file_path = os.path.join(script_dir, "log.txt")
log_file = None
try:
    log_file = open(log_file_path, 'w', encoding='utf-8')
    sys.stdout = log_file
    sys.stderr = log_file
    print(f"Script directory: {script_dir}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Python path: {sys.path}")
except Exception as e:
    # If logging fails, continue without it
    log_file = None


from gui import GUI

from intros import Initial, Intro, Ending
from demo import Demographics
from comments import Comments
from login import Login
from videointros import Sound, VideoIntro, StartVideos, SecondModuleIntro, QuizIntroduction
from videos import Videos, Attention, Quiz, EndQuestionnaire, Videos2, Postdiction
from questionnaire import UPPS, SCI, SAMS, Mindset, QuestInstructions
from intervention import Intervention



frames = [Initial,
          Login, 
          Intro,             
          Sound,
          VideoIntro,
          Intervention,
          StartVideos,
          Videos2, Attention,
          Videos2, Attention,
          Videos2, Attention,
          Videos2, Attention,
          SecondModuleIntro, 
          Videos2, Attention,
          Videos2, Attention,
          Videos2, Attention,
          Videos2, Attention,
          EndQuestionnaire,
          QuestInstructions,
          UPPS,
          SCI,
          SAMS,
          Mindset,
          QuizIntroduction,
          Quiz,
          Postdiction,
          Demographics,
          Comments,
          Ending
         ]

#frames = [Login, Videos2]

if __name__ == "__main__":
    try:
        print("Starting experiment...")
        gui = GUI(frames, load = os.path.exists("temp.json"))
        print("GUI session finished")
        print("Experiment completed")
    except Exception as e:
        print(f"Error during experiment execution: {e}")
        import traceback
        print("Full traceback:")
        traceback.print_exc()
    finally:
        # Ensure log file is closed properly
        if log_file and not log_file.closed:
            sys.stdout.flush()
            sys.stderr.flush()
            log_file.close()