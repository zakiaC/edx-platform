from pathlib import Path

from ingestion_tester.config import load_config


def test_load_config():
    path = Path(__file__).parent.parent / "scenarios" / "scenarios.yaml"
    scenarios = load_config(path)
    assert len(scenarios) >= 10
    assert scenarios[0].id
