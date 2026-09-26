from pathlib import Path

import pytest

def pytest_configure(config):
    config.addinivalue_line("markers", "step(n): workshop checkpoint that introduces this test")


def pytest_collection_modifyitems(config, items):
    step_file = Path(__file__).resolve().parent.parent / "STEP"
    current = int(step_file.read_text(encoding="utf-8").strip()) if step_file.exists() else 6
    for item in items:
        mark = item.get_closest_marker("step")
        if mark and int(mark.args[0]) > current:
            item.add_marker(pytest.mark.skip(reason=f"introduced at step {mark.args[0]}"))
