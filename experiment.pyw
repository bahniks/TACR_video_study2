#! python3

import sys
import os

sys.path.append(os.path.join(os.getcwd(), "Stuff"))


from gui import GUI

from intros import Initial, Intro, Ending
from demo import Demographics
from comments import Comments
from login import Login
from videointros import Sound, VideoIntro, StartVideos, SecondModuleIntro, QuizIntroduction
from videos import Videos, Attention, Quiz, EndQuestionnaire, Videos2, Postdiction
from questionnaire import UPPS, SCI, SAMS, Mindset, QuestInstructions
from intervention import Intervention


    
# TODO ukladani dat vsude
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
          Quiz, # upravit formatovani delky odpovedi
          Postdiction,
          Demographics,
          Comments,
          Ending
         ]

#frames = [Login, Videos2]

if __name__ == "__main__":
    GUI(frames, load = os.path.exists("temp.json"))