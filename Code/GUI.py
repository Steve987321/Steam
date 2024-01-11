import customtkinter as ctk
import SteamAPI
import requests
from PIL import Image
from io import BytesIO
import sys

from dataclasses import dataclass

COL_BG = "#16191C"
COL_HOVER = "#202227"
COL_BORDER = "#1D262F"
COL_STATUS_ONLINE_GREEN = "#91C257"
COL_STATUS_NAME_PLAYING = "#D6F1B8"
COL_GAME_TITLE = "#C0D0CE"
COL_GREY = "#434953"
COL_GREY_WIDGET = "#868789"
COL_LIGHT_BLUE = "#78CEF3"
COL_DARK_BLUE = "#4989A3"


def lerp(a, b, t):
    return a + (b - a) * t


def lerp_color(col1, col2, t):
    # naar dec
    r1 = int(col1[1:3], 16)
    g1 = int(col1[3:5], 16)
    b1 = int(col1[5:7], 16)

    # lerp
    r2 = int(col2[1:3], 16)
    g2 = int(col2[3:5], 16)
    b2 = int(col2[5:7], 16)

    # naar hex
    r = format(int(lerp(r1, r2, t)), "02x")
    g = format(int(lerp(g1, g2, t)), "02x")
    b = format(int(lerp(b1, b2, t)), "02x")

    return f"#{r}{g}{b}"


class StatistiekWindow:
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


class PlayerWidget:
    def __init__(self,
                 player,
                 master: any,
                 size: tuple[int, int],
                 avatar_formaat: SteamAPI.AvatarFormaat = SteamAPI.AvatarFormaat.KLEIN):

        image_data = requests.get(player.get_avatar(avatar_formaat))
        if not image_data.ok:
            print("[GUI] AvatarWidget image_data kon niet worden opgehaald")

        image = Image.open(BytesIO(image_data.content))
        resized_image = image.resize(size, Image.Resampling.LANCZOS)
        image_widget = ctk.CTkImage(dark_image=resized_image, size=size)

        status = ""
        status_col = ""
        status_name_col = ""
        if player.get_playing_game() != "":
            status = player.get_playing_game()
            status_col = COL_STATUS_ONLINE_GREEN
            status_name_col = COL_STATUS_NAME_PLAYING
        else:
            status = player.get_status().name.lower()
            status = status.replace(status[0], status[0].upper(), 1)
            status_col = COL_DARK_BLUE
            status_name_col = COL_LIGHT_BLUE

        self.frame = ctk.CTkFrame(master, width=1000, height=size[1]+20, fg_color="transparent")
        self.frame.pack_propagate(False)

        self.button = ctk.CTkButton(self.frame, text="", width=size[0], height=size[1], image=image_widget, border_color=status_col,
                                    border_width=0, border_spacing=0, hover_color=COL_HOVER, fg_color="transparent", command=self.avatar_click)
        self.button.pack_propagate(False)

        self.name_label = ctk.CTkLabel(self.frame, text=player.get_name(), text_color=status_name_col, font=("Arial", 15), height=0, anchor=ctk.W)

        self.status_label = ctk.CTkLabel(self.frame, text=status, text_color=status_col, font=("Arial", 12), height=0, anchor=ctk.W)

        self.name_label.pack_propagate(False)
        self.status_label.pack_propagate(False)

        self.button.pack(side=ctk.LEFT, anchor=ctk.W)
        # spacing
        ctk.CTkFrame(self.frame, height=8, fg_color="transparent").pack(side=ctk.TOP)
        self.name_label.pack(side=ctk.TOP, anchor=ctk.W, padx=5, pady=0)
        self.status_label.pack(side=ctk.TOP, anchor=ctk.W, padx=5, pady=0)

    def pack(self, **kwargs):
        self.frame.pack(**kwargs)

    def pack_forget(self):
        self.frame.pack_forget()

    def avatar_click(self):
        pass


class DropDownButton(ctk.CTkFrame):

    dropdowns = []

    def __init__(self, master: any, title: str, widgets: list[PlayerWidget], **kwargs):
        self.master = master
        self.widgets = widgets
        self.collapsed = False
        self.separator = SeparatorLine(self.master, COL_BORDER)
        self.collapse_widget_color = COL_BG
        self.animation_steps = 0
        DropDownButton.dropdowns.append(self)

        super().__init__(self.master, **kwargs, fg_color="transparent")

        self.title_widget = ctk.CTkLabel(self, text=title, anchor=ctk.W)
        self.collapse_widget = ctk.CTkLabel(self, text='-', anchor=ctk.W, text_color=self.collapse_widget_color)
        self.collapse_widget.pack(side=ctk.LEFT)
        self.title_widget.pack(side=ctk.LEFT)

        self.title_widget.bind("<Button-1>", self.on_click)
        self.title_widget.bind("<Enter>", self.on_hover)
        self.title_widget.bind("<Leave>", self.on_leave)

    @staticmethod
    def reset():
        for dp in DropDownButton.dropdowns:
            dp.pack_forget()
            dp.pack(side=ctk.TOP, anchor=ctk.W, pady=1, padx=2, expand=True, fill=ctk.X)

            if not dp.collapsed:
                for widget in dp.widgets:
                    widget.pack_forget()
                    widget.pack(side=ctk.TOP, anchor=ctk.W, pady=1)

            dp.separator.pack_forget()
            dp.separator.pack()

    def on_hover(self, _):
        # print("fade in start ")
        self.animation_steps = 0
        self.collapse_widget_color = COL_GREY_WIDGET
        self.fade_in()

    def on_leave(self, _):
        self.animation_steps = 0
        self.collapse_widget_color = COL_BG
        self.fade_out()

    def fade_in(self):
        if self.collapse_widget_color != COL_GREY_WIDGET:
            return

        if self.animation_steps < 1 - sys.float_info.epsilon:
            self.animation_steps += 0.01
            # print("in", self.animation_steps)
            col = lerp_color(self.collapse_widget.cget("text_color"), self.collapse_widget_color, self.animation_steps)
            self.collapse_widget.configure(text_color=col)
            self.collapse_widget.after(10, self.fade_in)
        else:
            # print("in", "done")
            self.animation_steps = 1
            self.collapse_widget.configure(text_color=self.collapse_widget_color)

    def fade_out(self):
        if self.collapse_widget_color != COL_BG:
            return

        if self.animation_steps < 1 - sys.float_info.epsilon:
            self.animation_steps += 0.01
            col = lerp_color(self.collapse_widget.cget("text_color"), self.collapse_widget_color, self.animation_steps)
            self.collapse_widget.configure(text_color=col)
            self.collapse_widget.after(10, self.fade_out)
        else:
            self.animation_steps = 1
            self.collapse_widget.configure(text_color=self.collapse_widget_color)


    def on_click(self, _):
        self.collapsed = not self.collapsed

        if self.collapsed:
            self.collapse_widget.configure(text="+")
        else:
            self.collapse_widget.configure(text="-")
            
        if self.collapsed:
            for widget in self.widgets:
                widget.pack_forget()

        DropDownButton.reset()

        # for dropdown in DropDownButton.dropdowns:
        #     dropdown.pack_forget()
        #     dropdown.pack(side=ctk.TOP, anchor=ctk.W)
        #     dropdown.separator.pack_forget()
        #     dropdown.separator.pack()


