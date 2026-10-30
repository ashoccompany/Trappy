# Trappy Programming Language

Trappy is an independent programming language built from scratch. It is designed to be approachable for beginners while providing built-in tools for desktop applications, 2D canvas games, and web requests without requiring third-party libraries.

The language uses explicit start and end blocks (`trst` and `tren`), categorized function prefixes, and an object manifest system.

Current version: **v0.8.5 (Beta)**

---

## Key Features

* **Readable Syntax:** Clean block boundaries using `trst` and `tren` instead of braces or strict indentation rules.
* **Built-in 2D Game Engine:** Native window creation (`cwin`), primitive shape drawing (`circ`, `regle`), keyboard detection, and frame pacing (`fps calm`) that syncs with display refresh rates.
* **Web and Network Utilities:** Native HTTP GET/POST queries (`http_get`, `http_post`) and file downloading (`download`) included directly in the runtime.
* **Object Manifests:** Explicit declarations at the top of programs with dot-notation property access (`player.x`, `player.hp`).
* **Categorized Functions:** Prefixes indicate function behavior at a glance (`fmh` for math, `ftxt` for text, `fweb` for network tasks, `fui` for interface events, `fdel` for memory cleanup).
* **Package Management:** A built-in CLI tool (`tpm`) for installing and managing external Trappy scripts.
* **Dedicated Desktop Studio:** Comes with `TrappyIDE.exe`, a standalone editor with syntax highlighting, an integrated console, and one-click run and debug capabilities.

---

## Code Examples

### 1. Variables and Output

```trappy
trst
    txt "Hello from Trappy" tit message
    gan message
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

    mh player.hp - 15 eq player.hp
    gan "Remaining HP:"
    gan player.hp
tren
```

### 3. Basic 2D Game Loop

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

### 4. Fetching Data from the Web

```trappy
trst
    gan "Fetching quote from API..."
    http_get "https://api.github.com/zen" tit quote
    gan quote
tren
```

---

## Tooling

* **TrappyIDE.exe**: Standalone code editor. Press F5 to execute scripts or F6 to check for syntax errors.
* **trpexec**: Terminal runner for executing `.trappy` source files.
  ```
  trpexec script.trappy
  ```
* **tpm**: Package manager for installing and listing packages.
  ```
  tpm list
  tpm install <package_url>
  ```

---

## Project Status and Roadmap

Trappy is currently in beta development. The staged milestones are:

* **v0.8.5 (Current Beta):** Core language runtime, object manifests, 2D game loop, HTTP client, TPM package manager, and TrappyIDE studio.
* **v0.9.0:** Extended math functions, multi-channel sound support, and multiple window handling.
* **v0.9.5:** Runtime optimizations, benchmark suites, and error-handling hardening.
* **v1.0.0:** First general release.

---

## License

Trappy is developed as an open source project. Source code releases and distributions are staged according to milestone readiness.
