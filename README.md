# Codex_20260122_file_sort_merger
Sort *.xy files and *.out files

## GUI 실행
```bash
python merge_tool.py
```

## 사용 방법 (요약)
- 탭에서 확장자를 선택한 뒤 `파일 추가`로 병합할 파일을 직접 선택합니다.
- `이 행 기준으로 컬럼 분석`을 눌러 컬럼을 읽은 후,
  - X축 기준 열을 선택하고,
  - Y축 병합 열을 원하는 순서대로 추가한 뒤 `선택 파일에 컬럼 설정 적용`을 눌러 저장합니다.
- .xy 파일은 `모든 .xy 파일에 공통 설정 적용`으로 한 번에 동일 설정을 적용할 수 있습니다.
- 맨 위에 있는 파일이 X축 기준이 되며, 파일 선택 순서가 기본 열 순서로 반영됩니다.
- 다중 선택 시 순서 확인 창에서 ▲/▼로 파일 순서를 조정한 뒤 확인할 수 있습니다.
- `선택 순서 정렬` 버튼을 누르면 처음 추가한 순서로 파일 목록을 되돌릴 수 있습니다.

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
