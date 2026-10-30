# Trappy Programming Language - Official Reference Manual (v1.0.0 Global Release)

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

Comparisons: `grt` (>), `lss` (<), `sm` (==).

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
