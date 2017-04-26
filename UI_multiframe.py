from Tkinter import *
import tkMessageBox
import tkFont

import myo as libmyo; libmyo.init('/Users/admin/Desktop/MYO_Download/sdk/myo.framework')
import time
import sys
import csv
import pandas as pd
import numpy as np
import os
from weka.core.dataset import Instance
import weka.core.jvm as jvm
import weka.core.serialization as serialization
from weka.core.converters import Loader
from weka.classifiers import Classifier
import math

import cv2
from PIL import Image,ImageTk


LARGE_FONT = ("verdana",50,"bold")
LARGE_FONT2 = ("verdana",35,"bold")
COUNT_FONT = ("verdana",100,"bold")
NORM_FONT = ("verdana",50,"bold")
SMALL_FONT = ("verdana",8)

EMG = []
for i in range(0,8):
    EMG.append([])
emgFile = []
hub = libmyo.Hub()

fileCount = 0
fileVideos = ['/Users/admin/Desktop/Downwist.mp4','/Users/admin/Desktop/Fingure-open.mp4','/Users/admin/Desktop/Fist-open.mp4']
picVideos = ['/Users/admin/Desktop/Downwist.png','/Users/admin/Desktop/Fingure-open.png','/Users/admin/Desktop/Fist-open.png']
gesture = ['Downed wrist','FINGER - OPEN','FIST - OPEN']
timeCount = 4
Count = 4
   
counter = 3
mistake = 0

start = False
fStart = True

def restart():
    global EMG,emgFile,hub,fileCount
    global timeCount,Count,counter,mistake,start,fStart
    EMG = []
    for i in range(0,8):
        EMG.append([])
    emgFile = []
    hub.stop()
    fileCount = 0
    timeCount = 4
    Count = 4
    
    counter = 3
    mistake = 0
    start = False
    fStart = True

def average_mean(lst):
    mean = np.mean(lst)
    return mean

def standard_deviation(lst):
    num_items = len(lst)
    mean = average_mean(lst)
    differences = [x - mean for x in lst]
    sq_differences = [d ** 2 for d in differences]
    ssd = sum(sq_differences)
    variance = ssd / (num_items - 1)
    sd = math.sqrt(variance)
    return sd

def waveform_length(lst):
    wl = 0
    for inst in range(0,len(lst)-1):
        wl = wl + abs(lst[inst+1]- lst[inst])
    return wl

def TrainAndTest(lst):
        # loadModel
    trainData = "/Users/admin/Desktop/MYO_Download/PythonTest/Mean_SD_WL.multilayer.model"
    loader = Loader(classname="weka.core.converters.ArffLoader")
    obj = serialization.read_all(trainData)
    cls = Classifier(jobject= obj[0])

    testData = "/Users/admin/Desktop/MYO_Download/PythonCode/Arff/traintestWL.arff"
    test = loader.load_file(testData)
    test.class_is_last()
    data = Instance.create_instance(lst)
    test.add_instance(data)

        #output predictions
    for index, inst in enumerate(test):

        pred = cls.classify_instance(inst)
        dist = cls.distribution_for_instance(inst)
        if index == 452:
            if(inst.class_attribute.value(int(pred))=='F'):
                print("Downed wrist")
                answer = "Downed wrist"
            elif(inst.class_attribute.value(int(pred))=='G'):
                print("FINGER - OPEN")
                answer = "FINGER - OPEN"
            elif(inst.class_attribute.value(int(pred))=='H'):
                print("FIST - OPEN")
                answer = "FIST - OPEN"
            else:
                answer = "None"
            return answer
def main():
    dataCompute_SD = []
    dataCompute_Mean = []
    dataCompute_WL =[]
    dataCombine = []

    for j in range (0,8):
        EMG[j] = []
    del emgFile[:]
    try:
        print("Starting")
        while hub.running:
            
            time.sleep(1)
            for a in EMG:
                dataCompute_Mean.append(average_mean(a))
                dataCompute_SD.append(standard_deviation(a))
                dataCompute_WL.append(waveform_length(a))

            dataCombine.extend(dataCompute_Mean)
            dataCombine.extend(dataCompute_SD)
            dataCombine.extend(dataCompute_WL)
            dataCombine.append(1)

            if dataCombine.count != 0 :
                jvm.start()
                train = TrainAndTest(dataCombine)

                return train
    finally:
        jvm.stop()
        
class Listener(libmyo.DeviceListener):
    def __init__(self,popupClass):
        super(Listener, self).__init__()
        self.popupClass = popupClass
        self.locked = False
        self.last_time = 0

    def on_connect(self, myo, timestamp, firmware_version):
        myo.vibrate('short')
        myo.set_stream_emg(libmyo.StreamEmg.enabled)

    def on_emg_data(self,myo,timestamp,emg):
        self.emg = emg
        i = 0
        if emgFile == []:
            myo.vibrate('short')

        emgFile.append(emg)
        for e in emg:
            if(e<0):
                e = e * -1
            EMG[i].append(e)
            i += 1
            
    def on_pose(self, myo, timestamp, pose):
        global start
        if start:
            if pose == libmyo.Pose.wave_out:
                self.popupClass.close('count')
                print('wave_out')
            elif pose == libmyo.Pose.wave_in:
                self.popupClass.close('click')
                print('wave_in')
            self.pose = pose    
            
