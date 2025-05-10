import wx

class MyFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Создаем панель
        self.panel = wx.Panel(self)

        # Создаем вертикальный BoxSizer
        self.vbox = wx.BoxSizer(wx.VERTICAL)

        # Добавляем кнопку в вертикальный BoxSizer
        self.button1 = wx.Button(self.panel, label="Кнопка 1")
        self.vbox.Add(self.button1, flag=wx.ALL | wx.CENTER, border=10)

        # Создаем горизонтальный BoxSizer
        self.hbox = wx.BoxSizer(wx.HORIZONTAL)

        # Добавляем три кнопки в горизонтальный BoxSizer
        self.button2 = wx.Button(self.panel, label="Кнопка 2")
        icon_path = "icons/play.png"  # Путь к иконке
        self.button2.SetBitmap(wx.Bitmap(icon_path))  # Устанавливаем иконку на кнопку
        self.button3 = wx.Button(self.panel, label="Кнопка 3")
        self.button4 = wx.Button(self.panel, label="Кнопка 4")

        # Скрываем кнопки 2, 3 и 4

        self.button2.Hide()
        self.button3.Hide()
        self.button4.Hide()


        self.hbox.Add(self.button2, flag=wx.ALL, border=5)
        self.hbox.Add(self.button3, flag=wx.ALL, border=5)
        self.hbox.Add(self.button4, flag=wx.ALL, border=5)

        # Добавляем горизонтальный BoxSizer в вертикальный BoxSizer
        self.vbox.Add(self.hbox, flag=wx.ALL | wx.CENTER, border=10)

        # Устанавливаем основной sizer для панели
        self.panel.SetSizer(self.vbox)

        # Устанавливаем размер окна
        self.SetSize((300, 200))
        self.SetTitle("Пример wxPython")
        self.Centre()

        # Привязываем обработчик события к кнопке 1
        self.button1.Bind(wx.EVT_BUTTON, self.on_button1_click)

    def on_button1_click(self, event):
        # Отображаем кнопку 2 в hbox
        self.button2.Show()
        self.button3.Show()
        self.panel.Layout()  # Обновляем макет для отображения изменений
        # self.panel.Refresh()

class MyApp(wx.App):
    def OnInit(self):
        frame = MyFrame(None)
        frame.Show()
        return True

if __name__ == "__main__":
    app = MyApp()
    app.MainLoop()