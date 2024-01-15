import customtkinter as ctk
import SteamAPI
import requests
from PIL import Image
from io import BytesIO
import sys

from dataclasses import dataclass

COL_BG = "#202228"
COL_HOVER = "#202227"
COL_BORDER = "#30627F"
COL_BORDER_BLACK ="#121216"
COL_LABEL = "#B7CCD5"
COL_STATUS_ONLINE_GREEN = "#91C257"
COL_STATUS_NAME_PLAYING = "#D6F1B8"
COL_STATUS_OFFLINE_NAME_GREY = "#979798"
COL_STATUS_OFFLINE_GREY = "#6E6E6E"
COL_GAME_TITLE = "#C0D0CE"
COL_GREY = "#434953"
COL_GREY_WIDGET = "#868789"
COL_LIGHT_BLUE = "#78CEF3"
COL_DARK_BLUE = "#4989A3"


def lerp(a, b, t):
    return a + (b - a) * t


def clamp(v, min, max):
    if v >= max:
        return max
    elif v <= min:
        return min
    return v


def lerp_color(col1, col2, t):
    # naar dec
    r1 = int(col1[1:3], 16)
    g1 = int(col1[3:5], 16)
    b1 = int(col1[5:7], 16)

    r2 = int(col2[1:3], 16)
    g2 = int(col2[3:5], 16)
    b2 = int(col2[5:7], 16)

    # lerp en naar hex
    r = format(int(lerp(r1, r2, t)), "02x")
    g = format(int(lerp(g1, g2, t)), "02x")
    b = format(int(lerp(b1, b2, t)), "02x")

    return f"#{r}{g}{b}"


class Tab(ctk.CTkFrame):
    def __init__(self, master: any, text, tabbar, content: ctk.CTkFrame, command: (), **kwargs):
        super().__init__(master, **kwargs)

        self.tabbar = tabbar
        self.button = ctk.CTkButton(self, text=text, command=command)
        self.content = content
        self.close_button = ctk.CTkButton(self, text='X', command=self.on_close)

    def on_close(self):
        self.tabbar.remove_tab(self)


class TabBar(ctk.CTkFrame):
    def __init__(self, master: any, **kwargs):
        self.tabs = []
        super().__init__(master, **kwargs)

    def reset(self):
        for tab in self.tabs:
            tab.pack(side=ctk.LEFT)

    def add_tab(self, tab: Tab):
        self.tabs.append(tab)
        self.reset()

    def remove_tab(self, tab: Tab):
        if tab in self.tabs:
            self.tabs.remove(tab)
            self.reset()


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

        status_str = player.get_status().name.lower()
        status_str = status_str.replace(status_str[0], status_str[0].upper(), 1)
        status_col = COL_DARK_BLUE
        status_name_col = COL_LIGHT_BLUE
        match player.get_status():
            case SteamAPI.PlayerStatus.ONLINE:
                if player.get_playing_game() != "":
                    status_str = player.get_playing_game()
                    status_col = COL_STATUS_ONLINE_GREEN
                    status_name_col = COL_STATUS_NAME_PLAYING
                else:
                    status_col = COL_DARK_BLUE
                    status_name_col = COL_LIGHT_BLUE
            case SteamAPI.PlayerStatus.OFFLINE:
                status_col = COL_STATUS_OFFLINE_GREY
                status_name_col = COL_STATUS_OFFLINE_NAME_GREY
            case _:
                pass

        self.status_str = status_str

        self.frame = ctk.CTkFrame(master, width=1000, height=size[1]+10, fg_color="transparent")
        self.frame.pack_propagate(False)

        self.button = ctk.CTkButton(self.frame, text="", width=size[0], height=size[1], image=image_widget, border_color=status_col,
                                    border_width=0, border_spacing=0, hover_color=COL_HOVER, fg_color="transparent", command=self.avatar_click)
        self.button.pack_propagate(False)

        self.name_label = ctk.CTkLabel(self.frame, text=player.get_name(), text_color=status_name_col, font=("Arial", 15), height=0, anchor=ctk.W)

        self.status_label = ctk.CTkLabel(self.frame, text=status_str, text_color=status_col, font=("Arial", 12), height=0, anchor=ctk.W)

        self.frame.bind("<Enter>", self.on_mouse_enter)
        self.frame.bind("<Leave>", self.on_mouse_leave)
        self.frame.bind("<Button-1>", self.on_mouse_press)

        self.button.bind("<Enter>", self.on_mouse_enter)
        self.button.bind("<Leave>", self.on_mouse_leave)

        self.status_label.bind("<Enter>", self.on_mouse_enter)
        self.status_label.bind("<Leave>", self.on_mouse_leave)
        self.status_label.bind("<Button-1>", self.on_mouse_press)

        self.name_label.bind("<Enter>", self.on_mouse_enter)
        self.name_label.bind("<Leave>", self.on_mouse_leave)
        self.name_label.bind("<Button-1>", self.on_mouse_press)

        self.name_label.pack_propagate(False)
        self.status_label.pack_propagate(False)

        self.button.pack(side=ctk.LEFT, anchor=ctk.W)
        # spacing
        ctk.CTkFrame(self.frame, height=5, fg_color="transparent").pack(side=ctk.TOP)
        self.name_label.pack(side=ctk.TOP, anchor=ctk.W, padx=5, pady=0)
        self.status_label.pack(side=ctk.TOP, anchor=ctk.W, padx=5, pady=1)

    def pack(self, **kwargs):
        self.frame.pack(**kwargs)

    def pack_forget(self):
        self.frame.pack_forget()

    def on_mouse_enter(self, _):
        if self.status_str.lower() == "online":
            self.frame.configure(fg_color="#23282F")
        else:
            self.frame.configure(fg_color="#0F0F12")

    def on_mouse_leave(self, _):
        self.frame.configure(fg_color="transparent")
        pass

    def on_mouse_press(self, _):
        pass

    def avatar_click(self, _):
        pass


