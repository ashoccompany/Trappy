# Trappy Programming Language

Trappy is an independent, universal programming language built from scratch. Its guiding design law is simple: **simple needs to be simple**. Beginners can create working games, apps, and network clients immediately, while advanced creators can connect almost anything across the web and local systems without pages of configuration or third-party dependencies.

Current version: **v1.5.0 (OS Development Engine & Advanced Defenses Release)**

---

## Official Community & Source Links

* **Discord (Official Headquarters):** https://discord.gg/3chDfAPE9H
* **GitHub:** https://github.com/ashoccompany/Trappy
* **X (Twitter):** https://x.com/tr4ppyai

Discord is the central community hub for Trappy. Join to share packages, get instant help, showcase games, and collaborate with creators.

---

## Design Principles

* **Simple Needs to Be Simple:** 3D perspective shapes, memory buffers, Discord webhooks, and object manifests do not require dozens of configuration lines. Sending a live Discord notification takes one line (`discord_webhook url:msg tit status`). Rendering a 3D wireframe cube takes one line (`cube3d 300:225:0 140 20:30 cyan`).
* **Noise-Free Boundaries:** Explicit program and function boundaries using `trst` (start) and `tren` (end) instead of curly braces or strict indentation rules.
* **Semantic Function Prefixes:** Prefixes identify function domains directly in source code: `fmh` for math, `ftxt` for strings, `f3d` for 3D graphics, `fos` for OS and memory, `fcli` for networking clients, `fui` for interface actions, and `fdel` for variable cleanup.
* **Batteries Included & Budget Hardware Optimized:** 3D perspective rendering, 2D arcade canvas, audio synthesis, file I/O, Discord webhooks, and package management are built directly into the runtime without requiring external dependencies. Memory usage stays under 30 MB idle, and `fps calm` drops refresh rates when unfocused to save up to 90% CPU on low-end laptops.

---

## Key Features in v1.0.0

* **Built-in Offline Docs Browser (IDE):** Press **`F1`** inside `TrappyIDE.exe` to open an offline searchable command reference with 1-click example insertion into your code.
* **Discord Webhooks & Online Integration:** Native 1-line Discord channel notifications (`discord_webhook`) and JSON serialization (`json_dump`, `json_parse`).
* **Offline Virtual Loopback Bus:** Test networked multiplayer games and distributed clients offline without needing active internet or open router ports (`cli_connect "loopback":port`).
* **Dynamic Dictionaries & Key-Value Maps:** Fast hash maps for game state and inventory management (`dict`, `dset`, `dget`, `dkeys`).
* **List Indexing & Operations:** Fast array manipulation with zero boilerplate (`lget`, `lset`, `llen`, `lpush`, `lpop`).
* **Universal Offline File I/O Suite:** Safe local storage for savegames, logs, and level configs (`file_write`, `file_read`, `file_append`, `file_exists`, `file_delete`, `dir_list`).
* **3D Multi-Shape Graphics Engine:** Native perspective wireframe rendering for cubes (`cube3d`), celestial spheres with orthogonal axis rings (`sphere3d`), 4-sided pyramids (`pyramid3d`), and lines (`line3d`).
* **Physics, Collision & Vector Math:** AABB 2D bounding-box collision detection (`box_hit`), vector math (`vec_add`, `vec_mag`), Euclidean distance (`dist`), and clamping (`clamp`).
* **Chiptune Audio Synthesizer:** Multi-waveform software synthesizer (`synth "square":440:150`) running directly on native hardware audio buffers.
* **Quick Code Assist:** Real-time grey ghost autocomplete in `TrappyIDE.exe`. Type keyword prefixes and press Tab or Right Arrow to accept.
* **Dedicated Standalone Studio:** Ships with `TrappyIDE.exe`, a standalone zero-dependency code editor with syntax highlighting, an integrated terminal, one-click execution (F5), debugging (F6), and direct Discord access.

---

## OS Development Suite in v1.5.0

