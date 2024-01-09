import customtkinter as ctk
import SteamAPI


class StatistiekWindow():
    def __init__(self, window_name: str = "SubWindow", window_size: str = "1080x1440"):
        self.root = ctk.CTkToplevel()
        self.root.title(window_name)
        self.root.resizable(False, False)
        self.root.geometry(window_size)

        self.steam_api_test()


    def is_open(self):
        """Geeft aan of scherm bestaat"""
        return self.root.winfo_exists()

    def get_window(self):
        return self.root

    def steam_api_test(self):
        SteamAPI.test_steam_api()
        self.root.after(10000, self.steam_api_test)


class Window:
    def __init__(self, naam: str, win_width: int, win_height: int):
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("green")

        self.statistiek_window = None

        self.root = ctk.ctk_tk.CTk()
        self.naam = naam

        self.root.geometry(f"{win_width}x{win_height}")
        self.root.title(naam)

        button = ctk.CTkButton(self.root, text="knop", command=self.button_click)
        button.pack()

    def toon_statistiek_window(self):
        if self.statistiek_window is not None:
            if self.statistiek_window.is_open():
                return

        self.statistiek_window = StatistiekWindow("Statistiek")

    def button_click(self):
        SteamAPI.test_steam_api()
        self.toon_statistiek_window()

    def show(self):
        self.root.mainloop()