# Started with wxPython demo for AUI MDI child windows

TRACE_EVENTS = False

import wx
import wx.aui

import wx.lib.inspection

def event_trace(window,title):
    if not TRACE_EVENTS: return
    import inspect
    exclude = ('EVT_COMMAND', 'EVT_COMMAND_RANGE',
               'EVT_IDLE',
               'EVT_UPDATE_UI', 'EVT_UPDATE_UI_RANGE')
    events = [(name,evt)
              for name,evt in inspect.getmembers(wx)
              if name.startswith('EVT_') and name not in exclude]
    def binder(name,evt):
        def callback(evt):
            try: obj = evt.GetObject()
            except: obj = None
            try: id = evt.GetId()
            except: id = None
            print "event", title, name, "object",obj, id
            evt.Skip()
        return callback
    for name,evt in events:
        window.Bind(evt, binder(name, evt))

#----------------------------------------------------------------------


class ParentFrame(wx.Frame):
    def __init__(self, parent, id=-1, title="", pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=wx.DEFAULT_FRAME_STYLE |
                                            wx.SUNKEN_BORDER |
                                            wx.CLIP_CHILDREN):

        wx.Frame.__init__(self, parent, id, title, pos, size, style)
        self.aui = wx.aui.AuiManager()
        self.aui.SetManagedWindow(self)
        data1 = wx.TextCtrl(self, -1, "This is some text",
                              style=wx.NO_BORDER | wx.TE_MULTILINE)
        data2 = wx.TextCtrl(self, -1, "This is some more text",
                              style=wx.NO_BORDER | wx.TE_MULTILINE)
        data3 = wx.TextCtrl(self, -1, "This is text 3",
                              style=wx.NO_BORDER | wx.TE_MULTILINE)
        self.aui.AddPane(data1, wx.aui.AuiPaneInfo().
                            CloseButton(True).
                            Name('data1').Caption("Data 1").
                            Top(). MaximizeButton(True))
        self.aui.AddPane(data2, wx.aui.AuiPaneInfo().
                            CloseButton(True).
                            Name('data2').Caption("Data 2").
                            Left())
        self.aui.AddPane(data3, wx.aui.AuiPaneInfo().
                            CloseButton(True).
                            Name('data3').Caption("Data 3").
                            Left())
        self.aui.Update()

#----------------------------------------------------------------------

class DemoApp(wx.App):
    def OnInit(self):
        self.frame = ParentFrame(None)
        self.frame.Show()
        self.SetTopWindow(self.frame)
        return True

def main():
    app = DemoApp(redirect=False)
    wx.lib.inspection.InspectionTool().Show()
    app.MainLoop()

if __name__ == "__main__": main()