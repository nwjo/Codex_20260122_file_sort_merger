# Codex_20260122_file_sort_merger
Sort *.xy files and *.out files

## GUI 실행
```bash
python merge_tool.py
```

## 독립 실행형 .exe 만들기 (Windows)
1. `pyinstaller` 설치:
   ```bash
   pip install -r requirements.txt
   ```
2. 빌드 스크립트 실행:
   ```bash
   python build_exe.py
   ```
3. 결과물은 `dist/merge_tool.exe`에 생성됩니다.
