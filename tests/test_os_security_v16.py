import unittest
import trappy

class TestOSSecurityV16(unittest.TestCase):
    def test_negative_ring_blocked(self):
        code = """
trst
    os_boot "SecureKernel" "1.6.0"
    os_ring_set -1
tren
"""
        with self.assertRaises(trappy.TrappySecurityError) as ctx:
            trappy.run_trappy(code)
        self.assertIn("Invalid protection ring -1", str(ctx.exception))

    def test_excessive_ring_blocked(self):
        code = """
trst
    os_boot "SecureKernel" "1.6.0"
    os_ring_set 4
tren
"""
        with self.assertRaises(trappy.TrappySecurityError) as ctx:
            trappy.run_trappy(code)
        self.assertIn("Invalid protection ring 4", str(ctx.exception))

    def test_unauthorized_ring_elevation_blocked(self):
        code = """
trst
    os_boot "SecureKernel" "1.6.0"
    os_ring_set 3
    os_ring_set 2
tren
"""
        with self.assertRaises(trappy.TrappySecurityError) as ctx:
            trappy.run_trappy(code)
        self.assertIn("Unauthorized ring elevation", str(ctx.exception))

    def test_unauthorized_defense_config_blocked(self):
        code = """
trst
    os_boot "SecureKernel" "1.6.0"
    os_ring_set 3
    os_jailbreak_defend "panic"
tren
"""
        with self.assertRaises(trappy.TrappySecurityError) as ctx:
            trappy.run_trappy(code)
        self.assertIn("cannot modify jailbreak defense policy", str(ctx.exception))

    def test_invalid_defense_action_blocked(self):
        code = """
trst
    os_boot "SecureKernel" "1.6.0"
    os_jailbreak_defend "invalid_action"
tren
"""
        with self.assertRaises(trappy.TrappySecurityError) as ctx:
            trappy.run_trappy(code)
        self.assertIn("Invalid defense action", str(ctx.exception))

    def test_unauthorized_exploit_guard_blocked(self):
        code = """
trst
    os_boot "SecureKernel" "1.6.0"
    os_ring_set 3
    os_exploit_guard "canary" 0
tren
"""
        with self.assertRaises(trappy.TrappySecurityError) as ctx:
            trappy.run_trappy(code)
        self.assertIn("cannot configure exploit guards", str(ctx.exception))

    def test_unauthorized_integrity_seal_blocked(self):
        code = """
trst
    os_boot "SecureKernel" "1.6.0"
    os_ring_set 3
    os_integrity_seal "/etc/hostname" "rogue_key"
tren
"""
        with self.assertRaises(trappy.TrappySecurityError) as ctx:
            trappy.run_trappy(code)
        self.assertIn("cannot generate or modify integrity seals", str(ctx.exception))

    def test_unauthorized_defense_hook_and_block_list_blocked(self):
        code_hook = """
trst
    os_boot "SecureKernel" "1.6.0"
    os_ring_set 3
    os_defense_hook "test_hook" "panic"
tren
"""
        with self.assertRaises(trappy.TrappySecurityError):
            trappy.run_trappy(code_hook)

        code_block = """
trst
    os_boot "SecureKernel" "1.6.0"
    os_ring_set 3
    os_block_list "ip" "192.168.1.1"
tren
"""
        with self.assertRaises(trappy.TrappySecurityError):
            trappy.run_trappy(code_block)

    def test_vfs_protected_writes_by_ring3_blocked(self):
        code = """
trst
    os_boot "SecureKernel" "1.6.0"
    os_ring_set 3
    os_vfs_write "/etc/shadow" "root:x:0:0"
tren
"""
        with self.assertRaises(trappy.TrappySecurityError) as ctx:
            trappy.run_trappy(code)
        self.assertIn("Writes restricted to /apps/, /storage/, /tmp/", str(ctx.exception))

    def test_vfs_allowed_userland_writes(self):
        code = """
trst
    os_boot "SecureKernel" "1.6.0"
    os_ring_set 3
    os_vfs_write "/apps/demo/data.txt" "App Data Content"
    os_vfs_write "/storage/user/note.txt" "User Note Content"
    os_vfs_write "/tmp/scratch.tmp" "Temporary Cache"
    os_vfs_read "/apps/demo/data.txt" tit app_read
    os_vfs_read "/storage/user/note.txt" tit user_read
    os_vfs_read "/tmp/scratch.tmp" tit tmp_read
    os_vfs_del "/tmp/scratch.tmp"
tren
"""
        interp = trappy.run_trappy(code)
        self.assertEqual(interp.global_env.get("app_read"), "App Data Content")
        self.assertEqual(interp.global_env.get("user_read"), "User Note Content")
        self.assertEqual(interp.global_env.get("tmp_read"), "Temporary Cache")

    def test_sandboxed_app_scope_isolation(self):
        code = """
trst
    os_boot "SecureKernel" "1.6.0"
    txt "MASTER_KERNEL_KEY_999" tit kernel_secret
    txt "trst\n txt 'CORRUPTED' tit kernel_secret\n mh 777 eq app_local_val\ntren" tit rogue_app_code
    os_app_install "rogue_app" rogue_app_code tit inst_res
    os_app_launch "rogue_app" tit app_pid
tren
"""
        interp = trappy.run_trappy(code)
        self.assertEqual(interp.global_env.get("kernel_secret"), "MASTER_KERNEL_KEY_999")
        self.assertFalse(interp.global_env.has("app_local_val"))
        self.assertIsNotNone(interp.os_kernel.last_app_env)
        self.assertEqual(interp.os_kernel.last_app_env.get("app_local_val"), 777)

if __name__ == "__main__":
    unittest.main()
