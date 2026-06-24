"""Validator: the all.py runner discovers validators and fails when any validator fails."""
import os
import subprocess
import sys
import textwrap

HERE = os.path.dirname(os.path.abspath(__file__))
ALL_PY = os.path.join(HERE, "all.py")


def _run_all(target: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, ALL_PY, "--target", target, "--no-node"],
        capture_output=True,
        text=True,
    )


def test_discovers_the_real_validators():
    import importlib.util

    spec = importlib.util.spec_from_file_location("all_runner", ALL_PY)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    found = mod.discover_validators(HERE)
    assert any(p.endswith("test_runner.py") for p in found)
    assert len(found) >= 3  # tree, placeholders, mock_llm, runner, ...


def test_passing_target_exits_zero(tmp_path):
    (tmp_path / "test_ok.py").write_text("def test_ok():\n    assert True\n")
    result = _run_all(str(tmp_path))
    assert result.returncode == 0, result.stdout + result.stderr


def test_failing_target_exits_nonzero(tmp_path):
    (tmp_path / "test_ok.py").write_text("def test_ok():\n    assert True\n")
    (tmp_path / "test_bad.py").write_text(
        textwrap.dedent(
            """
            def test_bad():
                assert False, "deliberate failure"
            """
        )
    )
    result = _run_all(str(tmp_path))
    assert result.returncode != 0, "runner must propagate a validator failure"
