import wx

from audio_player import AudioPlayer


class MainApp:
    def __init__(self):
        self.app = wx.App()
        self.player = AudioPlayer(None)
        self.player.Bind(wx.EVT_CLOSE, self.player.on_close)

    def run(self):
        self.player.Show()
        self.app.MainLoop()


if __name__ == '__main__':
    main_app = MainApp()
    main_app.run()
