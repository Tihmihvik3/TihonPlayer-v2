import keyboard
import wx


class HotkeysManager:

    def __init__(self, tab):
        self.number_key = 0
        self.tab = tab
        self.fast_key = "qwertyuiopasdfghjklzxcvbnm"

    def is_main_window_active(self):
        """Check if the main window is active."""
        main_window = wx.GetTopLevelParent(self.tab)
        return wx.GetActiveWindow() == main_window

    def register_hotkeys(self):
        """Register all hotkeys for the tab."""
        keyboard.add_hotkey('ctrl+b', lambda: wx.CallAfter(self.execute_if_active, self.tab.on_browse, None))
        keyboard.add_hotkey('space', lambda: wx.CallAfter(self.execute_if_active, self.tab.on_space_key))
        keyboard.add_hotkey('ctrl+space', lambda: wx.CallAfter(self.execute_if_active, self.tab.on_stop, None))
        keyboard.add_hotkey('menu', lambda: wx.CallAfter(self.execute_if_active, self.tab.context_menu.show))
        keyboard.add_hotkey('page up', lambda: wx.CallAfter(self.execute_if_active, self.tab.on_prev_track, None))
        keyboard.add_hotkey('page down', lambda: wx.CallAfter(self.execute_if_active, self.tab.on_next_track, None))
        keyboard.add_hotkey('ctrl+left', lambda: wx.CallAfter(self.execute_if_active, self.tab.on_rewind, None, -10))
        keyboard.add_hotkey('shift+left', lambda: wx.CallAfter(self.execute_if_active, self.tab.on_slow_down, None))
        keyboard.add_hotkey('shift+right', lambda: wx.CallAfter(self.execute_if_active, self.tab.on_speed_up, None))
        keyboard.add_hotkey('alt+left', lambda: wx.CallAfter(self.execute_if_active, self.tab.on_rewind, None, -30))
        keyboard.add_hotkey('ctrl+right', lambda: wx.CallAfter(self.execute_if_active, self.tab.on_forward, None, 10))
        keyboard.add_hotkey('alt+right', lambda: wx.CallAfter(self.execute_if_active, self.tab.on_forward, None, 30))
        keyboard.add_hotkey('left', lambda: wx.CallAfter(self.execute_if_active, self.tab.on_rewind, None))
        keyboard.add_hotkey('right', lambda: wx.CallAfter(self.execute_if_active, self.tab.on_forward, None))
        keyboard.add_hotkey('esc', lambda: wx.CallAfter(self.execute_if_active, self.tab.on_mute, None))
        keyboard.add_hotkey('ctrl+up', lambda: wx.CallAfter(self.execute_if_active, self.tab.on_volume_up, None))
        keyboard.add_hotkey('ctrl+down', lambda: wx.CallAfter(self.execute_if_active, self.tab.on_volume_down, None))
        keyboard.add_hotkey('ctrl+p', lambda: wx.CallAfter(self.execute_if_active, self.tab.on_settings, None))

        for char in self.fast_key:
            self.number_key += 1
            keyboard.add_hotkey(f'shift+{char}', lambda: wx.CallAfter(self.execute_if_active, self.tab.on_play_sample, None, f'{number_key}.mp3'))
        keyboard.add_hotkey('enter', lambda: wx.CallAfter(self.execute_if_active, self.tab.on_play, None))

    def execute_if_active(self, func, *args, **kwargs):
        """Execute the function only if the main window is active."""
        if self.is_main_window_active():
            func(*args, **kwargs)