class SeaofBTCapp(Toplevel):

    def __init__(self, *args,**kwargs):
        global Count
        self.count = Count

        Toplevel.__init__(self,*args,**kwargs)
        Toplevel.wm_title(self,"MYO Physical Therapy ")

        container = Frame(self,bg = "#FAFCBE")
        container.grid()

        container.grid_rowconfigure(0,weight = 1)
        container.grid_columnconfigure(0,weight = 1)

        menubar = Menu(container)
        filemenu = Menu(menubar,tearoff=0)
        filemenu.add_command(label = "Exit",command=quit)
        menubar.add_cascade(label="File", menu = filemenu)

        Toplevel.config(self,menu = menubar)

        self.frames = { }
        
        for F in (StartPage,BTC,LevelPage):
            frame = F(container,self)
            self.frames[F] = frame
            frame.grid(row=0,column=0,sticky="nsew")

        self.show_frame(StartPage)

    def show_frame(self,cont):

        frame = self.frames[cont]
        frame.tkraise()

    def start_program(self,cont,value):
        global cap
        global fileCount
        global timeCount
        global Count

        timeCount = value
        Count = value
        frame = self.frames[cont]
        frame.tkraise()
        # click()
        cap = cv2.VideoCapture(fileVideos[fileCount])


class StartPage(Frame):

    def __init__(self,parent,controller):
        Frame.__init__(self,parent,bg = "#FAFCBE")
        label = Label(self,text = "MYO \n Physical Therapy ", font = LARGE_FONT,bg = "#FAFCBE")
        label.grid(row = 0 ,column = 0,columnspan=2,sticky=W+E+N+S ,pady=50 ,padx=50)

        button1 = Button(self,text=" START ",command = lambda : controller.show_frame(LevelPage))
        button1.grid(row = 1 ,column = 1)
      
        button2 = Button(self,text="EXIT",command = quit)
        button2.grid(row = 1 ,column = 0)

class  LevelPage(Frame):

    def __init__(self,parent,controller):

        Frame.__init__(self,parent,bg = "#FAFCBE")

        label = Label(self,text = "How many time \n do you want to exercise?",font = LARGE_FONT2,bg = "#FAFCBE" )
        label.grid(pady = 50,padx = 50 )

        buttonLevel1 = Button(self,bg = "#FAFCBE",text = "Level 1 : 5  times/gesture",command = lambda : controller.start_program(BTC,5))  
        buttonLevel2 = Button(self,bg = "#FAFCBE",text = "Level 2 : 8  times/gesture",command = lambda : controller.start_program(BTC,8))   
        buttonLevel3 = Button(self,bg = "#FAFCBE",text = "Level 3 : 10 times/gesture",command = lambda : controller.start_program(BTC,10))   
        
        buttonLevel1.grid()
        buttonLevel2.grid()
        buttonLevel3.grid()
        