class DropDownButton(ctk.CTkFrame):

    dropdowns = []

    def __init__(self, master: any, title: str, widgets: list[PlayerWidget], **kwargs):
        self.master = master
        self.widgets = widgets
        self.collapsed = False
        self.collapse_widget_color = COL_BG
        self.animation_steps = 0
        self.separator = SeparatorLine(self.master, COL_BORDER)

        DropDownButton.dropdowns.append(self)

        super().__init__(self.master, **kwargs, fg_color="transparent")

        self.title_widget = ctk.CTkLabel(self, text=title, anchor=ctk.W, text_color=COL_LABEL)
        self.collapse_widget = ctk.CTkLabel(self, text='-', font=("Arial", 14), anchor=ctk.W, text_color=self.collapse_widget_color)
        self.count_widget = ctk.CTkLabel(self, text=f"({len(widgets)})", font=("Arial", 12), anchor=ctk.W, text_color=COL_GREY)
        self.collapse_widget.pack(side=ctk.LEFT, padx=2)
        self.title_widget.pack(side=ctk.LEFT, padx=2)
        self.count_widget.pack(side=ctk.LEFT, padx=2)

        self.title_widget.bind("<Button-1>", self.on_click)
        self.title_widget.bind("<Enter>", self.on_hover)
        self.title_widget.bind("<Leave>", self.on_leave)

    @staticmethod
    def reset():
        i = 0
        for dp in DropDownButton.dropdowns:
            i += 1

            dp.pack_forget()
            dp.pack(side=ctk.TOP, anchor=ctk.W, pady=0, padx=2, expand=True, fill=ctk.X)

            if not dp.collapsed:
                for widget in dp.widgets:
                    widget.pack_forget()
                    widget.pack(side=ctk.TOP, anchor=ctk.W, pady=0)
            dp.separator.pack_forget()

            if i < len(DropDownButton.dropdowns):
                if i == len(DropDownButton.dropdowns) - 1:
                    dp.separator.configure(fg_color=COL_STATUS_OFFLINE_GREY)

                dp.separator.pack(pady=5)

    def on_hover(self, _):
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


class SeparatorLine(ctk.CTkFrame):
    def __init__(self, master: any, color: str, **kwargs):
        super().__init__(master, fg_color=color, height=1, **kwargs)

    def pack(self, **kwargs):
        super().pack(fill=ctk.X, padx=0, **kwargs)


