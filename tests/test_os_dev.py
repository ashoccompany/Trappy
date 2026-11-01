import unittest
import trappy

class TestOSKernelAndBoot(unittest.TestCase):
    def test_os_boot_and_shutdown(self):
        code = """
trst
    os_boot "TrappyKernel" "1.5.0"
    os_setting_get "os.name" "unknown" tit cur_name
    os_setting_get "os.version" "unknown" tit cur_ver
    os_shutdown
tren
"""
        interp = trappy.run_trappy(code)
        self.assertEqual(interp.global_env.get("cur_name"), "TrappyKernel")
        self.assertEqual(interp.global_env.get("cur_ver"), "1.5.0")
        self.assertFalse(interp.os_kernel.is_booted)

    def test_os_panic(self):
        code = """
trst
    os_boot "PanicOS" "1.5"
    os_panic "Critical Kernel Test Halt"
tren
"""
        interp = trappy.run_trappy(code)
        self.assertTrue(len(interp.os_kernel.jailbreak_events) > 0)
        self.assertEqual(interp.os_kernel.jailbreak_events[-1]["reason"], "Critical Kernel Test Halt")


class TestOSProcessManagement(unittest.TestCase):
    def test_proc_spawn_and_list(self):
        code = """
trst
    os_boot "ProcOS" "1.5"
    os_proc_spawn "daemon_worker" "trst out 'work' tren" tit p1
    os_proc_spawn "ui_shell" "trst out 'shell' tren" tit p2
    os_proc_list tit all_procs
    os_yield
tren
"""
        interp = trappy.run_trappy(code)
        p1 = interp.global_env.get("p1")
        p2 = interp.global_env.get("p2")
        all_procs = interp.global_env.get("all_procs")
        self.assertEqual(p1, 2)
        self.assertEqual(p2, 3)
        self.assertEqual(len(all_procs), 3)

    def test_proc_kill(self):
        code = """
trst
    os_boot "ProcOS" "1.5"
    os_proc_spawn "temp_proc" "trst tren" tit pid
    os_proc_kill pid
    os_proc_list tit procs
tren
"""
        interp = trappy.run_trappy(code)
        procs = interp.global_env.get("procs")
        temp = [p for p in procs if p["name"] == "temp_proc"][0]
        self.assertEqual(temp["state"], "TERMINATED")

    def test_ipc_send_and_recv(self):
        code = """
trst
    os_boot "IpcOS" "1.5"
    os_ipc_send "sys_channel" "HELO_PACKET"
    os_ipc_send "sys_channel" "DATA_PACKET"
    os_ipc_recv "sys_channel" tit m1
    os_ipc_recv "sys_channel" tit m2
    os_ipc_recv "sys_channel" tit m3
tren
"""
        interp = trappy.run_trappy(code)
        self.assertEqual(interp.global_env.get("m1"), "HELO_PACKET")
        self.assertEqual(interp.global_env.get("m2"), "DATA_PACKET")
        self.assertEqual(interp.global_env.get("m3"), "")


class TestOSVirtualFileSystem(unittest.TestCase):
    def test_vfs_read_write_list_stat(self):
        code = """
trst
    os_boot "VfsOS" "1.5"
    os_vfs_write "/etc/hostname" "trappy-box-1"
    os_vfs_read "/etc/hostname" tit host
    os_vfs_write "/etc/dns" "8.8.8.8"
    os_vfs_list "/etc" tit etc_files
    os_vfs_stat "/etc/hostname" tit fstat
tren
"""
        interp = trappy.run_trappy(code)
        self.assertEqual(interp.global_env.get("host"), "trappy-box-1")
        etc_files = interp.global_env.get("etc_files")
        self.assertIn("hostname", etc_files)
        self.assertIn("dns", etc_files)
        fstat = interp.global_env.get("fstat")
        self.assertEqual(fstat["type"], "file")
        self.assertTrue(len(fstat["hash"]) > 0)

    def test_vfs_virtual_proc(self):
        code = """
trst
    os_boot "ProcVfs" "1.5"
    os_vfs_read "/proc/version" tit p_ver
    os_vfs_read "/proc/procs" tit p_cnt
tren
"""
        interp = trappy.run_trappy(code)
        self.assertIn("ProcVfs", interp.global_env.get("p_ver"))
        self.assertEqual(interp.global_env.get("p_cnt"), "1")


class TestOSSettingsRegistry(unittest.TestCase):
    def test_settings_set_and_get(self):
        code = """
trst
    os_boot "SetOS" "1.5"
    os_setting_set "theme" "cyber_neon"
    os_setting_set "sound.vol" 95
    os_setting_get "theme" "dark" tit active_theme
    os_setting_get "sound.vol" 50 tit active_vol
    os_setting_get "missing.key" "fallback_val" tit fallback
    os_setting_dump tit full_dump
tren
"""
        interp = trappy.run_trappy(code)
        self.assertEqual(interp.global_env.get("active_theme"), "cyber_neon")
        self.assertEqual(interp.global_env.get("active_vol"), 95)
        self.assertEqual(interp.global_env.get("fallback"), "fallback_val")
        self.assertIn("theme", interp.global_env.get("full_dump"))


class TestOSAppEcosystem(unittest.TestCase):
    def test_app_install_launch_and_list(self):
        code = """
trst
    os_boot "AppStoreOS" "1.5"
    os_app_install "counter" "trst\n mh 42 eq app_val\ntren" tit install_res
    os_app_list tit app_catalog
    os_app_launch "counter" tit app_pid
tren
"""
        interp = trappy.run_trappy(code)
        res = interp.global_env.get("install_res")
        self.assertEqual(res.get("status"), "ok")
        catalog = interp.global_env.get("app_catalog")
        self.assertEqual(len(catalog), 1)
        self.assertEqual(catalog[0]["app_id"], "counter")
        self.assertEqual(interp.global_env.get("app_pid"), 2)


