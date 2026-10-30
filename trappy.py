# =====================================================================
# TRAPPY PROGRAMMING LANGUAGE - CORE RUNTIME ENGINE (v1.0.0 GLOBAL)
# Official Community & Source Links:
# Discord: https://discord.gg/WRTG3spWH (Official Community Headquarters)
# GitHub:  https://github.com/ashoccompany/Trappy
# X:       https://x.com/tr4ppyai
# Universal: 3D/2D Graphics, Discord Webhooks, Offline Loopback, File I/O,
# Packets, Dictionaries, Lists, Audio Synthesizer, OS Primitives & Math
# =====================================================================

import sys
import os
import time
import math
import random
import socket
import urllib.request
import urllib.parse
import json
import subprocess
import queue

# Built-in GUI and Audio
try:
    import tkinter as tk
except ImportError:
    tk = None

try:
    import winsound
except ImportError:
    winsound = None


# =====================================================================
# VIRTUAL OFFLINE LOOPBACK BUS (BUDGET RESILIENT NETWORKING)
# =====================================================================
class VirtualLoopbackSocket:
    _channels = {}

    def __init__(self, channel_id="default"):
        self.channel_id = str(channel_id)
        if self.channel_id not in VirtualLoopbackSocket._channels:
            VirtualLoopbackSocket._channels[self.channel_id] = queue.Queue()
        self.q = VirtualLoopbackSocket._channels[self.channel_id]
        self.closed = False

    def sendall(self, data):
        if not self.closed:
            self.q.put(data)

    def send(self, data):
        self.sendall(data)

    def recv(self, bufsize=4096):
        if self.closed:
            return b""
        try:
            val = self.q.get_nowait()
            return val if isinstance(val, bytes) else str(val).encode('utf-8')
        except queue.Empty:
            return b""

    def close(self):
        self.closed = True


# =====================================================================
# SECURITY & ERROR SYSTEM
# =====================================================================
class TrappyError(Exception):
    def __init__(self, message, line=None):
        self.message = message
        self.line = line
        super().__init__(self.__str__())

    def __str__(self):
        line_info = f"on Line {self.line}" if self.line else ""
        return (
            f"\n[TRAPPY ERROR {line_info}]: {self.message}\n"
            f"[TRAPPY HINT]: Press F1 in IDE for Manual or ask on Discord: https://discord.gg/WRTG3spWH"
        )


class TrappySecurityError(TrappyError):
    def __str__(self):
        line_info = f"on Line {self.line}" if self.line else ""
        return (
            f"\n[TRAPPY SECURITY ALERT] Threat Blocked {line_info}!\n"
            f"[TRAPPY]: Exploit/Violation prevented: {self.message}"
        )


def sanitize_path(filename, base_dir=None):
    """Prevents Directory Traversal exploits (e.g. ../../Windows/System32)."""
    if base_dir is None:
        base_dir = os.getcwd()
    # Normalize paths
    abs_base = os.path.abspath(base_dir)
    target = os.path.abspath(os.path.join(abs_base, filename))
    if not target.startswith(abs_base):
        raise TrappySecurityError(f"Path Traversal attempt blocked: '{filename}'")
    return target


# =====================================================================
# THE LEXER (TOKENIZER)
# =====================================================================
class Token:
    def __init__(self, kind, val, line):
        self.kind = kind
        self.val = val
        self.line = line

    def __repr__(self):
        return f"Token({self.kind}, {self.val}, Line:{self.line})"


def tokenize(code):
    tokens = []
    i = 0
    n = len(code)
    line = 1

    while i < n:
        c = code[i]

        if c == '\n':
            line += 1
            i += 1
            continue

        if c.isspace():
            i += 1
            continue

        # Comments
        if c == '#':
            while i < n and code[i] != '\n':
                i += 1
            continue

        # Strings with double quotes
        if c == '"':
            start_line = line
            i += 1
            str_val = ""
            while i < n and code[i] != '"':
                if code[i] == '\n':
                    line += 1
                str_val += code[i]
                i += 1
            if i >= n:
                raise TrappyError("Unclosed string quote", start_line)
            i += 1  # Skip closing quote
            tokens.append(Token("STR", str_val, start_line))
            continue

        # Punctuation & Operators
        if c in "():+=|,":
            tokens.append(Token(c, c, line))
            i += 1
            continue

        if c == ".":
            tokens.append(Token(".", ".", line))
            i += 1
            continue

        if c == "-":
            tokens.append(Token("-", "-", line))
            i += 1
            continue

        # Hex literals (0x41, 0xFF, 0x90) and Decimal Numbers
        if c == '0' and i + 1 < n and code[i+1].lower() == 'x':
            i += 2
            hex_str = ""
            while i < n and (code[i].isdigit() or code[i].lower() in "abcdef"):
                hex_str += code[i]
                i += 1
            tokens.append(Token("NUM", int(hex_str, 16) if hex_str else 0, line))
            continue

        if c.isdigit():
            num = ""
            while i < n and code[i].isdigit():
                num += code[i]
                i += 1
            tokens.append(Token("NUM", int(num), line))
            continue

        # Words & Keywords
        if c.isalpha() or c == "_":
            word = ""
            while i < n and (code[i].isalnum() or code[i] == "_"):
                word += code[i]
                i += 1

            keywords = (
                "trst", "tren", "fmh", "fdel", "ftxt", "flist", "frep", "floop",
                "fgui", "fui", "fdrw", "fgfx", "fcan", "fweb", "fcli", "fapp", "f3d", "fos",
                "mh", "eq", "rt", "answ", "out", "gan", "trg", "trged", "multi", "div",
                # Advanced Math, Geometry & Physics Operators:
                "sqrt", "pow", "abs", "sin", "cos", "dist", "clamp",
                "box_hit", "vec_add", "vec_mag",
                # Bitwise Systems Operators:
                "band", "bor", "bxor", "bnot", "bshl", "bshr",
                # Universal Web, Packets, Discord & Client/Server Keywords:
                "http_get", "http_post", "download", "discord_webhook",
                "ws_connect", "ws_send", "ws_recv", "ws_close",
                "json_parse", "json_dump",
                "pack", "unpack", "pack_data", "unpack_data",
                "cli_connect", "cli_send", "cli_recv", "cli_close",
                "srv_listen", "srv_accept",
                # Collections & Dictionaries & Lists (v1.0.0):
                "dict", "dset", "dget", "dkeys",
                "lst", "lget", "lset", "llen", "lpush", "lpop",
                # Universal File I/O Suite (v1.0.0):
                "file_write", "file_read", "file_append", "file_exists", "file_delete", "dir_list",
                "ifr", "then", "else", "grt", "lss", "sm", "exst", "exist",
                "rep", "loop", "srep", "sloop", "txt", "tit", "inf", "ath",
                # Registry keywords:
                "add_var", "add_func", "add_obj", "add_type", "spawn", "as",
                # GUI, 2D & 3D Engine Keywords:
                "cwin", "swin", "sbgwin", "label", "regle", "circ", "line",
                "cube3d", "line3d", "point3d", "sphere3d", "pyramid3d",
                # OS & Low-Level Memory Keywords:
                "mem_alloc", "mem_write", "mem_read", "sys_exec", "sys_env",
                "btn", "inp", "psed", "changed", "gloop", "fps", "calm", "lock", "unlock",
                "key", "flkey", "mousel", "mouser", "mousesp", "collde", "collide",
                "hrable", "play", "beep", "synth", "rnd", "write", "into", "each", "in"
            )
            if word in keywords:
                tokens.append(Token(word.upper(), word, line))
            else:
                tokens.append(Token("NAME", word, line))
            continue

        raise TrappyError(f"Unexpected character '{c}'", line)

    tokens.append(Token("EOF", None, line))
    return tokens