class BTC(Frame):

    def __init__(self,parent,controller):
        
        Frame.__init__(self,parent,bg = "#FAFCBE")
        self.parent = parent
        self.initialize(controller)

    def initialize(self,controller):
        
        self.imageFrame = Frame(self,width = 445,height = 255,bg = "#A5EDDC")
        self.imageFrame.grid_propagate(0)
        self.imageFrame.grid(row=0, column=0, padx=10, pady=10)

        self.lmain = Label(self.imageFrame,bg = "#A5EDDC",font = COUNT_FONT)
        self.lmain.place(in_=self.imageFrame, anchor="c", relx=.5, rely=.5)
        self.lmain.config(image='')
        

        cap = cv2.VideoCapture('/Users/admin/Desktop/sample.mp4')

        self.rightFrame = Frame(self,bg="#FAFCBE")
        self.rightFrame.grid(row = 0,column = 1,padx = 10 ,pady = 2)

        self.countFrame = Frame(self.rightFrame,width = 100,height = 100)
        self.countFrame.grid(row = 1, column = 0)

        self.checkNum = Label(self.countFrame,font = NORM_FONT ,bg = "#FAFCBE")
        self.checkNum.grid()

        self.nameGesture = Frame(self.rightFrame,width = 120,height = 20,bg = "#FAFCBE")
        self.nameGesture.grid_propagate(0)
        self.nameGesture.grid(row = 2 ,column = 0)

        self.printName = Label(self.nameGesture,bg = "#FAFCBE")
        self.printName.grid()

        self.checkFrame = Frame(self.rightFrame,width = 120 ,height = 100,bg = "#FAFCBE")
        self.checkFrame.grid_propagate(0)
        self.checkFrame.grid(row=3,column = 0,padx = 0,pady = 2)

        self.checkPic = Label(self.checkFrame,bg = "#FAFCBE")
        self.checkPic.grid()

        self.bottom = Frame(self,bg = "#FAFCBE")
        self.bottom.grid(row = 1)
        
        self.B = Button(self.bottom,text="CLICK TO START",command = self.clickStart ,width = 15,bg = "#FAFCBE",state = NORMAL)
        self.B.grid(row = 0,column = 0,padx = 10,pady = 1)
        

        self.button1 = Button(self.bottom,text="back to home",command = lambda : self.exits(controller))
        self.button1.grid(row = 0,column = 1)

            

        
    def exits(self, controller):
        restart()
        self.B.config(state = "normal")
        self.lmain.config(text='',image='')
        self.checkPic.config(image = '')
        self.checkNum.config(text = '')
        self.printName.config(text='')
        self.initialize(controller)
        controller.show_frame(StartPage)
        
    def clickStart(self):
        global cap
        global fileCount
        print('click')

        cap = cv2.VideoCapture(fileVideos[fileCount])
        self.B.config(state = DISABLED)
        self.showFrame()
        
    
    def count(self):
        global counter
        global timeCount
        global fileCount
        global Count

        if counter == -1:
            self.checkNum["text"] = Count
            ans = main()
            
            self.printName.config(text = ans)
            if fileCount != 3 :
                if ans == gesture[fileCount]:
                    timeCount -= 1
                    self.checkNum.config(text = timeCount)
                    img = ImageTk.PhotoImage(Image.open('/Users/admin/Downloads/fr.png'))
                    
                else:
                    img = ImageTk.PhotoImage(Image.open('/Users/admin/Downloads/fs.png'))
                   
                    if timeCount == Count:
                        self.checkNum.config(text = Count)
                    else:
                        self.checkNum.config(text = timeCount)
                self.checkPic.image = img
                self.checkPic.config(image = img)
                    

                if  timeCount != 0:
                    self.checkNum.after(1000,self.count)

                elif fileCount ==2 and timeCount == 0:
                    self.checkNum.config(text = "")
                    fileCount = 0
                    timeCount = Count
                    self.lmain.config(text = "DONE",image = "")
                    self.B.config(state="normal")

                    
                else:
                    self.checkNum.config(text = "0")
                    fileCount += 1
                    counter = Count-1
                    timeCount = Count
                    self.lmain.after(100,self.clickStart)
        elif counter == 0:
            imgP = ImageTk.PhotoImage(Image.open(picVideos[fileCount]))
            self.lmain.image = imgP
            self.lmain.config(text="",image = imgP)
            self.checkNum.config(text = Count )
            counter -= 1
            self.lmain.after(100,self.count)

        else:
            self.lmain.config(text=str(counter),image = '')
            self.lmain.after(1000,self.count)
            counter -= 1

        print('count')

    def showFrame(self):

        ret, frame = cap.read()
        if ret == False:
            self.popUp()
        frame = cv2.flip(frame, 1)
        cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
        size = cv2.resize(cv2image,(400,225))
        img = Image.fromarray(size)
        imgtk = ImageTk.PhotoImage(image=img)
        self.lmain.imgtk = imgtk
        self.lmain.configure(image=imgtk)
        self.lmain.after(10, self.showFrame)

    def popUp(self):
        self.w = popup(self.parent,self)
        self.parent.wait_window(self.w.top)

class popup(Toplevel):

    def __init__(self,parent,frame):
        global start ,fStart
        if fStart :
            global hub
            hub.run(1000,Listener(self))
        start = True
        fStart = False
        self.top = Toplevel(parent)
        self.frame = frame
        self.top.wm_title("test")
        self.l = Label(self.top,text = "Do you want to start?")
        self.l.pack(side="top",padx = 10,pady = 10)

        imgR = ImageTk.PhotoImage(Image.open('/Users/admin/Desktop/1.png'))
        imgL = ImageTk.PhotoImage(Image.open('/Users/admin/Desktop/2.png')) 

        self.B1 = Button(self.top,width = 120,height = 120,command = lambda:self.close('count'))
        self.B1.config(image = imgR,compound = TOP)
        self.B1.image = imgR
        self.B1.pack(side="right",padx = 10,pady = 10)

        self.B2 = Button(self.top,width = 120,height = 120,command = lambda:self.close('click'))
        self.B2.config(image = imgL,compound = TOP)
        self.B2.image = imgL
        self.B2.pack(side="left",padx = 10,pady = 10)
        
        w = 300
        h = 160
        ws = self.top.winfo_screenwidth()
        hs = self.top.winfo_screenheight()
        x = (ws/2)-(w/2)
        y = (hs/2)-(h/2)

        self.top.geometry('%dx%d+%d+%d' % (w, h, x, y))

    def close(self,function):

        global start
        start = False

        self.top.destroy()

        if function == 'count':
            self.frame.count()
        elif function == 'click':
            self.frame.clickStart()


app = SeaofBTCapp()

w = 620 
h = 320 

ws = app.winfo_screenwidth() 
hs = app.winfo_screenheight()

x = (ws/2) - (w/2)
y = (hs/2) - (h/2)

app.geometry('%dx%d+%d+%d' % (w, h, x, y))
app.config(background = "#FAFCBE")

app.mainloop()
