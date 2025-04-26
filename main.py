import os
import wx
import subprocess
import time
from hotkeys import HotkeysManager


class AudioPlayer(wx.Frame):
    def __init__(self, *args, **kw):
        super(AudioPlayer, self).__init__(*args, **kw)

        self.is_paused = False
        self.is_play = False
        self.init_ui()
        self.current_process = None
        self.playback_speed = 1.0
        self.current_file = None

        self.start_time = 0
        self.pause_time = 0
        self.folder_path = None  # Initialize folder_path
        self.update_button_states()  # Initialize the hotkeys manager and register hotkeys
        self.hotkeys_manager = HotkeysManager(self)
        self.hotkeys_manager.register_hotkeys()
        self.on_space_key()
        self.listbox.Bind(wx.EVT_KEY_DOWN, self.on_key_down)

    def init_ui(self):
        panel = wx.Panel(self)

        def set_button_font_size(button, size):
            font = button.GetFont()
            font.SetPointSize(size)
            button.SetFont(font)

        vbox = wx.BoxSizer(wx.VERTICAL)

        self.listbox = wx.ListBox(panel)
        vbox.Add(self.listbox, proportion=1, flag=wx.EXPAND | wx.ALL, border=10)

        hbox = wx.BoxSizer(wx.HORIZONTAL)

        self.play_button = wx.Button(panel, label='Воспроизведение')
        self.pause_button = wx.Button(panel, label='Пауза')
        self.resume_button = wx.Button(panel, label='Продолжить')
        self.stop_button = wx.Button(panel, label='Стоп')
        self.browse_button = wx.Button(panel, label='Обзор')
        self.rewind_button = wx.Button(panel, label='Назад')
        self.forward_button = wx.Button(panel, label='Вперед')
        self.slow_down_button = wx.Button(panel, label='Замедлить')
        self.speed_up_button = wx.Button(panel, label='Ускорить')

        self.play_button.SetSize((30, 20))
        self.pause_button.SetSize((30, 20))
        self.resume_button.SetSize((30, 20))
        self.stop_button.SetSize((30, 20))
        self.browse_button.SetSize((30, 20))
        self.rewind_button.SetSize((30, 20))
        self.forward_button.SetSize((30, 20))
        self.slow_down_button.SetSize((30, 20))
        self.speed_up_button.SetSize((30, 20))

        # Устанавливаем выравнивание текста по левому краю для кнопок
        self.play_button.SetWindowStyle(wx.ALIGN_LEFT)
        self.pause_button.SetWindowStyle(wx.ALIGN_LEFT)
        self.resume_button.SetWindowStyle(wx.ALIGN_LEFT)
        self.stop_button.SetWindowStyle(wx.ALIGN_LEFT)
        self.browse_button.SetWindowStyle(wx.ALIGN_LEFT)
        self.speed_up_button.SetWindowStyle(wx.ALIGN_LEFT)
        self.slow_down_button.SetWindowStyle(wx.ALIGN_LEFT)
        self.rewind_button.SetWindowStyle(wx.ALIGN_LEFT)
        self.forward_button.SetWindowStyle(wx.ALIGN_LEFT)

        self.play_button.SetPosition((5, 180))
        self.pause_button.SetPosition((-35, 180))
        self.resume_button.SetPosition((-35, 180))
        self.stop_button.SetPosition((40, 180))
        self.browse_button.SetPosition((75, 180))
        self.rewind_button.SetPosition((110, 180))
        self.forward_button.SetPosition((145, 180))
        self.slow_down_button.SetPosition((180, 180))
        self.speed_up_button.SetPosition((215, 180))
        set_button_font_size(self.play_button, 8)

        hbox.Add(self.rewind_button, flag=wx.RIGHT, border=10)
        hbox.Add(self.forward_button)

        vbox.Add(hbox, flag=wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, border=10)

        panel.SetSizer(vbox)

        self.Bind(wx.EVT_BUTTON, self.on_play, self.play_button)
        self.Bind(wx.EVT_BUTTON, self.on_pause, self.pause_button)
        self.Bind(wx.EVT_BUTTON, self.on_resume, self.resume_button)
        self.Bind(wx.EVT_BUTTON, self.on_stop, self.stop_button)
        self.Bind(wx.EVT_BUTTON, self.on_browse, self.browse_button)
        self.Bind(wx.EVT_BUTTON, self.on_speed_up, self.speed_up_button)
        self.Bind(wx.EVT_BUTTON, self.on_slow_down, self.slow_down_button)
        self.Bind(wx.EVT_BUTTON, self.on_rewind, self.rewind_button)
        self.Bind(wx.EVT_BUTTON, self.on_forward, self.forward_button)
        self.listbox.Bind(wx.EVT_LISTBOX, self.OnListboxUpdate)

        self.SetTitle('Аудиоплеер')
        self.Centre()

    def on_play(self, event):
        # Остановить текущее воспроизведение, если оно запущено
        if self.current_process:
            self.on_stop(None)

        selection = self.listbox.GetSelection()
        if selection != wx.NOT_FOUND:
            file_name = self.listbox.GetString(selection)
            self.current_file = os.path.join(self.folder_path, file_name)
            command = ['ffplay', '-nodisp', '-autoexit', '-af', f'atempo={self.playback_speed}', self.current_file]
            self.current_process = subprocess.Popen(command, stdin=subprocess.PIPE)
            self.is_paused = False
            self.is_play = True
            self.update_button_states()
            self.start_time = time.time()

    def on_pause(self, event):
        if self.current_process and not self.is_paused:
            self.pause_time = time.time()
            self.current_process.stdin.write(b'p')  # Отправляем команду на паузу
            self.on_stop(None)
            self.is_play = False
            self.is_paused = True
            self.update_button_states()

    def on_resume(self, event):
        if self.current_file and self.is_paused:
            elapsed_time = time.time() - self.start_time
            command = [
                'ffplay', '-nodisp', '-autoexit', '-af', f'atempo={self.playback_speed}',
                '-ss', str(elapsed_time), self.current_file
            ]
            self.current_process = subprocess.Popen(command, stdin=subprocess.PIPE)
            self.is_play = True
            self.is_paused = False
            self.update_button_states()

    def on_stop(self, event):
        if self.current_process:
            self.current_process.terminate()
            self.current_process = None
            self.is_play = False
            self.is_paused = False
            self.update_button_states()

    def on_browse(self, event):
        with wx.DirDialog(self, "Выберите папку с аудиофайлами", style=wx.DD_DEFAULT_STYLE) as dlg:
            if dlg.ShowModal() == wx.ID_OK:
                self.folder_path = dlg.GetPath()  # Set folder_path here
                self.listbox.Clear()
                for file in os.listdir(self.folder_path):
                    if file.endswith('.mp3'):
                        self.listbox.Append(file)  # Добавляем только имя файла
                if self.listbox.GetCount() > 0:
                    self.listbox.SetSelection(0)  # Выделяем первый элемент
                    self.listbox.SetFocus()  # Устанавливаем фокус на listbox
                self.update_button_states()

    def on_speed_up(self, event):
        self.playback_speed = min(self.playback_speed + 0.1, 2.0)  # Увеличиваем скорость, но не более чем до 2.0
        if self.current_process:
            self.on_stop(None)
            self.on_play(None)

    def on_slow_down(self, event):
        self.playback_speed = max(self.playback_speed - 0.1, 0.5)  # Уменьшаем скорость, но не менее чем до 0.5
        if self.current_process:
            self.on_stop(None)
            self.on_play(None)

    def on_rewind(self, event=None, sec=-2):
        if self.current_process:
            # Save the stop time
            self.pause_time = time.time()
            elapsed_time = max(0, self.pause_time - self.start_time + sec)  # Subtract 2 seconds, minimum value is 0

            # Stop the current playback
            self.current_process.terminate()
            self.current_process = None

            # Start playback from the new position
            if self.current_file:
                command = [
                    'ffplay', '-nodisp', '-autoexit', '-af', f'atempo={self.playback_speed}',
                    '-ss', str(elapsed_time), self.current_file
                ]
                self.current_process = subprocess.Popen(command, stdin=subprocess.PIPE)
                self.start_time = time.time() - elapsed_time  # Update the start time
                self.is_paused = False

    def on_forward(self, event, sec=2):
        self.on_rewind(None, sec)

    def OnListboxUpdate(self, event):
        self.update_button_states()

    def update_button_states(self):
        is_listbox_empty = self.listbox.GetCount() == 0
        if not self.is_play and not self.is_paused:
            self.pause_button.Enable(False)
            self.pause_button.SetPosition((-35, 180))
            self.resume_button.Enable(False)
            self.resume_button.SetPosition((-35, 180))
            self.play_button.Enable(not is_listbox_empty)
            self.play_button.SetPosition((5, 180))
        elif self.is_play and not self.is_paused:
            self.play_button.Enable(False)
            self.play_button.SetPosition((-35, 180))
            self.resume_button.Enable(False)
            self.resume_button.SetPosition((-35, 180))
            self.pause_button.Enable(True)
            self.pause_button.SetPosition((5, 180))
        else:
            self.pause_button.Enable(False)
            self.pause_button.SetPosition((-35, 180))
            self.resume_button.Enable(not is_listbox_empty)
            self.resume_button.SetPosition((5, 180))
        self.stop_button.Enable(not is_listbox_empty)
        self.speed_up_button.Enable(not is_listbox_empty)
        self.slow_down_button.Enable(not is_listbox_empty)
        self.rewind_button.Enable(not is_listbox_empty)
        self.forward_button.Enable(not is_listbox_empty)
        # "Обзор" button remains always enabled

    def on_space_key(self):
        """Handle the space key press."""
        if not self.is_play and not self.is_paused:
            self.on_play(None)
        elif self.is_play and not self.is_paused:
            self.on_pause(None)
        else:
            self.on_resume(None)

    def on_key_down(self, event):
        """Handle key down events to prevent listbox navigation."""
        key_code = event.GetKeyCode()
        if key_code in [wx.WXK_LEFT, wx.WXK_RIGHT]:
            # Prevent default behavior for left and right keys
            return
        event.Skip()  # Allow other keys to be processed normally

    def on_close(self, event):
        if self.current_process:
            self.current_process.terminate()
        self.Destroy()


def main():
    app = wx.App()
    player = AudioPlayer(None)
    player.Bind(wx.EVT_CLOSE, player.on_close)
    player.Show()
    app.MainLoop()


if __name__ == '__main__':
    main()