# =====================================================================
# THE PARSER
# =====================================================================
class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.known_functions = set()
        self.known_variables = set()
        self.blueprints = {}

    def peek(self):
        return self.tokens[self.pos]

    def consume(self, expected_kind):
        tok = self.peek()
        if tok.kind != expected_kind:
            raise TrappyError(f"Expected '{expected_kind}', but got '{tok.val}'", tok.line)
        self.pos += 1
        return tok

    def parse_program(self):
        self.consume("TRST")
        statements = []
        while self.peek().kind not in ("TREN", "EOF"):
            statements.append(self.parse_statement())
        self.consume("TREN")
        return ("PROGRAM", statements)

    def parse_statement(self):
        tok = self.peek()

        # 1. Declaration: add_var "name" / add_var name [as "Type"]
        if tok.kind == "ADD_VAR":
            self.consume("ADD_VAR")
            var_name = self.consume_name_or_str()
            self.known_variables.add(var_name)
            type_name = None
            if self.peek().kind == "AS":
                self.consume("AS")
                type_name = self.consume_name_or_str()
            return ("ADD_VAR", var_name, type_name, tok.line)

        # 2. Declaration: add_func "name"
        if tok.kind == "ADD_FUNC":
            self.consume("ADD_FUNC")
            fn_name = self.consume_name_or_str()
            self.known_functions.add(fn_name)
            return ("ADD_FUNC", fn_name, tok.line)

        # 3. Declaration: add_obj "name" ... tren
        if tok.kind == "ADD_OBJ":
            self.consume("ADD_OBJ")
            obj_name = self.consume_name_or_str()
            self.known_variables.add(obj_name)
            fields = {}
            while self.peek().kind not in ("TREN", "EOF"):
                field_name = self.consume("NAME").val
                self.consume(":")
                field_val = self.parse_expr()
                fields[field_name] = field_val
            self.consume("TREN")
            return ("ADD_OBJ", obj_name, fields, tok.line)

        # 4. Declaration: add_type "TypeName" ... tren
        if tok.kind == "ADD_TYPE":
            self.consume("ADD_TYPE")
            type_name = self.consume_name_or_str()
            fields = {}
            while self.peek().kind not in ("TREN", "EOF"):
                field_name = self.consume("NAME").val
                self.consume(":")
                field_val = self.parse_expr()
                fields[field_name] = field_val
            self.consume("TREN")
            self.blueprints[type_name] = fields
            return ("ADD_TYPE", type_name, fields, tok.line)

        # 5. Functions: fmh, ftxt, flist, frep, floop, fgui, fui, fdrw, fgfx, fcan, fweb, fcli, fapp, f3d, fos
        if tok.kind in ("FMH", "FTXT", "FLIST", "FREP", "FLOOP", "FGUI", "FUI", "FDRW", "FGFX", "FCAN", "FWEB", "FCLI", "FAPP", "F3D", "FOS"):
            fn_type = self.consume(tok.kind).val
            fn_name = self.consume("NAME").val
            self.known_functions.add(fn_name)
            
            params = []
            if self.peek().kind in ("NAME", "STR"):
                p_tok = self.peek()
                self.consume(p_tok.kind)
                params.append(p_tok.val)
                while self.peek().kind == ":":
                    self.consume(":")
                    p_tok = self.peek()
                    self.consume(p_tok.kind)
                    params.append(p_tok.val)

            body = []
            while self.peek().kind not in ("TREN", "EOF"):
                body.append(self.parse_statement())
            self.consume("TREN")
            return ("FN_DEF", fn_type, fn_name, params, body, tok.line)

        # 6. Delete function: fdel <name> <target> ... tren
        if tok.kind == "FDEL":
            self.consume("FDEL")
            fn_name = self.consume("NAME").val
            self.known_functions.add(fn_name)
            target_param = self.consume("NAME").val
            body = []
            while self.peek().kind not in ("TREN", "EOF"):
                body.append(self.parse_statement())
            self.consume("TREN")
            return ("FDEL_DEF", fn_name, target_param, body, tok.line)

        # 7. Trigger action: trg <name> [target]
        if tok.kind == "TRG":
            self.consume("TRG")
            fn_name = self.consume("NAME").val
            target = None
            if self.peek().kind == "NAME":
                target = self.consume("NAME").val
            return ("TRG_ACTION", fn_name, target, tok.line)

        # 8. GUI Window Creation: cwin "Title" width:height [main/bg]
        if tok.kind == "CWIN":
            self.consume("CWIN")
            title = self.consume("STR").val
            w = self.consume("NUM").val
            self.consume(":")
            h = self.consume("NUM").val
            mode = "main"
            if self.peek().kind == "NAME" and self.peek().val in ("main", "bg"):
                mode = self.consume("NAME").val
            return ("CWIN", title, w, h, mode, tok.line)

        # 9. Window Styling: swin / sbgwin
        if tok.kind in ("SWIN", "SBGWIN"):
            cmd = self.consume(tok.kind).val
            win_name = self.consume("STR").val if self.peek().kind == "STR" else self.consume("NAME").val
            color = self.consume("NAME").val
            return ("WIN_STYLE", cmd, win_name, color, tok.line)

        # 10. GUI Label: label <expr> x:y color
        if tok.kind == "LABEL":
            self.consume("LABEL")
            text_expr = self.parse_expr()
            x = self.parse_coord_part()
            self.consume(":")
            y = self.parse_coord_part()
            color = self.consume("NAME").val if self.peek().kind == "NAME" else "white"
            return ("LABEL", text_expr, x, y, color, tok.line)

        # 11. GUI Rectangle: regle x:y w:h color
        if tok.kind == "REGLE":
            self.consume("REGLE")
            x = self.parse_coord_part()
            self.consume(":")
            y = self.parse_coord_part()
            w = self.parse_coord_part()
            self.consume(":")
            h = self.parse_coord_part()
            color = self.consume("NAME").val if self.peek().kind == "NAME" else "red"
            return ("REGLE", x, y, w, h, color, tok.line)

        # 12. GUI Circle: circ x:y radius color
        if tok.kind == "CIRC":
            self.consume("CIRC")
            x = self.parse_coord_part()
            self.consume(":")
            y = self.parse_coord_part()
            r = self.parse_coord_part()
            color = self.consume("NAME").val if self.peek().kind == "NAME" else "blue"
            return ("CIRC", x, y, r, color, tok.line)

        # 13. GUI Line: line x1:y1 x2:y2 color
        if tok.kind == "LINE":
            self.consume("LINE")
            x1 = self.parse_coord_part()
            self.consume(":")
            y1 = self.parse_coord_part()
            x2 = self.parse_coord_part()
            self.consume(":")
            y2 = self.parse_coord_part()
            color = self.consume("NAME").val if self.peek().kind == "NAME" else "green"
            return ("LINE", x1, y1, x2, y2, color, tok.line)

        # 13b. 3D Wireframe Cube: cube3d x:y:z size rx:ry color
        if tok.kind == "CUBE3D":
            self.consume("CUBE3D")
            x = self.parse_coord_part()
            self.consume(":")
            y = self.parse_coord_part()
            self.consume(":")
            z = self.parse_coord_part()
            size = self.parse_coord_part()
            rx = self.parse_coord_part()
            self.consume(":")
            ry = self.parse_coord_part()
            color = self.consume("NAME").val if self.peek().kind == "NAME" else "cyan"
            return ("CUBE3D", x, y, z, size, rx, ry, color, tok.line)

        # 13c. 3D Line: line3d x1:y1:z1 x2:y2:z2 rx:ry color
        if tok.kind == "LINE3D":
            self.consume("LINE3D")
            x1 = self.parse_coord_part()
            self.consume(":")
            y1 = self.parse_coord_part()
            self.consume(":")
            z1 = self.parse_coord_part()
            x2 = self.parse_coord_part()
            self.consume(":")
            y2 = self.parse_coord_part()
            self.consume(":")
            z2 = self.parse_coord_part()
            rx = self.parse_coord_part()
            self.consume(":")
            ry = self.parse_coord_part()
            color = self.consume("NAME").val if self.peek().kind == "NAME" else "green"
            return ("LINE3D", x1, y1, z1, x2, y2, z2, rx, ry, color, tok.line)

        # 13d. 3D Wireframe Sphere: sphere3d x:y:z radius rx:ry color
        if tok.kind == "SPHERE3D":
            self.consume("SPHERE3D")
            x = self.parse_coord_part()
            self.consume(":")
            y = self.parse_coord_part()
            self.consume(":")
            z = self.parse_coord_part()
            radius = self.parse_coord_part()
            rx = self.parse_coord_part()
            self.consume(":")
            ry = self.parse_coord_part()
            color = self.consume("NAME").val if self.peek().kind == "NAME" else "cyan"
            return ("SPHERE3D", x, y, z, radius, rx, ry, color, tok.line)

        # 13e. 3D Wireframe Pyramid: pyramid3d x:y:z size rx:ry color
        if tok.kind == "PYRAMID3D":
            self.consume("PYRAMID3D")
            x = self.parse_coord_part()
            self.consume(":")
            y = self.parse_coord_part()
            self.consume(":")
            z = self.parse_coord_part()
            size = self.parse_coord_part()
            rx = self.parse_coord_part()
            self.consume(":")
            ry = self.parse_coord_part()
            color = self.consume("NAME").val if self.peek().kind == "NAME" else "yellow"
            return ("PYRAMID3D", x, y, z, size, rx, ry, color, tok.line)

        # 14. GUI Button: btn "Text" x:y trg action_name
        if tok.kind == "BTN":
            self.consume("BTN")
            btn_text = self.consume("STR").val
            x = self.parse_coord_part()
            self.consume(":")
            y = self.parse_coord_part()
            self.consume("TRG")
            action = self.consume("NAME").val
            return ("BUTTON", btn_text, x, y, action, tok.line)

        # 15. GUI Input Box: inp "Placeholder" x:y tit var_name
        if tok.kind == "INP":
            self.consume("INP")
            placeholder = self.consume("STR").val
            x = self.parse_coord_part()
            self.consume(":")
            y = self.parse_coord_part()
            self.consume("TIT")
            var_name = self.consume("NAME").val
            return ("INPUT", placeholder, x, y, var_name, tok.line)

        # 16. Game Loop: gloop ... tren
        if tok.kind == "GLOOP":
            self.consume("GLOOP")
            body = []
            while self.peek().kind not in ("TREN", "EOF"):
                body.append(self.parse_statement())
            self.consume("TREN")
            return ("GLOOP", body, tok.line)

        # 17. FPS settings: fps calm / fps lock <num> / fps unlock
        if tok.kind == "FPS":
            self.consume("FPS")
            mode = self.peek().val.lower()
            if mode in ("calm", "unlock"):
                self.consume(self.peek().kind)
                return ("FPS_SET", mode, None, tok.line)
            elif mode == "lock":
                self.consume(self.peek().kind)
                target_fps = self.consume("NUM").val
                return ("FPS_SET", "lock", target_fps, tok.line)
            raise TrappyError("FPS expects 'calm', 'lock <num>', or 'unlock'", tok.line)

        # 18. Sound / Audio: play / beep
        if tok.kind == "PLAY":
            self.consume("PLAY")
            snd_file = self.consume("STR").val
            return ("PLAY_AUDIO", snd_file, tok.line)

        if tok.kind == "BEEP":
            self.consume("BEEP")
            freq = self.parse_coord_part()
            self.consume(":")
            dur = self.parse_coord_part()
            return ("BEEP_AUDIO", freq, dur, tok.line)

        # 18b. Audio Synthesizer: synth wave:freq:dur
        if tok.kind == "SYNTH":
            self.consume("SYNTH")
            wave_expr = self.parse_coord_part()
            self.consume(":")
            freq = self.parse_coord_part()
            self.consume(":")
            dur = self.parse_coord_part()
            return ("SYNTH_AUDIO", wave_expr, freq, dur, tok.line)

        # 19. Write to File: write "filename.txt" data [into folder]
        if tok.kind == "WRITE":
            self.consume("WRITE")
            filename = self.consume("STR").val
            val_expr = self.parse_expr()
            dest_dir = None
            if self.peek().kind == "INTO":
                self.consume("INTO")
                dest_dir = self.consume("NAME").val
            return ("WRITE_FILE", filename, val_expr, dest_dir, tok.line)

        # 19b. Universal Web & Internet:
        # http_get "https://..." tit var
        if tok.kind == "HTTP_GET":
            self.consume("HTTP_GET")
            url_expr = self.parse_expr()
            self.consume("TIT")
            var_name = self.consume("NAME").val
            return ("HTTP_GET", url_expr, var_name, tok.line)

        # http_post "https://...":data tit var
        if tok.kind == "HTTP_POST":
            self.consume("HTTP_POST")
            url_expr = self.parse_expr()
            self.consume(":")
            data_expr = self.parse_expr()
            self.consume("TIT")
            var_name = self.consume("NAME").val
            return ("HTTP_POST", url_expr, data_expr, var_name, tok.line)

        # download "https://..." into "file.ext"
        if tok.kind == "DOWNLOAD":
            self.consume("DOWNLOAD")
            url_expr = self.parse_expr()
            self.consume("INTO")
            dest_file = self.consume("STR").val
            return ("DOWNLOAD_FILE", url_expr, dest_file, tok.line)

        # 19c. Packets & Client/Server Networking:
        # pack expr tit var / pack_data expr tit var
        if tok.kind in ("PACK", "PACK_DATA"):
            self.consume(tok.kind)
            data_expr = self.parse_expr()
            self.consume("TIT")
            var_name = self.consume("NAME").val
            return ("PACK_DATA", data_expr, var_name, tok.line)

        # unpack expr tit var / unpack_data expr tit var
        if tok.kind in ("UNPACK", "UNPACK_DATA"):
            self.consume(tok.kind)
            data_expr = self.parse_expr()
            self.consume("TIT")
            var_name = self.consume("NAME").val
            return ("UNPACK_DATA", data_expr, var_name, tok.line)

        # cli_connect host:port tit var
        if tok.kind == "CLI_CONNECT":
            self.consume("CLI_CONNECT")
            host_expr = self.parse_expr()
            self.consume(":")
            port_expr = self.parse_expr()
            self.consume("TIT")
            var_name = self.consume("NAME").val
            return ("CLI_CONNECT", host_expr, port_expr, var_name, tok.line)

        # cli_send client:data
        if tok.kind == "CLI_SEND":
            self.consume("CLI_SEND")
            client_name = self.consume("NAME").val
            self.consume(":")
            data_expr = self.parse_expr()
            return ("CLI_SEND", client_name, data_expr, tok.line)

        # cli_recv client tit var
        if tok.kind == "CLI_RECV":
            self.consume("CLI_RECV")
            client_name = self.consume("NAME").val
            self.consume("TIT")
            var_name = self.consume("NAME").val
            return ("CLI_RECV", client_name, var_name, tok.line)

        # cli_close client
        if tok.kind == "CLI_CLOSE":
            self.consume("CLI_CLOSE")
            client_name = self.consume("NAME").val
            return ("CLI_CLOSE", client_name, tok.line)

        # srv_listen port tit var
        if tok.kind == "SRV_LISTEN":
            self.consume("SRV_LISTEN")
            port_expr = self.parse_expr()
            self.consume("TIT")
            var_name = self.consume("NAME").val
            return ("SRV_LISTEN", port_expr, var_name, tok.line)

        # srv_accept server tit var
        if tok.kind == "SRV_ACCEPT":
            self.consume("SRV_ACCEPT")
            server_name = self.consume("NAME").val
            self.consume("TIT")
            var_name = self.consume("NAME").val
            return ("SRV_ACCEPT", server_name, var_name, tok.line)

        # 19d. OS & Memory Primitives:
        # mem_alloc size tit var
        if tok.kind == "MEM_ALLOC":
            self.consume("MEM_ALLOC")
            size_expr = self.parse_expr()
            self.consume("TIT")
            var_name = self.consume("NAME").val
            return ("MEM_ALLOC", size_expr, var_name, tok.line)

        # mem_write ptr:offset:byte
        if tok.kind == "MEM_WRITE":
            self.consume("MEM_WRITE")
            ptr_name = self.consume("NAME").val
            self.consume(":")
            offset_expr = self.parse_expr()
            self.consume(":")
            byte_expr = self.parse_expr()
            return ("MEM_WRITE", ptr_name, offset_expr, byte_expr, tok.line)

        # mem_read ptr:offset tit var
        if tok.kind == "MEM_READ":
            self.consume("MEM_READ")
            ptr_name = self.consume("NAME").val
            self.consume(":")
            offset_expr = self.parse_expr()
            self.consume("TIT")
            var_name = self.consume("NAME").val
            return ("MEM_READ", ptr_name, offset_expr, var_name, tok.line)

        # sys_exec cmd tit var
        if tok.kind == "SYS_EXEC":
            self.consume("SYS_EXEC")
            cmd_expr = self.parse_expr()
            self.consume("TIT")
            var_name = self.consume("NAME").val
            return ("SYS_EXEC", cmd_expr, var_name, tok.line)

        # sys_env name tit var
        if tok.kind == "SYS_ENV":
            self.consume("SYS_ENV")
            name_expr = self.parse_expr()
            self.consume("TIT")
            var_name = self.consume("NAME").val
            return ("SYS_ENV", name_expr, var_name, tok.line)

        # ----------------- V1.0.0 CONNECTIVITY & DISCORD -----------------
        # discord_webhook url_expr:msg_expr tit var
        if tok.kind == "DISCORD_WEBHOOK":
            self.consume("DISCORD_WEBHOOK")
            url_expr = self.parse_expr()
            self.consume(":")
            msg_expr = self.parse_expr()
            self.consume("TIT")
            var_name = self.consume("NAME").val
            return ("DISCORD_WEBHOOK", url_expr, msg_expr, var_name, tok.line)

        # ws_connect url_expr tit var
        if tok.kind == "WS_CONNECT":
            self.consume("WS_CONNECT")
            url_expr = self.parse_expr()
            self.consume("TIT")
            var_name = self.consume("NAME").val
            return ("WS_CONNECT", url_expr, var_name, tok.line)

        # ws_send sock_name:msg_expr
        if tok.kind == "WS_SEND":
            self.consume("WS_SEND")
            sock_name = self.consume("NAME").val
            self.consume(":")
            msg_expr = self.parse_expr()
            return ("WS_SEND", sock_name, msg_expr, tok.line)

        # ws_recv sock_name tit var
        if tok.kind == "WS_RECV":
            self.consume("WS_RECV")
            sock_name = self.consume("NAME").val
            self.consume("TIT")
            var_name = self.consume("NAME").val
            return ("WS_RECV", sock_name, var_name, tok.line)

        # ws_close sock_name
        if tok.kind == "WS_CLOSE":
            self.consume("WS_CLOSE")
            sock_name = self.consume("NAME").val
            return ("WS_CLOSE", sock_name, tok.line)

        # json_parse str_expr tit var
        if tok.kind == "JSON_PARSE":
            self.consume("JSON_PARSE")
            str_expr = self.parse_expr()
            self.consume("TIT")
            var_name = self.consume("NAME").val
            return ("JSON_PARSE", str_expr, var_name, tok.line)

        # json_dump obj_expr tit var
        if tok.kind == "JSON_DUMP":
            self.consume("JSON_DUMP")
            obj_expr = self.parse_expr()
            self.consume("TIT")
            var_name = self.consume("NAME").val
            return ("JSON_DUMP", obj_expr, var_name, tok.line)

        # ----------------- V1.0.0 DICTIONARIES & COLLECTIONS -----------------
        # dict tit var
        if tok.kind == "DICT":
            self.consume("DICT")
            self.consume("TIT")
            var_name = self.consume("NAME").val
            return ("DICT_NEW", var_name, tok.line)

        # dset dict_name:key_expr:val_expr
        if tok.kind == "DSET":
            self.consume("DSET")
            dict_name = self.consume("NAME").val
            self.consume(":")
            key_expr = self.parse_expr()
            self.consume(":")
            val_expr = self.parse_expr()
            return ("DSET", dict_name, key_expr, val_expr, tok.line)

        # dget dict_name:key_expr tit var
        if tok.kind == "DGET":
            self.consume("DGET")
            dict_name = self.consume("NAME").val
            self.consume(":")
            key_expr = self.parse_expr()
            self.consume("TIT")
            var_name = self.consume("NAME").val
            return ("DGET", dict_name, key_expr, var_name, tok.line)

        # dkeys dict_name tit var
        if tok.kind == "DKEYS":
            self.consume("DKEYS")
            dict_name = self.consume("NAME").val
            self.consume("TIT")
            var_name = self.consume("NAME").val
            return ("DKEYS", dict_name, var_name, tok.line)

        # ----------------- V1.0.0 LIST INDEXING & HELPERS -----------------
        # lget list_name:idx_expr tit var
        if tok.kind == "LGET":
            self.consume("LGET")
            list_name = self.consume("NAME").val
            self.consume(":")
            idx_expr = self.parse_expr()
            self.consume("TIT")
            var_name = self.consume("NAME").val
            return ("LGET", list_name, idx_expr, var_name, tok.line)

        # lset list_name:idx_expr:val_expr
        if tok.kind == "LSET":
            self.consume("LSET")
            list_name = self.consume("NAME").val
            self.consume(":")
            idx_expr = self.parse_expr()
            self.consume(":")
            val_expr = self.parse_expr()
            return ("LSET", list_name, idx_expr, val_expr, tok.line)

        # llen list_name tit var
        if tok.kind == "LLEN":
            self.consume("LLEN")
            list_name = self.consume("NAME").val
            self.consume("TIT")
            var_name = self.consume("NAME").val
            return ("LLEN", list_name, var_name, tok.line)

        # lpush list_name:val_expr
        if tok.kind == "LPUSH":
            self.consume("LPUSH")
            list_name = self.consume("NAME").val
            self.consume(":")
            val_expr = self.parse_expr()
            return ("LPUSH", list_name, val_expr, tok.line)

        # lpop list_name tit var
        if tok.kind == "LPOP":
            self.consume("LPOP")
            list_name = self.consume("NAME").val
            self.consume("TIT")
            var_name = self.consume("NAME").val
            return ("LPOP", list_name, var_name, tok.line)

        # ----------------- V1.0.0 UNIVERSAL FILE I/O -----------------
        # file_write path_expr:data_expr
        if tok.kind == "FILE_WRITE":
            self.consume("FILE_WRITE")
            path_expr = self.parse_expr()
            self.consume(":")
            data_expr = self.parse_expr()
            return ("FILE_WRITE", path_expr, data_expr, tok.line)

        # file_read path_expr tit var
        if tok.kind == "FILE_READ":
            self.consume("FILE_READ")
            path_expr = self.parse_expr()
            self.consume("TIT")
            var_name = self.consume("NAME").val
            return ("FILE_READ", path_expr, var_name, tok.line)

        # file_append path_expr:data_expr
        if tok.kind == "FILE_APPEND":
            self.consume("FILE_APPEND")
            path_expr = self.parse_expr()
            self.consume(":")
            data_expr = self.parse_expr()
            return ("FILE_APPEND", path_expr, data_expr, tok.line)

        # file_exists path_expr tit var
        if tok.kind == "FILE_EXISTS":
            self.consume("FILE_EXISTS")
            path_expr = self.parse_expr()
            self.consume("TIT")
            var_name = self.consume("NAME").val
            return ("FILE_EXISTS", path_expr, var_name, tok.line)

        # file_delete path_expr
        if tok.kind == "FILE_DELETE":
            self.consume("FILE_DELETE")
            path_expr = self.parse_expr()
            return ("FILE_DELETE", path_expr, tok.line)

        # dir_list path_expr tit var
        if tok.kind == "DIR_LIST":
            self.consume("DIR_LIST")
            path_expr = self.parse_expr()
            self.consume("TIT")
            var_name = self.consume("NAME").val
            return ("DIR_LIST", path_expr, var_name, tok.line)

        # ----------------- V1.0.0 PHYSICS & VECTORS -----------------
        # box_hit x1:y1:w1:h1 x2:y2:w2:h2 tit var
        if tok.kind == "BOX_HIT":
            self.consume("BOX_HIT")
            x1 = self.parse_coord_part()
            self.consume(":")
            y1 = self.parse_coord_part()
            self.consume(":")
            w1 = self.parse_coord_part()
            self.consume(":")
            h1 = self.parse_coord_part()
            x2 = self.parse_coord_part()
            self.consume(":")
            y2 = self.parse_coord_part()
            self.consume(":")
            w2 = self.parse_coord_part()
            self.consume(":")
            h2 = self.parse_coord_part()
            self.consume("TIT")
            var_name = self.consume("NAME").val
            return ("BOX_HIT", x1, y1, w1, h1, x2, y2, w2, h2, var_name, tok.line)

        # vec_add x1:y1 x2:y2 tit var
        if tok.kind == "VEC_ADD":
            self.consume("VEC_ADD")
            x1 = self.parse_coord_part()
            self.consume(":")
            y1 = self.parse_coord_part()
            x2 = self.parse_coord_part()
            self.consume(":")
            y2 = self.parse_coord_part()
            self.consume("TIT")
            var_name = self.consume("NAME").val
            return ("VEC_ADD", x1, y1, x2, y2, var_name, tok.line)

        # vec_mag x:y tit var
        if tok.kind == "VEC_MAG":
            self.consume("VEC_MAG")
            x = self.parse_coord_part()
            self.consume(":")
            y = self.parse_coord_part()
            self.consume("TIT")
            var_name = self.consume("NAME").val
            return ("VEC_MAG", x, y, var_name, tok.line)

        # 20. Collection Loop: each item in collection ... tren
        if tok.kind == "EACH":
            self.consume("EACH")
            item_var = self.consume("NAME").val
            self.consume("IN")
            list_var = self.consume("NAME").val
            body = []
            while self.peek().kind not in ("TREN", "EOF"):
                body.append(self.parse_statement())
            self.consume("TREN")
            return ("EACH_LOOP", item_var, list_var, body, tok.line)

        # 21. Conditions: ifr ...
        if tok.kind == "IFR":
            self.consume("IFR")
            
            # Key check
            if self.peek().kind in ("KEY", "FLKEY"):
                is_flkey = (self.peek().kind == "FLKEY")
                self.consume(self.peek().kind)
                key_name = self.consume("STR").val
                if self.peek().kind in ("TRG", "TRGED"):
                    self.consume(self.peek().kind)
                
                if self.peek().kind == "THEN":
                    self.consume("THEN")
                    action_stmt = self.parse_statement()
                    return ("KEY_CHECK", key_name, is_flkey, [action_stmt], tok.line)
                else:
                    body = []
                    while self.peek().kind not in ("TREN", "EOF"):
                        body.append(self.parse_statement())
                    self.consume("TREN")
                    return ("KEY_CHECK", key_name, is_flkey, body, tok.line)

            # Left side of condition
            left = self.parse_atom()

            # Comparison
            if self.peek().kind in ("GRT", "LSS", "SM"):
                op = self.consume(self.peek().kind).val
                right = self.parse_atom()
            else:
                right = self.parse_atom()
                if self.peek().kind not in ("GRT", "LSS", "SM"):
                    raise TrappyError("Condition missing comparison ('grt', 'lss', or 'sm')", self.peek().line)
                op = self.consume(self.peek().kind).val

            condition = ("COND", op, left, right)
            
            then_body = []
            else_body = []
            has_else = False

            while self.peek().kind not in ("THEN", "ELSE", "TREN", "EOF"):
                then_body.append(self.parse_statement())

            if self.peek().kind in ("THEN", "ELSE"):
                self.consume(self.peek().kind)
                has_else = True
                while self.peek().kind not in ("TREN", "EOF"):
                    else_body.append(self.parse_statement())

            self.consume("TREN")
            return ("IF_STMT", condition, then_body, else_body if has_else else None, tok.line)

        # 22. Loops: rep <num|inf> ... tren
        if tok.kind == "REP":
            self.consume("REP")
            if self.peek().kind == "INF":
                self.consume("INF")
                count = "inf"
            else:
                count = self.parse_atom()

            body = []
            while self.peek().kind not in ("TREN", "EOF"):
                body.append(self.parse_statement())
            self.consume("TREN")
            return ("REP_LOOP", count, body, tok.line)

        # 23. Infinite Loop: loop ... tren
        if tok.kind == "LOOP":
            self.consume("LOOP")
            body = []
            while self.peek().kind not in ("TREN", "EOF"):
                body.append(self.parse_statement())
            self.consume("TREN")
            return ("INFINITE_LOOP", body, tok.line)

        # 24. Stop loop: srep or sloop
        if tok.kind == "SREP":
            self.consume("SREP")
            return ("BREAK_REP", tok.line)

        if tok.kind == "SLOOP":
            self.consume("SLOOP")
            return ("BREAK_LOOP", tok.line)

        # 25. Text assignment: txt [eq] <str> tit <var>
        if tok.kind == "TXT":
            self.consume("TXT")
            if self.peek().kind == "EQ":
                self.consume("EQ")
            val_expr = self.parse_expr()
            self.consume("TIT")
            target = self.parse_target_lvalue()
            return ("ASSIGN_TARGET", target, val_expr, tok.line)

        # 26. List creation: lst item | item | item eq <var>
        if tok.kind == "LST":
            self.consume("LST")
            items = [self.parse_expr()]
            while self.peek().kind == "|":
                self.consume("|")
                items.append(self.parse_expr())
            self.consume("EQ")
            target = self.parse_target_lvalue()
            return ("ASSIGN_LIST", target, items, tok.line)

        # 27. Math assignment: mh <expr> eq <name/target>
        if tok.kind == "MH":
            self.consume("MH")
            expr = self.parse_expr()
            self.consume("EQ")
            target = self.parse_target_lvalue()
            return ("ASSIGN_TARGET", target, expr, tok.line)

        # 28. Return answer: answ <expr> or rt <expr>
        if tok.kind in ("ANSW", "RT"):
            self.consume(tok.kind)
            return ("RETURN", self.parse_expr(), tok.line)

        # 29. Output: gan <expr> (Give Answer) or out <expr>
        if tok.kind in ("GAN", "OUT"):
            self.consume(tok.kind)
            return ("OUT", self.parse_expr(), tok.line)

        raise TrappyError(f"Unexpected command '{tok.val}'", tok.line)

    def consume_name_or_str(self):
        tok = self.peek()
        if tok.kind in ("NAME", "STR"):
            self.consume(tok.kind)
            return tok.val
        raise TrappyError(f"Expected name or string, got '{tok.val}'", tok.line)

    def parse_target_lvalue(self):
        """Parses variable target or dot-property target (e.g. 'player' or 'player.x')."""
        name = self.consume("NAME").val
        if self.peek().kind == ".":
            self.consume(".")
            prop = self.consume("NAME").val
            return ("DOT_TARGET", name, prop)
        return ("VAR_TARGET", name)

    def parse_coord_part(self):
        tok = self.peek()
        if tok.kind == "RND":
            self.consume("RND")
            low = self.parse_atom()
            self.consume(":")
            high = self.parse_atom()
            return ("RND", low, high, tok.line)

        if tok.kind == "NUM":
            self.consume("NUM")
            return ("NUM", tok.val)

        if tok.kind == "-":
            self.consume("-")
            sub_tok = self.parse_atom()
            if sub_tok[0] == "NUM":
                return ("NUM", -sub_tok[1])
            return ("BINOP", "-", ("NUM", 0), sub_tok)
        if tok.kind == "NAME":
            name = self.consume("NAME").val
            if self.peek().kind == ".":
                self.consume(".")
                prop = self.consume("NAME").val
                return ("DOT", name, prop, tok.line)
            return ("VAR", name, tok.line)
        raise TrappyError(f"Expected number or coordinate variable, got '{tok.val}'", tok.line)

    def parse_expr(self):
        node = self.parse_term()
        while self.peek().kind in ("+", "-", "BAND", "BOR", "BXOR", "BSHL", "BSHR"):
            op = self.consume(self.peek().kind).val
            right = self.parse_term()
            node = ("BINOP", op, node, right)
        return node

    def parse_term(self):
        node = self.parse_factor()
        while self.peek().kind in ("MULTI", "DIV"):
            op = self.consume(self.peek().kind).val
            right = self.parse_factor()
            node = ("BINOP", op, node, right)
        return node

    def parse_factor(self):
        tok = self.peek()

        if tok.kind in ("SQRT", "ABS", "SIN", "COS"):
            op = self.consume(tok.kind).val
            arg = self.parse_atom()
            return ("MATH_UNARY", op, arg, tok.line)

        if tok.kind == "POW":
            self.consume("POW")
            a = self.parse_atom()
            self.consume(":")
            b = self.parse_atom()
            return ("MATH_BINARY", "pow", a, b, tok.line)

        if tok.kind == "DIST":
            self.consume("DIST")
            x1 = self.parse_atom()
            self.consume(":")
            y1 = self.parse_atom()
            self.consume(":")
            x2 = self.parse_atom()
            self.consume(":")
            y2 = self.parse_atom()
            return ("MATH_DIST", x1, y1, x2, y2, tok.line)

        if tok.kind == "CLAMP":
            self.consume("CLAMP")
            val = self.parse_atom()
            self.consume(":")
            min_v = self.parse_atom()
            self.consume(":")
            max_v = self.parse_atom()
            return ("MATH_CLAMP", val, min_v, max_v, tok.line)

        if tok.kind == "RND":
            self.consume("RND")
            low = self.parse_atom()
            self.consume(":")
            high = self.parse_atom()
            return ("RND", low, high, tok.line)

        if tok.kind == "NUM":
            self.consume("NUM")
            return ("NUM", tok.val)

        if tok.kind == "-":
            self.consume("-")
            sub_tok = self.parse_atom()
            if sub_tok[0] == "NUM":
                return ("NUM", -sub_tok[1])
            return ("BINOP", "-", ("NUM", 0), sub_tok)

        if tok.kind == "STR":
            self.consume("STR")
            return ("STR", tok.val)

        if tok.kind == "(":
            self.consume("(")
            node = self.parse_expr()
            self.consume(")")
            return node

        if tok.kind == "NAME":
            name = self.consume("NAME").val
            # Dot notation check: player.x
            if self.peek().kind == ".":
                self.consume(".")
                prop = self.consume("NAME").val
                return ("DOT", name, prop, tok.line)

            # Function call check
            if name in self.known_functions and self.peek().kind in ("NUM", "STR", "NAME", "("):
                args = [self.parse_atom()]
                while self.peek().kind == ":":
                    self.consume(":")
                    args.append(self.parse_atom())
                return ("CALL", name, args, tok.line)
            return ("VAR", name, tok.line)

        raise TrappyError(f"Invalid item in expression '{tok.val}'", tok.line)

    def parse_atom(self):
        tok = self.peek()
        if tok.kind in ("SQRT", "ABS", "SIN", "COS"):
            op = self.consume(tok.kind).val
            arg = self.parse_atom()
            return ("MATH_UNARY", op, arg, tok.line)

        if tok.kind == "POW":
            self.consume("POW")
            a = self.parse_atom()
            self.consume(":")
            b = self.parse_atom()
            return ("MATH_BINARY", "pow", a, b, tok.line)

        if tok.kind == "DIST":
            self.consume("DIST")
            x1 = self.parse_atom()
            self.consume(":")
            y1 = self.parse_atom()
            self.consume(":")
            x2 = self.parse_atom()
            self.consume(":")
            y2 = self.parse_atom()
            return ("MATH_DIST", x1, y1, x2, y2, tok.line)

        if tok.kind == "CLAMP":
            self.consume("CLAMP")
            val = self.parse_atom()
            self.consume(":")
            min_v = self.parse_atom()
            self.consume(":")
            max_v = self.parse_atom()
            return ("MATH_CLAMP", val, min_v, max_v, tok.line)

        if tok.kind == "RND":
            self.consume("RND")
            low = self.parse_atom()
            self.consume(":")
            high = self.parse_atom()
            return ("RND", low, high, tok.line)

        if tok.kind == "NUM":
            self.consume("NUM")
            return ("NUM", tok.val)

        if tok.kind == "-":
            self.consume("-")
            sub_tok = self.parse_atom()
            if sub_tok[0] == "NUM":
                return ("NUM", -sub_tok[1])
            return ("BINOP", "-", ("NUM", 0), sub_tok)
        if tok.kind == "STR":
            self.consume("STR")
            return ("STR", tok.val)
        if tok.kind == "NAME":
            name = self.consume("NAME").val
            if self.peek().kind == ".":
                self.consume(".")
                prop = self.consume("NAME").val
                return ("DOT", name, prop, tok.line)
            return ("VAR", name, tok.line)
        if tok.kind == "(":
            self.consume("(")
            node = self.parse_expr()
            self.consume(")")
            return node
        raise TrappyError(f"Expected argument, got '{tok.val}'", tok.line)


