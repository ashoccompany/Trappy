# Trappy

<p align="center">
  <img src="https://img.shields.io/badge/Status-In%20Active%20Development-blue?style=for-the-badge" alt="Status: In Active Development">
  <img src="https://img.shields.io/badge/Language-Trappy%20v0.7-cyan?style=for-the-badge" alt="Language Version">
  <img src="https://img.shields.io/badge/Engine-2D%20Canvas%20%26%20GUI-orange?style=for-the-badge" alt="Engine Support">
  <img src="https://img.shields.io/badge/Security-Sandboxed-green?style=for-the-badge" alt="Security">
</p>

> **Trappy** is a modern, expressive programming language built completely from scratch. Designed to bridge the gap between beginner-friendly scripting, 2D game development, and serious low-level cybersecurity systems.

---

## Why Trappy?

*  **Human-Readable Syntax:** Clear noise-free block structure (`trst` to `tren`) without semicolon clutter.
*  **Built-in 2D Game Engine:** Native desktop windows (`cwin`), shapes (`circ`, `regle`), and **Calm FPS** hardware sync (`fps calm`) to prevent CPU overheating and stutter. (why did i wrote this)
*  **Cybersecurity & Systems Ready:** Native support for Hex literals (`0xFF`), bitwise operations (`band`, `bor`, `bxor`), and live network socket port scanners (`net_scan`). (honestly why did i added this too)
*  **Custom Object Manifests:** Full Object-Oriented dot notation (`player.x`, `player.hp`) registered via an explicit manifest header (`add_obj`, `add_var`). 
*  **Categorized Function System:** Built-in semantic prefixes that tag the exact purpose of every function (`fmh` for Math, `fnet` for Networking, `fsec` for Security, `fdel` for Memory Cleanup).
*  **Anti-Exploit Sandbox:** Native protection against directory traversal attacks (`sanitize_path`) and recursion bombs. (anddd i exposed it)

---

## Code Showcases

### 1. Hello World & Text
```trappy
trst
    txt "Welcome to the future of coding!" tit greeting
    gan greeting
tren
```

### 2. Object-Oriented RPG Stats (With Dot Notation)
```trappy
trst
    add_obj "hero"
        name: "TrappyKnight"
        hp: 100
        attack: 35
        defense: 12
    tren

    # Direct property updates
    mh hero.hp - 20 eq hero.hp
    gan "Hero HP remaining:"
    gan hero.hp
tren
```

### 3. A 2D Arcade Game in 20 Lines
```trappy
trst
    cwin "Trappy Arcade" 600:400 main
    sbgwin "Trappy Arcade" black
    fps calm  # Natural monitor sync

    mh 300 eq player_x
    mh 200 eq player_y
    mh 18 eq player_r

    gloop
        label "MOVE: W, A, S, D | JUMP: SPACE" 300:30 yellow
        circ player_x:player_y player_r cyan
        regle 150:180 50:50 red

        # Controls
        ifr key "W" trg then mh player_y - 4 eq player_y
        ifr key "S" trg then mh player_y + 4 eq player_y
        ifr key "A" trg then mh player_x - 4 eq player_x
        ifr key "D" trg then mh player_x + 4 eq player_x

        # Flight Jump Key (grows in air to bypass hazards!)
        ifr flkey "SPACE" trged then mh player_y - 25 eq player_y
    tren
tren
```

### 4. Cybersecurity: Port Recon & XOR Cryptography
```trappy
trst
    # Live TCP Port Scan
    net_scan "127.0.0.1":135 tit rpc_port
    ifr rpc_port sm 1
        gan "Port 135 (MS-RPC): [OPEN]"
    then
        gan "Port 135: [CLOSED]"
    tren

    # Scratch XOR Payload Cryptography
    mh 0x41 bxor 0x5A eq encrypted_byte
    gan "Encrypted Byte: "
    gan encrypted_byte
tren
```

---

##  Trappy Studio (`TrappyIDE.exe`)

Trappy comes with its own dedicated standalone desktop editor:
- **Dark Mode Studio:** Customized for Trappy code with auto-line numbers.
- **Syntax Highlighting:** Instant color categorization for blocks, keywords, numbers, and strings.
- **One-Click Run (F5):** Runs code and streams output directly into an integrated bottom console.
- **One-Click Debugger (F6):** Analyzes the AST tree and pinpoints exact error lines before execution.
also i will upload everything in here only after developing
---

##  Project Roadmap

- [x] Custom Lexer & Pratt Recursive Descent Parser
- [x] Semantic Function Family (`fmh`, `ftxt`, `fnet`, `fdel`, `fui`)
- [x] Dynamic Pipe List streaming (`10 | 20 | 30`)
- [x] Hardware Calm FPS VSync & 2D Canvas Engine
- [x] Object Manifests & Dot-Notation (`player.x`)
- [x] Standalone Desktop IDE (`TrappyIDE.exe`)
- [x] Network reconnaissance & Bitwise Cryptography
- [ ] Transpiler to raw C / Assembly (for bare-metal OS kernel development)
- [ ] Trappy Package Manager (`tpm`)

---

## License & Status

Trappy is currently in **Active Private Development**. Source files and builds will be released as core milestones are finalized.

*Designed and crafted with passion by me*