class SeparatorLine(ctk.CTkFrame):
    def __init__(self, master: any, color: str, **kwargs):
        super().__init__(master, fg_color=color, height=1, width=1000, **kwargs)

    def pack(self, **kwargs):
        super().pack(padx=0, pady=5, **kwargs)


class Window:
    def __init__(self, naam: str, win_width: int, win_height: int, steamid: str):
        self.player = SteamAPI.Player(SteamAPI.Api.get_player_summary(steamid))
        self.player_name = self.player.get_name()

        self.friends = self.player.get_friends()
        self.friends_online = []
        self.friends_offline = []
        self.friends_away = []
        self.friends_games = {}

        for friend in self.friends:
            match friend.get_status():
                case SteamAPI.PlayerStatus.ONLINE:
                    self.friends_online.append(friend)
                case SteamAPI.PlayerStatus.OFFLINE:
                    self.friends_offline.append(friend)
                case SteamAPI.PlayerStatus.AWAY:
                    self.friends_away.append(friend)

            self.friends_games[friend.get_playing_game()] = friend

        ctk.set_appearance_mode("System")

        self.statistiek_window = None

        self.root = ctk.ctk_tk.CTk()
        self.naam = naam

        self.root.geometry(f"{win_width}x{win_height}")
        self.root.title(naam)

        # Frames (links)
        header_frame = ctk.CTkFrame(self.root, height=80, width=200, fg_color=COL_BG, corner_radius=0)
        separator = ctk.CTkFrame(self.root, height=25, width=200, fg_color=COL_GREY, corner_radius=0)
        friends_frame = ctk.CTkScrollableFrame(self.root, width=182, height=10000, fg_color=COL_BG,
                                               border_color=COL_BORDER, border_width=1, corner_radius=0)

        separator_label = ctk.CTkLabel(separator, text="VRIENDEN", font=("Arial", 12))
        separator_label.pack(padx=10, pady=5, side=ctk.LEFT)

        header_frame.pack_propagate(False)
        header_frame.pack(side=ctk.TOP, anchor=ctk.NW)

        separator.pack_propagate(False)
        separator.pack(side=ctk.TOP, anchor=ctk.NW)

        self.friends_online_widgets = []
        self.friends_games_widgets = {}  # game - widget
        for friend in self.friends_online:
            w = PlayerWidget(friend, friends_frame, (30, 30),
                             SteamAPI.AvatarFormaat.KLEIN)

            if friend.get_playing_game() != "":
                if friend.get_playing_game() not in self.friends_games_widgets.keys():
                    self.friends_games_widgets[friend.get_playing_game()] = [w]
                else:
                    self.friends_games_widgets[friend.get_playing_game()].append(w)
                continue
            # player is gewoon online zonder een game te spelen
            self.friends_online_widgets.append(w)

        # TODO:
        # filter friends by game, status etc..

        online_games_dropdowns = []
        for game in self.friends_games_widgets.keys():
            # built button avatar widgets
            player_widgets = []
            for widget in self.friends_games_widgets[game]:
                player_widgets.append(widget)

            dp = DropDownButton(friends_frame, game, player_widgets, height=25, corner_radius=0)
            online_games_dropdowns.append(dp)

        online_dropdown = DropDownButton(friends_frame, f"online vrienden ({len(self.friends_online_widgets)})", self.friends_online_widgets, height=25, corner_radius=0)

        for dp in DropDownButton.dropdowns:
            dp.collapsed = False

        DropDownButton.reset()

        lplayer_avatar = PlayerWidget(self.player, header_frame, (50, 50))
        lplayer_avatar.pack(side=ctk.LEFT, anchor=ctk.NW, pady=10, padx=5)
        friends_frame.pack(side=ctk.LEFT, anchor=ctk.NW)

    def toon_statistiek_window(self):
        if self.statistiek_window is not None:
            if self.statistiek_window.is_open():
                return

        self.statistiek_window = StatistiekWindow("Statistiek")

    def button_click(self):
        self.toon_statistiek_window()

    def show(self):
        self.root.mainloop()
