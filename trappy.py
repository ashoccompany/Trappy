import sys
import os
import time
import math
import random
import socket
import select
import urllib.request
import urllib.parse
import json
import subprocess
import queue

try:
    import tkinter as tk
    from tkinter import ttk, messagebox
except ImportError:
    tk = None

try:
    import winsound
except ImportError:
    winsound = None

__version__ = "1.15.0"

class VirtualLoopbackSocket:
    _channels = {}

    def __init__(self, channel_id="default"):
        self.channel_id = str(channel_id)
        if self.channel_id not in VirtualLoopbackSocket._channels:
            VirtualLoopbackSocket._channels[self.channel_id] = queue.Queue()
        self.q = VirtualLoopbackSocket._channels[self.channel_id]
        self.is_open = True

    def sendall(self, data):
        if not self.is_open:
            return 0
        if isinstance(data, str):
            data = data.encode('utf-8')
        self.q.put(data)
        return len(data)

    def send(self, data):
        return self.sendall(data)

    def recv(self, bufsize=4096):
        if not self.is_open:
            return b""
        try:
            val = self.q.get_nowait()
            return val
        except queue.Empty:
            return b""

    def close(self):
        self.is_open = False

class TrappyError(Exception):
    def __init__(self, message, line=None):
        self.message = message
        self.line = line
        super().__init__(f"[Trappy Error at line {line}]: {message}" if line else f"[Trappy Error]: {message}")

class TrappySecurityError(TrappyError):
    def __init__(self, message, line=None):
        hint = "[TRAPPY HINT]: Press F1 in IDE for Manual or ask on Discord: https://discord.gg/3chDfAPE9H"
        super().__init__(f"SECURITY VIOLATION: {message}\n{hint}", line)

class ReturnSignal(Exception):
    def __init__(self, value):
        self.value = value

class BreakSignal(Exception):
    def __init__(self, loop_type="all"):
        self.loop_type = loop_type

class ContinueSignal(Exception):
    pass

def sanitize_path(filename, base_dir=None):
    if base_dir is None:
        base_dir = os.getcwd()
    base_dir = os.path.abspath(base_dir)
    target_path = os.path.abspath(os.path.join(base_dir, filename))
    if not (target_path == base_dir or target_path.startswith(base_dir + os.sep)):
        raise TrappySecurityError(f"Path Traversal attempt blocked: '{filename}'")
    return target_path

def validate_url(url, line=None):
    if not isinstance(url, str):
        raise TrappySecurityError("URL must be a string", line)
    clean_url = url.strip()
    parsed = urllib.parse.urlparse(clean_url)
    if parsed.scheme.lower() not in ("http", "https"):
        raise TrappySecurityError(
            f"Blocked insecure URL scheme '{parsed.scheme}': only HTTP and HTTPS are permitted",
            line
        )
    return clean_url

class Token:
    def __init__(self, kind, val, line=0):
        self.kind = kind
        self.val = val
        self.line = line

    def __repr__(self):
        return f"Token({self.kind}, {repr(self.val)}, L{self.line})"

