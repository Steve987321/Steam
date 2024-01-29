import time
import tkinter

import customtkinter as ctk
import SteamAPI
from PIL import Image
import sys

from dataclasses import dataclass

COL_BG = "#202228"
COL_HOVER = "#202227"
COL_BORDER = "#30627F"
COL_BORDER_BLACK = "#121216"
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


class StatistiekWindow:
    def __init__(self, window_name: str = "StatistiekWindow", window_size: str = "1080x1440"):
        self.root = ctk.CTkToplevel()
        self.root.title(window_name)
        self.root.geometry(window_size)

    def is_open(self):
        """Geeft aan of scherm bestaat"""
        return self.root.winfo_exists()

    def get_window(self):
        return self.root

    def steam_api_test(self):
        SteamAPI.test_steam_api()
        self.root.after(10000, self.steam_api_test)


class PlayerWidget:

    instances = []

    def __init__(self,
                 player,
                 master,
                 size: tuple[int, int],
                 window,
                 avatar_formaat: SteamAPI.AvatarFormaat = SteamAPI.AvatarFormaat.KLEIN):

        PlayerWidget.instances.append(self)
        self.window = window
        self.player_name = None
        self.player_status = SteamAPI.PlayerStatus.INVALID
        self.player_id = player.get_id()
        self.player_game_list = None
        self.size = size
        self.has_valid_image = False

        if player is None:
            status_str = "Invalid"
            self.player_status = SteamAPI.PlayerStatus.INVALID
            self.player_name = "-"
        else:
            self.player_status = player.get_status()
            status_str = self.player_status.name.lower()
            status_str = status_str.replace(status_str[0], status_str[0].upper(), 1)
            self.player_name = player.get_name()

        image = Image.new(mode="RGB", size=size)
        image = image.resize(size, Image.Resampling.LANCZOS)
        image_widget = ctk.CTkImage(size=size, dark_image=image)

        status_col = COL_DARK_BLUE
        status_name_col = COL_LIGHT_BLUE
        match self.player_status:
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

        self.frame = ctk.CTkFrame(master, width=1000, height=size[1] + 10, fg_color="transparent")
        self.frame.pack_propagate(False)

        self.button = ctk.CTkButton(self.frame, text="", width=size[0], height=size[1], image=image_widget,
                                    border_color=status_col,
                                    border_width=0, border_spacing=0, hover_color=COL_HOVER, fg_color="transparent",
                                    command=self.avatar_click)
        self.button.pack_propagate(False)

        self.name_label = ctk.CTkLabel(self.frame, text=self.player_name, text_color=status_name_col,
                                       font=("Arial", 15), height=0, anchor=ctk.W)

        self.status_label = ctk.CTkLabel(self.frame, text=status_str, text_color=status_col, font=("Arial", 12),
                                         height=0, anchor=ctk.W)

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

    def update_status(self, game: str, status: SteamAPI.PlayerStatus):
        self.player_status = status
        status_str = status.name.lower()
        status_str = status_str.replace(status_str[0], status_str[0].upper(), 1)

        match status:
            case SteamAPI.PlayerStatus.ONLINE:
                if game != "":
                    status_str = game
                    status_col = COL_STATUS_ONLINE_GREEN
                    status_name_col = COL_STATUS_NAME_PLAYING
                else:
                    status_col = COL_DARK_BLUE
                    status_name_col = COL_LIGHT_BLUE
            case SteamAPI.PlayerStatus.OFFLINE:
                status_col = COL_STATUS_OFFLINE_GREY
                status_name_col = COL_STATUS_OFFLINE_NAME_GREY
            case _:
                status_col = COL_STATUS_OFFLINE_GREY
                status_name_col = COL_STATUS_OFFLINE_NAME_GREY
                pass

        self.status_str = status_str

        self.status_label.configure(text=status_str, text_color=status_col)
        self.name_label.configure(text_color=status_name_col)

    def pack(self, **kwargs):
        self.frame.pack(**kwargs)

    def pack_forget(self):
        self.frame.pack_forget()

    def destroy(self):
        self.frame.destroy()

    def on_mouse_enter(self, _):
        if self.status_str.lower() == "online":
            self.frame.configure(fg_color="#23282F")
        else:
            self.frame.configure(fg_color="#0F0F12")

    def on_mouse_leave(self, _):
        self.frame.configure(fg_color="transparent")

    def on_mouse_press(self, _):
        if self.player_game_list is None:
            self.player_game_list = SteamAPI.Api.get_player_games_data(self.player_id)

        self.window.clear_info_panel()

        border_kleur = COL_BORDER
        if self.player_status == SteamAPI.PlayerStatus.OFFLINE:
            border_kleur = COL_GREY_WIDGET

        frame = ctk.CTkFrame(self.window.vriend_info, fg_color=COL_BG, border_width=1, border_color=border_kleur,
                             corner_radius=0)
        ctk.CTkButton(frame, text='X', width=25, height=25, command=self.window.reset_info_panel,
                      text_color=COL_LABEL, hover_color=COL_BG, fg_color=COL_BG).pack(anchor=ctk.NE, padx=2, pady=2)
        ctk.CTkLabel(frame, text=self.name_label.cget("text")).pack(pady=5, padx=5)
        game_list = ctk.CTkScrollableFrame(frame, fg_color=COL_BG, border_width=1, border_color=COL_BORDER)
        for game in self.player_game_list.values():
            print(game.get_name())
            image = ctk.CTkImage(game.get_capsule_img())
            label = ctk.CTkLabel(game_list, text=game.get_name(), image=image)
            label.pack(side=ctk.TOP)

        frame.pack_propagate(False)
        frame.pack(expand=True, side=ctk.TOP, fill=ctk.BOTH)
        game_list.pack(side=ctk.TOP)

    def avatar_click(self, _):
        pass


