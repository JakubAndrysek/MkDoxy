"""Run integration builds with retained output and bounded process lifetimes."""

import os
import signal
import subprocess
from pathlib import Path
from typing import Mapping


def run_build(
    command: list[str], root: Path, env: Mapping[str, str], timeout: float = 120
) -> subprocess.CompletedProcess[str]:
    log_path = root / "build.log"
    # Stream into a file so timeouts retain output, including non-UTF-8 diagnostics.
    with log_path.open("w", encoding="utf-8") as log:
        process = subprocess.Popen(
            command,
            cwd=root,
            env=env,
            stdout=log,
            stderr=subprocess.STDOUT,
            start_new_session=os.name == "posix",
        )
        try:
            returncode = process.wait(timeout=timeout)
        except BaseException as error:
            # Killing only the Python/MkDocs parent leaves its Doxygen child alive.
            if os.name == "posix":
                try:
                    os.killpg(process.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
            else:
                subprocess.run(
                    ["taskkill", "/F", "/T", "/PID", str(process.pid)],
                    stdout=log,
                    stderr=subprocess.STDOUT,
                    check=False,
                    timeout=10,
                )
                if process.poll() is None:
                    process.kill()
            process.wait()
            if isinstance(error, subprocess.TimeoutExpired):
                log.write(f"\nBuild timed out after {timeout} seconds; process tree terminated.\n")
            raise
    return subprocess.CompletedProcess(
        command, returncode, stdout=log_path.read_text(encoding="utf-8", errors="replace")
    )
