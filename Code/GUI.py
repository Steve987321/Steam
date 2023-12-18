import customtkinter as ctk
import SteamAPI


class Window:
    def __init__(self, naam: str, win_width: int, win_height: int):
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("green")

        self.root = ctk.ctk_tk.CTk()
        self.naam = naam

        self.root.geometry(f"{win_width}x{win_height}")
        self.root.title(naam)

        button = ctk.CTkButton(self.root, text="knop", command=self.button_click)
        button.pack()

    def button_click(self):
        SteamAPI.test_steam_api()

    def show(self):
        self.root.mainloop()


