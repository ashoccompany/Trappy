import unittest
import os
import shutil
import trappy

class TestTrappyV2Features(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = os.path.join(os.path.dirname(__file__), "tmp_v2_test")
        os.makedirs(self.tmp_dir, exist_ok=True)

    def tearDown(self):
        if os.path.exists(self.tmp_dir):
            shutil.rmtree(self.tmp_dir, ignore_errors=True)

    # 1. Comments
    def test_v2_comments_hash_slash_and_block(self):
        code = """
trst
    // Single line slash comment
    # Single line hash comment
    /* Multi-line
       block comment */
    mh 40 + 2 eq answer
tren
"""
        interp = trappy.run_trappy(code)
        self.assertEqual(interp.global_env.get("answer"), 42)

    # 2. Compound Booleans
    def test_v2_compound_booleans(self):
        code = """
trst
    mh 10 eq score
    mh 5 eq lives
    mh 0 eq flag1
    mh 0 eq flag2
    mh 0 eq flag3

    ifr score > 5 and lives > 0
        mh 1 eq flag1
    tren

    ifr score == 0 or lives == 5
        mh 1 eq flag2
    tren

    ifr not (score < 5) && (lives >= 5 || score == 100)
        mh 1 eq flag3
    tren
tren
"""
        interp = trappy.run_trappy(code)
        self.assertEqual(interp.global_env.get("flag1"), 1)
        self.assertEqual(interp.global_env.get("flag2"), 1)
        self.assertEqual(interp.global_env.get("flag3"), 1)

    # 3. Property Assignment (= and eq)
    def test_v2_property_assignment_syntax(self):
        code = """
trst
    add_obj "player"
        x: 0
        y: 0
    tren
    player.x = 10
    player.y eq 25
tren
"""
        interp = trappy.run_trappy(code)
        player = interp.global_env.get("player")
        self.assertEqual(player["x"], 10)
        self.assertEqual(player["y"], 25)

    # 4. Function Call Delimiters (: and ,)
    def test_v2_function_call_delimiters(self):
        code = """
trst
    fn add_two a:b
        mh a + b eq res
        return res
    tren

    call add_two 10:20 tit val1
    call add_two(30, 40) tit val2
tren
"""
        interp = trappy.run_trappy(code)
        self.assertEqual(interp.global_env.get("val1"), 30)
        self.assertEqual(interp.global_env.get("val2"), 70)

    # 5. efr (Else-IFr) Multi-Branch Control Flow
    def test_v2_efr_multi_branch(self):
        code = """
trst
    mh 85 eq score
    txt "none" tit rank

    ifr score >= 90
        txt "S" tit rank
    efr score >= 80
        txt "A" tit rank
    efr score >= 70
        txt "B" tit rank
    else
        txt "F" tit rank
    tren
tren
"""
        interp = trappy.run_trappy(code)
        self.assertEqual(interp.global_env.get("rank"), "A")

    # 6. brch & cas Pattern Matching
    def test_v2_brch_and_cas(self):
        code = """
trst
    txt "ATTACK" tit action
    mh 0 eq damage

    brch action
        cas "IDLE"
            mh 0 eq damage
        cas "MOVE"
            mh 1 eq damage
        cas "ATTACK"
            mh 50 eq damage
        othr
            mh -1 eq damage
    tren
tren
"""
        interp = trappy.run_trappy(code)
        self.assertEqual(interp.global_env.get("damage"), 50)

    # 7. Bracket Navigation & Slicing
    def test_v2_bracket_navigation_and_assignment(self):
        code = """
trst
    lst [100, 20, 5] eq stats
    mh stats[0] - 15 eq stats[0]
    stats[1] = 50
    stats[2] eq 10

    lst [[1, 2], [3, 4]] eq matrix
    matrix[1][0] = 99
tren
"""
        interp = trappy.run_trappy(code)
        stats = interp.global_env.get("stats")
        self.assertEqual(stats, [85, 50, 10])
        matrix = interp.global_env.get("matrix")
        self.assertEqual(matrix, [[1, 2], [99, 4]])

    # 8. Dictionary Manifest Literals
    def test_v2_dictionary_manifest_literals(self):
        code = """
trst
    add_var hero: {
        "name": "TrappyLegend",
        "level": 10,
        "attributes": {
            "strength": 40,
            "speed": 18.5
        }
    }
    hero["level"] = 11
    hero["attributes"]["strength"] = 45
tren
"""
        interp = trappy.run_trappy(code)
        hero = interp.global_env.get("hero")
        self.assertEqual(hero["name"], "TrappyLegend")
        self.assertEqual(hero["level"], 11)
        self.assertEqual(hero["attributes"]["strength"], 45)

    # 9. txtf String Interpolation
    def test_v2_txtf_string_interpolation(self):
        code = """
trst
    txt "Alex" tit player_name
    mh 2500 eq high_score
    txtf "Player {player_name} has scored {high_score} points!" tit banner
tren
"""
        interp = trappy.run_trappy(code)
        self.assertEqual(interp.global_env.get("banner"), "Player Alex has scored 2500 points!")

    # 10. loadpk Module System
    def test_v2_loadpk_engine(self):
        pkg_file = os.path.join(self.tmp_dir, "math_utils.trappy")
        with open(pkg_file, "w", encoding="utf-8") as f:
            f.write("""
trst
    fn square x
        mh x * x eq sq
        return sq
    tren
    mh 100 eq base_val
tren
""")
        clean_path = pkg_file.replace("\\", "/")
        code = f"""
trst
    loadpk "{clean_path}" tit mutils
    call mutils.square 7 tit result
    mh mutils.base_val eq base
tren
"""
        interp = trappy.run_trappy(code)
        self.assertEqual(interp.global_env.get("result"), 49)
        self.assertEqual(interp.global_env.get("base"), 100)

    # 11. 3D Camera & Shaded Polygons
    def test_v2_cam3d_and_poly3d(self):
        code = """
trst
    cam3d 0:200:500 0:0:0 60
    poly3d [[0, 100, 0], [-50, 0, -50], [50, 0, -50]] cyan
tren
"""
        interp = trappy.run_trappy(code)
        self.assertEqual(interp.camera_3d["fov"], 60.0)
        self.assertEqual(len(interp.poly3d_buffer), 1)
        self.assertEqual(interp.poly3d_buffer[0]["color"], "cyan")

    # 12. 2D Tilemap Viewport
    def test_v2_tilemap_viewport(self):
        code = """
trst
    tilemap_init "level_1" 20:20 16:16 "tiles.png"
    level_1[0][0] = 1
    level_1[0][1] = 2
    tilemap_draw "level_1" 0:0 160:160
tren
"""
        interp = trappy.run_trappy(code)
        self.assertIn("level_1", interp.tilemaps)
        self.assertEqual(interp.last_tilemap_draw["id"], "level_1")
        self.assertEqual(interp.last_tilemap_draw["rendered"], 2)

    # 13. Particle Emitter
    def test_v2_particle_emitter(self):
        code = """
trst
    particle_emitter "fire" 100:200 25 orange 1.5 -2.0 200
tren
"""
        interp = trappy.run_trappy(code)
        self.assertIn("fire", interp.particle_systems)
        self.assertEqual(len(interp.particle_systems["fire"]), 25)

    # 14. ADSR Synthesizer
    def test_v2_synth_adsr(self):
        code = """
trst
    synth_adsr "sawtooth" 440 300 25 50 0.8 100
tren
"""
        interp = trappy.run_trappy(code)
        self.assertIsNotNone(interp.last_synth_adsr)
        self.assertEqual(interp.last_synth_adsr["waveform"], "sawtooth")
        self.assertEqual(interp.last_synth_adsr["freq"], 440.0)

    # 15. Clipboard & Dialogs
    def test_v2_clipboard_and_dialogs(self):
        code = """
trst
    sys_clipboard_set "TrappyOS v2.0"
    sys_clipboard_get tit clip
    sys_dialog_open "Open Level" "*.dat" tit open_file
    sys_dialog_save "Save State" "*.dat" tit save_file
tren
"""
        interp = trappy.run_trappy(code)
        self.assertEqual(interp.global_env.get("clip"), "TrappyOS v2.0")
        self.assertTrue(len(str(interp.global_env.get("open_file"))) > 0)
        self.assertTrue(len(str(interp.global_env.get("save_file"))) > 0)

    # 16. UI Container & Tabs
    def test_v2_ui_container_and_tabs(self):
        code = """
trst
    ui_container "sidebar" "vertical" 0:0 200:600
        ui_tabs ["Home", "Settings", "Terminal"] tit active_tab
    tren
tren
"""
        interp = trappy.run_trappy(code)
        self.assertIn("sidebar", interp.ui_containers)
        self.assertEqual(interp.global_env.get("active_tab"), "Home")

    # 17. Micro-AI 2.0 (Conv2D, Pool2D, GRU, FFT, GA)
    def test_v2_micro_ai_conv2d_and_pool2d(self):
        code = """
trst
    lst [[1, 2, 3], [4, 5, 6], [7, 8, 9]] eq img
    lst [[1, 0], [0, 1]] eq kernel
    ai_conv2d img:kernel:1 tit conv_out
    ai_pool2d img:2 tit pool_out
tren
"""
        interp = trappy.run_trappy(code)
        conv = interp.global_env.get("conv_out")
        self.assertEqual(conv, [[6.0, 8.0], [12.0, 14.0]])
        pool = interp.global_env.get("pool_out")
        self.assertEqual(pool, [[5]])

    def test_v2_micro_ai_gru_step(self):
        code = """
trst
    ai_gru_new "npc_brain" 4 8
    lst [0.5, -0.2, 0.8, 0.1] eq in_vec
    ai_gru_step "npc_brain" in_vec tit hid_out
tren
"""
        interp = trappy.run_trappy(code)
        hid = interp.global_env.get("hid_out")
        self.assertEqual(len(hid), 8)

    def test_v2_micro_ai_audio_fft(self):
        code = """
trst
    lst [0.1, 0.5, 0.9, 0.2, -0.4, -0.8, 0.3, 0.7] eq wav
    ai_audio_fft wav 4 tit spectrum
tren
"""
        interp = trappy.run_trappy(code)
        spec = interp.global_env.get("spectrum")
        self.assertEqual(len(spec), 4)

    def test_v2_micro_ai_ga_evolution(self):
        code = """
trst
    ai_ga_init "race_bots" 10 [2, 4, 1]
    ai_ga_score "race_bots" 0 95.5
    ai_ga_score "race_bots" 1 42.0
    ai_ga_reproduce "race_bots" 0.05 0.3
tren
"""
        interp = trappy.run_trappy(code)
        self.assertIn("race_bots", interp.ga_populations)
        self.assertEqual(interp.ga_populations["race_bots"]["generation"], 2)

    # 18. TrappyOS 2.0 (MMU, Pipes, Drivers, Quantum)
    def test_v2_trappyos_mmu_and_paging(self):
        code = """
trst
    os_boot "TrappyOS" "2.0.0"
    os_mmu_page_alloc 1 4194304 8192 "RWX"
    os_mmu_protect 1 4194304 "R--"
tren
"""
        interp = trappy.run_trappy(code)
        self.assertIn(1, interp.os_kernel.mmu)
        self.assertEqual(interp.os_kernel.mmu[1][4194304]["perms"], "R--")

    def test_v2_trappyos_pipes_and_redirection(self):
        code = """
trst
    os_boot "TrappyOS" "2.0.0"
    os_pipe tit r_fd:w_fd
    os_redirect_stdout 1 w_fd
    os_redirect_stdin 2 r_fd
tren
"""
        interp = trappy.run_trappy(code)
        r = interp.global_env.get("r_fd")
        w = interp.global_env.get("w_fd")
        self.assertIn(r, interp.os_kernel.pipes)
        self.assertIn(w, interp.os_kernel.pipes)
        self.assertEqual(interp.os_kernel.process_streams[1]["stdout"], w)
        self.assertEqual(interp.os_kernel.process_streams[2]["stdin"], r)

    def test_v2_trappyos_dynamic_driver_architecture(self):
        code = """
trst
    os_boot "TrappyOS" "2.0.0"
    os_driver_register "VIRTUAL_AUDIO" 1 tit audio_driver
    os_driver_hook audio_driver:100 "on_audio_play"
tren
"""
        interp = trappy.run_trappy(code)
        drv = interp.global_env.get("audio_driver")
        self.assertIn(drv, interp.os_kernel.drivers)
        self.assertEqual(interp.os_kernel.drivers[drv]["name"], "VIRTUAL_AUDIO")
        self.assertEqual(interp.os_kernel.drivers[drv]["hooks"]["100"], "on_audio_play")

if __name__ == "__main__":
    unittest.main()
