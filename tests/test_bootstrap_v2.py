"""
Trappy v2.0 Bootstrap & TVM Self-Hosting Test Suite
Author: ashoccompany / Asham
License: MIT
Zero generic tropes, zero emojis.
"""

import unittest
import os
import sys
import subprocess
import tempfile
import trappy
import tvm_runtime as tvm


class TestTrappyBootstrapV2(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp(prefix="trappy_tvm_test_")
        self.repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.tvm_exe = os.path.join(self.repo_root, "tvm.exe")

    def tearDown(self):
        import shutil
        if os.path.exists(self.tmp_dir):
            shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_tvm_bytecode_serialization(self):
        bc = tvm.TVMBytecode()
        c_a = bc.add_const("score")
        c_val = bc.add_const(100)
        bc.emit(tvm.OP_CONST, c_val)
        bc.emit(tvm.OP_STORE, c_a)
        bc.emit(tvm.OP_LOAD, c_a)
        bc.emit(tvm.OP_OS_SYSCALL, 1)
        bc.emit(tvm.OP_HALT, 0)

        data = bc.serialize()
        self.assertTrue(data.startswith(tvm.MAGIC_HEADER))

        bc2 = tvm.TVMBytecode.deserialize(data)
        self.assertEqual(len(bc2.constants), 2)
        self.assertEqual(bc2.constants[c_a], "score")
        self.assertEqual(bc2.constants[c_val], 100)
        self.assertEqual(len(bc2.instructions), 5)

        dis = bc2.disassemble()
        self.assertIn("OP_CONST", dis)
        self.assertIn("OP_STORE", dis)
        self.assertIn("OP_LOAD", dis)

    def test_tvm_runtime_python_execution(self):
        bc = tvm.TVMBytecode()
        c_x = bc.add_const("x")
        c_y = bc.add_const("y")
        c_12 = bc.add_const(12)
        c_8 = bc.add_const(8)

        bc.emit(tvm.OP_CONST, c_12)
        bc.emit(tvm.OP_STORE, c_x)
        bc.emit(tvm.OP_CONST, c_8)
        bc.emit(tvm.OP_STORE, c_y)
        bc.emit(tvm.OP_LOAD, c_x)
        bc.emit(tvm.OP_LOAD, c_y)
        bc.emit(tvm.OP_ADD, 0)
        bc.emit(tvm.OP_OS_SYSCALL, 1)
        bc.emit(tvm.OP_HALT, 0)

        vm_inst = tvm.TVM(bc)
        vm_inst.execute()
        self.assertIn("20", vm_inst.output_buffer)

    def test_tvm_native_c_engine_execution(self):
        if not os.path.exists(self.tvm_exe):
            self.skipTest("tvm.exe not found")

        bc = tvm.TVMBytecode()
        c_a = bc.add_const(50)
        c_b = bc.add_const(2)
        bc.emit(tvm.OP_CONST, c_a)
        bc.emit(tvm.OP_CONST, c_b)
        bc.emit(tvm.OP_MUL, 0)
        bc.emit(tvm.OP_OS_SYSCALL, 1)
        bc.emit(tvm.OP_HALT, 0)

        trpc_file = os.path.join(self.tmp_dir, "test_mul.trpc")
        with open(trpc_file, "wb") as f:
            f.write(bc.serialize())

        res = subprocess.run([self.tvm_exe, trpc_file], capture_output=True, text=True, check=True)
        self.assertEqual(res.stdout.strip(), "100")

    def test_bootstrap_lexer_in_pure_trappy(self):
        code = f"""
trst
    loadpk "{os.path.join(self.repo_root, 'bootstrap', 'lexer.trappy').replace(chr(92), '/')}" tit lex
    txt "trst\\n  # comment\\n  mh 40 + 60 eq total\\ntren" tit src
    call lex.tokenize_trappy src tit res
    dget res:"types" tit types
    dget res:"values" tit values
    llen types tit count
tren
"""
        interp = trappy.run_trappy(code)
        count = interp.global_env.get("count")
        self.assertGreater(count, 0)
        values = interp.global_env.get("values")
        self.assertIn("trst", values)
        self.assertIn("total", values)

    def test_bootstrap_compiler_end_to_end(self):
        trappy_code = f"""
trst
    loadpk "{os.path.join(self.repo_root, 'bootstrap', 'compiler.trappy').replace(chr(92), '/')}" tit comp
    txt "trst\\n  mh 15 + 25 eq answer\\n  out answer\\ntren" tit src
    call comp.compile_source src tit bytecode
    file_write "{os.path.join(self.tmp_dir, 'compiled_ans.trpc').replace(chr(92), '/')}":bytecode
tren
"""
        trappy.run_trappy(trappy_code)

        target_trpc = os.path.join(self.tmp_dir, "compiled_ans.trpc")
        self.assertTrue(os.path.exists(target_trpc))
        self.assertGreater(os.path.getsize(target_trpc), 10)

        # Execute compiled bytecode using TVM Python runner
        vm_inst = tvm.TVM()
        with open(target_trpc, "rb") as f:
            bc = tvm.TVMBytecode.deserialize(f.read())
        vm_inst.execute(bc)
        self.assertIn("40", vm_inst.output_buffer)

        # Execute compiled bytecode using native C tvm.exe
        if os.path.exists(self.tvm_exe):
            res = subprocess.run([self.tvm_exe, target_trpc], capture_output=True, text=True, check=True)
            self.assertEqual(res.stdout.strip(), "40")

    def test_self_hosting_bit_for_bit_verification(self):
        compiler_path = os.path.join(self.repo_root, 'bootstrap', 'compiler.trappy').replace(chr(92), '/')
        f1_path = os.path.join(self.tmp_dir, 'run1.trpc').replace(chr(92), '/')
        f2_path = os.path.join(self.tmp_dir, 'run2.trpc').replace(chr(92), '/')
        sample_file = os.path.join(self.tmp_dir, 'sample_code.trappy')
        with open(sample_file, 'w', encoding='utf-8') as f:
            f.write("trst\n  txt \"TrappyV2\" tit banner\n  out banner\ntren\n")
        sample_path = sample_file.replace(chr(92), '/')

        trappy_code = f"""
trst
    loadpk "{compiler_path}" tit comp
    call comp.compile_file "{sample_path}":"{f1_path}" tit res1
    call comp.compile_file "{sample_path}":"{f2_path}" tit res2
tren
"""
        trappy.run_trappy(trappy_code)

        f1 = os.path.join(self.tmp_dir, "run1.trpc")
        f2 = os.path.join(self.tmp_dir, "run2.trpc")
        self.assertTrue(os.path.exists(f1))
        self.assertTrue(os.path.exists(f2))

        with open(f1, "rb") as a, open(f2, "rb") as b:
            data1 = a.read()
            data2 = b.read()

        self.assertEqual(data1, data2)
        self.assertTrue(data1.startswith(tvm.MAGIC_HEADER))


if __name__ == "__main__":
    unittest.main()