class SeparatorLineV(ctk.CTkFrame):
    def __init__(self, master: any, color: str, **kwargs):
        super().__init__(master, fg_color=color, width=6, **kwargs)

    def pack(self, **kwargs):
        super().pack(fill=ctk.Y, padx=0, pady=0, **kwargs)


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

        self.panel_start_x = 0

        ctk.set_appearance_mode("System")

        self.statistiek_window = None

        self.root = ctk.ctk_tk.CTk()
        self.naam = naam

        self.root.geometry(f"{win_width}x{win_height}")
        self.root.title(naam)

        # Panels

        # Vrienden Lijst
        self.friend_list_panel_width = win_width // 3
        self.info_panel_width = win_width - self.friend_list_panel_width

        self.friend_list_panel = ctk.CTkFrame(self.root, width=self.friend_list_panel_width, fg_color=COL_BG, border_color=COL_BORDER, border_width=1, corner_radius=0)
        header_frame = ctk.CTkFrame(self.friend_list_panel, fg_color=COL_BG, height=80, corner_radius=0)
        separator = ctk.CTkFrame(self.friend_list_panel, fg_color=COL_GREY, height=25, corner_radius=0)
        friends_frame = ctk.CTkScrollableFrame(self.friend_list_panel, fg_color=COL_BG,
                                               border_color=COL_BORDER, corner_radius=0)
        separator_label = ctk.CTkLabel(separator, text="VRIENDEN", font=("Arial", 12), text_color=COL_LABEL)
        separator_label.pack(padx=10, pady=5, side=ctk.LEFT)

        # Panel separator (x resizer)
        self.panel_separator = SeparatorLineV(self.root, "#23252A", border_width=1, corner_radius=0, border_color=COL_BORDER_BLACK)
        self.panel_separator.bind("<Enter>", self.panel_separator_mouse_enter)
        self.panel_separator.bind("<Leave>", self.panel_separator_mouse_leave)
        self.panel_separator.bind("<Motion>", self.panel_separator_mouse_held)

        self.info_panel = ctk.CTkFrame(self.root, width=self.info_panel_width, fg_color=COL_BG, border_color=COL_BORDER, border_width=0, corner_radius=0)
        self.info_panel_tabbar = TabBar(self.info_panel, height=60, corner_radius=0)

        temp = ctk.CTkLabel(self.info_panel, text="Druk op een vriend om te starten", text_color=COL_GREY_WIDGET, font=("Arial", 20))
        self.info_panel_tabbar.pack_propagate(False)
        temp.pack_propagate(False)
        self.info_panel_tabbar.pack(anchor=ctk.N, side=ctk.TOP, fill=ctk.X, expand=True)
        temp.pack(side=ctk.TOP, fill=ctk.BOTH, expand=True)

        header_frame.pack_propagate(False)
        separator.pack_propagate(False)

        self.friends_online_widgets = []
        self.friends_offline_widgets = []
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

        for friend in self.friends_offline:
            w = PlayerWidget(friend, friends_frame, (30, 30),
                             SteamAPI.AvatarFormaat.KLEIN)

            # player is gewoon online zonder een game te spelen
            self.friends_offline_widgets.append(w)

        online_games_dropdowns = []
        for game in self.friends_games_widgets.keys():
            # built button avatar widgets
            player_widgets = []
            for widget in self.friends_games_widgets[game]:
                player_widgets.append(widget)

            dp = DropDownButton(friends_frame, game, player_widgets, height=25, corner_radius=0)
            online_games_dropdowns.append(dp)

        DropDownButton(friends_frame, f"Online vrienden", self.friends_online_widgets, height=25, corner_radius=0)
        DropDownButton(friends_frame, f"Offline", self.friends_offline_widgets, height=25, corner_radius=0)

        for dp in DropDownButton.dropdowns:
            dp.collapsed = False

        DropDownButton.reset()

        header_frame.pack(side=ctk.TOP, fill=ctk.X)
        separator.pack(side=ctk.TOP, fill=ctk.X)

        lplayer_avatar = PlayerWidget(self.player, header_frame, (50, 50))
        lplayer_avatar.pack(side=ctk.TOP, pady=10, padx=5)
        friends_frame.pack(side=ctk.TOP, fill=ctk.BOTH, expand=True)

        self.friend_list_panel.pack_propagate(False)
        self.info_panel.pack_propagate(False)
        self.friend_list_panel.pack(side=ctk.LEFT, fill=ctk.BOTH)
        self.panel_separator.pack(side=ctk.LEFT)
        self.info_panel.pack(side=ctk.LEFT, fill=ctk.BOTH, expand=True)

    def panel_separator_mouse_enter(self, _):
        self.panel_separator.configure(fg_color="#343740")
        self.root.configure(cursor="sb_h_double_arrow")

    def panel_separator_mouse_leave(self, _):
        self.panel_separator.configure(fg_color="#23252A")
        self.root.configure(cursor="")

    def panel_separator_mouse_held(self, event):
        try:
            # muis knoppen
            if event.state == 256 or event.state == 512:
                if self.panel_start_x == 0:
                    self.panel_start_x = event.x

                offsetx = event.x - self.panel_start_x

                new_width = self.friend_list_panel.cget("width") + offsetx
                new_width = clamp(new_width, 120, self.root.winfo_width() - self.root.winfo_width() // 3)

                self.friend_list_panel.configure(width=new_width)
        except TypeError:
            self.panel_start_x = 0
            pass

    def toon_statistiek_window(self):
        if self.statistiek_window is not None:
            if self.statistiek_window.is_open():
                return

        self.statistiek_window = StatistiekWindow("Statistiek")

    def button_click(self):
        self.toon_statistiek_window()

    def show(self):
        self.root.mainloop()
