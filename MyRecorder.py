from tkinter import *
from tkinter import filedialog as fld
from PIL import Image,ImageGrab,ImageTk
from threading import Thread
import time
import cv2
import numpy as np
class Selector:
    def __init__(self,master,callback):
        self.master = master
        self.callback = callback
        self.width,self.height = master.winfo_screenwidth(),\
                                 master.winfo_screenheight()
    def select(self):
        self.tl = Toplevel(self.master)
        self.cv = Canvas(self.tl,width=self.width,height=self.height)
        self.cv.pack()
        self.img = ImageTk.PhotoImage(image=ImageGrab.grab())
        self.cv.create_image(self.width//2,self.height//2,image=self.img)
        self.cv.bind("<Button-1>",self.press)
        self.cv.bind("<ButtonRelease-1>",self.release)
        self.tl.overrideredirect(True)
    def get_rect(self,a,b):
        return (min(a[0],b[0]),min(a[1],b[1]),max(a[0],b[0]),max(a[1],b[1]))
    def press(self,event):
        self.start_pos = (event.x,event.y)
    def release(self,event):
        self.tl.destroy()
        self.callback(self.get_rect(self.start_pos,(event.x,event.y)))
class Recorder:
    FPS = 20
    def __init__(self):
        self.is_videoing = False
    def start_record(self,rect,name):
        self.filename = name
        self.rect = rect
        self.is_videoing = True
        self.start_time = self.pre_time = time.perf_counter()
        fourcc = cv2.VideoWriter.fourcc("X",'V','I','D')
        self.video_file = cv2.VideoWriter(name,fourcc,self.FPS,\
                                      (rect[2]-rect[0],rect[3]-rect[1]))
        Thread(target=self.record_video).start()
    def record_video(self):
        while self.is_videoing:
            if time.perf_counter() - self.pre_time >= 1/self.FPS:
                self.pre_time = time.perf_counter()
                img = ImageGrab.grab(self.rect)
                newimg = cv2.cvtColor(np.array(img),cv2.COLOR_RGB2BGR)
                self.video_file.write(newimg)
        print(time.perf_counter()-self.start_time)
        self.video_file.release()
    def pause(self):
        self.is_videoing = False
class App:
    def __init__(self,master):
        self.master = master
        self.width,self.height = master.winfo_screenwidth(),\
                                 master.winfo_screenheight()
        self.initwidgets()
    def initwidgets(self):
        self.recorder = Recorder()
        self.selector = Selector(self.master,self.start_video)
        self.bt1 = Button(self.master,text="开始",command=self.selector.select)
        self.bt1.pack(side=LEFT,ipadx=50,padx=20)
        self.bt2 = Button(self.master,text="结束",command=self.pause)
        self.bt2["state"] = DISABLED
        self.bt2.pack(side=LEFT,ipadx=50,padx=20)
    def start_video(self,rect):
        filename = fld.asksaveasfilename(title="输入保存文件名",\
                    filetypes=[("视频文件","*.avi")],defaultextension=".avi")
        self.bt1["state"] = DISABLED
        self.bt2["state"] = NORMAL
        self.recorder.start_record(rect,filename)
    def pause(self):
        self.recorder.pause()
        self.bt1["state"] = NORMAL
        self.bt2["state"] = DISABLED
root = Tk()
app = App(root)
root.title("MyRecorder")
root.mainloop()
