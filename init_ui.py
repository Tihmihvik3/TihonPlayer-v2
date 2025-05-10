import wx
import os


class UIManager:
    def __init__(self, parent):
        self.parent = parent
        self.panel = wx.Panel(parent)

        vbox = wx.BoxSizer(wx.VERTICAL)

        self.listbox = wx.ListBox(self.panel)
        self.listbox.SetMaxSize((-1, 470))
        vbox.Add(self.listbox, proportion=1, flag=wx.EXPAND | wx.ALL, border=10)
        self.hbox = wx.BoxSizer(wx.HORIZONTAL)

        self.buttons_data = [
            ('Воспроизведение (Space)', 'icons/play.png', parent.on_play),
            ('Пауза(Space)', 'icons/pause.png', parent.on_pause),
            ('Продолжить (Space)', 'icons/resume.png', parent.on_resume),
            ('Стоп (Ctrl+Space)', 'icons/stop.png', parent.on_stop),
            ('Перемотать назад (Left)', 'icons/seek_backward.png', parent.on_rewind),
            ('Перемотать вперёд (Right)', 'icons/seek_forward.png', parent.on_forward),
            ('Предыдущий трек (Page Up)', 'icons/prev_track.png', parent.on_prev_track),
            ('Следующий трек (Page Down)', 'icons/next_track.png', parent.on_next_track),
            ('Тише (Ctrl+Down)', 'icons/volume_down.png', parent.on_volume_down),
            ('Громче (Ctrl+Up)', 'icons/volume_up.png', parent.on_volume_up),
            ('Медленнее (Shift+Left)', 'icons/slow_down.png', parent.on_slow_down),
            ('Быстрее (Shift+Right)', 'icons/speed_up.png', parent.on_speed_up),
            ('Ниже (Shift+Down)', 'icons/pitch_down.png', parent.on_pitch_down),
            ('Выше (Shift+Up)', 'icons/pitch_up.png', parent.on_pitch_up),
            ('Обзор (Ctrl+B)', 'icons/browse.png', parent.on_browse),
        ]

        for label, icon, handler in self.buttons_data:
            button = self.create_button(self.panel, label, icon, handler)
            if label == 'Обзор (Ctrl+B)':
                button.Show()
            self.hbox.Add(button, flag=wx.ALL, border=2)

        vbox.Add(self.hbox, flag=wx.ALL | wx.CENTER, border=10)
        self.panel.SetSizer(vbox)

        self.listbox.Bind(wx.EVT_LISTBOX, parent.OnListboxUpdate)

        parent.SetTitle('TihonPlayer v2')
        parent.Centre()

    def create_button(self, panel, label, bitmap_path, event_handler):
        button = wx.Button(panel, label=label)
        button = wx.BitmapButton(panel, bitmap=wx.Bitmap(bitmap_path))
        self.parent.Bind(wx.EVT_BUTTON, event_handler, button)
        button.Hide()
        return button

    def update_button_states(self, play=False, pause=False):
        is_listbox_empty = self.listbox.GetCount() == 0
        if not is_listbox_empty:
            for i in range(3, 15):
                button = self.hbox.GetChildren()[i].GetWindow()
                button.Show()
            button_play = self.hbox.GetChildren()[0].GetWindow()
            button_pause = self.hbox.GetChildren()[1].GetWindow()
            button_resume = self.hbox.GetChildren()[2].GetWindow()

            if not play and not pause:
                button_play.Show()
                button_pause.Hide()
                button_resume.Hide()
            if play and not pause:
                button_play.Hide()
                button_pause.Show()
                button_resume.Hide()
            if not play and pause:
                button_play.Hide()
                button_pause.Hide()
                button_resume.Show()
            self.panel.Layout()  # Update layout
