import wx
from ObjectListView import ObjectListView, ColumnDefn

class OpenInfoDialog(wx.Dialog):
    def __init__(self, info_list):
        wx.Dialog.__init__(self, None, size=(750, 600))
        self.SetTitle('Choose Run')
        #~ info_list = [{'description': 'Test',
                      #~ 'creation'   : '2017-07-11 08:30:00'}]
        panel = wx.Panel(self)
        self.lb = ObjectListView(self, -1, style=wx.LC_REPORT)
        self.lb.SetColumns([
            ColumnDefn('Description', 'left', 300, 'description'),
            ColumnDefn('# Triangles', 'center', 150, 'num_polys'),
            ColumnDefn('Date/Time', 'left', 300, 'creation'),
        ])
        self.lb.SetObjects(info_list)
        
        btn_sizer = wx.Dialog.CreateButtonSizer(self, wx.OK|wx.CANCEL)
        
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.lb, 1, flag=wx.EXPAND)
        sizer.Add(btn_sizer, 0, flag=wx.EXPAND)
        self.SetSizer(sizer)
        
        self.lb.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.onDoubleClick)
        
    def onDoubleClick(self, event):
        self.EndModal(wx.ID_OK)
        
        