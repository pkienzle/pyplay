# Started with wxPython demo for AUI MDI child windows

import wx
import wx.aui

import wx.py.shell
import wx.lib.inspection

import inspect
def event_trace(window,title):
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


class ParentFrame(wx.aui.AuiMDIParentFrame):
    def __init__(self, parent):
        wx.aui.AuiMDIParentFrame.__init__(self, parent, -1,
                                          title="AuiMDIParentFrame",
                                          size=(640,480),
                                          style=wx.DEFAULT_FRAME_STYLE)
        self.count = 0
        mb = self.MakeMenuBar()
        self.SetMenuBar(mb)
        self.CreateStatusBar()

    def MakeMenuBar(self):
        mb = wx.MenuBar()
        menu = wx.Menu()
        item = menu.Append(-1, "New child window\tCtrl-N")
        self.Bind(wx.EVT_MENU, self.OnNewChild, item)
        item = menu.Append(-1, "Close parent")
        self.Bind(wx.EVT_MENU, self.OnDoClose, item)
        mb.Append(menu, "&File")
        return mb

    def OnNewChild(self, evt):
        self.count += 1
        child = ChildFrame(self, self.count)
        child.Show()

    def OnDoClose(self, evt):
        self.Close()


#----------------------------------------------------------------------

class ChildFrame(wx.aui.AuiMDIChildFrame):
    def __init__(self, parent, count):
        wx.aui.AuiMDIChildFrame.__init__(self, parent, -1,
                                         title="Child: %d" % count)
        mb = parent.MakeMenuBar()
        menu = wx.Menu()
        item = menu.Append(-1, "This is child %d's menu" % count)
        mb.Append(menu, "&Child")
        self.SetMenuBar(mb)

        p = wx.Panel(self)
        wx.StaticText(p, -1, "This is child %d" % count, (10,10))
        p.SetBackgroundColour('light blue')

        sizer = wx.BoxSizer()
        sizer.Add(p, 1, wx.EXPAND)
        self.SetSizer(sizer)

        wx.CallAfter(self.Layout)
        event_trace(self, "Child %d"%count)

#----------------------------------------------------------------------

class DemoApp(wx.App):
    def OnInit(self):
        frame = ParentFrame(None)
        frame.Show()
        self.SetTopWindow(frame)
        console = wx.py.shell.ShellFrame(None, locals=dict(app=self,frame=frame))
        console.Show()
        wx.lib.inspection.InspectionTool().Show()
        event_trace(frame,"MDI parent")
        return True

def main():
    app = DemoApp()
    app.MainLoop()

if __name__ == "__main__": main()