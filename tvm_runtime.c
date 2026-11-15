/*
 * Trappy Virtual Machine (TVM) v2.0.0 Native C Engine
 * Pure Scratch-Built Execution Virtual Machine for Trappy Language.
 * Author: ashoccompany / Asham
 * License: MIT
 * Zero generic tropes, zero external dependencies. ANSI C99 compliant.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

#define OP_CONST         0x01
#define OP_LOAD          0x02
#define OP_STORE         0x03
#define OP_ADD           0x04
#define OP_SUB           0x05
#define OP_MUL           0x06
#define OP_DIV           0x07
#define OP_INDEX_GET     0x08
#define OP_INDEX_SET     0x09
#define OP_JUMP          0x0A
#define OP_JUMP_IF_FALSE 0x0B
#define OP_CALL          0x0C
#define OP_RETURN        0x0D
#define OP_LOADPK        0x0E
#define OP_OS_SYSCALL    0x0F
#define OP_HALT          0x10

#define CONST_INT   0x01
#define CONST_FLOAT 0x02
#define CONST_STR   0x03
#define CONST_NULL  0x04

#define VAL_NULL    0
#define VAL_INT     1
#define VAL_FLOAT   2
#define VAL_STR     3

#define MAX_STACK      4096
#define MAX_CALL_STACK 512
#define MAX_VARS       1024

typedef struct {
    uint8_t type;
    union {
        int64_t i;
        double  f;
        char*   s;
    } as;
} Value;

typedef struct {
    uint8_t opcode;
    int32_t operand;
} Instruction;

typedef struct {
    char* name;
    Value val;
} VarEntry;

typedef struct {
    int return_ip;
    int frame_stack_base;
} CallFrame;

typedef struct {
    Value* constants;
    uint32_t num_constants;
    Instruction* instructions;
    uint32_t num_instructions;
} Bytecode;

typedef struct {
    Bytecode* bc;
    Value stack[MAX_STACK];
    int sp;
    CallFrame call_stack[MAX_CALL_STACK];
    int csp;
    VarEntry vars[MAX_VARS];
    int var_count;
    int ip;
    int halted;
} VM;

static Value val_null(void) {
    Value v;
    v.type = VAL_NULL;
    v.as.i = 0;
    return v;
}

static Value val_int(int64_t i) {
    Value v;
    v.type = VAL_INT;
    v.as.i = i;
    return v;
}

static Value val_float(double f) {
    Value v;
    v.type = VAL_FLOAT;
    v.as.f = f;
    return v;
}

static Value val_str(const char* s) {
    Value v;
    v.type = VAL_STR;
    v.as.s = strdup(s ? s : "");
    return v;
}

static void val_free(Value v) {
    if (v.type == VAL_STR && v.as.s) {
        free(v.as.s);
    }
}

static Value val_clone(Value v) {
    if (v.type == VAL_STR) {
        return val_str(v.as.s);
    }
    return v;
}

static int val_is_truthy(Value v) {
    if (v.type == VAL_NULL) return 0;
    if (v.type == VAL_INT) return v.as.i != 0;
    if (v.type == VAL_FLOAT) return v.as.f != 0.0;
    if (v.type == VAL_STR) return (v.as.s && v.as.s[0] != '\0');
    return 0;
}

static void vm_init(VM* vm, Bytecode* bc) {
    vm->bc = bc;
    vm->sp = 0;
    vm->csp = 0;
    vm->var_count = 0;
    vm->ip = 0;
    vm->halted = 0;
}

static void vm_push(VM* vm, Value v) {
    if (vm->sp < MAX_STACK) {
        vm->stack[vm->sp++] = v;
    } else {
        fprintf(stderr, "[TVM Error]: Stack overflow\n");
    }
}

static Value vm_pop(VM* vm) {
    if (vm->sp > 0) {
        return vm->stack[--vm->sp];
    }
    return val_null();
}

static void vm_set_var(VM* vm, const char* name, Value v) {
    for (int i = 0; i < vm->var_count; i++) {
        if (strcmp(vm->vars[i].name, name) == 0) {
            val_free(vm->vars[i].val);
            vm->vars[i].val = val_clone(v);
            return;
        }
    }
    if (vm->var_count < MAX_VARS) {
        vm->vars[vm->var_count].name = strdup(name);
        vm->vars[vm->var_count].val = val_clone(v);
        vm->var_count++;
    }
}

static Value vm_get_var(VM* vm, const char* name) {
    for (int i = 0; i < vm->var_count; i++) {
        if (strcmp(vm->vars[i].name, name) == 0) {
            return val_clone(vm->vars[i].val);
        }
    }
    return val_int(0);
}

static Bytecode* load_trpc(const char* filepath) {
    FILE* f = fopen(filepath, "rb");
    if (!f) {
        fprintf(stderr, "[TVM Error]: Cannot open file: %s\n", filepath);
        return NULL;
    }

    char header[6];
    if (fread(header, 1, 6, f) != 6 || memcmp(header, "TRPC\x02\x00", 6) != 0) {
        fprintf(stderr, "[TVM Error]: Invalid TRPC bytecode header\n");
        fclose(f);
        return NULL;
    }

    Bytecode* bc = (Bytecode*)calloc(1, sizeof(Bytecode));
    if (fread(&bc->num_constants, 4, 1, f) != 1) {
        fclose(f);
        free(bc);
        return NULL;
    }

    bc->constants = (Value*)calloc(bc->num_constants, sizeof(Value));
    for (uint32_t i = 0; i < bc->num_constants; i++) {
        uint8_t ctype = 0;
        fread(&ctype, 1, 1, f);
        if (ctype == CONST_INT) {
            int64_t ival = 0;
            fread(&ival, 8, 1, f);
            bc->constants[i] = val_int(ival);
        } else if (ctype == CONST_FLOAT) {
            double fval = 0;
            fread(&fval, 8, 1, f);
            bc->constants[i] = val_float(fval);
        } else if (ctype == CONST_STR) {
            uint32_t slen = 0;
            fread(&slen, 4, 1, f);
            char* sbuf = (char*)malloc(slen + 1);
            fread(sbuf, 1, slen, f);
            sbuf[slen] = '\0';
            bc->constants[i].type = VAL_STR;
            bc->constants[i].as.s = sbuf;
        } else {
            bc->constants[i] = val_null();
        }
    }

    if (fread(&bc->num_instructions, 4, 1, f) != 1) {
        fclose(f);
        return bc;
    }

    bc->instructions = (Instruction*)calloc(bc->num_instructions, sizeof(Instruction));
    for (uint32_t i = 0; i < bc->num_instructions; i++) {
        fread(&bc->instructions[i].opcode, 1, 1, f);
        fread(&bc->instructions[i].operand, 4, 1, f);
    }

    fclose(f);
    return bc;
}

static void free_bytecode(Bytecode* bc) {
    if (!bc) return;
    for (uint32_t i = 0; i < bc->num_constants; i++) {
        val_free(bc->constants[i]);
    }
    free(bc->constants);
    free(bc->instructions);
    free(bc);
}

static void syscall_dispatch(VM* vm, int sys_num) {
    if (sys_num == 1) { /* SYS_PRINT */
        Value v = vm_pop(vm);
        if (v.type == VAL_INT) {
            printf("%lld\n", (long long)v.as.i);
        } else if (v.type == VAL_FLOAT) {
            printf("%g\n", v.as.f);
        } else if (v.type == VAL_STR) {
            printf("%s\n", v.as.s ? v.as.s : "");
        } else {
            printf("null\n");
        }
        val_free(v);
    } else if (sys_num == 2) { /* SYS_INPUT */
        Value prompt = vm_pop(vm);
        if (prompt.type == VAL_STR && prompt.as.s) {
            printf("%s", prompt.as.s);
            fflush(stdout);
        }
        val_free(prompt);
        char buf[1024];
        if (fgets(buf, sizeof(buf), stdin)) {
            size_t l = strlen(buf);
            if (l > 0 && buf[l - 1] == '\n') buf[l - 1] = '\0';
            vm_push(vm, val_str(buf));
        } else {
            vm_push(vm, val_str(""));
        }
    } else if (sys_num == 3) { /* SYS_FILE_READ */
        Value fname = vm_pop(vm);
        const char* path = (fname.type == VAL_STR) ? fname.as.s : "";
        FILE* fp = fopen(path, "rb");
        if (fp) {
            fseek(fp, 0, SEEK_END);
            long sz = ftell(fp);
            fseek(fp, 0, SEEK_SET);
            char* content = (char*)malloc(sz + 1);
            if (content) {
                fread(content, 1, sz, fp);
                content[sz] = '\0';
                vm_push(vm, val_str(content));
                free(content);
            } else {
                vm_push(vm, val_str(""));
            }
            fclose(fp);
        } else {
            vm_push(vm, val_str(""));
        }
        val_free(fname);
    } else if (sys_num == 4) { /* SYS_FILE_WRITE */
        Value content = vm_pop(vm);
        Value fname = vm_pop(vm);
        const char* path = (fname.type == VAL_STR) ? fname.as.s : "";
        FILE* fp = fopen(path, "wb");
        if (fp) {
            if (content.type == VAL_STR && content.as.s) {
                fwrite(content.as.s, 1, strlen(content.as.s), fp);
            }
            fclose(fp);
            vm_push(vm, val_int(1));
        } else {
            vm_push(vm, val_int(0));
        }
        val_free(content);
        val_free(fname);
    } else {
        vm_push(vm, val_int(0));
    }
}

