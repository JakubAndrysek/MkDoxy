"""Regressions for the build harness's failure and timeout handling."""

import os
import subprocess
import sys
import time
from pathlib import Path

import pytest

from .runner import run_build


def test_failed_build_retains_output(tmp_path: Path) -> None:
    program = "import sys; print('partial output'); print('build error', file=sys.stderr); sys.exit(7)"
    result = run_build([sys.executable, "-c", program], tmp_path, {})
    assert result.returncode == 7
    assert "partial output" in result.stdout
    assert "build error" in result.stdout
    assert (tmp_path / "build.log").read_text(encoding="utf-8") == result.stdout


@pytest.mark.skipif(sys.platform != "linux", reason="Uses /proc to distinguish terminated children from live ones")
def test_timeout_stops_child_and_retains_output(tmp_path: Path) -> None:
    child = (
        "import os, time; from pathlib import Path; "
        "Path('child.pid').write_text(str(os.getpid())); "
        "print('child started', flush=True); time.sleep(60)"
    )
    parent = (
        "import subprocess, sys; "
        "print('parent diagnostic', file=sys.stderr, flush=True); "
        f"subprocess.run([sys.executable, '-c', {child!r}], check=True)"
    )
    try:
        with pytest.raises(subprocess.TimeoutExpired):
            run_build([sys.executable, "-c", parent], tmp_path, {}, timeout=2)
        output = (tmp_path / "build.log").read_text(encoding="utf-8")
        assert "parent diagnostic" in output
        assert "child started" in output
        assert "Build timed out" in output
        pid = int((tmp_path / "child.pid").read_text(encoding="utf-8"))
        status = Path(f"/proc/{pid}/status")
        # Some container init processes reap orphans late. A zombie is terminated,
        # even though kill(pid, 0) would still report that its PID exists.
        # Signal delivery and child teardown can finish just after the parent
        # is reaped. Allow a bounded interval, without waiting for the 60s sleep.
        deadline = time.monotonic() + 2
        while True:
            try:
                status_text = status.read_text()
            except (FileNotFoundError, ProcessLookupError):
                # /proc can disappear before open or while reading the status.
                break
            state = next(line for line in status_text.splitlines() if line.startswith("State:"))
            if "Z (zombie)" in state or "X (dead)" in state:
                break
            assert time.monotonic() < deadline, state
            time.sleep(0.01)
    finally:
        # A failing regression must not itself leave a sleeping child behind.
        pid_file = tmp_path / "child.pid"
        if pid_file.exists():
            try:
                os.kill(int(pid_file.read_text()), 9)
            except ProcessLookupError:
                pass