class DropDownButton(ctk.CTkFrame):
    dropdowns = []
    dropdowns_by_title = {}

    def __init__(self, master: any, title: str, widgets: list[PlayerWidget], **kwargs):
        self.master = master
        self.name = title
        self.widgets = widgets
        self.collapsed = False
        self.collapse_widget_color = COL_BG
        self.animation_steps = 0
        self.separator = SeparatorLine(self.master, COL_BORDER)

        DropDownButton.dropdowns.append(self)
        DropDownButton.dropdowns_by_title[title] = DropDownButton.dropdowns[-1]

        super().__init__(self.master, **kwargs, fg_color="transparent")

        self.title_widget = ctk.CTkLabel(self, text=title, anchor=ctk.W, text_color=COL_LABEL)
        self.collapse_widget = ctk.CTkLabel(self, text='-', font=("Arial", 14), anchor=ctk.W,
                                            text_color=self.collapse_widget_color)
        self.count_widget = ctk.CTkLabel(self, text=f"({len(widgets)})", font=("Arial", 12), anchor=ctk.W,
                                         text_color=COL_GREY)
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
            dp.separator.pack_forget()

            if len(dp.widgets) > 0:
                dp.pack(side=ctk.TOP, anchor=ctk.W, pady=0, padx=2, expand=True, fill=ctk.X)

                if not dp.collapsed:
                    for widget in dp.widgets:
                        widget.pack_forget()
                        widget.pack(side=ctk.TOP, anchor=ctk.W, pady=0)

                if i < len(DropDownButton.dropdowns):
                    if i == len(DropDownButton.dropdowns) - 1:
                        dp.separator.configure(fg_color=COL_STATUS_OFFLINE_GREY)

                    dp.separator.pack(pady=5)

    def update_count(self):
        self.count_widget.configure(text=f"({len(self.widgets)})")

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
        self.steamid = steamid

        self.steamAPIThread = SteamAPI.SteamApiThread(steamid)
        self.steamAPIThread.on_friend_list_change = self.on_fl_change
        self.steamAPIThread.on_steamid_status_change = self.on_player_change

        self.image_thread = SteamAPI.AvatarLoadThread({})

        self.panel_start_x = 0

        ctk.set_appearance_mode("System")

        self.statistiek_window = None

        self.root = ctk.ctk_tk.CTk()
        self.naam = naam

        self.root.geometry(f"{win_width}x{win_height}")
        self.root.title(naam)

        self.lplayer_avatar = None

        # Vrienden Lijst
        self.friend_list_panel_width = win_width // 3
        self.info_panel_width = win_width - self.friend_list_panel_width

        self.friend_list_panel = ctk.CTkFrame(self.root, width=self.friend_list_panel_width, fg_color=COL_BG,
                                              border_color=COL_BORDER, border_width=1, corner_radius=0)
        self.header_frame = ctk.CTkFrame(self.friend_list_panel, fg_color=COL_BG, height=80, corner_radius=0)
        self.separator = ctk.CTkFrame(self.friend_list_panel, fg_color=COL_GREY, height=25, corner_radius=0)
        self.friends_frame = ctk.CTkScrollableFrame(self.friend_list_panel, fg_color=COL_BG,
                                                    border_color=COL_BORDER, corner_radius=0)
        separator_label = ctk.CTkLabel(self.separator, text="VRIENDEN", font=("Arial", 12), text_color=COL_LABEL)
        separator_label.pack(padx=10, pady=5, side=ctk.LEFT)

        # Panel separator (x resizer)
        self.panel_separator = SeparatorLineV(self.root, "#23252A", border_width=1, corner_radius=0,
                                              border_color=COL_BORDER_BLACK)
        self.panel_separator.bind("<Enter>", self.panel_separator_mouse_enter)
        self.panel_separator.bind("<Leave>", self.panel_separator_mouse_leave)
        self.panel_separator.bind("<Motion>", self.panel_separator_mouse_held)

        self.info_panel = ctk.CTkFrame(self.root, width=self.info_panel_width, fg_color=COL_BG, border_color=COL_BORDER,
                                       border_width=0, corner_radius=0)
        statistiek_knop = ctk.CTkButton(self.info_panel, width=10, height=10, text="statistiek",
                                        command=self.toon_statistiek_window)
        statistiek_knop.pack(side=ctk.TOP, anchor=ctk.NW)
        self.vriend_info = ctk.CTkFrame(self.info_panel, width=self.info_panel_width, fg_color=COL_BG)
        self.vriend_info.pack(side=ctk.TOP, expand=True, fill=ctk.BOTH)

        self.progress_bar = ctk.CTkProgressBar(self.root, mode="indeterminate")
        self.progress_bar.place(relx=0.5, rely=0.5, anchor=ctk.CENTER)
        self.progress_bar.start()
        self.check_update()

    def on_player_change(self, status: SteamAPI.PlayerStatus, game: str):
        if self.lplayer_avatar is not None:
            self.lplayer_avatar.update_status(game, status)

    def on_fl_change(self, changed_friends):
        self.update_drop_downs(changed_friends)

    def show_widgets(self):
        self.header_frame.pack_propagate(False)
        self.separator.pack_propagate(False)
        self.header_frame.pack(side=ctk.TOP, fill=ctk.X)
        self.separator.pack(side=ctk.TOP, fill=ctk.X)

        self.lplayer_avatar = PlayerWidget(self.steamAPIThread.player, self.header_frame, (50, 50), self)
        self.lplayer_avatar.pack(side=ctk.TOP, pady=10, padx=5)
        self.friends_frame.pack(side=ctk.TOP, fill=ctk.BOTH, expand=True)

        self.friend_list_panel.pack_propagate(False)
        self.friend_list_panel.pack(side=ctk.LEFT, fill=ctk.BOTH)
        self.panel_separator.pack(side=ctk.LEFT)
        self.info_panel.pack(side=ctk.LEFT, fill=ctk.BOTH, expand=True)

    def check_update(self):
        if not self.steamAPIThread.has_data:
            if len(self.steamAPIThread.friends) > 0 and self.steamAPIThread.player is not None:
                if not self.image_thread.is_alive():
                    for friend in self.steamAPIThread.friends:
                        self.image_thread.avatars[friend] = None

                    self.image_thread.avatars[self.steamAPIThread.player] = None

                    self.image_thread.start()

            self.root.after(100, self.check_update)
        else:
            self.progress_bar.destroy()
            self.show_widgets()
            DropDownButton.reset()
            self.check_images()

    def update_drop_downs(self, changed_players: list[SteamAPI.Player]):
        d = {}

        if len(DropDownButton.dropdowns) == 0:
            friends_online_widgets = []
            friends_offline_widgets = []
            friends_games_widgets = {}  # game - widget

            friends_online = []
            friends_offline = []
            friends_away = []
            friends_games = {}

            for friend in changed_players:
                if friend.get_id() == self.steamid:
                    continue

                match friend.get_status():
                    case SteamAPI.PlayerStatus.ONLINE:
                        friends_online.append(friend)
                    case SteamAPI.PlayerStatus.OFFLINE:
                        friends_offline.append(friend)
                    case SteamAPI.PlayerStatus.AWAY:
                        friends_away.append(friend)

                if friend.get_playing_game() != "":
                    friends_games[friend.get_playing_game()] = friend

            for friend in friends_online:
                w = PlayerWidget(friend, self.friends_frame, (30, 30), self,
                                 SteamAPI.AvatarFormaat.KLEIN)

                if friend.get_playing_game() != "":
                    if friend.get_playing_game() not in friends_games_widgets.keys():
                        friends_games_widgets[friend.get_playing_game()] = [w]
                    else:
                        friends_games_widgets[friend.get_playing_game()].append(w)
                    continue
                # player is gewoon online zonder een game te spelen
                friends_online_widgets.append(w)

            for friend in friends_offline:
                w = PlayerWidget(friend, self.friends_frame, (30, 30), self,
                                 SteamAPI.AvatarFormaat.KLEIN)

                # player is gewoon online zonder een game te spelen
                friends_offline_widgets.append(w)

            online_games_dropdowns = []
            for game in friends_games_widgets.keys():
                # built button avatar widgets
                player_widgets = []
                for widget in friends_games_widgets[game]:
                    player_widgets.append(widget)

                dp = DropDownButton(self.friends_frame, game, player_widgets, height=25, corner_radius=0)
                online_games_dropdowns.append(dp)

            DropDownButton(self.friends_frame, f"Online Vrienden", friends_online_widgets, height=25, corner_radius=0)
            DropDownButton(self.friends_frame, f"Offline", friends_offline_widgets, height=25, corner_radius=0)

        else:
            for player in changed_players:
                d[player.get_name()] = player

            for dp in DropDownButton.dropdowns:
                for w in dp.widgets[:]:
                    if w.player_name in d.keys():
                        player = d[w.player_name]
                        new_player_status = player.get_status()
                        new_player_game = player.get_playing_game()

                        if w.player_status == SteamAPI.PlayerStatus.ONLINE or w.player_status == SteamAPI.PlayerStatus.AWAY:
                            if new_player_status == SteamAPI.PlayerStatus.OFFLINE:
                                # delete and move from dropdown section
                                dp.widgets.remove(w)
                                # w.frame.pack_forget()
                                DropDownButton.dropdowns_by_title["Offline"].widgets.append(w)
                        elif w.player_status == SteamAPI.PlayerStatus.OFFLINE:
                            if new_player_status == SteamAPI.PlayerStatus.ONLINE or w.player_status == SteamAPI.PlayerStatus.AWAY:
                                # delete and move from dropdown section
                                # w.frame.pack_forget()
                                dp.widgets.remove(w)
                                DropDownButton.dropdowns_by_title["Online Vrienden"].widgets.append(w)

                        if new_player_game != "" and new_player_game != w.player_status:
                            # w.frame.pack_forget()
                            dp.widgets.remove(w)
                            if new_player_game not in DropDownButton.dropdowns_by_title.keys():
                                DropDownButton(self.friends_frame, new_player_game, [w], height=25, corner_radius=0)
                            else:
                                DropDownButton.dropdowns_by_title[new_player_game].widgets.append(w)

                        w.update_status(new_player_game, new_player_status)

            for dp in DropDownButton.dropdowns:
                dp.update_count()

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
            print(self.statistiek_window.is_open())
            if self.statistiek_window.is_open():
                return

        self.statistiek_window = StatistiekWindow("Statistiek")

    def clear_info_panel(self):
        for child in self.vriend_info.winfo_children():
            child.destroy()

    def reset_info_panel(self):
        self.clear_info_panel()
        ctk.CTkLabel(self.vriend_info, text="Klik op een vriend om informatie te tonen").pack(fill=ctk.BOTH,
                                                                                              expand=True, padx=5,
                                                                                            pady=5)

    def check_images(self):
        if not self.image_thread.is_alive():
            if len(self.image_thread.avatars) == 0 or None in self.image_thread.avatars.values():
                self.image_thread.start()

        recheck = False
        for widget in PlayerWidget.instances:
            for player, img in self.image_thread.avatars.items():
                if img is None:
                    recheck = True
                else:
                    if widget.player_id == player.get_id():
                        widget.button.configure(
                            image=ctk.CTkImage(
                                dark_image=self.image_thread.avatars[player],
                                size=widget.size
                            )
                        )

        if recheck:
            self.root.after(500, self.check_images)

    def show(self):
        self.root.mainloop()