Trappy v1.5 turns Trappy into a complete Operating System development platform, enabling developers to build, sandbox, defend, and run simulated or visual operating systems on computers and smartphones:

* **Kernel Lifecycle & Process Table:** Boot kernels (`os_boot`), trigger diagnostic kernel panics (`os_panic`), spawn isolated virtual processes (`os_proc_spawn`), terminate tasks (`os_proc_kill`), query the process table (`os_proc_list`), yield the CPU (`os_yield`), and stream messages across channels (`os_ipc_send`, `os_ipc_recv`).
* **Virtual File System (VFS):** Built-in POSIX hierarchical storage with path traversal protection (`os_vfs_mount`, `os_vfs_write`, `os_vfs_read`, `os_vfs_list`, `os_vfs_del`, `os_vfs_stat`) and dynamic `/proc` mounts.
* **Target Device Form Factors (Phone vs Computer):** Switch device geometry, display orientation, and hardware metrics with `os_screen_mode "phone" "portrait"` (380x720) or `os_screen_mode "computer" "landscape"` (1024x700). Access simulated SoC cores, RAM, battery percentage (`os_battery_info`), and touch events (`os_touch_event`).
* **App Store & Sandboxing:** Download apps over verified HTTP/HTTPS (`os_app_download`), verify syntax and install (`os_app_install`), and launch applications in an isolated Ring 3 Userland environment (`os_app_launch`).
* **Custom Anti-Jailbreak Defenses:** Cryptographic SHA-256 integrity seals (`os_integrity_seal`), seal verification (`os_integrity_verify`), automated scanning for root elevation attempts (`os_jailbreak_check`), and defensive responses (`os_jailbreak_defend`).
* **Custom Anti-Exploit Defenses:** Hardware-emulated memory buffer canary guards (`os_exploit_guard "canary" 1`), NX data buffer protection, and automated interception of out-of-bounds writes and unauthorized shell executions (`sys_exec`).
* **Custom Defenses & Permissions:** Granular permission system (`os_perm_grant`, `os_perm_revoke`, `os_perm_check`) for `NETWORK`, `STORAGE`, `UI`, and `AUDIO`, coupled with per-app network firewall policies (`os_firewall_rule`) and threat blocklists (`os_block_list`).
* **UI Compositor & Shell:** Desktop/mobile window containers (`os_ui_window`), taskbar / dock (`os_ui_taskbar`), push notification banners (`os_ui_notify`), and unified display rendering (`os_ui_render`).

---

## Code Examples

### 1. 1-Line Discord Notification & Offline Save System

```trappy
trst
    dict tit profile
    dset profile:"hero":"TrappyKnight"
    dset profile:"gold":1200
    dset profile:"level":8

    json_dump profile tit save_data
    file_write "savegame.dat":save_data

    txt "https://discord.com/api/webhooks/your_webhook_url" tit hook_url
    txt "Player TrappyKnight reached Level 8!" tit announcement
    discord_webhook hook_url:announcement tit http_status
    gan "Discord Webhook HTTP Status:"
    gan http_status
tren
```

### 2. 3D Multi-Shape Rotating Scene

```trappy
trst
    cwin "Trappy 3D Multi-Shape Engine" 700:500 main
    sbgwin "Trappy 3D Multi-Shape Engine" black
    fps calm

    mh 20 eq rot_x
    mh 30 eq rot_y

    gloop
        label "TRAPPY 3D MULTI-SHAPE ENGINE" 350:25 cyan
        label "CONTROLS: [W/S] Pitch | [A/D] Yaw" 350:470 yellow

        mh rot_y + 1 eq rot_y

        cube3d 180:250:0 90 rot_x:rot_y cyan
        sphere3d 350:250:0 48 rot_x:rot_y green
        pyramid3d 520:250:0 100 rot_x:rot_y yellow

        ifr key "W" trg then mh rot_x - 3 eq rot_x
        ifr key "S" trg then mh rot_x + 3 eq rot_x
        ifr key "A" trg then mh rot_y - 3 eq rot_y
        ifr key "D" trg then mh rot_y + 3 eq rot_y
    tren
tren
```

