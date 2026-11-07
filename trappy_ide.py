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
    "abs", "add_func", "add_obj", "add_type", "add_var", "ai_agent_act", "ai_agent_load", "ai_agent_new",
    "ai_agent_reward", "ai_agent_save", "ai_embed", "ai_net_classify", "ai_net_load", "ai_net_new", "ai_net_predict", "ai_net_save",
    "ai_net_train", "ai_ngram_gen", "ai_ngram_train", "ai_sim", "ai_tokenize", "ai_ui_agent", "ai_ui_chat", "ai_ui_net",
    "answ", "as", "ath", "badge", "band", "beep", "bnot", "bor",
    "box_hit", "break", "bshl", "bshr", "btn", "btn_modern", "bxor", "card",
    "catch", "chr", "circ", "clamp", "cli_close", "cli_connect", "cli_recv", "cli_send",
    "cnt", "continue", "cos", "cube3d", "cwin", "ddel", "dget", "dhas",
    "dict", "dir_list", "discord_webhook", "dist", "dkeys", "download", "dset", "each",
    "else", "eq", "exit", "f3d", "fai", "false", "fapp", "fcli",
    "fdel", "file_append", "file_delete", "file_exists", "file_read", "file_write", "flist", "fmh",
    "fn", "fos", "ftxt", "fui", "func", "fweb", "gan", "gloop",
    "grt", "http_get", "http_post", "icon", "ifr", "import", "in", "inf",
    "inp", "is_alpha", "is_digit", "json_dump", "json_parse", "key", "label", "lcontains",
    "lget", "line", "line3d", "linsert", "llen", "loop", "lpop", "lpush",
    "lset", "lslice", "lss", "lst", "mem_alloc", "mem_read", "mem_write", "mh",
    "notify_toast", "ord", "os_ai_anomaly_check", "os_ai_assistant", "os_app_download", "os_app_install", "os_app_kill", "os_app_launch",
    "os_app_list", "os_app_uninstall", "os_battery_info", "os_block_list", "os_boot", "os_defense_hook", "os_exploit_guard", "os_exploit_status",
    "os_firewall_rule", "os_hw_info", "os_integrity_seal", "os_integrity_verify", "os_ipc_recv", "os_ipc_send", "os_jailbreak_check", "os_jailbreak_defend",
    "os_panic", "os_perm_check", "os_perm_grant", "os_perm_revoke", "os_proc_kill", "os_proc_list", "os_proc_spawn", "os_ring_get",
    "os_ring_set", "os_screen_mode", "os_setting_dump", "os_setting_get", "os_setting_set", "os_shutdown", "os_touch_event", "os_ui_notify",
    "os_ui_render", "os_ui_taskbar", "os_ui_window", "os_vfs_del", "os_vfs_list", "os_vfs_mount", "os_vfs_read", "os_vfs_stat",
    "os_vfs_write", "os_yield", "pack_data", "play", "pow", "progress", "pyramid3d", "regle",
    "rep", "return", "rnd", "rt", "sbgwin", "sfind", "sget", "sin",
    "sjoin", "slen", "slider", "sloop", "slower", "sm", "spawn", "sphere3d",
    "sqrt", "srep", "sreplace", "srv_accept", "srv_listen", "ssplit", "ssub", "strim",
    "supper", "swhile", "synth", "sys_env", "sys_exec", "then", "tit", "to_float",
    "to_int", "to_num", "to_str", "toggle", "tren", "trst", "true", "try",
    "txt", "type_of", "ui_ease", "ui_theme", "unpack_data", "vec_add", "vec_mag", "while",
    "ws_close", "ws_connect", "ws_recv", "ws_send"
]

HIGHLIGHT_KEYWORDS = list(set(ASSIST_KEYWORDS + [
    "fps", "calm", "lock", "unlock", "psed", "changed", "flkey", "mousel", "mouser"
]))

