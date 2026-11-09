import unittest
import os
import shutil
import trappy

class TestAIV17(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = os.path.join(os.path.dirname(__file__), "tmp_ai_test")
        os.makedirs(self.tmp_dir, exist_ok=True)

    def tearDown(self):
        if os.path.exists(self.tmp_dir):
            shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_ai_neural_net_train_and_predict(self):
        model_path = os.path.join(self.tmp_dir, "test_net.json").replace("\\", "/")
        code = f"""
trst
    ai_net_new "classifier" [2, 4, 1] "sigmoid"
    ai_net_train "classifier" [[0.0, 0.0], [1.0, 1.0]] [[0.0], [1.0]] 200 0.5 tit loss
    ai_net_predict "classifier" [1.0, 1.0] tit pred
    ai_net_classify "classifier" [1.0, 1.0] 0.5 tit cls
    ai_net_save "classifier" "{model_path}"
    ai_net_load "restored" "{model_path}"
    ai_net_predict "restored" [1.0, 1.0] tit restored_pred
tren
"""
        interp = trappy.run_trappy(code)
        self.assertIn("classifier", interp.ai_models)
        self.assertIn("restored", interp.ai_models)
        loss = interp.global_env.get("loss")
        pred = interp.global_env.get("pred")
        cls_res = interp.global_env.get("cls")
        restored_pred = interp.global_env.get("restored_pred")

        self.assertIsInstance(loss, float)
        self.assertIsInstance(pred, list)
        self.assertEqual(len(pred), 1)
        self.assertEqual(cls_res, 1)
        self.assertAlmostEqual(pred[0], restored_pred[0], places=5)
        self.assertTrue(os.path.exists(model_path))

    def test_ai_agent_qlearning(self):
        agent_path = os.path.join(self.tmp_dir, "test_agent.json").replace("\\", "/")
        code = f"""
trst
    ai_agent_new "bot" ["left", "right", "jump"] 0.2 0.9 0.0
    ai_agent_act "bot" "state_start" tit act1
    ai_agent_reward "bot" "state_start" "jump" 10.0 "state_end"
    ai_agent_act "bot" "state_start" tit best_act
    ai_agent_save "bot" "{agent_path}"
    ai_agent_load "bot2" "{agent_path}"
    ai_agent_act "bot2" "state_start" tit loaded_act
tren
"""
        interp = trappy.run_trappy(code)
        self.assertIn("bot", interp.ai_agents)
        self.assertIn("bot2", interp.ai_agents)
        best_act = interp.global_env.get("best_act")
        loaded_act = interp.global_env.get("loaded_act")
        self.assertEqual(best_act, "jump")
        self.assertEqual(loaded_act, "jump")
        self.assertTrue(os.path.exists(agent_path))

    def test_ai_nlp_tokenize_and_embed(self):
        code = """
trst
    ai_tokenize "Hello Trappy OS AI!" tit tokens
    ai_embed tokens 8 tit vec
    ai_sim vec vec tit score_self
tren
"""
        interp = trappy.run_trappy(code)
        tokens = interp.global_env.get("tokens")
        vec = interp.global_env.get("vec")
        score_self = interp.global_env.get("score_self")

        self.assertEqual(tokens, ["hello", "trappy", "os", "ai"])
        self.assertEqual(len(vec), 8)
        self.assertAlmostEqual(score_self, 1.0, places=4)

    def test_ai_ngram_markov_generation(self):
        code = """
trst
    ai_ngram_train "corpus" "trappy is fast trappy is secure trappy is intelligent" 2
    ai_ngram_gen "corpus" "trappy" 5 tit gen_text
tren
"""
        interp = trappy.run_trappy(code)
        gen_text = interp.global_env.get("gen_text")
        self.assertIsInstance(gen_text, str)
        self.assertTrue(gen_text.startswith("trappy"))
        words = gen_text.split()
        self.assertGreaterEqual(len(words), 2)

    def test_ai_ui_widgets(self):
        code = """
trst
    ai_net_new "viz_net" [2, 3, 1] "sigmoid"
    ai_agent_new "viz_agent" ["up", "down"] 0.1 0.9 0.1
    txt "Bot: Ready to assist" tit chat_log
    ai_ui_net "viz_net" 10:10 200:150
    ai_ui_agent "viz_agent" 220:10 200:150
    ai_ui_chat chat_log 10:170 410:120
tren
"""
        interp = trappy.run_trappy(code)
        self.assertEqual(len(interp.ui_elements), 3)
        self.assertEqual(interp.ui_elements[0]["type"], "ai_ui_net")
        self.assertEqual(interp.ui_elements[0]["name"], "viz_net")
        self.assertEqual(interp.ui_elements[1]["type"], "ai_ui_agent")
        self.assertEqual(interp.ui_elements[1]["name"], "viz_agent")
        self.assertEqual(interp.ui_elements[2]["type"], "ai_ui_chat")

    def test_os_ai_security_and_assistant(self):
        code = """
trst
    os_boot "AegisOS" "1.7.0"
    os_ai_anomaly_check [15.0, 30.0, 5.0] tit safe_report
    os_ai_anomaly_check [99.0, 95.0, 500.0] tit threat_report
    os_ai_assistant "what is the system status?" tit assist_status
    os_ai_assistant "check security alert" tit assist_sec
tren
"""
        interp = trappy.run_trappy(code)
        safe_report = interp.global_env.get("safe_report")
        threat_report = interp.global_env.get("threat_report")
        assist_status = interp.global_env.get("assist_status")
        assist_sec = interp.global_env.get("assist_sec")

        self.assertIsInstance(safe_report, dict)
        self.assertIsInstance(threat_report, dict)
        self.assertEqual(safe_report["status"], "OPTIMAL")
        self.assertEqual(threat_report["status"], "CRITICAL")
        self.assertIn("AegisOS", assist_status)
        self.assertIn("SECURE", assist_sec)

    def test_ai_save_creates_nested_parent_dirs(self):
        nested_model = os.path.join(self.tmp_dir, "deep", "nested", "model.json").replace("\\", "/")
        nested_agent = os.path.join(self.tmp_dir, "deep", "nested", "agent.json").replace("\\", "/")
        code = f"""
trst
    ai_net_new "test_deep" [2, 1] "sigmoid"
    ai_net_save "test_deep" "{nested_model}"
    ai_agent_new "test_agent_deep" ["left", "right"] 0.1 0.9 0.1
    ai_agent_save "test_agent_deep" "{nested_agent}"
tren
"""
        interp = trappy.run_trappy(code)
        self.assertTrue(os.path.exists(nested_model))
        self.assertTrue(os.path.exists(nested_agent))

    def test_ai_load_missing_file_raises_clean_error(self):
        code = """
trst
    ai_net_load "ghost_net" "missing/dir/nonexistent.json"
tren
"""
        with self.assertRaises(trappy.TrappyError) as ctx:
            trappy.run_trappy(code)
        self.assertIn("not found", str(ctx.exception).lower())

    def test_file_write_creates_nested_parent_dirs(self):
        nested_log = os.path.join(self.tmp_dir, "logs", "2026", "audit.log").replace("\\", "/")
        code = f"""
trst
    file_write "{nested_log}":"test log entry"
    file_append "{nested_log}":" appended"
tren
"""
        trappy.run_trappy(code)
        self.assertTrue(os.path.exists(nested_log))
        with open(nested_log, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertEqual(content, "test log entry appended")

if __name__ == "__main__":
    unittest.main()
