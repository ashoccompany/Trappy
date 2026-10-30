# Trappy Programming Language

Trappy is an independent, universal programming language built from scratch. Its guiding design law is simple: **simple needs to be simple**. Beginners can create working games, apps, and network clients immediately, while advanced creators can connect almost anything across the web and local systems without pages of configuration or third-party dependencies.

Current version: **v1.1.0 (Advanced Performance & Architecture Patch)**

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

---

## Documentation

For the complete command reference guide, see [MANUAL.md](MANUAL.md).

---

## License

Trappy is an open source programming language project.
