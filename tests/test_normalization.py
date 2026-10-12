import importlib.util
from pathlib import Path
import unittest

spec=importlib.util.spec_from_file_location("normalization", Path(__file__).resolve().parents[1]/"analysis/normalize_outcomes.py")
normalization=importlib.util.module_from_spec(spec)
spec.loader.exec_module(normalization)

class NormalizationTests(unittest.TestCase):
    def test_empty_at_limit_is_uniformly_truncated_without_mutating_source(self):
        for stage in ({"finish_reason":"length"}, {"details":{"raw_response":{"done_reason":"length"}}}):
            source={"terminal_outcome":"empty_response","correct":False,"stages":[stage]}
            result=normalization.normalize(source)
            self.assertEqual(result["terminal_outcome"],"truncated_response")
            self.assertEqual(source["terminal_outcome"],"empty_response")
            self.assertFalse(result["correct"])

    def test_normal_empty_and_success_are_preserved(self):
        for label in ("empty_response","correct","runtime_error"):
            source={"terminal_outcome":label,"correct":label=="correct","stages":[{"finish_reason":"stop"}]}
            self.assertEqual(normalization.normalize(source)["terminal_outcome"],label)
