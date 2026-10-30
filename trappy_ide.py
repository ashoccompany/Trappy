# =====================================================================
# TRAPPY IDE - OFFICIAL INTEGRATED DEVELOPMENT ENVIRONMENT (v1.0.0 GLOBAL)
# Official Community & Source Links:
# Discord: https://discord.gg/WRTG3spWH (Official Community Headquarters)
# GitHub:  https://github.com/ashoccompany/Trappy
# X:       https://x.com/tr4ppyai
# Code Editor, F1 Offline Docs Browser, Quick Code Assist & Budget Runner
# =====================================================================

import sys
import os
import re
import subprocess
import threading
import webbrowser
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

import trappy

# Trappy Theme Colors
BG_DARK = "#18181b"
BG_SIDE = "#202024"
BG_LINKS = "#141417"
BG_EDITOR = "#121214"
TEXT_COLOR = "#f4f4f5"
ACCENT_COLOR = "#06b6d4"   # Cyan
KEYWORD_COLOR = "#f97316"  # Orange
STRING_COLOR = "#eab308"   # Yellow
COMMENT_COLOR = "#22c55e"  # Green
NUMBER_COLOR = "#38bdf8"   # Light Blue
GHOST_COLOR = "#71717a"    # Grey ghost text for Quick Code Assist
DISCORD_COLOR = "#5865F2"  # Discord Blurple

# Vocabulary for Quick Code Assist
ASSIST_KEYWORDS = [
    # Program structure
    "trst", "tren",
    # UI and Windowing
    "cwin", "sbgwin", "label", "regle", "circ", "line", "btn", "inp",
    # 3D Wireframe Graphics (v1.0)
    "cube3d", "line3d", "sphere3d", "pyramid3d",
    # Loops and Controls
    "gloop", "fps calm", "fps lock", "rep", "loop", "srep", "sloop", "each", "in",
    # Declarations
    "add_obj", "add_var", "add_func",
    # Packets, Discord & Universal Connectivity (v1.0)
    "discord_webhook", "json_parse", "json_dump",
    "pack_data", "unpack_data", "cli_connect", "cli_send", "cli_recv", "cli_close",
    "srv_listen", "srv_accept", "http_get", "http_post", "download",
    "ws_connect", "ws_send", "ws_recv", "ws_close",
    # Dictionaries & Collections (v1.0)
    "dict", "dset", "dget", "dkeys",
    "lst", "lget", "lset", "llen", "lpush", "lpop",
    # Universal File I/O Suite (v1.0)
    "file_write", "file_read", "file_append", "file_exists", "file_delete", "dir_list",
    # Conditions and Logic
    "ifr", "then", "else", "grt", "lss", "sm",
    # Text, Variables & Math
    "txt", "tit", "gan", "answ", "rt", "mh", "eq",
    # Math, Physics & Collisions (v1.0)
    "sqrt", "dist", "clamp", "pow", "abs", "sin", "cos", "rnd",
    "box_hit", "vec_add", "vec_mag",
    # OS & Low-Level Memory
    "mem_alloc", "mem_write", "mem_read", "sys_exec", "sys_env",
    # Audio
    "synth", "beep", "play", "key",
    # Functions
    "fmh", "ftxt", "flist", "fweb", "fcli", "fapp", "fdel", "fui", "f3d", "fos",
    # General
    "true", "false", "import", "exit"
]

HIGHLIGHT_KEYWORDS = list(set(ASSIST_KEYWORDS + [
    "fps", "calm", "lock", "unlock", "psed", "changed", "flkey", "mousel", "mouser"
]))

