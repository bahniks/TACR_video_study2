#! python3

import sys
import os

sys.path.append(os.path.join(os.getcwd(), "Stuff"))


from gui import GUI

from intros import Initial, Intro, Ending
from demo import Demographics
from comments import Comments
from login import Login
from videointros import Sound, EndVideos, VideoIntro, StartVideos, SecondModuleIntro
from videos import Videos, Attention, Quiz, Videos2
from quest import QuestInstructions
from questionnaire import UPPS
from intervention import Intervention




frames = [Initial,
          Login, 
          Intro,             
          Sound,
          VideoIntro,
          Intervention, # TO DO
          StartVideos,
          Videos, Attention,
          Videos, Attention,
          Videos, Attention,
          Videos, Attention,
          SecondModuleIntro, 
          Videos, Attention,
          Videos, Attention,
          Videos, Attention,
          Videos, Attention,
          EndVideos,
          QuestInstructions,
          UPPS,
          Quiz,
          Demographics,
          Comments,
          Ending
         ]

#frames = [Login, Videos2]

if __name__ == "__main__":
    GUI(frames, load = os.path.exists("temp.json"))