def tokenize(code):
    tokens = []
    line = 1
    i = 0
    n = len(code)

    keywords = {
        "trst", "tren", "fmh", "fdel", "ftxt", "flist", "frep", "floop",
        "fgui", "fui", "fdrw", "fgfx", "fcan", "fweb", "fcli", "fapp", "f3d", "fos",
        "mh", "eq", "rt", "answ", "out", "gan", "trg", "trged", "multi", "div",
        "sqrt", "pow", "abs", "sin", "cos", "dist", "clamp",
        "box_hit", "vec_add", "vec_mag",
        "band", "bor", "bxor", "bnot", "bshl", "bshr",
        "http_get", "http_post", "download", "discord_webhook",
        "ws_connect", "ws_send", "ws_recv", "ws_close",
        "json_parse", "json_dump",
        "pack", "unpack", "pack_data", "unpack_data",
        "cli_connect", "cli_send", "cli_recv", "cli_close",
        "srv_listen", "srv_accept",
        "dict", "dset", "dget", "dkeys",
        "lst", "lget", "lset", "llen", "lpush", "lpop",
        "file_write", "file_read", "file_append", "file_exists", "file_delete", "dir_list",
        "ifr", "then", "else", "grt", "lss", "sm", "exst", "exist",
        "rep", "loop", "srep", "sloop", "while", "swhile", "break", "continue", "cnt",
        "try", "catch", "fn", "func", "return",
        "slen", "sget", "ssub", "ssplit", "sjoin", "sfind", "sreplace", "strim", "slower", "supper",
        "ord", "chr", "is_digit", "is_alpha",
        "type_of", "to_str", "to_num", "to_int", "to_float",
        "dhas", "ddel", "lcontains", "linsert", "lslice",
        "txt", "tit", "inf", "ath",
        "add_var", "add_func", "add_obj", "add_type", "spawn", "as",
        "cwin", "swin", "sbgwin", "label", "regle", "circ", "line",
        "cube3d", "line3d", "point3d", "sphere3d", "pyramid3d",
        "mem_alloc", "mem_write", "mem_read", "sys_exec", "sys_env",
        "btn", "inp", "psed", "changed", "gloop", "fps", "calm", "lock", "unlock",
        "key", "flkey", "mousel", "mouser", "mousesp", "collde", "collide",
        "hrable", "play", "beep", "synth", "rnd", "write", "into", "each", "in"
    }

    while i < n:
        c = code[i]

        if c == "\n":
            line += 1
            i += 1
            continue

        if c.isspace():
            i += 1
            continue

        if c == '#':
            while i < n and code[i] != '\n':
                i += 1
            continue

        if c == '"':
            start_line = line
            i += 1
            start_s = i
            while i < n and code[i] != '"':
                if code[i] == '\n':
                    line += 1
                i += 1
            if i >= n:
                raise TrappyError("Unclosed string quote", start_line)
            str_val = code[start_s:i]
            i += 1
            tokens.append(Token("STR", str_val, start_line))
            continue

        if c == '=' and i + 1 < n and code[i + 1] == '=':
            tokens.append(Token("==", "==", line))
            i += 2
            continue

        if c == '!' and i + 1 < n and code[i + 1] == '=':
            tokens.append(Token("!=", "!=", line))
            i += 2
            continue

        if c == '>' and i + 1 < n and code[i + 1] == '=':
            tokens.append(Token(">=", ">=", line))
            i += 2
            continue

        if c == '<' and i + 1 < n and code[i + 1] == '=':
            tokens.append(Token("<=", "<=", line))
            i += 2
            continue

        if c in "():+=|,><*/%":
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

        if c == '0' and i + 1 < n and code[i+1].lower() == 'x':
            i += 2
            start_hex = i
            while i < n and (code[i].isdigit() or code[i].lower() in "abcdef"):
                i += 1
            hex_str = code[start_hex:i]
            tokens.append(Token("NUM", int(hex_str, 16) if hex_str else 0, line))
            continue

        if c.isdigit() or (c == '.' and i + 1 < n and code[i + 1].isdigit()):
            start_num = i
            is_float = False
            if c == '.':
                is_float = True
                i += 1
            while i < n and code[i].isdigit():
                i += 1
            if not is_float and i < n and code[i] == '.' and i + 1 < n and code[i + 1].isdigit():
                is_float = True
                i += 1
                while i < n and code[i].isdigit():
                    i += 1
            num_str = code[start_num:i]
            num_val = float(num_str) if is_float else int(num_str)
            tokens.append(Token("NUM", num_val, line))
            continue

        if c.isalpha() or c == "_":
            start_w = i
            while i < n and (code[i].isalnum() or code[i] == "_"):
                i += 1
            word = code[start_w:i]
            if word in keywords:
                tokens.append(Token(word.upper(), word, line))
            else:
                tokens.append(Token("NAME", word, line))
            continue

        raise TrappyError(f"Unexpected character '{c}'", line)

    tokens.append(Token("EOF", None, line))
    return tokens

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.known_functions = set()
        self.known_variables = set()
        self.blueprints = {}

        self._dispatch = {
            "ADD_VAR": self._parse_add_var,
            "ADD_FUNC": self._parse_add_func,
            "ADD_OBJ": self._parse_add_obj,
            "ADD_TYPE": self._parse_add_type,
            "FDEL": self._parse_fdel,
            "TRG": self._parse_trg,
            "CWIN": self._parse_cwin,
            "SWIN": self._parse_cwin,
            "SBGWIN": self._parse_sbgwin,
            "LABEL": self._parse_label,
            "REGLE": self._parse_regle,
            "CIRC": self._parse_circ,
            "LINE": self._parse_line,
            "CUBE3D": self._parse_cube3d,
            "LINE3D": self._parse_line3d,
            "SPHERE3D": self._parse_sphere3d,
            "PYRAMID3D": self._parse_pyramid3d,
            "BTN": self._parse_btn,
            "INP": self._parse_inp,
            "GLOOP": self._parse_gloop,
            "FPS": self._parse_fps,
            "PLAY": self._parse_play,
            "BEEP": self._parse_beep,
            "SYNTH": self._parse_synth,
            "WRITE": self._parse_write,
            "HTTP_GET": self._parse_http_get,
            "HTTP_POST": self._parse_http_post,
            "DOWNLOAD": self._parse_download,
            "CLI_CONNECT": self._parse_cli_connect,
            "CLI_SEND": self._parse_cli_send,
            "CLI_RECV": self._parse_cli_recv,
            "CLI_CLOSE": self._parse_cli_close,
            "SRV_LISTEN": self._parse_srv_listen,
            "SRV_ACCEPT": self._parse_srv_accept,
            "MEM_ALLOC": self._parse_mem_alloc,
            "MEM_WRITE": self._parse_mem_write,
            "MEM_READ": self._parse_mem_read,
            "SYS_EXEC": self._parse_sys_exec,
            "SYS_ENV": self._parse_sys_env,
            "DISCORD_WEBHOOK": self._parse_discord_webhook,
            "WS_CONNECT": self._parse_ws_connect,
            "WS_SEND": self._parse_ws_send,
            "WS_RECV": self._parse_ws_recv,
            "WS_CLOSE": self._parse_ws_close,
            "JSON_PARSE": self._parse_json_parse,
            "JSON_DUMP": self._parse_json_dump,
            "DICT": self._parse_dict,
            "DSET": self._parse_dset,
            "DGET": self._parse_dget,
            "DKEYS": self._parse_dkeys,
            "LGET": self._parse_lget,
            "LSET": self._parse_lset,
            "LLEN": self._parse_llen,
            "LPUSH": self._parse_lpush,
            "LPOP": self._parse_lpop,
            "FILE_WRITE": self._parse_file_write,
            "FILE_READ": self._parse_file_read,
            "FILE_APPEND": self._parse_file_append,
            "FILE_EXISTS": self._parse_file_exists,
            "FILE_DELETE": self._parse_file_delete,
            "DIR_LIST": self._parse_dir_list,
            "BOX_HIT": self._parse_box_hit,
            "VEC_ADD": self._parse_vec_add,
            "VEC_MAG": self._parse_vec_mag,
            "EACH": self._parse_each,
            "IFR": self._parse_ifr,
            "REP": self._parse_rep,
            "LOOP": self._parse_loop,
            "SREP": self._parse_srep,
            "SLOOP": self._parse_sloop,
            "TXT": self._parse_txt,
            "LST": self._parse_lst,
            "MH": self._parse_mh,
            "SLEN": self._parse_slen,
            "SGET": self._parse_sget,
            "SSUB": self._parse_ssub,
            "SSPLIT": self._parse_ssplit,
            "SJOIN": self._parse_sjoin,
            "SFIND": self._parse_sfind,
            "SREPLACE": self._parse_sreplace,
            "STRIM": self._parse_strim,
            "SLOWER": self._parse_slower,
            "SUPPER": self._parse_supper,
            "ORD": self._parse_ord,
            "CHR": self._parse_chr,
            "IS_DIGIT": self._parse_is_digit,
            "IS_ALPHA": self._parse_is_alpha,
            "TYPE_OF": self._parse_type_of,
            "TO_STR": self._parse_to_str,
            "TO_NUM": self._parse_to_num,
            "TO_INT": self._parse_to_num,
            "TO_FLOAT": self._parse_to_float,
            "LCONTAINS": self._parse_lcontains,
            "LINSERT": self._parse_linsert,
            "LSLICE": self._parse_lslice,
            "DHAS": self._parse_dhas,
            "DDEL": self._parse_ddel,
            "WHILE": self._parse_while,
            "SWHILE": self._parse_swhile,
            "BREAK": self._parse_break,
            "CONTINUE": self._parse_continue,
            "CNT": self._parse_continue,
            "TRY": self._parse_try,
            "RETURN": self._parse_return
        }

    def peek(self):
        return self.tokens[self.pos]

    def consume(self, expected_kind):
        tok = self.peek()
        if tok.kind != expected_kind:
            raise TrappyError(f"Expected '{expected_kind}', but got '{tok.val}'", tok.line)
        self.pos += 1
        return tok

    def consume_tit_or_eq(self):
        tok = self.peek()
        if tok.kind in ("TIT", "EQ", "="):
            return self.consume(tok.kind).val
        raise TrappyError(f"Expected 'tit' or 'eq', but got '{tok.val}'", tok.line)

    def parse_condition(self):
        left = self.parse_atom()
        cmp_tokens = ("GRT", "LSS", "SM", "EQ", "==", "!=", ">", "<", ">=", "<=")
        if self.peek().kind in cmp_tokens:
            op_tok = self.consume(self.peek().kind)
            op = op_tok.val.lower() if isinstance(op_tok.val, str) else op_tok.val
            right = self.parse_atom()
            return ("COND", op, left, right)
        elif self.peek().kind in ("NUM", "STR", "NAME", "("):
            right = self.parse_atom()
            if self.peek().kind in cmp_tokens:
                op_tok = self.consume(self.peek().kind)
                op = op_tok.val.lower() if isinstance(op_tok.val, str) else op_tok.val
                return ("COND", op, left, right)
            else:
                raise TrappyError(f"Condition missing comparison operator, got '{self.peek().val}'", self.peek().line)
        else:
            return ("COND", "!=", left, ("NUM", 0))

    def parse_program(self):
        self.consume("TRST")
        stmts = []
        while self.peek().kind not in ("TREN", "EOF"):
            stmts.append(self.parse_statement())
        self.consume("TREN")
        return ("PROGRAM", stmts)

    def parse_statement(self):
        tok = self.peek()
        handler = self._dispatch.get(tok.kind)
        if handler:
            return handler(tok)
        return self._parse_function_or_call(tok)

    def _parse_add_var(self, tok):
        self.consume("ADD_VAR")
        name = self.consume_name_or_str()
        self.known_variables.add(name)
        return ("ADD_VAR", name, tok.line)

    def _parse_add_func(self, tok):
        self.consume("ADD_FUNC")
        name = self.consume_name_or_str()
        self.known_functions.add(name)
        return ("ADD_FUNC", name, tok.line)

    def _parse_add_obj(self, tok):
        self.consume("ADD_OBJ")
        obj_name = self.consume_name_or_str()
        props = {}
        while self.peek().kind not in ("TREN", "EOF"):
            prop_name = self.consume("NAME").val
            self.consume(":")
            val = self.parse_atom()
            props[prop_name] = val
        self.consume("TREN")
        self.known_variables.add(obj_name)
        return ("ADD_OBJ", obj_name, props, tok.line)

    def _parse_add_type(self, tok):
        self.consume("ADD_TYPE")
        type_name = self.consume_name_or_str()
        props = {}
        while self.peek().kind not in ("TREN", "EOF"):
            prop_name = self.consume("NAME").val
            self.consume(":")
            val = self.parse_atom()
            props[prop_name] = val
        self.consume("TREN")
        self.blueprints[type_name] = props
        return ("ADD_TYPE", type_name, props, tok.line)

    def _parse_fdel(self, tok):
        self.consume("FDEL")
        fn_name = self.consume("NAME").val
        arg_name = self.consume("NAME").val
        self.consume("TREN")
        return ("FDEL_DEF", fn_name, arg_name, tok.line)

    def _parse_trg(self, tok):
        self.consume("TRG")
        fn_name = self.consume("NAME").val
        arg = self.parse_atom()
        return ("TRG_ACTION", fn_name, arg, tok.line)

    def _parse_cwin(self, tok):
        self.consume(tok.kind)
        title = self.parse_atom()
        w = self.parse_coord_part()
        self.consume(":")
        h = self.parse_coord_part()
        mode = "main"
        if self.peek().kind == "NAME" and self.peek().val in ("main", "bg"):
            mode = self.consume("NAME").val
        return ("CWIN", title, w, h, mode, tok.line)

    def _parse_sbgwin(self, tok):
        self.consume("SBGWIN")
        title = self.parse_atom()
        color = self.parse_color()
        return ("WIN_STYLE", title, color, tok.line)

    def _parse_label(self, tok):
        self.consume("LABEL")
        text = self.parse_atom()
        x = self.parse_coord_part()
        self.consume(":")
        y = self.parse_coord_part()
        color = self.parse_color()
        return ("LABEL", text, x, y, color, tok.line)

    def _parse_regle(self, tok):
        self.consume("REGLE")
        x = self.parse_coord_part()
        self.consume(":")
        y = self.parse_coord_part()
        w = self.parse_coord_part()
        self.consume(":")
        h = self.parse_coord_part()
        color = self.parse_color()
        return ("REGLE", x, y, w, h, color, tok.line)

    def _parse_circ(self, tok):
        self.consume("CIRC")
        x = self.parse_coord_part()
        self.consume(":")
        y = self.parse_coord_part()
        r = self.parse_coord_part()
        color = self.parse_color()
        return ("CIRC", x, y, r, color, tok.line)

    def _parse_line(self, tok):
        self.consume("LINE")
        x1 = self.parse_coord_part()
        self.consume(":")
        y1 = self.parse_coord_part()
        x2 = self.parse_coord_part()
        self.consume(":")
        y2 = self.parse_coord_part()
        color = self.parse_color()
        return ("LINE", x1, y1, x2, y2, color, tok.line)

    def _parse_cube3d(self, tok):
        self.consume("CUBE3D")
        cx = self.parse_coord_part()
        self.consume(":")
        cy = self.parse_coord_part()
        self.consume(":")
        cz = self.parse_coord_part()
        size = self.parse_coord_part()
        rx = self.parse_coord_part()
        self.consume(":")
        ry = self.parse_coord_part()
        color = self.parse_color()
        return ("CUBE3D", cx, cy, cz, size, rx, ry, color, tok.line)

    def _parse_line3d(self, tok):
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
        color = self.parse_color()
        return ("LINE3D", x1, y1, z1, x2, y2, z2, rx, ry, color, tok.line)

    def _parse_sphere3d(self, tok):
        self.consume("SPHERE3D")
        cx = self.parse_coord_part()
        self.consume(":")
        cy = self.parse_coord_part()
        self.consume(":")
        cz = self.parse_coord_part()
        rad = self.parse_coord_part()
        rx = self.parse_coord_part()
        self.consume(":")
        ry = self.parse_coord_part()
        color = self.parse_color()
        return ("SPHERE3D", cx, cy, cz, rad, rx, ry, color, tok.line)

    def _parse_pyramid3d(self, tok):
        self.consume("PYRAMID3D")
        cx = self.parse_coord_part()
        self.consume(":")
        cy = self.parse_coord_part()
        self.consume(":")
        cz = self.parse_coord_part()
        size = self.parse_coord_part()
        rx = self.parse_coord_part()
        self.consume(":")
        ry = self.parse_coord_part()
        color = self.parse_color()
        return ("PYRAMID3D", cx, cy, cz, size, rx, ry, color, tok.line)

    def _parse_btn(self, tok):
        self.consume("BTN")
        label_text = self.parse_atom()
        x = self.parse_coord_part()
        self.consume(":")
        y = self.parse_coord_part()
        self.consume("TRG")
        fn_name = self.consume("NAME").val
        return ("BUTTON", label_text, x, y, fn_name, tok.line)

    def _parse_inp(self, tok):
        self.consume("INP")
        placeholder = self.parse_atom()
        x = self.parse_coord_part()
        self.consume(":")
        y = self.parse_coord_part()
        self.consume("TIT")
        var_name = self.consume("NAME").val
        return ("INPUT", placeholder, x, y, var_name, tok.line)

    def _parse_gloop(self, tok):
        self.consume("GLOOP")
        body = []
        while self.peek().kind not in ("TREN", "EOF"):
            body.append(self.parse_statement())
        self.consume("TREN")
        return ("GLOOP", body, tok.line)

    def _parse_fps(self, tok):
        self.consume("FPS")
        mode_tok = self.peek()
        if mode_tok.kind == "CALM":
            self.consume("CALM")
            return ("FPS_SET", "calm", 60, tok.line)
        elif mode_tok.kind == "LOCK":
            self.consume("LOCK")
            rate = self.consume("NUM").val
            return ("FPS_SET", "lock", rate, tok.line)
        elif mode_tok.kind == "UNLOCK":
            self.consume("UNLOCK")
            return ("FPS_SET", "unlock", 0, tok.line)
        raise TrappyError("FPS expects 'calm', 'lock <num>', or 'unlock'", tok.line)

    def _parse_play(self, tok):
        self.consume("PLAY")
        sound_name = self.consume("STR").val
        return ("PLAY_AUDIO", sound_name, tok.line)

    def _parse_beep(self, tok):
        self.consume("BEEP")
        freq = self.parse_atom()
        self.consume(":")
        duration = self.parse_atom()
        return ("BEEP_AUDIO", freq, duration, tok.line)

    def _parse_synth(self, tok):
        self.consume("SYNTH")
        wave_type = self.parse_atom()
        self.consume(":")
        freq = self.parse_atom()
        self.consume(":")
        duration = self.parse_atom()
        return ("SYNTH_AUDIO", wave_type, freq, duration, tok.line)

    def _parse_write(self, tok):
        self.consume("WRITE")
        content = self.parse_expr()
        self.consume("INTO")
        filename = self.consume("STR").val
        return ("WRITE_FILE", content, filename, tok.line)

    def _parse_http_get(self, tok):
        self.consume("HTTP_GET")
        url_expr = self.parse_expr()
        self.consume("TIT")
        var_name = self.consume("NAME").val
        return ("HTTP_GET", url_expr, var_name, tok.line)

    def _parse_http_post(self, tok):
        self.consume("HTTP_POST")
        url_expr = self.parse_expr()
        self.consume(":")
        data_expr = self.parse_expr()
        self.consume("TIT")
        var_name = self.consume("NAME").val
        return ("HTTP_POST", url_expr, data_expr, var_name, tok.line)

    def _parse_download(self, tok):
        self.consume("DOWNLOAD")
        url_expr = self.parse_expr()
        self.consume("INTO")
        file_path = self.consume("STR").val
        return ("DOWNLOAD_FILE", url_expr, file_path, tok.line)

    def _parse_cli_connect(self, tok):
        self.consume("CLI_CONNECT")
        host_expr = self.parse_atom()
        self.consume(":")
        port_expr = self.parse_expr()
        self.consume("TIT")
        var_name = self.consume("NAME").val
        return ("CLI_CONNECT", host_expr, port_expr, var_name, tok.line)

    def _parse_cli_send(self, tok):
        self.consume("CLI_SEND")
        client_name = self.consume("NAME").val
        self.consume(":")
        data_expr = self.parse_expr()
        return ("CLI_SEND", client_name, data_expr, tok.line)

    def _parse_cli_recv(self, tok):
        self.consume("CLI_RECV")
        client_name = self.consume("NAME").val
        self.consume("TIT")
        var_name = self.consume("NAME").val
        return ("CLI_RECV", client_name, var_name, tok.line)

    def _parse_cli_close(self, tok):
        self.consume("CLI_CLOSE")
        client_name = self.consume("NAME").val
        return ("CLI_CLOSE", client_name, tok.line)

    def _parse_srv_listen(self, tok):
        self.consume("SRV_LISTEN")
        port_expr = self.parse_expr()
        self.consume("TIT")
        var_name = self.consume("NAME").val
        return ("SRV_LISTEN", port_expr, var_name, tok.line)

    def _parse_srv_accept(self, tok):
        self.consume("SRV_ACCEPT")
        server_name = self.consume("NAME").val
        self.consume("TIT")
        var_name = self.consume("NAME").val
        return ("SRV_ACCEPT", server_name, var_name, tok.line)

    def _parse_mem_alloc(self, tok):
        self.consume("MEM_ALLOC")
        size_expr = self.parse_expr()
        self.consume("TIT")
        var_name = self.consume("NAME").val
        return ("MEM_ALLOC", size_expr, var_name, tok.line)

    def _parse_mem_write(self, tok):
        self.consume("MEM_WRITE")
        buf_name = self.consume("NAME").val
        self.consume(":")
        offset_expr = self.parse_expr()
        self.consume(":")
        byte_expr = self.parse_expr()
        return ("MEM_WRITE", buf_name, offset_expr, byte_expr, tok.line)

    def _parse_mem_read(self, tok):
        self.consume("MEM_READ")
        buf_name = self.consume("NAME").val
        self.consume(":")
        offset_expr = self.parse_expr()
        self.consume("TIT")
        var_name = self.consume("NAME").val
        return ("MEM_READ", buf_name, offset_expr, var_name, tok.line)

    def _parse_sys_exec(self, tok):
        self.consume("SYS_EXEC")
        cmd_expr = self.parse_expr()
        self.consume("TIT")
        var_name = self.consume("NAME").val
        return ("SYS_EXEC", cmd_expr, var_name, tok.line)

    def _parse_sys_env(self, tok):
        self.consume("SYS_ENV")
        key_expr = self.parse_expr()
        self.consume("TIT")
        var_name = self.consume("NAME").val
        return ("SYS_ENV", key_expr, var_name, tok.line)

    def _parse_discord_webhook(self, tok):
        self.consume("DISCORD_WEBHOOK")
        url_expr = self.parse_expr()
        self.consume(":")
        msg_expr = self.parse_expr()
        self.consume("TIT")
        status_var = self.consume("NAME").val
        return ("DISCORD_WEBHOOK", url_expr, msg_expr, status_var, tok.line)

    def _parse_ws_connect(self, tok):
        self.consume("WS_CONNECT")
        url_expr = self.parse_expr()
        self.consume("TIT")
        var_name = self.consume("NAME").val
        return ("WS_CONNECT", url_expr, var_name, tok.line)

    def _parse_ws_send(self, tok):
        self.consume("WS_SEND")
        ws_name = self.consume("NAME").val
        self.consume(":")
        data_expr = self.parse_expr()
        return ("WS_SEND", ws_name, data_expr, tok.line)

    def _parse_ws_recv(self, tok):
        self.consume("WS_RECV")
        ws_name = self.consume("NAME").val
        self.consume("TIT")
        var_name = self.consume("NAME").val
        return ("WS_RECV", ws_name, var_name, tok.line)

    def _parse_ws_close(self, tok):
        self.consume("WS_CLOSE")
        ws_name = self.consume("NAME").val
        return ("WS_CLOSE", ws_name, tok.line)

    def _parse_json_parse(self, tok):
        self.consume("JSON_PARSE")
        json_str_expr = self.parse_expr()
        self.consume("TIT")
        dest_var = self.consume("NAME").val
        return ("JSON_PARSE", json_str_expr, dest_var, tok.line)

    def _parse_json_dump(self, tok):
        self.consume("JSON_DUMP")
        obj_expr = self.parse_expr()
        self.consume("TIT")
        dest_var = self.consume("NAME").val
        return ("JSON_DUMP", obj_expr, dest_var, tok.line)

    def _parse_dict(self, tok):
        self.consume("DICT")
        self.consume("TIT")
        dict_name = self.consume("NAME").val
        return ("DICT_NEW", dict_name, tok.line)

    def _parse_dset(self, tok):
        self.consume("DSET")
        dict_name = self.consume("NAME").val
        self.consume(":")
        key_expr = self.parse_expr()
        self.consume(":")
        val_expr = self.parse_expr()
        return ("DSET", dict_name, key_expr, val_expr, tok.line)

    def _parse_dget(self, tok):
        self.consume("DGET")
        dict_name = self.consume("NAME").val
        self.consume(":")
        key_expr = self.parse_expr()
        self.consume("TIT")
        dest_var = self.consume("NAME").val
        return ("DGET", dict_name, key_expr, dest_var, tok.line)

    def _parse_dkeys(self, tok):
        self.consume("DKEYS")
        dict_name = self.consume("NAME").val
        self.consume("TIT")
        dest_var = self.consume("NAME").val
        return ("DKEYS", dict_name, dest_var, tok.line)

    def _parse_lget(self, tok):
        self.consume("LGET")
        list_name = self.consume("NAME").val
        self.consume(":")
        idx_expr = self.parse_expr()
        self.consume("TIT")
        dest_var = self.consume("NAME").val
        return ("LGET", list_name, idx_expr, dest_var, tok.line)

    def _parse_lset(self, tok):
        self.consume("LSET")
        list_name = self.consume("NAME").val
        self.consume(":")
        idx_expr = self.parse_expr()
        self.consume(":")
        val_expr = self.parse_expr()
        return ("LSET", list_name, idx_expr, val_expr, tok.line)

    def _parse_llen(self, tok):
        self.consume("LLEN")
        list_name = self.consume("NAME").val
        self.consume("TIT")
        dest_var = self.consume("NAME").val
        return ("LLEN", list_name, dest_var, tok.line)

    def _parse_lpush(self, tok):
        self.consume("LPUSH")
        list_name = self.consume("NAME").val
        self.consume(":")
        val_expr = self.parse_expr()
        return ("LPUSH", list_name, val_expr, tok.line)

    def _parse_lpop(self, tok):
        self.consume("LPOP")
        list_name = self.consume("NAME").val
        self.consume("TIT")
        dest_var = self.consume("NAME").val
        return ("LPOP", list_name, dest_var, tok.line)

    def _parse_file_write(self, tok):
        self.consume("FILE_WRITE")
        file_expr = self.parse_expr()
        self.consume(":")
        content_expr = self.parse_expr()
        return ("FILE_WRITE", file_expr, content_expr, tok.line)

    def _parse_file_read(self, tok):
        self.consume("FILE_READ")
        file_expr = self.parse_expr()
        self.consume("TIT")
        dest_var = self.consume("NAME").val
        return ("FILE_READ", file_expr, dest_var, tok.line)

    def _parse_file_append(self, tok):
        self.consume("FILE_APPEND")
        file_expr = self.parse_expr()
        self.consume(":")
        content_expr = self.parse_expr()
        return ("FILE_APPEND", file_expr, content_expr, tok.line)

    def _parse_file_exists(self, tok):
        self.consume("FILE_EXISTS")
        file_expr = self.parse_expr()
        self.consume("TIT")
        dest_var = self.consume("NAME").val
        return ("FILE_EXISTS", file_expr, dest_var, tok.line)

    def _parse_file_delete(self, tok):
        self.consume("FILE_DELETE")
        file_expr = self.parse_expr()
        return ("FILE_DELETE", file_expr, tok.line)

    def _parse_dir_list(self, tok):
        self.consume("DIR_LIST")
        path_expr = self.parse_expr()
        self.consume("TIT")
        dest_var = self.consume("NAME").val
        return ("DIR_LIST", path_expr, dest_var, tok.line)

    def _parse_box_hit(self, tok):
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
        dest_var = self.consume("NAME").val
        return ("BOX_HIT", x1, y1, w1, h1, x2, y2, w2, h2, dest_var, tok.line)

    def _parse_vec_add(self, tok):
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

    def _parse_vec_mag(self, tok):
        self.consume("VEC_MAG")
        x = self.parse_coord_part()
        self.consume(":")
        y = self.parse_coord_part()
        self.consume("TIT")
        dest_var = self.consume("NAME").val
        return ("VEC_MAG", x, y, dest_var, tok.line)

    def _parse_each(self, tok):
        self.consume("EACH")
        item_var = self.consume("NAME").val
        self.consume("IN")
        list_var = self.consume("NAME").val
        body = []
        while self.peek().kind not in ("TREN", "EOF"):
            body.append(self.parse_statement())
        self.consume("TREN")
        return ("EACH_LOOP", item_var, list_var, body, tok.line)

    def _parse_ifr(self, tok):
        self.consume("IFR")

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

        condition = self.parse_condition()

        if self.peek().kind == "THEN":
            self.consume("THEN")

        then_body = []
        else_body = []
        has_else = False

        while self.peek().kind not in ("ELSE", "TREN", "EOF"):
            if self.peek().kind == "THEN":
                self.consume("THEN")
                has_else = True
                while self.peek().kind not in ("TREN", "EOF"):
                    else_body.append(self.parse_statement())
                break
            then_body.append(self.parse_statement())

        if self.peek().kind == "ELSE":
            self.consume("ELSE")
            has_else = True
            while self.peek().kind not in ("TREN", "EOF"):
                else_body.append(self.parse_statement())

        self.consume("TREN")
        return ("IF_STMT", condition, then_body, else_body if has_else else None, tok.line)

    def _parse_rep(self, tok):
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

    def _parse_loop(self, tok):
        self.consume("LOOP")
        body = []
        while self.peek().kind not in ("TREN", "EOF"):
            body.append(self.parse_statement())
        self.consume("TREN")
        return ("INFINITE_LOOP", body, tok.line)

    def _parse_srep(self, tok):
        self.consume("SREP")
        return ("BREAK_REP", tok.line)

    def _parse_sloop(self, tok):
        self.consume("SLOOP")
        return ("BREAK_LOOP", tok.line)

    def _parse_txt(self, tok):
        self.consume("TXT")
        expr = self.parse_expr()
        self.consume("TIT")
        var_name = self.consume("NAME").val
        return ("ASSIGN_TARGET", ("VAR_TARGET", var_name), expr, tok.line)

    def _parse_lst(self, tok):
        self.consume("LST")
        items = [self.parse_atom()]
        while self.peek().kind == "|":
            self.consume("|")
            items.append(self.parse_atom())
        self.consume_tit_or_eq()
        var_name = self.consume("NAME").val
        return ("ASSIGN_LIST", var_name, items, tok.line)

    def _parse_mh(self, tok):
        self.consume("MH")
        expr = self.parse_expr()
        self.consume("EQ")
        target = self.parse_target_lvalue()
        return ("ASSIGN_TARGET", target, expr, tok.line)

    def _parse_slen(self, tok):
        self.consume("SLEN")
        str_expr = self.parse_expr()
        self.consume_tit_or_eq()
        dest = self.parse_target_lvalue()
        return ("SLEN", str_expr, dest, tok.line)

    def _parse_sget(self, tok):
        self.consume("SGET")
        str_expr = self.parse_expr()
        self.consume(":")
        idx_expr = self.parse_expr()
        self.consume_tit_or_eq()
        dest = self.parse_target_lvalue()
        return ("SGET", str_expr, idx_expr, dest, tok.line)

    def _parse_ssub(self, tok):
        self.consume("SSUB")
        str_expr = self.parse_expr()
        self.consume(":")
        start_expr = self.parse_expr()
        self.consume(":")
        end_expr = self.parse_expr()
        self.consume_tit_or_eq()
        dest = self.parse_target_lvalue()
        return ("SSUB", str_expr, start_expr, end_expr, dest, tok.line)

    def _parse_ssplit(self, tok):
        self.consume("SSPLIT")
        str_expr = self.parse_expr()
        self.consume(":")
        delim_expr = self.parse_expr()
        self.consume_tit_or_eq()
        dest = self.parse_target_lvalue()
        return ("SSPLIT", str_expr, delim_expr, dest, tok.line)

    def _parse_sjoin(self, tok):
        self.consume("SJOIN")
        list_expr = self.parse_expr()
        self.consume(":")
        delim_expr = self.parse_expr()
        self.consume_tit_or_eq()
        dest = self.parse_target_lvalue()
        return ("SJOIN", list_expr, delim_expr, dest, tok.line)

    def _parse_sfind(self, tok):
        self.consume("SFIND")
        str_expr = self.parse_expr()
        self.consume(":")
        needle_expr = self.parse_expr()
        self.consume_tit_or_eq()
        dest = self.parse_target_lvalue()
        return ("SFIND", str_expr, needle_expr, dest, tok.line)

    def _parse_sreplace(self, tok):
        self.consume("SREPLACE")
        str_expr = self.parse_expr()
        self.consume(":")
        old_expr = self.parse_expr()
        self.consume(":")
        new_expr = self.parse_expr()
        self.consume_tit_or_eq()
        dest = self.parse_target_lvalue()
        return ("SREPLACE", str_expr, old_expr, new_expr, dest, tok.line)

    def _parse_strim(self, tok):
        self.consume("STRIM")
        str_expr = self.parse_expr()
        self.consume_tit_or_eq()
        dest = self.parse_target_lvalue()
        return ("STRIM", str_expr, dest, tok.line)

    def _parse_slower(self, tok):
        self.consume("SLOWER")
        str_expr = self.parse_expr()
        self.consume_tit_or_eq()
        dest = self.parse_target_lvalue()
        return ("SLOWER", str_expr, dest, tok.line)

    def _parse_supper(self, tok):
        self.consume("SUPPER")
        str_expr = self.parse_expr()
        self.consume_tit_or_eq()
        dest = self.parse_target_lvalue()
        return ("SUPPER", str_expr, dest, tok.line)

    def _parse_ord(self, tok):
        self.consume("ORD")
        char_expr = self.parse_expr()
        self.consume_tit_or_eq()
        dest = self.parse_target_lvalue()
        return ("ORD", char_expr, dest, tok.line)

    def _parse_chr(self, tok):
        self.consume("CHR")
        code_expr = self.parse_expr()
        self.consume_tit_or_eq()
        dest = self.parse_target_lvalue()
        return ("CHR", code_expr, dest, tok.line)

    def _parse_is_digit(self, tok):
        self.consume("IS_DIGIT")
        str_expr = self.parse_expr()
        self.consume_tit_or_eq()
        dest = self.parse_target_lvalue()
        return ("IS_DIGIT", str_expr, dest, tok.line)

    def _parse_is_alpha(self, tok):
        self.consume("IS_ALPHA")
        str_expr = self.parse_expr()
        self.consume_tit_or_eq()
        dest = self.parse_target_lvalue()
        return ("IS_ALPHA", str_expr, dest, tok.line)

    def _parse_type_of(self, tok):
        self.consume("TYPE_OF")
        expr = self.parse_expr()
        self.consume_tit_or_eq()
        dest = self.parse_target_lvalue()
        return ("TYPE_OF", expr, dest, tok.line)

    def _parse_to_str(self, tok):
        self.consume("TO_STR")
        expr = self.parse_expr()
        self.consume_tit_or_eq()
        dest = self.parse_target_lvalue()
        return ("TO_STR", expr, dest, tok.line)

    def _parse_to_num(self, tok):
        self.consume(tok.kind)
        expr = self.parse_expr()
        self.consume_tit_or_eq()
        dest = self.parse_target_lvalue()
        return ("TO_NUM", expr, dest, tok.line)

    def _parse_to_float(self, tok):
        self.consume("TO_FLOAT")
        expr = self.parse_expr()
        self.consume_tit_or_eq()
        dest = self.parse_target_lvalue()
        return ("TO_FLOAT", expr, dest, tok.line)

    def _parse_lcontains(self, tok):
        self.consume("LCONTAINS")
        list_expr = self.parse_expr()
        self.consume(":")
        item_expr = self.parse_expr()
        self.consume_tit_or_eq()
        dest = self.parse_target_lvalue()
        return ("LCONTAINS", list_expr, item_expr, dest, tok.line)

    def _parse_linsert(self, tok):
        self.consume("LINSERT")
        list_name = self.consume("NAME").val
        self.consume(":")
        idx_expr = self.parse_expr()
        self.consume(":")
        val_expr = self.parse_expr()
        return ("LINSERT", list_name, idx_expr, val_expr, tok.line)

    def _parse_lslice(self, tok):
        self.consume("LSLICE")
        list_name = self.consume("NAME").val
        self.consume(":")
        start_expr = self.parse_expr()
        self.consume(":")
        end_expr = self.parse_expr()
        self.consume_tit_or_eq()
        dest = self.parse_target_lvalue()
        return ("LSLICE", list_name, start_expr, end_expr, dest, tok.line)

    def _parse_dhas(self, tok):
        self.consume("DHAS")
        dict_name = self.consume("NAME").val
        self.consume(":")
        key_expr = self.parse_expr()
        self.consume_tit_or_eq()
        dest = self.parse_target_lvalue()
        return ("DHAS", dict_name, key_expr, dest, tok.line)

    def _parse_ddel(self, tok):
        self.consume("DDEL")
        dict_name = self.consume("NAME").val
        self.consume(":")
        key_expr = self.parse_expr()
        return ("DDEL", dict_name, key_expr, tok.line)

    def _parse_while(self, tok):
        self.consume("WHILE")
        cond = self.parse_condition()
        body = []
        while self.peek().kind not in ("TREN", "EOF"):
            body.append(self.parse_statement())
        self.consume("TREN")
        return ("WHILE_LOOP", cond, body, tok.line)

    def _parse_swhile(self, tok):
        self.consume("SWHILE")
        return ("BREAK_WHILE", tok.line)

    def _parse_break(self, tok):
        self.consume("BREAK")
        return ("BREAK_ALL", tok.line)

    def _parse_continue(self, tok):
        self.consume(tok.kind)
        return ("CONTINUE_LOOP", tok.line)

    def _parse_try(self, tok):
        self.consume("TRY")
        try_body = []
        while self.peek().kind not in ("CATCH", "TREN", "EOF"):
            try_body.append(self.parse_statement())
        err_var = None
        catch_body = []
        if self.peek().kind == "CATCH":
            self.consume("CATCH")
            if self.peek().kind == "NAME":
                err_var = self.consume("NAME").val
            while self.peek().kind not in ("TREN", "EOF"):
                catch_body.append(self.parse_statement())
        self.consume("TREN")
        return ("TRY_CATCH", try_body, err_var, catch_body, tok.line)

    def _parse_return(self, tok):
        self.consume("RETURN")
        expr = self.parse_expr()
        return ("RETURN", expr, tok.line)

    def _parse_function_or_call(self, tok):
        fn_prefixes = ("FMH", "FTXT", "F3D", "FOS", "FCLI", "FUI", "FLIST", "FREP", "FLOOP", "FGUI", "FDRW", "FGFX", "FCAN", "FWEB", "FAPP", "FN", "FUNC")
        if tok.kind in fn_prefixes:
            self.consume(tok.kind)
            fn_name = self.consume("NAME").val
            self.known_functions.add(fn_name)

            params = []
            if self.peek().kind == "NAME":
                first_param = self.consume("NAME").val
                params.append(first_param)
                while self.peek().kind == ":":
                    self.consume(":")
                    p_name = self.consume("NAME").val
                    params.append(p_name)

            body = []
            while self.peek().kind not in ("TREN", "EOF"):
                body.append(self.parse_statement())
            self.consume("TREN")
            return ("FN_DEF", fn_name, params, body, tok.line)

        if tok.kind in ("ANSW", "RETURN"):
            self.consume(tok.kind)
            expr = self.parse_expr()
            return ("RETURN", expr, tok.line)

        if tok.kind in ("OUT", "GAN"):
            self.consume(tok.kind)
            expr = self.parse_expr()
            return ("OUT", expr, tok.line)

        if tok.kind == "PACK_DATA":
            self.consume("PACK_DATA")
            obj_name = self.consume("NAME").val
            self.consume("TIT")
            var_name = self.consume("NAME").val
            return ("PACK_DATA", obj_name, var_name, tok.line)

        if tok.kind == "UNPACK_DATA":
            self.consume("UNPACK_DATA")
            packet_expr = self.parse_expr()
            self.consume("TIT")
            obj_name = self.consume("NAME").val
            return ("UNPACK_DATA", packet_expr, obj_name, tok.line)

        if tok.kind == "SPAWN":
            self.consume("SPAWN")
            type_name = self.consume("NAME").val
            self.consume("AS")
            obj_name = self.consume("NAME").val
            return ("ADD_OBJ", obj_name, type_name, tok.line)

        if tok.kind == "NAME":
            name = self.consume("NAME").val
            if name in self.known_functions:
                args = []
                if self.peek().kind in ("NUM", "STR", "NAME", "("):
                    args.append(self.parse_atom())
                    while self.peek().kind == ":":
                        self.consume(":")
                        args.append(self.parse_atom())
                if self.peek().kind in ("TIT", "EQ", "="):
                    self.consume(self.peek().kind)
                    dest = self.parse_target_lvalue()
                    return ("ASSIGN_TARGET", dest, ("CALL", name, args, tok.line), tok.line)
                return ("CALL", name, args, tok.line)

            if self.peek().kind == ".":
                self.consume(".")
                prop = self.consume("NAME").val
                self.consume("EQ")
                expr = self.parse_expr()
                return ("ASSIGN_TARGET", ("DOT_TARGET", name, prop), expr, tok.line)

            if self.peek().kind == "EQ":
                self.consume("EQ")
                expr = self.parse_expr()
                return ("ASSIGN_TARGET", ("VAR_TARGET", name), expr, tok.line)

            if self.peek().kind in ("NUM", "STR", "NAME", "("):
                args = [self.parse_atom()]
                while self.peek().kind == ":":
                    self.consume(":")
                    args.append(self.parse_atom())
                if self.peek().kind in ("TIT", "EQ", "="):
                    self.consume(self.peek().kind)
                    dest = self.parse_target_lvalue()
                    return ("ASSIGN_TARGET", dest, ("CALL", name, args, tok.line), tok.line)
                return ("CALL", name, args, tok.line)

        raise TrappyError(f"Unexpected command '{tok.val}'", tok.line)

    def consume_name_or_str(self):
        tok = self.peek()
        if tok.kind == "NAME":
            return self.consume("NAME").val
        elif tok.kind == "STR":
            return self.consume("STR").val
        raise TrappyError(f"Expected name or string, got '{tok.val}'", tok.line)

    def parse_color(self):
        tok = self.peek()
        if tok.kind == "NAME":
            return self.consume("NAME").val
        elif tok.kind == "STR":
            return self.consume("STR").val
        return "white"

    def parse_target_lvalue(self):
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
            if self.peek().kind == "(":
                self.consume("(")
                args = []
                if self.peek().kind != ")":
                    args.append(self.parse_expr())
                    while self.peek().kind == ":":
                        self.consume(":")
                        args.append(self.parse_expr())
                self.consume(")")
                return ("CALL", name, args, tok.line)
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
        while self.peek().kind in ("MULTI", "DIV", "*", "/", "%"):
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
            if self.peek().kind == ".":
                self.consume(".")
                prop = self.consume("NAME").val
                return ("DOT", name, prop, tok.line)

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
        if tok.kind == "NUM":
            self.consume("NUM")
            return ("NUM", tok.val)
        if tok.kind == "-":
            self.consume("-")
            sub = self.parse_atom()
            if sub[0] == "NUM":
                return ("NUM", -sub[1])
            return ("BINOP", "-", ("NUM", 0), sub)
        if tok.kind == "STR":
            self.consume("STR")
            return ("STR", tok.val)
        if tok.kind == "NAME":
            name = self.consume("NAME").val
            if self.peek().kind == ".":
                self.consume(".")
                prop = self.consume("NAME").val
                return ("DOT", name, prop, tok.line)
            if self.peek().kind == "(":
                self.consume("(")
                args = []
                if self.peek().kind != ")":
                    args.append(self.parse_expr())
                    while self.peek().kind == ":":
                        self.consume(":")
                        args.append(self.parse_expr())
                self.consume(")")
                return ("CALL", name, args, tok.line)
            return ("VAR", name, tok.line)
        if tok.kind == "(":
            self.consume("(")
            node = self.parse_expr()
            self.consume(")")
            return node
        raise TrappyError(f"Expected argument, got '{tok.val}'", tok.line)

