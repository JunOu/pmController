## A GUI for the pour machine
## author: Jun
## junmse.ou@gmail.com

import wx
import serial
import time
from threading import *
# from wx.lib.pubsub import Publisher
from wx.lib.pubsub import setuparg1
from wx.lib.pubsub import pub
Publisher = pub.Publisher()

class MainWindow(wx.Frame):
    
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(400,200))
        self.CreateStatusBar() 

        # Setting up the menu.
        fileMenu = wx.Menu()
        helpMenu = wx.Menu()

        #fileMenu.AppendSeparator()
        mExit = fileMenu.Append(wx.ID_EXIT,"E&xit"," Terminate the program")
        
        #helpMenu.AppendSeparator()
        mAbout = helpMenu.Append(wx.ID_ABOUT, "&About"," Information about this program")


        # Creating the menubar.
        menuBar = wx.MenuBar()
        menuBar.Append(fileMenu,"&File")
        menuBar.Append(helpMenu,"&Help")
        self.SetMenuBar(menuBar)
        self.Show(True)
        
        # buttons
        self.pnlCOM = wx.Panel(self, -1)
        COMNO = ['2','3','4','5','6','7']
        self.stTxtCOM = wx.StaticText(self.pnlCOM,-1,label='COM',pos=(5,5))
        #self.stTxtCOMinfo = wx.StaticText(self.pnlCOM,-1,label='Note: Recommend to disconnect port before exit.',pos=(5,30))
        self.cmbCOM = wx.ComboBox(self.pnlCOM, choices=COMNO,value=COMNO[3],size=(40,-1),pos=(40,0))
        self.btn_Con = wx.Button(self.pnlCOM,-1,label='Connect',size=(80,-1),pos=(90,0))
        self.stTxtCon = wx.StaticText(self.pnlCOM,-1,label='Select a Port',pos=(180,5))
        self.pnrb = wx.Panel(self,-1)
        self.rb1 = wx.RadioButton(self.pnrb, label='Manual',pos=(5,20))
        self.rb2 = wx.RadioButton(self.pnrb, label='Replay',pos=(5,50))
        self.btn_Start = wx.Button(self,-1,label='Enter')
        self.btn_Exit = wx.Button(self,-1,label='Exit')
        
        #Bind Event
        self.Bind(wx.EVT_MENU, self.onDestroy, mExit)
        self.Bind(wx.EVT_MENU, self.onAbout, mAbout)
        self.Bind(wx.EVT_BUTTON, self.onStart, self.btn_Start)
        self.Bind(wx.EVT_BUTTON, self.onDestroy, self.btn_Exit)
        self.Bind(wx.EVT_BUTTON, self.onConnect, self.btn_Con)
        
        self.__layout()
 
    def __layout(self):
        #Layout
        sizerCOM = wx.BoxSizer(wx.HORIZONTAL)
        sizerRb = wx.BoxSizer(wx.HORIZONTAL)
        sizer0 = wx.BoxSizer(wx.VERTICAL)
        sizer0.SetMinSize((260,200))
        sizerCOM.Add(self.pnlCOM,1, wx.RIGHT)
        sizerRb.Add(self.pnrb,1,wx.EXPAND)
        sizer0.Add(sizerCOM,0,wx.EXPAND)
        sizer0.Add(sizerRb,1,wx.EXPAND)
        sizer0.Add(self.btn_Start,0,wx.EXPAND)
        sizer0.Add(self.btn_Exit,0,wx.EXPAND)
                
        self.SetSizerAndFit(sizer0)
        self.Refresh()
        self.Show()

    def onAbout(self,event):
        description="""This software is a controller for the pour macine of the Casting Group
at MTRL UBC which is designed and built by IGEN."""
        licence0 = "GPL"
        info = wx.AboutDialogInfo()
        #info.SetIcon(wx.Icon('icon_controller.ico', wx.BITMAP_TYPE_PNG))
        info.SetName('Pour Machine Controller')
        info.SetVersion('1.0')
        info.SetDescription(description)
        info.SetCopyright('(C) Casting Group')
        #info.SetWebSite('http://www.ubc.com')
        info.SetLicence(licence0)
        info.AddDeveloper('Jun Ou')
        info.AddDocWriter('Gabriel Lessard-Kragen')
        wx.AboutBox(info)

    def onStart(self,event):
        if self.rb1.GetValue()==True:
            manMode(self)
        elif self.rb2.GetValue()==True:
            repMode(self)
        else:
            self.errDial = wx.MessageDialog(None, 'Please choose the mode to enter.', 'Error!', 
            wx.OK | wx.ICON_ERROR)
            self.errDial.ShowModal()
        
    def onConnect(self,event):
        comIndex = int(self.cmbCOM.GetValue())-1
        global ser
        try:
            ser = serial.Serial(comIndex, timeout=1)
            self.stTxtCon.SetLabel("Connected!")
            self.btn_Con.SetLabel('Disconnect')
        except:
            self.stTxtCon.SetLabel("Not Connected!")
            self.btn_Con.SetLabel('Connect')
            try:
                ser
                ser.close()
            except:
                pass
            
    def onDestroy(self,event):
        try:
            ser
            if ser.isOpen()==True:
                ser.close()
        except:
            pass
        self.Destroy()

        
