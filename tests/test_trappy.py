import unittest
import os
import sys

# Ensure root repository directory is in sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import trappy

class TestLexer(unittest.TestCase):
    def test_integer_and_float_tokens(self):
        tokens = trappy.tokenize('42 3.14 0.05 100.25 0xFF')
        kinds_and_vals = [(t.kind, t.val) for t in tokens if t.kind != "EOF"]
        self.assertEqual(kinds_and_vals, [
            ("NUM", 42),
            ("NUM", 3.14),
            ("NUM", 0.05),
            ("NUM", 100.25),
            ("NUM", 255)
        ])

    def test_string_tokens(self):
        tokens = trappy.tokenize('"Hello World" "Trappy v1.1"')
        strings = [t.val for t in tokens if t.kind == "STR"]
        self.assertEqual(strings, ["Hello World", "Trappy v1.1"])

    def test_keywords_and_operators(self):
        tokens = trappy.tokenize('trst ifr then else grt lss sm eq tren == != >= <=')
        kinds = [t.kind for t in tokens if t.kind != "EOF"]
        self.assertIn("TRST", kinds)
        self.assertIn("IFR", kinds)
        self.assertIn("THEN", kinds)
        self.assertIn("ELSE", kinds)
        self.assertIn("==", kinds)
        self.assertIn("!=", kinds)

class TestRuntimeMathAndLogic(unittest.TestCase):
    def test_basic_arithmetic(self):
        code = '''
trst
    mh 15 + 25 eq res_add
    mh 50 - 18 eq res_sub
    mh 6 multi 7 eq res_mul
    mh 84 div 2 eq res_div
tren
'''
        interp = trappy.run_trappy(code)
        self.assertEqual(interp.global_env.get("res_add"), 40)
        self.assertEqual(interp.global_env.get("res_sub"), 32)
        self.assertEqual(interp.global_env.get("res_mul"), 42)
        self.assertEqual(interp.global_env.get("res_div"), 42.0)

    def test_float_math(self):
        code = '''
trst
    mh 3.5 + 2.5 eq sum_float
    mh 10.0 multi 0.5 eq half
tren
'''
        interp = trappy.run_trappy(code)
        self.assertAlmostEqual(interp.global_env.get("sum_float"), 6.0)
        self.assertAlmostEqual(interp.global_env.get("half"), 5.0)

    def test_advanced_math_operations(self):
        code = '''
trst
    mh sqrt 144 eq r_sqrt
    mh pow 2:8 eq r_pow
    mh abs -55 eq r_abs
    mh clamp 150:0:100 eq r_clamp
    mh dist 0:0:3:4 eq r_dist
tren
'''
        interp = trappy.run_trappy(code)
        self.assertEqual(interp.global_env.get("r_sqrt"), 12.0)
        self.assertEqual(interp.global_env.get("r_pow"), 256.0)
        self.assertEqual(interp.global_env.get("r_abs"), 55)
        self.assertEqual(interp.global_env.get("r_clamp"), 100)
        self.assertEqual(interp.global_env.get("r_dist"), 5.0)

class TestControlFlow(unittest.TestCase):
    def test_if_else_modern(self):
        code = '''
trst
    mh 25 eq val
    ifr val > 10
        txt "greater" tit res1
    else
        txt "lesser" tit res1
    tren

    ifr val < 5
        txt "yes" tit res2
    else
        txt "no" tit res2
    tren
tren
'''
        interp = trappy.run_trappy(code)
        self.assertEqual(interp.global_env.get("res1"), "greater")
        self.assertEqual(interp.global_env.get("res2"), "no")

    def test_if_legacy_then(self):
        code = '''
trst
    mh 42 eq x
    ifr x 10 grt
        txt "branch_true" tit outcome
    then
        txt "branch_false" tit outcome
    tren
tren
'''
        interp = trappy.run_trappy(code)
        self.assertEqual(interp.global_env.get("outcome"), "branch_true")

    def test_equality_conditions(self):
        code = '''
trst
    mh 100 eq a
    mh 100 eq b
    ifr a == b
        mh 1 eq flag_eq
    else
        mh 0 eq flag_eq
    tren
tren
'''
        interp = trappy.run_trappy(code)
        self.assertEqual(interp.global_env.get("flag_eq"), 1)

    def test_rep_loop_and_srep(self):
        code = '''
trst
    mh 0 eq counter
    rep 10
        mh counter + 1 eq counter
        ifr counter == 4
            srep
        tren
    tren
tren
'''
        interp = trappy.run_trappy(code)
        self.assertEqual(interp.global_env.get("counter"), 4)

    def test_custom_functions_with_return(self):
        code = '''
trst
    fmh multiply_sub a:b:c
        mh a multi b eq prod
        answ prod - c
    tren

    mh multiply_sub 6:7:2 eq result
tren
'''
        interp = trappy.run_trappy(code)
        self.assertEqual(interp.global_env.get("result"), 40)