# Built-in Offline Documentation Database for F1 Help Window
MANUAL_DATABASE = [
    ("discord_webhook", "discord_webhook url:msg tit status", "Sends a live notification to a Discord channel via Webhook. Returns HTTP status 204 or error.", 'discord_webhook "https://discord.com/api/webhooks/...":"Player won!" tit res'),
    ("dict", "dict tit var_name", "Initializes a fast key-value dictionary hash map.", 'dict tit inventory\ndset inventory:"gold":500\ndget inventory:"gold" tit gold'),
    ("dset", "dset dict:key:val", "Stores a key-value pair in a dictionary.", 'dset player:"name":"Alex"'),
    ("dget", "dget dict:key tit var", "Retrieves a value from a dictionary by its key.", 'dget player:"name" tit hero_name'),
    ("dkeys", "dkeys dict tit var", "Retrieves a list of all keys inside a dictionary.", 'dkeys player tit key_list'),
    ("lget", "lget list:index tit var", "Gets item from a list at the specified 0-based index.", 'lget scores:0 tit top_score'),
    ("lset", "lset list:index:val", "Updates item in a list at the specified index.", 'lset scores:0:999'),
    ("lpush", "lpush list:val", "Appends a new value to the end of a list.", 'lpush inventory:"Potion"'),
    ("llen", "llen list tit var", "Returns total number of items in a list.", 'llen inventory tit total_items'),
    ("file_write", "file_write path:content", "Writes text data into an offline file on local storage.", 'file_write "save.dat":"score=500"'),
    ("file_read", "file_read path tit var", "Reads full text content from a local file.", 'file_read "save.dat" tit data'),
    ("file_exists", "file_exists path tit var", "Returns 1 if file exists on disk, 0 otherwise.", 'file_exists "save.dat" tit exists_flag'),
    ("file_delete", "file_delete path", "Deletes a local file if it exists.", 'file_delete "temp.dat"'),
    ("json_dump", "json_dump obj tit var", "Serializes a dictionary or list into a clean JSON string.", 'json_dump player_data tit json_str'),
    ("json_parse", "json_parse json_str tit var", "Deserializes a JSON string into a Trappy dictionary.", 'json_parse json_str tit player_data'),
    ("cube3d", "cube3d x:y:z size rx:ry color", "Renders a 3D wireframe box with perspective projection.", 'cube3d 300:225:0 140 rot_x:rot_y cyan'),
    ("sphere3d", "sphere3d x:y:z radius rx:ry color", "Renders a 3D celestial wireframe sphere with 3 axis rings.", 'sphere3d 350:250:0 60 rot_x:rot_y green'),
    ("pyramid3d", "pyramid3d x:y:z size rx:ry color", "Renders a 3D 4-sided wireframe pyramid with apex.", 'pyramid3d 500:250:0 100 rot_x:rot_y yellow'),
    ("box_hit", "box_hit x1:y1:w1:h1 x2:y2:w2:h2 tit var", "Calculates 2D AABB bounding box collision (1 if hit, 0 if not).", 'box_hit player.x:player.y:32:32 200:100:64:64 tit collided'),
    ("vec_add", "vec_add x1:y1 x2:y2 tit var", "Calculates vector sum [x1+x2, y1+y2].", 'vec_add 10:20 5:5 tit new_pos'),
    ("vec_mag", "vec_mag x:y tit var", "Calculates vector magnitude / length.", 'vec_mag 3:4 tit speed'),
    ("cli_connect", 'cli_connect "host":port tit var', "Connects client socket (use 'loopback' for offline testing).", 'cli_connect "loopback":8080 tit client'),
    ("cli_send", "cli_send client:payload", "Sends network stream to connected server or loopback.", 'cli_send client:packet_data'),
    ("cli_recv", "cli_recv client tit var", "Non-blocking receive from network socket.", 'cli_recv client tit reply'),
    ("synth", "synth wave:freq:dur", "Chiptune / wave tone synthesizer on budget hardware.", 'synth "square":440:150'),
    ("cwin", 'cwin "Title" width:height main', "Creates a hardware-accelerated canvas game window.", 'cwin "My Game" 600:400 main'),
    ("fps calm", "fps calm", "Enables hardware-calm VSync to save CPU and battery.", 'fps calm'),
    ("gloop", "gloop ... tren", "Hardware-synchronized continuous game loop.", 'gloop\n    circ player.x:player.y 16 cyan\ntren')
]