class manMode(wx.Dialog):
    
    def __init__(self, *args, **kw):
        super(manMode, self).__init__(*args, **kw)            

        self.SetSize((600, 400))
        self.SetTitle("Manual Operation Mode")

        self.txtCommand = wx.TextCtrl(self,-1,style= wx.TE_MULTILINE | wx.SUNKEN_BORDER)
        self.btn_Save = wx.Button(self,-1,'Save')
        self.btn_ActM = wx.Button(self,-1,'Activate')
        self.btn_StpM = wx.Button(self,-1,'Stop')
        self.btn_manQuit = wx.Button(self,-1,'Quit')

        #Bind
        self.Bind(wx.EVT_BUTTON, self.onManQuit, self.btn_manQuit)
        self.Bind(wx.EVT_BUTTON, self.onSaveFile, self.btn_Save)
        self.Bind(wx.EVT_BUTTON, self.onActivateM, self.btn_ActM)
        self.Bind(wx.EVT_BUTTON, self.onStopM, self.btn_StpM)


        Publisher.subscribe(self.writeText, ("arduino.data"))

        # ----------Thread---------------
        # Indicate we aren't working on it yet
        self.working = 0
        # And indicate we don't have a worker thread yet
        self.worker = None
        
        self.__layout()        
        
    def __layout(self):

        self.sizerBtn = wx.BoxSizer(wx.HORIZONTAL)
        self.sizerBase = wx.BoxSizer(wx.VERTICAL)
        self.sizerBtn.Add(self.btn_Save,0,wx.EXPAND)
        self.sizerBtn.Add(self.btn_ActM,0,wx.EXPAND)
        self.sizerBtn.Add(self.btn_StpM,0,wx.EXPAND)
        self.sizerBtn.Add(self.btn_manQuit,0,wx.EXPAND)
        self.sizerBase.Add(self.txtCommand,1,wx.EXPAND)
        self.sizerBase.Add(self.sizerBtn,0,wx.EXPAND)
        self.SetSizer(self.sizerBase)
        self.ShowModal()

    def writeText(self,rc):
        self.txtCommand.AppendText(rc.data)
        
    def onManQuit(self,event):
        self.btn_ActM.Enable()
        if self.worker:
            self.worker.abort()
            self.worker = None # this tell the worker is done
        try:
            ser
            if ser.isOpen()==True:
                ser.write('s')
        except:
            pass
        self.Close()

    def onActivateM(self,event):
        try:
            ser
            if ser.isOpen()==True:
                self.btn_ActM.Disable()
                ser.flushInput()
                ser.write('g')
                if not self.worker:
                    self.worker = WorkerThread(self)
            else:
                portError(self,'A error related to the port connection happens.')            
        except:
            portError(self,'A error related to the port connection happens.')
                    
    def onStopM(self,event):
        self.btn_ActM.Enable()
        if self.worker:
            self.worker.abort()
            self.worker = None # this tell the worker is done
        try:
            ser
            if ser.isOpen()==True:
                ser.write('s')
        except:
            portError(self,'A error related to the port connection happens.')

    def onSaveFile(self,event):
        """   Browse for file         """
        wildcard = "Text files (*.txt)|*.txt|Data files (*.dat)|*.dat|All files (*.*)|*.*"
        dialog = wx.FileDialog(None, "Choose a command file",
                               wildcard=wildcard,
                               style=wx.SAVE|wx.OVERWRITE_PROMPT)
        if dialog.ShowModal() == wx.ID_OK:
            f2 = open(dialog.GetPath(),'w')
            f2.write(self.txtCommand.GetValue())
            f2.close()
            dialog.Destroy() 
        else:
            pass
        
