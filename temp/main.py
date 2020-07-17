import wx
import wx.media
import os
import cv2
import time 
import math
import numpy as np
import matplotlib.pyplot as plt
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
        
        stopButton = wx.Button(self, -1, "Clear")
        self.Bind(wx.EVT_BUTTON, self.onStop, stopButton)

        self.pickcen = wx.Button(self, -1, "Pick Center")
        self.Bind(wx.EVT_BUTTON, self.pick_cen, self.pickcen)

        self.status = wx.StaticText(self, -1, "pls choose a vid", size=(200,-1))
      
        
        # setup the button/label layout using a sizer
        sizer = wx.GridBagSizer(2,5)
        sizer.Add(loadButton, (2,1))
        sizer.Add(self.playButton, (2,2))
        sizer.Add(self.slowButton, (2,3))
        sizer.Add(stopButton, (2,4))
        sizer.Add(self.pickcen, (2,5))
        sizer.Add(self.status, (1,1), span=(1,5))
        self.SetSizer(sizer)
       
        self.timer = wx.Timer(self)
        #self.Bind(wx.EVT_TIMER, self.onTimer)
        self.timer.Start(100)
        self.im_i = 0
        self.lastframe = 1
        self.im = wx.StaticBitmap(self, -1, wx.Bitmap('a.bmp'), pos=(15,70),
               size=(500,200), style=2)
        self.pause = True
        self.pause2 = True
        
        self.im.Bind(wx.EVT_LEFT_DOWN, self.on_clic)
        self.point = []
        self.point_ = []
        self.mode_cen = False
        self.cen_x, self.cen_y  = -1, -1
        self.lock = False
        self.pointandi = []
    def crop(self):
        up = self.cen_y
        down = self.y - self.cen_y
        left = self.cen_x
        right = self.x - self.cen_x
        self.rad = min(up, down, left, right)

        ze = np.zeros(self.vid[0].shape)
        y, x, col = np.where(ze==0)
        r2 = self.rad**2
        mask = (x-self.cen_x)**2 + (y-self.cen_y)**2  < r2
        self.mask = mask.reshape(self.vid[0].shape)

        self.vid_ = []
        for i in range(self.vid.shape[0]):
            self.vid_.append(self.vid[i]*self.mask)
            self.status.SetLabelText('calculating... '+str(i)+'/'+str(self.vid.shape[0]))
        self.vid = np.array(self.vid_)
        self.status.SetLabelText('cropped vid')
        # np.save('vid',self.vid)
        # np.save('cen',(self.cen_x,self.cen_y,self.rad))

    def drawcir(self):
        self.dc = wx.MemoryDC(self.bit)
        self.dc.SetBrush(wx.Brush((255,0,0)))
        self.dc.DrawCircle(self.cen_x,self.cen_y,4)
        self.dc.SetPen(wx.Pen("black"))
        self.dc.SetBrush(wx.Brush("grey",style=wx.TRANSPARENT))
        self.dc.DrawCircle(self.cen_x,self.cen_y,self.rad-1)
        self.dc.SelectObject(wx.NullBitmap)
        self.im.SetBitmap(self.bit)

    def rotate(self):
        #find rotate dir
        def angle(a, c, b = [self.cen_x, self.cen_y] ):
            ang = math.degrees(math.atan2(c[1]-b[1], c[0]-b[0]) - math.atan2(a[1]-b[1], a[0]-b[0]) )
            return abs(ang)
        found = 0
        oneframeang = []
        for i in range(len(self.pointandi)):
            if found == 0:
                if self.pointandi[i][0] > self.cen_y and self.pointandi[i][0] > self.cen_y: #upper part of circle
                    if self.pointandi[i][0] < self.pointandi[i][1]:
                        first_point_x = self.point[i][0][0]
                        sec_point_x = self.point[i][1][0]
                    else :
                        first_point_x = self.point[i][1][0]
                        sec_point_x = self.point[i][0][0]

                    self.rotate_dir = 'clock' if first_point_x < sec_point_x else 'reverse'
                    found = 1

                elif self.pointandi[i][0] < self.cen_y and self.pointandi[i][0] < self.cen_y: #lower part of circle
                    if self.pointandi[i][0] > self.pointandi[i][1]:
                        first_point_x = self.point[i][0][0]
                        sec_point_x = self.point[i][1][0]
                    else :
                        first_point_x = self.point[i][1][0]
                        sec_point_x = self.point[i][0][0]

                    self.rotate_dir = 'clock' if first_point_x > sec_point_x else 'reverse'
                    found = 1

            n_frame = abs(self.pointandi[i][0] - self.pointandi[i][1])
            print('len=',len(self.pointandi), len(self.point))
            print(self.pointandi[i][0],self.pointandi[i][1])
            p1 = self.point[i][0]
            p2 = self.point[i][1]
            ang = angle(p1, p2)
            if n_frame <= 0 : continue
            oneframeang_ = ang/n_frame
            oneframeang.append(oneframeang_)
        f_min = min(oneframeang)
        f_max = max(oneframeang)
        print('min,max = ',f_min, f_max)

        self.vid_r = []
        self.n_scan = 4
        dura = int(f_max*15/(f_min/self.n_scan))

        self.frame_step = 10
        start = 0
        st = 0
        ang_start = 0
        for ii in range(self.vid.shape[0]//self.frame_step):
            for iii in range(self.frame_step):
                if start+iii+1 >= self.vid.shape[0]: break
                self.vid_r_ = []
                start = st
                ck = start+iii+1
                # print('start,ck=',start,',',ck)
                # print('dura=',dura)
                for i in range(dura):
                    if i==0: continue
                    M = cv2.getRotationMatrix2D((self.cen_x,self.cen_y), i*f_min/self.n_scan , 1)
                    im_r = cv2.warpAffine(self.vid[ck], M, (self.vid.shape[2], self.vid.shape[1]))
                    self.vid_r_.append(im_r)
                loss = []
                for j in range(len(self.vid_r_)): 
                    loss.append(((self.vid[start]-self.vid_r_[j])**2).sum())
                np.save('loss/'+str(ck),loss)
               
                #plt.plot(loss)
                #plt.show()
                if ang_start != 0:
                    M = cv2.getRotationMatrix2D((self.cen_x,self.cen_y), ang_start , 1)
                    im_r = cv2.warpAffine(self.vid_r_[np.argmin(loss)], M, (self.vid.shape[2], self.vid.shape[1]))
                    self.vid_r.append(im_r)
                else: self.vid_r.append(self.vid_r_[np.argmin(loss)])
                self.status.SetLabelText('analyzing... %d/%d'%(ck, self.vid.shape[0]))
            ang_start += np.argmin(loss)*f_min/self.n_scan
            st = ck
        self.vid = np.array(self.vid_r)
        self.updateim(0)
        self.status.SetLabelText('done!')

    def pick_cen(self, evt):
        if len(self.point) <2:
            self.status.SetLabelText('get more than 2 line before select center point')
        if len(self.point) >= 2:
            self.mode_cen = True
            self.pause = True
            self.pause2 = True
            self.playButton.SetLabelText('Play')
            self.slowButton.SetLabelText('Play Slow')
            self.status.SetLabelText('pick your center point')
        if self.mode_cen == True and self.cen_x != -1:
            self.crop()
            self.status.SetLabelText('center point saved')
            self.lock = True
            self.bit = wx.Bitmap.FromBuffer(self.x, self.y, self.vid[self.im_i]) #reset cen
            self.dc = wx.MemoryDC(self.bit)
            self.dc.SetBrush(wx.Brush((255,0,0)))
            self.dc.DrawCircle(self.cen_x,self.cen_y,4)
            self.dc.SetPen(wx.Pen("black"))
            self.dc.SetBrush(wx.Brush("grey",style=wx.TRANSPARENT))
            self.crop()
            self.dc.DrawCircle(self.cen_x,self.cen_y,self.rad)
            self.dc.SelectObject(wx.NullBitmap)
            self.rotate()
            self.im.SetBitmap(self.bit)
            

    def on_clic(self, evt):
        if not self.lock:
            if self.mode_cen == True:
                self.cen_x, self.cen_y = evt.GetPosition()
                self.bit = wx.Bitmap.FromBuffer(self.x, self.y, self.vid[self.im_i]) #reset cen
                self.dc = wx.MemoryDC(self.bit)
                self.dc.SetBrush(wx.Brush((0,255,0)))
                self.drawpoint()
                self.dc.SetBrush(wx.Brush((255,0,0)))
                self.dc.DrawCircle(self.cen_x,self.cen_y,4)
                self.dc.SelectObject(wx.NullBitmap)
                self.im.SetBitmap(self.bit)
                self.status.SetLabelText('click at "Pick Center" to confirm this center point')
    
            else:
                self.dx, self.dy = evt.GetPosition()
                
                self.point_.append([self.dx, self.dy])
                if len(self.point_) == 2:
                    self.pointandi.append([self.im_i_, self.im_i])
                    self.point.append(self.point_)
                    self.point_ = []
                    self.status.SetLabelText('you can add more tracking point to increase precision')
                    
                elif self.point_ != []:
                    self.im_i_ = self.im_i
                    self.status.SetLabelText('track this point')
                    #self.onPlay_(evt)
                else:
                    
                    self.pause = True
                    self.pause2 = True
                    self.playButton.SetLabelText('Play')
                    self.slowButton.SetLabelText('Play Slow')
                self.drawbit()

    def drawbit(self):
        self.dc = wx.MemoryDC(self.bit)
        self.dc.SetBrush(wx.Brush((0,255,0)))
        if not self.lock:
            self.drawpoint()
        if self.cen_x != -1:
            self.dc.SetBrush(wx.Brush((255,0,0)))
            self.dc.DrawCircle(self.cen_x,self.cen_y,4)
        self.dc.SelectObject(wx.NullBitmap)
        self.im.SetBitmap(self.bit)

    def drawpoint(self):
        def line(p1, p2):
            A = (p1[1] - p2[1])
            B = (p2[0] - p1[0])
            C = (p1[0]*p2[1] - p2[0]*p1[1])
            return A, B, -C
        def intersection(L1, L2):
            D  = L1[0] * L2[1] - L1[1] * L2[0]
            Dx = L1[2] * L2[1] - L1[1] * L2[2]
            Dy = L1[0] * L2[2] - L1[2] * L2[0]
            if D != 0:
                x = Dx / D
                y = Dy / D
                return x,y
            else:
                return False
        for i in range(len(self.point)):
            if len(self.point[i]) == 2:
                p1, p2 = self.point[i]
                self.dc.DrawCircle(p1[0],p1[1],3)
                self.dc.DrawCircle(p2[0],p2[1],3)
                self.dc.DrawLine(p1[0],p1[1],p2[0],p2[1])
                m = (p2[0]-p1[0])/(p2[1]-p1[1]+1e-10)*-1          # y = mx + c , m = y/x
                x, y = (p1[0]+p2[0])/2 , (p1[1]+p2[1])/2    # center point
                #self.dc.DrawCircle(x,y,3)
                c = (m*x-y )*-1       
                x1 = -100
                x2 = 600
                y1 = m*x1+c
                y2 = m*x2+c
                if y1 > 1e10: #special case -> m = infinity
                    y1 = -100
                    y2 = 600
                    x1 = (y1-c )/m
                    x2 = (y2-c )/m
                self.dc.DrawLine(x1,y1,x2,y2)
                
        if len(self.point_)==1:
            self.dc.DrawCircle(self.point_[0][0],self.point_[0][1],3)

        
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
        self.vid = np.array(self.vid)
        cap.release()
        cv2.destroyAllWindows()
        
        slider = wx.Slider(self, 5, 0, 0, len(self.vid)-1, pos=(15,520),size=(600,20))
        self.slider = slider
        self.Bind(wx.EVT_SLIDER, self.onSeek, slider)
        self.lastframe = len(self.vid)-1
        self.im.SetSize(20,20)
        self.updateim(0)
        self.status.SetLabelText('track a point to find center point')
                
    def updateim(self, i):
        #if self.im_i < self.lastframe:
        self.bit = wx.Bitmap.FromBuffer(self.x, self.y, self.vid[i])
        self.im.SetBitmap(self.bit)
        self.drawbit()
        if self.lock:
            self.drawcir()
      
        
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
            if i >= self.lastframe:
                self.pause = True
                self.playButton.SetLabelText('Play')
                self.im_i = 0
                self.slider.SetValue(self.im_i)
                break
            key = cv2.waitKey(1)
    def onPlay_(self, evt):
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
        t_end = t0
        secch = 0.05/self.fps
        while t0-t_end < 0.1:
            if self.pause == True:
                break
            tm = time.time()-t0
            if tm >= secch and i<self.lastframe:
                i+=1
                t0 = time.time()
                self.im_i = i
                self.slider.SetValue(i)
                self.updateim(i)
            if i >= self.lastframe:
                self.pause = True
                self.playButton.SetLabelText('Play')
                self.im_i = 0
                self.slider.SetValue(self.im_i)
                break
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
            if i >= self.lastframe:
                self.pause2 = True
                self.slowButton.SetLabelText('Play Slow')
                self.im_i = 0
                self.slider.SetValue(self.im_i)
                break  
            key = cv2.waitKey(1)
    
    def onStop(self, evt):
        self.im_i = 0
        self.slider.SetValue(self.im_i)
        self.pause = True
        self.pause2 = True
        self.mode_cen = False
        self.lock = False
        self.playButton.SetLabelText('Play')
        self.slowButton.SetLabelText('Play Slow')
        self.status.SetLabelText('cleared, track a new point')
        self.point = []
        self.point_ = []
        self.cen_x, self.cen_y = -1, -1
        self.rad = 0
        self.updateim(self.im_i)
    
    def onSeek(self, evt):
        offset = self.slider.GetValue()
        self.updateim(offset)
        if self.lock:
            self.drawcir()
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