class Environment:
    def __init__(self, parent=None):
        self.vars = {}
        self.declared_vars = set()
        self.parent = parent

    def declare(self, name):
        self.declared_vars.add(name)
        if name not in self.vars:
            self.vars[name] = 0

    def has(self, name):
        if name in self.vars:
            return True
        if self.parent:
            return self.parent.has(name)
        return False

    def get(self, name, line=None):
        if name in self.vars:
            return self.vars[name]
        if self.parent:
            return self.parent.get(name, line)
        raise TrappyError(f"'{name}' was wiped out or never created!", line)

    def set(self, name, val):
        curr = self
        while curr is not None:
            if name in curr.vars:
                curr.vars[name] = val
                return
            curr = curr.parent
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
    def __init__(self, safe_mode=False):
        self.safe_mode = safe_mode or (os.environ.get("TRAPPY_SAFE_MODE") == "1")
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
        self.MAX_CALL_DEPTH = 100

        self._eval_dispatch = {
            "PROGRAM": self._eval_program,
            "OUT": self._eval_out,
            "ASSIGN_TARGET": self._eval_assign_target,
            "ASSIGN_LIST": self._eval_assign_list,
            "FN_DEF": self._eval_fn_def,
            "FDEL_DEF": self._eval_fdel_def,
            "TRG_ACTION": self._eval_trg_action,
            "CALL": self._eval_call,
            "RETURN": self._eval_return,
            "ADD_VAR": self._eval_add_var,
            "ADD_FUNC": self._eval_add_func,
            "ADD_OBJ": self._eval_add_obj,
            "ADD_TYPE": self._eval_add_type,
            "CWIN": self._eval_cwin,
            "SWIN": self._eval_cwin,
            "WIN_STYLE": self._eval_win_style,
            "LABEL": self._eval_label,
            "REGLE": self._eval_regle,
            "CIRC": self._eval_circ,
            "LINE": self._eval_line,
            "CUBE3D": self._eval_cube3d,
            "LINE3D": self._eval_line3d,
            "SPHERE3D": self._eval_sphere3d,
            "PYRAMID3D": self._eval_pyramid3d,
            "BUTTON": self._eval_button,
            "INPUT": self._eval_input,
            "GLOOP": self._eval_gloop,
            "FPS_SET": self._eval_fps_set,
            "PLAY_AUDIO": self._eval_play_audio,
            "BEEP_AUDIO": self._eval_beep_audio,
            "SYNTH_AUDIO": self._eval_synth_audio,
            "WRITE_FILE": self._eval_write_file,
            "HTTP_GET": self._eval_http_get,
            "HTTP_POST": self._eval_http_post,
            "DOWNLOAD_FILE": self._eval_download_file,
            "CLI_CONNECT": self._eval_cli_connect,
            "CLI_SEND": self._eval_cli_send,
            "CLI_RECV": self._eval_cli_recv,
            "CLI_CLOSE": self._eval_cli_close,
            "SRV_LISTEN": self._eval_srv_listen,
            "SRV_ACCEPT": self._eval_srv_accept,
            "MEM_ALLOC": self._eval_mem_alloc,
            "MEM_WRITE": self._eval_mem_write,
            "MEM_READ": self._eval_mem_read,
            "SYS_EXEC": self._eval_sys_exec,
            "SYS_ENV": self._eval_sys_env,
            "DISCORD_WEBHOOK": self._eval_discord_webhook,
            "WS_CONNECT": self._eval_ws_connect,
            "WS_SEND": self._eval_ws_send,
            "WS_RECV": self._eval_ws_recv,
            "WS_CLOSE": self._eval_ws_close,
            "JSON_PARSE": self._eval_json_parse,
            "JSON_DUMP": self._eval_json_dump,
            "DICT_NEW": self._eval_dict_new,
            "DSET": self._eval_dset,
            "DGET": self._eval_dget,
            "DKEYS": self._eval_dkeys,
            "LGET": self._eval_lget,
            "LSET": self._eval_lset,
            "LLEN": self._eval_llen,
            "LPUSH": self._eval_lpush,
            "LPOP": self._eval_lpop,
            "FILE_WRITE": self._eval_file_write,
            "FILE_READ": self._eval_file_read,
            "FILE_APPEND": self._eval_file_append,
            "FILE_EXISTS": self._eval_file_exists,
            "FILE_DELETE": self._eval_file_delete,
            "DIR_LIST": self._eval_dir_list,
            "BOX_HIT": self._eval_box_hit,
            "VEC_ADD": self._eval_vec_add,
            "VEC_MAG": self._eval_vec_mag,
            "EACH_LOOP": self._eval_each_loop,
            "IF_STMT": self._eval_if_stmt,
            "KEY_CHECK": self._eval_key_check,
            "REP_LOOP": self._eval_rep_loop,
            "INFINITE_LOOP": self._eval_infinite_loop,
            "BREAK_REP": self._eval_break_rep,
            "BREAK_LOOP": self._eval_break_loop,
            "PACK_DATA": self._eval_pack_data,
            "UNPACK_DATA": self._eval_unpack_data,
            "WHILE_LOOP": self._eval_while_loop,
            "BREAK_WHILE": self._eval_break_while,
            "BREAK_ALL": self._eval_break_all,
            "CONTINUE_LOOP": self._eval_continue,
            "TRY_CATCH": self._eval_try_catch,
            "SLEN": self._eval_slen,
            "SGET": self._eval_sget,
            "SSUB": self._eval_ssub,
            "SSPLIT": self._eval_ssplit,
            "SJOIN": self._eval_sjoin,
            "SFIND": self._eval_sfind,
            "SREPLACE": self._eval_sreplace,
            "STRIM": self._eval_strim,
            "SLOWER": self._eval_slower,
            "SUPPER": self._eval_supper,
            "ORD": self._eval_ord,
            "CHR": self._eval_chr,
            "IS_DIGIT": self._eval_is_digit,
            "IS_ALPHA": self._eval_is_alpha,
            "TYPE_OF": self._eval_type_of,
            "TO_STR": self._eval_to_str,
            "TO_NUM": self._eval_to_num,
            "TO_FLOAT": self._eval_to_float,
            "LCONTAINS": self._eval_lcontains,
            "LINSERT": self._eval_linsert,
            "LSLICE": self._eval_lslice,
            "DHAS": self._eval_dhas,
            "DDEL": self._eval_ddel
        }

    def run(self, ast):
        if ast[0] == "PROGRAM":
            for stmt in ast[1]:
                self.eval_stmt(stmt, self.global_env)

            if self.gui and self.gui.root:
                if self.game_loop_body:
                    self._schedule_game_frame()
                self.gui.root.mainloop()

    def _schedule_game_frame(self):
        if not (self.gui and self.gui.root and self.gui.canvas):
            return

        self.gui.canvas.delete("all")
        if self.game_loop_body:
            for stmt in self.game_loop_body:
                self.eval_stmt(stmt, self.global_env)

        if self.fps_mode == "calm":
            delay = 16 if self.gui.is_focused else 66
        elif self.fps_mode == "lock" and self.target_fps > 0:
            delay = int(1000 / self.target_fps)
        else:
            delay = 1

        self.gui.root.after(delay, self._schedule_game_frame)

    def _set_target(self, target, val, env, line=0):
        if isinstance(target, str):
            env.set(target, val)
        elif target[0] == "VAR_TARGET":
            env.set(target[1], val)
        elif target[0] == "DOT_TARGET":
            _, obj_name, prop_name = target
            env.set_dot(obj_name, prop_name, val, line)

    def _eval_cond_bool(self, condition, env):
        _, op, left_expr, right_expr = condition
        left = self.eval_expr(left_expr, env)
        right = self.eval_expr(right_expr, env)
        if left is None and isinstance(right, (int, float)):
            left = 0
        if right is None and isinstance(left, (int, float)):
            right = 0

        op_clean = op.lower() if isinstance(op, str) else op

        if op_clean in ("grt", ">"):
            return (left > right)
        elif op_clean in ("lss", "<"):
            return (left < right)
        elif op_clean in ("sm", "eq", "=="):
            return (left == right)
        elif op_clean in ("!=", "ne"):
            return (left != right)
        elif op_clean in (">=", "gte"):
            return (left >= right)
        elif op_clean in ("<=", "lte"):
            return (left <= right)
        return False

    def _eval_slen(self, stmt, env):
        _, str_expr, dest, line = stmt
        s = str(self.eval_expr(str_expr, env))
        self._set_target(dest, len(s), env, line)

    def _eval_sget(self, stmt, env):
        _, str_expr, idx_expr, dest, line = stmt
        s = str(self.eval_expr(str_expr, env))
        idx = int(self.eval_expr(idx_expr, env))
        val = s[idx] if 0 <= idx < len(s) else ""
        self._set_target(dest, val, env, line)

    def _eval_ssub(self, stmt, env):
        _, str_expr, start_expr, end_expr, dest, line = stmt
        s = str(self.eval_expr(str_expr, env))
        st = int(self.eval_expr(start_expr, env))
        en = int(self.eval_expr(end_expr, env))
        self._set_target(dest, s[st:en], env, line)

    def _eval_ssplit(self, stmt, env):
        _, str_expr, delim_expr, dest, line = stmt
        s = str(self.eval_expr(str_expr, env))
        delim = str(self.eval_expr(delim_expr, env))
        res = list(s) if delim == "" else s.split(delim)
        self._set_target(dest, res, env, line)

    def _eval_sjoin(self, stmt, env):
        _, list_expr, delim_expr, dest, line = stmt
        lst = self.eval_expr(list_expr, env)
        delim = str(self.eval_expr(delim_expr, env))
        if isinstance(lst, list):
            res = delim.join(str(x) for x in lst)
        else:
            res = str(lst)
        self._set_target(dest, res, env, line)

    def _eval_sfind(self, stmt, env):
        _, str_expr, needle_expr, dest, line = stmt
        s = str(self.eval_expr(str_expr, env))
        needle = str(self.eval_expr(needle_expr, env))
        self._set_target(dest, s.find(needle), env, line)

    def _eval_sreplace(self, stmt, env):
        _, str_expr, old_expr, new_expr, dest, line = stmt
        s = str(self.eval_expr(str_expr, env))
        old = str(self.eval_expr(old_expr, env))
        new = str(self.eval_expr(new_expr, env))
        self._set_target(dest, s.replace(old, new), env, line)

    def _eval_strim(self, stmt, env):
        _, str_expr, dest, line = stmt
        s = str(self.eval_expr(str_expr, env)).strip()
        self._set_target(dest, s, env, line)

    def _eval_slower(self, stmt, env):
        _, str_expr, dest, line = stmt
        s = str(self.eval_expr(str_expr, env)).lower()
        self._set_target(dest, s, env, line)

    def _eval_supper(self, stmt, env):
        _, str_expr, dest, line = stmt
        s = str(self.eval_expr(str_expr, env)).upper()
        self._set_target(dest, s, env, line)

    def _eval_ord(self, stmt, env):
        _, char_expr, dest, line = stmt
        s = str(self.eval_expr(char_expr, env))
        code = ord(s[0]) if len(s) > 0 else 0
        self._set_target(dest, code, env, line)

    def _eval_chr(self, stmt, env):
        _, code_expr, dest, line = stmt
        c = int(self.eval_expr(code_expr, env))
        val = chr(c) if 0 <= c <= 0x10ffff else ""
        self._set_target(dest, val, env, line)

    def _eval_is_digit(self, stmt, env):
        _, str_expr, dest, line = stmt
        s = str(self.eval_expr(str_expr, env))
        self._set_target(dest, 1 if (len(s) > 0 and s.isdigit()) else 0, env, line)

    def _eval_is_alpha(self, stmt, env):
        _, str_expr, dest, line = stmt
        s = str(self.eval_expr(str_expr, env))
        self._set_target(dest, 1 if (len(s) > 0 and all(ch.isalpha() or ch == "_" for ch in s)) else 0, env, line)

    def _eval_type_of(self, stmt, env):
        _, expr, dest, line = stmt
        val = self.eval_expr(expr, env)
        if isinstance(val, bool):
            t = "bool"
        elif isinstance(val, (int, float)):
            t = "number"
        elif isinstance(val, str):
            t = "string"
        elif isinstance(val, list):
            t = "list"
        elif isinstance(val, dict):
            t = "dict"
        elif val is None:
            t = "nil"
        else:
            t = "unknown"
        self._set_target(dest, t, env, line)

    def _eval_to_str(self, stmt, env):
        _, expr, dest, line = stmt
        val = str(self.eval_expr(expr, env))
        self._set_target(dest, val, env, line)

    def _eval_to_num(self, stmt, env):
        _, expr, dest, line = stmt
        val = self.eval_expr(expr, env)
        try:
            res = int(float(val)) if isinstance(val, (str, float)) else int(val)
        except (ValueError, TypeError):
            res = 0
        self._set_target(dest, res, env, line)

    def _eval_to_float(self, stmt, env):
        _, expr, dest, line = stmt
        val = self.eval_expr(expr, env)
        try:
            res = float(val)
        except (ValueError, TypeError):
            res = 0.0
        self._set_target(dest, res, env, line)

    def _eval_lcontains(self, stmt, env):
        _, list_expr, item_expr, dest, line = stmt
        lst = self.eval_expr(list_expr, env)
        it = self.eval_expr(item_expr, env)
        if isinstance(lst, list):
            res = 1 if it in lst else 0
        elif isinstance(lst, str):
            res = 1 if str(it) in lst else 0
        else:
            res = 0
        self._set_target(dest, res, env, line)

    def _eval_linsert(self, stmt, env):
        _, list_name, idx_expr, val_expr, line = stmt
        lst = env.get(list_name, line)
        if isinstance(lst, list):
            idx = int(self.eval_expr(idx_expr, env))
            val = self.eval_expr(val_expr, env)
            lst.insert(idx, val)
        else:
            raise TrappyError(f"'{list_name}' is not a list!", line)

    def _eval_lslice(self, stmt, env):
        _, list_name, start_expr, end_expr, dest, line = stmt
        lst = env.get(list_name, line)
        if isinstance(lst, list):
            st = int(self.eval_expr(start_expr, env))
            en = int(self.eval_expr(end_expr, env))
            self._set_target(dest, lst[st:en], env, line)
        else:
            raise TrappyError(f"'{list_name}' is not a list!", line)

    def _eval_dhas(self, stmt, env):
        _, dict_name, key_expr, dest, line = stmt
        d = env.get(dict_name, line)
        if isinstance(d, dict):
            k = str(self.eval_expr(key_expr, env))
            self._set_target(dest, 1 if k in d else 0, env, line)
        else:
            raise TrappyError(f"'{dict_name}' is not a dictionary!", line)

    def _eval_ddel(self, stmt, env):
        _, dict_name, key_expr, line = stmt
        d = env.get(dict_name, line)
        if isinstance(d, dict):
            k = str(self.eval_expr(key_expr, env))
            if k in d:
                del d[k]
        else:
            raise TrappyError(f"'{dict_name}' is not a dictionary!", line)

    def _eval_while_loop(self, stmt, env):
        _, condition, body, _ = stmt
        while self._eval_cond_bool(condition, env):
            try:
                for s in body:
                    self.eval_stmt(s, env)
            except BreakSignal as b:
                if b.loop_type in ("while", "swhile", "all"):
                    break
                raise b
            except ContinueSignal:
                continue

    def _eval_break_while(self, stmt, env):
        raise BreakSignal("while")

    def _eval_break_all(self, stmt, env):
        raise BreakSignal("all")

    def _eval_continue(self, stmt, env):
        raise ContinueSignal()

    def _eval_try_catch(self, stmt, env):
        _, try_body, err_var, catch_body, line = stmt
        try:
            for s in try_body:
                self.eval_stmt(s, env)
        except (ReturnSignal, BreakSignal, ContinueSignal):
            raise
        except Exception as e:
            if err_var:
                env.set(err_var, str(e))
            for s in catch_body:
                self.eval_stmt(s, env)
    def eval_stmt(self, stmt, env):
        kind = stmt[0]
        handler = self._eval_dispatch.get(kind)
        if handler:
            return handler(stmt, env)
        return None

    def _eval_program(self, stmt, env):
        for s in stmt[1]:
            self.eval_stmt(s, env)

    def _eval_out(self, stmt, env):
        _, expr, _ = stmt
        val = self.eval_expr(expr, env)
        if isinstance(val, list):
            out_str = " | ".join(str(x) for x in val)
        else:
            out_str = str(val)
        print(f">>> {out_str}")

    def _eval_assign_target(self, stmt, env):
        _, target, expr, line = stmt
        val = self.eval_expr(expr, env)
        if target[0] == "VAR_TARGET":
            env.set(target[1], val)
        elif target[0] == "DOT_TARGET":
            _, obj_name, prop_name = target
            env.set_dot(obj_name, prop_name, val, line)

    def _eval_assign_list(self, stmt, env):
        _, var_name, items, _ = stmt
        evaluated_items = [self.eval_expr(it, env) for it in items]
        env.set(var_name, evaluated_items)

    def _eval_fn_def(self, stmt, env):
        _, fn_name, params, body, _ = stmt
        self.functions[fn_name] = (params, body)

    def _eval_fdel_def(self, stmt, env):
        _, fn_name, arg_name, _ = stmt
        self.del_functions[fn_name] = arg_name

    def _eval_trg_action(self, stmt, env):
        _, fn_name, arg_expr, line = stmt
        if fn_name in self.del_functions:
            if isinstance(arg_expr, tuple) and arg_expr[0] == "VAR":
                target_var = arg_expr[1]
            elif isinstance(arg_expr, str):
                target_var = arg_expr
            else:
                target_var = str(self.eval_expr(arg_expr, env))
            deleted = env.delete(target_var)
            if deleted:
                print(f"[Memory]: '{target_var}' has been wiped out by {fn_name}!")
            else:
                print(f"[Memory Alert]: Could not wipe '{target_var}' - not found.")
        elif fn_name in self.functions:
            self.call_function(fn_name, [arg_expr], env, line)

    def _eval_call(self, stmt, env):
        _, name, args, line = stmt
        self.call_function(name, args, env, line)

    def _eval_return(self, stmt, env):
        _, expr, _ = stmt
        val = self.eval_expr(expr, env)
        raise ReturnSignal(val)

    def _eval_add_var(self, stmt, env):
        _, name, _ = stmt
        env.declare(name)

    def _eval_add_func(self, stmt, env):
        pass

    def _eval_add_obj(self, stmt, env):
        _, obj_name, props, _ = stmt
        if isinstance(props, str) and props in self.blueprints:
            instance = {}
            for k, v in self.blueprints[props].items():
                instance[k] = self.eval_expr(v, env)
            env.set(obj_name, instance)
        else:
            obj_data = {}
            for k, v in props.items():
                obj_data[k] = self.eval_expr(v, env)
            env.set(obj_name, obj_data)

    def _eval_add_type(self, stmt, env):
        pass

    def _eval_cwin(self, stmt, env):
        _, title_expr, w_expr, h_expr, mode, _ = stmt
        title = str(self.eval_expr(title_expr, env))
        w = int(self.eval_coord(w_expr, env))
        h = int(self.eval_coord(h_expr, env))
        if tk:
            self.gui = TrappyGUI(title, w, h, mode)

    def _eval_win_style(self, stmt, env):
        _, title_expr, color_val, _ = stmt
        color = str(self.eval_expr(color_val, env)) if isinstance(color_val, tuple) else str(color_val)
        if self.gui and self.gui.canvas:
            self.gui.canvas.configure(bg=color)

    def _eval_label(self, stmt, env):
        _, text_expr, x_expr, y_expr, color, _ = stmt
        if self.gui and self.gui.canvas:
            text = str(self.eval_expr(text_expr, env))
            x = self.eval_coord(x_expr, env)
            y = self.eval_coord(y_expr, env)
            self.gui.canvas.create_text(x, y, text=text, fill=color, font=("Consolas", 11, "bold"))

    def _eval_regle(self, stmt, env):
        _, x_expr, y_expr, w_expr, h_expr, color, _ = stmt
        if self.gui and self.gui.canvas:
            x = self.eval_coord(x_expr, env)
            y = self.eval_coord(y_expr, env)
            w = self.eval_coord(w_expr, env)
            h = self.eval_coord(h_expr, env)
            self.gui.canvas.create_rectangle(x, y, x + w, y + h, fill=color, outline="")

    def _eval_circ(self, stmt, env):
        _, x_expr, y_expr, r_expr, color, _ = stmt
        if self.gui and self.gui.canvas:
            x = self.eval_coord(x_expr, env)
            y = self.eval_coord(y_expr, env)
            r = self.eval_coord(r_expr, env)
            self.gui.canvas.create_oval(x - r, y - r, x + r, y + r, fill=color, outline="")

    def _eval_line(self, stmt, env):
        _, x1_expr, y1_expr, x2_expr, y2_expr, color, _ = stmt
        if self.gui and self.gui.canvas:
            x1 = self.eval_coord(x1_expr, env)
            y1 = self.eval_coord(y1_expr, env)
            x2 = self.eval_coord(x2_expr, env)
            y2 = self.eval_coord(y2_expr, env)
            self.gui.canvas.create_line(x1, y1, x2, y2, fill=color, width=2)

    def _eval_cube3d(self, stmt, env):
        _, cx_e, cy_e, cz_e, size_e, rx_e, ry_e, color, _ = stmt
        if not (self.gui and self.gui.canvas):
            return
        cx = self.eval_coord(cx_e, env)
        cy = self.eval_coord(cy_e, env)
        cz = self.eval_coord(cz_e, env)
        size = self.eval_coord(size_e, env) / 2.0
        pitch = math.radians(self.eval_coord(rx_e, env))
        yaw = math.radians(self.eval_coord(ry_e, env))
        camera_dist = 400.0

        vertices = [
            (-size, -size, -size), (size, -size, -size), (size, size, -size), (-size, size, -size),
            (-size, -size, size),  (size, -size, size),  (size, size, size),  (-size, size, size)
        ]
        edges = [
            (0,1), (1,2), (2,3), (3,0),
            (4,5), (5,6), (6,7), (7,4),
            (0,4), (1,5), (2,6), (3,7)
        ]

        proj = []
        for vx, vy, vz in vertices:
            x1 = vx * math.cos(yaw) + vz * math.sin(yaw)
            z1 = -vx * math.sin(yaw) + vz * math.cos(yaw)
            y1 = vy * math.cos(pitch) - z1 * math.sin(pitch)
            z2 = vy * math.sin(pitch) + z1 * math.cos(pitch)

            depth = camera_dist + z2 + cz
            if depth < 1.0:
                depth = 1.0
            fov = camera_dist / depth
            proj.append((cx + x1 * fov, cy + y1 * fov))

        for u, v in edges:
            self.gui.canvas.create_line(proj[u][0], proj[u][1], proj[v][0], proj[v][1], fill=color, width=2)

    def _eval_line3d(self, stmt, env):
        _, x1_e, y1_e, z1_e, x2_e, y2_e, z2_e, rx_e, ry_e, color, _ = stmt
        if not (self.gui and self.gui.canvas):
            return
        x1_val = self.eval_coord(x1_e, env)
        y1_val = self.eval_coord(y1_e, env)
        z1_val = self.eval_coord(z1_e, env)
        x2_val = self.eval_coord(x2_e, env)
        y2_val = self.eval_coord(y2_e, env)
        z2_val = self.eval_coord(z2_e, env)
        pitch = math.radians(self.eval_coord(rx_e, env))
        yaw = math.radians(self.eval_coord(ry_e, env))
        camera_dist = 400.0

        pts = []
        for vx, vy, vz in [(x1_val, y1_val, z1_val), (x2_val, y2_val, z2_val)]:
            x1 = vx * math.cos(yaw) + vz * math.sin(yaw)
            z1 = -vx * math.sin(yaw) + vz * math.cos(yaw)
            y1 = vy * math.cos(pitch) - z1 * math.sin(pitch)
            z2 = vy * math.sin(pitch) + z1 * math.cos(pitch)
            depth = camera_dist + z2
            if depth < 1.0:
                depth = 1.0
            fov = camera_dist / depth
            pts.append((x1 * fov + 300, y1 * fov + 200))

        self.gui.canvas.create_line(pts[0][0], pts[0][1], pts[1][0], pts[1][1], fill=color, width=2)

    def _eval_sphere3d(self, stmt, env):
        _, cx_e, cy_e, cz_e, rad_e, rx_e, ry_e, color, _ = stmt
        if not (self.gui and self.gui.canvas):
            return
        cx = self.eval_coord(cx_e, env)
        cy = self.eval_coord(cy_e, env)
        cz = self.eval_coord(cz_e, env)
        rad = self.eval_coord(rad_e, env)
        pitch = math.radians(self.eval_coord(rx_e, env))
        yaw = math.radians(self.eval_coord(ry_e, env))
        camera_dist = 400.0

        rings = []
        seg = 12
        for ang in range(seg):
            t = 2.0 * math.pi * ang / seg
            rings.append((rad * math.cos(t), 0, rad * math.sin(t)))
        for ang in range(seg):
            t = 2.0 * math.pi * ang / seg
            rings.append((rad * math.cos(t), rad * math.sin(t), 0))

        proj = []
        for vx, vy, vz in rings:
            x1 = vx * math.cos(yaw) + vz * math.sin(yaw)
            z1 = -vx * math.sin(yaw) + vz * math.cos(yaw)
            y1 = vy * math.cos(pitch) - z1 * math.sin(pitch)
            z2 = vy * math.sin(pitch) + z1 * math.cos(pitch)
            depth = camera_dist + z2 + cz
            if depth < 1.0:
                depth = 1.0
            fov = camera_dist / depth
            proj.append((cx + x1 * fov, cy + y1 * fov))

        for k in range(seg):
            n1 = (k + 1) % seg
            self.gui.canvas.create_line(proj[k][0], proj[k][1], proj[n1][0], proj[n1][1], fill=color, width=1)
            n2 = seg + ((k + 1) % seg)
            self.gui.canvas.create_line(proj[seg + k][0], proj[seg + k][1], proj[n2][0], proj[n2][1], fill=color, width=1)

    def _eval_pyramid3d(self, stmt, env):
        _, cx_e, cy_e, cz_e, size_e, rx_e, ry_e, color, _ = stmt
        if not (self.gui and self.gui.canvas):
            return
        cx = self.eval_coord(cx_e, env)
        cy = self.eval_coord(cy_e, env)
        cz = self.eval_coord(cz_e, env)
        s = self.eval_coord(size_e, env) / 2.0
        pitch = math.radians(self.eval_coord(rx_e, env))
        yaw = math.radians(self.eval_coord(ry_e, env))
        camera_dist = 400.0

        vertices = [
            (-s, s, -s), (s, s, -s), (s, s, s), (-s, s, s),
            (0, -s, 0)
        ]
        edges = [
            (0,1), (1,2), (2,3), (3,0),
            (0,4), (1,4), (2,4), (3,4)
        ]

        proj = []
        for vx, vy, vz in vertices:
            x1 = vx * math.cos(yaw) + vz * math.sin(yaw)
            z1 = -vx * math.sin(yaw) + vz * math.cos(yaw)
            y1 = vy * math.cos(pitch) - z1 * math.sin(pitch)
            z2 = vy * math.sin(pitch) + z1 * math.cos(pitch)
            depth = camera_dist + z2 + cz
            if depth < 1.0:
                depth = 1.0
            fov = camera_dist / depth
            proj.append((cx + x1 * fov, cy + y1 * fov))

        for u, v in edges:
            self.gui.canvas.create_line(proj[u][0], proj[u][1], proj[v][0], proj[v][1], fill=color, width=2)

    def _eval_button(self, stmt, env):
        _, label_text_expr, x_expr, y_expr, fn_name, _ = stmt
        if self.gui and self.gui.root:
            label_text = str(self.eval_expr(label_text_expr, env))
            x = self.eval_coord(x_expr, env)
            y = self.eval_coord(y_expr, env)
            btn = tk.Button(self.gui.root, text=label_text, command=lambda: self.trigger_action(fn_name))
            btn.place(x=x, y=y)

    def _eval_input(self, stmt, env):
        _, placeholder_expr, x_expr, y_expr, var_name, _ = stmt
        if self.gui and self.gui.root:
            placeholder = str(self.eval_expr(placeholder_expr, env))
            x = self.eval_coord(x_expr, env)
            y = self.eval_coord(y_expr, env)
            entry = tk.Entry(self.gui.root)
            entry.insert(0, placeholder)
            entry.place(x=x, y=y)
            entry.bind("<KeyRelease>", lambda e: env.set(var_name, entry.get()))

    def _eval_gloop(self, stmt, env):
        _, body, _ = stmt
        self.game_loop_body = body

    def _eval_fps_set(self, stmt, env):
        _, mode, rate, _ = stmt
        self.fps_mode = mode
        self.target_fps = int(rate) if rate else 60

    def _eval_play_audio(self, stmt, env):
        _, sound_name, line = stmt
        if winsound:
            try:
                safe_sound = sanitize_path(sound_name)
                winsound.PlaySound(safe_sound, winsound.SND_FILENAME | winsound.SND_ASYNC)
            except Exception as e:
                print(f"[Trappy Audio]: Could not play sound '{sound_name}': {e}")

    def _eval_beep_audio(self, stmt, env):
        _, freq_expr, duration_expr, _ = stmt
        if winsound:
            try:
                freq = int(self.eval_expr(freq_expr, env))
                duration = int(self.eval_expr(duration_expr, env))
                winsound.Beep(max(37, min(32767, freq)), max(1, duration))
            except Exception:
                pass

    def _eval_synth_audio(self, stmt, env):
        _, wave_type_expr, freq_expr, duration_expr, _ = stmt
        if winsound:
            try:
                freq = int(self.eval_expr(freq_expr, env))
                duration = int(self.eval_expr(duration_expr, env))
                winsound.Beep(max(37, min(32767, freq)), max(1, duration))
            except Exception:
                pass

    def _eval_write_file(self, stmt, env):
        _, content_expr, filename, line = stmt
        content = str(self.eval_expr(content_expr, env))
        safe_name = sanitize_path(filename)
        with open(safe_name, "w", encoding="utf-8") as f:
            f.write(content)

    def _eval_http_get(self, stmt, env):
        _, url_expr, var_name, line = stmt
        url = validate_url(str(self.eval_expr(url_expr, env)), line)
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'TrappyRuntime/1.15'})
            with urllib.request.urlopen(req, timeout=3.0) as resp:
                data = resp.read().decode('utf-8', errors='ignore')
                env.set(var_name, data)
        except Exception as e:
            env.set(var_name, f"Error: {e}")

    def _eval_http_post(self, stmt, env):
        _, url_expr, data_expr, var_name, line = stmt
        url = validate_url(str(self.eval_expr(url_expr, env)), line)
        data_raw = self.eval_expr(data_expr, env)
        try:
            if isinstance(data_raw, dict):
                post_data = json.dumps(data_raw).encode('utf-8')
                content_type = 'application/json'
            else:
                post_data = str(data_raw).encode('utf-8')
                content_type = 'text/plain'
            req = urllib.request.Request(url, data=post_data, headers={'User-Agent': 'TrappyRuntime/1.15', 'Content-Type': content_type}, method='POST')
            with urllib.request.urlopen(req, timeout=3.0) as resp:
                data = resp.read().decode('utf-8', errors='ignore')
                env.set(var_name, data)
        except Exception as e:
            env.set(var_name, f"Error: {e}")

    def _eval_download_file(self, stmt, env):
        _, url_expr, file_path, line = stmt
        url = validate_url(str(self.eval_expr(url_expr, env)), line)
        safe_path = sanitize_path(file_path)
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'TrappyRuntime/1.15'})
            with urllib.request.urlopen(req, timeout=10.0) as resp:
                with open(safe_path, "wb") as f:
                    f.write(resp.read())
            print(f"[Trappy Web]: Successfully downloaded '{url}' -> '{safe_path}'")
        except Exception as e:
            raise TrappyError(f"Download failed: {e}", line)

    def _eval_cli_connect(self, stmt, env):
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
                s.setblocking(False)
                env.set(var_name, s)
                print(f"[Trappy Client]: Connected to {host}:{port}")
            except Exception as e:
                sock = VirtualLoopbackSocket(channel_id=f"port_{port}")
                env.set(var_name, sock)
                print(f"[Trappy Client]: Offline fallback active -> loopback channel {port}")

    def _eval_cli_send(self, stmt, env):
        _, client_name, data_expr, line = stmt
        sock = env.get(client_name, line)
        payload = self.eval_expr(data_expr, env)
        if isinstance(payload, str):
            payload_bytes = payload.encode('utf-8')
        elif isinstance(payload, bytes):
            payload_bytes = payload
        else:
            payload_bytes = str(payload).encode('utf-8')

        if sock and hasattr(sock, "sendall"):
            try:
                sock.sendall(payload_bytes)
            except Exception as e:
                print(f"[Trappy Client Error]: Send failed: {e}")

    def _eval_cli_recv(self, stmt, env):
        _, client_name, var_name, line = stmt
        sock = env.get(client_name, line)
        msg = ""
        if sock and hasattr(sock, "recv"):
            try:
                if isinstance(sock, VirtualLoopbackSocket):
                    raw = sock.recv(4096)
                else:
                    ready, _, _ = select.select([sock], [], [], 0)
                    if ready:
                        raw = sock.recv(4096)
                    else:
                        raw = b""
                if isinstance(raw, bytes):
                    msg = raw.decode('utf-8', errors='ignore').strip()
                else:
                    msg = str(raw).strip()
            except Exception:
                msg = ""
        env.set(var_name, msg)

    def _eval_cli_close(self, stmt, env):
        _, client_name, line = stmt
        sock = env.get(client_name, line)
        if sock and hasattr(sock, "close"):
            try:
                sock.close()
            except Exception:
                pass

    def _eval_srv_listen(self, stmt, env):
        _, port_expr, var_name, line = stmt
        port = int(self.eval_expr(port_expr, env))
        host = os.environ.get("TRAPPY_HOST", "127.0.0.1")
        try:
            srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            srv.bind((host, port))
            srv.listen(5)
            srv.setblocking(False)
            env.set(var_name, srv)
            print(f"[Trappy Server]: Listening on {host}:{port}")
        except Exception as e:
            print(f"[Trappy Server]: Failed to bind on {host}:{port}: {e}")
            env.set(var_name, None)

    def _eval_srv_accept(self, stmt, env):
        _, server_name, var_name, line = stmt
        srv = env.get(server_name, line)
        client_sock = None
        if srv:
            try:
                ready, _, _ = select.select([srv], [], [], 0)
                if ready:
                    client_sock, _ = srv.accept()
                    client_sock.setblocking(False)
            except Exception:
                client_sock = None
        env.set(var_name, client_sock)

    def _eval_mem_alloc(self, stmt, env):
        _, size_expr, var_name, _ = stmt
        size = int(self.eval_expr(size_expr, env))
        buf = bytearray(size)
        buf_id = len(self.memory_blocks) + 1
        self.memory_blocks[buf_id] = buf
        env.set(var_name, buf_id)

    def _eval_mem_write(self, stmt, env):
        _, buf_name, offset_expr, byte_expr, line = stmt
        if self.safe_mode:
            raise TrappySecurityError("Direct memory manipulation is disabled in safe mode", line)
        buf_id = env.get(buf_name, line)
        offset = int(self.eval_expr(offset_expr, env))
        val = int(self.eval_expr(byte_expr, env))
        if buf_id in self.memory_blocks:
            buf = self.memory_blocks[buf_id]
            if 0 <= offset < len(buf):
                buf[offset] = val & 0xFF
            else:
                raise TrappyError(f"Memory out of bounds write at offset {offset}", line)

    def _eval_mem_read(self, stmt, env):
        _, buf_name, offset_expr, var_name, line = stmt
        buf_id = env.get(buf_name, line)
        offset = int(self.eval_expr(offset_expr, env))
        if buf_id in self.memory_blocks:
            buf = self.memory_blocks[buf_id]
            if 0 <= offset < len(buf):
                env.set(var_name, buf[offset])
            else:
                raise TrappyError(f"Memory out of bounds read at offset {offset}", line)

    def _eval_sys_exec(self, stmt, env):
        _, cmd_expr, var_name, line = stmt
        if self.safe_mode:
            raise TrappySecurityError("Command execution ('sys_exec') is disabled in safe mode", line)
        cmd = str(self.eval_expr(cmd_expr, env))
        try:
            res = subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.STDOUT)
            env.set(var_name, res.strip())
        except Exception as e:
            env.set(var_name, f"Exec Error: {e}")

    def _eval_sys_env(self, stmt, env):
        _, key_expr, var_name, _ = stmt
        key = str(self.eval_expr(key_expr, env))
        env.set(var_name, os.environ.get(key, ""))

    def _eval_discord_webhook(self, stmt, env):
        _, url_expr, msg_expr, status_var, line = stmt
        url = validate_url(str(self.eval_expr(url_expr, env)), line)
        msg = str(self.eval_expr(msg_expr, env))
        status = 0
        try:
            payload = json.dumps({"content": msg}).encode("utf-8")
            req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json", "User-Agent": "TrappyDiscord/1.15"}, method="POST")
            with urllib.request.urlopen(req, timeout=3.0) as resp:
                status = resp.status
        except urllib.error.HTTPError as he:
            status = he.code
        except Exception:
            status = 0
        env.set(status_var, status)

    def _eval_ws_connect(self, stmt, env):
        pass

    def _eval_ws_send(self, stmt, env):
        pass

    def _eval_ws_recv(self, stmt, env):
        pass

    def _eval_ws_close(self, stmt, env):
        pass

    def _eval_json_parse(self, stmt, env):
        _, json_str_expr, dest_var, line = stmt
        raw_str = str(self.eval_expr(json_str_expr, env))
        try:
            parsed = json.loads(raw_str)
            env.set(dest_var, parsed)
        except Exception as e:
            raise TrappyError(f"JSON Parse failed: {e}", line)

    def _eval_json_dump(self, stmt, env):
        _, obj_expr, dest_var, _ = stmt
        val = self.eval_expr(obj_expr, env)
        dumped = json.dumps(val)
        env.set(dest_var, dumped)

    def _eval_dict_new(self, stmt, env):
        _, dict_name, _ = stmt
        env.set(dict_name, {})

    def _eval_dset(self, stmt, env):
        _, dict_name, key_expr, val_expr, line = stmt
        d = env.get(dict_name, line)
        if isinstance(d, dict):
            k = str(self.eval_expr(key_expr, env))
            v = self.eval_expr(val_expr, env)
            d[k] = v
        else:
            raise TrappyError(f"'{dict_name}' is not a dictionary!", line)

    def _eval_dget(self, stmt, env):
        _, dict_name, key_expr, dest_var, line = stmt
        d = env.get(dict_name, line)
        if isinstance(d, dict):
            k = str(self.eval_expr(key_expr, env))
            env.set(dest_var, d.get(k, 0))
        else:
            raise TrappyError(f"'{dict_name}' is not a dictionary!", line)

    def _eval_dkeys(self, stmt, env):
        _, dict_name, dest_var, line = stmt
        d = env.get(dict_name, line)
        if isinstance(d, dict):
            env.set(dest_var, list(d.keys()))
        else:
            raise TrappyError(f"'{dict_name}' is not a dictionary!", line)

    def _eval_lget(self, stmt, env):
        _, list_name, idx_expr, dest_var, line = stmt
        lst = env.get(list_name, line)
        if isinstance(lst, list):
            idx = int(self.eval_expr(idx_expr, env))
            if 0 <= idx < len(lst):
                env.set(dest_var, lst[idx])
            else:
                env.set(dest_var, 0)
        else:
            raise TrappyError(f"'{list_name}' is not a list!", line)

    def _eval_lset(self, stmt, env):
        _, list_name, idx_expr, val_expr, line = stmt
        lst = env.get(list_name, line)
        if isinstance(lst, list):
            idx = int(self.eval_expr(idx_expr, env))
            v = self.eval_expr(val_expr, env)
            if 0 <= idx < len(lst):
                lst[idx] = v
            else:
                raise TrappyError(f"List index {idx} out of range (length {len(lst)})", line)
        else:
            raise TrappyError(f"'{list_name}' is not a list!", line)

    def _eval_llen(self, stmt, env):
        _, list_name, dest_var, line = stmt
        lst = env.get(list_name, line)
        if isinstance(lst, list):
            env.set(dest_var, len(lst))
        elif isinstance(lst, str):
            env.set(dest_var, len(lst))
        elif isinstance(lst, dict):
            env.set(dest_var, len(lst))
        else:
            env.set(dest_var, 0)

    def _eval_lpush(self, stmt, env):
        _, list_name, val_expr, line = stmt
        lst = env.get(list_name, line)
        if isinstance(lst, list):
            v = self.eval_expr(val_expr, env)
            lst.append(v)
        else:
            raise TrappyError(f"'{list_name}' is not a list!", line)

    def _eval_lpop(self, stmt, env):
        _, list_name, dest_var, line = stmt
        lst = env.get(list_name, line)
        if isinstance(lst, list) and len(lst) > 0:
            env.set(dest_var, lst.pop())
        else:
            env.set(dest_var, 0)

    def _eval_file_write(self, stmt, env):
        _, file_expr, content_expr, line = stmt
        fname = str(self.eval_expr(file_expr, env))
        content = str(self.eval_expr(content_expr, env))
        safe_name = sanitize_path(fname)
        with open(safe_name, "w", encoding="utf-8") as f:
            f.write(content)

    def _eval_file_read(self, stmt, env):
        _, file_expr, dest_var, line = stmt
        fname = str(self.eval_expr(file_expr, env))
        safe_name = sanitize_path(fname)
        if os.path.exists(safe_name):
            with open(safe_name, "r", encoding="utf-8") as f:
                env.set(dest_var, f.read())
        else:
            env.set(dest_var, "")

    def _eval_file_append(self, stmt, env):
        _, file_expr, content_expr, line = stmt
        fname = str(self.eval_expr(file_expr, env))
        content = str(self.eval_expr(content_expr, env))
        safe_name = sanitize_path(fname)
        with open(safe_name, "a", encoding="utf-8") as f:
            f.write(content)

    def _eval_file_exists(self, stmt, env):
        _, file_expr, dest_var, line = stmt
        fname = str(self.eval_expr(file_expr, env))
        safe_name = sanitize_path(fname)
        env.set(dest_var, 1 if os.path.exists(safe_name) else 0)

    def _eval_file_delete(self, stmt, env):
        _, file_expr, line = stmt
        fname = str(self.eval_expr(file_expr, env))
        safe_name = sanitize_path(fname)
        if os.path.exists(safe_name):
            try:
                os.remove(safe_name)
            except Exception:
                pass

    def _eval_dir_list(self, stmt, env):
        _, path_expr, dest_var, line = stmt
        path_str = str(self.eval_expr(path_expr, env))
        safe_path = sanitize_path(path_str)
        if os.path.isdir(safe_path):
            env.set(dest_var, os.listdir(safe_path))
        else:
            env.set(dest_var, [])

    def _eval_box_hit(self, stmt, env):
        _, x1_e, y1_e, w1_e, h1_e, x2_e, y2_e, w2_e, h2_e, dest_var, line = stmt
        x1 = self.eval_coord(x1_e, env)
        y1 = self.eval_coord(y1_e, env)
        w1 = self.eval_coord(w1_e, env)
        h1 = self.eval_coord(h1_e, env)
        x2 = self.eval_coord(x2_e, env)
        y2 = self.eval_coord(y2_e, env)
        w2 = self.eval_coord(w2_e, env)
        h2 = self.eval_coord(h2_e, env)
        hit = (x1 < x2 + w2 and x1 + w1 > x2 and y1 < y2 + h2 and y1 + h1 > y2)
        env.set(dest_var, 1 if hit else 0)

    def _eval_vec_add(self, stmt, env):
        _, x1_e, y1_e, x2_e, y2_e, var_name, _ = stmt
        x1 = self.eval_coord(x1_e, env)
        y1 = self.eval_coord(y1_e, env)
        x2 = self.eval_coord(x2_e, env)
        y2 = self.eval_coord(y2_e, env)
        env.set(var_name, [x1 + x2, y1 + y2])

    def _eval_vec_mag(self, stmt, env):
        _, x_e, y_e, dest_var, _ = stmt
        x = self.eval_coord(x_e, env)
        y = self.eval_coord(y_e, env)
        mag = math.sqrt(x*x + y*y)
        env.set(dest_var, mag)

    def _eval_each_loop(self, stmt, env):
        _, item_var, list_var, body, line = stmt
        lst = env.get(list_var, line)
        if isinstance(lst, list):
            for item in lst:
                env.set(item_var, item)
                try:
                    for s in body:
                        self.eval_stmt(s, env)
                except BreakSignal as b:
                    if b.loop_type in ("sloop", "srep", "each", "all"):
                        break
                    raise b
                except ContinueSignal:
                    continue
        else:
            raise TrappyError(f"'{list_var}' is not a list to loop over!", line)

    def _eval_if_stmt(self, stmt, env):
        _, condition, then_body, else_body, _ = stmt
        if self._eval_cond_bool(condition, env):
            for s in then_body:
                self.eval_stmt(s, env)
        elif else_body:
            for s in else_body:
                self.eval_stmt(s, env)

    def _eval_key_check(self, stmt, env):
        _, key_name, is_flkey, body, _ = stmt
        if self.gui:
            is_active = (key_name.upper() in self.gui.pressed_keys)
            if is_active:
                for s in body:
                    self.eval_stmt(s, env)

    def _eval_rep_loop(self, stmt, env):
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
                if b.loop_type in ("srep", "all"):
                    break
                raise b
            except ContinueSignal:
                pass
            i += 1

    def _eval_infinite_loop(self, stmt, env):
        _, body, _ = stmt
        while True:
            try:
                for s in body:
                    self.eval_stmt(s, env)
            except BreakSignal as b:
                if b.loop_type in ("sloop", "srep", "all"):
                    break
                raise b
            except ContinueSignal:
                continue

    def _eval_break_rep(self, stmt, env):
        raise BreakSignal("srep")

    def _eval_break_loop(self, stmt, env):
        raise BreakSignal("sloop")

    def _eval_pack_data(self, stmt, env):
        _, obj_name, var_name, line = stmt
        obj = env.get(obj_name, line)
        if isinstance(obj, dict):
            packet_str = json.dumps(obj)
            env.set(var_name, packet_str)
        else:
            raise TrappyError(f"'{obj_name}' is not an object/dict to pack!", line)

    def _eval_unpack_data(self, stmt, env):
        _, packet_expr, obj_name, line = stmt
        packet_val = self.eval_expr(packet_expr, env)
        try:
            parsed = json.loads(str(packet_val))
            if isinstance(parsed, dict):
                env.set(obj_name, parsed)
            else:
                env.set(obj_name, {"data": parsed})
        except Exception as e:
            raise TrappyError(f"Failed to unpack packet: {e}", line)

    def trigger_action(self, fn_name):
        if fn_name in self.functions:
            self.call_function(fn_name, [], self.global_env, 0)
        else:
            print(f"[Trappy Alert]: No function named '{fn_name}' found to trigger!")

    def eval_coord(self, raw, env):
        if isinstance(raw, (int, float)):
            return raw
        if isinstance(raw, tuple):
            if raw[0] == "NUM":
                return raw[1]
            if raw[0] == "VAR":
                val = env.get(raw[1], raw[2])
                return float(val) if isinstance(val, (int, float)) else 0.0
            if raw[0] == "DOT":
                val = env.get_dot(raw[1], raw[2], raw[3])
                return float(val) if isinstance(val, (int, float)) else 0.0
            if raw[0] == "RND":
                low = self.eval_coord(raw[1], env)
                high = self.eval_coord(raw[2], env)
                return random.randint(int(low), int(high))
            if raw[0] == "BINOP":
                return self.eval_expr(raw, env)
        return float(raw) if isinstance(raw, (int, float)) else 0.0

    def eval_expr(self, expr, env):
        if isinstance(expr, (int, float, str)):
            return expr

        kind = expr[0]
        if kind == "NUM":
            return expr[1]
        if kind == "STR":
            return expr[1]
        if kind == "VAR":
            return env.get(expr[1], expr[2])
        if kind == "DOT":
            return env.get_dot(expr[1], expr[2], expr[3])

        if kind == "RND":
            low = self.eval_expr(expr[1], env)
            high = self.eval_expr(expr[2], env)
            return random.randint(int(low), int(high))

        if kind == "MATH_UNARY":
            _, op, arg_expr, line = expr
            val = self.eval_expr(arg_expr, env)
            if op == "sqrt":
                return math.sqrt(val)
            elif op == "abs":
                return abs(val)
            elif op == "sin":
                return math.sin(math.radians(val))
            elif op == "cos":
                return math.cos(math.radians(val))
            raise TrappyError(f"Unknown math operation '{op}'", line)

        if kind == "MATH_BINARY":
            _, op, a_expr, b_expr, line = expr
            a = self.eval_expr(a_expr, env)
            b = self.eval_expr(b_expr, env)
            if op == "pow":
                return math.pow(a, b)
            raise TrappyError(f"Unknown binary math operation '{op}'", line)

        if kind == "MATH_DIST":
            _, x1_e, y1_e, x2_e, y2_e, _ = expr
            x1 = self.eval_expr(x1_e, env)
            y1 = self.eval_expr(y1_e, env)
            x2 = self.eval_expr(x2_e, env)
            y2 = self.eval_expr(y2_e, env)
            return math.hypot(x2 - x1, y2 - y1)

        if kind == "MATH_CLAMP":
            _, v_e, min_e, max_e, _ = expr
            v = self.eval_expr(v_e, env)
            mi = self.eval_expr(min_e, env)
            ma = self.eval_expr(max_e, env)
            return max(mi, min(v, ma))

        if kind == "BINOP":
            _, op, left_expr, right_expr = expr
            left = self.eval_expr(left_expr, env)
            right = self.eval_expr(right_expr, env)

            if op == "+":
                if isinstance(left, str) or isinstance(right, str):
                    return str(left) + str(right)
                return left + right
            elif op == "-":
                return left - right
            elif op in ("multi", "*"):
                return left * right
            elif op in ("div", "/"):
                if right == 0:
                    raise TrappyError("Division by zero", 0)
                return left / right
            elif op == "%":
                if right == 0:
                    raise TrappyError("Modulo by zero", 0)
                return left % right
            elif op == "BAND":
                return int(left) & int(right)
            elif op == "BOR":
                return int(left) | int(right)
            elif op == "BXOR":
                return int(left) ^ int(right)
            elif op == "BSHL":
                return int(left) << int(right)
            elif op == "BSHR":
                return int(left) >> int(right)

        if kind == "CALL":
            _, name, args, line = expr
            return self.call_function(name, args, env, line)

        return 0

    def call_function(self, fn_name, args, env, line):
        self.call_depth += 1
        if self.call_depth > self.MAX_CALL_DEPTH:
            self.call_depth = 0
            raise TrappySecurityError(
                f"Recursion bomb blocked: exceeded maximum stack ceiling ({self.MAX_CALL_DEPTH})!",
                line
            )

        if fn_name not in self.functions:
            self.call_depth -= 1
            raise TrappyError(f"Undefined Trappy function '{fn_name}'", line)

        params, body = self.functions[fn_name]
        if len(args) != len(params):
            self.call_depth -= 1
            raise TrappyError(
                f"Function '{fn_name}' expects {len(params)} argument(s), but got {len(args)}",
                line
            )

        fn_env = Environment(parent=env)
        for p_name, arg_expr in zip(params, args):
            val = self.eval_expr(arg_expr, env)
            fn_env.set(p_name, val)

        result = 0
        try:
            for stmt in body:
                self.eval_stmt(stmt, fn_env)
        except ReturnSignal as ret:
            result = ret.value
        finally:
            self.call_depth -= 1

        return result

def run_trappy(code, safe_mode=False):
    tokens = tokenize(code)
    parser = Parser(tokens)
    ast = parser.parse_program()
    interpreter = TrappyInterpreter(safe_mode=safe_mode)
    interpreter.run(ast)
    return interpreter

if __name__ == "__main__":
    safe_flag = "--safe" in sys.argv
    clean_argv = [a for a in sys.argv[1:] if a != "--safe"]
    if clean_argv:
        filepath = clean_argv[0]
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                source = f.read()
            run_trappy(source, safe_mode=safe_flag)
        else:
            print(f"Error: File '{filepath}' does not exist.")
    else:
        print(f"Trappy Language Core Runtime Engine v{__version__}")
        print("Usage: python trappy.py <filename.trappy>")
