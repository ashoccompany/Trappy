import sys
import os
import re
import subprocess
import threading
import webbrowser
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

import trappy

BG_DARK = "#18181b"
BG_SIDE = "#202024"
BG_LINKS = "#141417"
BG_EDITOR = "#121214"
TEXT_COLOR = "#f4f4f5"
ACCENT_COLOR = "#06b6d4"
KEYWORD_COLOR = "#f97316"
STRING_COLOR = "#eab308"
COMMENT_COLOR = "#22c55e"
NUMBER_COLOR = "#38bdf8"
GHOST_COLOR = "#71717a"
DISCORD_COLOR = "#5865F2"

ASSIST_KEYWORDS = [
    "trst", "tren",
    "cwin", "sbgwin", "label", "regle", "circ", "line", "btn", "inp",
    "cube3d", "line3d", "sphere3d", "pyramid3d",
    "gloop", "fps calm", "fps lock", "rep", "loop", "srep", "sloop", "each", "in",
    "add_obj", "add_var", "add_func",
    "discord_webhook", "json_parse", "json_dump",
    "pack_data", "unpack_data", "cli_connect", "cli_send", "cli_recv", "cli_close",
    "srv_listen", "srv_accept", "http_get", "http_post", "download",
    "ws_connect", "ws_send", "ws_recv", "ws_close",
    "dict", "dset", "dget", "dkeys",
    "lst", "lget", "lset", "llen", "lpush", "lpop",
    "file_write", "file_read", "file_append", "file_exists", "file_delete", "dir_list",
    "ifr", "then", "else", "grt", "lss", "sm",
    "txt", "tit", "gan", "answ", "rt", "mh", "eq",
    "sqrt", "dist", "clamp", "pow", "abs", "sin", "cos", "rnd",
    "box_hit", "vec_add", "vec_mag",
    "mem_alloc", "mem_write", "mem_read", "sys_exec", "sys_env",
    "synth", "beep", "play", "key",
    "fmh", "ftxt", "flist", "fweb", "fcli", "fapp", "fdel", "fui", "f3d", "fos",
    "fn", "func", "return", "while", "swhile", "break", "continue", "cnt",
    "try", "catch", "slen", "sget", "ssub", "ssplit", "sjoin", "sfind", "sreplace", "strim",
    "slower", "supper", "ord", "chr", "is_digit", "is_alpha",
    "type_of", "to_str", "to_num", "to_int", "to_float",
    "lcontains", "linsert", "lslice", "dhas", "ddel",
    "true", "false", "import", "exit",
    "os_boot", "os_shutdown", "os_panic",
    "os_proc_spawn", "os_proc_kill", "os_proc_list", "os_yield",
    "os_ipc_send", "os_ipc_recv",
    "os_vfs_mount", "os_vfs_write", "os_vfs_read", "os_vfs_list", "os_vfs_del", "os_vfs_stat",
    "os_setting_set", "os_setting_get", "os_setting_dump",
    "os_app_download", "os_app_install", "os_app_launch", "os_app_list", "os_app_kill", "os_app_uninstall",
    "os_screen_mode", "os_hw_info", "os_battery_info", "os_touch_event",
    "os_ui_window", "os_ui_taskbar", "os_ui_notify", "os_ui_render",
    "os_integrity_seal", "os_integrity_verify", "os_jailbreak_check", "os_jailbreak_defend",
    "os_exploit_guard", "os_exploit_status", "os_ring_set", "os_ring_get",
    "os_perm_grant", "os_perm_revoke", "os_perm_check",
    "os_firewall_rule", "os_defense_hook", "os_block_list"
]

HIGHLIGHT_KEYWORDS = list(set(ASSIST_KEYWORDS + [
    "fps", "calm", "lock", "unlock", "psed", "changed", "flkey", "mousel", "mouser"
]))

