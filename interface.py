import tkinter as tk
from tkinter import ttk
import pyautogui
import keyboard
import threading
import time
import random
import ctypes
import os
import sys

# On importe la logique depuis l'autre fichier
from logic import BotVision


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


class WplaceBotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ARC PLACER")

        # --- CONFIG WINDOWS ---
        self.setup_dpi_awareness()
        self.setup_dark_mode_title_bar()

        # --- FENÊTRE ---
        self.root.geometry("260x450")
        self.root.resizable(True, True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.95)

        # --- ICONE ---
        try:
            img_path = resource_path(os.path.join("Assets", "Logo.png"))
            self.root.iconphoto(False, tk.PhotoImage(file=img_path))
        except Exception as e:
            print(f"Info: Pas de logo trouvé ({e})")

        # --- THEME ---
        self.bg_color = "#1e1e2e"
        self.fg_color = "#cdd6f4"
        self.accent_color = "#cba6f7"
        self.btn_color = "#313244"
        self.btn_active = "#45475a"
        self.highlight = "#89b4fa"
        self.border_color = "#45475a"

        self.root.configure(bg=self.bg_color)
        self.setup_styles()

        # --- VARIABLES ---
        self.running = False
        self.full_block_size = tk.IntVar(value=0)
        self.play_area = None
        self.target_color = tk.StringVar(value="51, 57, 65")
        self.tolerance = 15
        self.user_delay = tk.StringVar(value="0.2")
        self.status_var = tk.StringVar(value="En attente...")

        self.create_widgets()

        # --- HOTKEYS ---
        try:
            keyboard.add_hotkey('s', self.toggle_bot_safe)
        except Exception as e:
            print(f"Erreur Hotkey: {e}")

    # --- SETUP SYSTÈME ---
    def setup_dpi_awareness(self):
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except:
            pass

    def setup_dark_mode_title_bar(self):
        try:
            self.root.update()
            value = ctypes.c_int(2)
            ctypes.windll.dwmapi.DwmSetWindowAttribute(
                ctypes.windll.user32.GetParent(self.root.winfo_id()),
                20, ctypes.byref(value), ctypes.sizeof(value))
        except:
            pass

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure(".", background=self.bg_color, foreground=self.fg_color, font=("Segoe UI", 10), borderwidth=0,
                        focuscolor=self.bg_color)
        style.configure("TLabelframe", background=self.bg_color, foreground=self.accent_color,
                        bordercolor=self.border_color, lightcolor=self.bg_color, borderwidth=1, relief="solid")
        style.configure("TLabelframe.Label", background=self.bg_color, foreground=self.accent_color,
                        font=("Segoe UI", 9, "bold"))
        style.configure("TEntry", fieldbackground=self.btn_color, foreground="white", insertcolor="white",
                        bordercolor=self.bg_color, lightcolor=self.btn_color, borderwidth=0, relief="flat")
        style.configure("TButton", background=self.btn_color, foreground=self.fg_color, borderwidth=0,
                        font=("Segoe UI", 9), padding=6, relief="flat")
        style.map("TButton", background=[("active", self.btn_active), ("pressed", self.accent_color)],
                  foreground=[("pressed", self.bg_color)])
        style.configure("Start.TButton", background=self.accent_color, foreground=self.bg_color,
                        font=("Segoe UI", 11, "bold"), padding=10)
        style.map("Start.TButton", background=[("active", self.highlight), ("disabled", self.btn_color)],
                  foreground=[("disabled", "#6c7086")])

    def create_widgets(self):
        # Header
        header = tk.Frame(self.root, bg=self.bg_color)
        header.pack(fill="x", pady=(15, 5))
        tk.Label(header, text="ARC PLACER", font=("Segoe UI", 16, "bold"), bg=self.bg_color,
                 fg=self.accent_color).pack()
        tk.Label(header, text="v2.3 • Anti-Spam Fix", font=("Segoe UI", 8), bg=self.bg_color, fg="#6c7086").pack()

        # Paramètres
        f_params = ttk.LabelFrame(self.root, text="Paramètres", padding=10)
        f_params.pack(fill="x", padx=15, pady=5)

        tk.Label(f_params, text="Couleur (RGB) :", bg=self.bg_color, fg="#6c7086", font=("Segoe UI", 8)).pack(
            anchor="w")
        ttk.Entry(f_params, textvariable=self.target_color, justify="center").pack(fill="x", pady=(0, 8))

        tk.Label(f_params, text="Délai Clic (sec) :", bg=self.bg_color, fg="#6c7086", font=("Segoe UI", 8)).pack(
            anchor="w")
        ttk.Entry(f_params, textvariable=self.user_delay, justify="center").pack(fill="x")

        # Setup Buttons
        f_conf = ttk.LabelFrame(self.root, text="Setup", padding=10)
        f_conf.pack(fill="x", padx=15, pady=5)

        # MODIFICATION ICI : On assigne à self.btn_... pour pouvoir les désactiver
        self.btn_calib = ttk.Button(f_conf, text="1. Calibrer (Carré Plein)", command=self.start_auto_calib)
        self.btn_calib.pack(fill="x", pady=2)

        self.btn_zone = ttk.Button(f_conf, text="2. Zone de Jeu", command=self.start_zone_select)
        self.btn_zone.pack(fill="x", pady=2)

        self.lbl_info = tk.Label(f_conf, text="Non calibré", bg=self.bg_color, fg="#6c7086",
                                 font=("Segoe UI", 8, "italic"))
        self.lbl_info.pack(pady=(5, 0))

        # Actions
        f_act = tk.Frame(self.root, bg=self.bg_color)
        f_act.pack(fill="x", padx=15, pady=10)
        self.btn_start = ttk.Button(f_act, text="▶  START (Touche 'S')", command=self.toggle_bot, state="disabled",
                                    style="Start.TButton")
        self.btn_start.pack(fill="x")

        # Footer
        self.status_bar = tk.Label(self.root, textvariable=self.status_var, bg=self.btn_color, fg=self.fg_color,
                                   font=("Consolas", 8), anchor="w", padx=10, pady=5)
        self.status_bar.pack(side="bottom", fill="x")

    def log(self, message):
        self.status_var.set(f"> {message}")
        self.root.update_idletasks()

    # --- UTILITAIRE UI : Activer/Désactiver boutons Setup ---
    def toggle_setup_buttons(self, state):
        self.btn_calib.config(state=state)
        self.btn_zone.config(state=state)

    def cancel_overlay(self, event=None):
        # Appelé quand on fait Echap
        if hasattr(self, 'top') and self.top:
            self.top.destroy()
        self.toggle_setup_buttons("normal")
        self.log("Annulé.")

    # --- GESTION DU BOT ---
    def toggle_bot_safe(self):
        self.root.after(0, self.toggle_bot)

    def toggle_bot(self):
        if not self.running:
            self.running = True
            self.btn_start.config(text="⏹ STOP (Touche 'Q')", style="TButton")
            self.log("RUNNING... ('Q' pour stop)")
            threading.Thread(target=self.bot_loop, daemon=True).start()
        else:
            self.running = False
            self.btn_start.config(text="▶  START (Touche 'S')", style="Start.TButton")
            self.log("Arrêté.")

    def bot_loop(self):
        target_rgb = BotVision.parse_rgb(self.target_color.get())
        ref_size = self.full_block_size.get()
        tol = self.tolerance
        threshold = ref_size * 0.7
        scan_step = 4

        try:
            base_delay = float(self.user_delay.get().replace(',', '.'))
            if base_delay < 0.01: base_delay = 0.01
        except:
            base_delay = 0.1

        pic_test = pyautogui.screenshot()
        w_s, h_s = pic_test.size
        sx, sy, ex, ey = 20, 100, w_s - 20, h_s - 20
        if self.play_area:
            sx, sy, ex, ey = self.play_area

        while self.running:
            if keyboard.is_pressed('q'):
                self.root.after(0, self.toggle_bot)
                break

            pic = pyautogui.screenshot()
            pixels = pic.load()
            found = False
            processed_zones = []

            y = sy
            while y < ey:
                if not self.running: break
                x = sx
                while x < ex:
                    if keyboard.is_pressed('q'): break

                    if self.is_in_processed_zone(x, y, processed_zones):
                        x += scan_step;
                        continue

                    if not BotVision.check_match(pixels[x, y], target_rgb, tol):
                        x += scan_step;
                        continue

                    blob_w, blob_h, bbox = BotVision.measure_blob_at(pixels, x, y, w_s, h_s, target_rgb, tol)
                    blob_size = max(blob_w, blob_h)
                    processed_zones.append(bbox)

                    if blob_size < threshold:
                        cx, cy = (bbox[0] + bbox[2]) // 2, (bbox[1] + bbox[3]) // 2
                        if sx <= cx <= ex and sy <= cy <= ey:
                            ox, oy = random.randint(-1, 1), random.randint(-1, 1)
                            pyautogui.click(cx + ox, cy + oy)

                            actual_delay = base_delay + random.uniform(0, base_delay * 0.3)
                            time.sleep(actual_delay)

                            found = True

                    x = bbox[2] + 2
                y += scan_step

            if not found: time.sleep(0.5)

    def is_in_processed_zone(self, x, y, zones):
        for z in zones:
            if z[0] <= x <= z[2] and z[1] <= y <= z[3]: return True
        return False

    # --- CALIBRATION ---
    def start_zone_select(self):
        self.toggle_setup_buttons("disabled")  # On bloque les boutons
        self.log("Encadre la zone de jeu...")

        self.top = tk.Toplevel(self.root)
        self.top.attributes('-fullscreen', True);
        self.top.attributes('-alpha', 0.3)
        self.top.config(cursor="crosshair")

        self.canvas = tk.Canvas(self.top, bg="black", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.canvas.bind("<ButtonPress-1>",
                         lambda e: setattr(self, 'start_x', e.x) or setattr(self, 'start_y', e.y) or setattr(self,
                                                                                                             'rect_id',
                                                                                                             self.canvas.create_rectangle(
                                                                                                                 e.x,
                                                                                                                 e.y,
                                                                                                                 e.x,
                                                                                                                 e.y,
                                                                                                                 outline="#cba6f7",
                                                                                                                 width=2,
                                                                                                                 fill="#cba6f7",
                                                                                                                 stipple="gray25")))
        self.canvas.bind("<B1-Motion>",
                         lambda e: self.canvas.coords(self.rect_id, self.start_x, self.start_y, e.x, e.y))
        self.canvas.bind("<ButtonRelease-1>", self.on_zone_end)

        # On lie Echap à la fonction qui nettoie tout
        self.top.bind("<Escape>", self.cancel_overlay)

    def on_zone_end(self, event):
        self.play_area = (min(self.start_x, event.x), min(self.start_y, event.y), max(self.start_x, event.x),
                          max(self.start_y, event.y))
        self.top.destroy()
        w, h = self.play_area[2] - self.play_area[0], self.play_area[3] - self.play_area[1]

        self.toggle_setup_buttons("normal")  # On débloque
        self.log("Zone définie !")
        self.update_info_label()

    def start_auto_calib(self):
        self.toggle_setup_buttons("disabled")  # On bloque
        self.log("Overlay actif. Clique sur un PLEIN.")

        self.top = tk.Toplevel(self.root)
        self.top.attributes('-fullscreen', True);
        self.top.attributes('-alpha', 0.3)
        self.top.config(cursor="crosshair")

        self.canvas = tk.Canvas(self.top, bg="white", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<ButtonRelease-1>", self.run_calib_scan)

        self.top.bind("<Escape>", self.cancel_overlay)

    def run_calib_scan(self, event):
        self.root.update();
        time.sleep(0.1)
        pic = pyautogui.screenshot()
        target = pic.load()[event.x, event.y]

        width, height, bbox = BotVision.measure_blob_at(pic.load(), event.x, event.y, pic.width, pic.height, target, 30)

        self.canvas.delete("all")
        self.canvas.create_rectangle(bbox[0], bbox[1], bbox[2], bbox[3], outline="#ff0000", width=3)
        self.root.update()

        size = max(width, height)
        if size < 5:
            self.log("Erreur: Trop petit.")
            self.root.after(1000,
                            lambda: (self.top.destroy(), self.toggle_setup_buttons("normal")))  # On débloque aussi ici
            return

        time.sleep(0.5);
        self.top.destroy()

        self.toggle_setup_buttons("normal")  # On débloque succès
        self.full_block_size.set(size)
        self.update_info_label()
        self.btn_start.config(state="normal")
        self.log(f"Calibré ! Ref: {size}px.")

    def update_info_label(self):
        txt = f"Ref: {self.full_block_size.get()}px"
        if self.play_area:
            w, h = self.play_area[2] - self.play_area[0], self.play_area[3] - self.play_area[1]
            txt += f" | Zone: {w}x{h}"
        self.lbl_info.config(text=txt, fg="#a6e3a1")