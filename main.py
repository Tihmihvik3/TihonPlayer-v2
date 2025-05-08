import os
import wx
import subprocess
import time
from hotkeys import HotkeysManager
from wx import Bitmap, Image
import threading


class AudioPlayer(wx.Frame):
    def __init__(self, *args, **kw):
        super(AudioPlayer, self).__init__(*args, **kw)
        self.SetSize(wx.Size(600, 600))

        self.is_paused = False
        self.is_play = False
        self.is_stop = False
        self.init_ui()
        self.current_process = None
        self.playback_speed = 1.0
        self.pitch_factor = 1.0
        self.current_file = None
        self.repeat_track = True
        self.repeat_list = False

        self.start_time = 0
        self.pause_time = 0
        self.playback_thread_started = False  # Флаг для отслеживания состояния потока
        self.folder_path = None  # Initialize folder_path
        self.volume_normal =70

        self.hotkeys_manager = HotkeysManager(self)
        self.hotkeys_manager.register_hotkeys()
        self.on_space_key()
        self.listbox.Bind(wx.EVT_KEY_DOWN, self.on_key_down)
        self.update_button_states()  # Initialize the hotkeys manager and register hotkeys

    def init_ui(self):
        panel = wx.Panel(self)

        vbox = wx.BoxSizer(wx.VERTICAL)

        self.listbox = wx.ListBox(panel)
        self.listbox.SetMaxSize((-1, 470))
        vbox.Add(self.listbox, proportion=1, flag=wx.EXPAND | wx.ALL, border=10)

        self.play_button = self.create_button(panel, 'Воспроизведение (Space)', 'icons/play.png', (5, 500), self.on_play)
        self.pause_button = self.create_button(panel, 'Пауза(Space)', 'icons/pause.png', (5, 500), self.on_pause)
        self.resume_button = self.create_button(panel, 'Продолжить (Space)', 'icons/resume.png', (5, 500), self.on_resume)
        self.stop_button = self.create_button(panel, 'Стоп (Ctrl+Space)', 'icons/stop.png', (40, 500), self.on_stop)
        self.browse_button = self.create_button(panel, 'Обзор (Ctrl+B)', 'icons/browse.png', (75, 500), self.on_browse)
        self.browse_button.Show()
        self.rewind_button = self.create_button(panel, 'Перемотать назад (Left)', 'icons/seek_backward.png', (110, 500), self.on_rewind)
        self.forward_button = self.create_button(panel, 'Перемотать вперёд (Right)', 'icons/seek_forward.png', (145, 500), self.on_forward)
        self.prev_track_button = self.create_button(panel, 'Предыдущий трек (Page Up)', 'icons/prev_track.png', (180, 500), self.on_prev_track)
        self.next_track_button = self.create_button(panel, 'Следующий трек (Page Down)', 'icons/next_track.png', (215, 500), self.on_next_track)
        self.volume_down_button = self.create_button(panel, 'Тише (Ctrl+Down)', 'icons/volume_down.png', (250, 500), self.on_volume_down)
        self.volume_up_button = self.create_button(panel, 'Громче (Ctrl+Up)', 'icons/volume_up.png', (285, 500), self.on_volume_up)
        self.slow_down_button = self.create_button(panel, 'Медленнее (Shift+Left)', 'icons/slow_down.png', (320, 500), self.on_slow_down)
        self.speed_up_button = self.create_button(panel, 'Быстрее (Shift+Right)', 'icons/speed_up.png', (355, 500), self.on_speed_up)
        self.pitch_down_button = self.create_button(panel, 'Ниже (Shift+Down)', 'icons/pitch_down.png', (390, 500), self.on_pitch_down)
        self.pitch_up_button = self.create_button(panel, 'Выше (Shift+Up)', 'icons/pitch_up.png', (425, 500), self.on_pitch_up)

        panel.SetSizer(vbox)


        self.Bind(wx.EVT_BUTTON, self.on_speed_up, self.speed_up_button)
        self.Bind(wx.EVT_BUTTON, self.on_slow_down, self.slow_down_button)

        self.listbox.Bind(wx.EVT_LISTBOX, self.OnListboxUpdate)

        self.SetTitle('TihonPlayer v2')
        self.Centre()

    def create_button(self, panel, label, bitmap_path, position, event_handler):
        button = wx.Button(panel, label=label)
        button = wx.BitmapButton(panel, bitmap=wx.Bitmap(bitmap_path))
        button.SetPosition(position)
        self.Bind(wx.EVT_BUTTON, event_handler, button)
        button.Hide()
        return button

    def on_play(self, event):
        # Stop current playback if it's running
        if self.current_process:
            self.on_stop(None)

        selection = self.listbox.GetSelection()
        if selection != wx.NOT_FOUND:
            file_name = self.listbox.GetString(selection)
            self.current_file = os.path.join(self.folder_path, file_name)
            command = [
                'ffplay', '-nodisp', '-autoexit',
                '-af',
                f'asetrate=44100*{self.pitch_factor},atempo={self.playback_speed}',
                '-volume', str(self.volume_normal),  # Set volume
                self.current_file
            ]
            self.current_process = subprocess.Popen(command, stdin=subprocess.PIPE)
            self.is_paused = False
            self.is_stop = False
            self.is_play = True
            self.update_button_states()
            self.start_time = time.time()

            # Start a thread to monitor playback completion
            if not self.playback_thread_started:
                threading.Thread(target=self.monitor_playback, daemon=True).start()
                self.playback_thread_started = True

    def monitor_playback(self):
        """Monitor the playback process and update button states when it finishes."""
        if self.current_process:
            self.current_process.wait()  # Подождите, пока процесс закончится
            self.current_process = None
            self.is_play = False

            wx.CallAfter(self.update_button_states)
            self.playback_thread_started = False
            if self.repeat_track and not self.is_paused and not self.is_stop:
                self.on_play(None)

    def on_pause(self, event):
        if self.current_process and not self.is_paused:
            self.pause_time = time.time()

            self.on_stop(None)
            self.is_play = False
            self.is_paused = True
            self.update_button_states()

    def on_resume(self, event, sek=0):
        if self.current_file and self.is_paused:
            elapsed_time = self.pause_time - self.start_time + sek
            print(sek)
            command = [
                'ffplay', '-nodisp', '-autoexit',
                '-af',
                f'asetrate=44100*{self.pitch_factor},atempo={self.playback_speed}',
                # Устанавливаем текущий темп и тональность
                '-ss', str(elapsed_time), '-volume', str(self.volume_normal),  # Устанавливаем громкость
                self.current_file
            ]
            self.current_process = subprocess.Popen(command, stdin=subprocess.PIPE)
            self.is_play = True
            self.is_stop = False
            self.is_paused = False
            self.update_button_states()
            if not self.playback_thread_started:
                threading.Thread(target=self.monitor_playback, daemon=True).start()
                self.playback_thread_started = True

    def on_stop(self, event):
        if self.current_process:
            self.current_process.terminate()  # Завершаем процесс
            self.current_process = None
            self.is_play = False
            self.is_paused = False
            self.is_stop = True
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
            self.on_pause(None)
            self.on_resume(None)

    def on_slow_down(self, event):
        self.playback_speed = max(self.playback_speed - 0.1, 0.5)  # Уменьшаем скорость, но не менее чем до 0.5
        if self.current_process:
            self.on_pause(None)
            self.on_resume(None)

    def on_rewind(self, event=None, sec=-2):
        if self.current_process:
            self.on_pause(None)
            self.on_resume(None, sec)


    def on_forward(self, event, sec=2):
        self.on_rewind(None, sec)

    def on_prev_track(self):
        """Переход к предыдущему треку."""
        selection = self.listbox.GetSelection()
        if selection != wx.NOT_FOUND and selection > 0:
            self.listbox.SetSelection(selection - 1)
            self.on_play(None)

    def on_next_track(self):
        """Переход к следующему треку."""
        selection = self.listbox.GetSelection()
        if selection != wx.NOT_FOUND and selection < self.listbox.GetCount() - 1:
            self.listbox.SetSelection(selection + 1)
            self.on_play(None)

    def on_volume_up(self, event):
        if self.current_process:
            self.on_pause(None)  # Pause playback
            self.volume_normal = min(self.volume_normal + 5, 100)  # Increase volume by 5, max 100
            self.on_resume(None)  # Resume playback

    def on_volume_down(self, event):
        if self.current_process:
            self.on_pause(None)  # Pause playback
            self.volume_normal = max(self.volume_normal - 5, 0)  # Decrease volume by 5, minimum 0
            self.on_resume(None)  # Resume playback

    def on_pitch_down(self, event=None):
        """Уменьшение тона воспроизведения."""
        if self.current_process:
            self.on_pause(None)  # Приостановить воспроизведение
            self.pitch_factor = max(self.pitch_factor - 0.1, 0.5)  # Уменьшить тон, минимум 0.5
            self.on_resume(None)  # Возобновить воспроизведение

    def on_pitch_up(self, event=None):
        """Increase the pitch of playback."""
        if self.current_process:
            self.on_pause(None)  # Pause playback
            self.pitch_factor = min(self.pitch_factor + 0.1, 2.0)  # Increase pitch, maximum 2.0
            self.on_resume(None)  # Resume playback

    def OnListboxUpdate(self, event):
        self.update_button_states()

    def update_button_states(self):
        is_listbox_empty = self.listbox.GetCount() == 0
        if not is_listbox_empty:
            if not self.is_play and not self.is_paused:
                self.pause_button.Hide()
                self.resume_button.Hide()
                self.play_button.Show()
            elif self.is_play and not self.is_paused:
                self.play_button.Hide()
                self.resume_button.Hide()
                self.pause_button.Show()
            else:
                self.pause_button.Hide()
                self.play_button.Hide()
                self.resume_button.Show()
            self.stop_button.Show()
            self.speed_up_button.Show()
            self.slow_down_button.Show()
            self.rewind_button.Show()
            self.forward_button.Show()
            self.prev_track_button.Show()
            self.next_track_button.Show()
            self.volume_down_button.Show()
            self.volume_up_button.Show()
            self.pitch_down_button.Show()
            self.pitch_up_button.Show()
            self.slow_down_button.Show()
            self.speed_up_button.Show

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
        if key_code in [wx.WXK_LEFT, wx.WXK_RIGHT, wx.WXK_PAGEUP, wx.WXK_PAGEDOWN]:
            return
        if event.ControlDown() and key_code in [wx.WXK_UP, wx.WXK_DOWN]:
            return  # Prevent Control+Up and Control+Down from affecting the listbox
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