int vm_run(VM* vm) {
    while (vm->ip < (int)vm->bc->num_instructions && !vm->halted) {
        Instruction instr = vm->bc->instructions[vm->ip++];
        switch (instr.opcode) {
            case OP_CONST: {
                if (instr.operand >= 0 && instr.operand < (int)vm->bc->num_constants) {
                    vm_push(vm, val_clone(vm->bc->constants[instr.operand]));
                } else {
                    vm_push(vm, val_null());
                }
                break;
            }
            case OP_LOAD: {
                const char* var_name = "";
                if (instr.operand >= 0 && instr.operand < (int)vm->bc->num_constants) {
                    var_name = vm->bc->constants[instr.operand].as.s;
                }
                vm_push(vm, vm_get_var(vm, var_name));
                break;
            }
            case OP_STORE: {
                const char* var_name = "";
                if (instr.operand >= 0 && instr.operand < (int)vm->bc->num_constants) {
                    var_name = vm->bc->constants[instr.operand].as.s;
                }
                Value v = vm_pop(vm);
                vm_set_var(vm, var_name, v);
                val_free(v);
                break;
            }
            case OP_ADD: {
                Value b = vm_pop(vm);
                Value a = vm_pop(vm);
                if (a.type == VAL_STR || b.type == VAL_STR) {
                    char buf_a[128], buf_b[128];
                    const char* sa = (a.type == VAL_STR) ? a.as.s : (sprintf(buf_a, "%lld", (long long)a.as.i), buf_a);
                    const char* sb = (b.type == VAL_STR) ? b.as.s : (sprintf(buf_b, "%lld", (long long)b.as.i), buf_b);
                    size_t len = strlen(sa) + strlen(sb);
                    char* res = (char*)malloc(len + 1);
                    strcpy(res, sa);
                    strcat(res, sb);
                    vm_push(vm, val_str(res));
                    free(res);
                } else if (a.type == VAL_FLOAT || b.type == VAL_FLOAT) {
                    double fa = (a.type == VAL_FLOAT) ? a.as.f : (double)a.as.i;
                    double fb = (b.type == VAL_FLOAT) ? b.as.f : (double)b.as.i;
                    vm_push(vm, val_float(fa + fb));
                } else {
                    vm_push(vm, val_int(a.as.i + b.as.i));
                }
                val_free(a);
                val_free(b);
                break;
            }
            case OP_SUB: {
                Value b = vm_pop(vm);
                Value a = vm_pop(vm);
                if (a.type == VAL_FLOAT || b.type == VAL_FLOAT) {
                    double fa = (a.type == VAL_FLOAT) ? a.as.f : (double)a.as.i;
                    double fb = (b.type == VAL_FLOAT) ? b.as.f : (double)b.as.i;
                    vm_push(vm, val_float(fa - fb));
                } else {
                    vm_push(vm, val_int(a.as.i - b.as.i));
                }
                val_free(a);
                val_free(b);
                break;
            }
            case OP_MUL: {
                Value b = vm_pop(vm);
                Value a = vm_pop(vm);
                if (a.type == VAL_FLOAT || b.type == VAL_FLOAT) {
                    double fa = (a.type == VAL_FLOAT) ? a.as.f : (double)a.as.i;
                    double fb = (b.type == VAL_FLOAT) ? b.as.f : (double)b.as.i;
                    vm_push(vm, val_float(fa * fb));
                } else {
                    vm_push(vm, val_int(a.as.i * b.as.i));
                }
                val_free(a);
                val_free(b);
                break;
            }
            case OP_DIV: {
                Value b = vm_pop(vm);
                Value a = vm_pop(vm);
                if (b.type == VAL_INT && b.as.i == 0) {
                    vm_push(vm, val_int(0));
                } else if (b.type == VAL_FLOAT && b.as.f == 0.0) {
                    vm_push(vm, val_float(0.0));
                } else if (a.type == VAL_FLOAT || b.type == VAL_FLOAT) {
                    double fa = (a.type == VAL_FLOAT) ? a.as.f : (double)a.as.i;
                    double fb = (b.type == VAL_FLOAT) ? b.as.f : (double)b.as.i;
                    vm_push(vm, val_float(fa / fb));
                } else {
                    vm_push(vm, val_int(a.as.i / b.as.i));
                }
                val_free(a);
                val_free(b);
                break;
            }
            case OP_INDEX_GET: {
                Value idx = vm_pop(vm);
                Value container = vm_pop(vm);
                if (container.type == VAL_STR && container.as.s) {
                    int64_t i = (idx.type == VAL_INT) ? idx.as.i : 0;
                    size_t len = strlen(container.as.s);
                    if (i >= 0 && (size_t)i < len) {
                        char ch_str[2] = { container.as.s[i], '\0' };
                        vm_push(vm, val_str(ch_str));
                    } else {
                        vm_push(vm, val_str(""));
                    }
                } else {
                    vm_push(vm, val_int(0));
                }
                val_free(idx);
                val_free(container);
                break;
            }
            case OP_INDEX_SET: {
                Value val = vm_pop(vm);
                Value idx = vm_pop(vm);
                Value container = vm_pop(vm);
                vm_push(vm, container);
                val_free(val);
                val_free(idx);
                break;
            }
            case OP_JUMP: {
                vm->ip = instr.operand;
                break;
            }
            case OP_JUMP_IF_FALSE: {
                Value cond = vm_pop(vm);
                if (!val_is_truthy(cond)) {
                    vm->ip = instr.operand;
                }
                val_free(cond);
                break;
            }
            case OP_CALL: {
                Value fn = vm_pop(vm);
                if (fn.type == VAL_INT && vm->csp < MAX_CALL_STACK) {
                    vm->call_stack[vm->csp].return_ip = vm->ip;
                    vm->call_stack[vm->csp].frame_stack_base = vm->sp;
                    vm->csp++;
                    vm->ip = (int)fn.as.i;
                }
                val_free(fn);
                break;
            }
            case OP_RETURN: {
                Value ret = vm_pop(vm);
                if (vm->csp > 0) {
                    vm->csp--;
                    vm->ip = vm->call_stack[vm->csp].return_ip;
                    vm_push(vm, ret);
                } else {
                    vm_push(vm, ret);
                    vm->halted = 1;
                }
                break;
            }
            case OP_LOADPK: {
                vm_push(vm, val_int(1));
                break;
            }
            case OP_OS_SYSCALL: {
                syscall_dispatch(vm, instr.operand);
                break;
            }
            case OP_HALT: {
                vm->halted = 1;
                break;
            }
            default:
                break;
        }
    }
    return 0;
}

