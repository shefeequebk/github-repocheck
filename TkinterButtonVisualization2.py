import math
from tkinter import *
import os
import random
import re
from glob import glob
from tkinter import ttk, filedialog
import numpy as np
import cv2
from itertools import groupby, product
from pathlib import Path

visResizeVal = 0
imgResizeVal = 0
imgFullDirs = {}
imgFullPath = ''
posiList = []


# Adding Function Attached To Mouse Callback
def draw(event, x, y, flags, params):
    if event == 1:
        i = math.floor(x / visResizeVal)
        j = math.floor(y / visResizeVal)
        # print('{}_{}'.format(i,j))
        imgKey = '{}_{}'.format(j, i)
        if imgKey in imgFullDirs:
            if (j, i) in posiList:
                # if True:

                # print(imgFullDirs[imgKey])
                imgFile = imgFullDirs[imgKey] + '.jpg'
                filename = os.path.join(imgFullPath, imgFile)
                img = cv2.imread(filename)
                print(filename)
                width = int(img.shape[1] * (imgResizeVal/100))
                height = int(img.shape[0] * (imgResizeVal/100))
                dim = (width, height)
                # resize image
                img = cv2.resize(img, dim, interpolation=cv2.INTER_AREA)
                cv2.imshow('Pos', img)
                cv2.waitKey(0)

def runScript():
    global visResizeVal, imgFullPath, posiList, imgResizeVal
    inGrainImgDir = directory1Select.folder_path
    inGrainImgDir = inGrainImgDir + '/*.jpg'
    imgFullPath = directory2Select.folder_path
    imgFullDir = imgFullPath + '/*.jpg'
    imgFullList = glob(imgFullDir)
    visResizeVal = v1.get()
    imgResizeVal = v2.get()
    imgList = glob(inGrainImgDir)
    imgPosList = []

    for img in imgList:
        filepath = os.path.splitext(img)[0]
        filename = Path(filepath).stem
        imgPos = [int(e) for e in re.search('Pos(.*)_PMax', filename).group(1).split('_')]
        imgPosList.append((imgPos[0], imgPos[1]))
    for img in imgFullList:
        filepath = os.path.splitext(img)[0]
        filename = Path(filepath).stem
        imgPos = [int(e) for e in re.search('Pos(.*)_PMax', filename).group(1).split('_')]
        imgFullDirs[str(imgPos[0]) + '_' + str(imgPos[1])] = filename

    def Manhattan(tup1, tup2):
        return abs(tup1[0] - tup2[0]) + abs(tup1[1] - tup2[1])

    # initializing list
    test_list = imgPosList

    # printing original list
    # print("The original list is : " + str(test_list))

    # Group Adjacent Coordinates
    # Using product() + groupby() + list comprehension
    man_tups = [sorted(sub) for sub in product(test_list, repeat=2)
                if Manhattan(*sub) == 1]

    res_dict = {ele: {ele} for ele in test_list}
    for tup1, tup2 in man_tups:
        res_dict[tup1] |= res_dict[tup2]
        res_dict[tup2] = res_dict[tup1]
    arrangedList = [[*next(val)] for key, val in groupby(
        sorted(res_dict.values(), key=id), id)]
    # print(arrangedList)
    xMax = max([e[0] for e in imgPosList]) + 1
    yMax = max([e[1] for e in imgPosList]) + 1
    imgPosArr = np.zeros([xMax, yMax, 3])
    posiList = []
    arrangedTemp = []
    for x in arrangedList:
        li = []
        for i in x:
            if i not in posiList:
                li.append(i)
                posiList.append(i)
        if len(li) > 0:
            arrangedTemp.append(li)
    arrangedList = arrangedTemp
    for x in arrangedList:
        f, s, t = random.randint(0, 200) / 210, random.randint(0, 200) / 210, random.randint(0, 200) / 210
        for i in x:
            imgPosArr[i[0]][i[1]] = [f, s, t]
    width = int(imgPosArr.shape[1] * visResizeVal)
    height = int(imgPosArr.shape[0] * visResizeVal)
    dim = (width, height)
    # resize image
    imgPosArr = cv2.resize(imgPosArr, dim, interpolation=cv2.INTER_AREA)
    # Making Window For The Image
    cv2.namedWindow("imgGroup")
    # Adding Mouse CallBack Event
    cv2.setMouseCallback("imgGroup", draw)
    cv2.imshow('imgGroup', imgPosArr)

    cv2.waitKey(0)


gui = Tk()
gui.title('Image Groups Visualizer')
# gui.geometry('400x400')


class FolderSelect(Frame):
    def __init__(self, parent=None, folderDescription="", **kw):
        Frame.__init__(self, master=parent, **kw)
        self.folderPath = StringVar()
        self.lblName = Label(self, text=folderDescription)
        self.lblName.grid(row=0, column=0)
        self.entPath = Entry(self, textvariable=self.folderPath)
        self.entPath.grid(row=0, column=1)
        self.btnFind = ttk.Button(self, text="Browse Folder", command=self.setFolderPath)
        self.btnFind.grid(row=0, column=2)

    def setFolderPath(self):
        folder_selected = filedialog.askdirectory()
        self.folderPath.set(folder_selected)

    @property
    def folder_path(self):
        return self.folderPath.get()


folderPath = StringVar()

directory1Select = FolderSelect(gui, "Select cropped grain images directory")
directory1Select.grid(row=0, pady=(10, 10), padx=(10, 10), columnspan=1100)

directory2Select = FolderSelect(gui, "Select complete images directory")
directory2Select.grid(row=1, pady=(10, 10), padx=(10, 10), columnspan=1100)

lab1 = Label(gui, text="Visualizer image box size in pixel", anchor='w')
lab1.grid(row=2, column=0, pady=(30, 10), padx=(10, 0), sticky='e')
v1 = DoubleVar()
v1.set(10)
s1 = Scale(gui, variable=v1,
           from_=5, to=20,
           orient=HORIZONTAL)
s1.grid(row=2, column=1, pady=(10, 0), padx=(10, 10), sticky="w")
lab1 = Label(gui, text="Image window size in %", anchor='w')
lab1.grid(row=3, column=0, pady=(30, 10), padx=(10, 0), sticky='e')
v2 = DoubleVar()
v2.set(10)
s2 = Scale(gui, variable=v2,
           from_=5, to=100,
           orient=HORIZONTAL)
s2.grid(row=3, column=1, pady=(10, 0), padx=(10, 10), sticky="w")
runButton = Button(gui, text='Run', width=10, command=runScript)
runButton.grid(row=3, column=2, padx=(50, 10), pady=(30, 10))

gui.mainloop()