MANUAL_DATABASE = [
    ("trst", "trst ... tren", "Marks the entry point and start of the Trappy program or function execution block.", "trst\n    out \"Program initialized\"\ntren"),
    ("tren", "tren", "Terminates the current code block, function body, loop, or main program scope.", "trst\n    out \"Running\"\ntren"),
    ("txt", "txt \"string\" tit var_name", "Declares a text variable and assigns a string literal value.", "txt \"Welcome to Trappy v1.7\" tit greeting\nout greeting"),
    ("tit", "... tit var_name", "Target assignment keyword used across commands to store results into variables.", "slen \"Trappy\" tit length\nout length"),
    ("inf", "inf \"message\"", "Outputs an informational system notice to standard output or the IDE console.", "inf \"System subsystem ready\""),
    ("ath", "ath \"Author Name\"", "Declares author attribution metadata for the current script or application.", "ath \"ashoccompany / Asham\""),
    ("fdel", "fdel var_name", "Fast variable deletion shorthand that removes a variable from the active scope.", "add_var temp:100\nfdel temp"),
    ("mh", "mh expr eq var_name", "Evaluates a mathematical expression and assigns the numerical result to a variable.", "mh (10 * 5) + 2 eq result\nout result"),
    ("eq", "... eq var_name", "Equals assignment operator used with mh, add_var, and expression statements.", "mh 100 / 4 eq quarter"),
    ("rt", "rt var_name", "Reads a line of user text from standard input directly into a variable.", "out \"Enter player name: \"\nrt player_name\nout player_name"),
    ("answ", "answ \"Prompt text\" tit var_name", "Prompts the user with a question and captures their text input.", "answ \"What is your username? \" tit user\ngan user"),
    ("out", "out expression", "Prints an evaluated expression, string, or number to standard console output.", "out \"Calculated value: \" + to_str(42)"),
    ("gan", "gan expression", "Outputs message to the terminal console with automatic newline formatting.", "gan \"Process terminated cleanly.\""),
    ("add_var", "add_var name:value", "Initializes a new variable with a name and initial value.", "add_var health:100\nout health"),
    ("add_obj", "add_obj object_name", "Instantiates a new object namespace container for fields and methods.", "add_obj player\nplayer.x = 10\nplayer.y = 20"),
    ("add_func", "add_func obj:name:fn", "Attaches a named method or function reference to an instantiated object.", "add_obj hero\nfn attack\n    out \"Hero attacks!\"\ntren\nadd_func hero:strike:attack"),
    ("add_type", "add_type name:schema", "Defines a custom object type schema with structured properties.", "add_type Vector3:\"x,y,z\""),
    ("spawn", "spawn type_name as var_name", "Instantiates a new instance of a user-defined struct or object type.", "spawn Vector3 as player_pos\nplayer_pos.x = 0"),
    ("as", "spawn type as alias", "Type instantiation and aliasing binding keyword.", "spawn Actor as npc"),
    ("ifr", "ifr condition ... else ... tren", "Evaluates a conditional expression and branches execution accordingly.", "ifr score > 50\n    out \"Passed\"\nelse\n    out \"Try again\"\ntren"),
    ("then", "ifr condition then ... tren", "Optional keyword following an if condition for enhanced readability.", "ifr health <= 0 then\n    out \"Defeated\"\ntren"),
    ("else", "else", "Defines the alternative execution block in an ifr statement when condition is false.", "ifr is_ready == 1\n    out \"Ready\"\nelse\n    out \"Standby\"\ntren"),
    ("grt", "a grt b", "Greater-than relational comparison operator (equivalent to a > b).", "ifr score grt 100\n    out \"High score!\"\ntren"),
    ("lss", "a lss b", "Less-than relational comparison operator (equivalent to a < b).", "ifr energy lss 10\n    out \"Low battery warning\"\ntren"),
    ("sm", "a sm b", "Same / equality relational comparison operator (equivalent to a == b).", "ifr status sm \"OK\"\n    out \"Online\"\ntren"),
    ("exst", "exst var_name", "Checks if a variable or property exists and is defined in the current scope.", "ifr exst user_token\n    out \"Token present\"\ntren"),
    ("exist", "exist file_or_var", "Tests whether a file path exists on disk or variable exists in memory.", "ifr exist \"save.dat\"\n    out \"Save found\"\ntren"),
    ("rep", "rep count ... tren", "Executes the enclosed block of statements a fixed number of times.", "rep 5\n    out \"Repeating step\"\ntren"),
    ("loop", "loop ... tren", "Executes an unconditional continuous loop until an explicit break signal.", "add_var i:0\nloop\n    mh i + 1 eq i\n    ifr i >= 10\n        break\n    tren\ntren"),
    ("srep", "srep max_count ... tren", "Safe bounded repeat loop with upper limit guard against runaway iteration.", "srep 100\n    out \"Safe step\"\ntren"),
    ("sloop", "sloop ... tren", "Safe continuous loop with automatic execution cycle watchdog ceiling.", "sloop\n    ifr done == 1\n        break\n    tren\ntren"),
    ("while", "while condition ... tren", "Executes the loop body repeatedly as long as the condition evaluates to true.", "add_var n:5\nwhile n > 0\n    out n\n    mh n - 1 eq n\ntren"),
    ("swhile", "swhile condition ... tren", "Safe guarded while loop that prevents infinite loops via watchdog timeout.", "swhile retry_count < 3\n    out \"Attempting...\"\ntren"),
    ("each", "each item in list ... tren", "Iterates sequentially over every item in a collection or list.", "lst 10 | 20 | 30 eq nums\neach x in nums\n    out x\ntren"),
    ("in", "each item in collection", "Specifies the target collection in an each iteration loop.", "each file in file_list\n    out file\ntren"),
    ("cnt", "cnt loop_var", "Inspects the current loop cycle iteration counter.", "rep 3\n    cnt step\n    out step\ntren"),
    ("break", "break", "Immediately breaks and terminates the innermost active loop block.", "loop\n    break\ntren"),
    ("continue", "continue", "Skips remaining statements in the current iteration and jumps to the next cycle.", "each x in items\n    ifr x == 0\n        continue\n    tren\n    out x\ntren"),
    ("fn", "fn name param1:param2 ... return val ... tren", "Declares a reusable first-class function with arguments and return support.", "fn add_points a:b\n    mh a + b eq sum\n    return sum\ntren\nout add_points(15:25)"),
    ("func", "func name param:param ... tren", "Alternative syntax keyword for defining Trappy functions.", "func greet user\n    out \"Hello \" + user\ntren\ngreet(\"Asham\")"),
    ("return", "return expression", "Exits the active function call frame and returns the evaluated value.", "fn square x\n    return x * x\ntren"),
    ("try", "try ... catch err ... tren", "Executes block safely, catching any runtime error without terminating script.", "try\n    mh 10 / 0 eq fail\ncatch err\n    out \"Error trapped: \" + err\ntren"),
    ("catch", "catch error_var ... tren", "Error handler block that binds the caught exception message to a variable.", "try\n    file_read \"missing.txt\" tit data\ncatch err\n    out \"Handled: \" + err\ntren"),
    ("fmh", "fmh expr eq var", "Fast math expression shorthand.", "fmh (5 * 4) + 10 eq total"),
    ("ftxt", "ftxt \"str\" tit var", "Fast string assignment shorthand.", "ftxt \"Fast text\" tit label"),
    ("flist", "flist ... eq var", "Fast list declaration shorthand.", "flist 1 | 2 | 3 eq vals"),
    ("frep", "frep count ... tren", "Fast repeat loop shorthand.", "frep 3\n    out \"Fast rep\"\ntren"),
    ("floop", "floop ... tren", "Fast continuous loop shorthand.", "floop\n    break\ntren"),
    ("fgui", "fgui ... tren", "Fast GUI window initialization block.", "fgui\n    label \"Fast UI\" 20:20\ntren"),
    ("fui", "fui <cmd>", "Fast UI widget dispatcher shorthand.", "fui card 10:10 200:100"),
    ("fdrw", "fdrw <cmd>", "Fast canvas drawing dispatcher.", "fdrw circ 50:50 20 #06b6d4"),
    ("fgfx", "fgfx <cmd>", "Fast graphics pipeline dispatcher.", "fgfx regle 0:0 100:100 #22c55e"),
    ("fcan", "fcan <cmd>", "Fast canvas container dispatcher.", "fcan cwin \"Fast Canvas\" 400:300 main"),
    ("fweb", "fweb <cmd>", "Fast web request dispatcher.", "fweb http_get \"https://api.github.com\" tit res"),
    ("fcli", "fcli <cmd>", "Fast TCP client dispatcher.", "fcli cli_connect \"127.0.0.1:8080\" tit s"),
    ("fapp", "fapp <cmd>", "Fast application manager dispatcher.", "fapp os_app_list tit apps"),
    ("f3d", "f3d <cmd>", "Fast 3D rendering pipeline dispatcher.", "f3d cube3d 0:0:0 10 #f97316"),
    ("fos", "fos <cmd>", "Fast OS kernel command prefix.", "fos os_hw_info tit info"),
    ("fai", "fai <cmd>", "Fast AI engine command prefix.", "fai ai_net_new \"quick_net\" [2, 1] \"sigmoid\""),
    ("multi", "multi a:b tit var", "Multiplies two numbers and stores the result.", "multi 6:7 tit ans\nout ans"),
    ("div", "div a:b tit var", "Performs safe division between two numbers with zero-division protection.", "div 100:4 tit ans"),
    ("sqrt", "sqrt num tit var", "Calculates the positive square root of a numerical expression.", "sqrt 144 tit root\nout root"),
    ("pow", "pow base:exp tit var", "Raises a base number to the specified power exponent.", "pow 2:8 tit byte_max"),
    ("abs", "abs num tit var", "Computes the absolute magnitude of a real number.", "abs -45.5 tit positive_val"),
    ("sin", "sin deg tit var", "Calculates the trigonometric sine for an angle in degrees.", "sin 90 tit s"),
    ("cos", "cos deg tit var", "Calculates the trigonometric cosine for an angle in degrees.", "cos 0 tit c"),
    ("dist", "dist x1:y1:x2:y2 tit var", "Computes the 2D Euclidean distance between two points.", "dist 0:0:30:40 tit d\nout d"),
    ("clamp", "clamp val:min:max tit var", "Clamps a value within specified lower and upper bounds.", "clamp 150:0:100 tit capped"),
    ("rnd", "rnd min:max tit var", "Generates a pseudo-random integer between min and max inclusive.", "rnd 1:6 tit dice_roll"),
    ("box_hit", "box_hit x1:y1:w1:h1:x2:y2:w2:h2 tit var", "Performs 2D Axis-Aligned Bounding Box (AABB) intersection testing.", "box_hit 10:10:20:20:15:15:20:20 tit hit"),
    ("vec_add", "vec_add x1:y1 x2:y2 tit var", "Adds two 2D vectors and returns a list [x1+x2, y1+y2].", "vec_add 10:20 5:15 tit velocity"),
    ("vec_mag", "vec_mag x:y tit var", "Calculates the Euclidean magnitude (length) of a 2D vector.", "vec_mag 3:4 tit length"),
    ("band", "band a:b tit var", "Performs bitwise AND across two integer operands.", "band 0xFF:0x0F tit masked"),
    ("bor", "bor a:b tit var", "Performs bitwise OR across two integer operands.", "bor 0xF0:0x0F tit combined"),
    ("bxor", "bxor a:b tit var", "Performs bitwise XOR across two integer operands.", "bxor 12:25 tit toggled"),
    ("bnot", "bnot a tit var", "Performs bitwise NOT inversion on an integer.", "bnot 0 tit inverted"),
    ("bshl", "bshl a:shift tit var", "Bitwise left shift (equivalent to a << shift).", "bshl 1:4 tit shifted"),
    ("bshr", "bshr a:shift tit var", "Bitwise right shift (equivalent to a >> shift).", "bshr 64:2 tit shifted"),
    ("slen", "slen text tit var", "Calculates the total character length of a string expression.", "slen \"Trappy Language\" tit length"),
    ("sget", "sget text:index tit var", "Retrieves character at zero-based index from string.", "sget \"Trappy\":0 tit first_char"),
    ("ssub", "ssub text:start:end tit var", "Extracts substring slice from start to end index.", "ssub \"Trappy Language\":0:6 tit title"),
    ("ssplit", "ssplit text:delimiter tit var", "Splits a string by delimiter into a list of substrings.", "ssplit \"apple,banana,orange\":\",\" tit fruits"),
    ("sjoin", "sjoin list:delimiter tit var", "Joins a list of items into a single delimited string.", "sjoin fruits:\", \" tit joined_str"),
    ("sfind", "sfind text:needle tit var", "Searches for substring and returns index, or -1 if not found.", "sfind \"hello world\":\"world\" tit idx"),
    ("sreplace", "sreplace text:old:new tit var", "Replaces all occurrences of substring with replacement.", "sreplace \"hello world\":\"world\":\"trappy\" tit res"),
    ("strim", "strim text tit var", "Strips leading and trailing whitespace characters from string.", "strim \"   spaced   \" tit cleaned"),
    ("slower", "slower text tit var", "Converts all characters in string to lowercase.", "slower \"TRAPPY\" tit lower_name"),
    ("supper", "supper text tit var", "Converts all characters in string to uppercase.", "supper \"trappy\" tit upper_name"),
    ("ord", "ord char tit var", "Returns integer ASCII code of the first character.", "ord \"A\" tit ascii_code"),
    ("chr", "chr code tit var", "Converts integer ASCII code to its single-character string.", "chr 65 tit char_val"),
    ("is_digit", "is_digit text tit var", "Returns 1 if string consists purely of digits, else 0.", "is_digit \"12345\" tit is_num"),
    ("is_alpha", "is_alpha text tit var", "Returns 1 if string contains alphabetic or underscore characters, else 0.", "is_alpha \"user_name\" tit is_id"),
    ("type_of", "type_of value tit var", "Inspects runtime type: string, number, list, dict, bool, nil.", "type_of 42 tit t"),
    ("to_str", "to_str value tit var", "Converts any variable or expression into a string representation.", "to_str 100 tit s"),
    ("to_num", "to_num value tit var", "Converts string or float value into an integer number.", "to_num \"42\" tit n"),
    ("to_int", "to_int value tit var", "Explicit integer truncation conversion.", "to_int 3.99 tit truncated"),
    ("to_float", "to_float value tit var", "Converts integer or string value into a floating-point number.", "to_float \"3.1415\" tit pi"),
    ("lst", "lst a | b | c eq var", "Declares a new list with elements separated by pipes, or list size.", "lst 10 | 20 | 30 eq my_list"),
    ("[", "[item, item, ...]", "Modern native list and matrix literal syntax for lists, vectors, and neural nets.", "add_var layers:[2, 4, 1]\nadd_var grid:[[0, 1], [1, 0]]"),
    ("lget", "lget list:index tit var", "Retrieves item from list at zero-based index.", "lget my_list:0 tit first_val"),
    ("lset", "lset list:index:val", "Updates the value of list at specified index.", "lset my_list:0:99"),
    ("llen", "llen list tit var", "Calculates total number of elements in list.", "llen my_list tit total_items"),
    ("lpush", "lpush list:val", "Appends a new value onto the end of a list.", "lpush my_list:42"),
    ("lpop", "lpop list tit var", "Pops and removes the last element from a list, storing it in variable.", "lpop my_list tit removed_item"),
    ("lcontains", "lcontains list:item tit var", "Returns 1 if item exists in list, else 0.", "lcontains my_list:42 tit exists"),
    ("linsert", "linsert list:index:val", "Inserts value into list at specified index position.", "linsert my_list:1:55"),
    ("lslice", "lslice list:start:end tit var", "Extracts sublist slice between start and end index.", "lslice my_list:0:2 tit sub"),
    ("dict", "dict tit var_name", "Initializes a fast key-value dictionary hashmap.", "dict tit config"),
    ("dset", "dset dict:key:val", "Stores a key-value mapping into dictionary.", "dset config:\"theme\":\"dark\""),
    ("dget", "dget dict:key tit var", "Retrieves value associated with key from dictionary.", "dget config:\"theme\" tit curr_theme"),
    ("dkeys", "dkeys dict tit var", "Retrieves a list of all keys present in dictionary.", "dkeys config tit all_keys"),
    ("dhas", "dhas dict:key tit var", "Returns 1 if key exists in dictionary, else 0.", "dhas config:\"theme\" tit has_key"),
    ("ddel", "ddel dict:key", "Deletes specified key-value pair from dictionary.", "ddel config:\"temp_key\""),
    ("file_write", "file_write path:content", "Writes string content to disk file with path traversal guard.", "file_write \"log.txt\":\"System booted\""),
    ("file_read", "file_read path tit var", "Reads entire text file from disk into variable.", "file_read \"log.txt\" tit log_data"),
    ("file_append", "file_append path:content", "Appends text content to an existing or new disk file.", "file_append \"log.txt\":\"\nTask completed\""),
    ("file_exists", "file_exists path tit var", "Tests whether a file exists on disk, returning 1 or 0.", "file_exists \"log.txt\" tit exists"),
    ("file_delete", "file_delete path", "Safely removes a file from disk within sandbox boundaries.", "file_delete \"log.txt\""),
    ("dir_list", "dir_list path tit var", "Returns list of files and folders inside directory.", "dir_list \".\" tit files"),
    ("write", "write expr into var", "Directional assignment statement storing expression into variable.", "write 42 into score"),
    ("into", "write val into target", "Directional assignment binding keyword.", "write \"player1\" into username"),
    ("mem_alloc", "mem_alloc bytes tit handle", "Allocates virtual byte buffer in sandboxed process memory table.", "mem_alloc 1024 tit buf_id"),
    ("mem_write", "mem_write handle:offset:val", "Writes byte value at offset in allocated memory buffer.", "mem_write buf_id:0:0x7F"),
    ("mem_read", "mem_read handle:offset tit var", "Reads byte value from memory buffer at offset.", "mem_read buf_id:0 tit b"),
    ("sys_exec", "sys_exec command tit output", "Executes command line in sandboxed environment, capturing stdout.", "sys_exec \"echo Trappy\" tit out"),
    ("sys_env", "sys_env key tit var", "Reads system environment variable safely.", "sys_env \"PATH\" tit sys_path"),
    ("pack", "pack \"format\":val1:val2 tit bytes", "Packs values into binary byte structure using struct format.", "pack \"ii\":100:200 tit bin_data"),
    ("unpack", "unpack \"format\":bytes tit list", "Unpacks binary bytes into list of typed values.", "unpack \"ii\":bin_data tit coords"),
    ("pack_data", "pack_data \"format\":values tit bytes", "Alias for binary data structure packing.", "pack_data \"h\":42 tit b"),
    ("unpack_data", "unpack_data \"format\":bytes tit list", "Alias for binary data structure unpacking.", "unpack_data \"h\":b tit v"),
    ("cli_connect", "cli_connect \"host:port\" tit sock", "Opens TCP client socket connection to remote host.", "cli_connect \"127.0.0.1:8080\" tit client"),
    ("cli_send", "cli_send sock:data", "Transmits raw string or bytes over active TCP client socket.", "cli_send client:\"PING\\n\""),
    ("cli_recv", "cli_recv sock:bytes tit var", "Receives incoming bytes from TCP client socket.", "cli_recv client:1024 tit reply"),
    ("cli_close", "cli_close sock", "Closes active TCP client socket connection.", "cli_close client"),
    ("srv_listen", "srv_listen port tit srv", "Binds TCP server socket and starts listening for connections.", "srv_listen 8080 tit srv"),
    ("srv_accept", "srv_accept srv tit conn", "Accepts incoming TCP client connection, returning socket handle.", "srv_accept srv tit client_conn"),
    ("http_get", "http_get url tit response", "Performs HTTP GET request with SSL verification and redirects.", "http_get \"https://api.github.com\" tit resp"),
    ("http_post", "http_post url:data tit response", "Performs HTTP POST request sending payload data to endpoint.", "http_post \"https://httpbin.org/post\":\"test=1\" tit resp"),
    ("download", "download url:save_path tit status", "Downloads remote file over HTTP securely to disk.", "download \"https://example.com/asset.png\":\"asset.png\" tit status"),
    ("discord_webhook", "discord_webhook url:msg tit status", "Dispatches notification payload directly to Discord Webhook URL.", "discord_webhook \"https://discord.com/api/webhooks/...\":\"Server Started\" tit res"),
    ("ws_connect", "ws_connect url tit ws", "Initiates WebSocket connection to remote server endpoint.", "ws_connect \"ws://echo.websocket.events\" tit socket"),
    ("ws_send", "ws_send ws:payload", "Sends frame payload over WebSocket.", "ws_send socket:\"{\\\"action\\\":\\\"ping\\\"}\""),
    ("ws_recv", "ws_recv ws tit msg", "Receives text frame from WebSocket connection.", "ws_recv socket tit msg"),
    ("ws_close", "ws_close ws", "Performs clean WebSocket protocol disconnection handshake.", "ws_close socket"),
    ("json_parse", "json_parse json_str tit obj", "Parses JSON string into Trappy dictionary or list.", "json_parse \"{\\\"status\\\":\\\"ok\\\"}\" tit res"),
    ("json_dump", "json_dump obj tit json_str", "Serializes Trappy dictionary or list into formatted JSON string.", "json_dump config tit json_out"),
    ("synth", "synth \"waveform\":freq:duration_ms", "Synthesizes audio tone (sine, square, triangle, sawtooth).", "synth \"sine\":440:200"),
    ("play", "play \"sound_path\"", "Plays recorded audio file sample through audio output.", "play \"alert.wav\""),
    ("beep", "beep freq:duration_ms", "Emits basic system motherboard audio frequency beep tone.", "beep 880:150"),
    ("hrable", "hrable", "Diagnostic check verifying audio output device is enabled.", "hrable"),
    ("cwin", "cwin \"Title\" width:height main", "Creates hardware-accelerated 2D canvas window.", "cwin \"My App\" 640:480 main"),
    ("swin", "swin \"Title\" width:height", "Creates standalone graphical viewport window.", "swin \"Viewer\" 400:300"),
    ("sbgwin", "sbgwin \"#color\"", "Configures background color for active graphical window.", "sbgwin \"#18181b\""),
    ("label", "label text x:y [color]", "Renders text string onto 2D canvas surface.", "label \"Trappy OS\" 50:50 \"#ffffff\""),
    ("regle", "regle x1:y1 x2:y2 [color]", "Draws filled rectangle between two diagonal points.", "regle 10:10 100:100 \"#06b6d4\""),
    ("circ", "circ x:y radius [color]", "Draws filled circle centered at coordinate.", "circ 150:150 25 \"#22c55e\""),
    ("line", "line x1:y1 x2:y2 [color]", "Draws 2D vector line between two coordinates.", "line 0:0 200:200 \"#eab308\""),
    ("btn", "btn \"Label\" x:y w:h trg fn_name", "Draws clickable canvas button bound to callback function.", "btn \"Click\" 50:50 100:35 trg on_click"),
    ("inp", "inp var_name x:y w:h", "Draws interactive text entry field bound to variable.", "inp username 50:100 150:30"),
    ("psed", "psed key tit pressed", "Polls keyboard key or mouse button pressed state.", "psed \"Space\" tit is_jumping"),
    ("changed", "changed var_name tit changed", "Checks whether bound input variable was altered.", "changed username tit updated"),
    ("gloop", "gloop ... tren", "Hardware-synchronized continuous graphics render loop.", "gloop\n    circ x:y 10 \"#06b6d4\"\ntren"),
    ("fps calm", "fps calm", "Limits canvas frame rate to 60 FPS with VSync calming to reduce CPU load.", "fps calm"),
    ("lock", "lock", "Locks canvas buffer to enable high-speed batch graphics rendering.", "lock"),
    ("unlock", "unlock", "Flushes and unlocks canvas draw buffer presenting next frame.", "unlock"),
    ("key", "key \"KeyName\" trg fn_name", "Binds keyboard press event to trigger function.", "key \"Escape\" trg on_quit"),
    ("flkey", "flkey key tit state", "Fast non-blocking poll of keyboard key state.", "flkey \"W\" tit w_pressed"),
    ("mousel", "mousel trg fn_name", "Binds left mouse button click event.", "mousel trg on_left_click"),
    ("mouser", "mouser trg fn_name", "Binds right mouse button click event.", "mouser trg on_right_click"),
    ("mousesp", "mousesp x:y", "Queries current mouse cursor position coordinates.", "mousesp mouse_x:mouse_y"),
    ("collde", "collde obj1:obj2 tit hit", "Tests collision between two game objects or sprites.", "collde player:enemy tit hit"),
    ("collide", "collide a:b tit hit", "Collision intersection testing alias.", "collide ball:paddle tit hit"),
    ("trg", "... trg fn_name", "Event trigger callback binding keyword.", "btn \"Submit\" 10:10 80:30 trg on_submit"),
    ("trged", "trged event tit handled", "Checks if event trigger was activated.", "trged click_event tit handled"),
    ("cube3d", "cube3d x:y:z size [color]", "Renders 3D cube mesh at coordinate in space.", "cube3d 0:0:50 20 \"#06b6d4\""),
    ("line3d", "line3d x1:y1:z1:x2:y2:z2 [color]", "Draws 3D vector line segment between coordinates.", "line3d 0:0:0 10:10:10 \"#f97316\""),
    ("point3d", "point3d x:y:z [color]", "Renders 3D coordinate point in space.", "point3d 0:0:100 \"#ffffff\""),
    ("sphere3d", "sphere3d x:y:z radius [color]", "Renders 3D wireframe sphere at coordinate.", "sphere3d 0:0:50 15 \"#22c55e\""),
    ("pyramid3d", "pyramid3d x:y:z base:height [color]", "Renders 3D pyramid geometry in space.", "pyramid3d 0:0:50 20:30 \"#eab308\""),
    ("card", "card x1:y1 x2:y2 [radius] [fill] [border]", "Renders modern container card with rounded corners, customizable fill, and border outline.", "card 50:50 350:250 16 \"#18181b\" \"#27272a\""),
    ("btn_modern", "btn_modern \"Label\" x:y w:h trg fn [color]", "Renders modern styled flat button with hover styling, rounded corners, and click action trigger.", "btn_modern \"Launch OS\" 100:100 140:40 trg on_click \"#06b6d4\""),
    ("toggle", "toggle var_name x:y [trg fn]", "Renders modern interactive toggle switch with smooth track pill and circular knob.", "toggle wifi_enabled 200:150 trg on_toggle"),
    ("progress", "progress val max x:y w:h [fill] [track]", "Renders modern progress bar with smooth rounded pill track and active fill percentage.", "progress 75 100 50:300 200:20 \"#10b981\" \"#27272a\""),
    ("badge", "badge \"Text\" x:y [variant]", "Renders modern status badge pill with colored indicator dot (secure, warning, danger, info, neutral).", "badge \"SECURE\" 30:30 \"secure\""),
    ("slider", "slider var min max x:y w [trg fn]", "Renders modern interactive slider with rounded track, progress fill, and draggable thumb knob.", "slider brightness 0 100 50:350 200 trg on_slide"),
    ("icon", "icon \"name\" x:y [size] [color]", "Renders built-in vector glyph icons (shield, lock, unlock, gear, terminal, wifi, battery, cpu, check, cross, star, bell, user, folder, play, ai, bot).", "icon \"shield\" 10:10 24 \"#06b6d4\""),
    ("notify_toast", "notify_toast \"Title\" \"Message\" [level]", "Presents floating modern toast notification card with accent strip and auto-dismiss timer.", "notify_toast \"System Notice\" \"v1.7 Kernel Active\" \"info\""),
    ("ui_theme", "ui_theme \"dark\"|\"cyber\"|\"glass\"|\"light\"|\"nord\"", "Switches active GUI theme setting default canvas background and palette colors.", "ui_theme \"cyber\""),
    ("ui_ease", "ui_ease var start end t [style]", "Calculates animation easing interpolation across styles (linear, ease_in, ease_out, ease_in_out, bounce). Usable inline via ui_ease(start:end:t:style).", "ui_ease smooth_x 0 100 0.5 \"ease_out\""),
    ("ai_net_new", "ai_net_new \"name\" [layers] [activation]", "Initializes a feedforward neural network with Xavier initialization and configurable activation function (sigmoid, relu, tanh).", "ai_net_new \"xor_net\" [2, 4, 1] \"sigmoid\""),
    ("ai_net_train", "ai_net_train \"name\" inputs targets [epochs] [lr] [tit loss]", "Trains neural network on dataset using backpropagation and gradient descent, returning final mean squared error.", "ai_net_train \"xor_net\" [[0,0],[0,1],[1,0],[1,1]] [[0],[1],[1],[0]] 1000 0.5 tit loss"),
    ("ai_net_predict", "ai_net_predict \"name\" input tit output", "Computes neural network forward inference pass for given input feature vector.", "ai_net_predict \"xor_net\" [1, 0] tit prediction\nout prediction"),
    ("ai_net_classify", "ai_net_classify \"name\" input [threshold] tit class_idx", "Classifies input to highest probability class index (argmax) or binary threshold.", "ai_net_classify \"xor_net\" [1, 1] 0.5 tit class_id"),
    ("ai_net_save", "ai_net_save \"name\" \"path.json\"", "Serializes neural network architecture, weights, biases, and activation state to a JSON file.", "ai_net_save \"xor_net\" \"models/xor.json\""),
    ("ai_net_load", "ai_net_load \"name\" \"path.json\"", "Loads serialized neural network architecture and learned weights from a JSON file.", "ai_net_load \"restored_net\" \"models/xor.json\""),
    ("ai_agent_new", "ai_agent_new \"name\" [actions] [lr] [gamma] [epsilon]", "Creates a tabular Q-learning reinforcement learning agent with specified action space, learning rate, discount factor, and exploration rate.", "ai_agent_new \"bot\" [\"up\", \"down\", \"left\", \"right\"] 0.2 0.9 0.1"),
    ("ai_agent_act", "ai_agent_act \"name\" state tit action", "Queries reinforcement learning agent for action selection using epsilon-greedy policy.", "ai_agent_act \"bot\" \"room_1\" tit next_action"),
    ("ai_agent_reward", "ai_agent_reward \"name\" state action reward next_state", "Updates agent Q-value table using Bellman equation based on observed environment reward and transition.", "ai_agent_reward \"bot\" \"room_1\" \"right\" 10.0 \"room_2\""),
    ("ai_agent_save", "ai_agent_save \"name\" \"path.json\"", "Saves reinforcement learning agent learned Q-table policy and hyperparameters to JSON file.", "ai_agent_save \"bot\" \"models/agent.json\""),
    ("ai_agent_load", "ai_agent_load \"name\" \"path.json\"", "Loads reinforcement learning agent learned policy and Q-table from JSON file.", "ai_agent_load \"bot2\" \"models/agent.json\""),
    ("ai_tokenize", "ai_tokenize \"text string\" tit tokens", "Splits natural language text into a clean normalized list of lowercase word tokens.", "ai_tokenize \"Trappy Micro AI Engine v1.7\" tit words\nout words"),
    ("ai_embed", "ai_embed tokens vocab|dim tit vector", "Embeds word tokens into a dense numerical vector using feature hashing or vocabulary bag-of-words.", "ai_embed words 16 tit embedding_vector"),
    ("ai_sim", "ai_sim vec1 vec2 tit score", "Calculates cosine similarity between two embedding vectors, returning similarity score from -1.0 to 1.0.", "ai_sim vec_a vec_b tit similarity_score"),
    ("ai_ngram_train", "ai_ngram_train \"name\" \"corpus text\" [n]", "Trains probabilistic Markov n-gram text generation model on source text corpus.", "ai_ngram_train \"markov\" \"trappy is fast trappy is secure trappy is modern\" 2"),
    ("ai_ngram_gen", "ai_ngram_gen \"name\" \"seed\" length tit output", "Generates synthetic natural language text from trained Markov n-gram model starting from seed phrase.", "ai_ngram_gen \"markov\" \"trappy\" 6 tit generated_text"),
    ("ai_ui_net", "ai_ui_net \"name\" x:y w:h", "Visualizes neural network topology diagram directly on GUI canvas showing nodes, layers, and weight connections.", "ai_ui_net \"xor_net\" 50:50 250:180"),
    ("ai_ui_agent", "ai_ui_agent \"name\" x:y w:h", "Renders reinforcement learning agent status widget displaying top state Q-values and policy metrics.", "ai_ui_agent \"bot\" 320:50 250:180"),
    ("ai_ui_chat", "ai_ui_chat [user_msg] bot_msg x:y w:h", "Renders modern conversational chat bubble card with speech bubbles and AI avatar icon.", "ai_ui_chat \"Hello Assistant\" \"Ready to assist you.\" 50:250 400:150"),
    ("os_boot", "os_boot \"OSName\" \"Version\"", "Initializes and boots TrappyOS kernel, process table, virtual filesystem, memory manager, and security guard subsystems.", "os_boot \"TrappyOS\" \"1.7.0\""),
    ("os_shutdown", "os_shutdown", "Performs clean operating system shutdown, terminating all active processes and flushing virtual filesystems.", "os_shutdown"),
    ("os_panic", "os_panic \"reason\"", "Triggers kernel halt panic dump recording registers, current protection ring, and stack trace.", "os_panic \"Fatal filesystem corruption detected\""),
    ("os_proc_spawn", "os_proc_spawn \"name\" \"code\" tit pid", "Spawns and schedules a new sandboxed process running isolated Trappy userland bytecode.", "os_proc_spawn \"worker\" \"trst out 1 tren\" tit pid"),
    ("os_proc_kill", "os_proc_kill pid", "Terminates an active process by PID and reclaims allocated process memory table.", "os_proc_kill pid"),
    ("os_proc_list", "os_proc_list tit procs", "Returns list of active system processes including PID, name, protection ring, and execution state.", "os_proc_list tit process_table"),
    ("os_yield", "os_yield", "Yields the current CPU timeslice to the kernel scheduler for cooperative multitasking.", "os_yield"),
    ("os_ipc_send", "os_ipc_send target_pid:msg tit sent", "Sends an inter-process communication message to a process mailbox queue.", "os_ipc_send target_pid:\"DATA_READY\" tit sent"),
    ("os_ipc_recv", "os_ipc_recv tit msg", "Reads and consumes the next message from current process IPC mailbox.", "os_ipc_recv tit message"),
    ("os_vfs_mount", "os_vfs_mount \"/path\"", "Mounts a virtual filesystem directory hierarchy with path traversal guards.", "os_vfs_mount \"/storage/user\""),
    ("os_vfs_write", "os_vfs_write \"/path\" \"data\"", "Writes file data securely to the OS Virtual File System with permission checks.", "os_vfs_write \"/etc/hostname\" \"trappy-station\""),
    ("os_vfs_read", "os_vfs_read \"/path\" tit var", "Reads file data or virtual kernel proc status (/proc/version, /proc/uptime) from VFS.", "os_vfs_read \"/etc/hostname\" tit host"),
    ("os_vfs_list", "os_vfs_list \"/dir\" tit files", "Lists directory entries inside the specified virtual filesystem folder.", "os_vfs_list \"/bin\" tit binaries"),
    ("os_vfs_del", "os_vfs_del \"/path\"", "Deletes a virtual file or directory within VFS storage.", "os_vfs_del \"/tmp/cache.dat\""),
    ("os_vfs_stat", "os_vfs_stat \"/path\" tit info", "Returns file metadata dictionary including size, permissions, and creation timestamp.", "os_vfs_stat \"/etc/hostname\" tit meta"),
    ("os_app_download", "os_app_download \"url\" \"app_id\" tit status", "Downloads and verifies a Trappy application from network repository into /apps.", "os_app_download \"https://repo.trappy.org/calc.trappy\" \"calc\" tit status"),
    ("os_app_install", "os_app_install \"app_id\" \"source_code\" tit status", "Registers and compiles an application into the OS application manifest table.", "os_app_install \"notes\" \"trst out 1 tren\" tit status"),
    ("os_app_launch", "os_app_launch \"app_id\" tit pid", "Launches installed application in isolated Ring 3 Userland sandbox.", "os_app_launch \"calc\" tit pid"),
    ("os_app_list", "os_app_list tit apps", "Returns list of all registered applications in the system manifest.", "os_app_list tit installed_apps"),
    ("os_app_kill", "os_app_kill \"app_id\"", "Terminates all running instances of an application.", "os_app_kill \"calc\""),
    ("os_app_uninstall", "os_app_uninstall \"app_id\"", "Uninstalls application package and purges its sandboxed app storage directory.", "os_app_uninstall \"calc\""),
    ("os_screen_mode", "os_screen_mode \"phone\"|\"computer\" \"portrait\"|\"landscape\"", "Configures the OS target device frame, aspect ratio, and resolution (smartphone vs desktop workstation).", "os_screen_mode \"phone\" \"portrait\""),
    ("os_hw_info", "os_hw_info tit info", "Inspects virtual hardware specifications: CPU cores, RAM, and virtual SoC architecture.", "os_hw_info tit hw"),
    ("os_battery_info", "os_battery_info tit info", "Queries battery charge level percentage and power charging status.", "os_battery_info tit power"),
    ("os_touch_event", "os_touch_event x:y \"tap\"|\"swipe\" tit handled", "Routes mobile touchscreen gesture inputs through OS event compositor.", "os_touch_event 150:200 \"tap\" tit handled"),
    ("os_ui_window", "os_ui_window \"Title\" x:y:w:h tit win_id", "Registers a composited window container with Mac-style traffic lights or mobile bezel frame.", "os_ui_window \"Terminal\" 50:50:400:250 tit win"),
    ("os_ui_taskbar", "os_ui_taskbar \"menu_title\"", "Configures the OS desktop system taskbar or mobile dock launcher bar.", "os_ui_taskbar \"TrappyOS Start\""),
    ("os_ui_notify", "os_ui_notify \"Title\" \"Message\" [level]", "Dispatches system notification banner to the OS notification center.", "os_ui_notify \"Security\" \"System integrity verified\" \"info\""),
    ("os_ui_render", "os_ui_render [\"phone\"|\"desktop\"]", "Renders complete composite OS shell interface, dynamic island/bezel, taskbar, active windows, and notifications.", "os_ui_render \"desktop\""),
    ("os_setting_set", "os_setting_set \"key\" \"value\"", "Stores persistent configuration setting in system settings database.", "os_setting_set \"display.dark_mode\" \"1\""),
    ("os_setting_get", "os_setting_get \"key\" tit val", "Retrieves system configuration setting value.", "os_setting_get \"display.dark_mode\" tit is_dark"),
    ("os_setting_dump", "os_setting_dump tit dict", "Dumps all system configuration settings to a dictionary.", "os_setting_dump tit all_settings"),
    ("os_ring_set", "os_ring_set ring_number", "Transitions privilege protection ring (Ring 0 Kernel, Ring 1 Drivers, Ring 2 Services, Ring 3 User Apps) with elevation protection.", "os_ring_set 3"),
    ("os_ring_get", "os_ring_get tit ring", "Queries current active privilege protection ring of executing process.", "os_ring_get tit current_ring"),
    ("os_perm_grant", "os_perm_grant \"app_id\" \"PERMISSION\"", "Grants granular capability permission (NETWORK, STORAGE, UI, AUDIO, MEMORY) to sandboxed application.", "os_perm_grant \"calc\" \"UI\""),
    ("os_perm_revoke", "os_perm_revoke \"app_id\" \"PERMISSION\"", "Revokes capability permission from sandboxed application.", "os_perm_revoke \"calc\" \"NETWORK\""),
    ("os_perm_check", "os_perm_check \"app_id\" \"PERMISSION\" tit allowed", "Validates whether sandboxed application holds required permission.", "os_perm_check \"calc\" \"STORAGE\" tit allowed"),
    ("os_firewall_rule", "os_firewall_rule \"ALLOW\"|\"BLOCK\" \"pattern\"", "Adds inbound/outbound domain and IP filtering rule to kernel firewall.", "os_firewall_rule \"BLOCK\" \"*.malicious.com\""),
    ("os_defense_hook", "os_defense_hook \"event\" \"action\"", "Attaches automated kernel defense action (panic, isolate, block) to security event alarms.", "os_defense_hook \"privilege_violation\" \"isolate\""),
    ("os_block_list", "os_block_list tit list", "Retrieves list of active firewall blocked hosts, IPs, and suspicious signatures.", "os_block_list tit blocked_hosts"),
    ("os_integrity_seal", "os_integrity_seal", "Computes SHA-256 cryptographic tamper seal across all system binaries and VFS components.", "os_integrity_seal"),
    ("os_integrity_verify", "os_integrity_verify tit report", "Audits system VFS files against cryptographic seal, detecting any unauthorized modifications.", "os_integrity_verify tit audit_report"),
    ("os_jailbreak_check", "os_jailbreak_check tit report", "Scans kernel state for privilege ring escalations, hook tampering, and rootkit jailbreak indicators.", "os_jailbreak_check tit jailbreak_report"),
    ("os_jailbreak_defend", "os_jailbreak_defend \"panic\"|\"sandbox\"|\"isolate\"", "Sets active kernel defense strategy triggered upon jailbreak detection.", "os_jailbreak_defend \"isolate\""),
    ("os_exploit_guard", "os_exploit_guard \"guard_type\" 1", "Enables hardware-level exploit guards: canary buffer bounds checking, nx_memory execution filters, and syscall filtering.", "os_exploit_guard \"canary\" 1"),
    ("os_exploit_status", "os_exploit_status tit status", "Returns diagnostic summary of active exploit guards and logged violation events.", "os_exploit_status tit guard_status"),
    ("os_ai_anomaly_check", "os_ai_anomaly_check [metrics] tit report", "Employs kernel AI engine to analyze real-time CPU, RAM, and syscall telemetry to detect intrusions and anomalies.", "os_ai_anomaly_check [10.0, 20.0, 5.0] tit anomaly_report"),
    ("os_ai_assistant", "os_ai_assistant \"prompt\" tit response", "Embedded intelligent OS assistant for real-time natural language system diagnosis, status queries, and security remediation.", "os_ai_assistant \"diagnose system health\" tit response"),
]

class TrappyIDE:
    def __init__(self, root):
        self.root = root
        self.root.title("Trappy IDE - Official Code Studio (v1.7.0)")
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
            text="Ready | Trappy v1.7.0 | Discord: discord.gg/3chDfAPE9H | Press F1 for Docs, F5 to Run",
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
        self.manual_win.geometry("840x620")
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