class repMode(wx.Dialog):
    
    def __init__(self, *args, **kw):
        super(repMode, self).__init__(*args, **kw) 

        self.SetSize((600, 400))
        self.SetTitle("Replay Mode")

        self.txtCommand = wx.TextCtrl(self,-1,style= wx.TE_MULTILINE | wx.SUNKEN_BORDER)
        self.txtctrlPath = wx.TextCtrl(self,-1)
        self.btn_open = wx.Button(self,-1,'Open')
        self.btn_upload = wx.Button(self,-1,'UpLoad')
        self.btn_repQuit = wx.Button(self,-1,'Quit')

        #Bind
        self.Bind(wx.EVT_BUTTON, self.onRepQuit, self.btn_repQuit)
        self.Bind(wx.EVT_BUTTON, self.onOpenFile, self.btn_open)
        self.Bind(wx.EVT_BUTTON, self.onUpload, self.btn_upload)
        
        self.__layout()        
        
    def __layout(self):
        self.sizerBtn = wx.BoxSizer(wx.HORIZONTAL)
        self.sizerBase = wx.BoxSizer(wx.VERTICAL)
        self.sizerBtn.Add(self.txtctrlPath,1,wx.EXPAND)
        self.sizerBtn.Add(self.btn_open,0,wx.EXPAND)
        self.sizerBtn.Add(self.btn_upload,0,wx.EXPAND)
        self.sizerBtn.Add(self.btn_repQuit,0,wx.EXPAND)
        self.sizerBase.Add(self.txtCommand,1,wx.EXPAND)
        self.sizerBase.Add(self.sizerBtn,0,wx.EXPAND)
        self.SetSizer(self.sizerBase)
        self.ShowModal()

    def onRepQuit(self,event):
        try:
            ser
            if ser.isOpen()==True:
                ser.write(s)
        except:
            pass
        self.Close()

    def onOpenFile(self,event):
        """   Browse for file         """
        wildcard = "Text files (*.txt)|*.txt|Data files (*.dat)|*.dat|All files (*.*)|*.*"
        dialog = wx.FileDialog(None, "Choose a command file",
                               wildcard=wildcard,
                               style=wx.OPEN)
        if dialog.ShowModal() == wx.ID_OK:
            self.txtctrlPath.SetValue(dialog.GetPath())
            f1 = open(dialog.GetPath(),'r')
            lines1 = f1.read()
            self.txtCommand.AppendText(lines1)
            dialog.Destroy() 
        else:
            pass

    def onUpload(self,event):
        try:
            ser
            if ser.isOpen()==True:
                time.sleep(0.5)
                ser.write('r')
                for i in range(self.txtCommand.GetNumberOfLines()):
                    time.sleep(0.5)
                    ser.write(self.txtCommand.GetLineText(i))
                time.sleep(0.5)
                ser.write("QUIT")
                self.dial = wx.MessageDialog(None, 'Upload Finished! The Machine is Running!', 'Finished!', 
                wx.OK | wx.ICON_INFORMATION)
                self.dial.ShowModal()
            else:
                portError(self,'A error related to the port connection happens.')
        except:
            portError(self,'A error related to the port connection happens.')
            
##-------------Another-Thread----------------
        # Thread class that executes processing
class WorkerThread(Thread):
    """Worker Thread Class."""
    def __init__(self, notify_window):
        """Init Worker Thread Class."""
        Thread.__init__(self)
        self._notify_window = notify_window
        self._want_abort = 0
        # This starts the thread running on creation, but you could
        # also make the GUI thread responsible for calling this
        self.start()

    def run(self):
        """Run Worker Thread."""
        # This is the code executing in the new thread.
        while True:
            rc = ser.readline()
            if rc!="":
                Publisher.sendMessage(("arduino.data"),rc)
            if self._want_abort:
                return

    def abort(self):
        """abort worker thread."""
        # Method for use by main thread to signal an abort
        self._want_abort = 1        

def portError(self,errorinfo):
    self.dial = wx.MessageDialog(None, errorinfo, 'ERROR!', 
    wx.OK | wx.ICON_ERROR)
    self.dial.ShowModal()

    
if __name__=='__main__':
    app = wx.PySimpleApp()
    frame = MainWindow(None, title='Pour Machine')
    frame.Show(True)
    app.MainLoop()
