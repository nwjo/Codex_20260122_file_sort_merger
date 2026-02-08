import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk


class MergeToolApp:
    def __init__(self, root):
        self.root = root
        self.root.title(".xy / .out 개별 설정 병합기")
        self.root.geometry("700x900")

        self.files_by_ext = {".xy": [], ".out": []}
        self.file_settings = {".xy": {}, ".out": {}}
        self.target_file = None

        # --- 1. 파일 관리 영역 ---
        folder_frame = tk.LabelFrame(
            root,
            text="1. 파일 목록 (순서가 열 순서, 맨 위 파일이 X축 기준)",
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

        tk.Button(btn_frame, text="📄 파일 추가", command=self.add_files).pack(
            side=tk.LEFT, padx=2
        )
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
        self.listbox.bind("<<ListboxSelect>>", self.on_file_select)

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
            command=lambda: self.update_columns(ext_name),
        )
        btn_update.pack(side=tk.LEFT)

        # (2) 컬럼 선택
        col_frame = tk.Frame(frame)
        col_frame.pack(fill=tk.X, pady=10)

        tk.Label(col_frame, text="X축 기준 열:").grid(row=0, column=0, sticky="e", padx=5)
        combo_x = ttk.Combobox(col_frame, state="readonly", width=40)
        combo_x.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(col_frame, text="Y축 병합 열(추가):").grid(
            row=1, column=0, sticky="e", padx=5
        )
        combo_y = ttk.Combobox(col_frame, state="readonly", width=40)
        combo_y.grid(row=1, column=1, padx=5, pady=5)
        tk.Button(
            col_frame,
            text="추가",
            command=lambda: self.add_y_column(ext_name),
        ).grid(row=1, column=2, padx=5)

        tk.Label(col_frame, text="Y축 열 순서:").grid(
            row=2, column=0, sticky="ne", padx=5
        )
        list_y = tk.Listbox(col_frame, height=6, selectmode=tk.SINGLE)
        list_y.grid(row=2, column=1, padx=5, pady=5, sticky="nsew")
        list_buttons = tk.Frame(col_frame)
        list_buttons.grid(row=2, column=2, sticky="n")
        tk.Button(
            list_buttons,
            text="▲",
            width=3,
            command=lambda: self.move_y_column(ext_name, -1),
        ).pack(pady=2)
        tk.Button(
            list_buttons,
            text="▼",
            width=3,
            command=lambda: self.move_y_column(ext_name, 1),
        ).pack(pady=2)
        tk.Button(
            list_buttons,
            text="삭제",
            command=lambda: self.remove_y_column(ext_name),
        ).pack(pady=2)

        tk.Button(
            frame,
            text="선택 파일에 컬럼 설정 적용",
            command=lambda: self.apply_file_settings(ext_name),
            bg="#e6f7ff",
        ).pack(pady=5, anchor="w")
        if ext_name == ".xy":
            tk.Button(
                frame,
                text="모든 .xy 파일에 공통 설정 적용",
                command=lambda: self.apply_common_settings(ext_name),
                bg="#e6ffe6",
            ).pack(pady=5, anchor="w")

        # 컨트롤 객체 반환
        return {
            "spin_row": spin_row,
            "combo_x": combo_x,
            "combo_y": combo_y,
            "list_y": list_y,
        }

    # --- 이벤트 핸들러 ---
    def on_tab_change(self, event):
        """탭이 바뀔 때마다 해당 확장자의 파일로 미리보기를 변경"""
        selected_tab = self.notebook.select()
        tab_text = self.notebook.tab(selected_tab, "text").strip()

        target_ext = ".xy" if ".xy" in tab_text else ".out"
        self.refresh_file_list(target_ext)
        self.load_preview_for_ext(target_ext)

    def on_file_select(self, event):
        target_ext = self.get_active_ext()
        if not target_ext:
            return
        self.load_preview_for_ext(target_ext)
        self.load_file_settings(target_ext)

    def load_preview_for_ext(self, ext):
        """특정 확장자의 파일을 찾아서 미리보기 창에 띄움"""
        if not self.files_by_ext[ext]:
            self.txt_preview.config(state="normal")
            self.txt_preview.delete(1.0, tk.END)
            self.txt_preview.insert(tk.END, "파일을 먼저 추가해주세요.")
            self.txt_preview.config(state="disabled")
            return

        try:
            file_path = self.get_selected_file(ext)
            self.txt_preview.config(state="normal")
            self.txt_preview.delete(1.0, tk.END)

            if not file_path:
                self.txt_preview.insert(tk.END, f"경고: 선택된 {ext} 파일이 없습니다.")
                self.lbl_preview_info.config(text=f"상태: {ext} 파일 없음")
            else:
                self.lbl_preview_info.config(
                    text=f"미리보기 파일: {os.path.basename(file_path)} ({ext})"
                )

                with open(file_path, "r", encoding="utf-8") as f:
                    for i in range(20):
                        line = f.readline()
                        if not line:
                            break
                        self.txt_preview.insert(tk.END, f"{i + 1:02d}: {line}")

            self.txt_preview.config(state="disabled")

        except Exception as e:
            self.lbl_preview_info.config(text=f"에러 발생: {e}")

    def update_columns(self, ext):
        """현재 탭의 설정(Start Row)으로 해당 확장자 파일의 컬럼을 분석"""
        selected_file = self.get_selected_file(ext)
        if not selected_file:
            messagebox.showwarning("경고", "파일을 선택해주세요.")
            return
        try:
            spin_widget = self.get_controls(ext)["spin_row"]
            start_row_idx = int(spin_widget.get()) - 1
            if start_row_idx < 0:
                start_row_idx = 0

            found_data = None

            with open(selected_file, "r", encoding="utf-8") as f:
                for i, line in enumerate(f):
                    if i == start_row_idx:
                        found_data = line.strip().split()
                        break

            if found_data:
                options = [f"Col {i} (값: {val})" for i, val in enumerate(found_data)]
                controls = self.get_controls(ext)
                controls["combo_x"]["values"] = options
                controls["combo_y"]["values"] = options
                if len(options) > 0:
                    controls["combo_x"].current(0)
                    controls["combo_y"].current(0)
                controls["list_y"].delete(0, tk.END)
                self.file_settings[ext].setdefault(selected_file, {})
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

    # --- 파일 관리 함수들 ---
    def add_files(self):
        ext = self.get_active_ext()
        if not ext:
            return
        files = filedialog.askopenfilenames(
            filetypes=[(f"{ext} 파일", f"*{ext}"), ("모든 파일", "*.*")]
        )
        if files:
            for file_path in files:
                if file_path not in self.files_by_ext[ext]:
                    self.files_by_ext[ext].append(file_path)
            self.refresh_file_list(ext)
            self.load_preview_for_ext(ext)

    def delete_selected(self):
        sel = self.listbox.curselection()
        if sel:
            ext = self.get_active_ext()
            if not ext:
                return
            del self.files_by_ext[ext][sel[0]]
            self.listbox.delete(sel[0])
            self.load_preview_for_ext(ext)

    def clear_all(self):
        ext = self.get_active_ext()
        if not ext:
            return
        self.files_by_ext[ext] = []
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
        ext = self.get_active_ext()
        if not ext:
            return
        self.files_by_ext[ext][idx], self.files_by_ext[ext][idx - 1] = (
            self.files_by_ext[ext][idx - 1],
            self.files_by_ext[ext][idx],
        )

    def move_down(self):
        sel = self.listbox.curselection()
        ext = self.get_active_ext()
        if not ext:
            return
        if not sel or sel[0] == len(self.files_by_ext[ext]) - 1:
            return
        idx = sel[0]
        text = self.listbox.get(idx)
        self.listbox.delete(idx)
        self.listbox.insert(idx + 1, text)
        self.listbox.selection_set(idx + 1)
        self.files_by_ext[ext][idx], self.files_by_ext[ext][idx + 1] = (
            self.files_by_ext[ext][idx + 1],
            self.files_by_ext[ext][idx],
        )

    # --- 병합 실행 ---
    def run_merge(self):
        if len(self.files_by_ext[".xy"]) < 2:
            messagebox.showerror("오류", "최소 2개 이상의 .xy 파일이 필요합니다.")
            return

        # 1. 각 탭의 설정값 읽어오기
        settings = {}

        # .xy 설정 가져오기
        try:
            settings[".xy"] = {
                "start_row": int(self.controls_xy["spin_row"].get()) - 1,
            }
            settings[".out"] = {
                "start_row": int(self.controls_out["spin_row"].get()) - 1,
            }
        except ValueError:
            messagebox.showerror("오류", "행 번호 설정을 확인해주세요.")
            return

        # 2. 실행 준비
        base_file = self.files_by_ext[".xy"][0]
        parent_dir = os.path.dirname(base_file)
        output_dir = os.path.join(parent_dir, "Merged_Output")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        success_count = 0
        skipped_count = 0

        # 3. 파일 처리 (.xy)
        xy_output = os.path.join(output_dir, "merged_xy.tsv")
        xy_settings = settings[".xy"]
        combined_data, header = self.merge_files(
            ".xy",
            xy_settings["start_row"],
        )
        if combined_data:
            with open(xy_output, "w", encoding="utf-8") as f:
                f.write("\t".join(header) + "\n")
                for row in combined_data:
                    f.write("\t".join(row) + "\n")
            success_count += 1
        else:
            skipped_count += 1

        # 4. 파일 처리 (.out)
        if self.files_by_ext[".out"]:
            out_output = os.path.join(output_dir, "merged_out.tsv")
            out_settings = settings[".out"]
            combined_data, header = self.merge_files(
                ".out",
                out_settings["start_row"],
            )
            if combined_data:
                with open(out_output, "w", encoding="utf-8") as f:
                    f.write("\t".join(header) + "\n")
                    for row in combined_data:
                        f.write("\t".join(row) + "\n")
                success_count += 1
            else:
                skipped_count += 1

        msg = f"작업 완료!\n\n- 성공: {success_count}개\n"
        if skipped_count > 0:
            msg += f"- 건너뜀(설정 미비): {skipped_count}개\n"
        msg += f"\n저장 폴더: {output_dir}"

        messagebox.showinfo("완료", msg)

    def merge_files(self, ext, start_row):
        files = self.files_by_ext[ext]
        if not files:
            return [], []

        base_file = files[0]
        base_settings = self.file_settings[ext].get(base_file, {})
        x_idx = base_settings.get("x_idx")
        if x_idx is None:
            messagebox.showerror("오류", "첫 번째 파일의 X축 열을 설정해주세요.")
            return [], []

        base_rows = self.read_rows(base_file, start_row)
        combined_data = []
        for row in base_rows:
            combined_data.append([row[x_idx] if x_idx < len(row) else ""])

        header = ["X-Axis"]
        for file_path in files:
            file_settings = self.file_settings[ext].get(file_path, {})
            y_cols = file_settings.get("y_cols", [])
            if not y_cols:
                messagebox.showwarning(
                    "경고", f"{os.path.basename(file_path)}의 Y축 열을 설정해주세요."
                )
                return [], []
            for col in y_cols:
                header.append(f"{os.path.basename(file_path)}[Col {col}]")

        for file_path in files:
            file_settings = self.file_settings[ext].get(file_path, {})
            y_cols = file_settings.get("y_cols", [])
            rows = self.read_rows(file_path, start_row)
            for row_idx, _ in enumerate(combined_data):
                if row_idx >= len(rows):
                    combined_data[row_idx].extend([""] * len(y_cols))
                    continue
                row = rows[row_idx]
                for col in y_cols:
                    combined_data[row_idx].append(row[col] if col < len(row) else "")

        return combined_data, header

    def read_rows(self, file_path, start_row):
        rows = []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                for i, line in enumerate(f):
                    if i < start_row:
                        continue
                    rows.append(line.strip().split())
        except Exception:
            return []
        return rows

    def add_y_column(self, ext):
        controls = self.get_controls(ext)
        selection = controls["combo_y"].current()
        if selection == -1:
            return
        label = controls["combo_y"].get()
        existing = controls["list_y"].get(0, tk.END)
        if label not in existing:
            controls["list_y"].insert(tk.END, label)

    def remove_y_column(self, ext):
        controls = self.get_controls(ext)
        sel = controls["list_y"].curselection()
        if sel:
            controls["list_y"].delete(sel[0])

    def move_y_column(self, ext, direction):
        controls = self.get_controls(ext)
        sel = controls["list_y"].curselection()
        if not sel:
            return
        idx = sel[0]
        new_idx = idx + direction
        if new_idx < 0 or new_idx >= controls["list_y"].size():
            return
        text = controls["list_y"].get(idx)
        controls["list_y"].delete(idx)
        controls["list_y"].insert(new_idx, text)
        controls["list_y"].selection_set(new_idx)

    def apply_file_settings(self, ext):
        file_path = self.get_selected_file(ext)
        if not file_path:
            messagebox.showwarning("경고", "파일을 선택해주세요.")
            return
        controls = self.get_controls(ext)
        x_idx = controls["combo_x"].current()
        if x_idx == -1:
            messagebox.showwarning("경고", "X축 열을 선택해주세요.")
            return
        y_cols = []
        for i in range(controls["list_y"].size()):
            label = controls["list_y"].get(i)
            if label.startswith("Col "):
                try:
                    idx_str = label.split()[1]
                    y_cols.append(int(idx_str))
                except (ValueError, IndexError):
                    continue
        if not y_cols:
            messagebox.showwarning("경고", "Y축 병합 열을 추가해주세요.")
            return
        self.file_settings[ext][file_path] = {"x_idx": x_idx, "y_cols": y_cols}
        messagebox.showinfo("저장", f"{os.path.basename(file_path)} 설정을 저장했습니다.")

    def apply_common_settings(self, ext):
        if not self.files_by_ext[ext]:
            messagebox.showwarning("경고", "파일을 먼저 추가해주세요.")
            return
        controls = self.get_controls(ext)
        x_idx = controls["combo_x"].current()
        if x_idx == -1:
            messagebox.showwarning("경고", "X축 열을 선택해주세요.")
            return
        y_cols = []
        for i in range(controls["list_y"].size()):
            label = controls["list_y"].get(i)
            if label.startswith("Col "):
                try:
                    idx_str = label.split()[1]
                    y_cols.append(int(idx_str))
                except (ValueError, IndexError):
                    continue
        if not y_cols:
            messagebox.showwarning("경고", "Y축 병합 열을 추가해주세요.")
            return
        for file_path in self.files_by_ext[ext]:
            self.file_settings[ext][file_path] = {"x_idx": x_idx, "y_cols": y_cols}
        messagebox.showinfo("저장", f"{len(self.files_by_ext[ext])}개 파일에 공통 설정을 적용했습니다.")

    def load_file_settings(self, ext):
        file_path = self.get_selected_file(ext)
        if not file_path:
            return
        controls = self.get_controls(ext)
        settings = self.file_settings[ext].get(file_path, {})
        if settings.get("x_idx") is not None and controls["combo_x"]["values"]:
            controls["combo_x"].current(settings["x_idx"])
        controls["list_y"].delete(0, tk.END)
        for col in settings.get("y_cols", []):
            controls["list_y"].insert(tk.END, f"Col {col}")

    def refresh_file_list(self, ext):
        self.listbox.delete(0, tk.END)
        for file_path in self.files_by_ext[ext]:
            self.listbox.insert(tk.END, file_path)

    def get_active_ext(self):
        selected_tab = self.notebook.select()
        tab_text = self.notebook.tab(selected_tab, "text").strip()
        return ".xy" if ".xy" in tab_text else ".out" if ".out" in tab_text else None

    def get_selected_file(self, ext):
        sel = self.listbox.curselection()
        if not sel:
            if self.files_by_ext[ext]:
                return self.files_by_ext[ext][0]
            return None
        return self.files_by_ext[ext][sel[0]]

    def get_controls(self, ext):
        return self.controls_xy if ext == ".xy" else self.controls_out


if __name__ == "__main__":
    root = tk.Tk()
    app = MergeToolApp(root)
    root.mainloop()
