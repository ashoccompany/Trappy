import unittest
import trappy

class TestUIModernV16(unittest.TestCase):
    def test_card_parsing_and_evaluation(self):
        code = """
trst
    card 50:50 350:250 16 "#18181b" "#27272a"
tren
"""
        interp = trappy.run_trappy(code)
        self.assertEqual(len(interp.ui_elements), 1)
        el = interp.ui_elements[0]
        self.assertEqual(el["type"], "card")
        self.assertEqual(el["x1"], 50)
        self.assertEqual(el["y1"], 50)
        self.assertEqual(el["x2"], 350)
        self.assertEqual(el["y2"], 250)
        self.assertEqual(el["radius"], 16)
        self.assertEqual(el["fill"], "#18181b")

    def test_btn_modern_parsing_and_evaluation(self):
        code = """
trst
    fn on_click
        mh 1 eq clicked
    tren
    btn_modern "Launch OS" 100:100 140:40 trg on_click "#06b6d4"
tren
"""
        interp = trappy.run_trappy(code)
        self.assertEqual(len(interp.ui_elements), 1)
        el = interp.ui_elements[0]
        self.assertEqual(el["type"], "btn_modern")
        self.assertEqual(el["label"], "Launch OS")
        self.assertEqual(el["action"], "on_click")
        self.assertEqual(el["bg"], "#06b6d4")

    def test_toggle_parsing_and_evaluation(self):
        code = """
trst
    mh 1 eq wifi_enabled
    toggle wifi_enabled 200:150
tren
"""
        interp = trappy.run_trappy(code)
        self.assertEqual(len(interp.ui_elements), 1)
        el = interp.ui_elements[0]
        self.assertEqual(el["type"], "toggle")
        self.assertEqual(el["var"], "wifi_enabled")
        self.assertEqual(el["state"], 1)

    def test_progress_parsing_and_evaluation(self):
        code = """
trst
    progress 75 100 50:300 200:20 "#10b981" "#27272a"
tren
"""
        interp = trappy.run_trappy(code)
        self.assertEqual(len(interp.ui_elements), 1)
        el = interp.ui_elements[0]
        self.assertEqual(el["type"], "progress")
        self.assertEqual(el["pct"], 0.75)
        self.assertEqual(el["w"], 200)
        self.assertEqual(el["h"], 20)

    def test_badge_parsing_and_evaluation(self):
        code = """
trst
    badge "SECURE" 30:30 "secure"
tren
"""
        interp = trappy.run_trappy(code)
        self.assertEqual(len(interp.ui_elements), 1)
        el = interp.ui_elements[0]
        self.assertEqual(el["type"], "badge")
        self.assertEqual(el["text"], "SECURE")
        self.assertEqual(el["variant"], "secure")

    def test_slider_parsing_and_evaluation(self):
        code = """
trst
    mh 50 eq brightness
    slider brightness 0 100 50:350 200
tren
"""
        interp = trappy.run_trappy(code)
        self.assertEqual(len(interp.ui_elements), 1)
        el = interp.ui_elements[0]
        self.assertEqual(el["type"], "slider")
        self.assertEqual(el["var"], "brightness")
        self.assertEqual(el["val"], 50.0)

    def test_icon_parsing_and_evaluation(self):
        code = """
trst
    icon "shield" 10:10 24 "#06b6d4"
    icon "terminal" 40:10 24 "#10b981"
    icon "lock" 70:10 24 "#f59e0b"
tren
"""
        interp = trappy.run_trappy(code)
        self.assertEqual(len(interp.ui_elements), 3)
        self.assertEqual(interp.ui_elements[0]["name"], "shield")
        self.assertEqual(interp.ui_elements[1]["name"], "terminal")
        self.assertEqual(interp.ui_elements[2]["name"], "lock")

    def test_notify_toast_parsing_and_evaluation(self):
        code = """
trst
    os_boot "AegisCore" "1.6.0"
    notify_toast "System Notice" "v1.6 Kernel Active" "info"
tren
"""
        interp = trappy.run_trappy(code)
        self.assertEqual(len(interp.ui_elements), 1)
        el = interp.ui_elements[0]
        self.assertEqual(el["type"], "notify_toast")
        self.assertEqual(el["title"], "System Notice")
        self.assertEqual(el["msg"], "v1.6 Kernel Active")
        self.assertEqual(len(interp.os_kernel.notifications), 1)

    def test_ui_theme_switching(self):
        code = """
trst
    ui_theme cyber
tren
"""
        interp = trappy.run_trappy(code)
        self.assertEqual(interp.current_theme, "cyber")

    def test_ui_ease_statement(self):
        code = """
trst
    ui_ease smooth_x 0 100 0.5 "linear"
    ui_ease bounce_val 0 100 1.0 "bounce"
tren
"""
        interp = trappy.run_trappy(code)
        self.assertEqual(interp.global_env.get("smooth_x"), 50.0)
        self.assertAlmostEqual(interp.global_env.get("bounce_val"), 100.0, places=3)

    def test_ui_ease_call_expression(self):
        code = """
trst
    mh ui_ease(0:200:0.5:"ease_out") eq pos
    mh ui_ease(0:100:1.0:"ease_in") eq end_val
tren
"""
        interp = trappy.run_trappy(code)
        pos = interp.global_env.get("pos")
        end_val = interp.global_env.get("end_val")
        self.assertTrue(pos > 100.0)
        self.assertAlmostEqual(end_val, 100.0, places=3)

if __name__ == "__main__":
    unittest.main()
