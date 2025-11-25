#! python3
# -*- coding: utf-8 -*- 

import os
import uuid


studies = {"Login": ("id", "first_video","second_video"),
           "JOL": ("id", "trial", "version", "answer"),
           "IMI1": ("id", "item", "answer"),
           "Quiz1": ("id", "trial", "question", "answer", "correct", "total_correct", "condition", "version"), 
           "IMI2": ("id", "item", "answer"),
           "Quiz2": ("id", "trial", "question", "answer", "correct", "total_correct", "condition", "version"), 
           "Selection": ("id", "choice", "condition"),
           "IMI3": ("id", "item", "answer"),
           "Quiz3": ("id", "trial", "question", "answer", "correct", "total_correct", "condition", "version"), 
           "NFC": ("id", "item", "answer"),           
           "Boredom": ("id", "item", "answer"),
           "Hexaco": ("id", "trial", "answer", "item"),
           "Attention checks": ("id", "questionnaire", "correct"),
           "Social": ("id", "item", "answer"),
           "Demographics": ("id", "sex", "age", "language", "student", "field"),
           "Comments": ("id", "comment"),
           "Ending": ("id", "reward")}

frames = ["Initial",
          "Login",
          "Intro",              
          "VideoIntro1",
          "VideoIntro2",
          "Sound",
          "Videos", "JOL", "IMI1", "Quiz1",
          "VideoIntro4",
          "Videos", "JOL", "IMI2", "Quiz2",
          "VideoIntro5",
          "Selection",
          "VideoIntro6",
          "Videos", "Videos", "Videos", "Videos", "Videos",
          "IMI3",
          "Quiz3",
          "QuestInstructions",
          "NFC",
          "Boredom",
          "Hexaco",
          "Social",
          "Demographics",
          "Comments",
          "Ending",         
          "end"
         ]

read = True
compute = True

if read:
    for study in studies:
        with open("{} results.txt".format(study), mode = "w", encoding = "utf-8") as f:
            f.write("\t".join(studies[study]))

    with open("Time results.txt", mode = "w", encoding = "utf-8") as times:
        times.write("\t".join(["id", "order", "frame", "time"]))

    files = os.listdir()
    for file in files:
        if ".py" in file or "results" in file or "file.txt" in file or ".txt" not in file:
            continue

        with open(file, encoding = "utf-8") as datafile:
            #filecount += 1 #
            count = 1
            for line in datafile:

                study = line.strip()
                if line.startswith("time: "):
                    with open("Time results.txt", mode = "a") as times:
                        #print(frames[count-1])
                        #print(line.split()[1])
                        times.write("\n" + "\t".join([file, str(count), frames[count-1], line.split()[1]]))
                        count += 1
                        continue
                if study in studies:
                    with open("{} results.txt".format(study), mode = "a", encoding = "utf-8") as results:
                        for line in datafile:
                            content = line.strip()
                            if not content or content.startswith("time: "):
                                break
                            elif len(content.split("\t")[0]) == 36:
                                try:
                                    uuid.UUID(content.split("\t")[0])
                                    results.write("\n" + content)
                                except ValueError:
                                    results.write(" " + content)
                            else:
                                results.write(" " + content)
                            

if compute:
    times = {frame: [] for frame in frames}
    with open("Time results.txt", mode = "r") as t:
        t.readline()
        for line in t:
            _, num, frame, time = line.split("\t")    
            if int(num) > 1:            
                times[frame0].append(float(time) - t0)            
            t0 = float(time)
            frame0 = frame

    total = 0
    for frame, ts in times.items():
        if ts:
            if frame != "Ending":
                total += sum(ts)/len(ts)
    print("Total")
    print(round(total / 60, 2))

            
