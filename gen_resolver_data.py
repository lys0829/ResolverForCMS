import json
import requests
from requests.compat import urljoin
from datetime import datetime

Config = {}
with open("config.json","r") as f:
    Config = json.loads(f.read())

Subchange_list = json.loads(requests.get(urljoin(Config["cmsRWSURL"],"subchanges")).text)
Problem_list = json.loads(requests.get(urljoin(Config["cmsRWSURL"],"tasks")).text)
User_list = json.loads(requests.get(urljoin(Config["cmsRWSURL"],"users")).text)

Start_time = datetime.strptime(Config["start_time"],"%Y-%m-%d %H:%M:%S").timestamp()
End_time = datetime.strptime(Config["end_time"],"%Y-%m-%d %H:%M:%S").timestamp()
Freeze_time = datetime.strptime(Config["freeze_time"],"%Y-%m-%d %H:%M:%S").timestamp()

Before_Data = {
    "attempted": {},
    "points": 0,
    "problems": {},
    "scoreboard": [],
    "solved": {}
}

for pname in Problem_list:
    Before_Data["attempted"][pname] = 0
    Before_Data["solved"][pname] = 0
    Before_Data["problems"][pname] = {"first_user": 0,"maxscore": 0,"pid": Problem_list[pname]["order"],"score":Problem_list[pname]["max_score"]}

for user in User_list:
    uid = len(Before_Data["scoreboard"])
    User_list[user]["uid"] = uid
    Before_Data["scoreboard"].append({"name":User_list[user]["f_name"]+" "+User_list[user]["l_name"],"group":"","id":uid,"rank":1,"solved":0,"points":0,"score":0})
    for pname in Problem_list:
        Before_Data["scoreboard"][uid][pname] = {"a": 0, "t": 0, "s": "nottried", "score": 0, "color": "_0"}

Final_Data = json.loads(json.dumps(Before_Data))
#print(Before_Data)

for user in User_list:
    print(user)
    print(urljoin(urljoin(Config["cmsRWSURL"],"sublist/"),user))
    req = requests.get(urljoin(urljoin(Config["cmsRWSURL"],"sublist/"),user))
    if req.status_code != 200:
        continue
    #print(req.status_code)
    submissions = json.loads(req.text)
    uid = User_list[user]["uid"]
    for sub in submissions:
        #print(sub["task"])
        Final_Data["scoreboard"][uid][sub["task"]]["a"] += 1
        Final_Data["attempted"][sub["task"]] += 1
        if Final_Data["scoreboard"][uid][sub["task"]]["s"] == "nottried":
            Final_Data["scoreboard"][uid][sub["task"]]["s"] = "tried"
        if sub["score"] > Final_Data["scoreboard"][uid][sub["task"]]["score"]:
            Final_Data["scoreboard"][uid][sub["task"]]["score"] = sub["score"]
            Final_Data["scoreboard"][uid][sub["task"]]["t"] = sub["time"] - Start_time
            if Final_Data["scoreboard"][uid][sub["task"]]["s"] != "solved":
                Final_Data["solved"][sub["task"]] += 1
            Final_Data["scoreboard"][uid][sub["task"]]["s"] = "solved"
        if sub["time"] < Freeze_time:
            Before_Data["scoreboard"][uid][sub["task"]]["a"] += 1
            Before_Data["attempted"][sub["task"]] += 1
            if Before_Data["scoreboard"][uid][sub["task"]]["s"] == "nottried":
                Before_Data["scoreboard"][uid][sub["task"]]["s"] = "tried"
            if sub["score"] > Before_Data["scoreboard"][uid][sub["task"]]["score"]:
                Before_Data["scoreboard"][uid][sub["task"]]["score"] = sub["score"]
                Before_Data["scoreboard"][uid][sub["task"]]["t"] = sub["time"] - Start_time
                if Before_Data["scoreboard"][uid][sub["task"]]["s"] != "solved":
                    Before_Data["solved"][sub["task"]] += 1
                Before_Data["scoreboard"][uid][sub["task"]]["s"] = "solved"
    for pname in Problem_list:
        Final_Data["scoreboard"][uid]["score"] += Final_Data["scoreboard"][uid][pname]["score"]
        Before_Data["scoreboard"][uid]["score"] += Before_Data["scoreboard"][uid][pname]["score"]
        if Final_Data["scoreboard"][uid][pname]["s"] == "solved":
            Final_Data["scoreboard"][uid]["solved"] += 1
        if Before_Data["scoreboard"][uid][pname]["s"] == "solved":
            Before_Data["scoreboard"][uid]["solved"] += 1

import os
from shutil import copyfile
if not os.path.isdir(Config["OutputDir"]):
    os.mkdir(Config["OutputDir"])

with open(os.path.join(Config["OutputDir"],"resolver_before.json"),"w") as f:
    f.write(json.dumps(Before_Data))

with open(os.path.join(Config["OutputDir"],"resolver_final.json"),"w") as f:
    f.write(json.dumps(Final_Data))

for file in os.listdir("template"):
    copyfile("template/"+file,os.path.join(Config["OutputDir"],file))