# Trappy Programming Language

Trappy is an independent, general-purpose programming language built from scratch. Its guiding design principle is simple: **simple needs to be simple**. Beginners should be able to write working code immediately, while advanced tasks like networking packets, 2D games, and community package distribution should stay clean and readable without pages of boilerplate.

Current version: **v0.9 (Beta)**

---

## Design Principles

* **Simple Needs to Be Simple:** Networking, object manifests, and graphics should not require dozens of configuration lines. Packing data into a network stream takes one line (`pack data tit pkt`). Connecting a client takes one line (`cli_connect "127.0.0.1":8080 tit client`).
* **Noise-Free Boundaries:** Explicit program and function boundaries using `trst` (start) and `tren` (end) instead of curly braces or strict whitespace rules.
* **Semantic Function Prefixes:** Prefixes identify function types directly in source code: `fmh` for math, `ftxt` for strings, `fcli` for networking clients, `fui` for interface actions, and `fdel` for memory cleanup.
* **Batteries Included:** 2D graphics, windowing, audio synthesis, HTTP clients, and package management are built directly into the runtime without requiring external dependencies.

---

## Key Features

* **Packets and Networking:** Serialize structured data into streamable packets with `pack` and restore them with `unpack`. Built-in non-blocking client and server sockets (`cli_connect`, `cli_send`, `cli_recv`, `srv_listen`, `srv_accept`) designed to run smoothly inside game loops.
* **Community Hub & Package Manager (TPM):** Search, install, and publish community creations directly from the terminal or IDE using `tpm search`, `tpm install`, and `tpm publish`.
* **2D Canvas Game Engine:** Native window creation (`cwin`), primitive rendering (`circ`, `regle`, `line`), keyboard/mouse input, and frame pacing (`fps calm`) that matches display refresh rates to keep CPU usage low.
* **Universal Web Client:** Direct HTTP GET and POST requests (`http_get`, `http_post`) and file downloading (`download`).
* **Object Manifests:** Structured object creation with dot notation (`player.x`, `player.hp`) registered through an explicit header (`add_obj`, `add_var`).
* **Dedicated Studio:** Ships with `TrappyIDE.exe`, a standalone code editor with syntax highlighting, an integrated terminal, one-click execution (F5), debugging (F6), and a Community Hub package viewer.

---

## Code Examples

### 1. Variables and Output

```trappy
trst
    txt "Hello from Trappy" tit greeting
    gan greeting

    mh 10 + 5 eq total
    gan total
tren
```

### 2. Objects and Dot Notation

```trappy
trst
    add_obj "player"
        name: "Alex"
        hp: 100
        speed: 5
    tren

    mh player.hp - 20 eq player.hp
    gan "Remaining HP:"
    gan player.hp
tren
```

### 3. Packets and Client Networking

```trappy
trst
    add_obj "player_sync"
        id: 42
        x: 250
        y: 180
    tren

    # Pack object into a transmission stream
    pack player_sync tit packet_data
    gan packet_data

    # Connect client and send
    cli_connect "127.0.0.1":8080 tit client
    cli_send client:packet_data
    cli_recv client tit response
    cli_close client
tren
```

### 4. 2D Game Loop

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

### 5. Web API Requests

```trappy
trst
    gan "Querying API..."
    http_get "https://api.github.com/zen" tit quote
    gan quote
tren
```

---

## Package Management & Community Hub (TPM)

Trappy includes its own package manager (`tpm`) so users can share code, download libraries, and collaborate:

```
tpm search [keyword]                Search for community packages
tpm install <package_name_or_url>   Install a community package
tpm publish <file.trappy> [author]  Publish code to the community hub
tpm list                            List installed packages
```

---

## Tooling

* **TrappyIDE.exe**: Standalone desktop editor. Press F5 to execute code or F6 to run a syntax check.
* **trpexec**: Command-line runner for executing `.trappy` files.
  ```
  trpexec script.trappy
  ```
* **tpm**: Command-line tool for package installation and publishing.

---

## Project Status and Roadmap

Trappy is currently in beta development:

* **v0.8.5:** Core runtime, object manifests, 2D game canvas, HTTP client, and TrappyIDE studio.
* **v0.9.0 (Current Beta):** Structured packet engine (`pack`/`unpack`), non-blocking client/server sockets, and the TPM Community Hub.
* **v0.9.5:** Performance tuning, runtime memory optimizations, and benchmark tests.
* **v1.0.0:** First general stable release.

---

## License

Trappy is an open source programming language project.