class TestOSTargetScreenAndHAL(unittest.TestCase):
    def test_screen_modes_phone_and_computer(self):
        code = """
trst
    os_boot "MobileOS" "1.5"
    os_screen_mode "phone" "portrait"
    os_hw_info tit phone_hw
    os_screen_mode "computer" "landscape"
    os_hw_info tit pc_hw
    os_battery_info tit bat
    os_touch_event tit touch
tren
"""
        interp = trappy.run_trappy(code)
        phone_hw = interp.global_env.get("phone_hw")
        self.assertEqual(phone_hw["device_type"], "phone")
        self.assertEqual(phone_hw["screen_resolution"], "380x720")

        pc_hw = interp.global_env.get("pc_hw")
        self.assertEqual(pc_hw["device_type"], "computer")
        self.assertEqual(pc_hw["screen_resolution"], "1024x700")

        bat = interp.global_env.get("bat")
        self.assertTrue(bat["level"] > 0)
        self.assertIn("type", interp.global_env.get("touch"))


class TestOSAntiJailbreakDefenses(unittest.TestCase):
    def test_integrity_seals_and_verification(self):
        code = """
trst
    os_boot "SecureOS" "1.5"
    os_integrity_seal "/etc/hostname" "secret_passphrase"
    os_integrity_verify "/etc/hostname" "secret_passphrase" tit verify_ok
    os_integrity_verify "/etc/hostname" "wrong_password" tit verify_bad
    os_jailbreak_check tit jb_clean
tren
"""
        interp = trappy.run_trappy(code)
        self.assertEqual(interp.global_env.get("verify_ok"), 1)
        self.assertEqual(interp.global_env.get("verify_bad"), 0)
        clean_report = interp.global_env.get("jb_clean")
        self.assertEqual(clean_report["status"], "SECURE")
        self.assertEqual(clean_report["jailbroken"], 0)

    def test_unauthorized_ring0_elevation_blocked(self):
        code = """
trst
    os_boot "SecureOS" "1.5"
    os_ring_set 3
    os_ring_set 0
tren
"""
        with self.assertRaises(trappy.TrappySecurityError) as ctx:
            trappy.run_trappy(code)
        self.assertIn("Ring 0 elevation", str(ctx.exception))


class TestOSAntiExploitDefenses(unittest.TestCase):
    def test_memory_canary_bounds_guard(self):
        code = """
trst
    os_boot "GuardOS" "1.5"
    os_exploit_guard "canary" 1
    mem_alloc 32 tit ptr
    mem_write ptr:10:99
    mem_read ptr:10 tit val
    mem_write ptr:50:255
tren
"""
        with self.assertRaises(trappy.TrappySecurityError) as ctx:
            trappy.run_trappy(code)
        self.assertIn("Anti-Exploit: Buffer boundary violation", str(ctx.exception))

    def test_userland_sys_exec_blocked(self):
        code = """
trst
    os_boot "GuardOS" "1.5"
    os_ring_set 3
    sys_exec "echo attack" tit out_res
tren
"""
        with self.assertRaises(trappy.TrappySecurityError) as ctx:
            trappy.run_trappy(code)
        self.assertIn("Userland Ring", str(ctx.exception))


class TestOSCustomDefensesAndPermissions(unittest.TestCase):
    def test_permissions_grant_revoke_check(self):
        code = """
trst
    os_boot "DefenseOS" "1.5"
    os_perm_grant "game_app" "AUDIO"
    os_perm_grant "game_app" "UI"
    os_perm_check "game_app" "AUDIO" tit has_audio
    os_perm_check "game_app" "CAMERA" tit has_camera
    os_perm_revoke "game_app" "AUDIO"
    os_perm_check "game_app" "AUDIO" tit audio_after_revoke
tren
"""
        interp = trappy.run_trappy(code)
        self.assertEqual(interp.global_env.get("has_audio"), 1)
        self.assertEqual(interp.global_env.get("has_camera"), 0)
        self.assertEqual(interp.global_env.get("audio_after_revoke"), 0)

    def test_firewall_rule_and_block_list(self):
        code = """
trst
    os_boot "DefenseOS" "1.5"
    os_firewall_rule "untrusted_app" "block"
    os_defense_hook "network_intrusion" "isolate"
    os_block_list "app" "bad_malware"
    os_app_install "bad_malware" "trst tren" tit blocked_res
tren
"""
        interp = trappy.run_trappy(code)
        blocked_res = interp.global_env.get("blocked_res")
        self.assertEqual(blocked_res.get("status"), "blocked")


class TestOSUICompositor(unittest.TestCase):
    def test_ui_window_taskbar_and_render_headless(self):
        code = """
trst
    os_boot "DesktopOS" "1.5"
    os_screen_mode "computer" "landscape"
    os_ui_window "FileManager" 40 40 400 300 tit fm_win
    os_ui_taskbar "bottom" "#18181b"
    os_ui_notify "System" "Welcome to DesktopOS v1.5" "info"
    os_ui_render
tren
"""
        interp = trappy.run_trappy(code)
        self.assertEqual(interp.global_env.get("fm_win"), "win_1")
        self.assertEqual(len(interp.os_kernel.windows), 1)
        self.assertEqual(len(interp.os_kernel.notifications), 1)


if __name__ == "__main__":
    unittest.main()
