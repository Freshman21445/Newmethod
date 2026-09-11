import threading
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout

# Import everything from your dropper.py
import dropper


class MainScreen(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", padding=10, spacing=10, **kwargs)

        self._running = False

        # Buttons
        btn_row = BoxLayout(size_hint_y=None, height=50, spacing=10)

        self.start_btn = Button(text="Start")
        self.start_btn.bind(on_press=self.start)
        btn_row.add_widget(self.start_btn)

        self.stop_btn = Button(text="Stop", disabled=True)
        self.stop_btn.bind(on_press=self.stop)
        btn_row.add_widget(self.stop_btn)

        self.add_widget(btn_row)

        # Log area
        self.log_layout = GridLayout(cols=1, size_hint_y=None, spacing=4)
        self.log_layout.bind(minimum_height=self.log_layout.setter("height"))

        scroll = ScrollView()
        scroll.add_widget(self.log_layout)
        self.add_widget(scroll)

    def log(self, msg):
        self.log_layout.add_widget(
            Label(text=msg, size_hint_y=None, height=28)
        )

    def start(self, *args):
        self._running = True
        self.start_btn.disabled = True
        self.stop_btn.disabled = False
        Clock.schedule_once(lambda dt: self.log("Started..."))
        threading.Thread(target=self._run_loop, daemon=True).start()

    def stop(self, *args):
        self._running = False
        self.start_btn.disabled = False
        self.stop_btn.disabled = True
        Clock.schedule_once(lambda dt: self.log("Stopped."))

    def _run_loop(self):
        # Calls your coffee.py logic in a background thread
        # Replace coffee.run() with whatever your main function is called
        try:
            dropper.main()
        except Exception as e:
            Clock.schedule_once(lambda dt, err=e: self.log(f"Error: {err}"))


class dropperApp(App):
    def build(self):
        return MainScreen()


if __name__ == "__main__":
    dropperApp().run()
