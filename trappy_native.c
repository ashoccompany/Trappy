/*
 * Trappy Native Engine & Self-Hosting Runtime v2.0.0
 * Pure Scratch-Built Native Implementation in ANSI C99.
 * Author: ashoccompany / Asham
 * License: MIT
 * Zero generic tropes, zero external dependencies.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <ctype.h>
#include <time.h>

#define TRAPPY_VERSION "2.0.0"

/* TVM 16 Opcodes */
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

/* Constant Types */
#define CONST_INT   0x01
#define CONST_FLOAT 0x02
#define CONST_STR   0x03
#define CONST_NULL  0x04

/* Runtime Value Types */
#define VAL_NULL    0
#define VAL_INT     1
#define VAL_FLOAT   2
#define VAL_STR     3
#define VAL_LIST    4
#define VAL_DICT    5

#define MAX_STACK      8192
#define MAX_CALL_STACK 1024
#define MAX_VARS       2048

struct Value;

typedef struct {
    struct Value* items;
    int count;
    int capacity;
} ListVal;

typedef struct {
    char** keys;
    struct Value* vals;
    int count;
    int capacity;
} DictVal;

typedef struct Value {
    uint8_t type;
    union {
        int64_t  i;
        double   f;
        char*    s;
        ListVal* list;
        DictVal* dict;
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
    int stack_base;
    char* target_var;
} CallFrame;

typedef struct {
    Value* constants;
    uint32_t num_constants;
    uint32_t cap_constants;
    Instruction* instructions;
    uint32_t num_instructions;
    uint32_t cap_instructions;
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

/* Value Constructors & Helpers */
static Value val_null(void) {
    Value v; v.type = VAL_NULL; v.as.i = 0; return v;
}

static Value val_int(int64_t i) {
    Value v; v.type = VAL_INT; v.as.i = i; return v;
}

static Value val_float(double f) {
    Value v; v.type = VAL_FLOAT; v.as.f = f; return v;
}

static Value val_str(const char* s) {
    Value v; v.type = VAL_STR; v.as.s = strdup(s ? s : ""); return v;
}

static Value val_list(void) {
    Value v; v.type = VAL_LIST;
    v.as.list = (ListVal*)calloc(1, sizeof(ListVal));
    v.as.list->capacity = 8;
    v.as.list->items = (Value*)calloc(v.as.list->capacity, sizeof(Value));
    return v;
}

static Value val_dict(void) {
    Value v; v.type = VAL_DICT;
    v.as.dict = (DictVal*)calloc(1, sizeof(DictVal));
    v.as.dict->capacity = 8;
    v.as.dict->keys = (char**)calloc(v.as.dict->capacity, sizeof(char*));
    v.as.dict->vals = (Value*)calloc(v.as.dict->capacity, sizeof(Value));
    return v;
}

static void val_free(Value v);

static Value val_clone(Value v) {
    if (v.type == VAL_STR) {
        return val_str(v.as.s);
    } else if (v.type == VAL_LIST && v.as.list) {
        Value n = val_list();
        for (int i = 0; i < v.as.list->count; i++) {
            if (n.as.list->count >= n.as.list->capacity) {
                n.as.list->capacity *= 2;
                n.as.list->items = (Value*)realloc(n.as.list->items, n.as.list->capacity * sizeof(Value));
            }
            n.as.list->items[n.as.list->count++] = val_clone(v.as.list->items[i]);
        }
        return n;
    } else if (v.type == VAL_DICT && v.as.dict) {
        Value d = val_dict();
        for (int i = 0; i < v.as.dict->count; i++) {
            if (d.as.dict->count >= d.as.dict->capacity) {
                d.as.dict->capacity *= 2;
                d.as.dict->keys = (char**)realloc(d.as.dict->keys, d.as.dict->capacity * sizeof(char*));
                d.as.dict->vals = (Value*)realloc(d.as.dict->vals, d.as.dict->capacity * sizeof(Value));
            }
            d.as.dict->keys[d.as.dict->count] = strdup(v.as.dict->keys[i]);
            d.as.dict->vals[d.as.dict->count] = val_clone(v.as.dict->vals[i]);
            d.as.dict->count++;
        }
        return d;
    }
    return v;
}

static void val_free(Value v) {
    if (v.type == VAL_STR && v.as.s) {
        free(v.as.s);
    } else if (v.type == VAL_LIST && v.as.list) {
        for (int i = 0; i < v.as.list->count; i++) {
            val_free(v.as.list->items[i]);
        }
        free(v.as.list->items);
        free(v.as.list);
    } else if (v.type == VAL_DICT && v.as.dict) {
        for (int i = 0; i < v.as.dict->count; i++) {
            free(v.as.dict->keys[i]);
            val_free(v.as.dict->vals[i]);
        }
        free(v.as.dict->keys);
        free(v.as.dict->vals);
        free(v.as.dict);
    }
}

static int val_is_truthy(Value v) {
    if (v.type == VAL_NULL) return 0;
    if (v.type == VAL_INT) return v.as.i != 0;
    if (v.type == VAL_FLOAT) return v.as.f != 0.0;
    if (v.type == VAL_STR) return (v.as.s && v.as.s[0] != '\0');
    if (v.type == VAL_LIST) return (v.as.list && v.as.list->count > 0);
    if (v.type == VAL_DICT) return (v.as.dict && v.as.dict->count > 0);
    return 0;
}

static char* val_to_string(Value v) {
    char buf[128];
    if (v.type == VAL_NULL) return strdup("null");
    if (v.type == VAL_INT) {
        snprintf(buf, sizeof(buf), "%lld", (long long)v.as.i);
        return strdup(buf);
    }
    if (v.type == VAL_FLOAT) {
        snprintf(buf, sizeof(buf), "%g", v.as.f);
        return strdup(buf);
    }
    if (v.type == VAL_STR) return strdup(v.as.s ? v.as.s : "");
    if (v.type == VAL_LIST) return strdup("[list]");
    if (v.type == VAL_DICT) return strdup("{dict}");
    return strdup("");
}

/* Bytecode Management */
static Bytecode* bc_new(void) {
    Bytecode* bc = (Bytecode*)calloc(1, sizeof(Bytecode));
    bc->cap_constants = 16;
    bc->constants = (Value*)calloc(bc->cap_constants, sizeof(Value));
    bc->cap_instructions = 64;
    bc->instructions = (Instruction*)calloc(bc->cap_instructions, sizeof(Instruction));
    return bc;
}

static void bc_free(Bytecode* bc) {
    if (!bc) return;
    for (uint32_t i = 0; i < bc->num_constants; i++) {
        val_free(bc->constants[i]);
    }
    free(bc->constants);
    free(bc->instructions);
    free(bc);
}

static int bc_add_const(Bytecode* bc, Value v) {
    for (uint32_t i = 0; i < bc->num_constants; i++) {
        if (bc->constants[i].type == v.type) {
            if (v.type == VAL_INT && bc->constants[i].as.i == v.as.i) return (int)i;
            if (v.type == VAL_FLOAT && bc->constants[i].as.f == v.as.f) return (int)i;
            if (v.type == VAL_STR && strcmp(bc->constants[i].as.s, v.as.s) == 0) return (int)i;
        }
    }
    if (bc->num_constants >= bc->cap_constants) {
        bc->cap_constants *= 2;
        bc->constants = (Value*)realloc(bc->constants, bc->cap_constants * sizeof(Value));
    }
    int idx = (int)bc->num_constants++;
    bc->constants[idx] = val_clone(v);
    return idx;
}

static int bc_emit(Bytecode* bc, uint8_t op, int32_t operand) {
    if (bc->num_instructions >= bc->cap_instructions) {
        bc->cap_instructions *= 2;
        bc->instructions = (Instruction*)realloc(bc->instructions, bc->cap_instructions * sizeof(Instruction));
    }
    int idx = (int)bc->num_instructions++;
    bc->instructions[idx].opcode = op;
    bc->instructions[idx].operand = operand;
    return idx;
}

static void bc_patch(Bytecode* bc, int idx, int32_t operand) {
    if (idx >= 0 && idx < (int)bc->num_instructions) {
        bc->instructions[idx].operand = operand;
    }
}

/* Binary .trpc Serialization & Deserialization */
static int bc_save_trpc(Bytecode* bc, const char* filepath) {
    FILE* f = fopen(filepath, "wb");
    if (!f) return 0;
    fwrite("TRPC\x02\x00", 1, 6, f);
    fwrite(&bc->num_constants, 4, 1, f);
    for (uint32_t i = 0; i < bc->num_constants; i++) {
        Value* cv = &bc->constants[i];
        if (cv->type == VAL_INT) {
            uint8_t t = CONST_INT; fwrite(&t, 1, 1, f);
            fwrite(&cv->as.i, 8, 1, f);
        } else if (cv->type == VAL_FLOAT) {
            uint8_t t = CONST_FLOAT; fwrite(&t, 1, 1, f);
            fwrite(&cv->as.f, 8, 1, f);
        } else if (cv->type == VAL_STR) {
            uint8_t t = CONST_STR; fwrite(&t, 1, 1, f);
            uint32_t slen = (uint32_t)strlen(cv->as.s);
            fwrite(&slen, 4, 1, f);
            fwrite(cv->as.s, 1, slen, f);
        } else {
            uint8_t t = CONST_NULL; fwrite(&t, 1, 1, f);
        }
    }
    fwrite(&bc->num_instructions, 4, 1, f);
    for (uint32_t i = 0; i < bc->num_instructions; i++) {
        fwrite(&bc->instructions[i].opcode, 1, 1, f);
        fwrite(&bc->instructions[i].operand, 4, 1, f);
    }
    fclose(f);
    return 1;
}

static Bytecode* bc_load_trpc(const char* filepath) {
    FILE* f = fopen(filepath, "rb");
    if (!f) return NULL;
    char header[6];
    if (fread(header, 1, 6, f) != 6 || memcmp(header, "TRPC\x02\x00", 6) != 0) {
        fclose(f);
        return NULL;
    }
    Bytecode* bc = bc_new();
    uint32_t num_consts = 0;
    if (fread(&num_consts, 4, 1, f) != 1) { fclose(f); bc_free(bc); return NULL; }
    for (uint32_t i = 0; i < num_consts; i++) {
        uint8_t ctype = 0; fread(&ctype, 1, 1, f);
        if (ctype == CONST_INT) {
            int64_t iv = 0; fread(&iv, 8, 1, f);
            Value v = val_int(iv); bc_add_const(bc, v); val_free(v);
        } else if (ctype == CONST_FLOAT) {
            double fv = 0; fread(&fv, 8, 1, f);
            Value v = val_float(fv); bc_add_const(bc, v); val_free(v);
        } else if (ctype == CONST_STR) {
            uint32_t sl = 0; fread(&sl, 4, 1, f);
            char* sb = (char*)malloc(sl + 1);
            fread(sb, 1, sl, f); sb[sl] = '\0';
            Value v; v.type = VAL_STR; v.as.s = sb;
            bc_add_const(bc, v); val_free(v);
        } else {
            Value v = val_null(); bc_add_const(bc, v);
        }
    }
    uint32_t num_inst = 0;
    if (fread(&num_inst, 4, 1, f) == 1) {
        for (uint32_t i = 0; i < num_inst; i++) {
            uint8_t op = 0; int32_t rand_val = 0;
            fread(&op, 1, 1, f);
            fread(&rand_val, 4, 1, f);
            bc_emit(bc, op, rand_val);
        }
    }
    fclose(f);
    return bc;
}

/* TVM Execution Engine */
static void vm_init(VM* vm, Bytecode* bc) {
    memset(vm, 0, sizeof(VM));
    vm->bc = bc;
}

static void vm_push(VM* vm, Value v) {
    if (vm->sp < MAX_STACK) {
        vm->stack[vm->sp++] = v;
    } else {
        fprintf(stderr, "[TVM Error]: Stack overflow\n");
    }
}

static Value vm_pop(VM* vm) {
    if (vm->sp > 0) return vm->stack[--vm->sp];
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

static void vm_syscall(VM* vm, int num) {
    if (num == 1) { /* SYS_PRINT (out) */
        Value v = vm_pop(vm);
        char* s = val_to_string(v);
        printf("%s\n", s);
        free(s);
        val_free(v);
    } else if (num == 2) { /* SYS_INPUT (answ) */
        char buf[1024];
        if (fgets(buf, sizeof(buf), stdin)) {
            size_t l = strlen(buf);
            if (l > 0 && buf[l - 1] == '\n') buf[l - 1] = '\0';
            vm_push(vm, val_str(buf));
        } else {
            vm_push(vm, val_str(""));
        }
    } else if (num == 3) { /* SYS_FILE_READ */
        Value fn_val = vm_pop(vm);
        const char* path = (fn_val.type == VAL_STR) ? fn_val.as.s : "";
        FILE* fp = fopen(path, "rb");
        if (fp) {
            fseek(fp, 0, SEEK_END);
            long sz = ftell(fp);
            fseek(fp, 0, SEEK_SET);
            char* c = (char*)malloc(sz + 1);
            if (c) {
                fread(c, 1, sz, fp);
                c[sz] = '\0';
                vm_push(vm, val_str(c));
                free(c);
            } else {
                vm_push(vm, val_str(""));
            }
            fclose(fp);
        } else {
            vm_push(vm, val_str(""));
        }
        val_free(fn_val);
    } else if (num == 4) { /* SYS_FILE_WRITE */
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
    } else if (num == 5) { /* SYS_CLOCK */
        vm_push(vm, val_int((int64_t)time(NULL)));
    } else {
        vm_push(vm, val_int(0));
    }
}

static int vm_execute(VM* vm) {
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
                const char* vname = "";
                if (instr.operand >= 0 && instr.operand < (int)vm->bc->num_constants) {
                    vname = vm->bc->constants[instr.operand].as.s;
                }
                vm_push(vm, vm_get_var(vm, vname));
                break;
            }
            case OP_STORE: {
                const char* vname = "";
                if (instr.operand >= 0 && instr.operand < (int)vm->bc->num_constants) {
                    vname = vm->bc->constants[instr.operand].as.s;
                }
                Value v = vm_pop(vm);
                vm_set_var(vm, vname, v);
                val_free(v);
                break;
            }
            case OP_ADD: {
                Value b = vm_pop(vm);
                Value a = vm_pop(vm);
                if (a.type == VAL_STR || b.type == VAL_STR) {
                    char* sa = val_to_string(a);
                    char* sb = val_to_string(b);
                    size_t la = strlen(sa), lb = strlen(sb);
                    char* res = (char*)malloc(la + lb + 1);
                    strcpy(res, sa); strcat(res, sb);
                    vm_push(vm, val_str(res));
                    free(sa); free(sb); free(res);
                } else if (a.type == VAL_FLOAT || b.type == VAL_FLOAT) {
                    double fa = (a.type == VAL_FLOAT) ? a.as.f : (double)a.as.i;
                    double fb = (b.type == VAL_FLOAT) ? b.as.f : (double)b.as.i;
                    vm_push(vm, val_float(fa + fb));
                } else {
                    vm_push(vm, val_int(a.as.i + b.as.i));
                }
                val_free(a); val_free(b);
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
                val_free(a); val_free(b);
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
                val_free(a); val_free(b);
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
                val_free(a); val_free(b);
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
                } else if (container.type == VAL_LIST && container.as.list) {
                    int64_t i = (idx.type == VAL_INT) ? idx.as.i : 0;
                    if (i >= 0 && i < container.as.list->count) {
                        vm_push(vm, val_clone(container.as.list->items[i]));
                    } else {
                        vm_push(vm, val_int(0));
                    }
                } else {
                    vm_push(vm, val_int(0));
                }
                val_free(idx); val_free(container);
                break;
            }
            case OP_INDEX_SET: {
                Value val = vm_pop(vm);
                Value idx = vm_pop(vm);
                Value container = vm_pop(vm);
                if (container.type == VAL_LIST && container.as.list) {
                    int64_t i = (idx.type == VAL_INT) ? idx.as.i : 0;
                    if (i >= 0 && i < container.as.list->count) {
                        val_free(container.as.list->items[i]);
                        container.as.list->items[i] = val_clone(val);
                    }
                }
                vm_push(vm, container);
                val_free(val); val_free(idx);
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
                    vm->call_stack[vm->csp].stack_base = vm->sp;
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
                vm_syscall(vm, instr.operand);
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

/* Native Trappy Source Lexer */
typedef enum {
    TOK_EOF,
    TOK_NAME,
    TOK_NUM,
    TOK_STR,
    TOK_OP,
    TOK_COLON,
    TOK_COMMA,
    TOK_DOT,
    TOK_LBRACKET,
    TOK_RBRACKET,
    TOK_LBRACE,
    TOK_RBRACE,
    TOK_LPAREN,
    TOK_RPAREN,
    TOK_EQ,
    TOK_NEQ,
    TOK_LT,
    TOK_GT,
    TOK_LTE,
    TOK_GTE,
    TOK_AND,
    TOK_OR,
    TOK_NOT
} TokenType;

typedef struct {
    TokenType type;
    char* val;
    int line;
} Token;

typedef struct {
    Token* tokens;
    int count;
    int capacity;
    int pos;
} TokenStream;

static TokenStream* tokenize_source(const char* src) {
    TokenStream* ts = (TokenStream*)calloc(1, sizeof(TokenStream));
    ts->capacity = 128;
    ts->tokens = (Token*)calloc(ts->capacity, sizeof(Token));
    int i = 0, n = (int)strlen(src), line = 1;

    while (i < n) {
        char c = src[i];
        if (c == '\n') { line++; i++; continue; }
        if (isspace(c)) { i++; continue; }

        /* Comment: # or // */
        if (c == '#' || (c == '/' && i + 1 < n && src[i + 1] == '/')) {
            while (i < n && src[i] != '\n') i++;
            continue;
        }
        /* Block comment: /* ... */
        if (c == '/' && i + 1 < n && src[i + 1] == '*') {
            i += 2;
            while (i + 1 < n && !(src[i] == '*' && src[i + 1] == '/')) {
                if (src[i] == '\n') line++;
                i++;
            }
            if (i + 1 < n) i += 2;
            continue;
        }

        /* String Literal */
        if (c == '"' || c == '\'') {
            char quote = c;
            i++;
            int start = i;
            while (i < n && src[i] != quote) i++;
            int len = i - start;
            char* s = (char*)malloc(len + 1);
            memcpy(s, src + start, len); s[len] = '\0';
            if (i < n) i++;

            if (ts->count >= ts->capacity) {
                ts->capacity *= 2;
                ts->tokens = (Token*)realloc(ts->tokens, ts->capacity * sizeof(Token));
            }
            ts->tokens[ts->count].type = TOK_STR;
            ts->tokens[ts->count].val = s;
            ts->tokens[ts->count].line = line;
            ts->count++;
            continue;
        }

        /* Number */
        if (isdigit(c) || (c == '-' && i + 1 < n && isdigit(src[i + 1]))) {
            int start = i++;
            while (i < n && (isdigit(src[i]) || src[i] == '.')) i++;
            int len = i - start;
            char* s = (char*)malloc(len + 1);
            memcpy(s, src + start, len); s[len] = '\0';

            if (ts->count >= ts->capacity) {
                ts->capacity *= 2;
                ts->tokens = (Token*)realloc(ts->tokens, ts->capacity * sizeof(Token));
            }
            ts->tokens[ts->count].type = TOK_NUM;
            ts->tokens[ts->count].val = s;
            ts->tokens[ts->count].line = line;
            ts->count++;
            continue;
        }

        /* Multi-character operators */
        if (i + 1 < n) {
            char c2 = src[i + 1];
            TokenType op_t = TOK_EOF;
            if (c == '=' && c2 == '=') op_t = TOK_EQ;
            else if (c == '!' && c2 == '=') op_t = TOK_NEQ;
            else if (c == '<' && c2 == '=') op_t = TOK_LTE;
            else if (c == '>' && c2 == '=') op_t = TOK_GTE;
            else if (c == '&' && c2 == '&') op_t = TOK_AND;
            else if (c == '|' && c2 == '|') op_t = TOK_OR;
            if (op_t != TOK_EOF) {
                if (ts->count >= ts->capacity) {
                    ts->capacity *= 2;
                    ts->tokens = (Token*)realloc(ts->tokens, ts->capacity * sizeof(Token));
                }
                char op_s[3] = { c, c2, '\0' };
                ts->tokens[ts->count].type = op_t;
                ts->tokens[ts->count].val = strdup(op_s);
                ts->tokens[ts->count].line = line;
                ts->count++;
                i += 2;
                continue;
            }
        }

        /* Single character punctuation & symbols */
        if (strchr(":=+-*/%<>()[]{};,", c)) {
            TokenType st = TOK_OP;
            if (c == ':') st = TOK_COLON;
            else if (c == ',') st = TOK_COMMA;
            else if (c == '.') st = TOK_DOT;
            else if (c == '[') st = TOK_LBRACKET;
            else if (c == ']') st = TOK_RBRACKET;
            else if (c == '{') st = TOK_LBRACE;
            else if (c == '}') st = TOK_RBRACE;
            else if (c == '(') st = TOK_LPAREN;
            else if (c == ')') st = TOK_RPAREN;
            else if (c == '<') st = TOK_LT;
            else if (c == '>') st = TOK_GT;
            else if (c == '=') st = TOK_EQ;

            if (ts->count >= ts->capacity) {
                ts->capacity *= 2;
                ts->tokens = (Token*)realloc(ts->tokens, ts->capacity * sizeof(Token));
            }
            char s[2] = { c, '\0' };
            ts->tokens[ts->count].type = st;
            ts->tokens[ts->count].val = strdup(s);
            ts->tokens[ts->count].line = line;
            ts->count++;
            i++;
            continue;
        }

        /* Identifier or Keyword */
        if (isalpha(c) || c == '_') {
            int start = i++;
            while (i < n && (isalnum(src[i]) || src[i] == '_')) i++;
            int len = i - start;
            char* s = (char*)malloc(len + 1);
            memcpy(s, src + start, len); s[len] = '\0';

            TokenType it = TOK_NAME;
            if (strcmp(s, "and") == 0) it = TOK_AND;
            else if (strcmp(s, "or") == 0) it = TOK_OR;
            else if (strcmp(s, "not") == 0) it = TOK_NOT;

            if (ts->count >= ts->capacity) {
                ts->capacity *= 2;
                ts->tokens = (Token*)realloc(ts->tokens, ts->capacity * sizeof(Token));
            }
            ts->tokens[ts->count].type = it;
            ts->tokens[ts->count].val = s;
            ts->tokens[ts->count].line = line;
            ts->count++;
            continue;
        }

        i++;
    }

    if (ts->count >= ts->capacity) {
        ts->capacity += 1;
        ts->tokens = (Token*)realloc(ts->tokens, ts->capacity * sizeof(Token));
    }
    ts->tokens[ts->count].type = TOK_EOF;
    ts->tokens[ts->count].val = strdup("");
    ts->tokens[ts->count].line = line;
    return ts;
}

static void free_tokens(TokenStream* ts) {
    if (!ts) return;
    for (int i = 0; i <= ts->count; i++) {
        free(ts->tokens[i].val);
    }
    free(ts->tokens);
    free(ts);
}

/* Native Trappy Bytecode Compiler */
static Token* ts_peek(TokenStream* ts) {
    return &ts->tokens[ts->pos];
}

static Token* ts_next(TokenStream* ts) {
    if (ts->pos < ts->count) return &ts->tokens[ts->pos++];
    return &ts->tokens[ts->count];
}

static int ts_match(TokenStream* ts, const char* str) {
    Token* t = ts_peek(ts);
    if (strcmp(t->val, str) == 0) {
        ts_next(ts);
        return 1;
    }
    return 0;
}

static void compile_expr(TokenStream* ts, Bytecode* bc);

static void compile_atom(TokenStream* ts, Bytecode* bc) {
    Token* t = ts_next(ts);
    if (t->type == TOK_NUM) {
        if (strchr(t->val, '.')) {
            Value v = val_float(atof(t->val));
            int c = bc_add_const(bc, v); val_free(v);
            bc_emit(bc, OP_CONST, c);
        } else {
            Value v = val_int(atoll(t->val));
            int c = bc_add_const(bc, v); val_free(v);
            bc_emit(bc, OP_CONST, c);
        }
    } else if (t->type == TOK_STR) {
        Value v = val_str(t->val);
        int c = bc_add_const(bc, v); val_free(v);
        bc_emit(bc, OP_CONST, c);
    } else if (t->type == TOK_NAME) {
        Value v = val_str(t->val);
        int c = bc_add_const(bc, v); val_free(v);
        bc_emit(bc, OP_LOAD, c);
        /* Check bracket indexing: var[idx] */
        if (ts_peek(ts)->type == TOK_LBRACKET) {
            ts_next(ts);
            compile_expr(ts, bc);
            ts_match(ts, "]");
            bc_emit(bc, OP_INDEX_GET, 0);
        }
    } else if (t->type == TOK_LPAREN) {
        compile_expr(ts, bc);
        ts_match(ts, ")");
    }
}

static void compile_expr(TokenStream* ts, Bytecode* bc) {
    compile_atom(ts, bc);
    Token* p = ts_peek(ts);
    while (p->type == TOK_OP && strchr("+-*/%", p->val[0])) {
        Token* op = ts_next(ts);
        compile_atom(ts, bc);
        if (op->val[0] == '+') bc_emit(bc, OP_ADD, 0);
        else if (op->val[0] == '-') bc_emit(bc, OP_SUB, 0);
        else if (op->val[0] == '*') bc_emit(bc, OP_MUL, 0);
        else if (op->val[0] == '/') bc_emit(bc, OP_DIV, 0);
        p = ts_peek(ts);
    }
}

static void compile_statement(TokenStream* ts, Bytecode* bc) {
    Token* t = ts_peek(ts);
    if (strcmp(t->val, "trst") == 0) {
        ts_next(ts);
        return;
    }
    if (strcmp(t->val, "tren") == 0) {
        ts_next(ts);
        return;
    }

    if (strcmp(t->val, "out") == 0 || strcmp(t->val, "inf") == 0) {
        ts_next(ts);
        compile_expr(ts, bc);
        bc_emit(bc, OP_OS_SYSCALL, 1);
        return;
    }

    if (strcmp(t->val, "add_var") == 0) {
        ts_next(ts);
        Token* vname = ts_next(ts);
        Value vn = val_str(vname->val);
        int c_name = bc_add_const(bc, vn); val_free(vn);
        if (ts_match(ts, ":") || ts_match(ts, "=")) {
            compile_expr(ts, bc);
            bc_emit(bc, OP_STORE, c_name);
        }
        return;
    }

    if (strcmp(t->val, "mh") == 0) {
        ts_next(ts);
        compile_expr(ts, bc);
        if (ts_match(ts, "eq") || ts_match(ts, "=")) {
            Token* target = ts_next(ts);
            Value vt = val_str(target->val);
            int ct = bc_add_const(bc, vt); val_free(vt);
            bc_emit(bc, OP_STORE, ct);
        }
        return;
    }

    if (strcmp(t->val, "txt") == 0) {
        ts_next(ts);
        Token* sval = ts_next(ts);
        Value vs = val_str(sval->val);
        int cs = bc_add_const(bc, vs); val_free(vs);
        bc_emit(bc, OP_CONST, cs);
        if (ts_match(ts, "tit") || ts_match(ts, "eq") || ts_match(ts, "=")) {
            Token* target = ts_next(ts);
            Value vt = val_str(target->val);
            int ct = bc_add_const(bc, vt); val_free(vt);
            bc_emit(bc, OP_STORE, ct);
        }
        return;
    }

    if (strcmp(t->val, "txtf") == 0) {
        ts_next(ts);
        Token* sval = ts_next(ts);
        char* raw = sval->val;
        char buf[2048] = {0};
        int bi = 0, ri = 0, has_accum = 0;
        while (raw[ri] != '\0') {
            if (raw[ri] == '{') {
                ri++;
                int vstart = ri;
                while (raw[ri] != '}' && raw[ri] != '\0') ri++;
                int vlen = ri - vstart;
                char vname[128] = {0};
                memcpy(vname, raw + vstart, vlen);
                if (raw[ri] == '}') ri++;

                Value v = val_str(buf);
                int cb = bc_add_const(bc, v); val_free(v);
                bc_emit(bc, OP_CONST, cb);

                Value vn = val_str(vname);
                int cv = bc_add_const(bc, vn); val_free(vn);
                bc_emit(bc, OP_LOAD, cv);
                bc_emit(bc, OP_ADD, 0);

                if (has_accum) {
                    bc_emit(bc, OP_ADD, 0);
                }
                has_accum = 1;
                bi = 0; buf[0] = '\0';
            } else {
                buf[bi++] = raw[ri++];
                buf[bi] = '\0';
            }
        }
        if (bi > 0 || !has_accum) {
            Value v = val_str(buf);
            int cb = bc_add_const(bc, v); val_free(v);
            bc_emit(bc, OP_CONST, cb);
            if (has_accum) {
                bc_emit(bc, OP_ADD, 0);
            }
        }
        if (ts_match(ts, "tit") || ts_match(ts, "eq") || ts_match(ts, "=")) {
            Token* target = ts_next(ts);
            Value vt = val_str(target->val);
            int ct = bc_add_const(bc, vt); val_free(vt);
            bc_emit(bc, OP_STORE, ct);
        }
        return;
    }

    if (strcmp(t->val, "file_read") == 0) {
        ts_next(ts);
        compile_expr(ts, bc);
        bc_emit(bc, OP_OS_SYSCALL, 3);
        if (ts_match(ts, "tit") || ts_match(ts, "eq") || ts_match(ts, "=")) {
            Token* target = ts_next(ts);
            Value vt = val_str(target->val);
            int ct = bc_add_const(bc, vt); val_free(vt);
            bc_emit(bc, OP_STORE, ct);
        }
        return;
    }

    if (strcmp(t->val, "file_write") == 0) {
        ts_next(ts);
        compile_expr(ts, bc); /* path */
        ts_match(ts, ":");
        compile_expr(ts, bc); /* content */
        bc_emit(bc, OP_OS_SYSCALL, 4);
        return;
    }

    if (strcmp(t->val, "call") == 0) {
        ts_next(ts);
        Token* fn_tok = ts_next(ts);
        Value vf = val_str(fn_tok->val);
        int cf = bc_add_const(bc, vf); val_free(vf);
        bc_emit(bc, OP_LOAD, cf);
        bc_emit(bc, OP_CALL, 0);
        if (ts_match(ts, "tit") || ts_match(ts, "eq") || ts_match(ts, "=")) {
            Token* target = ts_next(ts);
            Value vt = val_str(target->val);
            int ct = bc_add_const(bc, vt); val_free(vt);
            bc_emit(bc, OP_STORE, ct);
        }
        return;
    }

    /* Skip unhandled token */
    ts_next(ts);
}

static Bytecode* compile_source_to_bc(const char* src) {
    TokenStream* ts = tokenize_source(src);
    Bytecode* bc = bc_new();
    while (ts->pos < ts->count && ts_peek(ts)->type != TOK_EOF) {
        compile_statement(ts, bc);
    }
    bc_emit(bc, OP_HALT, 0);
    free_tokens(ts);
    return bc;
}

/* CLI Driver */
static void print_usage(void) {
    printf("Trappy Language Core Native Engine v%s\n", TRAPPY_VERSION);
    printf("100%% Self-Hosted TVM Execution Architecture\n");
    printf("Usage:\n");
    printf("  trappy <program.trappy>           Execute Trappy source code natively\n");
    printf("  trappy <program.trpc>             Execute pre-compiled TVM bytecode binary\n");
    printf("  trappy -c <in.trappy> -o <out.trpc> Compile Trappy source into TVM bytecode\n");
    printf("  trappy --disasm <file.trpc>       Disassemble TVM bytecode binary\n");
    printf("  trappy -v, --version              Show engine version information\n");
}

int main(int argc, char** argv) {
    if (argc < 2) {
        print_usage();
        return 1;
    }

    if (strcmp(argv[1], "-v") == 0 || strcmp(argv[1], "--version") == 0) {
        printf("Trappy Language Core Native Engine v%s\n", TRAPPY_VERSION);
        printf("Trappy Virtual Machine (TVM) v%s (ANSI C99 Native Engine)\n", TRAPPY_VERSION);
        return 0;
    }

    if (strcmp(argv[1], "--disasm") == 0 && argc >= 3) {
        Bytecode* bc = bc_load_trpc(argv[2]);
        if (!bc) {
            fprintf(stderr, "[Trappy Error]: Cannot load bytecode: %s\n", argv[2]);
            return 1;
        }
        printf("[TVM Disassembly: %s]\n", argv[2]);
        printf("Constants (%u):\n", bc->num_constants);
        for (uint32_t i = 0; i < bc->num_constants; i++) {
            char* s = val_to_string(bc->constants[i]);
            printf("  [%04u] %s\n", i, s);
            free(s);
        }
        printf("Instructions (%u):\n", bc->num_instructions);
        for (uint32_t i = 0; i < bc->num_instructions; i++) {
            printf("  %04u: OP 0x%02X, Operand %d\n", i, bc->instructions[i].opcode, bc->instructions[i].operand);
        }
        bc_free(bc);
        return 0;
    }

    if (strcmp(argv[1], "-c") == 0 && argc >= 3) {
        const char* in_file = argv[2];
        const char* out_file = (argc >= 5 && strcmp(argv[3], "-o") == 0) ? argv[4] : "a.trpc";

        FILE* f = fopen(in_file, "rb");
        if (!f) {
            fprintf(stderr, "[Trappy Error]: Cannot open file: %s\n", in_file);
            return 1;
        }
        fseek(f, 0, SEEK_END);
        long sz = ftell(f);
        fseek(f, 0, SEEK_SET);
        char* src = (char*)malloc(sz + 1);
        fread(src, 1, sz, f);
        src[sz] = '\0';
        fclose(f);

        Bytecode* bc = compile_source_to_bc(src);
        free(src);

        if (bc_save_trpc(bc, out_file)) {
            printf("[Trappy Compiler]: Compiled '%s' -> '%s' (%u instructions)\n", in_file, out_file, bc->num_instructions);
            bc_free(bc);
            return 0;
        } else {
            fprintf(stderr, "[Trappy Error]: Failed to write bytecode: %s\n", out_file);
            bc_free(bc);
            return 1;
        }
    }

    const char* filename = argv[1];
    if (strstr(filename, ".trpc")) {
        Bytecode* bc = bc_load_trpc(filename);
        if (!bc) {
            fprintf(stderr, "[Trappy Error]: Cannot load bytecode: %s\n", filename);
            return 1;
        }
        VM vm;
        vm_init(&vm, bc);
        int res = vm_execute(&vm);
        bc_free(bc);
        return res;
    }

    /* Execute .trappy source code directly */
    FILE* f = fopen(filename, "rb");
    if (!f) {
        fprintf(stderr, "[Trappy Error]: Cannot open file: %s\n", filename);
        return 1;
    }
    fseek(f, 0, SEEK_END);
    long sz = ftell(f);
    fseek(f, 0, SEEK_SET);
    char* src = (char*)malloc(sz + 1);
    fread(src, 1, sz, f);
    src[sz] = '\0';
    fclose(f);

    Bytecode* bc = compile_source_to_bc(src);
    free(src);

    VM vm;
    vm_init(&vm, bc);
    int res = vm_execute(&vm);
    bc_free(bc);
    return res;
}
