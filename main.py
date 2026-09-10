from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout

class SystemUpdateApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        label = Label(text='System Update App')
        layout.add_widget(label)
        return layout

if __name__ == '__main__':
    SystemUpdateApp().run()