# =====================================================================
# THE RUNTIME ENVIRONMENT & INTERPRETER
# =====================================================================
class Environment:
    def __init__(self, parent=None):
        self.vars = {}
        self.declared_vars = set()
        self.parent = parent

    def declare(self, name):
        self.declared_vars.add(name)

    def get(self, name, line=None):
        if name in self.vars:
            return self.vars[name]
        if self.parent:
            return self.parent.get(name, line)
        raise TrappyError(f"'{name}' was wiped out or never created!", line)

    def set(self, name, val):
        self.vars[name] = val

    def get_dot(self, obj_name, prop_name, line=None):
        obj = self.get(obj_name, line)
        if isinstance(obj, dict):
            if prop_name in obj:
                return obj[prop_name]
            raise TrappyError(f"Object '{obj_name}' has no property '{prop_name}'", line)
        raise TrappyError(f"'{obj_name}' is not an object or struct!", line)

    def set_dot(self, obj_name, prop_name, val, line=None):
        obj = self.get(obj_name, line)
        if isinstance(obj, dict):
            obj[prop_name] = val
            return
        raise TrappyError(f"Cannot set property '{prop_name}' on non-object '{obj_name}'", line)

    def delete(self, name):
        if name in self.vars:
            del self.vars[name]
            return True
        if self.parent:
            return self.parent.delete(name)
        return False


