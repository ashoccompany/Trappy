# Trappy Programming Language

Trappy is an independent, general-purpose programming language built from scratch. Its guiding design principle is simple: **simple needs to be simple**. Beginners can write working code immediately, while advanced tasks like 3D graphics, OS memory operations, networking packets, 2D games, and community package distribution stay clean and readable without pages of boilerplate.

Current version: **v0.9.5 (Beta)**

---

## Official Links

* GitHub: https://github.com/ashoccompany/Trappy
* Discord: https://discord.gg/WRTG3spWH
* X (Twitter): https://x.com/tr4ppyai

---

## Design Principles

* **Simple Needs to Be Simple:** 3D perspective graphics, memory buffers, networking, and object manifests should not require dozens of configuration lines. Rendering a 3D cube takes one line (`cube3d 300:225:0 140 20:30 cyan`). Packing data into a network stream takes one line (`pack player_sync tit pkt`).
* **Noise-Free Boundaries:** Explicit program and function boundaries using `trst` (start) and `tren` (end) instead of curly braces or strict whitespace rules.
* **Semantic Function Prefixes:** Prefixes identify function domains directly in source code: `fmh` for math, `ftxt` for strings, `f3d` for 3D graphics, `fos` for OS and memory, `fcli` for networking clients, `fui` for interface actions, and `fdel` for variable cleanup.
* **Batteries Included:** 3D perspective wireframe rendering, 2D graphics, windowing, audio synthesis, memory buffers, HTTP clients, and package management are built directly into the runtime without requiring external dependencies.

---

## Key Features

* **Quick Code Assist (IDE):** Built into `TrappyIDE.exe`. As you write code, grey ghost text predicts keywords and statements (e.g., `cw` suggests `in`). Press Tab or Right Arrow to accept completions instantly.
* **3D Wireframe Graphics Engine:** Native perspective projection pipeline inside canvas windows (`cube3d`, `line3d`) with full real-time yaw/pitch rotation.
* **Extended Math, Algebra and Physics:** Native calculations including `sqrt`, `pow`, `abs`, `dist` (Euclidean distance), `clamp`, `sin`, `cos`, and negative numbers.
* **OS and Low-Level Memory Buffers:** Safe byte buffer allocation and inspection (`mem_alloc`, `mem_write`, `mem_read`), environment variable access (`sys_env`), and system process execution (`sys_exec`).
* **Packets and Networking:** Serialize structured data into streamable packets with `pack_data` and restore them with `unpack_data`. Non-blocking client and server sockets (`cli_connect`, `cli_send`, `cli_recv`, `srv_listen`, `srv_accept`).
* **Community Hub and Package Manager (TPM):** Search, install, and publish community creations directly from the terminal or IDE using `tpm search`, `tpm install`, and `tpm publish`.
* **2D Canvas Game Engine:** Native window creation (`cwin`), primitive rendering (`circ`, `regle`, `line`), keyboard/mouse input, and frame pacing (`fps calm`) that matches display refresh rates to keep CPU usage low.
* **Universal Web Client:** Direct HTTP GET and POST requests (`http_get`, `http_post`) and file downloading (`download`).
* **Dedicated Studio:** Ships with `TrappyIDE.exe`, a standalone code editor with Quick Code Assist, syntax highlighting, an integrated terminal, one-click execution (F5), debugging (F6), and official community links.

---

## Code Examples

### 1. Real-Time 3D Rotating Cube

```trappy
trst
    cwin "Trappy 3D Engine" 600:450 main
    sbgwin "Trappy 3D Engine" black
    fps calm

    mh 300 eq cube_x
    mh 225 eq cube_y
    mh 0 eq cube_z
    mh 140 eq cube_size
    mh 20 eq rot_x
    mh 30 eq rot_y

    gloop
        label "TRAPPY 3D WIREFRAME ENGINE" 300:25 cyan
        label "ROTATE CUBE: [W / S] Pitch | [A / D] Yaw" 300:420 yellow

        # Continuous auto-spin
        mh rot_y + 1 eq rot_y

        # Draw 3D wireframe box with perspective projection
        cube3d cube_x:cube_y:cube_z cube_size rot_x:rot_y cyan

        # Keyboard 3D controls
        ifr key "W" trg then mh rot_x - 3 eq rot_x
        ifr key "S" trg then mh rot_x + 3 eq rot_x
        ifr key "A" trg then mh rot_y - 3 eq rot_y
        ifr key "D" trg then mh rot_y + 3 eq rot_y
    tren
tren
```

### 2. Math, Algebra and Physics Functions

```trappy
trst
    mh sqrt 144 eq root
    mh pow 2:8 eq power
    mh abs -42 eq absolute
    mh dist 0:0:30:40 eq distance
    mh clamp 150:0:100 eq clamped_val

    gan root          # 12.0
    gan power         # 256.0
    gan absolute      # 42.0
    gan distance      # 50.0
    gan clamped_val   # 100
tren
```

### 3. OS Memory Buffer Allocation

```trappy
trst
    mem_alloc 64 tit ram
    mem_write ram:0:84     # 'T'
    mem_write ram:1:82     # 'R'
    mem_write ram:2:65     # 'A'
    mem_write ram:3:80     # 'P'

    mem_read ram:0 tit b0
    mem_read ram:1 tit b1
    gan "Read bytes from memory block:"
    gan b0
    gan b1
tren
```

### 4. Packets and Client Networking

```trappy
trst
    add_obj "player_sync"
        id: 42
        x: 250
        y: 180
    tren

    # Pack object into a transmission stream
    pack_data player_sync tit packet_data
    gan packet_data

    # Connect client and send
    cli_connect "127.0.0.1":8080 tit client
    cli_send client:packet_data
    cli_recv client tit response
    cli_close client
tren
```

### 5. 2D Arcade Game Loop

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

        ifr key "W" trg then mh player_y - 4 eq player_y
        ifr key "S" trg then mh player_y + 4 eq player_y
        ifr key "A" trg then mh player_x - 4 eq player_x
        ifr key "D" trg then mh player_x + 4 eq player_x
    tren
tren
```

---

## Package Management and Community Hub (TPM)

Trappy includes its own package manager (`tpm`) so developers can share code, install community modules, and collaborate:

```
tpm search [keyword]                Search for community packages
tpm install <package_name_or_url>   Install a community package
tpm publish <file.trappy> [author]  Publish code to the community hub
tpm list                            List installed packages
```

---

## Tooling

* **TrappyIDE.exe**: Standalone desktop editor with Quick Code Assist, syntax highlighting, integrated terminal, one-click execution (F5), debugging (F6), and community links.
* **trpexec**: Command-line runner for executing `.trappy` files.
  ```
  trpexec script.trappy
  ```
* **tpm**: Command-line tool for package management.

---

## Project Status and Roadmap

Trappy is currently in beta development:

* **v0.8.5:** Core runtime, object manifests, 2D game canvas, HTTP client, and TrappyIDE studio.
* **v0.9.0:** Structured packet engine (`pack`/`unpack`), non-blocking client/server sockets, and the TPM Community Hub.
* **v0.9.5 (Current Beta):** Quick Code Assist autocomplete, 3D perspective wireframe engine, OS and memory buffers, extended math/physics library, official community links and watermarks.
* **v1.0.0:** First general stable release.

---

## License

Trappy is an open source programming language project.
