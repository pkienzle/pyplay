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


class ParentFrame(wx.aui.AuiMDIParentFrame):
    def __init__(self, parent):
        wx.aui.AuiMDIParentFrame.__init__(self, parent, -1,
                                          title="AuiMDIParentFrame",
                                          size=(640,480),
                                          style=wx.DEFAULT_FRAME_STYLE)
        event_trace(self,"MDI parent")
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
        event_trace(self, "Child %d"%count)
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