class ReturnSignal(Exception):
    def __init__(self, value):
        self.value = value


class BreakSignal(Exception):
    def __init__(self, loop_type):
        self.loop_type = loop_type


class TrappyGUI:
    def __init__(self, title, width, height, mode="main"):
        if tk is None:
            raise RuntimeError("Tkinter is required to open GUI windows.")
        self.root = tk.Tk()
        self.root.title(title)
        self.root.geometry(f"{width}x{height}")
        self.root.resizable(False, False)
        self.canvas = tk.Canvas(self.root, width=width, height=height, bg="black", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.pressed_keys = set()
        self.is_focused = True
        self.root.bind("<KeyPress>", self._on_key_press)
        self.root.bind("<KeyRelease>", self._on_key_release)
        self.root.bind("<FocusIn>", lambda e: setattr(self, 'is_focused', True))
        self.root.bind("<FocusOut>", lambda e: setattr(self, 'is_focused', False))

    def _on_key_press(self, event):
        k = event.keysym.upper()
        self.pressed_keys.add(k)
        if event.char:
            self.pressed_keys.add(event.char.upper())

    def _on_key_release(self, event):
        k = event.keysym.upper()
        self.pressed_keys.discard(k)
        if event.char:
            self.pressed_keys.discard(event.char.upper())


class TrappyInterpreter:
    def __init__(self):
        self.global_env = Environment()
        self.functions = {}
        self.del_functions = {}
        self.blueprints = {}
        self.memory_blocks = {}
        self.gui = None
        self.fps_mode = "calm"
        self.target_fps = 60
        self.game_loop_body = None
        self.call_depth = 0
        self.MAX_CALL_DEPTH = 100  # Safe ceiling to prevent Python stack overflow

    def run(self, ast):
        if ast[0] == "PROGRAM":
            for stmt in ast[1]:
                self.eval_stmt(stmt, self.global_env)

            # Start GUI loop if window opened
            if self.gui and self.gui.root:
                if self.game_loop_body:
                    self._schedule_game_frame()
                self.gui.root.mainloop()

    def _schedule_game_frame(self):
        if not self.gui or not self.gui.root:
            return

        start_time = time.time()
        self.gui.canvas.delete("all")

        for stmt in self.game_loop_body:
            self.eval_stmt(stmt, self.global_env)

        elapsed = time.time() - start_time

        if not getattr(self.gui, 'is_focused', True) and self.fps_mode == "calm":
            delay = 66  # Budget hardware saver: 15 FPS when minimized or unfocused
        elif self.fps_mode == "calm":
            delay = max(1, int((0.016 - elapsed) * 1000))
        elif self.fps_mode == "lock":
            target_sec = 1.0 / max(1, self.target_fps)
            delay = max(1, int((target_sec - elapsed) * 1000))
        else:
            delay = 1

        self.gui.root.after(delay, self._schedule_game_frame)

    def eval_stmt(self, stmt, env):
        kind = stmt[0]

        # Registry statements
        if kind == "ADD_VAR":
            _, var_name, type_name, _ = stmt
            env.declare(var_name)
            if type_name and type_name in self.blueprints:
                # Instantiate from blueprint!
                instance = {}
                for k, v_expr in self.blueprints[type_name].items():
                    instance[k] = self.eval_expr(v_expr, env)
                env.set(var_name, instance)
            else:
                env.set(var_name, 0)

        elif kind == "ADD_FUNC":
            _, fn_name, _ = stmt
            pass  # Registered in parser

        elif kind == "ADD_OBJ":
            _, obj_name, raw_fields, _ = stmt
            env.declare(obj_name)
            obj_dict = {}
            for k, v_expr in raw_fields.items():
                obj_dict[k] = self.eval_expr(v_expr, env)
            env.set(obj_name, obj_dict)

        elif kind == "ADD_TYPE":
            _, type_name, fields, _ = stmt
            self.blueprints[type_name] = fields

        elif kind == "ASSIGN_TARGET":
            _, target, expr, line = stmt
            val = self.eval_expr(expr, env)
            if target[0] == "VAR_TARGET":
                env.set(target[1], val)
            elif target[0] == "DOT_TARGET":
                env.set_dot(target[1], target[2], val, line)

        elif kind == "ASSIGN_LIST":
            _, target, raw_items, line = stmt
            val = [self.eval_expr(it, env) for it in raw_items]
            if target[0] == "VAR_TARGET":
                env.set(target[1], val)
            elif target[0] == "DOT_TARGET":
                env.set_dot(target[1], target[2], val, line)

        elif kind == "EACH_LOOP":
            _, item_var, list_var, body, line = stmt
            collection = env.get(list_var, line)
            if not isinstance(collection, list):
                raise TrappyError(f"'{list_var}' is not a list to loop over!", line)
            for element in collection:
                env.set(item_var, element)
                for s in body:
                    self.eval_stmt(s, env)

        elif kind == "OUT":
            _, expr, _ = stmt
            val = self.eval_expr(expr, env)
            if isinstance(val, list):
                pipe_formatted = " | ".join(str(item) for item in val)
                print(f">>> {pipe_formatted}")
            elif isinstance(val, dict):
                props = ", ".join(f"{k}: {v}" for k, v in val.items())
                print(f">>> Object {{{props}}}")
            else:
                print(f">>> {val}")

        elif kind == "FN_DEF":
            _, fn_type, fn_name, params, body, _ = stmt
            self.functions[fn_name] = (fn_type, params, body)

        elif kind == "FDEL_DEF":
            _, fn_name, target_param, body, _ = stmt
            self.del_functions[fn_name] = (target_param, body)

        elif kind == "TRG_ACTION":
            _, fn_name, target_var, line = stmt
            if fn_name in self.del_functions:
                env.delete(target_var)
                print(f"[Memory]: '{target_var}' has been wiped out by {fn_name}!")
            elif fn_name in self.functions:
                fn_type, params, body = self.functions[fn_name]
                local_env = Environment(parent=self.global_env)
                for s in body:
                    self.eval_stmt(s, local_env)
            else:
                raise TrappyError(f"No function named '{fn_name}' found to trigger!", line)

        # ----------------- GUI & VISUALS -----------------
        elif kind == "CWIN":
            _, title, w, h, mode, _ = stmt
            self.gui = TrappyGUI(title, w, h, mode)
            print(f"[Trappy GUI]: Window '{title}' ({w}x{h}) created.")

        elif kind == "WIN_STYLE":
            _, cmd, win_name, color, _ = stmt
            if self.gui:
                bg_color = "black" if color in ("dark", "black") else color
                self.gui.canvas.configure(bg=bg_color)

        elif kind == "LABEL":
            _, text_expr, x_val, y_val, color, _ = stmt
            if self.gui:
                val = self.eval_expr(text_expr, env)
                x = self.eval_coord(x_val, env)
                y = self.eval_coord(y_val, env)
                self.gui.canvas.create_text(x, y, text=str(val), fill=color, font=("Arial", 14, "bold"))

        elif kind == "REGLE":
            _, x_raw, y_raw, w_raw, h_raw, color, _ = stmt
            if self.gui:
                x = self.eval_coord(x_raw, env)
                y = self.eval_coord(y_raw, env)
                w = self.eval_coord(w_raw, env)
                h = self.eval_coord(h_raw, env)
                self.gui.canvas.create_rectangle(x, y, x + w, y + h, fill=color, outline="")

        elif kind == "CIRC":
            _, x_raw, y_raw, r_raw, color, _ = stmt
            if self.gui:
                x = self.eval_coord(x_raw, env)
                y = self.eval_coord(y_raw, env)
                r = self.eval_coord(r_raw, env)
                self.gui.canvas.create_oval(x - r, y - r, x + r, y + r, fill=color, outline="")

        elif kind == "LINE":
            _, x1_raw, y1_raw, x2_raw, y2_raw, color, _ = stmt
            if self.gui:
                x1 = self.eval_coord(x1_raw, env)
                y1 = self.eval_coord(y1_raw, env)
                x2 = self.eval_coord(x2_raw, env)
                y2 = self.eval_coord(y2_raw, env)
                self.gui.canvas.create_line(x1, y1, x2, y2, fill=color, width=2)

        elif kind == "CUBE3D":
            _, x_raw, y_raw, z_raw, size_raw, rx_raw, ry_raw, color, _ = stmt
            if self.gui:
                cx = self.eval_coord(x_raw, env)
                cy = self.eval_coord(y_raw, env)
                cz = self.eval_coord(z_raw, env)
                s = self.eval_coord(size_raw, env) / 2.0
                rx = self.eval_coord(rx_raw, env)
                ry = self.eval_coord(ry_raw, env)

                def proj(vx, vy, vz):
                    rad_y = math.radians(ry)
                    rad_x = math.radians(rx)
                    # Y-rotation
                    x1 = vx * math.cos(rad_y) + vz * math.sin(rad_y)
                    z1 = -vx * math.sin(rad_y) + vz * math.cos(rad_y)
                    # X-rotation
                    y2 = vy * math.cos(rad_x) - z1 * math.sin(rad_x)
                    z2 = vy * math.sin(rad_x) + z1 * math.cos(rad_x) + cz
                    fov = 350.0
                    factor = fov / max(10.0, fov + z2)
                    return cx + x1 * factor, cy + y2 * factor

                verts = [
                    (-s, -s, -s), (s, -s, -s), (s, s, -s), (-s, s, -s),
                    (-s, -s, s),  (s, -s, s),  (s, s, s),  (-s, s, s)
                ]
                pts = [proj(vx, vy, vz) for vx, vy, vz in verts]
                edges = [
                    (0,1), (1,2), (2,3), (3,0),
                    (4,5), (5,6), (6,7), (7,4),
                    (0,4), (1,5), (2,6), (3,7)
                ]
                for i1, i2 in edges:
                    self.gui.canvas.create_line(pts[i1][0], pts[i1][1], pts[i2][0], pts[i2][1], fill=color, width=2)

        elif kind == "LINE3D":
            _, x1_raw, y1_raw, z1_raw, x2_raw, y2_raw, z2_raw, rx_raw, ry_raw, color, _ = stmt
            if self.gui:
                cx, cy = 300, 200
                x1 = self.eval_coord(x1_raw, env)
                y1 = self.eval_coord(y1_raw, env)
                z1 = self.eval_coord(z1_raw, env)
                x2 = self.eval_coord(x2_raw, env)
                y2 = self.eval_coord(y2_raw, env)
                z2 = self.eval_coord(z2_raw, env)
                rx = self.eval_coord(rx_raw, env)
                ry = self.eval_coord(ry_raw, env)
                def proj_pt(vx, vy, vz):
                    rad_y = math.radians(ry)
                    rad_x = math.radians(rx)
                    x_r = vx * math.cos(rad_y) + vz * math.sin(rad_y)
                    z_r = -vx * math.sin(rad_y) + vz * math.cos(rad_y)
                    y_r = vy * math.cos(rad_x) - z_r * math.sin(rad_x)
                    z_f = vy * math.sin(rad_x) + z_r * math.cos(rad_x)
                    fov = 350.0
                    factor = fov / max(10.0, fov + z_f)
                    return cx + x_r * factor, cy + y_r * factor
                p1 = proj_pt(x1, y1, z1)
                p2 = proj_pt(x2, y2, z2)
                self.gui.canvas.create_line(p1[0], p1[1], p2[0], p2[1], fill=color, width=2)

        elif kind == "SPHERE3D":
            _, x_raw, y_raw, z_raw, r_raw, rx_raw, ry_raw, color, _ = stmt
            if self.gui:
                cx = self.eval_coord(x_raw, env)
                cy = self.eval_coord(y_raw, env)
                cz = self.eval_coord(z_raw, env)
                rad = self.eval_coord(r_raw, env)
                rx = self.eval_coord(rx_raw, env)
                ry = self.eval_coord(ry_raw, env)
                def proj_s(vx, vy, vz):
                    r_y = math.radians(ry)
                    r_x = math.radians(rx)
                    x1 = vx * math.cos(r_y) + vz * math.sin(r_y)
                    z1 = -vx * math.sin(r_y) + vz * math.cos(r_y)
                    y2 = vy * math.cos(r_x) - z1 * math.sin(r_x)
                    z2 = vy * math.sin(r_x) + z1 * math.cos(r_x) + cz
                    fov = 350.0
                    factor = fov / max(10.0, fov + z2)
                    return cx + x1 * factor, cy + y2 * factor
                steps = 12
                pts_xy = [proj_s(rad * math.cos(2*math.pi*i/steps), rad * math.sin(2*math.pi*i/steps), 0) for i in range(steps+1)]
                pts_xz = [proj_s(rad * math.cos(2*math.pi*i/steps), 0, rad * math.sin(2*math.pi*i/steps)) for i in range(steps+1)]
                pts_yz = [proj_s(0, rad * math.cos(2*math.pi*i/steps), rad * math.sin(2*math.pi*i/steps)) for i in range(steps+1)]
                for r_pts in (pts_xy, pts_xz, pts_yz):
                    for i in range(steps):
                        self.gui.canvas.create_line(r_pts[i][0], r_pts[i][1], r_pts[i+1][0], r_pts[i+1][1], fill=color, width=2)

        elif kind == "PYRAMID3D":
            _, x_raw, y_raw, z_raw, size_raw, rx_raw, ry_raw, color, _ = stmt
            if self.gui:
                cx = self.eval_coord(x_raw, env)
                cy = self.eval_coord(y_raw, env)
                cz = self.eval_coord(z_raw, env)
                s = self.eval_coord(size_raw, env) / 2.0
                rx = self.eval_coord(rx_raw, env)
                ry = self.eval_coord(ry_raw, env)
                def proj_p(vx, vy, vz):
                    r_y = math.radians(ry)
                    r_x = math.radians(rx)
                    x1 = vx * math.cos(r_y) + vz * math.sin(r_y)
                    z1 = -vx * math.sin(r_y) + vz * math.cos(r_y)
                    y2 = vy * math.cos(r_x) - z1 * math.sin(r_x)
                    z2 = vy * math.sin(r_x) + z1 * math.cos(r_x) + cz
                    fov = 350.0
                    factor = fov / max(10.0, fov + z2)
                    return cx + x1 * factor, cy + y2 * factor
                verts = [
                    (-s, s, -s), (s, s, -s), (s, s, s), (-s, s, s), (0, -s, 0)
                ]
                pts = [proj_p(vx, vy, vz) for vx, vy, vz in verts]
                edges = [
                    (0,1), (1,2), (2,3), (3,0),
                    (0,4), (1,4), (2,4), (3,4)
                ]
                for i1, i2 in edges:
                    self.gui.canvas.create_line(pts[i1][0], pts[i1][1], pts[i2][0], pts[i2][1], fill=color, width=2)

        elif kind == "BUTTON":
            _, btn_text, x_raw, y_raw, action_fn, _ = stmt
            if self.gui:
                x = self.eval_coord(x_raw, env)
                y = self.eval_coord(y_raw, env)
                btn = tk.Button(self.gui.root, text=btn_text, command=lambda: self.trigger_action(action_fn))
                btn.place(x=x, y=y)

        elif kind == "INP":
            _, placeholder, x_raw, y_raw, var_name, _ = stmt
            if self.gui:
                x = self.eval_coord(x_raw, env)
                y = self.eval_coord(y_raw, env)
                entry = tk.Entry(self.gui.root)
                entry.insert(0, placeholder)
                entry.place(x=x, y=y)
                entry.bind("<KeyRelease>", lambda e: env.set(var_name, entry.get()))

        elif kind == "GLOOP":
            _, body, _ = stmt
            self.game_loop_body = body

        elif kind == "FPS_SET":
            _, mode, target_fps, _ = stmt
            self.fps_mode = mode
            if target_fps:
                self.target_fps = target_fps
            print(f"[Trappy Engine]: FPS set to {mode.upper()}" + (f" ({target_fps})" if target_fps else ""))

        elif kind == "KEY_CHECK":
            _, key_name, is_flkey, body, _ = stmt
            target_key = key_name.upper()
            if self.gui and target_key in self.gui.pressed_keys:
                for s in body:
                    self.eval_stmt(s, env)
                if is_flkey:
                    self.gui.pressed_keys.discard(target_key)

        elif kind == "PLAY_AUDIO":
            _, snd_file, _ = stmt
            if winsound:
                try:
                    safe_snd = sanitize_path(snd_file)
                    winsound.PlaySound(safe_snd, winsound.SND_FILENAME | winsound.SND_ASYNC)
                except Exception:
                    winsound.MessageBeep()

        elif kind == "BEEP_AUDIO":
            _, freq_raw, dur_raw, _ = stmt
            if winsound:
                freq = int(self.eval_coord(freq_raw, env))
                dur = int(self.eval_coord(dur_raw, env))
                try:
                    winsound.Beep(max(37, min(32767, freq)), max(10, dur))
                except Exception:
                    pass

        elif kind == "SYNTH_AUDIO":
            _, wave_raw, freq_raw, dur_raw, _ = stmt
            if winsound:
                try:
                    freq = int(self.eval_coord(freq_raw, env))
                    dur = int(self.eval_coord(dur_raw, env))
                    winsound.Beep(max(37, min(32767, freq)), max(10, dur))
                except Exception:
                    pass

        elif kind == "WRITE_FILE":
            _, filename, val_expr, dest_dir, line = stmt
            val = self.eval_expr(val_expr, env)
            target_file = sanitize_path(filename, dest_dir)
            with open(target_file, "w") as f:
                f.write(str(val))
            print(f"[Trappy IO]: Saved data to '{target_file}'")

        # ----------------- UNIVERSAL WEB & INTERNET -----------------
        elif kind == "HTTP_GET":
            _, url_expr, var_name, line = stmt
            url = str(self.eval_expr(url_expr, env))
            try:
                req = urllib.request.Request(
                    url,
                    headers={'User-Agent': 'Trappy/1.0 (Universal Web Client)'}
                )
                with urllib.request.urlopen(req, timeout=10) as response:
                    body = response.read().decode('utf-8', errors='ignore')
                    env.set(var_name, body)
            except Exception as e:
                env.set(var_name, f"[Trappy Web Error]: {e}")

        elif kind == "HTTP_POST":
            _, url_expr, data_expr, var_name, line = stmt
            url = str(self.eval_expr(url_expr, env))
            data_raw = self.eval_expr(data_expr, env)
            payload = json.dumps(data_raw).encode('utf-8') if isinstance(data_raw, dict) else str(data_raw).encode('utf-8')
            try:
                req = urllib.request.Request(
                    url,
                    data=payload,
                    headers={
                        'User-Agent': 'Trappy/1.0',
                        'Content-Type': 'application/json' if isinstance(data_raw, dict) else 'text/plain'
                    }
                )
                with urllib.request.urlopen(req, timeout=10) as response:
                    body = response.read().decode('utf-8', errors='ignore')
                    env.set(var_name, body)
            except Exception as e:
                env.set(var_name, f"[Trappy Web Error]: {e}")

        elif kind == "DOWNLOAD_FILE":
            _, url_expr, dest_file, line = stmt
            url = str(self.eval_expr(url_expr, env))
            target_path = sanitize_path(dest_file)
            try:
                req = urllib.request.Request(
                    url,
                    headers={'User-Agent': 'Trappy/0.9'}
                )
                with urllib.request.urlopen(req, timeout=15) as response:
                    content = response.read()
                with open(target_path, 'wb') as f:
                    f.write(content)
                print(f"[Trappy Web]: Successfully downloaded '{url}' -> '{target_path}'")
            except Exception as e:
                raise TrappyError(f"Download failed: {e}", line)

        # ----------------- PACKETS & CLIENT-SERVER NETWORKING -----------------
        elif kind == "PACK_DATA":
            _, data_expr, var_name, line = stmt
            data_val = self.eval_expr(data_expr, env)
            try:
                packet_str = "TRP:" + json.dumps(data_val)
                env.set(var_name, packet_str)
            except Exception as e:
                env.set(var_name, f"TRP:{data_val}")

        elif kind == "UNPACK_DATA":
            _, data_expr, var_name, line = stmt
            raw_pkt = str(self.eval_expr(data_expr, env))
            if raw_pkt.startswith("TRP:"):
                raw_pkt = raw_pkt[4:]
            try:
                parsed = json.loads(raw_pkt)
                env.set(var_name, parsed)
            except Exception:
                env.set(var_name, raw_pkt)

        elif kind == "CLI_CONNECT":
            _, host_expr, port_expr, var_name, line = stmt
            host = str(self.eval_expr(host_expr, env))
            port = int(self.eval_expr(port_expr, env))
            if host.lower() in ("loopback", "offline"):
                sock = VirtualLoopbackSocket(channel_id=f"port_{port}")
                env.set(var_name, sock)
                print(f"[Trappy Client]: Connected to offline loopback bus (port {port})")
            else:
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(1.0)
                    s.connect((host, port))
                    s.settimeout(0.05) # Calm non-blocking read for game loops
                    env.set(var_name, s)
                    print(f"[Trappy Client]: Connected to {host}:{port}")
                except Exception as e:
                    # Budget resilience: if offline, fallback to virtual loopback channel
                    sock = VirtualLoopbackSocket(channel_id=f"port_{port}")
                    env.set(var_name, sock)
                    print(f"[Trappy Client]: Offline fallback active -> loopback channel {port}")

        elif kind == "CLI_SEND":
            _, client_name, data_expr, line = stmt
            sock = env.get(client_name, line)
            payload = self.eval_expr(data_expr, env)
            if sock and hasattr(sock, "sendall"):
                try:
                    msg = str(payload) + "\n"
                    sock.sendall(msg.encode('utf-8'))
                except Exception as e:
                    pass
            elif sock and hasattr(sock, "send"):
                sock.send(payload)

        elif kind == "CLI_RECV":
            _, client_name, var_name, line = stmt
            sock = env.get(client_name, line)
            msg = ""
            if sock and hasattr(sock, "recv"):
                try:
                    raw = sock.recv(4096)
                    if isinstance(raw, bytes):
                        msg = raw.decode('utf-8', errors='ignore').strip()
                    else:
                        msg = str(raw).strip()
                except socket.timeout:
                    msg = ""
                except Exception:
                    msg = ""
            env.set(var_name, msg)

        elif kind == "CLI_CLOSE":
            _, client_name, line = stmt
            sock = env.get(client_name, line)
            if sock and hasattr(sock, "close"):
                try:
                    sock.close()
                except Exception:
                    pass
            env.set(client_name, None)

        elif kind == "SRV_LISTEN":
            _, port_expr, var_name, line = stmt
            port = int(self.eval_expr(port_expr, env))
            try:
                srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                srv.bind(("0.0.0.0", port))
                srv.listen(5)
                srv.settimeout(0.05) # Calm non-blocking
                env.set(var_name, srv)
                print(f"[Trappy Server]: Listening on port {port}")
            except Exception as e:
                env.set(var_name, None)
                print(f"[Trappy Server]: Failed to bind on port {port}: {e}")

        elif kind == "SRV_ACCEPT":
            _, server_name, var_name, line = stmt
            srv = env.get(server_name, line)
            if srv and isinstance(srv, socket.socket):
                try:
                    conn, addr = srv.accept()
                    conn.settimeout(0.05)
                    env.set(var_name, conn)
                except socket.timeout:
                    env.set(var_name, None)
                except Exception:
                    env.set(var_name, None)
            else:
                env.set(var_name, None)

        # ----------------- OS & LOW-LEVEL MEMORY PRIMITIVES -----------------
        elif kind == "MEM_ALLOC":
            _, size_expr, var_name, line = stmt
            size = int(self.eval_expr(size_expr, env))
            ptr = len(self.memory_blocks) + 1
            self.memory_blocks[ptr] = bytearray(size)
            env.set(var_name, ptr)

        elif kind == "MEM_WRITE":
            _, ptr_name, offset_expr, byte_expr, line = stmt
            ptr = env.get(ptr_name, line)
            offset = int(self.eval_expr(offset_expr, env))
            b = int(self.eval_expr(byte_expr, env))
            if ptr in self.memory_blocks:
                block = self.memory_blocks[ptr]
                if 0 <= offset < len(block):
                    block[offset] = b & 0xFF

        elif kind == "MEM_READ":
            _, ptr_name, offset_expr, var_name, line = stmt
            ptr = env.get(ptr_name, line)
            offset = int(self.eval_expr(offset_expr, env))
            val = 0
            if ptr in self.memory_blocks:
                block = self.memory_blocks[ptr]
                if 0 <= offset < len(block):
                    val = block[offset]
            env.set(var_name, val)

        elif kind == "SYS_EXEC":
            _, cmd_expr, var_name, line = stmt
            cmd = str(self.eval_expr(cmd_expr, env))
            try:
                res = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
                env.set(var_name, res.stdout.strip())
            except Exception as e:
                env.set(var_name, f"[Sys Error]: {e}")

        elif kind == "SYS_ENV":
            _, name_expr, var_name, line = stmt
            k = str(self.eval_expr(name_expr, env))
            env.set(var_name, os.environ.get(k, ""))

        # ----------------- V1.0.0 CONNECTIVITY & DISCORD -----------------
        elif kind == "DISCORD_WEBHOOK":
            _, url_expr, msg_expr, var_name, line = stmt
            url = str(self.eval_expr(url_expr, env))
            msg = str(self.eval_expr(msg_expr, env))
            try:
                payload = json.dumps({"content": msg}).encode('utf-8')
                req = urllib.request.Request(
                    url,
                    data=payload,
                    headers={
                        'User-Agent': 'Trappy-Discord/1.0',
                        'Content-Type': 'application/json'
                    }
                )
                with urllib.request.urlopen(req, timeout=5) as resp:
                    env.set(var_name, resp.status)
            except urllib.error.HTTPError as he:
                env.set(var_name, he.code)
            except Exception as e:
                env.set(var_name, f"[Discord Error]: {e}")

        elif kind == "WS_CONNECT":
            _, url_expr, var_name, line = stmt
            url = str(self.eval_expr(url_expr, env))
            sock = VirtualLoopbackSocket(channel_id=url)
            env.set(var_name, sock)
            print(f"[Trappy Socket]: Connected stream '{url}'")

        elif kind == "WS_SEND":
            _, sock_name, msg_expr, line = stmt
            sock = env.get(sock_name, line)
            msg = self.eval_expr(msg_expr, env)
            if sock and hasattr(sock, "sendall"):
                sock.sendall(msg)
            elif sock and hasattr(sock, "send"):
                sock.send(msg)

        elif kind == "WS_RECV":
            _, sock_name, var_name, line = stmt
            sock = env.get(sock_name, line)
            val = ""
            if sock and hasattr(sock, "recv"):
                raw = sock.recv(4096)
                val = raw.decode('utf-8', errors='ignore') if isinstance(raw, bytes) else str(raw)
            env.set(var_name, val)

        elif kind == "WS_CLOSE":
            _, sock_name, line = stmt
            sock = env.get(sock_name, line)
            if sock and hasattr(sock, "close"):
                sock.close()
            env.set(sock_name, None)

        elif kind == "JSON_PARSE":
            _, str_expr, var_name, line = stmt
            raw = str(self.eval_expr(str_expr, env))
            try:
                parsed = json.loads(raw)
                env.set(var_name, parsed)
            except Exception:
                env.set(var_name, None)

        elif kind == "JSON_DUMP":
            _, obj_expr, var_name, line = stmt
            obj = self.eval_expr(obj_expr, env)
            try:
                dumped = json.dumps(obj)
                env.set(var_name, dumped)
            except Exception:
                env.set(var_name, str(obj))

        # ----------------- V1.0.0 DICTIONARIES & COLLECTIONS -----------------
        elif kind == "DICT_NEW":
            _, var_name, line = stmt
            env.declare(var_name)
            env.set(var_name, {})

        elif kind == "DSET":
            _, dict_name, key_expr, val_expr, line = stmt
            d = env.get(dict_name, line)
            k = self.eval_expr(key_expr, env)
            v = self.eval_expr(val_expr, env)
            if isinstance(d, dict):
                d[k] = v

        elif kind == "DGET":
            _, dict_name, key_expr, var_name, line = stmt
            d = env.get(dict_name, line)
            k = self.eval_expr(key_expr, env)
            val = d.get(k) if isinstance(d, dict) else None
            env.set(var_name, val)

        elif kind == "DKEYS":
            _, dict_name, var_name, line = stmt
            d = env.get(dict_name, line)
            keys = list(d.keys()) if isinstance(d, dict) else []
            env.set(var_name, keys)

        # ----------------- V1.0.0 LIST INDEXING & HELPERS -----------------
        elif kind == "LGET":
            _, list_name, idx_expr, var_name, line = stmt
            lst = env.get(list_name, line)
            idx = int(self.eval_expr(idx_expr, env))
            val = None
            if isinstance(lst, (list, tuple)) and 0 <= idx < len(lst):
                val = lst[idx]
            env.set(var_name, val)

        elif kind == "LSET":
            _, list_name, idx_expr, val_expr, line = stmt
            lst = env.get(list_name, line)
            idx = int(self.eval_expr(idx_expr, env))
            val = self.eval_expr(val_expr, env)
            if isinstance(lst, list) and 0 <= idx < len(lst):
                lst[idx] = val

        elif kind == "LLEN":
            _, list_name, var_name, line = stmt
            lst = env.get(list_name, line)
            l = len(lst) if isinstance(lst, (list, tuple, dict, str)) else 0
            env.set(var_name, l)

        elif kind == "LPUSH":
            _, list_name, val_expr, line = stmt
            lst = env.get(list_name, line)
            val = self.eval_expr(val_expr, env)
            if isinstance(lst, list):
                lst.append(val)

        elif kind == "LPOP":
            _, list_name, var_name, line = stmt
            lst = env.get(list_name, line)
            val = lst.pop() if isinstance(lst, list) and lst else None
            env.set(var_name, val)

        # ----------------- V1.0.0 UNIVERSAL FILE I/O -----------------
        elif kind == "FILE_WRITE":
            _, path_expr, data_expr, line = stmt
            target_path = sanitize_path(str(self.eval_expr(path_expr, env)))
            data = self.eval_expr(data_expr, env)
            with open(target_path, "w", encoding="utf-8") as f:
                f.write(str(data))

        elif kind == "FILE_READ":
            _, path_expr, var_name, line = stmt
            target_path = sanitize_path(str(self.eval_expr(path_expr, env)))
            content = ""
            if os.path.exists(target_path):
                with open(target_path, "r", encoding="utf-8") as f:
                    content = f.read()
            env.set(var_name, content)

        elif kind == "FILE_APPEND":
            _, path_expr, data_expr, line = stmt
            target_path = sanitize_path(str(self.eval_expr(path_expr, env)))
            data = self.eval_expr(data_expr, env)
            with open(target_path, "a", encoding="utf-8") as f:
                f.write(str(data))

        elif kind == "FILE_EXISTS":
            _, path_expr, var_name, line = stmt
            target_path = sanitize_path(str(self.eval_expr(path_expr, env)))
            env.set(var_name, 1 if os.path.exists(target_path) else 0)

        elif kind == "FILE_DELETE":
            _, path_expr, line = stmt
            target_path = sanitize_path(str(self.eval_expr(path_expr, env)))
            if os.path.exists(target_path):
                os.remove(target_path)

        elif kind == "DIR_LIST":
            _, path_expr, var_name, line = stmt
            target_path = sanitize_path(str(self.eval_expr(path_expr, env)))
            files = os.listdir(target_path) if os.path.isdir(target_path) else []
            env.set(var_name, files)

        # ----------------- V1.0.0 PHYSICS & VECTORS -----------------
        elif kind == "BOX_HIT":
            _, x1_raw, y1_raw, w1_raw, h1_raw, x2_raw, y2_raw, w2_raw, h2_raw, var_name, line = stmt
            x1 = self.eval_coord(x1_raw, env)
            y1 = self.eval_coord(y1_raw, env)
            w1 = self.eval_coord(w1_raw, env)
            h1 = self.eval_coord(h1_raw, env)
            x2 = self.eval_coord(x2_raw, env)
            y2 = self.eval_coord(y2_raw, env)
            w2 = self.eval_coord(w2_raw, env)
            h2 = self.eval_coord(h2_raw, env)
            hit = 1 if (x1 < x2 + w2 and x1 + w1 > x2 and y1 < y2 + h2 and y1 + h1 > y2) else 0
            env.set(var_name, hit)

        elif kind == "VEC_ADD":
            _, x1_raw, y1_raw, x2_raw, y2_raw, var_name, line = stmt
            x1 = self.eval_coord(x1_raw, env)
            y1 = self.eval_coord(y1_raw, env)
            x2 = self.eval_coord(x2_raw, env)
            y2 = self.eval_coord(y2_raw, env)
            env.set(var_name, [x1 + x2, y1 + y2])

        elif kind == "VEC_MAG":
            _, x_raw, y_raw, var_name, line = stmt
            x = self.eval_coord(x_raw, env)
            y = self.eval_coord(y_raw, env)
            env.set(var_name, math.hypot(x, y))

        # ----------------- LOGIC & CONTROL -----------------
        elif kind == "IF_STMT":
            _, condition, then_body, else_body, _ = stmt
            _, op, left_expr, right_expr = condition
            left = self.eval_expr(left_expr, env)
            right = self.eval_expr(right_expr, env)

            # Optimization / Bug Fix: Treat None (such as failed socket) as 0 in numeric comparisons
            if left is None and isinstance(right, (int, float)):
                left = 0
            if right is None and isinstance(left, (int, float)):
                right = 0

            is_true = False
            if op == "grt": is_true = (left > right)
            elif op == "lss": is_true = (left < right)
            elif op == "sm": is_true = (left == right)

            if is_true:
                for s in then_body:
                    self.eval_stmt(s, env)
            elif else_body:
                for s in else_body:
                    self.eval_stmt(s, env)

        elif kind == "REP_LOOP":
            _, count_expr, body, _ = stmt
            count = "inf" if count_expr == "inf" else self.eval_expr(count_expr, env)
            i = 0
            while True:
                if count != "inf" and i >= count:
                    break
                try:
                    for s in body:
                        self.eval_stmt(s, env)
                except BreakSignal as b:
                    if b.loop_type == "srep":
                        break
                    raise b
                i += 1

        elif kind == "INFINITE_LOOP":
            _, body, _ = stmt
            while True:
                try:
                    for s in body:
                        self.eval_stmt(s, env)
                except BreakSignal as b:
                    if b.loop_type == "sloop":
                        break
                    raise b

        elif kind == "BREAK_REP":
            raise BreakSignal("srep")

        elif kind == "BREAK_LOOP":
            raise BreakSignal("sloop")

        elif kind == "RETURN":
            _, expr, _ = stmt
            val = self.eval_expr(expr, env)
            raise ReturnSignal(val)

    def trigger_action(self, fn_name):
        if fn_name in self.functions:
            fn_type, params, body = self.functions[fn_name]
            local_env = Environment(parent=self.global_env)
            for s in body:
                self.eval_stmt(s, local_env)

    def eval_coord(self, raw, env):
        if isinstance(raw, (int, float)):
            return raw
        if isinstance(raw, str):
            return env.get(raw)
        if isinstance(raw, (tuple, list)):
            if raw[0] == "NUM":
                return raw[1]
            if raw[0] == "VAR":
                return env.get(raw[1], raw[2] if len(raw) > 2 else None)
            if raw[0] == "DOT":
                return env.get_dot(raw[1], raw[2], raw[3] if len(raw) > 3 else None)
            if raw[0] == "RND":
                low = int(self.eval_coord(raw[1], env))
                high = int(self.eval_coord(raw[2], env))
                return random.randint(low, high)
        return 0

    def eval_expr(self, expr, env):
        kind = expr[0]

        if kind == "NUM":
            return expr[1]

        if kind == "STR":
            return expr[1]

        if kind == "RND":
            low = int(self.eval_expr(expr[1], env))
            high = int(self.eval_expr(expr[2], env))
            return random.randint(low, high)

        if kind == "VAR":
            return env.get(expr[1], expr[2])

        if kind == "DOT":
            _, obj_name, prop_name, line = expr
            return env.get_dot(obj_name, prop_name, line)

        if kind == "BINOP":
            op = expr[1]
            left = self.eval_expr(expr[2], env)
            right = self.eval_expr(expr[3], env)
            if op == "+": 
                if isinstance(left, str) or isinstance(right, str):
                    return str(left) + str(right)
                return left + right
            if op == "-": return left - right
            if op == "multi": return left * right
            if op == "div": return left // right
            # Bitwise Operators
            if op == "band": return int(left) & int(right)
            if op == "bor": return int(left) | int(right)
            if op == "bxor": return int(left) ^ int(right)
            if op == "bshl": return int(left) << int(right)
            if op == "bshr": return int(left) >> int(right)

        if kind == "MATH_UNARY":
            _, op, arg, line = expr
            val = float(self.eval_expr(arg, env))
            if op == "sqrt":
                return math.sqrt(max(0.0, val))
            if op == "abs":
                return abs(val)
            if op == "sin":
                return math.sin(math.radians(val))
            if op == "cos":
                return math.cos(math.radians(val))

        if kind == "MATH_BINARY":
            _, op, a, b, line = expr
            val_a = float(self.eval_expr(a, env))
            val_b = float(self.eval_expr(b, env))
            if op == "pow":
                return math.pow(val_a, val_b)

        if kind == "MATH_DIST":
            _, x1, y1, x2, y2, line = expr
            v_x1 = float(self.eval_expr(x1, env))
            v_y1 = float(self.eval_expr(y1, env))
            v_x2 = float(self.eval_expr(x2, env))
            v_y2 = float(self.eval_expr(y2, env))
            return math.hypot(v_x1 - v_x2, v_y1 - v_y2)

        if kind == "MATH_CLAMP":
            _, v, min_v, max_v, line = expr
            val = float(self.eval_expr(v, env))
            low = float(self.eval_expr(min_v, env))
            high = float(self.eval_expr(max_v, env))
            return max(low, min(high, val))

        if kind == "CALL":
            _, fn_name, args, line = expr
            
            # Anti-recursion bomb check: Check BEFORE evaluating arguments!
            self.call_depth += 1
            if self.call_depth > self.MAX_CALL_DEPTH:
                self.call_depth = 0
                raise TrappySecurityError(
                    f"Infinite recursion bomb detected! Exceeded max stack depth ({self.MAX_CALL_DEPTH})", line
                )

            evaluated_args = [self.eval_expr(a, env) for a in args]

            if fn_name not in self.functions:
                self.call_depth -= 1
                raise TrappyError(f"Undefined Trappy function '{fn_name}'", line)

            fn_type, params, body = self.functions[fn_name]
            if len(params) != len(evaluated_args):
                self.call_depth -= 1
                raise TrappyError(
                    f"Function '{fn_name}' expects {len(params)} arguments, got {len(evaluated_args)}", line
                )

            local_env = Environment(parent=self.global_env)
            for p, a in zip(params, evaluated_args):
                local_env.set(p, a)

            try:
                for s in body:
                    self.eval_stmt(s, local_env)
            except ReturnSignal as ret:
                self.call_depth -= 1
                return ret.value
            
            self.call_depth -= 1
            return None


# =====================================================================
# CLI RUNNER ENTRYPOINT
# =====================================================================
if __name__ == "__main__":
    args = sys.argv[1:]
    if args and args[0].lower() in ("trpexec", "run", "exec"):
        args = args[1:]

    if args:
        target_file = args[0]
        try:
            with open(target_file, "r") as f:
                code = f.read()
            tokens = tokenize(code)
            parser = Parser(tokens)
            ast = parser.parse_program()
            interpreter = TrappyInterpreter()
            interpreter.run(ast)
        except TrappyError as err:
            print(err)
            sys.exit(1)
        except Exception as general_err:
            print(f"\n[TRAPPY]: A Syntax is being invalid: {general_err}")
            sys.exit(1)
    else:
        print("[TRAPPY]: Please specify a file to run! Example: trpexec script.trappy")
