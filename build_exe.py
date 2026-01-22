import shutil
import subprocess
import sys
from pathlib import Path


def main() -> int:
    repo_root = Path(__file__).resolve().parent
    script_path = repo_root / "merge_tool.py"

    if not script_path.exists():
        print("merge_tool.py를 찾을 수 없습니다.", file=sys.stderr)
        return 1

    pyinstaller = shutil.which("pyinstaller")
    if not pyinstaller:
        print(
            "pyinstaller가 설치되어 있지 않습니다. "
            "requirements.txt를 먼저 설치해주세요.",
            file=sys.stderr,
        )
        return 1

    build_cmd = [
        pyinstaller,
        "--onefile",
        "--windowed",
        "--name",
        "merge_tool",
        str(script_path),
    ]

    result = subprocess.run(build_cmd, cwd=repo_root)
    if result.returncode != 0:
        print("exe 빌드에 실패했습니다.", file=sys.stderr)
    else:
        print("빌드 완료: dist/merge_tool.exe")
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