class TestCollectionsAndData(unittest.TestCase):
    def test_dictionaries(self):
        code = '''
trst
    dict tit player
    dset player:"name":"Knight"
    dset player:"score":999
    dget player:"name" tit hero
    dget player:"score" tit pts
tren
'''
        interp = trappy.run_trappy(code)
        self.assertEqual(interp.global_env.get("hero"), "Knight")
        self.assertEqual(interp.global_env.get("pts"), 999)

    def test_lists(self):
        code = '''
trst
    lst 10 | 20 | 30 eq nums
    lpush nums:40
    llen nums tit total
    lget nums:0 tit first
    lpop nums tit popped
tren
'''
        interp = trappy.run_trappy(code)
        self.assertEqual(interp.global_env.get("total"), 4)
        self.assertEqual(interp.global_env.get("first"), 10)
        self.assertEqual(interp.global_env.get("popped"), 40)

    def test_each_collection_loop(self):
        code = '''
trst
    lst 1 | 2 | 3 | 4 eq items
    mh 0 eq total
    each it in items
        mh total + it eq total
    tren
tren
'''
        interp = trappy.run_trappy(code)
        self.assertEqual(interp.global_env.get("total"), 10)

    def test_json_dump_and_parse(self):
        code = '''
trst
    dict tit obj
    dset obj:"status":"ok"
    dset obj:"code":200
    json_dump obj tit json_text
    json_parse json_text tit restored
    dget restored:"status" tit status_val
tren
'''
        interp = trappy.run_trappy(code)
        self.assertEqual(interp.global_env.get("status_val"), "ok")

class TestPhysicsAndVectors(unittest.TestCase):
    def test_box_hit_collision(self):
        code = '''
trst
    # Overlapping boxes
    box_hit 10:10:20:20 15:15:20:20 tit hit_yes
    # Separated boxes
    box_hit 10:10:10:10 100:100:10:10 tit hit_no
tren
'''
        interp = trappy.run_trappy(code)
        self.assertEqual(interp.global_env.get("hit_yes"), 1)
        self.assertEqual(interp.global_env.get("hit_no"), 0)

    def test_vectors(self):
        code = '''
trst
    vec_add 10:20 5:8 tit v_res
    vec_mag 3:4 tit v_mag
tren
'''
        interp = trappy.run_trappy(code)
        self.assertEqual(interp.global_env.get("v_res"), [15, 28])
        self.assertEqual(interp.global_env.get("v_mag"), 5.0)

class TestFileIOSandbox(unittest.TestCase):
    def test_file_io_lifecycle(self):
        test_file = "unit_test_tmp.dat"
        code = f'''
trst
    file_write "{test_file}":"Trappy v1.1 Unit Test"
    file_exists "{test_file}" tit exists_flag
    file_read "{test_file}" tit read_back
    file_delete "{test_file}"
    file_exists "{test_file}" tit after_delete
tren
'''
        interp = trappy.run_trappy(code)
        self.assertEqual(interp.global_env.get("exists_flag"), 1)
        self.assertEqual(interp.global_env.get("read_back"), "Trappy v1.1 Unit Test")
        self.assertEqual(interp.global_env.get("after_delete"), 0)

    def test_path_traversal_protection(self):
        code = '''
trst
    file_write "../../etc/passwd":"malicious content"
tren
'''
        with self.assertRaises(trappy.TrappySecurityError):
            trappy.run_trappy(code)

class TestSecurityGuards(unittest.TestCase):
    def test_recursion_bomb_blocked(self):
        code = '''
trst
    fmh infinite_bomb n
        mh infinite_bomb n + 1 eq dummy
        answ dummy
    tren

    mh infinite_bomb 1 eq bomb_res
tren
'''
        with self.assertRaises(trappy.TrappySecurityError) as ctx:
            trappy.run_trappy(code)
        self.assertIn("Recursion bomb blocked", str(ctx.exception))

class TestNetworkingAndLoopback(unittest.TestCase):
    def test_virtual_loopback_socket(self):
        sock = trappy.VirtualLoopbackSocket(channel_id="test_channel")
        sock.sendall("Hello Trappy Loopback")
        received = sock.recv().decode("utf-8")
        self.assertEqual(received, "Hello Trappy Loopback")
        sock.close()


class TestBenchmarkStressAndScale(unittest.TestCase):
    def test_stress_loop_10k(self):
        code = """
trst
    mh 0 eq c
    rep 10000
        mh c + 1 eq c
    tren
tren
"""
        interp = trappy.run_trappy(code)
        self.assertEqual(interp.global_env.get("c"), 10000)

    def test_stress_list_pushes_5k(self):
        code = """
trst
    lst 0 eq my_list
    rep 5000
        lpush my_list:42
    tren
    llen my_list tit total_len
tren
"""
        interp = trappy.run_trappy(code)
        self.assertEqual(interp.global_env.get("total_len"), 5001)

    def test_rapid_dict_operations(self):
        code = """
trst
    dict tit map
    rep 1000
        dset map:"key":"val"
    tren
    dget map:"key" tit got
tren
"""
        interp = trappy.run_trappy(code)
        self.assertEqual(interp.global_env.get("got"), "val")

if __name__ == "__main__":
    unittest.main()
