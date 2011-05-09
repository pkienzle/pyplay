# Started with wxPython demo for AUI MDI child windows

TRACE_EVENTS = False

import wx
import wx.aui

from wx.aui import AuiNotebook
# floating pages doesn't work well on Windows; use an alternate technique
#from auinotebookwithfloatingpages import AuiNotebookWithFloatingPages as AuiNotebook


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
    events += [(name, evt)
               for name,evt in inspect.getmembers(wx.aui)
               if name.startswith('EVT_')]
    print "events",[k for k,v in events]
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
        self.aui = AuiNotebook(self)

        data1 = wx.TextCtrl(self, -1, "This is some text",
                              style=wx.NO_BORDER | wx.TE_MULTILINE)
        data2 = wx.TextCtrl(self, -1, "This is some more text",
                              style=wx.NO_BORDER | wx.TE_MULTILINE)
        data3 = wx.TextCtrl(self, -1, "This is text 3",
                              style=wx.NO_BORDER | wx.TE_MULTILINE)
        self.aui.AddPage(data1, "Data 1")
        self.aui.AddPage(data2, "Data 2")
        self.aui.AddPage(data3, "Data 3")
        event_trace(self.aui, "aui")

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.aui, 1, wx.EXPAND)
        self.SetSizer(sizer)
        self.Layout()
        self.aui.Split(0, wx.TOP)

        self.Bind(wx.aui.EVT_AUINOTEBOOK_PAGE_CLOSE, self.OnPageClose, self.aui)

    def OnPageClose(self, evt):
        print "Closing"

    def SavePerspective(self):
        return self.aui.GetAuiManager().SavePerspective()

    def RestorePerspective(self, p):
        self.aui.GetAuiManager().LoadPerspective(p)

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
