import customtkinter as ctk


class Window:
    def __init__(self,
                 naam: str,
                 win_width: int,
                 win_height: int):

        # App appearance
        ctk.set_appearance_mode("System")
        # Kleuren van de Widget
        ctk.set_default_color_theme("green")

        self.root = ctk.ctk_tk.CTk()
        self.naam = naam

        self.root.geometry(f"{win_width}x{win_height}")
        self.root.title(naam)

        ctk.CTkButton(self.root, text="knop").pack()

    def show(self):
        self.root.mainloop()