int main(int argc, char** argv) {
    if (argc < 2) {
        printf("Trappy Virtual Machine (TVM) v2.0.0\n");
        printf("Usage: tvm <program.trpc> [--disasm]\n");
        return 1;
    }

    const char* filename = argv[1];
    Bytecode* bc = load_trpc(filename);
    if (!bc) {
        return 1;
    }

    if (argc >= 3 && strcmp(argv[2], "--disasm") == 0) {
        printf("[TRPC v2.0 Disassembly: %s]\n", filename);
        printf("Constants (%u):\n", bc->num_constants);
        for (uint32_t i = 0; i < bc->num_constants; i++) {
            printf("  [%04u] ", i);
            if (bc->constants[i].type == VAL_INT) printf("INT %lld\n", (long long)bc->constants[i].as.i);
            else if (bc->constants[i].type == VAL_FLOAT) printf("FLOAT %g\n", bc->constants[i].as.f);
            else if (bc->constants[i].type == VAL_STR) printf("STR \"%s\"\n", bc->constants[i].as.s);
            else printf("NULL\n");
        }
        printf("Instructions (%u):\n", bc->num_instructions);
        for (uint32_t i = 0; i < bc->num_instructions; i++) {
            printf("  %04u: OP 0x%02X, Operand %d\n", i, bc->instructions[i].opcode, bc->instructions[i].operand);
        }
        free_bytecode(bc);
        return 0;
    }

    VM vm;
    vm_init(&vm, bc);
    int res = vm_run(&vm);
    free_bytecode(bc);
    return res;
}
