import wx
import wx.media
import time
import os

class MyApp(wx.App):
    def OnInit(self):
        self.frame = MyFrame()
        self.SetTopWindow(self.frame)
        return True

class MyFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, title="Window", pos = (100,150), size =(800,800))
        self.print = wx.StaticText(self, -1, 'my text', (200, 0))
        self.font1 = wx.Font(20, wx.SWISS, wx.NORMAL, wx.NORMAL, False, 'Comic Sans MS')
        self.print.SetFont(self.font1)
        self.vid = wx.media.MediaCtrl(self, style=wx.SIMPLE_BORDER)
       
        loadButton = wx.Button(self, -1, 'load', pos = (0,0),size=(100,50))
        self.Bind(wx.EVT_BUTTON, self.onLoadFile, loadButton)

        loadButton2 = wx.Button(self, -1, 'load2', pos = (0,120),size=(100,100))
        self.Show()
    def onLoadFile(self, evt):
        dlg = wx.FileDialog(self, message="Choose a media file",
                            defaultDir=os.getcwd(), defaultFile="")
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            # self.doLoadFile(path)
            self.a(path)
            self.print.SetLabelText(path)
            
        dlg.Destroy()
    def a(self, path):  
        self.vid.Load(path)
        self.vid.Create(self,-1,path,(100,100),(300,300),0,wx.EmptyString, validator=wx.DefaultValidator, name="mediaCtrl")
        self.vid.Play(1)
        print('fin')


    def doLoadFile(self, path):
        if not self.mc.Load(path):
            wx.MessageBox("Unable to load %s: Unsupported format?" % path, "ERROR", wx.ICON_ERROR | wx.OK)
        else:
            folder, filename = os.path.split(path)
            self.st_file.SetLabel('%s' % filename)
         
            self.GetSizer().Layout()
            self.slider.SetRange(0, self.mc.Length())
            self.mc.Play()
            print('len =',self.mc.Length())


if __name__ == '__main__':

    app = MyApp()
    app.MainLoop()
    