### 3. Offline Loopback Client / Server Testing

```trappy
trst
    add_obj "sync_pkt"
        event: "PLAYER_MOVE"
        x: 320
        y: 240
    tren

    pack_data sync_pkt tit outgoing_pkt

    cli_connect "loopback":8080 tit client
    cli_send client:outgoing_pkt
    cli_recv client tit received_pkt
    gan "Received on Loopback Bus:"
    gan received_pkt
    cli_close client
tren
```

### 4. 2D Arcade Game Loop with Collision Check

```trappy
trst
    cwin "Trappy Game" 600:400 main
    sbgwin "Trappy Game" black
    fps calm

    mh 300 eq player_x
    mh 200 eq player_y

    gloop
        circ player_x:player_y 16 cyan
        regle 150:180 50:50 red

        box_hit player_x:player_y:16:16 150:180:50:50 tit is_hit
        ifr is_hit sm 1
            label "COLLISION DETECTED!" 300:100 yellow
        tren

        ifr key "W" trg then mh player_y - 4 eq player_y
        ifr key "S" trg then mh player_y + 4 eq player_y
        ifr key "A" trg then mh player_x - 4 eq player_x
        ifr key "D" trg then mh player_x + 4 eq player_x
    tren
tren
```

### 5. Complete OS Boot Sequence & Custom Defenses (v1.5.0)

```trappy
trst
    // Boot the kernel
    os_boot "TrappyOS" "1.5.0"

    // Set hardware screen mode (phone or computer)
    os_screen_mode "phone" "portrait"

    // Set system files in Virtual File System (VFS)
    os_vfs_write "/etc/hostname" "trappy-phone-01"
    os_vfs_read "/etc/hostname" tit host_name

    // Configure Anti-Exploit Canary Guards & Anti-Jailbreak Sealing
    os_exploit_guard "canary" 1
    os_exploit_guard "nx_memory" 1
    os_jailbreak_defend "panic"

    os_integrity_seal "/etc/hostname" "security_passphrase"
    os_jailbreak_check tit report

    // Install and Sandbox a Userland App in Ring 3
    os_perm_grant "calculator" "UI"
    os_app_install "calculator" "trst\n out 'Calculator Running'\ntren" tit install_res
    os_app_launch "calculator" tit calc_pid

    // Dispatch Window and Render Compositor
    os_ui_window "Calculator" 20 60 340 500 tit win1
    os_ui_taskbar "bottom" "#18181b"
    os_ui_notify "System Online" "TrappyOS v1.5 is secured." "info"
    os_ui_render
tren
```

---

## Package Management and Community Hub (TPM)

Trappy includes its own package manager (`tpm`) with offline caching support:

```
tpm search [keyword]                Search for community packages
tpm install <package_name_or_url>   Install a community package (cached locally)
tpm publish <file.trappy> [author]  Publish code to the community hub
tpm discord                         Show official Discord community invite
tpm list                            List installed packages
```

---

## Tooling

* **TrappyIDE.exe**: Standalone desktop editor with Quick Code Assist, F1 Documentation Browser, integrated terminal, one-click execution (F5), debugging (F6), and community links.
* **trpexec**: Command-line runner for executing `.trappy` files.
  ```
  trpexec script.trappy
  ```
* **tpm**: Command-line tool for package management.

---

## Project Status and Roadmap