class TrappyIDE:
    def __init__(self, root):
        self.root = root
        self.root.title("Trappy IDE - Official Code Studio (v1.0.0 Global Release)")
        self.root.geometry("1060x730")
        self.root.configure(bg=BG_DARK)

        self.current_file = None
        self.ghost_text = ""
        self.highlight_job = None
        self.manual_win = None
        self.is_focused = True

        self._create_ui()
        self._setup_highlighting()
        self.load_default_code()

        # Keyboard shortcuts
        self.root.bind("<F1>", lambda e: self.open_manual_window())
        self.root.bind("<F5>", lambda e: self.run_code())
        self.root.bind("<F6>", lambda e: self.debug_code())
        self.root.bind("<Control-s>", lambda e: self.save_file())
        self.root.bind("<Control-o>", lambda e: self.open_file())

        self.root.bind("<FocusIn>", lambda e: self._on_focus(True))
        self.root.bind("<FocusOut>", lambda e: self._on_focus(False))

    def _on_focus(self, focused):
        self.is_focused = focused

    def _create_ui(self):
        # 1. Top Action Toolbar
        toolbar = tk.Frame(self.root, bg=BG_SIDE, height=45)
        toolbar.pack(fill="x", side="top")

        btn_style = {"bg": "#27272a", "fg": TEXT_COLOR, "font": ("Consolas", 10, "bold"), "bd": 0, "padx": 10, "pady": 6}

        tk.Button(toolbar, text="[New]", command=self.new_file, **btn_style).pack(side="left", padx=3, pady=5)
        tk.Button(toolbar, text="[Open]", command=self.open_file, **btn_style).pack(side="left", padx=3, pady=5)
        tk.Button(toolbar, text="[Save (Ctrl+S)]", command=self.save_file, **btn_style).pack(side="left", padx=3, pady=5)

        # F1 Help Button
        doc_btn = dict(btn_style)
        doc_btn["bg"] = "#0d9488"  # Teal
        tk.Button(toolbar, text="[Manual / Docs (F1)]", command=self.open_manual_window, **doc_btn).pack(side="left", padx=4, pady=5)

        # Example selector dropdown
        self.example_var = tk.StringVar(value="Load Example...")
        examples = [
            "3D Multi-Shapes (Cube, Sphere, Pyramid)",
            "Discord & Online Connect Demo",
            "File I/O & Save System Demo",
            "2D Arcade Game Demo",
            "RPG Stats & Inventory Demo",
            "Packets & Client Demo",
            "Web & Internet Demo",
            "Language Showcase Demo"
        ]
        dropdown = ttk.OptionMenu(toolbar, self.example_var, "Load Example...", *examples, command=self.load_example)
        dropdown.pack(side="left", padx=6, pady=5)

        # Discord Headquarters Button
        discord_btn = dict(btn_style)
        discord_btn["bg"] = DISCORD_COLOR
        tk.Button(toolbar, text="[Discord Community]", command=lambda: webbrowser.open_new_tab("https://discord.gg/WRTG3spWH"), **discord_btn).pack(side="left", padx=4, pady=5)

        # Community Hub Button
        hub_btn = dict(btn_style)
        hub_btn["bg"] = "#0284c7"  # Sky blue
        tk.Button(toolbar, text="[Community Hub (TPM)]", command=self.open_community_hub, **hub_btn).pack(side="left", padx=4, pady=5)

        # Action Buttons
        debug_btn = dict(btn_style)
        debug_btn["bg"] = "#4338ca"  # Indigo
        tk.Button(toolbar, text="[Debug / Check (F6)]", command=self.debug_code, **debug_btn).pack(side="right", padx=6, pady=5)

        run_btn = dict(btn_style)
        run_btn["bg"] = "#059669"  # Emerald green
        tk.Button(toolbar, text="[RUN TRAPPY (F5)]", command=self.run_code, **run_btn).pack(side="right", padx=6, pady=5)

        # 2. Watermark Links Bar
        links_bar = tk.Frame(self.root, bg=BG_LINKS, height=28)
        links_bar.pack(fill="x", side="top")

        tk.Label(links_bar, text="OFFICIAL CHANNELS:", bg=BG_LINKS, fg="#71717a", font=("Consolas", 8, "bold")).pack(side="left", padx=(10, 4), pady=3)

        discord_link = tk.Label(links_bar, text="Discord (Main): discord.gg/WRTG3spWH", bg=BG_LINKS, fg="#a78bfa", font=("Consolas", 8, "underline"), cursor="hand2")
        discord_link.pack(side="left", padx=8, pady=3)
        discord_link.bind("<Button-1>", lambda e: webbrowser.open_new_tab("https://discord.gg/WRTG3spWH"))

        github_link = tk.Label(links_bar, text="GitHub: github.com/ashoccompany/Trappy", bg=BG_LINKS, fg="#38bdf8", font=("Consolas", 8, "underline"), cursor="hand2")
        github_link.pack(side="left", padx=8, pady=3)
        github_link.bind("<Button-1>", lambda e: webbrowser.open_new_tab("https://github.com/ashoccompany/Trappy"))

        x_link = tk.Label(links_bar, text="X (Twitter): x.com/tr4ppyai", bg=BG_LINKS, fg="#34d399", font=("Consolas", 8, "underline"), cursor="hand2")
        x_link.pack(side="left", padx=8, pady=3)
        x_link.bind("<Button-1>", lambda e: webbrowser.open_new_tab("https://x.com/tr4ppyai"))

        assist_badge = tk.Label(links_bar, text="[Quick Assist: Active | F1: Manual]", bg=BG_LINKS, fg="#94a3b8", font=("Consolas", 8))
        assist_badge.pack(side="right", padx=10, pady=3)

        # 3. Main Area (Split into Editor and Console)
        paned = tk.PanedWindow(self.root, orient="vertical", bg=BG_DARK, sashwidth=4)
        paned.pack(fill="both", expand=True)

        # Editor Frame
        editor_frame = tk.Frame(paned, bg=BG_EDITOR)
        paned.add(editor_frame, height=450)

        # Line Numbers
        self.line_numbers = tk.Text(editor_frame, width=4, bg=BG_SIDE, fg="#71717a", font=("Consolas", 12), bd=0, padx=4, pady=6)
        self.line_numbers.pack(side="left", fill="y")
        self.line_numbers.configure(state="disabled")

        # Code Area
        self.code_text = tk.Text(editor_frame, bg=BG_EDITOR, fg=TEXT_COLOR, insertbackground="white", font=("Consolas", 12), bd=0, padx=8, pady=6, undo=True)
        self.code_text.pack(side="left", fill="both", expand=True)

        scroll = tk.Scrollbar(editor_frame, command=self.code_text.yview)
        scroll.pack(side="right", fill="y")
        self.code_text.configure(yscrollcommand=scroll.set)

        # Editor Key Events for Quick Assist & Editing
        self.code_text.bind("<KeyPress>", self._on_key_press)
        self.code_text.bind("<KeyRelease>", self._on_key_release)
        self.code_text.bind("<Button-1>", lambda e: self.clear_ghost())

        # Console Frame
        console_frame = tk.Frame(paned, bg=BG_DARK)
        paned.add(console_frame, height=200)

        console_bar = tk.Frame(console_frame, bg=BG_SIDE)
        console_bar.pack(fill="x")
        tk.Label(console_bar, text="OUTPUT & TERMINAL CONSOLE", bg=BG_SIDE, fg="#a1a1aa", font=("Consolas", 9, "bold")).pack(side="left", padx=8, pady=2)
        tk.Button(console_bar, text="[Clear]", bg=BG_SIDE, fg="#a1a1aa", font=("Consolas", 8), bd=0, command=self.clear_console).pack(side="right", padx=8)

        self.console = tk.Text(console_frame, bg="#09090b", fg="#22c55e", font=("Consolas", 10), bd=0, padx=8, pady=6)
        self.console.pack(fill="both", expand=True)

        # Status Bar
        self.status = tk.Label(
            self.root,
            text="Ready | Trappy v1.0.0 Global Release | Discord: discord.gg/WRTG3spWH | Press F1 for Docs, F5 to Run",
            bg=BG_SIDE,
            fg="#a1a1aa",
            font=("Consolas", 9),
            anchor="w",
            padx=8,
            pady=2
        )
        self.status.pack(fill="x", side="bottom")

    def _setup_highlighting(self):
        self.code_text.tag_configure("keyword", foreground=KEYWORD_COLOR, font=("Consolas", 12, "bold"))
        self.code_text.tag_configure("string", foreground=STRING_COLOR)
        self.code_text.tag_configure("comment", foreground=COMMENT_COLOR, font=("Consolas", 12, "italic"))
        self.code_text.tag_configure("number", foreground=NUMBER_COLOR)
        self.code_text.tag_configure("accent", foreground=ACCENT_COLOR, font=("Consolas", 12, "bold"))
        self.code_text.tag_configure("ghost", foreground=GHOST_COLOR)

    def _schedule_highlight(self):
        if not self.is_focused:
            return
        if self.highlight_job:
            self.root.after_cancel(self.highlight_job)
        self.highlight_job = self.root.after(250, self.highlight_syntax)

    def highlight_syntax(self):
        self.highlight_job = None
        for tag in ("keyword", "string", "comment", "number", "accent"):
            self.code_text.tag_remove(tag, "1.0", "end")

        content = self.code_text.get("1.0", "end-1c")
        if not content:
            return

        for m in re.finditer(r'#.*$', content, re.MULTILINE):
            self.code_text.tag_add("comment", f"1.0+{m.start()}c", f"1.0+{m.end()}c")

        for m in re.finditer(r'"[^"\n]*"', content):
            self.code_text.tag_add("string", f"1.0+{m.start()}c", f"1.0+{m.end()}c")

        for m in re.finditer(r'\b\d+(\.\d+)?\b', content):
            self.code_text.tag_add("number", f"1.0+{m.start()}c", f"1.0+{m.end()}c")

        for m in re.finditer(r'\b(trst|tren)\b', content, re.IGNORECASE):
            self.code_text.tag_add("accent", f"1.0+{m.start()}c", f"1.0+{m.end()}c")

        kw_pattern = r'\b(' + '|'.join(re.escape(k) for k in HIGHLIGHT_KEYWORDS) + r')\b'
        for m in re.finditer(kw_pattern, content):
            self.code_text.tag_add("keyword", f"1.0+{m.start()}c", f"1.0+{m.end()}c")

    # =====================================================================
    # F1 BUILT-IN OFFLINE MANUAL & COMMAND REFERENCE BROWSER
    # =====================================================================
    def open_manual_window(self):
        if self.manual_win and tk.Toplevel.winfo_exists(self.manual_win):
            self.manual_win.lift()
            return

        self.manual_win = tk.Toplevel(self.root)
        self.manual_win.title("Trappy Command Reference & Manual (Press F1)")
        self.manual_win.geometry("700x550")
        self.manual_win.configure(bg=BG_DARK)

        # Header Search Frame
        search_frame = tk.Frame(self.manual_win, bg=BG_SIDE, padx=10, pady=8)
        search_frame.pack(fill="x", side="top")

        tk.Label(search_frame, text="Search Command:", bg=BG_SIDE, fg=TEXT_COLOR, font=("Consolas", 10, "bold")).pack(side="left")
        search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=search_var, bg=BG_EDITOR, fg=TEXT_COLOR, insertbackground="white", font=("Consolas", 10), width=28)
        search_entry.pack(side="left", padx=8)
        search_entry.focus_set()

        tk.Label(search_frame, text="Discord Help: discord.gg/WRTG3spWH", bg=BG_SIDE, fg="#a78bfa", font=("Consolas", 9)).pack(side="right")

        # Split frame: List of commands on left, details on right
        content_paned = tk.PanedWindow(self.manual_win, orient="horizontal", bg=BG_DARK, sashwidth=4)
        content_paned.pack(fill="both", expand=True, padx=8, pady=8)

        # Left Listbox
        list_frame = tk.Frame(content_paned, bg=BG_EDITOR)
        content_paned.add(list_frame, width=220)

        cmd_listbox = tk.Listbox(list_frame, bg=BG_EDITOR, fg=TEXT_COLOR, selectbackground="#0284c7", selectforeground="white", font=("Consolas", 11), bd=0)
        cmd_listbox.pack(fill="both", expand=True, side="left")
        list_scroll = tk.Scrollbar(list_frame, command=cmd_listbox.yview)
        list_scroll.pack(side="right", fill="y")
        cmd_listbox.configure(yscrollcommand=list_scroll.set)

        # Right Detail View
        detail_frame = tk.Frame(content_paned, bg=BG_SIDE, padx=12, pady=10)
        content_paned.add(detail_frame, width=460)

        title_lbl = tk.Label(detail_frame, text="Command Name", bg=BG_SIDE, fg=ACCENT_COLOR, font=("Consolas", 13, "bold"), anchor="w")
        title_lbl.pack(fill="x")

        syntax_lbl = tk.Label(detail_frame, text="Syntax: ...", bg="#18181b", fg=KEYWORD_COLOR, font=("Consolas", 10, "bold"), anchor="w", padx=6, pady=4)
        syntax_lbl.pack(fill="x", pady=6)

        desc_txt = tk.Text(detail_frame, bg=BG_SIDE, fg=TEXT_COLOR, font=("Consolas", 10), bd=0, wrap="word", height=5)
        desc_txt.pack(fill="x", pady=4)
        desc_txt.configure(state="disabled")

        tk.Label(detail_frame, text="Example Code:", bg=BG_SIDE, fg="#a1a1aa", font=("Consolas", 9, "bold"), anchor="w").pack(fill="x", pady=(8, 2))
        example_box = tk.Text(detail_frame, bg=BG_EDITOR, fg=COMMENT_COLOR, font=("Consolas", 10), bd=0, height=8)
        example_box.pack(fill="both", expand=True, pady=4)

        def insert_current_example():
            code_snippet = example_box.get("1.0", "end-1c").strip()
            if code_snippet:
                self.code_text.insert("insert", "\n" + code_snippet + "\n")
                self.manual_win.destroy()
                self.code_text.focus_set()
                self.update_line_numbers()
                self._schedule_highlight()

        tk.Button(detail_frame, text="[Insert Example into Editor]", command=insert_current_example, bg="#059669", fg="white", font=("Consolas", 10, "bold"), bd=0, pady=6).pack(fill="x", pady=4)

        current_items = list(MANUAL_DATABASE)

        def refresh_list():
            query = search_var.get().strip().lower()
            cmd_listbox.delete(0, "end")
            nonlocal current_items
            current_items = [entry for entry in MANUAL_DATABASE if query in entry[0].lower() or query in entry[2].lower()]
            for entry in current_items:
                cmd_listbox.insert("end", entry[0])
            if current_items:
                cmd_listbox.select_set(0)
                display_entry(current_items[0])

        def display_entry(entry):
            name, syntax, desc, example = entry
            title_lbl.config(text=name.upper())
            syntax_lbl.config(text=f"Syntax: {syntax}")
            desc_txt.configure(state="normal")
            desc_txt.delete("1.0", "end")
            desc_txt.insert("1.0", desc)
            desc_txt.configure(state="disabled")
            example_box.delete("1.0", "end")
            example_box.insert("1.0", example)

        def on_select(evt):
            sel = cmd_listbox.curselection()
            if sel and sel[0] < len(current_items):
                display_entry(current_items[sel[0]])

        cmd_listbox.bind("<<ListboxSelect>>", on_select)
        search_var.trace_add("write", lambda *args: refresh_list())
        refresh_list()

    # =====================================================================
    # QUICK CODE ASSIST ENGINE
    # =====================================================================
    def clear_ghost(self):
        if not self.ghost_text:
            return
        ranges = self.code_text.tag_ranges("ghost")
        if ranges:
            self.code_text.delete(ranges[0], ranges[1])
        self.ghost_text = ""

    def accept_ghost(self):
        if not self.ghost_text:
            return False
        ranges = self.code_text.tag_ranges("ghost")
        if ranges:
            self.code_text.tag_remove("ghost", ranges[0], ranges[1])
            self.code_text.mark_set("insert", ranges[1])
            self.ghost_text = ""
            self.update_line_numbers()
            self._schedule_highlight()
            return True
        return False

    def _on_key_press(self, event):
        if event.keysym == "Tab":
            if self.ghost_text:
                self.accept_ghost()
                return "break"
            else:
                self.code_text.insert("insert", "    ")
                return "break"
        elif event.keysym == "Right":
            if self.ghost_text:
                self.accept_ghost()
                return "break"
        elif event.keysym == "Escape":
            if self.ghost_text:
                self.clear_ghost()
                return "break"
        elif event.keysym in ("Shift_L", "Shift_R", "Control_L", "Control_R", "Alt_L", "Alt_R", "Caps_Lock"):
            return
        else:
            self.clear_ghost()

    def _on_key_release(self, event):
        self.update_line_numbers()
        self._schedule_highlight()

        if event.keysym in ("Shift_L", "Shift_R", "Control_L", "Control_R", "Alt_L", "Alt_R", 
                            "Caps_Lock", "Tab", "Return", "Escape", "Up", "Down", "Left", 
                            "Home", "End", "Prior", "Next"):
            return

        self._check_code_assist()

    def _check_code_assist(self):
        self.clear_ghost()
        try:
            cur = self.code_text.index("insert")
            after_char = self.code_text.get(cur, f"{cur}+1c")
            if after_char and (after_char.isalnum() or after_char == "_"):
                return

            line_start = f"{cur.split('.')[0]}.0"
            line_prefix = self.code_text.get(line_start, cur)
            m = re.search(r'([a-zA-Z0-9_]+)$', line_prefix)
            if not m:
                return
            prefix = m.group(1)
            if len(prefix) < 2:
                return

            prefix_lower = prefix.lower()
            candidates = [k for k in ASSIST_KEYWORDS if k.lower().startswith(prefix_lower) and k.lower() != prefix_lower]
            if not candidates:
                return

            candidates.sort(key=lambda x: (len(x), x))
            best = candidates[0]
            suffix = best[len(prefix):]
            if prefix.isupper():
                suffix = suffix.upper()

            self.ghost_text = suffix
            self.code_text.insert(cur, suffix, "ghost")
            self.code_text.mark_set("insert", cur)
        except Exception:
            pass

    def get_clean_code(self):
        self.clear_ghost()
        return self.code_text.get("1.0", "end-1c")

    def update_line_numbers(self):
        lines = self.code_text.get("1.0", "end-1c").count("\n") + 1
        self.line_numbers.configure(state="normal")
        self.line_numbers.delete("1.0", "end")
        self.line_numbers.insert("1.0", "\n".join(str(i) for i in range(1, lines + 1)))
        self.line_numbers.configure(state="disabled")

    def log(self, text, is_err=False):
        self.console.insert("end", text + "\n")
        self.console.see("end")

    def clear_console(self):
        self.console.delete("1.0", "end")

    def new_file(self):
        self.clear_ghost()
        self.code_text.delete("1.0", "end")
        self.code_text.insert("1.0", "trst\n    # Your Trappy Code here\n    gan \"Hello from Trappy IDE!\"\ntren\n")
        self.current_file = None
        self.status.config(text="New file created.")
        self.update_line_numbers()
        self._schedule_highlight()

    def open_file(self):
        path = filedialog.askopenfilename(filetypes=[("Trappy Files", "*.trappy"), ("All Files", "*.*")])
        if path:
            self.clear_ghost()
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            self.code_text.delete("1.0", "end")
            self.code_text.insert("1.0", content)
            self.current_file = path
            self.status.config(text=f"Loaded: {os.path.basename(path)}")
            self.update_line_numbers()
            self._schedule_highlight()

    def save_file(self):
        if not self.current_file:
            path = filedialog.asksaveasfilename(defaultextension=".trappy", filetypes=[("Trappy Files", "*.trappy")])
            if not path:
                return
            self.current_file = path
        clean_code = self.get_clean_code()
        with open(self.current_file, "w", encoding="utf-8") as f:
            f.write(clean_code)
        self.status.config(text=f"Saved: {os.path.basename(self.current_file)}")

    def load_example(self, choice):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        target_map = {
            "3D Multi-Shapes (Cube, Sphere, Pyramid)": "shapes3d_demo.trappy",
            "Discord & Online Connect Demo": "discord_demo.trappy",
            "File I/O & Save System Demo": "file_io_demo.trappy",
            "2D Arcade Game Demo": "game_demo.trappy",
            "RPG Stats & Inventory Demo": "advanced_demo.trappy",
            "Packets & Client Demo": "packets_client_demo.trappy",
            "Web & Internet Demo": "web_demo.trappy",
            "Language Showcase Demo": "main.trappy"
        }
        if choice in target_map:
            path = os.path.join(base_dir, target_map[choice])
            if os.path.exists(path):
                self.clear_ghost()
                with open(path, "r", encoding="utf-8") as f:
                    self.code_text.delete("1.0", "end")
                    self.code_text.insert("1.0", f.read())
                self.current_file = path
                self.status.config(text=f"Loaded Example: {target_map[choice]}")
                self.update_line_numbers()
                self._schedule_highlight()

    def open_community_hub(self):
        self.clear_console()
        self.log("[TRAPPY COMMUNITY HUB (TPM)]: Loading community repository index...")
        import subprocess, shutil
        base_dir = os.path.dirname(os.path.abspath(__file__)) if not getattr(sys, 'frozen', False) else os.path.dirname(sys.executable)
        py_runner = shutil.which("python") or r"C:\Python315\python.exe"
        tpm_script = os.path.join(base_dir, "tpm.py")
        
        def run_hub():
            proc = subprocess.Popen([py_runner, tpm_script, "search"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            stdout, stderr = proc.communicate()
            if stdout:
                self.root.after(0, lambda: self.log(stdout))
            if stderr:
                self.root.after(0, lambda: self.log(stderr, is_err=True))
            self.root.after(0, lambda: self.status.config(text="Community Hub packages loaded."))
        
        threading.Thread(target=run_hub, daemon=True).start()

    def load_default_code(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(base_dir, "shapes3d_demo.trappy")
        if not os.path.exists(path):
            path = os.path.join(base_dir, "game3d_demo.trappy")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                self.code_text.insert("1.0", f.read())
            self.current_file = path
        else:
            self.new_file()
        self.update_line_numbers()
        self._schedule_highlight()
        
        self.log("=====================================================================")
        self.log("TRAPPY STUDIO IDE (v1.0.0 GLOBAL RELEASE)")
        self.log("Discord: https://discord.gg/WRTG3spWH (Official Community Headquarters)")
        self.log("GitHub:  https://github.com/ashoccompany/Trappy")
        self.log("X:       https://x.com/tr4ppyai")
        self.log("Press F1 anytime for the Built-in Manual & Command Reference Browser")
        self.log("Universal: 3D/2D Graphics, Discord Webhooks, Offline Loopback, File I/O")
        self.log("=====================================================================")

    def debug_code(self):
        self.clear_console()
        self.log("[TRAPPY DEBUGGER]: Analyzing code syntax and structure...")
        code = self.get_clean_code()

        try:
            tokens = trappy.tokenize(code)
            ast = trappy.Parser(tokens).parse_program()
            self.log("[SUCCESS]: SYNTAX VERIFIED - 0 Errors detected!")
            self.log(f"[INFO]: Statements successfully parsed: {len(ast[1])}")
            self.status.config(text="Debug Check Passed: Code syntax is healthy!")
        except trappy.TrappyError as err:
            self.log(str(err))
            self.status.config(text="Debug Alert: Syntax error detected!")
        except Exception as ex:
            self.log(f"[TRAPPY DEBUGGER]: {ex}")

    def run_code(self):
        base_dir = os.path.dirname(os.path.abspath(__file__)) if not getattr(sys, 'frozen', False) else os.path.dirname(sys.executable)
        temp_path = os.path.join(base_dir, "_temp_run.trappy")
        with open(temp_path, "w", encoding="utf-8") as f:
            f.write(self.get_clean_code())

        self.clear_console()
        self.log("[TRAPPY RUNNER]: Launching program execution...")

        import shutil
        py_runner = shutil.which("python") or shutil.which("python3")
        if not py_runner:
            for candidate in (r"C:\Python315\python.exe", r"C:\Python314\python.exe", r"C:\Python313\python.exe", r"C:\Python312\python.exe", r"C:\Python311\python.exe"):
                if os.path.exists(candidate):
                    py_runner = candidate
                    break
        if not py_runner:
            py_runner = "python"

        trappy_script = os.path.join(base_dir, "trappy.py")

        def run_thread():
            cmd = [py_runner, trappy_script, temp_path]

            try:
                proc = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
                )
                stdout, stderr = proc.communicate()
                if stdout:
                    self.root.after(0, lambda: self.log(stdout))
                if stderr:
                    self.root.after(0, lambda: self.log(stderr, is_err=True))
                self.root.after(0, lambda: self.status.config(text=f"Program finished (exit code {proc.returncode})"))
            except Exception as e:
                self.root.after(0, lambda: self.log(f"[RUN ERROR]: Could not launch runner: {e}", is_err=True))

        threading.Thread(target=run_thread, daemon=True).start()


if __name__ == "__main__":
    import multiprocessing
    multiprocessing.freeze_support()

    root = tk.Tk()
    app = TrappyIDE(root)
    root.mainloop()
