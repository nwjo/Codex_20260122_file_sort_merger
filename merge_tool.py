import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


class MergeToolApp:
    def __init__(self, root):
        self.root = root
        self.root.title(".xy / .out 개별 설정 병합기")
        self.root.geometry("700x900")

        self.folder_list = []
        self.target_file = None

        # --- 1. 폴더 관리 영역 ---
        folder_frame = tk.LabelFrame(
            root,
            text="1. 폴더 목록 (맨 위 폴더가 X축 기준)",
            font=("맑은 고딕", 10, "bold"),
        )
        folder_frame.pack(pady=5, padx=10, fill=tk.X)

        list_frame = tk.Frame(folder_frame)
        list_frame.pack(fill=tk.X, padx=5, pady=5)

        self.listbox = tk.Listbox(list_frame, selectmode=tk.SINGLE, height=5)
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=self.listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.listbox.config(yscrollcommand=scrollbar.set)

        btn_frame = tk.Frame(folder_frame)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)

        tk.Button(btn_frame, text="📂 폴더 추가", command=self.add_folder).pack(
            side=tk.LEFT, padx=2
        )
        tk.Button(
            btn_frame,
            text="📂 하위폴더 몽땅 추가",
            command=self.add_subfolders,
            bg="#fff5cc",
        ).pack(side=tk.LEFT, padx=2)
        tk.Button(btn_frame, text="삭제", command=self.delete_selected).pack(
            side=tk.LEFT, padx=2
        )
        tk.Button(btn_frame, text="초기화", command=self.clear_all).pack(
            side=tk.LEFT, padx=2
        )

        tk.Button(btn_frame, text="▼", width=3, command=self.move_down).pack(
            side=tk.RIGHT, padx=2
        )
        tk.Button(btn_frame, text="▲", width=3, command=self.move_up).pack(
            side=tk.RIGHT, padx=2
        )

        # --- 2. 확장자별 설정 (탭) ---
        setting_frame = tk.LabelFrame(
            root,
            text="2. 확장자별 상세 설정 (탭을 눌러 각각 설정하세요)",
            font=("맑은 고딕", 10, "bold"),
        )
        setting_frame.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)

        self.notebook = ttk.Notebook(setting_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 탭 생성
        self.tab_xy = tk.Frame(self.notebook)
        self.tab_out = tk.Frame(self.notebook)

        self.notebook.add(self.tab_xy, text="  [.xy] 파일 설정  ")
        self.notebook.add(self.tab_out, text="  [.out] 파일 설정  ")

        # 각 탭에 UI 구성 (함수로 분리하여 코드 재사용)
        self.controls_xy = self.create_tab_content(self.tab_xy, ".xy")
        self.controls_out = self.create_tab_content(self.tab_out, ".out")

        # 탭 변경 이벤트 바인딩 (탭 바뀔 때마다 미리보기 자동 갱신)
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)

        # --- 3. 미리보기 창 (공통) ---
        preview_frame = tk.LabelFrame(root, text="3. 파일 내용 미리보기", font=("맑은 고딕", 9))
        preview_frame.pack(pady=5, padx=10, fill=tk.BOTH, expand=True)

        self.txt_preview = tk.Text(
            preview_frame, height=10, state="disabled", bg="#f9f9f9", font=("Consolas", 9)
        )
        self.txt_preview.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.lbl_preview_info = tk.Label(preview_frame, text="-", fg="blue", anchor="w")
        self.lbl_preview_info.pack(fill=tk.X, padx=5)

        # --- 4. 실행 버튼 ---
        run_frame = tk.Frame(root)
        run_frame.pack(pady=10, fill=tk.X, padx=10)

        self.btn_run = tk.Button(
            run_frame,
            text="🚀 설정대로 병합 시작",
            height=2,
            bg="lightblue",
            font=("맑은 고딕", 12, "bold"),
            command=self.run_merge,
        )
        self.btn_run.pack(fill=tk.X)

    def create_tab_content(self, parent, ext_name):
        """각 탭 안에 들어갈 설정 UI를 생성하고 컨트롤 변수들을 리턴"""
        frame = tk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # (1) 데이터 시작 행
        row_frame = tk.Frame(frame)
        row_frame.pack(fill=tk.X, pady=5)
        tk.Label(row_frame, text=f"[{ext_name}] 데이터 시작 행 번호:", font=("bold")).pack(
            side=tk.LEFT
        )

        spin_row = tk.Spinbox(row_frame, from_=1, to=1000, width=5, font=("bold"))
        spin_row.delete(0, "end")
        spin_row.insert(0, 1)
        spin_row.pack(side=tk.LEFT, padx=10)

        # 갱신 버튼
        btn_update = tk.Button(
            row_frame,
            text="이 행 기준으로 컬럼 분석 ⟳",
            bg="#e6e6fa",
            command=lambda: self.update_columns(ext_name, spin_row, combo_x, combo_y),
        )
        btn_update.pack(side=tk.LEFT)

        # (2) 컬럼 선택
        col_frame = tk.Frame(frame)
        col_frame.pack(fill=tk.X, pady=10)

        tk.Label(col_frame, text="X축 기준 열:").grid(row=0, column=0, sticky="e", padx=5)
        combo_x = ttk.Combobox(col_frame, state="readonly", width=40)
        combo_x.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(col_frame, text="Y축 병합 열:").grid(row=1, column=0, sticky="e", padx=5)
        combo_y = ttk.Combobox(col_frame, state="readonly", width=40)
        combo_y.grid(row=1, column=1, padx=5, pady=5)

        # 컨트롤 객체 반환
        return {
            "spin_row": spin_row,
            "combo_x": combo_x,
            "combo_y": combo_y,
        }

    # --- 이벤트 핸들러 ---
    def on_tab_change(self, event):
        """탭이 바뀔 때마다 해당 확장자의 파일로 미리보기를 변경"""
        selected_tab = self.notebook.select()
        tab_text = self.notebook.tab(selected_tab, "text").strip()

        target_ext = ".xy" if ".xy" in tab_text else ".out"
        self.load_preview_for_ext(target_ext)

    def load_preview_for_ext(self, ext):
        """특정 확장자의 파일을 찾아서 미리보기 창에 띄움"""
        if not self.folder_list:
            self.txt_preview.config(state="normal")
            self.txt_preview.delete(1.0, tk.END)
            self.txt_preview.insert(tk.END, "폴더를 먼저 추가해주세요.")
            self.txt_preview.config(state="disabled")
            return

        base_folder = self.folder_list[0]
        try:
            # 해당 확장자 파일 찾기
            files = [f for f in os.listdir(base_folder) if f.lower().endswith(ext)]

            self.txt_preview.config(state="normal")
            self.txt_preview.delete(1.0, tk.END)

            if not files:
                self.txt_preview.insert(
                    tk.END, f"경고: 첫 번째 폴더에 {ext} 파일이 없습니다."
                )
                self.lbl_preview_info.config(text=f"상태: {ext} 파일 없음")
            else:
                target_file = os.path.join(base_folder, files[0])
                self.lbl_preview_info.config(text=f"미리보기 파일: {files[0]} ({ext})")

                with open(target_file, "r", encoding="utf-8") as f:
                    for i in range(20):
                        line = f.readline()
                        if not line:
                            break
                        self.txt_preview.insert(tk.END, f"{i + 1:02d}: {line}")

            self.txt_preview.config(state="disabled")

        except Exception as e:
            self.lbl_preview_info.config(text=f"에러 발생: {e}")

    def update_columns(self, ext, spin_widget, combo_x, combo_y):
        """현재 탭의 설정(Start Row)으로 해당 확장자 파일의 컬럼을 분석"""
        if not self.folder_list:
            messagebox.showwarning("경고", "폴더를 추가해주세요.")
            return

        base_folder = self.folder_list[0]
        files = [f for f in os.listdir(base_folder) if f.lower().endswith(ext)]

        if not files:
            messagebox.showwarning("파일 없음", f"폴더에 {ext} 파일이 없습니다.")
            return

        try:
            start_row_idx = int(spin_widget.get()) - 1
            if start_row_idx < 0:
                start_row_idx = 0

            file_path = os.path.join(base_folder, files[0])
            found_data = None

            with open(file_path, "r", encoding="utf-8") as f:
                for i, line in enumerate(f):
                    if i == start_row_idx:
                        found_data = line.strip().split()
                        break

            if found_data:
                options = [f"Col {i} (값: {val})" for i, val in enumerate(found_data)]
                combo_x["values"] = options
                combo_y["values"] = options
                if len(options) > 0:
                    combo_x.current(0)
                if len(options) > 1:
                    combo_y.current(1)
                else:
                    combo_y.current(0)
                messagebox.showinfo(
                    "성공",
                    f"[{ext}] 설정 갱신 완료!\n{start_row_idx + 1}번째 행 데이터를 불러왔습니다.",
                )
            else:
                messagebox.showerror("실패", "해당 행을 찾을 수 없습니다.")

        except ValueError:
            messagebox.showerror("오류", "행 번호는 숫자여야 합니다.")
        except Exception as e:
            messagebox.showerror("오류", str(e))

    # --- 기존 폴더 함수들 ---
    def add_folder(self):
        d = filedialog.askdirectory()
        if d and d not in self.folder_list:
            self.folder_list.append(d)
            self.listbox.insert(tk.END, d)
            # 폴더 추가 즉시 현재 탭 미리보기 갱신
            current_tab = self.notebook.index(self.notebook.select())  # 0 or 1
            ext = ".xy" if current_tab == 0 else ".out"
            self.load_preview_for_ext(ext)

    def add_subfolders(self):
        p = filedialog.askdirectory()
        if p:
            subs = [
                os.path.join(p, f)
                for f in os.listdir(p)
                if os.path.isdir(os.path.join(p, f))
            ]
            subs.sort()
            for s in subs:
                if s not in self.folder_list:
                    self.folder_list.append(s)
                    self.listbox.insert(tk.END, s)
            # 갱신
            current_tab = self.notebook.index(self.notebook.select())
            ext = ".xy" if current_tab == 0 else ".out"
            self.load_preview_for_ext(ext)

    def delete_selected(self):
        sel = self.listbox.curselection()
        if sel:
            del self.folder_list[sel[0]]
            self.listbox.delete(sel[0])

    def clear_all(self):
        self.folder_list = []
        self.listbox.delete(0, tk.END)
        self.txt_preview.config(state="normal")
        self.txt_preview.delete(1.0, tk.END)
        self.txt_preview.config(state="disabled")

    def move_up(self):
        sel = self.listbox.curselection()
        if not sel or sel[0] == 0:
            return
        idx = sel[0]
        text = self.listbox.get(idx)
        self.listbox.delete(idx)
        self.listbox.insert(idx - 1, text)
        self.listbox.selection_set(idx - 1)
        self.folder_list[idx], self.folder_list[idx - 1] = (
            self.folder_list[idx - 1],
            self.folder_list[idx],
        )

    def move_down(self):
        sel = self.listbox.curselection()
        if not sel or sel[0] == len(self.folder_list) - 1:
            return
        idx = sel[0]
        text = self.listbox.get(idx)
        self.listbox.delete(idx)
        self.listbox.insert(idx + 1, text)
        self.listbox.selection_set(idx + 1)
        self.folder_list[idx], self.folder_list[idx + 1] = (
            self.folder_list[idx + 1],
            self.folder_list[idx],
        )

    # --- 병합 실행 ---
    def run_merge(self):
        if len(self.folder_list) < 2:
            messagebox.showerror("오류", "최소 2개 이상의 폴더가 필요합니다.")
            return

        # 1. 각 탭의 설정값 읽어오기
        settings = {}

        # .xy 설정 가져오기
        try:
            settings[".xy"] = {
                "start_row": int(self.controls_xy["spin_row"].get()) - 1,
                "x_idx": self.controls_xy["combo_x"].current(),
                "y_idx": self.controls_xy["combo_y"].current(),
            }
            settings[".out"] = {
                "start_row": int(self.controls_out["spin_row"].get()) - 1,
                "x_idx": self.controls_out["combo_x"].current(),
                "y_idx": self.controls_out["combo_y"].current(),
            }
        except ValueError:
            messagebox.showerror("오류", "행 번호 설정을 확인해주세요.")
            return

        # 2. 실행 준비
        target_folders = self.folder_list
        base_folder = target_folders[0]
        parent_dir = os.path.dirname(base_folder)
        output_dir = os.path.join(parent_dir, "Merged_Output")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        files = [f for f in os.listdir(base_folder) if f.lower().endswith((".xy", ".out"))]
        success_count = 0
        skipped_count = 0

        # 3. 파일 처리
        for filename in files:
            ext = os.path.splitext(filename)[1].lower()

            # 해당 확장자의 설정값 사용
            if ext not in settings:
                continue

            conf = settings[ext]

            # 컬럼 선택이 안 되어있으면 스킵
            if conf["x_idx"] == -1 or conf["y_idx"] == -1:
                skipped_count += 1
                continue

            combined_data = []

            # (A) 기준 파일 읽기
            try:
                with open(os.path.join(base_folder, filename), "r", encoding="utf-8") as f:
                    for i, line in enumerate(f):
                        if i < conf["start_row"]:
                            continue  # 지정한 행 이전은 스킵
                        parts = line.strip().split()
                        if len(parts) > max(conf["x_idx"], conf["y_idx"]):
                            combined_data.append(
                                [parts[conf["x_idx"]], parts[conf["y_idx"]]]
                            )
            except Exception:
                continue

            # (B) 나머지 폴더 읽기
            for folder in target_folders[1:]:
                target_path = os.path.join(folder, filename)
                if os.path.exists(target_path):
                    with open(target_path, "r", encoding="utf-8") as f:
                        lines = f.readlines()
                        # 데이터 영역만 추출
                        data_lines = (
                            lines[conf["start_row"] :] if len(lines) > conf["start_row"] else []
                        )

                        for i, line in enumerate(data_lines):
                            parts = line.strip().split()
                            if i < len(combined_data) and len(parts) > conf["y_idx"]:
                                combined_data[i].append(parts[conf["y_idx"]])
                            elif i < len(combined_data):
                                combined_data[i].append("")
                else:
                    pass

            # (C) 저장
            with open(os.path.join(output_dir, filename), "w", encoding="utf-8") as f:
                header = ["X-Axis"] + [os.path.basename(fd) for fd in target_folders]
                f.write("\t".join(header) + "\n")
                for row in combined_data:
                    f.write("\t".join(row) + "\n")

            success_count += 1

        msg = f"작업 완료!\n\n- 성공: {success_count}개\n"
        if skipped_count > 0:
            msg += f"- 건너뜀(설정 미비): {skipped_count}개\n"
        msg += f"\n저장 폴더: {output_dir}"

        messagebox.showinfo("완료", msg)


if __name__ == "__main__":
    root = tk.Tk()
    app = MergeToolApp(root)
    root.mainloop()