* **v0.8.5:** Core runtime, object manifests, 2D game canvas, HTTP client, and TrappyIDE studio.
* **v0.9.0:** Structured packet engine (`pack`/`unpack`), non-blocking client/server sockets, and the TPM Community Hub.
* **v0.9.5:** Quick Code Assist autocomplete, 3D wireframe perspective, OS memory buffers, and extended math/physics library.
* **v1.0.0 (Global Release):** Official global launch. Discord webhooks, offline loopback bus, dynamic dictionaries, list indexing, universal file I/O, 3D multi-shapes (sphere, pyramid), AABB collision, chiptune synthesizer, F1 in-IDE documentation browser, and ultra-budget hardware frame throttling.
* **v1.1.0 (Advanced Patch):** Major architectural refactor and benchmark optimization. Decoupled 700+ line parser into modular O(1) dispatchers, added native float literals (`3.14`), introduced first-class `else` keyword syntax, optimized tokenizer slicing from O(n^2) to O(n), zero-latency non-blocking socket polling, and added an automated 24-test suite (`tests/test_trappy.py`).
* **v1.5.0 (OS Development Engine & Advanced Defenses Release):**
  * **Dedicated OS Architecture:** Native kernel lifecycle (`os_boot`, `os_shutdown`, `os_panic`), process table with ring privileges, cooperative multitasking scheduler (`os_yield`), and inter-process communication channels (`os_ipc_send`, `os_ipc_recv`).
  * **Virtual File System (VFS):** POSIX virtual storage hierarchy (`/sys`, `/bin`, `/etc`, `/apps`, `/storage`, `/proc`) with path traversal guards.
  * **Device Targets (Phone vs Computer):** Hardware Abstraction Layer running on `phone` (380x720) or `computer` (1024x700), with virtual battery management, SoC hardware metrics, and touch event handling.
  * **App Store & Sandboxing:** Secure application downloader (`os_app_download`), package registration (`os_app_install`), and execution inside a Ring 3 Userland sandbox (`os_app_launch`).
  * **Custom Anti-Jailbreak Defenses:** Cryptographic SHA-256 integrity sealing (`os_integrity_seal`), automated root escalation scans (`os_jailbreak_check`), and defense triggers (`os_jailbreak_defend`).
  * **Custom Anti-Exploit Defenses:** Hardware-emulated memory canary guards (`os_exploit_guard "canary" 1`), NX data buffer protection, and command execution filtering blocking `sys_exec` for user processes.
  * **Custom Permissions & Firewall:** Granular permissions (`os_perm_grant`, `os_perm_check`) for NETWORK, STORAGE, UI, and AUDIO, network firewalls (`os_firewall_rule`), and malicious threat blocklists (`os_block_list`).
  * **UI Compositor:** Managed window containers (`os_ui_window`), taskbar / status bar (`os_ui_taskbar`), toast notification banners (`os_ui_notify`), and unified display rendering (`os_ui_render`).
  * **54 Automated Tests:** Comprehensive unit and security regression test suite passing at 100%.
* **v1.15.0 (Bootstrapping Foundation & Stability Release):**
  * **Self-Hosting Bootstrapping for v2:** Added pure-Trappy self-hosting lexer prototype (`bootstrap/trappy_bootstrap.trappy`) proving Trappy can tokenize itself.
  * **Full String Suite:** Added `slen`, `sget`, `ssub`, `ssplit`, `sjoin`, `sfind`, `sreplace`, `strim`, `slower`, `supper`, `ord`, `chr`, `is_digit`, `is_alpha`.
  * **Type Introspection & Reflection:** Added `type_of`, `to_str`, `to_num`, `to_float`.
  * **Universal Functions:** Added first-class `fn` and `func` declaration keywords with `return` statement support and expression-level calling.
  * **Modern Control Flow:** Added `while <cond> ... tren`, `break`, `continue` / `cnt`, `swhile`.
  * **Exception Handling:** Added `try ... catch <err> ... tren` native exception recovery.
  * **Collection Ergonomics:** Added `lcontains`, `linsert`, `lslice`, `dhas`, `ddel`.
  * **32-Test Automated Suite:** Expanded automated test suite with 100% pass rate.
* **v2.0.0 (Upcoming Self-Hosting Milestone):** Complete self-hosting bootstrap compiler where Trappy compiles and interprets itself natively without requiring the Python host runtime.

---

## Documentation

For the complete command reference guide, see [MANUAL.md](MANUAL.md).

---

## License

Trappy is an open source programming language project.
