"""
Trappy Virtual Machine (TVM) v2.0.0 Runtime Engine
Pure Scratch-Built Execution Virtual Machine for Trappy Language.
Author: ashoccompany / Asham
License: MIT
Zero generic tropes, zero external dependencies.
"""

import sys
import os
import struct
import time

OP_CONST         = 0x01
OP_LOAD          = 0x02
OP_STORE         = 0x03
OP_ADD           = 0x04
OP_SUB           = 0x05
OP_MUL           = 0x06
OP_DIV           = 0x07
OP_INDEX_GET     = 0x08
OP_INDEX_SET     = 0x09
OP_JUMP          = 0x0A
OP_JUMP_IF_FALSE = 0x0B
OP_CALL          = 0x0C
OP_RETURN        = 0x0D
OP_LOADPK        = 0x0E
OP_OS_SYSCALL    = 0x0F
OP_HALT          = 0x10

OP_NAMES = {
    OP_CONST: "OP_CONST",
    OP_LOAD: "OP_LOAD",
    OP_STORE: "OP_STORE",
    OP_ADD: "OP_ADD",
    OP_SUB: "OP_SUB",
    OP_MUL: "OP_MUL",
    OP_DIV: "OP_DIV",
    OP_INDEX_GET: "OP_INDEX_GET",
    OP_INDEX_SET: "OP_INDEX_SET",
    OP_JUMP: "OP_JUMP",
    OP_JUMP_IF_FALSE: "OP_JUMP_IF_FALSE",
    OP_CALL: "OP_CALL",
    OP_RETURN: "OP_RETURN",
    OP_LOADPK: "OP_LOADPK",
    OP_OS_SYSCALL: "OP_OS_SYSCALL",
    OP_HALT: "OP_HALT",
}

CONST_INT   = 0x01
CONST_FLOAT = 0x02
CONST_STR   = 0x03
CONST_NULL  = 0x04

MAGIC_HEADER = b"TRPC\x02\x00"


class TVMBytecode:
    def __init__(self):
        self.constants = []
        self.instructions = []  # list of (opcode, operand)
        self.const_map = {}

    def add_const(self, val):
        if val in self.const_map:
            return self.const_map[val]
        idx = len(self.constants)
        self.constants.append(val)
        self.const_map[val] = idx
        return idx

    def emit(self, opcode, operand=0):
        idx = len(self.instructions)
        self.instructions.append((opcode, operand))
        return idx

    def patch_operand(self, instr_idx, operand):
        op, _ = self.instructions[instr_idx]
        self.instructions[instr_idx] = (op, operand)

    def serialize(self) -> bytes:
        data = bytearray(MAGIC_HEADER)
        # Constants
        data.extend(struct.pack("<I", len(self.constants)))
        for c in self.constants:
            if isinstance(c, int) and not isinstance(c, bool):
                data.append(CONST_INT)
                data.extend(struct.pack("<q", c))
            elif isinstance(c, float):
                data.append(CONST_FLOAT)
                data.extend(struct.pack("<d", c))
            elif isinstance(c, str):
                encoded = c.encode("utf-8")
                data.append(CONST_STR)
                data.extend(struct.pack("<I", len(encoded)))
                data.extend(encoded)
            else:
                data.append(CONST_NULL)

        # Instructions
        data.extend(struct.pack("<I", len(self.instructions)))
        for op, operand in self.instructions:
            data.append(op & 0xFF)
            data.extend(struct.pack("<i", operand))
        return bytes(data)

    @classmethod
    def deserialize(cls, data: bytes):
        if len(data) < 6 or data[:6] != MAGIC_HEADER:
            raise ValueError("Invalid TRPC bytecode file header")
        bc = cls()
        offset = 6

        # Read constants
        (num_consts,) = struct.unpack_from("<I", data, offset)
        offset += 4
        for _ in range(num_consts):
            ctype = data[offset]
            offset += 1
            if ctype == CONST_INT:
                (val,) = struct.unpack_from("<q", data, offset)
                offset += 8
                bc.constants.append(val)
            elif ctype == CONST_FLOAT:
                (val,) = struct.unpack_from("<d", data, offset)
                offset += 8
                bc.constants.append(val)
            elif ctype == CONST_STR:
                (slen,) = struct.unpack_from("<I", data, offset)
                offset += 4
                sval = data[offset : offset + slen].decode("utf-8", errors="replace")
                offset += slen
                bc.constants.append(sval)
            elif ctype == CONST_NULL:
                bc.constants.append(None)
            else:
                bc.constants.append(0)

        # Read instructions
        (num_instrs,) = struct.unpack_from("<I", data, offset)
        offset += 4
        for _ in range(num_instrs):
            opcode = data[offset]
            offset += 1
            (operand,) = struct.unpack_from("<i", data, offset)
            offset += 4
            bc.instructions.append((opcode, operand))

        return bc

    def disassemble(self) -> str:
        lines = ["[TRPC v2.0 Disassembly]", f"Constants ({len(self.constants)}):"]
        for i, c in enumerate(self.constants):
            lines.append(f"  [{i:04d}] {repr(c)}")
        lines.append(f"Instructions ({len(self.instructions)}):")
        for i, (op, operand) in enumerate(self.instructions):
            name = OP_NAMES.get(op, f"UNKNOWN_{op}")
            detail = ""
            if op in (OP_LOAD, OP_STORE, OP_CONST):
                if 0 <= operand < len(self.constants):
                    detail = f"({repr(self.constants[operand])})"
            lines.append(f"  {i:04d}:  {name:<16}  {operand:<8} {detail}")
        return "\n".join(lines)


