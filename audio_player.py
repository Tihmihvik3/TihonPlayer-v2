import os
from config import Config
import keyboard
import wx
import subprocess
import time
from hotkeys import HotkeysManager
from init_ui import UIManager
from wx import Bitmap, Image
import threading
from settings import SettingsDialog


class AudioPlayer(wx.Frame):
    def __init__(self, *args, **kw):
        super(AudioPlayer, self).__init__(*args, **kw)
        self.SetSize(wx.Size(600, 600))

        self.num = 0
        self.is_paused = False
        self.is_play = False
        self.is_stop = False

        self.current_process = None
        self.playback_speed = 1.0
        self.pitch_factor = 1.0
        self.current_file = None
        self.buttons_data = None

        self.config = Config()
        self.repeat_track = self.config.get('REPEAT_MUSIC', 'repeat_track') == 'True'
        self.repeat_list = self.config.get('REPEAT_MUSIC', 'repeat_list') == 'True'
        self.play_list = self.config.get('REPEAT_MUSIC', 'all_list') == 'True'

        self.start_time = 0
        self.pause_time = 0
        self.playback_thread_started = False  # Флаг для отслеживания состояния потока
        self.daemonthread = threading.Thread(target=self.monitor_playback)
        self.blocking_keyboard = False
        self.blocking_keyboard_thread = threading.Thread(target=self.time_blocking_keyboard)
        # self.blocking_keyboard_thread.start()
        self.folder_path = None  # Initialize folder_path
        self.volume_normal = 70

        self.hotkeys_manager = HotkeysManager(self)
        self.hotkeys_manager.register_hotkeys()
        # Initialize UIManager
        self.ui_manager = UIManager(self)
        self.listbox = self.ui_manager.listbox
        self.hbox = self.ui_manager.hbox

        self.on_space_key()
        self.listbox.Bind(wx.EVT_KEY_DOWN, self.on_key_down)
        self.update_button_states = self.ui_manager.update_button_states

    def on_play(self, event):
        self.blocking_keyboard = True
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
            self.update_button_states(self.is_play, self.is_paused)
            self.start_time = time.time()

            # Start a thread to monitor playback completion
            if not self.playback_thread_started:
                self.daemonthread.start()
                self.playback_thread_started = True

    def monitor_playback(self):
        """Monitor the playback process and update button states when it finishes."""
        while True:
            time.sleep(1)
            if self.current_process:

                self.current_process.wait()  # Подождите, пока процесс закончится
                self.current_process = None
                self.is_play = False

                self.update_button_states(self.is_play, self.is_paused)

                if self.repeat_track and not self.is_paused and not self.is_stop:
                    self.on_play(None)
                if self.play_list and not self.is_paused and not self.is_stop:
                    self.on_next_track(None)

    def time_blocking_keyboard(self):
        while True:
            time.sleep(1)
            print('Blocking keyboard')
            if self.blocking_keyboard:
                # keyboard.block_key('all')
                time.sleep(5)
                # keyboard.unblock_key('all')
                self.blocking_keyboard = False

    def on_pause(self, event):
        if self.current_process and not self.is_paused:
            self.pause_time = time.time()

            self.on_stop(None)
            self.is_play = False
            self.is_paused = True
            self.update_button_states(self.is_play, self.is_paused)

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
            self.update_button_states(self.is_play, self.is_paused)

    def on_stop(self, event):
        if self.current_process:
            self.current_process.terminate()  # Завершаем процесс
            self.current_process = None

            self.is_play = False
            self.is_paused = False
            self.is_stop = True
            self.update_button_states(self.is_play, self.is_paused)

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
                self.update_button_states(self.is_play, self.is_paused)

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

    def on_prev_track(self, event=None):
        """Переход к предыдущему треку."""
        selection = self.listbox.GetSelection()
        if selection != wx.NOT_FOUND and selection > 0:
            self.listbox.SetSelection(selection - 1)
            self.on_play(None)

    def on_next_track(self, event=None):
        """Переход к следующему треку."""
        selection = self.listbox.GetSelection()
        if selection != wx.NOT_FOUND and selection < self.listbox.GetCount() - 1:
            self.listbox.SetSelection(selection + 1)
            self.on_play(None)
        if selection != wx.NOT_FOUND and selection == self.listbox.GetCount() - 1 and self.repeat_list:
            self.listbox.SetSelection(0)
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
        self.update_button_states(self.is_play, self.is_paused)

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
        if event.ShiftDown() and key_code in [wx.WXK_UP, wx.WXK_DOWN]:
            return
        event.Skip()  # Allow other keys to be processed normally

    def on_settings(self, event):

        settings_dialog = SettingsDialog(self)
        settings_dialog.ShowModal()
        settings_dialog.Destroy()

    def on_close(self, event):
        if self.current_process:
            self.current_process.terminate()
        self.Destroy()