MANUAL_DATABASE = [
    ("os_boot", 'os_boot "OSName" "Version"', "Initializes and boots the TrappyOS kernel, process table, VFS, and security subsystem.", 'os_boot "TrappyOS" "1.5.0"'),
    ("os_screen_mode", 'os_screen_mode "phone"|"computer" "portrait"|"landscape"', "Configures the OS target device frame, aspect ratio, and resolution (smartphone vs desktop workstation).", 'os_screen_mode "phone" "portrait"'),
    ("os_vfs_write", 'os_vfs_write "/path" "data"', "Writes data securely to the OS Virtual File System with path traversal guards.", 'os_vfs_write "/etc/hostname" "trappy-node"'),
    ("os_vfs_read", 'os_vfs_read "/path" tit var', "Reads file data or virtual proc files (/proc/version, /proc/uptime) from VFS.", 'os_vfs_read "/etc/hostname" tit host'),
    ("os_app_download", 'os_app_download "url" "app_id" tit status', "Downloads and verifies a Trappy application from the network into /apps.", 'os_app_download "https://example.com/app.trappy" "calc" tit status'),
    ("os_app_launch", 'os_app_launch "app_id" tit pid', "Launches an installed Trappy app in an isolated Ring 3 Userland sandbox.", 'os_app_launch "calc" tit pid'),
    ("os_jailbreak_check", 'os_jailbreak_check tit report', "Scans for system file tampering, unverified components, and root privilege escalation attempts.", 'os_jailbreak_check tit report'),
    ("os_exploit_guard", 'os_exploit_guard "canary"|"nx_memory" 1', "Enables hardware-level exploit guards such as memory buffer canary bounds checking and execution filters.", 'os_exploit_guard "canary" 1'),
    ("os_perm_grant", 'os_perm_grant "app_id" "PERMISSION"', "Grants granular permissions (NETWORK, STORAGE, UI, AUDIO) to a sandboxed app.", 'os_perm_grant "calc" "UI"'),
    ("os_ui_window", 'os_ui_window "Title" x:y:w:h tit win_id', "Registers a managed desktop or mobile window container in the OS compositor.", 'os_ui_window "Terminal" 50:50:400:250 tit term_win'),
    ("os_ui_render", 'os_ui_render', "Renders the composite OS desktop or phone interface, status bar, windows, and notifications.", 'os_ui_render'),
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
    ("gloop", "gloop ... tren", "Hardware-synchronized continuous game loop.", 'gloop\n    circ player.x:player.y 16 cyan\ntren'),
    ("ifr", "ifr a > b ... else ... tren", "Evaluates a condition and runs branch code based on the result.", 'ifr score > 10\n    gan "Winner!"\nelse\n    gan "Keep trying!"\ntren'),
    ("else", "else", "Defines the alternative execution block in an ifr statement when condition is false.", 'ifr health < 1\n    gan "Game Over"\nelse\n    gan "Alive"\ntren'),
    ("while", "while condition ... tren", "Executes body repeatedly while condition evaluates to true.", 'while i < 10\n    mh i + 1 eq i\ntren'),
    ("break", "break", "Immediately breaks and terminates innermost loop (rep, loop, while, each).", 'ifr count == 5\n    break\ntren'),
    ("continue", "continue", "Skips remaining statements and continues to next loop iteration.", 'ifr count == 3\n    continue\ntren'),
    ("try", "try ... catch err ... tren", "Catches runtime exceptions and errors safely without crashing.", 'try\n    mh 10 / 0 eq fail\ncatch err\n    gan err\ntren'),
    ("fn", "fn name params ... return val ... tren", "Universal function definition keyword with first-class return value support.", 'fn calculate_score base:mult\n    mh base * mult eq total\n    return total\ntren'),
    ("slen", "slen text tit var", "Calculates character length of string expression.", 'slen "Trappy" tit str_len'),
    ("sget", "sget text:index tit var", "Retrieves character from string at zero-based index.", 'sget "Trappy":0 tit first_ch'),
    ("ssub", "ssub text:start:end tit var", "Extracts substring slice from start to end index.", 'ssub "Trappy Language":0:6 tit title'),
    ("ssplit", "ssplit text:delimiter tit var", "Splits string by delimiter into a list of strings.", 'ssplit "10,20,30":"," tit list_vals'),
    ("sjoin", "sjoin list:delimiter tit var", "Joins list elements into a single delimited string.", 'sjoin items:" - " tit formatted'),
    ("sfind", "sfind text:needle tit var", "Finds index of substring, or -1 if needle is not found.", 'sfind "Welcome to Trappy":"Trappy" tit idx'),
    ("sreplace", "sreplace text:old:new tit var", "Replaces all occurrences of substring with replacement.", 'sreplace "hello world":"world":"community" tit res'),
    ("strim", "strim text tit var", "Strips leading and trailing whitespace characters.", 'strim "   spaced   " tit cleaned'),
    ("ord", "ord char tit var", "Returns integer ASCII code of the first character.", 'ord "A" tit ascii_code'),
    ("chr", "chr code tit var", "Returns single-character string from integer ASCII code.", 'chr 65 tit char_val'),
    ("is_digit", "is_digit text tit var", "Returns 1 if string is composed purely of digits, else 0.", 'is_digit "12345" tit is_num'),
    ("is_alpha", "is_alpha text tit var", "Returns 1 if string contains alphabetic/underscore characters, else 0.", 'is_alpha "my_var" tit is_id'),
    ("type_of", "type_of value tit var", "Inspects runtime type: string, number, list, dict, bool, nil.", 'type_of 42 tit val_type'),
    ("to_str", "to_str value tit var", "Converts value of any type to string representation.", 'to_str 999 tit str_val'),
    ("to_num", "to_num value tit var", "Converts string/float value to integer number.", 'to_num "42" tit int_val'),
    ("to_float", "to_float value tit var", "Converts string/integer value to floating-point number.", 'to_float "3.1415" tit float_val'),
    ("lcontains", "lcontains list:item tit var", "Returns 1 if item exists in list, else 0.", 'lcontains scores:100 tit has_top'),
    ("linsert", "linsert list:index:val", "Inserts value into list at specified index.", 'linsert queue:0:first_player'),
    ("lslice", "lslice list:start:end tit var", "Extracts sublist slice from start to end index.", 'lslice inventory:0:3 tit hotbar'),
    ("dhas", "dhas dict:key tit var", "Returns 1 if dictionary contains specified key, else 0.", 'dhas player:"level" tit has_level'),
    ("ddel", "ddel dict:key", "Removes specified key from dictionary if present.", 'ddel player:"temp_buff"')
]

