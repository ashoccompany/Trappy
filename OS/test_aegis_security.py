import unittest
import tkinter as tk
import trappy

# Ensure tests run headless without blocking on Tk mainloop
tk.Tk.mainloop = lambda self: self.update()

class TestAegisOSSecurity(unittest.TestCase):
    def setUp(self):
        with open("AegisOS.trappy", "r", encoding="utf-8") as f:
            self.aegis_code = f.read()

    def test_01_aegis_full_boot_and_gui_and_integrity(self):
        """Test full AegisOS boot, cwin GUI initialization, and clean security audit."""
        interp = trappy.run_trappy(self.aegis_code)
        self.assertTrue(interp.os_kernel.is_booted)
        self.assertEqual(interp.os_kernel.os_name, "AegisOS")
        self.assertEqual(interp.os_kernel.version, "1.5.0-HARDENED")
        
        # Verify GUI canvas was created via cwin
        self.assertIsNotNone(interp.gui)
        self.assertIsNotNone(interp.gui.canvas)
        
        # Verify 4 Exploit Guards are all activated
        guards = interp.os_kernel.settings["security.exploit_guards"]
        self.assertEqual(guards["canary"], 1)
        self.assertEqual(guards["nx_memory"], 1)
        self.assertEqual(guards["syscall_filter"], 1)
        self.assertEqual(guards["strict_bounds"], 1)

        # Verify integrity seals are intact
        jb_report = interp.os_kernel.jailbreak_check()
        self.assertEqual(jb_report["jailbroken"], 0)
        self.assertEqual(jb_report["status"], "SECURE")
        self.assertEqual(jb_report["violations_count"], 0)
        if interp.gui and interp.gui.root:
            try:
                interp.gui.root.destroy()
            except Exception:
                pass

    def test_02_anti_jailbreak_blocks_unauthorized_ring0_elevation(self):
        """Persona 2 jailbreak vector 1: Attempting to escalate privileges from Ring 3 to Ring 0."""
        attack_code = """
trst
    os_boot "AegisOS" "1.5.0-HARDENED"
    os_ring_set 3
    # Malicious attempt to elevate back to kernel ring
    os_ring_set 0
tren
"""
        with self.assertRaises(trappy.TrappySecurityError) as ctx:
            trappy.run_trappy(attack_code)
        self.assertIn("Ring 0 elevation", str(ctx.exception))

    def test_03_anti_jailbreak_blocks_unauthorized_vfs_tamper(self):
        """Persona 2 jailbreak vector 2: Attempting to overwrite /sys/security.conf or /bin/aegis_auth from Userland."""
        attack_code = """
trst
    os_boot "AegisOS" "1.5.0-HARDENED"
    os_ring_set 3
    # Malicious attempt to tamper with sealed kernel configuration
    os_vfs_write "/sys/security.conf" "ENFORCE=0"
tren
"""
        with self.assertRaises(trappy.TrappySecurityError) as ctx:
            trappy.run_trappy(attack_code)
        self.assertIn("Permission denied", str(ctx.exception))

    def test_04_anti_jailbreak_triggers_panic_on_corrupted_seals(self):
        """Persona 2 jailbreak vector 3: If an attacker modifies sealed state, jailbreak check panics."""
        interp = trappy.run_trappy(self.aegis_code)
        interp.os_kernel.vfs["/etc/hostname"]["content"] = "pwned-node"
        
        report = interp.os_kernel.jailbreak_check()
        self.assertEqual(report["jailbroken"], 1)
        self.assertEqual(report["status"], "VIOLATION_DETECTED")
        self.assertTrue(len(interp.os_kernel.jailbreak_events) > 0)
        if interp.gui and interp.gui.root:
            try:
                interp.gui.root.destroy()
            except Exception:
                pass

    def test_05_anti_exploit_blocks_memory_buffer_overflow(self):
        """Persona 2 jailbreak vector 4: Buffer overflow memory attack."""
        attack_code = """
trst
    os_boot "AegisOS" "1.5.0-HARDENED"
    os_exploit_guard "canary" 1
    os_exploit_guard "strict_bounds" 1
    mem_alloc 32 tit ptr
    mem_write ptr:64:255
tren
"""
        with self.assertRaises(trappy.TrappySecurityError) as ctx:
            trappy.run_trappy(attack_code)
        self.assertIn("Buffer boundary violation", str(ctx.exception))

    def test_06_anti_exploit_blocks_arbitrary_sys_exec_in_userland(self):
        """Persona 2 jailbreak vector 5: Shellcode / sys_exec invocation from Userland."""
        attack_code = """
trst
    os_boot "AegisOS" "1.5.0-HARDENED"
    os_ring_set 3
    sys_exec "whoami" tit res
tren
"""
        with self.assertRaises(trappy.TrappySecurityError) as ctx:
            trappy.run_trappy(attack_code)
        self.assertIn("Userland Ring", str(ctx.exception))

    def test_07_app_store_blocks_malicious_downloads(self):
        """Verify App Store blocklists untrusted packages."""
        attack_code = """
trst
    os_boot "AegisOS" "1.5.0-HARDENED"
    os_block_list "app" "unc0ver_trappy"
    os_app_download "https://untrusted.org/unc0ver_trappy.trappy" "unc0ver_trappy" tit res
tren
"""
        interp = trappy.run_trappy(attack_code)
        res = interp.global_env.get("res")
        self.assertEqual(res.get("status"), "blocked")

if __name__ == "__main__":
    unittest.main()