class TVMFrame:
    def __init__(self, return_ip, locals_dict):
        self.return_ip = return_ip
        self.locals = locals_dict


class TVM:
    def __init__(self, bytecode: TVMBytecode = None, safe_mode=False):
        self.bytecode = bytecode
        self.stack = []
        self.call_stack = []
        self.globals = {}
        self.safe_mode = safe_mode
        self.output_buffer = []
        self.ip = 0
        self.halted = False

    def push(self, val):
        self.stack.append(val)

    def pop(self):
        if not self.stack:
            return 0
        return self.stack.pop()

    def current_scope(self):
        if self.call_stack:
            return self.call_stack[-1].locals
        return self.globals

    def execute(self, bytecode: TVMBytecode = None) -> int:
        if bytecode is not None:
            self.bytecode = bytecode
        if self.bytecode is None:
            return 1

        instrs = self.bytecode.instructions
        consts = self.bytecode.constants
        n_instrs = len(instrs)
        self.ip = 0
        self.halted = False

        while self.ip < n_instrs and not self.halted:
            op, operand = instrs[self.ip]
            self.ip += 1

            if op == OP_CONST:
                val = consts[operand] if 0 <= operand < len(consts) else 0
                self.push(val)

            elif op == OP_LOAD:
                var_name = consts[operand] if 0 <= operand < len(consts) else str(operand)
                scope = self.current_scope()
                if var_name in scope:
                    self.push(scope[var_name])
                elif var_name in self.globals:
                    self.push(self.globals[var_name])
                else:
                    self.push(0)

            elif op == OP_STORE:
                var_name = consts[operand] if 0 <= operand < len(consts) else str(operand)
                val = self.pop()
                scope = self.current_scope()
                scope[var_name] = val

            elif op == OP_ADD:
                b = self.pop()
                a = self.pop()
                if isinstance(a, str) or isinstance(b, str):
                    self.push(str(a) + str(b))
                elif isinstance(a, list) and isinstance(b, list):
                    self.push(a + b)
                else:
                    try:
                        self.push(a + b)
                    except Exception:
                        self.push(0)

            elif op == OP_SUB:
                b = self.pop()
                a = self.pop()
                try:
                    self.push(a - b)
                except Exception:
                    self.push(0)

            elif op == OP_MUL:
                b = self.pop()
                a = self.pop()
                try:
                    self.push(a * b)
                except Exception:
                    self.push(0)

            elif op == OP_DIV:
                b = self.pop()
                a = self.pop()
                if b == 0:
                    self.push(0)
                else:
                    self.push(a // b if isinstance(a, int) and isinstance(b, int) else a / b)

            elif op == OP_INDEX_GET:
                idx = self.pop()
                container = self.pop()
                try:
                    self.push(container[idx])
                except Exception:
                    self.push(0)

            elif op == OP_INDEX_SET:
                val = self.pop()
                idx = self.pop()
                container = self.pop()
                try:
                    container[idx] = val
                    self.push(container)
                except Exception:
                    self.push(0)

            elif op == OP_JUMP:
                self.ip = operand

            elif op == OP_JUMP_IF_FALSE:
                cond = self.pop()
                if not cond:
                    self.ip = operand

            elif op == OP_CALL:
                # operand is arg_count
                # Function target is on top of stack or in operand
                fn_val = self.pop()
                args = []
                for _ in range(operand):
                    args.append(self.pop())
                args.reverse()

                if isinstance(fn_val, int):
                    # Local jump to function IP
                    frame = TVMFrame(return_ip=self.ip, locals_dict={f"arg{i}": a for i, a in enumerate(args)})
                    self.call_stack.append(frame)
                    self.ip = fn_val
                elif callable(fn_val):
                    res = fn_val(*args)
                    self.push(res if res is not None else 0)
                else:
                    self.push(0)

            elif op == OP_RETURN:
                ret_val = self.pop()
                if self.call_stack:
                    frame = self.call_stack.pop()
                    self.ip = frame.return_ip
                    self.push(ret_val)
                else:
                    self.push(ret_val)
                    self.halted = True

            elif op == OP_LOADPK:
                pkg_name = consts[operand] if 0 <= operand < len(consts) else ""
                # Packages can be linked dynamically
                self.push(1)

            elif op == OP_OS_SYSCALL:
                syscall_num = operand
                self._dispatch_syscall(syscall_num)

            elif op == OP_HALT:
                self.halted = True
                break

        return 0

    def _dispatch_syscall(self, num: int):
        if num == 1:  # SYS_PRINT / SYS_OUT
            val = self.pop()
            s = str(val)
            self.output_buffer.append(s)
            print(s)
        elif num == 2:  # SYS_INPUT
            prompt = str(self.pop()) if self.stack else ""
            try:
                line = input(prompt)
            except Exception:
                line = ""
            self.push(line)
        elif num == 3:  # SYS_FILE_READ
            fname = str(self.pop())
            if os.path.exists(fname):
                try:
                    if fname.endswith(".trpc"):
                        with open(fname, "rb") as f:
                            self.push(f.read().decode("latin1"))
                    else:
                        with open(fname, "r", encoding="utf-8") as f:
                            self.push(f.read())
                except Exception:
                    self.push("")
            else:
                self.push("")
        elif num == 4:  # SYS_FILE_WRITE
            content = self.pop()
            fname = str(self.pop())
            try:
                parent = os.path.dirname(fname)
                if parent and not os.path.exists(parent):
                    os.makedirs(parent, exist_ok=True)
                if fname.endswith(".trpc") or (isinstance(content, str) and content.startswith("TRPC")):
                    if isinstance(content, bytes):
                        with open(fname, "wb") as f:
                            f.write(content)
                    else:
                        with open(fname, "w", encoding="latin1") as f:
                            f.write(str(content))
                else:
                    with open(fname, "w", encoding="utf-8") as f:
                        f.write(str(content))
                self.push(1)
            except Exception:
                self.push(0)
        elif num == 5:  # SYS_CLOCK
            self.push(int(time.time()))
        else:
            self.push(0)


def run_trpc_file(filepath: str) -> int:
    with open(filepath, "rb") as f:
        data = f.read()
    bc = TVMBytecode.deserialize(data)
    vm = TVM(bc)
    return vm.execute()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python tvm_runtime.py <file.trpc> [--disasm]")
        sys.exit(1)
    target = sys.argv[1]
    if "--disasm" in sys.argv:
        with open(target, "rb") as f:
            bc = TVMBytecode.deserialize(f.read())
        print(bc.disassemble())
    else:
        sys.exit(run_trpc_file(target))