class TrappyIDE:
    def __init__(self, root):
        self.root = root
        self.root.title("Trappy IDE - Official Code Studio (v1.15.0)")
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
        toolbar = tk.Frame(self.root, bg=BG_SIDE, height=45)
        toolbar.pack(fill="x", side="top")

        btn_style = {"bg": "#27272a", "fg": TEXT_COLOR, "font": ("Consolas", 10, "bold"), "bd": 0, "padx": 10, "pady": 6}

        tk.Button(toolbar, text="[New]", command=self.new_file, **btn_style).pack(side="left", padx=3, pady=5)
        tk.Button(toolbar, text="[Open]", command=self.open_file, **btn_style).pack(side="left", padx=3, pady=5)
        tk.Button(toolbar, text="[Save (Ctrl+S)]", command=self.save_file, **btn_style).pack(side="left", padx=3, pady=5)

        doc_btn = dict(btn_style)
        doc_btn["bg"] = "#0d9488"
        tk.Button(toolbar, text="[Manual / Docs (F1)]", command=self.open_manual_window, **doc_btn).pack(side="left", padx=4, pady=5)

        self.example_var = tk.StringVar(value="Load Example...")
        examples = [
            "3D Multi-Shapes (Cube, Sphere, Pyramid)",
            "Discord & Online Connect Demo",
            "File I/O & Save System Demo",
            "RPG Stats & Inventory Demo",
            "Packets & Client Demo",
            "Web & Internet Demo",
            "Language Showcase Demo"
        ]
        dropdown = ttk.OptionMenu(toolbar, self.example_var, "Load Example...", *examples, command=self.load_example)
        dropdown.pack(side="left", padx=6, pady=5)

        discord_btn = dict(btn_style)
        discord_btn["bg"] = DISCORD_COLOR
        tk.Button(toolbar, text="[Discord Community]", command=lambda: webbrowser.open_new_tab("https://discord.gg/3chDfAPE9H"), **discord_btn).pack(side="left", padx=4, pady=5)

        hub_btn = dict(btn_style)
        hub_btn["bg"] = "#0284c7"
        tk.Button(toolbar, text="[Community Hub (TPM)]", command=self.open_community_hub, **hub_btn).pack(side="left", padx=4, pady=5)

        debug_btn = dict(btn_style)
        debug_btn["bg"] = "#4338ca"
        tk.Button(toolbar, text="[Debug / Check (F6)]", command=self.debug_code, **debug_btn).pack(side="right", padx=6, pady=5)

        run_btn = dict(btn_style)
        run_btn["bg"] = "#059669"
        tk.Button(toolbar, text="[RUN TRAPPY (F5)]", command=self.run_code, **run_btn).pack(side="right", padx=6, pady=5)

        links_bar = tk.Frame(self.root, bg=BG_LINKS, height=28)
        links_bar.pack(fill="x", side="top")

        tk.Label(links_bar, text="OFFICIAL CHANNELS:", bg=BG_LINKS, fg="#71717a", font=("Consolas", 8, "bold")).pack(side="left", padx=(10, 4), pady=3)

        discord_link = tk.Label(links_bar, text="Discord (Main): discord.gg/3chDfAPE9H", bg=BG_LINKS, fg="#a78bfa", font=("Consolas", 8, "underline"), cursor="hand2")
        discord_link.pack(side="left", padx=8, pady=3)
        discord_link.bind("<Button-1>", lambda e: webbrowser.open_new_tab("https://discord.gg/3chDfAPE9H"))

        github_link = tk.Label(links_bar, text="GitHub: github.com/ashoccompany/Trappy", bg=BG_LINKS, fg="#38bdf8", font=("Consolas", 8, "underline"), cursor="hand2")
        github_link.pack(side="left", padx=8, pady=3)
        github_link.bind("<Button-1>", lambda e: webbrowser.open_new_tab("https://github.com/ashoccompany/Trappy"))

        x_link = tk.Label(links_bar, text="X (Twitter): x.com/tr4ppyai", bg=BG_LINKS, fg="#34d399", font=("Consolas", 8, "underline"), cursor="hand2")
        x_link.pack(side="left", padx=8, pady=3)
        x_link.bind("<Button-1>", lambda e: webbrowser.open_new_tab("https://x.com/tr4ppyai"))

        assist_badge = tk.Label(links_bar, text="[Quick Assist: Active | F1: Manual]", bg=BG_LINKS, fg="#94a3b8", font=("Consolas", 8))
        assist_badge.pack(side="right", padx=10, pady=3)

        paned = tk.PanedWindow(self.root, orient="vertical", bg=BG_DARK, sashwidth=4)
        paned.pack(fill="both", expand=True)

        editor_frame = tk.Frame(paned, bg=BG_EDITOR)
        paned.add(editor_frame, height=450)

        self.line_numbers = tk.Text(editor_frame, width=4, bg=BG_SIDE, fg="#71717a", font=("Consolas", 12), bd=0, padx=4, pady=6)
        self.line_numbers.pack(side="left", fill="y")
        self.line_numbers.configure(state="disabled")

        self.code_text = tk.Text(editor_frame, bg=BG_EDITOR, fg=TEXT_COLOR, insertbackground="white", font=("Consolas", 12), bd=0, padx=8, pady=6, undo=True)
        self.code_text.pack(side="left", fill="both", expand=True)

        scroll = tk.Scrollbar(editor_frame, command=self.code_text.yview)
        scroll.pack(side="right", fill="y")
        self.code_text.configure(yscrollcommand=scroll.set)

        self.code_text.bind("<KeyPress>", self._on_key_press)
        self.code_text.bind("<KeyRelease>", self._on_key_release)
        self.code_text.bind("<Button-1>", lambda e: self.clear_ghost())

        console_frame = tk.Frame(paned, bg=BG_DARK)
        paned.add(console_frame, height=200)

        console_bar = tk.Frame(console_frame, bg=BG_SIDE)
        console_bar.pack(fill="x")
        tk.Label(console_bar, text="OUTPUT & TERMINAL CONSOLE", bg=BG_SIDE, fg="#a1a1aa", font=("Consolas", 9, "bold")).pack(side="left", padx=8, pady=2)
        tk.Button(console_bar, text="[Clear]", bg=BG_SIDE, fg="#a1a1aa", font=("Consolas", 8), bd=0, command=self.clear_console).pack(side="right", padx=8)

        self.console = tk.Text(console_frame, bg="#09090b", fg="#22c55e", font=("Consolas", 10), bd=0, padx=8, pady=6)
        self.console.pack(fill="both", expand=True)

        self.status = tk.Label(
            self.root,
            text="Ready | Trappy v1.15.0 | Discord: discord.gg/3chDfAPE9H | Press F1 for Docs, F5 to Run",
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

    def open_manual_window(self):
        if self.manual_win and tk.Toplevel.winfo_exists(self.manual_win):
            self.manual_win.lift()
            return

        self.manual_win = tk.Toplevel(self.root)
        self.manual_win.title("Trappy Command Reference & Manual (Press F1)")
        self.manual_win.geometry("700x550")
        self.manual_win.configure(bg=BG_DARK)

        search_frame = tk.Frame(self.manual_win, bg=BG_SIDE, padx=10, pady=8)
        search_frame.pack(fill="x", side="top")

        tk.Label(search_frame, text="Search Command:", bg=BG_SIDE, fg=TEXT_COLOR, font=("Consolas", 10, "bold")).pack(side="left")
        search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=search_var, bg=BG_EDITOR, fg=TEXT_COLOR, insertbackground="white", font=("Consolas", 10), width=28)
        search_entry.pack(side="left", padx=8)
        search_entry.focus_set()

        tk.Label(search_frame, text="Discord Help: discord.gg/3chDfAPE9H", bg=BG_SIDE, fg="#a78bfa", font=("Consolas", 9)).pack(side="right")

        content_paned = tk.PanedWindow(self.manual_win, orient="horizontal", bg=BG_DARK, sashwidth=4)
        content_paned.pack(fill="both", expand=True, padx=8, pady=8)

        list_frame = tk.Frame(content_paned, bg=BG_EDITOR)
        content_paned.add(list_frame, width=220)

        cmd_listbox = tk.Listbox(list_frame, bg=BG_EDITOR, fg=TEXT_COLOR, selectbackground="#0284c7", selectforeground="white", font=("Consolas", 11), bd=0)
        cmd_listbox.pack(fill="both", expand=True, side="left")
        list_scroll = tk.Scrollbar(list_frame, command=cmd_listbox.yview)
        list_scroll.pack(side="right", fill="y")
        cmd_listbox.configure(yscrollcommand=list_scroll.set)

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
        self.code_text.insert("1.0", "trst\n    gan \"Hello from Trappy IDE!\"\ntren\n")
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
            path = os.path.join(base_dir, "main.trappy")
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                self.code_text.insert("1.0", f.read())
            self.current_file = path
        else:
            self.new_file()
        self.update_line_numbers()
        self._schedule_highlight()

        self.log("=====================================================================")
        self.log("TRAPPY STUDIO IDE (v1.15.0 RELEASE)")
        self.log("Discord: https://discord.gg/3chDfAPE9H (Official Community Headquarters)")
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
