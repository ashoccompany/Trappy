# Trappy Programming Language - Official Reference Manual (v1.7.0 Release)

Copyright (c) Trappy Language Project. All rights reserved.  
Official File Extension: `.trappy`  
Execution Command: `trpexec <file.trappy>`  
Package Manager: `tpm <command>`  
Standalone Studio: `TrappyIDE.exe`  

### Official Community & Source Links
* **Discord (Main Community Headquarters):** https://discord.gg/3chDfAPE9H
* **GitHub:** https://github.com/ashoccompany/Trappy
* **X (Twitter):** https://x.com/tr4ppyai

---

## Table of Contents
1. [What is Trappy?](#1-what-is-trappy)
2. [Help Anytime Everywhere & Discord Community](#2-help-anytime-everywhere--discord-community)
3. [How to Run Trappy & Trappy IDE](#3-how-to-run-trappy--trappy-ide)
4. [Discord Webhooks & Universal Connectivity](#4-discord-webhooks--universal-connectivity)
5. [Dictionaries & Key-Value Storage](#5-dictionaries--key-value-storage)
6. [Lists & Array Indexing](#6-lists--array-indexing)
7. [Universal Offline File I/O](#7-universal-offline-file-io)
8. [Packets & Networking with Offline Loopback](#8-packets--networking-with-offline-loopback)
9. [Trappy Community Hub & Package Manager (TPM)](#9-trappy-community-hub--package-manager-tpm)
10. [Universal Web & APIs](#10-universal-web--apis)
11. [Mathematics, Algebra & Physics](#11-mathematics-algebra--physics)
12. [3D Multi-Shape Wireframe Engine](#12-3d-multi-shape-wireframe-engine)
13. [OS & Low-Level Memory Primitives](#13-os--low-level-memory-primitives)
14. [2D Canvas Game Engine & Graphics](#14-2d-canvas-game-engine--graphics)
15. [Sound & Chiptune Audio Synthesizer](#15-sound--chiptune-audio-synthesizer)
16. [Declarations & Object Manifests](#16-declarations--object-manifests)
17. [Conditions & Logic](#17-conditions--logic)
18. [Loops & Repetition](#18-loops--repetition)
19. [Function Families](#19-function-families)
20. [Complete Example Programs](#20-complete-example-programs)
21. [Self-Hosting Bootstrapping & The Road to v2](#21-self-hosting-bootstrapping--the-road-to-v2)
22. [Full String Processing & Reflection Suite](#22-full-string-processing--reflection-suite)
23. [Modern Control Flow & Error Handling](#23-modern-control-flow--error-handling)
24. [OS Development & Security Architecture](#24-os-development--security-architecture)
25. [Modern UI/GUI Suite](#25-modern-uigui-suite)
26. [Micro-AI Development Engine](#26-micro-ai-development-engine)

---

## 1. What is Trappy?

Trappy is an expressive, universal programming language built from scratch to make software, 2D/3D games, distributed network clients, and offline tools accessible to everyone.

**Guiding Law:** Simple needs to be simple.

### Ultra-Budget Hardware Optimization
* **Memory Footprint:** Under 30 MB idle RAM.
* **Focus Sensing (`fps calm`):** Automatically drops refresh rates to 15 FPS when windows lose focus or are minimized, saving up to 90% CPU on budget laptops (Intel Celeron, Atom, 2GB RAM).
* **Offline Virtual Loopback:** Test multiplayer and distributed networking without open ports or network adapters.

---

## 2. Help Anytime Everywhere & Discord Community

Discord is the central community headquarters for all things Trappy:
* **Join Discord:** https://discord.gg/3chDfAPE9H
* Ask questions, showcase games, report ideas, and install community packages.

### Getting Help
1. **Inside `TrappyIDE.exe`:** Press `F1` to open the Built-in Offline Documentation Browser with real-time command search and 1-click example insertion.
2. **Quick Code Assist:** Inline grey ghost text suggests completions as you type. Press `Tab` or `Right Arrow` to commit.
3. **On GitHub:** Full documentation and releases at https://github.com/ashoccompany/Trappy
4. **On X:** Follow @tr4ppyai for syntax tips and release announcements.

---

## 3. How to Run Trappy & Trappy IDE

### Method 1: Using Standalone Studio (`TrappyIDE.exe`)
Double-click `TrappyIDE.exe`:
* Press `F1`: Built-in offline command documentation.
* Click `[Discord Community]`: Direct access to official Discord.
* Press `F5`: One-click execution.
* Press `F6`: Fast AST syntax verification.
* Quick Code Assist: Automatic keyword completion.

### Method 2: Using Terminal (`trpexec`)
```bash
trpexec script.trappy
```

---

## 4. Discord Webhooks & Universal Connectivity

### 1-Line Discord Webhook
```trappy
txt "https://discord.com/api/webhooks/your_webhook" tit hook_url
txt "Player reached Level 10!" tit msg
discord_webhook hook_url:msg tit status
gan status
```

### Native JSON Serialization
```trappy
dict tit profile
dset profile:"score":5000
json_dump profile tit json_text
gan json_text

json_parse json_text tit restored_profile
dget restored_profile:"score" tit score_val
gan score_val
```

### Streaming WebSockets
```trappy
ws_connect "ws://127.0.0.1:8080" tit stream
ws_send stream:"Hello"
ws_recv stream tit incoming
ws_close stream
```

---

## 5. Dictionaries & Key-Value Storage

```trappy
dict tit inventory
dset inventory:"gold":500
dset inventory:"weapon":"Excalibur"

dget inventory:"gold" tit player_gold
gan player_gold

dkeys inventory tit all_keys
gan all_keys
```

---

## 6. Lists & Array Indexing

```trappy
lst 10 | 20 | 30 eq scores
lget scores:0 tit first_score
lset scores:1:99
lpush scores:50
llen scores tit count
lpop scores tit last_val
```

---

## 7. Universal Offline File I/O

Safe sandboxed local file storage:
```trappy
file_write "save.dat":"level=5;coins=250"
file_exists "save.dat" tit exists_flag
file_read "save.dat" tit content
file_append "log.txt":"Session logged\n"
file_delete "temp.dat"
dir_list "." tit files
```

---

## 8. Packets & Networking with Offline Loopback

### Packet Serialization
```trappy
add_obj "sync_pkt"
    id: 101
    x: 250
    y: 180
tren
pack_data sync_pkt tit stream_pkt
unpack_data stream_pkt tit restored
```

### Offline Resilient Loopback
```trappy
cli_connect "loopback":8080 tit client
cli_send client:stream_pkt
cli_recv client tit reply
cli_close client
```

### Live Sockets
```trappy
cli_connect "127.0.0.1":8080 tit client
srv_listen 8080 tit server
srv_accept server tit incoming_conn
```

---

## 9. Trappy Community Hub & Package Manager (TPM)

* `tpm search [keyword]` - Search community packages
* `tpm install <name_or_url>` - Install package (cached locally in `/packages/cache`)
* `tpm publish <file.trappy> [author]` - Publish package to community hub
* `tpm discord` - Display Discord invite
* `tpm list` - List installed packages

---

## 10. Universal Web & APIs

```trappy
http_get "https://api.github.com/zen" tit quote
gan quote

http_post "https://httpbin.org/post":payload tit response
download "https://example.com/asset.png" into "asset.png"
```

---

## 11. Mathematics, Algebra & Physics

```trappy
mh 10 + 5 eq total
mh sqrt 144 eq root
mh pow 2:8 eq power
mh abs -42 eq absolute
mh clamp val:0:100 eq bounded
mh sin 30 eq s
mh cos 60 eq c
mh rnd 1:100 eq roll
```

### 2D Physics & Collision
```trappy
box_hit x1:y1:w1:h1 x2:y2:w2:h2 tit is_hit

vec_add x1:y1 x2:y2 tit sum_vector
vec_mag x:y tit length
```

---

## 12. 3D Multi-Shape Wireframe Engine

### 3D Cube
```trappy
cube3d x:y:z size rx:ry color
cube3d 300:225:0 140 20:30 cyan
```

### 3D Celestial Sphere (3 Orthogonal Axis Rings)
```trappy
sphere3d x:y:z radius rx:ry color
sphere3d 350:250:0 60 20:30 green
```

### 3D Pyramid (4-Sided with Apex)
```trappy
pyramid3d x:y:z size rx:ry color
pyramid3d 500:250:0 100 20:30 yellow
```

### 3D Line
```trappy
line3d x1:y1:z1 x2:y2:z2 rx:ry color
```

---

## 13. OS & Low-Level Memory Primitives

```trappy
mem_alloc 64 tit buffer_id
mem_write buffer_id:0:65
mem_read buffer_id:0 tit val
sys_env "PATH" tit sys_path
sys_exec "echo Hello" tit output
```

---

## 14. 2D Canvas Game Engine & Graphics

```trappy
cwin "Trappy Game" 600:400 main
sbgwin "Trappy Game" black
fps calm

gloop
    circ player.x:player.y 16 cyan
    regle 150:180 50:50 red
    ifr key "W" trg then mh player.y - 4 eq player.y
tren
```

---

## 15. Sound & Chiptune Audio Synthesizer

```trappy
synth "square":440:150
beep 1000:80
play "sound.wav"
```

---

## 16. Declarations & Object Manifests

```trappy
add_var "score"
add_obj "player"
    x: 100
    y: 200
    hp: 100
tren
mh player.hp - 10 eq player.hp
```

---

## 17. Conditions & Logic

```trappy
ifr score grt 50
    gan "High score!"
then
    gan "Try again!"
tren
```

Comparisons: `>`, `<`, `==`, `!=`, `>=`, `<=`, `grt`, `lss`, `sm`, `eq`.
Both `else` (standard in v1.1) and `then` (legacy) are fully supported for the alternative branch.

---

## 18. Loops & Repetition

```trappy
rep 5
    gan "Looping"
tren

each item in list_var
    gan item
tren
```

---

## 19. Function Families

* `fmh`   : Math function
* `ftxt`  : String function
* `f3d`   : 3D graphics function
* `fos`   : OS and system function
* `fweb`  : Web & API function
* `fcli`  : Client socket function
* `fdel`  : Cleanup function

---

## 20. Complete Example Programs

### Program 1: Discord Notification & Offline Save System
```trappy
trst
    dict tit save_data
    dset save_data:"player":"Hero_01"
    dset save_data:"high_score":14500

    json_dump save_data tit payload
    file_write "backup_score.dat":payload

    txt "https://discord.com/api/webhooks/your_hook_here" tit hook
    txt "Trappy v1.0 notification: New High Score Recorded!" tit alert
    discord_webhook hook:alert tit status
    gan "Discord response status:"
    gan status
tren
```

### Program 2: 3D Rotating Multi-Shape Scene
```trappy
trst
    cwin "3D World" 700:500 main
    sbgwin "3D World" black
    fps calm

    mh 20 eq rot_x
    mh 30 eq rot_y

    gloop
        mh rot_y + 1 eq rot_y
        cube3d 200:250:0 100 rot_x:rot_y cyan
        sphere3d 380:250:0 50 rot_x:rot_y green
        pyramid3d 540:250:0 110 rot_x:rot_y yellow
        ifr key "W" trg then mh rot_x - 3 eq rot_x
        ifr key "S" trg then mh rot_x + 3 eq rot_x
    tren
tren
```

---

## 21. Self-Hosting Bootstrapping & The Road to v2

Trappy v1.15 introduces the foundation for **compiler bootstrapping**. Bootstrapping is the milestone where a programming language is written in itself (self-hosting). 

The official bootstrapping module is located at `bootstrap/trappy_bootstrap.trappy`:
```trappy
# Trappy Self-Hosting Lexer (Bootstrapping Prototype for v2)
fn tokenize_trappy src
    dict tit res
    lst 0 eq token_types
    lst 0 eq token_values
    ...
    return res
tren
```

When Trappy v2 arrives, Trappy's runtime, parser, and code generator will be fully self-hosted, written in Trappy itself!

---

## 22. Full String Processing & Reflection Suite

Trappy v1.15 includes comprehensive string manipulation and runtime type reflection:

### String Suite
```trappy
txt "   Hello, Trappy!   " tit raw
strim raw tit trimmed
slen trimmed tit len_val
sget trimmed:0 tit first_char
ssub trimmed:0:5 tit greeting
slower greeting tit lower_greeting
supper greeting tit upper_greeting
sreplace trimmed:"Trappy":"Community" tit replaced
sfind trimmed:"Trappy" tit pos
ord "A" tit ascii_code
chr 65 tit char_out
is_digit "12345" tit is_num
is_alpha "my_var" tit is_ident
ssplit "10,20,30":"," tit list_items
sjoin list_items:" - " tit formatted_str
```

### Type Introspection & Safe Casting
```trappy
type_of 42 tit t1             # "number"
type_of "hello" tit t2        # "string"
type_of my_list tit t3        # "list"
type_of my_dict tit t4        # "dict"

to_str 999 tit str_val        # "999"
to_num "42" tit int_val       # 42
to_float "3.14" tit flt_val   # 3.14
```

---

## 23. Modern Control Flow & Error Handling

### While Loops & Universal Break/Continue
```trappy
mh 0 eq i
while i < 10
    mh i + 1 eq i
    ifr i == 5
        continue              # skip to next iteration
    tren
    ifr i == 8
        break                 # break out of while loop
    tren
    gan i
tren
```

### First-Class Functions (`fn` and `func`)
```trappy
fn calculate_area width:height
    mh width * height eq area
    return area
tren

calculate_area 20:30 tit room_area
gan room_area
```

### Safe Error Recovery (`try ... catch`)
```trappy
try
    mh 100 / 0 eq bad_math
catch err
    gan "Safely recovered from error:"
    gan err
tren
```

### Enhanced Collections
```trappy
# Lists
lcontains items:42 tit has_it
linsert items:0:999
lslice items:0:3 tit sub_list

# Dictionaries
dhas player:"score" tit has_score
ddel player:"temp_tag"
```


---

## 24. OS Development & Security Architecture

Trappy includes an operating system microkernel and security framework for building, testing, and defending operating systems:

```trappy
trst
    os_boot "AegisOS" "1.6.0"
    os_screen_mode "computer" "landscape"
    os_exploit_guard "canary" 1
    os_integrity_seal "/etc/hostname" "secret_salt"
    os_vfs_write "/storage/app.dat" "system state"
    os_jailbreak_check tit report
    os_shutdown
tren
```

* **Protection Rings:** Ring 0 (Kernel Init), Ring 1 (Device Drivers), Ring 2 (System Services), Ring 3 (Userland Applications).
* **Negative Ring & Underflow Protection:** Enforced rings 0..3; attempts to set negative rings or escalate privilege from userland are blocked.
* **Integrity Seals & Anti-Jailbreak:** SHA-256 integrity verification detects unauthorized component modifications.
* **Exploit Guards:** Emulated memory boundary canaries and execution filters block buffer overflows and shell injection.

---

## 25. Modern UI/GUI Suite

Trappy v1.6 introduces modern, fluid graphical interface components:

```trappy
trst
    cwin "Trappy Dashboard" 800:600 main
    ui_theme "cyber"
    card 50:50 750:550 16 "#0d1527" "#00ffcc"
    badge "SECURE NODE" 80:80 "secure"
    icon "shield" 80:120 28 "#00ffcc"
    progress 85 100 80:180 300:20 "#ff0055" "#1e293b"
    slider brightness 0 100 80:230 300 trg on_slide
    toggle network_online 80:280 trg on_net_toggle
    btn_modern "Reboot Kernel" 80:330 160:42 trg on_reboot "#ff0055"
    notify_toast "Security Status" "All subsystems nominal" "info"
    ui_ease anim_y 0 300 0.5 "ease_out"
tren
```

* `card`: Rounded container card with drop shadow and outline.
* `btn_modern`: Modern flat button with hover styling and callback trigger.
* `toggle`: Smooth pill switch track with circular knob.
* `progress`: Rounded progress bar with percentage readout.
* `badge`: Pill status badge with indicator dot.
* `slider`: Interactive value slider with tracking line and draggable thumb.
* `icon`: 15 canvas vector glyph icons without external images.
* `notify_toast`: Floating notification card with auto-dismiss.
* `ui_theme`: Active palette switching (dark, cyber, glass, light, nord).
* `ui_ease`: High-precision animation easing (linear, ease_in, ease_out, ease_in_out, bounce).


---

## 26. Micro-AI Development Engine

Trappy v1.7 introduces a complete, native Micro-AI development ecosystem built directly into the language runtime with zero external dependencies:

```trappy
trst
# 1. Neural Networks (Feedforward MLP with Backpropagation)
ai_net_new "classifier" [2, 4, 1] "sigmoid"
ai_net_train "classifier" [[0.0, 0.0], [0.0, 1.0], [1.0, 0.0], [1.0, 1.0]] [[0.0], [1.0], [1.0], [0.0]] 1500 1.0 tit loss
ai_net_predict "classifier" [1.0, 0.0] tit prediction
ai_net_classify "classifier" [1.0, 0.0] 0.5 tit class_idx
ai_net_save "classifier" "models/classifier.json"
ai_net_load "restored_model" "models/classifier.json"

# 2. Reinforcement Learning (Tabular Q-Learning)
ai_agent_new "agent" ["up", "down", "left", "right"] 0.2 0.9 0.1
ai_agent_act "agent" "state_a" tit next_action
ai_agent_reward "agent" "state_a" "right" 10.0 "state_b"
ai_agent_save "agent" "models/agent.json"
ai_agent_load "agent2" "models/agent.json"

# 3. NLP, Embeddings & Vector Cosine Similarity
ai_tokenize "Hello Trappy OS AI Engine!" tit tokens
ai_embed tokens 16 tit dense_vector
ai_sim dense_vector dense_vector tit similarity_score

# 4. Probabilistic Markov N-Gram Language Model
ai_ngram_train "text_gen" "trappy is fast trappy is secure trappy is modern" 2
ai_ngram_gen "text_gen" "trappy" 5 tit generated_sentence

# 5. Visual AI UI Components
ai_ui_net "classifier" 50:50 240:160
ai_ui_agent "agent" 310:50 240:160
ai_ui_chat "Hello Agent" "Ready to assist." 50:230 500:140

# 6. Kernel AI Integration & Diagnosis
os_ai_anomaly_check [10.0, 25.0, 4.0] tit anomaly_report
os_ai_assistant "diagnose system health" tit response
tren
```

* `ai_net_new`: Instantiates a feedforward neural network with Xavier initialization and configurable activation function (sigmoid, relu, tanh).
* `ai_net_train`: Trains the network via backpropagation and gradient descent, returning final mean squared error loss.
* `ai_net_predict`: Performs forward pass inference prediction on input feature vectors.
* `ai_net_classify`: Categorizes inputs using argmax class index or binary threshold.
* `ai_net_save` / `ai_net_load`: Serializes and restores neural network models to/from JSON.
* `ai_agent_new`: Instantiates a tabular Q-learning RL agent with configurable learning rate, discount factor, and epsilon exploration rate.
* `ai_agent_act`: Queries the RL agent for action selection using an epsilon-greedy policy.
* `ai_agent_reward`: Updates Bellman equation Q-values based on environment reward feedback and state transitions.
* `ai_agent_save` / `ai_agent_load`: Saves and restores RL agent Q-tables to/from disk.
* `ai_tokenize`: Normalizes and splits input text into lowercase alphanumeric tokens.
* `ai_embed`: Encodes token lists into dense numerical vectors via feature hashing or vocabulary bags-of-words.
* `ai_sim`: Computes cosine similarity between two embedding vectors (-1.0 to 1.0).
* `ai_ngram_train`: Learns probabilistic Markov transitions from a source text corpus.
* `ai_ngram_gen`: Generates synthetic sentences from learned Markov n-gram models starting from seed prompts.
* `ai_ui_net`: Draws interactive topology diagrams of neural net layers and synaptic weights on the canvas.
* `ai_ui_agent`: Renders active RL agent policies, Q-values, and state statistics.
* `ai_ui_chat`: Draws modern conversational chat cards with avatar icons and message bubbles.
* `os_ai_anomaly_check`: Kernel AI telemetry scanner detecting abnormal CPU, memory, and syscall spikes.
* `os_ai_assistant`: Interactive conversational assistant for kernel diagnosis, system queries, and security remediation.
* `[...]`: Native bracket syntax for multi-dimensional lists, matrices, layers, and coordinate arrays.
