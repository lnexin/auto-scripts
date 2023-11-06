## ==============================================
# 说明：
# gitLab需要配置成自己的参数
# groupName为空则拉取所有项目，否则拉取group下面的项目
# ==============================================
import tkinter as tk
from tkinter import filedialog
from urllib.request import urlopen
import json
import subprocess
import shlex
import os

# 配置gitLab
gitlabAddr = ''
gitlabPrivateToken = ''
groupName =['group1',
    'group2']

root = tk.Tk()
root.withdraw()
folderPath = filedialog.askdirectory()

def main():
    for item in groupName:
        clont(item)

def clont(groupName):
    url = "http://%s/api/v4/groups/%s/projects?private_token=%s&per_page=1000&order_by=name" % (
            gitlabAddr, groupName, gitlabPrivateToken)

    print(url)

    allProjects = urlopen(url)
    allProjectsDict = json.loads(allProjects.read().decode(encoding='UTF-8'))
    for thisProject in allProjectsDict:
        try:
            thisProjectURL = thisProject['http_url_to_repo']
            thisProjectPath = thisProject['path_with_namespace']
            print(thisProjectURL + ' ' + thisProjectPath)

            filePath = folderPath + "/" + thisProjectPath
            if os.path.exists(filePath):
                os.system('cd %s && git pull' % filePath)
            else:
                command = shlex.split('git clone %s %s' % (thisProjectURL, thisProjectPath))
                resultCode = subprocess.Popen(command, cwd=folderPath)

        except Exception as e:
            print("Error on %s: %s" % (thisProjectURL, e.strerror))


main()