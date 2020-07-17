import wx
import wx.media
import os
import cv2
import time 
class Panel1(wx.Panel):
    def __init__(self, parent, id):
        #self.log = log
        wx.Panel.__init__(self, parent, -1
                , style=wx.TAB_TRAVERSAL|wx.CLIP_CHILDREN )
        # Create some controls
        
        loadButton = wx.Button(self, -1, "Load File")
        self.Bind(wx.EVT_BUTTON, self.onLoadFile, loadButton)
        
        self.playButton = wx.Button(self, -1, "Play")
        self.Bind(wx.EVT_BUTTON, self.onPlay, self.playButton)
      
        self.slowButton = wx.Button(self, -1, "Play Slow")
        self.Bind(wx.EVT_BUTTON, self.onSlow, self.slowButton)
        
        stopButton = wx.Button(self, -1, "Stop")
        self.Bind(wx.EVT_BUTTON, self.onStop, stopButton)

        self.st_file = wx.StaticText(self, -1, ".mp4", size=(200,-1))
        self.st_size = wx.StaticText(self, -1, size=(100,-1))
        self.st_len  = wx.StaticText(self, -1, size=(100,-1))
        self.st_pos  = wx.StaticText(self, -1, size=(100,-1))
        
        # setup the button/label layout using a sizer
        sizer = wx.GridBagSizer(1,5)
        sizer.Add(loadButton, (1,1))
        sizer.Add(self.playButton, (1,2))
        sizer.Add(self.slowButton, (1,3))
        sizer.Add(stopButton, (1,4))
        self.SetSizer(sizer)
       
        self.timer = wx.Timer(self)
        #self.Bind(wx.EVT_TIMER, self.onTimer)
        self.timer.Start(100)
        self.im_i = 0
        self.lastframe = 1
        self.im = wx.StaticBitmap(self, -1, wx.Bitmap('a.bmp'), pos=(15,55),
               size=(500,200), style=2)
        self.pause = True
        self.pause2 = True
        
        
        self.im.Bind(wx.EVT_LEFT_DOWN, self.on_clic)
        self.point = []
        self.point_ = []
        

    def on_clic(self, evt):
        self.dx, self.dy = evt.GetPosition()
        self.point_.append([self.dx, self.dy])
        if len(self.point_) == 2:
            self.point.append(self.point_)
            self.point_ = []
        self.dc = wx.MemoryDC(self.bit)
        self.dc.SetBrush(wx.Brush((255,0,0)))
        self.drawpoint()
        self.dc.SelectObject(wx.NullBitmap)
        self.im.SetBitmap(self.bit)

    def drawpoint(self):
        print('in draw')
        for i in range(len(self.point)):
            if len(self.point[i]) == 2:
                p1, p2 = self.point[i]
                self.dc.DrawCircle(p1[0],p1[1],5)
                self.dc.DrawCircle(p2[0],p2[1],5)
                self.dc.DrawLine(p1[0],p1[1],p2[0],p2[1])
        if len(self.point_)==1:
            self.dc.DrawCircle(self.point_[0][0],self.point_[0][1],5)

        
    def onLoadFile(self, evt):
        dlg = wx.FileDialog(self, message="Choose a media file",
                            defaultDir=os.getcwd(), defaultFile="")
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.doLoadFile(path)
        dlg.Destroy()
        
    def doLoadFile(self, path):
        cap = cv2.VideoCapture(path)
        i=0
        self.fps = cap.get(cv2.CAP_PROP_FPS)
        _, frame = cap.read()
        x = frame.shape[1]
        y = frame.shape[0]
        size = 600
        if x>y:
            y = y/x*size
            x = size
        else:
            x = x/y*size
            y = size
        self.x = int(x)
        self.y = int(y)
        self.vid = []
        while 1:
            _, frame = cap.read()
            if not _:
                break
            frame_res = cv2.resize(frame, (self.x,self.y))
            self.vid.append(frame_res)
            cv2.putText(frame, 'loading video', (100,100), cv2.FONT_HERSHEY_SIMPLEX 
                    ,1, (0,255,0), 2, cv2.LINE_AA)
            cv2.imshow('loading...',frame)
            key = cv2.waitKey(1)
            if key == 27:
                break
        cap.release()
        cv2.destroyAllWindows()
        
        slider = wx.Slider(self, 5, 0, 0, len(self.vid)-1, pos=(15,520),size=(600,20))
        self.slider = slider
        self.Bind(wx.EVT_SLIDER, self.onSeek, slider)
        self.lastframe = len(self.vid)-1
        self.im.SetSize(20,20)
        self.updateim(0)
                
    def updateim(self, i):
        #if self.im_i < self.lastframe:
        self.bit = wx.Bitmap.FromBuffer(self.x, self.y, self.vid[i])
        self.im.SetBitmap(self.bit)
        
    def onPlay(self, evt):
        if self.pause: #play
            self.pause = False
            self.playButton.SetLabelText('Pause')
            if self.pause2 == False:
                self.pause2 = True
                self.slowButton.SetLabelText('Play Slow')
        else: #pause
            self.pause = True
            self.playButton.SetLabelText('Play')
        i = self.im_i
        t0 = time.time()
        secch = 1/self.fps
        while True:
            if self.pause == True:
                break
            tm = time.time()-t0
            if tm >= secch and i<self.lastframe:
                i+=1
                t0 = time.time()
                self.im_i = i
                self.slider.SetValue(i)
                
                self.updateim(i)
                
            key = cv2.waitKey(1)
    def onSlow(self, evt):
        if self.pause2:
            self.pause2 = False
            self.slowButton.SetLabelText('Pause')
            if self.pause == False:
                self.pause = True
                self.playButton.SetLabelText('Play')
        else:
            self.pause2 = True
            self.slowButton.SetLabelText('Play Slow')
        i = self.im_i
        t0 = time.time()
        secch = 4/self.fps
        while True:
            if self.pause2 == True:
                break
            tm = time.time()-t0
            if tm >= secch and i<self.lastframe:
                i+=1
                t0 = time.time()
                self.im_i = i
                self.slider.SetValue(i)
                self.updateim(i)
                
            key = cv2.waitKey(1)
    
    def onStop(self, evt):
        self.im_i = 0
        self.slider.SetValue(self.im_i)
        self.updateim(self.im_i)
        self.pause = True
        self.pause2 = True
        self.playButton.SetLabelText('Play')
        self.slowButton.SetLabelText('Play Slow')
    
    def onSeek(self, evt):
        offset = self.slider.GetValue()
        self.updateim(offset)
        self.im_i = offset
        self.pause = True
        self.pause2 = True
        self.playButton.SetLabelText('Play')
        self.slowButton.SetLabelText('Play Slow')


if __name__ == '__main__':
    app = wx.PySimpleApp()
    # create a window/frame, no parent, -1 is default ID
    frame = wx.Frame(None, -1, "SKYs @dev4geo", size = (1150, 600),pos=(10,10))
    # call the derived class
    Panel1(frame, -1)
    frame.Show(1)
    app.MainLoop()