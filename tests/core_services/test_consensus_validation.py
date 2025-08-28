import unittest
import json
from datetime import datetime

from src.core_services.consensus_validation import ConsensusDataValidator, ConsensusDataSerializer
from src.core_services.consensus_models import ConsensusInput, ConsensusRequest, AlgorithmMetadata, ValidationResult, AlgorithmType

class TestConsensusDataValidator(unittest.TestCase):
    def test_validate_consensus_input_valid(self):
        data = {
            "agent_id": "test_agent",
            "position": "agree",
            "confidence": 0.8,
            "reasoning": "logical deduction",
            "evidence": ["fact1", "fact2"],
            "metadata": {"source": "human"},
            "timestamp": datetime.now().isoformat()
        }
        result = ConsensusDataValidator.validate_consensus_input(data)
        self.assertTrue(result.is_valid)
        self.assertEqual(len(result.errors), 0)

    def test_validate_consensus_input_invalid(self):
        data = {
            "agent_id": "",
            "position": None,
            "confidence": 1.5,
        }
        result = ConsensusDataValidator.validate_consensus_input(data)
        self.assertFalse(result.is_valid)
        self.assertGreater(len(result.errors), 0)
        self.assertTrue(any("agent_id" in err for err in result.errors))
        self.assertTrue(any("position" in err for err in result.errors))
        self.assertTrue(any("confidence" in err for err in result.errors))

    def test_validate_consensus_request_valid(self):
        data = {
            "inputs": [
                {
                    "agent_id": "test_agent",
                    "position": "agree",
                    "confidence": 0.8,
                    "timestamp": datetime.now().isoformat()
                }
            ],
            "timeout": 60.0
        }
        result = ConsensusDataValidator.validate_consensus_request(data)
        self.assertTrue(result.is_valid)
        self.assertEqual(len(result.errors), 0)

    def test_validate_consensus_request_invalid(self):
        data = {
            "inputs": [],
            "timeout": -10.0
        }
        result = ConsensusDataValidator.validate_consensus_request(data)
        self.assertFalse(result.is_valid)
        self.assertGreater(len(result.errors), 0)
        self.assertIn("inputs", result.errors[0])
        self.assertIn("timeout", result.errors[1])

    def test_validate_algorithm_metadata_valid(self):
        data = {
            "name": "TestAlgo",
            "version": "1.0.0",
            "description": "A test algorithm",
            "algorithm_type": AlgorithmType.WEIGHTED_VOTING.value,
            "input_types": ["str"],
            "output_types": ["str"],
            "complexity": "medium",
            "accuracy": 0.9,
            "performance": "fast",
        }
        result = ConsensusDataValidator.validate_algorithm_metadata(data)
        self.assertTrue(result.is_valid)
        self.assertEqual(len(result.errors), 0)

    def test_validate_algorithm_metadata_invalid(self):
        data = {
            "name": "",
            "version": "invalid_version",
            "algorithm_type": "unknown",
            "complexity": "very_high",
        }
        result = ConsensusDataValidator.validate_algorithm_metadata(data)
        self.assertFalse(result.is_valid)
        self.assertGreater(len(result.errors), 0)
        self.assertTrue(any("Field required" in err for err in result.errors))
        self.assertIn("版本号建议使用语义化版本格式", result.warnings[0])
        self.assertTrue(any("algorithm_type" in err for err in result.errors))
        self.assertTrue(any("complexity" in err for err in result.errors))

class TestConsensusDataSerializer(unittest.TestCase):
    def test_serialize_to_json(self):
        data = {
            "key1": "value1",
            "key2": 123,
            "key3": True,
            "key4": datetime(2025, 8, 27, 10, 0, 0)
        }
        json_str = ConsensusDataSerializer.serialize_to_json(data)
        loaded_data = json.loads(json_str)
        self.assertEqual(loaded_data["key1"], "value1")
        self.assertEqual(loaded_data["key4"], "2025-08-27T10:00:00")

    def test_deserialize_from_json_valid(self):
        json_str = '{"agent_id": "test", "position": "pos", "confidence": 0.5, "timestamp": "2025-08-27T10:00:00"}'
        obj = ConsensusDataSerializer.deserialize_from_json(json_str, ConsensusInput)
        self.assertIsInstance(obj, ConsensusInput)
        self.assertEqual(obj.agent_id, "test")
        self.assertIsInstance(obj.timestamp, datetime)

    def test_deserialize_from_json_invalid(self):
        invalid_json_str = '{"agent_id": "test", "position": "pos", "confidence": "invalid"}'
        with self.assertRaisesRegex(ValueError, "反序列化失败"):
            ConsensusDataSerializer.deserialize_from_json(invalid_json_str, ConsensusInput)

        malformed_json_str = '{"agent_id": "test", "position": "pos", "confidence": 0.5'
        with self.assertRaisesRegex(ValueError, "JSON格式错误"):
            ConsensusDataSerializer.deserialize_from_json(malformed_json_str, ConsensusInput)

    def test_convert_legacy_format_debate_turn(self):
        legacy_data = {"role_id": "user1", "opinion": "My opinion", "round": 1}
        converted = ConsensusDataSerializer.convert_legacy_format(legacy_data, "debate_turn")
        self.assertIn("agent_id", converted)
        self.assertEqual(converted["agent_id"], "user1")
        self.assertEqual(converted["position"], "My opinion")
        self.assertEqual(converted["confidence"], 0.8)

    def test_convert_legacy_format_advanced_consensus_input(self):
        legacy_data = {"agent_id": "agentX", "position": 10.5, "confidence": 0.9, "cognitive_profile": {"bias": "none"}}
        converted = ConsensusDataSerializer.convert_legacy_format(legacy_data, "advanced_consensus_input")
        self.assertIn("agent_id", converted)
        self.assertEqual(converted["agent_id"], "agentX")
        self.assertEqual(converted["position"], 10.5)
        self.assertEqual(converted["confidence"], 0.9)
        self.assertIn("cognitive_profile", converted["metadata"])

    def test_convert_legacy_format_unsupported(self):
        legacy_data = {"data": "some_data"}
        with self.assertRaisesRegex(ValueError, "不支持的源格式"):
            ConsensusDataSerializer.convert_legacy_format(legacy_data, "unsupported_format")

if __name__ == "__main__":
    unittest.main()
