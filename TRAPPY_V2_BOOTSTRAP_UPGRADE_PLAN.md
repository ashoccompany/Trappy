# Trappy v2.0 Absolute Bootstrap & Architecture Upgrade Specification
**Project:** Trappy Programming Language  
**Target Milestone:** v2.0 Pure Scratch-Built Self-Hosting Bootstrap  
**Repository:** `https://github.com/ashoccompany/Trappy` / Local: `C:\Trappy Coding Language`  
**Guiding Law:** Simple Needs to Be Simple  
**Design Law:** 100% From Scratch — Zero Borrowing of Generic Language Tropes

---

## Table of Contents
1. [The Pure Scratch-Built Identity Manifesto](#1-the-pure-scratch-built-identity-manifesto)
2. [Critical Bugs & Security Vulnerabilities Audit](#2-critical-bugs--security-vulnerabilities-audit)
   - 2.1 [Bug #1: Comment Tokenizer Mismatch (`//` vs `#`)](#21-bug-1-comment-tokenizer-mismatch--vs-)
   - 2.2 [Vulnerability #2: Path Sanitization CWD Dependency & Root Escapes](#22-vulnerability-2-path-sanitization-cwd-dependency--root-escapes)
   - 2.3 [Bug #3: Compound Boolean Expression Failure (`and`, `or`, `not`)](#23-bug-3-compound-boolean-expression-failure-and-or-not)
   - 2.4 [Bug #4: Object Property Assignment Grammar Inconsistency (`=` vs `eq`)](#24-bug-4-object-property-assignment-grammar-inconsistency--vs-eq)
   - 2.5 [Bug #5: Function Argument Delimiter Rigidity (`:` vs `,`)](#25-bug-5-function-argument-delimiter-rigidity--vs-)
   - 2.6 [Architectural Gap #6: TPM Package Disconnect & The `loadpk` Solution](#26-architectural-gap-6-tpm-package-disconnect--the-loadpk-solution)
   - 2.7 [Vulnerability #7: Unbounded Call-Stack Recursion Exhaustion](#27-vulnerability-7-unbounded-call-stack-recursion-exhaustion)
3. [Trappy-Native Core Syntax & Lexicon](#3-trappy-native-core-syntax--lexicon)
   - 3.1 [`loadpk` (Load Package / Load Packet) Module Engine](#31-loadpk-load-package--load-packet-module-engine)
   - 3.2 [`efr` (Else-IFr) Multi-Branch Control Flow](#32-efr-else-ifr-multi-branch-control-flow)
   - 3.3 [`brch` & `cas` Discrete State & Pattern Matching](#33-brch--cas-discrete-state--pattern-matching)
   - 3.4 [Direct Bracket Navigation & Slicing (`arr[i]`, `dict[key]`)](#34-direct-bracket-navigation--slicing-arri-dictkey)
   - 3.5 [Dictionary Manifest Literals (`{ "key": value }`)](#35-dictionary-manifest-literals--key-value-)
   - 3.6 [`txtf` Trappy Interpolation Format Strings](#36-txtf-trappy-interpolation-format-strings)
4. [Games & 2D/3D Graphics Engine Suite](#4-games--2d3d-graphics-engine-suite)
   - 4.1 [3D Virtual Camera Matrix & Shaded Polygons (`cam3d`, `poly3d`)](#41-3d-virtual-camera-matrix--shaded-polygons-cam3d-poly3d)
   - 4.2 [2D Tilemap Viewport Engine (`tilemap_init`, `tilemap_draw`)](#42-2d-tilemap-viewport-engine-tilemap_init-tilemap_draw)
   - 4.3 [Particle Emission Physics (`particle_emitter`)](#43-particle-emission-physics-particle_emitter)
   - 4.4 [Polyphonic Audio with ADSR Envelopes (`synth_adsr`)](#44-polyphonic-audio-with-adsr-envelopes-synth_adsr)
5. [Applications, Desktop & Modern UI Suite](#5-applications-desktop--modern-ui-suite)
   - 5.1 [Interactive Window Compositor & Stacking Manager](#51-interactive-window-compositor--stacking-manager)
   - 5.2 [Native Clipboard, File Chooser & Dialogs (`sys_clipboard`, `sys_dialog`)](#52-native-clipboard-file-chooser--dialogs-sys_clipboard-sys_dialog)
   - 5.3 [Responsive Containers & Tab Navigation (`ui_container`, `ui_tabs`)](#53-responsive-containers--tab-navigation-ui_container-ui_tabs)
6. [Micro-AI Development Engine 2.0](#6-micro-ai-development-engine-20)
   - 6.1 [1D & 2D Convolutional Layers (`ai_conv2d`, `ai_pool2d`)](#61-1d--2d-convolutional-layers-ai_conv2d-ai_pool2d)
   - 6.2 [Gated Recurrent Unit Sequential Memory (`ai_gru_step`)](#62-gated-recurrent-unit-sequential-memory-ai_gru_step)
   - 6.3 [Audio FFT Frequency Spectrum Extractor (`ai_audio_fft`)](#63-audio-fft-frequency-spectrum-extractor-ai_audio_fft)
   - 6.4 [Neuroevolution & Genetic Reinforcement (`ai_ga_optimize`)](#64-neuroevolution--genetic-reinforcement-ai_ga_optimize)
7. [Operating System Simulation Suite 2.0 (TrappyOS)](#7-operating-system-simulation-suite-20-trappyos)
   - 7.1 [Virtual Memory Management Unit (MMU) & Paging Simulation](#71-virtual-memory-management-unit-mmu--paging-simulation)
   - 7.2 [Preemptive Task Scheduler with Instruction Quantum Interrupts](#72-preemptive-task-scheduler-with-instruction-quantum-interrupts)
   - 7.3 [Virtual UNIX Pipes & Stream Redirection (`os_pipe`, `os_redirect`)](#73-virtual-unix-pipes--stream-redirection-os_pipe-os_redirect)
   - 7.4 [Ring 1 Dynamic Driver Architecture (`os_driver_register`)](#74-ring-1-dynamic-driver-architecture-os_driver_register)
8. [The Absolute v2.0 Self-Hosting Bootstrapping Plan](#8-the-absolute-v20-self-hosting-bootstrapping-plan)
   - 8.1 [Bootstrapping Architecture & Pipeline](#81-bootstrapping-architecture--pipeline)
   - 8.2 [Trappy Virtual Machine (TVM) Instruction Set Architecture](#82-trappy-virtual-machine-tvm-instruction-set-architecture)
   - 8.3 [Self-Hosting Compiler Staged Implementation Plan](#83-self-hosting-compiler-staged-implementation-plan)

---

## 1. The Pure Scratch-Built Identity Manifesto

Trappy was conceived as an independent, universal language built from scratch. Its guiding design law is **"Simple needs to be simple"**. 

A core principle of Trappy is that **it must not copy or borrow generic keywords from other languages**. 
- Python uses `import`, `def`, `elif`, `try/except`.
- C/C++ uses `#include`, `switch`, `case`, `struct`.
- JavaScript uses `require`, `function`, `catch`.

Trappy has its own distinct, semantic identity built around:
- **Noise-Free Program & Block Bounds:** `trst` (start) and `tren` (end).
- **Target Directional Assignment:** `tit` (into target).
- **Mathematical Statement Scope:** `mh ... eq <var>`.
- **Domain Function Families:** `fmh` (math), `ftxt` (text), `f3d` (3D), `fos` (OS), `fcli` (client sockets), `fdel` (cleanup).
- **Declarations:** `add_var`, `add_obj`, `add_func`, `add_type`.
- **Output:** `gan` (print line), `out` (raw output).
- **Input:** `rt` (read text), `answ` (answer prompt).

In Trappy v2.0, all new language constructs adhere strictly to this custom-built vocabulary. For example:
- **Loading packages/modules is `loadpk`** (load packet / load package), NOT `import`.
- **Multi-branch conditionals use `efr`** (`else` + `ifr`), NOT `elif`.
- **Multi-state pattern matching uses `brch` & `cas`**, NOT `switch`.
- **String template formatting is `txtf`**, NOT Python's `f"..."`.

---

## 2. Critical Bugs & Security Vulnerabilities Audit

During deep inspection of the local codebase, seven critical bugs, security vulnerabilities, and architectural gaps were identified. Each is analyzed below with root cause, demonstration, and the exact architectural fix.

---

### 2.1 Bug #1: Comment Tokenizer Mismatch (`//` vs `#`)

#### Domain
Core Lexer (`tokenize()` in `trappy.py`)

#### Problem
The official documentation (`README.md`, Example 5, line 206) instructs users to write comments using `//`:
```trappy
// Boot the kernel
os_boot "TrappyOS" "1.5.0"
```
However, line 1273 of `trappy.py` only implements support for `#`:
```python
if c == '#':
    while i < n and code[i] != '\n':
        i += 1
    continue
```
When `//` is encountered, the lexer consumes `/` as an arithmetic operator. It produces two consecutive `Token('/', '/', line)` instances followed by words as variable names. When passed to the parser, the script crashes immediately with:
`[Trappy Error at line 1]: Unexpected command '/'`

#### Example
```trappy
trst
    // This is valid according to README.md
    out "Hello World"
tren
# Execution fails with: [Trappy Error at line 2]: Unexpected command '/'
```

#### Fix Blueprint
Upgrade `tokenize()` with a multi-character lookahead state machine supporting `#`, `//`, and block comments `/* ... */`:
```python
# Check for single-line hash comment
if c == '#':
    while i < n and code[i] != '\n':
        i += 1
    continue

# Check for comments starting with '/'
if c == '/' and i + 1 < n:
    # Single-line comment //
    if code[i + 1] == '/':
        i += 2
        while i < n and code[i] != '\n':
            i += 1
        continue
    # Multi-line block comment /* ... */
    if code[i + 1] == '*':
        start_line = line
        i += 2
        while i + 1 < n and not (code[i] == '*' and code[i + 1] == '/'):
            if code[i] == '\n':
                line += 1
            i += 1
        if i + 1 >= n:
            raise TrappyError("Unterminated block comment /* ... */", start_line)
        i += 2  # Skip past */
        continue
```

#### Result
Both single-line comment forms (`#`, `//`) and multi-line comments (`/* ... */`) execute seamlessly. All README examples become 100% executable without modification.

---

### 2.2 Vulnerability #2: Path Sanitization CWD Dependency & Root Escapes

#### Domain
Security Engine (`sanitize_path()` in `trappy.py`, line 84)

#### Problem
The path traversal mitigation is implemented as:
```python
def sanitize_path(filename, base_dir=None, line=None):
    if base_dir is None:
        base_dir = os.getcwd()
    base_dir = os.path.abspath(base_dir)
    target_path = os.path.abspath(os.path.join(base_dir, filename))
    if not (target_path == base_dir or target_path.startswith(base_dir + os.sep)):
        raise TrappySecurityError(f"Path Traversal attempt blocked: '{filename}'")
    return target_path
```
This implementation contains two severe security and reliability flaws:
1. **False Positive Failures:** If a caller or test runs Trappy from outside the project directory (e.g. `python -m unittest discover` run from `C:\Users\ThinkPad`), `base_dir` resolves to `C:\Users\ThinkPad`. When Trappy evaluates a perfectly valid path inside `C:/Trappy Coding Language/tests/...`, it blocks execution with `SECURITY VIOLATION: Path Traversal attempt blocked` because the target does not start with `C:\Users\ThinkPad`.
2. **Drive Root Escapes:** If a user runs a Trappy script from their system root (e.g. `C:\`), `base_dir` becomes `C:\`. Because every path on the drive starts with `C:\`, the security check evaluates to `True` for every sensitive system file (`C:\Windows\System32`, `C:\Users\...`), completely disabling the sandbox!

#### Example
```python
# From C:\Users\ThinkPad:
python -m unittest discover -s "C:\Trappy Coding Language\tests"
# Results in 4 failed tests with false-positive security violations!
```

#### Fix Blueprint
Tie the sandbox boundary explicitly to the **Script Directory** or an explicit configuration root, and reject absolute drive roots:
```python
def sanitize_path(filename, base_dir=None, line=None):
    if base_dir is None:
        # Priority: explicit env var -> script directory -> current working dir
        base_dir = os.environ.get("TRAPPY_SANDBOX_ROOT")
        if not base_dir:
            if hasattr(sys.modules.get("__main__"), "__file__"):
                base_dir = os.path.dirname(os.path.abspath(sys.modules["__main__"].__file__))
            else:
                base_dir = os.getcwd()

    base_dir = os.path.realpath(os.path.abspath(base_dir))
    
    # Block running directly from root drive without a subfolder sandbox
    if base_dir == os.path.abspath(os.sep) or (os.name == 'nt' and len(base_dir) <= 3):
        sandbox_fallback = os.path.join(base_dir, "trappy_sandbox")
        os.makedirs(sandbox_fallback, exist_ok=True)
        base_dir = sandbox_fallback

    # Normalize and verify boundary
    target_path = os.path.realpath(os.path.abspath(os.path.join(base_dir, filename)))
    prefix = base_dir if base_dir.endswith(os.sep) else base_dir + os.sep
    if not (target_path == base_dir or target_path.startswith(prefix)):
        raise TrappySecurityError(f"Path Traversal attempt blocked: '{filename}' outside '{base_dir}'", line)
    return target_path
```

#### Result
Unit tests pass regardless of the invoking working directory, and running scripts from drive roots can never inadvertently compromise external system files.

---

### 2.3 Bug #3: Compound Boolean Expression Failure (`and`, `or`, `not`)

#### Domain
Parser & Evaluator (`parse_condition()` and `eval_condition()`)

#### Problem
In `trappy.py` line 1596:
```python
def parse_condition(self):
    left = self.parse_atom()
    cmp_tokens = ("GRT", "LSS", "SM", "EQ", "==", "!=", ">", "<", ">=", "<=")
    if self.peek().kind in cmp_tokens:
        op_tok = self.consume(self.peek().kind)
        right = self.parse_atom()
        return ("COND", op, left, right)
```
The parser only consumes exactly one binary relational comparison. When a developer attempts to write compound conditions using `and`, `or`, or `not`, the parser stops after `left op right`, treats `and` as an unknown command, and crashes.

#### Example
```trappy
trst
    mh 10 eq score
    mh 5 eq lives
    ifr score > 5 and lives > 0
        out "Player active"
    tren
tren
# Crashes with: [Trappy Error at line 4]: Unexpected command '>'
```

#### Fix Blueprint
Implement full recursive-descent precedence climbing for boolean expressions supporting both symbolic (`&&`, `||`, `!`) and keyword-based (`and`, `or`, `not`) conditions:
```python
def parse_condition(self):
    return self.parse_or_condition()

def parse_or_condition(self):
    node = self.parse_and_condition()
    while self.peek().kind in ("OR", "BOR", "||"):
        self.consume(self.peek().kind)
        right = self.parse_and_condition()
        node = ("LOGICAL_OR", node, right)
    return node

def parse_and_condition(self):
    node = self.parse_not_condition()
    while self.peek().kind in ("AND", "BAND", "&&"):
        self.consume(self.peek().kind)
        right = self.parse_not_condition()
        node = ("LOGICAL_AND", node, right)
    return node

def parse_not_condition(self):
    if self.peek().kind in ("NOT", "BNOT", "!"):
        self.consume(self.peek().kind)
        sub = self.parse_not_condition()
        return ("LOGICAL_NOT", sub)
    return self.parse_rel_condition()
```

#### Result
Developers can express complex game state, network validation, and security rule logic in clean single-line statements with short-circuit evaluation.

---

### 2.4 Bug #4: Object Property Assignment Grammar Inconsistency (`=` vs `eq`)

#### Domain
Documentation & AST Statement Parser (`_parse_add_obj` and `_parse_function_or_call`)

#### Problem
`MANUAL.md` line 76 and 310 explicitly provides the following code example:
```trappy
add_obj player
player.x = 10
player.y = 20
```
When this code is executed:
1. `add_obj player` enters an object definition loop waiting for `tren`. It expects colon-separated properties (`x: 10`), NOT statements.
2. Even outside `add_obj`, line 3257 of `trappy.py` specifies:
   ```python
   if self.peek().kind == ".":
       self.consume(".")
       prop = self.consume("NAME").val
       self.consume("EQ")  # Strictly consumes the keyword 'eq', NOT '='!
       expr = self.parse_expr()
   ```
   Single `=` is tokenized as `Token('=', '=', line)`. Because `self.consume("EQ")` requires the keyword `eq`, the manual's documented syntax `player.x = 10` crashes with:
   `[Trappy Error at line 2]: Expected 'EQ', but got '='`

#### Example
```trappy
trst
    add_obj "player"
        x: 0
        y: 0
    tren
    player.x = 10  # Crashes: Expected 'EQ', but got '='
tren
```

#### Fix Blueprint
Harmonize the parser's assignment consumer to accept both `EQ` (`eq`) and `=` (`=`):
```python
def consume_assign_op(self):
    if self.peek().kind in ("EQ", "="):
        return self.consume(self.peek().kind)
    raise TrappyError(f"Expected assignment operator 'eq' or '=', but got '{self.peek().val}'", self.peek().line)
```
Apply `consume_assign_op()` across all property assignments and variable assignments in `_parse_function_or_call()`.

#### Result
Both the traditional Trappy syntax (`player.x eq 10`) and standard programming syntax (`player.x = 10`) work identically.

---

### 2.5 Bug #5: Function Argument Delimiter Rigidity (`:` vs `,`)

#### Domain
Parser Expression Engine (`parse_factor()` and `parse_atom()`)

#### Problem
When invoking functions inside expressions (e.g. `dist(x1: y1: x2: y2)` or custom user functions `add(a: b)`), Trappy strictly requires colons (`:`) as argument separators.
In lists, Trappy permits commas: `[1, 2, 3]`.
If a developer intuitively writes `calculate_sum(10, 20)`, the parser encounters `,` and crashes with:
`[Trappy Error at line 2]: Expected ')', but got ','`

#### Example
```trappy
trst
    fn add_two a:b
        mh a + b eq sum
        return sum
    tren
    out add_two(10, 20)  # Crashes: Expected ')', but got ','
tren
```

#### Fix Blueprint
Permit both `:` and `,` as valid argument delimiters in function call parsing:
```python
if self.peek().kind == "(":
    self.consume("(")
    args = []
    if self.peek().kind != ")":
        args.append(self.parse_expr())
        while self.peek().kind in (":", ","):
            self.consume(self.peek().kind)
            args.append(self.parse_expr())
    self.consume(")")
    return ("CALL", name, args, tok.line)
```

#### Result
Function arguments can be separated using colons (`:`) or standard commas (`,`), accommodating developer preference without syntax errors.

---

### 2.6 Architectural Gap #6: TPM Package Disconnect & The `loadpk` Solution

#### Domain
Package Ecosystem & Runtime Architecture (`tpm.py` and `trappy.py`)

#### Problem
Trappy ships with a package manager (`tpm.py`) that successfully queries and downloads packages from `community_hub/hub_index.json` to `packages/`.
However, inside `trappy.py`, there is **no package loading keyword**.
When a developer installs `packet_utils.trappy` or `physics_2d.trappy`, they have no way to load the code into their program. The package manager is completely disconnected from the language execution engine!
Using Python's keyword `import` violates Trappy's independent identity.

#### Solution
Implement Trappy's proprietary package loader: **`loadpk`** (Load Package / Load Packet).

#### Example
```trappy
trst
    # Load package directly into active scope
    loadpk "physics_2d"

    # Or load package into a target namespace using Trappy's 'tit' keyword
    loadpk "packet_utils" tit net

    # Call loaded functions cleanly:
    call net.make_chat_packet "Player1":"Ready!" tit pkt
tren
```

---

### 2.7 Vulnerability #7: Unbounded Call-Stack Recursion Exhaustion

#### Domain
Runtime Security & Stability (`call_function()` in `trappy.py`)

#### Problem
When user code executes recursive function calls, Trappy relies directly on Python's native call stack. A malicious or accidental infinite recursion loop (e.g. `fn loop_me ... call loop_me ... tren`) triggers a Python host `RecursionError` and crashes the entire application process, bypassing Trappy's error handling.

#### Example
```trappy
trst
    fn bomb x
        mh x + 1 eq next_x
        call bomb next_x
    tren
    call bomb 1
tren
# Crashes the Python interpreter with: Fatal RecursionError
```

#### Fix Blueprint
Implement an explicit, configurable recursion depth counter in `TrappyInterpreter`:
```python
class TrappyInterpreter:
    def __init__(self, safe_mode=False):
        self.call_stack_depth = 0
        self.max_call_stack_depth = 500  # Safe execution ceiling

    def call_function(self, name, args, env, line):
        if self.call_stack_depth >= self.max_call_stack_depth:
            raise TrappyError(f"Call stack overflow: Maximum recursion depth ({self.max_call_stack_depth}) exceeded", line)
        self.call_stack_depth += 1
        try:
            return self._execute_function_body(name, args, env, line)
        finally:
            self.call_stack_depth -= 1
```

#### Result
Infinite recursion attempts are intercepted gracefully and converted into catchable `TrappyError` exceptions without crashing the host process.

---

## 3. Trappy-Native Core Syntax & Lexicon

---

### 3.1 `loadpk` (Load Package / Load Packet) Module Engine

#### Concept
Trappy is built around packets and packages. Instead of generic `import`, Trappy introduces **`loadpk`**.

#### Formal Grammar (EBNF)
```ebnf
LoadPkStatement ::= "loadpk" StringLiteral ( "tit" TargetIdentifier )?
```

#### Usage Examples
```trappy
trst
    # 1. Global package load
    loadpk "physics_2d"
    apply_gravity player:9.8

    # 2. Namespaced package load using Trappy's 'tit'
    loadpk "packet_utils" tit net
    call net.make_game_packet "Player1":250:180 tit pkt
    cli_send client:pkt
tren
```

#### Engine Implementation Blueprint
```python
def _eval_loadpk(self, stmt, env):
    _, pkg_path_expr, target_alias, line = stmt
    pkg_name = str(self.eval_expr(pkg_path_expr, env))
    
    # 1. Check module cache to prevent circular loads
    if pkg_name in self.loaded_packages:
        module_env = self.loaded_packages[pkg_name]
    else:
        # 2. Resolve file path in search directories: [".", "packages", "packages/cache"]
        file_path = self._resolve_package_path(pkg_name, line)
        with open(file_path, "r", encoding="utf-8") as f:
            code = f.read()
        
        # 3. Parse and run in an isolated Environment
        tokens = tokenize(code)
        parser = Parser(tokens)
        ast = parser.parse_program()
        module_env = Environment()
        sub_interp = TrappyInterpreter(safe_mode=self.safe_mode)
        sub_interp.run(ast, module_env)
        self.loaded_packages[pkg_name] = module_env

    # 4. Bind exported functions & variables
    if target_alias:
        # Pack module into an object namespace
        module_obj = {}
        for var_name, var_val in module_env.vars.items():
            module_obj[var_name] = var_val
        for fn_name, fn_def in sub_interp.functions.items():
            module_obj[fn_name] = fn_def
        env.set(target_alias, module_obj)
    else:
        # Expose directly into current environment
        for var_name, var_val in module_env.vars.items():
            env.set(var_name, var_val)
        for fn_name, fn_def in sub_interp.functions.items():
            self.functions[fn_name] = fn_def
```

---

### 3.2 `efr` (Else-IFr) Multi-Branch Control Flow

#### Concept
In Trappy, `if` is **`ifr`**. Therefore, the natural, scratch-built Trappy keyword for "else if" is **`efr`** (`else` + `ifr` combined).
It completely replaces the need for Python's `elif`.

#### Formal Grammar (EBNF)
```ebnf
IfStatement ::= "ifr" Condition ( "then" )?
                Statement*
                ( "efr" Condition ( "then" )? Statement* )*
                ( ( "else" | "then" ) Statement* )?
                "tren"
```

#### Example
```trappy
trst
    mh 85 eq grade

    ifr grade >= 90
        out "Rank: S"
    efr grade >= 80
        out "Rank: A"
    efr grade >= 70
        out "Rank: B"
    efr grade >= 60
        out "Rank: C"
    else
        out "Rank: F"
    tren
tren
```

#### Benefits
- Pure Trappy DNA: pairs `ifr` with `efr`.
- Zero nesting: flat indentation.
- Single closing `tren`.

---

### 3.3 `brch` & `cas` Discrete State & Pattern Matching

#### Concept
Instead of generic `switch` or `match`, Trappy introduces **`brch`** (Branch) and **`cas`** (Case).

#### Formal Grammar (EBNF)
```ebnf
BranchStatement ::= "brch" Expression
                    ( "cas" Expression ( "then" )? Statement* )+
                    ( ( "else" | "othr" ) Statement* )?
                    "tren"
```

#### Example
```trappy
trst
    txt "ATTACK" tit player_action

    brch player_action
        cas "IDLE"
            call play_anim "idle"
        cas "MOVE"
            call play_anim "walk"
        cas "ATTACK"
            call play_anim "slash"
            call trigger_damage 25
        othr
            inf "Unknown state"
    tren
tren
```

---

### 3.4 Direct Bracket Navigation & Slicing (`arr[i]`, `dict[key]`)

#### Concept
Extend list and dictionary operations beyond statement-level `lget`/`dget` by allowing direct bracket indexing in expressions and assignments.

#### Example
```trappy
trst
    # Define player and grid
    lst [100, 20, 5] eq stats # [hp, mp, def]
    
    # Read directly in math expressions
    mh stats[0] - 15 eq stats[0]
    out "Remaining HP: " + to_str(stats[0])

    # Direct index assignment
    stats[1] eq 50

    # 2D Grid / Matrix navigation
    tilemap[player.y][player.x] eq 0
tren
```

---

### 3.5 Dictionary Manifest Literals (`{ "key": value }`)

#### Concept
Trappy supports list literals with `[...]`. Trappy v2.0 introduces dictionary manifest literals with `{...}`.

#### Example
```trappy
trst
    add_var hero: {
        "name": "TrappyLegend",
        "level": 10,
        "inventory": ["Shield", "Key"],
        "attributes": {
            "strength": 40,
            "speed": 18.5
        }
    }

    out "Hero Name: " + hero["name"]
    out "Strength: " + to_str(hero["attributes"]["strength"])
tren
```

---

### 3.6 `txtf` Trappy Interpolation Format Strings

#### Concept
Instead of Python's `f"..."`, Trappy introduces **`txtf`** (Text Format), matching the `ftxt` domain prefix.

#### Example
```trappy
trst
    txt "Alex" tit player_name
    mh 2500 eq high_score

    txtf "Player {player_name} has scored {high_score} points!" tit banner
    gan banner
tren
```

---

## 4. Games & 2D/3D Graphics Engine Suite

---

### 4.1 3D Virtual Camera Matrix & Shaded Polygons (`cam3d`, `poly3d`)

#### Current State
Wireframe projection only (`cube3d`, `sphere3d`, `pyramid3d`).

#### v2.0 Architecture
1. **Camera Matrix (`cam3d`):**
   ```trappy
   cam3d eye_x:eye_y:eye_z target_x:target_y:target_z fov
   cam3d 0:200:500 0:0:0 60
   ```
2. **Solid Shaded Polygons (`poly3d`):**
   Renders depth-sorted surfaces with Lambertian cosine shading:
   ```trappy
   poly3d [[0, 100, 0], [-50, 0, -50], [50, 0, -50]] cyan
   ```

---

### 4.2 2D Tilemap Viewport Engine (`tilemap_init`, `tilemap_draw`)

#### Concept
High-performance arcade grid rendering with automatic camera clipping:
```trappy
# 1. Initialize tilemap
tilemap_init "level_1" 200:100 32:32 "assets/tileset.png"

# 2. Render visible viewport in game loop
gloop
    tilemap_draw "level_1" cam_x:cam_y 800:600
tren
```

---

### 4.3 Particle Emission Physics (`particle_emitter`)

#### Concept
Hardware-optimized 2D particle simulation for combat effects and environmental ambiance:
```trappy
particle_emitter "sparks" player.x:player.y 30 yellow 2.0 -3.0 180
# particle_emitter id pos count color vel_x vel_y lifetime_ms
```

---

### 4.4 Polyphonic Audio with ADSR Envelopes (`synth_adsr`)

#### Concept
Adds Attack, Decay, Sustain, Release sound modulation to produce warm instruments and eliminate click artifacts:
```trappy
# Waveform, Frequency, Duration(ms), Attack, Decay, Sustain, Release
synth_adsr "sawtooth" 440 400 30 60 0.7 120
```

---

## 5. Applications, Desktop & Modern UI Suite

---

### 5.1 Interactive Window Compositor & Stacking Manager

#### Concept
Turn simulated windows into interactive, draggable desktop containers:
```trappy
os_ui_window "Calculator" 80:80 320:450 trg on_close tit win_calc
# Header dragging, title bar buttons, and active Z-index focus are handled automatically
```

---

### 5.2 Native Clipboard, File Chooser & Dialogs (`sys_clipboard`, `sys_dialog`)

#### Concept
Direct desktop OS integration:
```trappy
sys_clipboard_set "Text copied from Trappy app"
sys_dialog_open "Open Level File" "*.dat" tit chosen_path
file_read chosen_path tit level_data
```

---

### 5.3 Responsive Containers & Tab Navigation (`ui_container`, `ui_tabs`)

#### Concept
Modular layouts that adapt to window geometry:
```trappy
ui_container "sidebar" "vertical" 0:0 200:600
    ui_tabs ["Home", "Settings", "Terminal"] tit active_tab
tren
```

---

## 6. Micro-AI Development Engine 2.0

---

### 6.1 1D & 2D Convolutional Layers (`ai_conv2d`, `ai_pool2d`)

#### Concept
Zero-dependency 2D convolution for computer vision, sprite recognition, and grid game analysis:
```trappy
# Convolve a 2D tilemap with a 3x3 edge-detection kernel
ai_conv2d screen_matrix:kernel_edge:1 tit edge_features
ai_pool2d edge_features:2 tit downsampled_map
```

---

### 6.2 Gated Recurrent Unit Sequential Memory (`ai_gru_step`)

#### Concept
Pure-Python GRU recurrent memory for sequence modeling and dialogue:
```trappy
ai_gru_new "npc_memory" 16 32 # Input 16, Hidden 32
ai_gru_step "npc_memory" player_input_vector tit next_thought
```

---

### 6.3 Audio FFT Frequency Spectrum Extractor (`ai_audio_fft`)

#### Concept
Converts sound waveforms into frequency energy bands for audio AI classification:
```trappy
ai_audio_fft "voice.wav" 16 tit bands
ai_net_predict "voice_model" bands tit speaker
```

---

### 6.4 Neuroevolution & Genetic Reinforcement (`ai_ga_optimize`)

#### Concept
Evolve neural network weights using genetic mutation and survival-of-the-fittest:
```trappy
ai_ga_init "car_bots" 40 [6, 12, 2] # 40 car neural nets
ai_ga_score "car_bots" bot_id distance_traveled
ai_ga_reproduce "car_bots" 0.05 0.25 # 5% mutation rate, top 25% breed
```

---

## 7. Operating System Simulation Suite 2.0 (TrappyOS)

---

### 7.1 Virtual Memory Management Unit (MMU) & Paging Simulation

#### Concept
Simulate hardware page tables, virtual addresses, and NX protection:
```trappy
# Allocate 4KB page frame in process virtual space
os_mmu_page_alloc pid 0x00400000 4096 "RWX"
os_mmu_protect pid 0x00400000 "R--" # Remove execute -> traps execution attempts
```

---

### 7.2 Preemptive Task Scheduler with Instruction Quantum Interrupts

#### Concept
Preempt running tasks automatically without requiring manual `os_yield`:
- Every 100 executed instructions, the kernel preempts Ring 3 userland processes and context-switches to the next process in the ready queue.

---

### 7.3 Virtual UNIX Pipes & Stream Redirection (`os_pipe`, `os_redirect`)

#### Concept
Stream data between independent simulated processes:
```trappy
os_pipe tit pipe_read:pipe_write
os_redirect_stdout proc_a pipe_write
os_redirect_stdin proc_b pipe_read
```

---

### 7.4 Ring 1 Dynamic Driver Architecture (`os_driver_register`)

#### Concept
Register virtual hardware drivers into kernel Ring 1:
```trappy
os_driver_register "VIRTUAL_AUDIO" Ring1 tit audio_driver
os_driver_hook audio_driver:SYSCALL_PLAY on_audio_play
```

---

## 8. The Absolute v2.0 Self-Hosting Bootstrapping Plan

---

### 8.1 Bootstrapping Architecture & Pipeline

To achieve true language independence, Trappy v2.0 will eliminate Python entirely. The language will be rewritten in itself.

```
┌────────────────────────────────────────────────────────────────────────┐
│               TRAPPY v2.0 SELF-HOSTING COMPILER PIPELINE               │
├────────────────────────────────────────────────────────────────────────┤
│ 1. Lexer in Trappy (`bootstrap/lexer.trappy`)                          │
│    • Consumes source string, produces token list                       │
│    • Proved functional in Trappy v1.15 bootstrap prototype             │
├────────────────────────────────────────────────────────────────────────┤
│ 2. Parser in Trappy (`bootstrap/parser.trappy`)                        │
│    • Consumes tokens, constructs nested AST node dictionaries          │
│    • Fully recursive-descent written in pure Trappy                    │
├────────────────────────────────────────────────────────────────────────┤
│ 3. Bytecode Compiler in Trappy (`bootstrap/codegen.trappy`)            │
│    • Traverses AST dictionaries and emits compact binary bytecode      │
│    • Emits `.trpc` executable bytecode files                           │
├────────────────────────────────────────────────────────────────────────┤
│ 4. Trappy Virtual Machine (TVM)                                        │
│    • Ultra-fast register/stack VM written in C/Rust or pure assembly   │
│    • Zero dependency, under 500 KB executable size                     │
│    • 50x-100x execution speedup over current Python interpreter       │
└────────────────────────────────────────────────────────────────────────┘
```

---

### 8.2 Trappy Virtual Machine (TVM) Instruction Set Architecture

The TVM instruction set is designed for simplicity, safety, and rapid execution:

| Opcode | Mnemonic | Operands | Description |
| :--- | :--- | :--- | :--- |
| `0x01` | `OP_CONST` | `const_idx` | Pushes constant literal onto evaluation stack |
| `0x02` | `OP_LOAD` | `var_id` | Loads variable value from active environment scope |
| `0x03` | `OP_STORE` | `var_id` | Pops top of stack and stores into variable |
| `0x04` | `OP_ADD` | - | Pops $b$, pops $a$, pushes $a + b$ |
| `0x05` | `OP_SUB` | - | Pops $b$, pops $a$, pushes $a - b$ |
| `0x06` | `OP_MUL` | - | Pops $b$, pops $a$, pushes $a \times b$ |
| `0x07` | `OP_DIV` | - | Pops $b$, pops $a$, pushes $a \div b$ with zero check |
| `0x08` | `OP_INDEX_GET` | - | Pops index, pops container, pushes element |
| `0x09` | `OP_INDEX_SET` | - | Pops value, pops index, pops container, sets element |
| `0x0A` | `OP_JUMP` | `offset` | Unconditional jump to bytecode instruction offset |
| `0x0B` | `OP_JUMP_IF_FALSE` | `offset` | Pops condition; jumps if value is false/zero |
| `0x0C` | `OP_CALL` | `arg_count` | Invokes function with argument frame allocation |
| `0x0D` | `OP_RETURN` | - | Pops return value and restores caller stack frame |
| `0x0E` | `OP_LOADPK` | `pkg_idx` | Loads and links external Trappy package module |
| `0x0F` | `OP_OS_SYSCALL` | `call_num` | Traps to TrappyOS Ring 0 kernel dispatcher |
| `0x10` | `OP_HALT` | - | Terminates execution cleanly |

---

### 8.3 Self-Hosting Compiler Staged Implementation Plan

```
                           THE BOOTSTRAP CYCLE
                           
   [ Step 1: trappy.py (Host) ] ──Compiles──► [ bootstrap/*.trappy ]
                                                     │
                                                     ▼
                                          [ Emits: compiler.trpc ]
                                                     │
                                                     ▼
   [ Step 2: TVM Engine (C/Rust) ] ◄──Runs─── [ compiler.trpc ]
                 │
                 ▼
      Compiles itself natively!
                 │
                 ▼
      [ TRAPPY v2.0 IS BORN: 100% SELF-HOSTED & INDEPENDENT ]
```

1. **Step 1: Complete Parser in Trappy (`bootstrap/parser.trappy`):**
   Expand the existing pure-Trappy lexer (`bootstrap/trappy_bootstrap.trappy`) to parse all statements and return an AST encoded in Trappy dictionaries.
2. **Step 2: Bytecode Emitter in Trappy (`bootstrap/codegen.trappy`):**
   Write the bytecode generator in Trappy that converts AST dictionaries into TVM opcodes and writes `.trpc` files using `file_write`.
3. **Step 3: TVM C-Runtime (`tvm_runtime.c`):**
   Write a lightweight, cross-platform C runner (under 2,000 lines of clean ANSI C) that loads and executes `.trpc` bytecode files with native speed and zero external dependencies.
4. **Step 4: The Self-Hosting Verification Test:**
   - Execute `compiler.trappy` using the Python interpreter to compile `compiler.trappy` into `compiler_v2.trpc`.
   - Run `compiler_v2.trpc` on the native TVM engine to compile `compiler.trappy` again, generating `compiler_v3.trpc`.
   - Run a binary diff between `compiler_v2.trpc` and `compiler_v3.trpc`.
   - **When both bytecodes match bit-for-bit, Trappy is 100% self-hosted, bootstrapped, and fully independent!**

---

## 9. Conclusion

By adopting **`loadpk`**, **`efr`**, **`brch/cas`**, and **`txtf`**, Trappy maintains 100% originality and establishes its own unique design language. This blueprint equips the project with everything required to transition from a prototype runtime to an independent, self-hosting v2.0 compiler.
