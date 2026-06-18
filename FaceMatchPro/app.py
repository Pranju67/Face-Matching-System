"""
FaceMatch Pro - Main Application
A professional face similarity and verification desktop app.
Built with CustomTkinter, OpenCV, NumPy.
"""

import os
import sys
import threading
import datetime
import tkinter as tk
from tkinter import filedialog, messagebox
from typing import Optional, Dict, Any

# ── Ensure local modules resolve ──────────────────────────────────────────────
sys.path.insert(0, os.path.dirname(__file__))

from database import get_db, connect_database
from face_matcher import FaceMatcher
from settings import get_settings
from utils import export_csv, format_timestamp, short_filename, score_color, make_report_id

try:
    import customtkinter as ctk
    CTK_AVAILABLE = True
except ImportError:
    CTK_AVAILABLE = False

try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import matplotlib
    matplotlib.use("TkAgg")
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    MPL_AVAILABLE = True
except ImportError:
    MPL_AVAILABLE = False

# ── Colour tokens ──────────────────────────────────────────────────────────────
C = {
    "bg":       "#0F172A",
    "card":     "#1E293B",
    "card2":    "#253044",
    "border":   "#334155",
    "accent":   "#8B5CF6",
    "accent2":  "#6366F1",
    "success":  "#10B981",
    "warning":  "#F59E0B",
    "error":    "#EF4444",
    "text":     "#F8FAFC",
    "subtext":  "#94A3B8",
    "hover":    "#3B4D6B",
}

FONT = ("Segoe UI", 10)
FONT_BOLD = ("Segoe UI", 10, "bold")

if CTK_AVAILABLE:
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")


# ══════════════════════════════════════════════════════════════════════════════
#  Helper widgets
# ══════════════════════════════════════════════════════════════════════════════

def _label(parent, text, size=10, bold=False, color=None, **kw):
    color = color or C["text"]
    weight = "bold" if bold else "normal"
    if CTK_AVAILABLE:
        return ctk.CTkLabel(parent, text=text,
                            font=ctk.CTkFont(family="Segoe UI", size=size, weight=weight),
                            text_color=color, **kw)
    else:
        return tk.Label(parent, text=text, font=("Segoe UI", size, weight),
                        fg=color, bg=C["card"], **kw)


def _button(parent, text, command=None, color=None, text_color="white",
            width=120, height=36, **kw):
    color = color or C["accent"]
    if CTK_AVAILABLE:
        return ctk.CTkButton(parent, text=text, command=command,
                             fg_color=color, hover_color=C["accent2"],
                             text_color=text_color,
                             font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
                             corner_radius=8, width=width, height=height, **kw)
    else:
        b = tk.Button(parent, text=text, command=command,
                      bg=color, fg=text_color,
                      font=("Segoe UI", 10, "bold"),
                      relief="flat", cursor="hand2", **kw)
        return b


def _frame(parent, color=None, corner=12, **kw):
    color = color or C["card"]
    if CTK_AVAILABLE:
        return ctk.CTkFrame(parent, fg_color=color, corner_radius=corner, **kw)
    else:
        return tk.Frame(parent, bg=color, **kw)


def _entry(parent, **kw):
    if CTK_AVAILABLE:
        return ctk.CTkEntry(parent,
                            fg_color=C["card2"], border_color=C["border"],
                            text_color=C["text"], **kw)
    else:
        return tk.Entry(parent, bg=C["card2"], fg=C["text"], **kw)


def _scrollable(parent, **kw):
    if CTK_AVAILABLE:
        return ctk.CTkScrollableFrame(parent, fg_color=C["bg"], **kw)
    else:
        return tk.Frame(parent, bg=C["bg"], **kw)


# ══════════════════════════════════════════════════════════════════════════════
#  Image Upload Card
# ══════════════════════════════════════════════════════════════════════════════

class ImageCard:
    PREVIEW_SIZE = (180, 180)

    def __init__(self, parent, title: str, index: int):
        self.title   = title
        self.index   = index
        self.path: Optional[str] = None

        self.frame = _frame(parent)
        self.frame.pack(fill="x", pady=6, padx=4)

        # Title row
        title_row = _frame(self.frame, color=C["card"], corner=0)
        title_row.pack(fill="x", padx=12, pady=(12, 4))
        _label(title_row, f"  {title}", size=12, bold=True,
               color=C["accent"]).pack(side="left")

        # Preview canvas
        self.canvas = tk.Canvas(
            self.frame, width=self.PREVIEW_SIZE[0], height=self.PREVIEW_SIZE[1],
            bg=C["card2"], highlightthickness=1, highlightbackground=C["border"],
        )
        self.canvas.pack(pady=6)
        self._draw_placeholder()

        # File name label
        self.name_lbl = _label(self.frame, "No file selected",
                               size=9, color=C["subtext"])
        self.name_lbl.pack()

        # Dims label
        self.dims_lbl = _label(self.frame, "", size=9, color=C["subtext"])
        self.dims_lbl.pack()

        # Browse button
        _button(self.frame, "Browse Image", command=self._browse,
                width=160, height=34).pack(pady=10)

    def _draw_placeholder(self):
        w, h = self.PREVIEW_SIZE
        self.canvas.delete("all")
        self.canvas.create_rectangle(0, 0, w, h, fill=C["card2"], outline="")
        self.canvas.create_text(w//2, h//2-14, text="📷", font=("Segoe UI", 32),
                                fill=C["border"])
        self.canvas.create_text(w//2, h//2+18, text="Click Browse",
                                font=("Segoe UI", 9), fill=C["subtext"])

    def _browse(self):
        path = filedialog.askopenfilename(
            title=f"Select {self.title}",
            filetypes=[("Images", "*.jpg *.jpeg *.png *.bmp *.tiff *.webp"),
                       ("All Files", "*.*")]
        )
        if path:
            self.set_image(path)

    def set_image(self, path: str):
        self.path = path
        self.name_lbl.configure(text=short_filename(path))
        if PIL_AVAILABLE:
            try:
                img = Image.open(path)
                w_orig, h_orig = img.size
                self.dims_lbl.configure(text=f"{w_orig} × {h_orig} px")
                img.thumbnail(self.PREVIEW_SIZE, Image.LANCZOS)
                self._tk_img = ImageTk.PhotoImage(img)
                self.canvas.delete("all")
                # Centre it
                cx, cy = self.PREVIEW_SIZE[0]//2, self.PREVIEW_SIZE[1]//2
                self.canvas.create_image(cx, cy, anchor="center",
                                         image=self._tk_img)
            except Exception as e:
                self.dims_lbl.configure(text="Preview error")
        else:
            self.dims_lbl.configure(text="PIL not installed")

    def clear(self):
        self.path = None
        self._draw_placeholder()
        self.name_lbl.configure(text="No file selected")
        self.dims_lbl.configure(text="")


# ══════════════════════════════════════════════════════════════════════════════
#  Score Ring (pure Tk canvas)
# ══════════════════════════════════════════════════════════════════════════════

class ScoreRing(tk.Canvas):
    SIZE = 160

    def __init__(self, parent, **kw):
        super().__init__(parent, width=self.SIZE, height=self.SIZE,
                         bg=C["card"], highlightthickness=0, **kw)
        self.score = 0.0
        self._draw(0.0)

    def set_score(self, score: float):
        self.score = score
        self._draw(score)

    def _draw(self, score: float):
        self.delete("all")
        s = self.SIZE
        pad = 16
        # Track
        self.create_arc(pad, pad, s-pad, s-pad,
                        start=90, extent=360, style="arc",
                        outline=C["border"], width=12)
        # Filled arc
        ext = score / 100 * 360
        colour = score_color(score)
        if ext > 0:
            self.create_arc(pad, pad, s-pad, s-pad,
                            start=90, extent=-ext, style="arc",
                            outline=colour, width=12)
        # Score text
        self.create_text(s//2, s//2-8,
                         text=f"{score:.1f}%",
                         font=("Segoe UI", 18, "bold"),
                         fill=C["text"])
        self.create_text(s//2, s//2+14,
                         text="Score",
                         font=("Segoe UI", 9),
                         fill=C["subtext"])


# ══════════════════════════════════════════════════════════════════════════════
#  Main Application Window
# ══════════════════════════════════════════════════════════════════════════════

class FaceMatchApp:
    def __init__(self):
        self.settings  = get_settings()
        self.db        = get_db()
        self.matcher   = FaceMatcher(threshold=self.settings.get("similarity_threshold", 60.0))
        self._result: Optional[Dict[str, Any]] = None
        self._comparing = False

        # Root window
        if CTK_AVAILABLE:
            self.root = ctk.CTk()
        else:
            self.root = tk.Tk()

        self.root.title("FaceMatch Pro — AI Face Verification")
        w = self.settings.get("window_width", 1400)
        h = self.settings.get("window_height", 860)
        self.root.geometry(f"{w}x{h}")
        self.root.configure(bg=C["bg"])
        self.root.minsize(1100, 720)

        self._build_ui()
        self._start_clock()

    # ── UI construction ────────────────────────────────────────────────────────

    def _build_ui(self):
        self._build_header()
        self._build_tabs()

    def _build_header(self):
        hdr = _frame(self.root, color="#0B1120", corner=0)
        hdr.pack(fill="x", pady=0)

        inner = _frame(hdr, color="#0B1120", corner=0)
        inner.pack(fill="x", padx=24, pady=10)

        # Logo + title
        left = _frame(inner, color="#0B1120", corner=0)
        left.pack(side="left")
        _label(left, "⬡  FaceMatch Pro", size=20, bold=True,
               color=C["accent"]).pack(side="left", padx=(0, 16))
        _label(left, "AI Face Verification & Similarity System",
               size=9, color=C["subtext"]).pack(side="left", pady=(4,0))

        # Status indicators
        right = _frame(inner, color="#0B1120", corner=0)
        right.pack(side="right")

        self.clock_lbl = _label(right, "", size=9, color=C["subtext"])
        self.clock_lbl.pack(side="right", padx=14)

        db_status = self.db.get_status()
        db_col = C["success"] if "Connected" in db_status else C["warning"]
        self.db_lbl = _label(right, f"● DB: {db_status}", size=9, color=db_col)
        self.db_lbl.pack(side="right", padx=14)

        _label(right, "● System Ready", size=9, color=C["success"]).pack(side="right", padx=4)

    def _build_tabs(self):
        if CTK_AVAILABLE:
            self.tabview = ctk.CTkTabview(self.root, fg_color=C["bg"],
                                          segmented_button_fg_color=C["card"],
                                          segmented_button_selected_color=C["accent"],
                                          segmented_button_unselected_color=C["card"],
                                          text_color=C["text"])
            self.tabview.pack(fill="both", expand=True, padx=12, pady=4)
            for tab in ("Compare", "History", "Analytics", "Settings"):
                self.tabview.add(tab)
            compare_tab   = self.tabview.tab("Compare")
            history_tab   = self.tabview.tab("History")
            analytics_tab = self.tabview.tab("Analytics")
            settings_tab  = self.tabview.tab("Settings")
        else:
            notebook_frame = tk.Frame(self.root, bg=C["bg"])
            notebook_frame.pack(fill="both", expand=True)
            compare_tab   = tk.Frame(notebook_frame, bg=C["bg"])
            history_tab   = tk.Frame(notebook_frame, bg=C["bg"])
            analytics_tab = tk.Frame(notebook_frame, bg=C["bg"])
            settings_tab  = tk.Frame(notebook_frame, bg=C["bg"])
            compare_tab.pack(fill="both", expand=True)

        self._build_compare_tab(compare_tab)
        self._build_history_tab(history_tab)
        self._build_analytics_tab(analytics_tab)
        self._build_settings_tab(settings_tab)

    # ── Compare Tab ────────────────────────────────────────────────────────────

    def _build_compare_tab(self, parent):
        outer = tk.Frame(parent, bg=C["bg"])
        outer.pack(fill="both", expand=True, padx=8, pady=6)
        outer.columnconfigure(0, weight=1, minsize=220)
        outer.columnconfigure(1, weight=2, minsize=340)
        outer.columnconfigure(2, weight=1, minsize=280)
        outer.rowconfigure(0, weight=1)

        self._build_left_panel(outer)
        self._build_center_panel(outer)
        self._build_right_panel(outer)

    def _build_left_panel(self, parent):
        col = tk.Frame(parent, bg=C["bg"])
        col.grid(row=0, column=0, sticky="nsew", padx=(0, 6))

        _label(col, "Image Upload", size=13, bold=True,
               color=C["text"]).pack(anchor="w", pady=(4, 8))

        self.card1 = ImageCard(col, "Face Image 1", 1)
        self.card2 = ImageCard(col, "Face Image 2", 2)

        # Clear button
        _button(col, "Clear Both", command=self._clear_images,
                color=C["card2"], width=160, height=30).pack(pady=(8,0))

    def _build_center_panel(self, parent):
        col = tk.Frame(parent, bg=C["bg"])
        col.grid(row=0, column=1, sticky="nsew", padx=6)

        _label(col, "Face Comparison Engine", size=13, bold=True,
               color=C["text"]).pack(anchor="w", pady=(4, 8))

        # Compare button
        btn_frame = _frame(col)
        btn_frame.pack(fill="x", pady=6)
        self.compare_btn = _button(
            btn_frame, "⬡  Compare Faces",
            command=self._start_comparison,
            width=260, height=52,
        )
        self.compare_btn.pack(pady=20, padx=20)

        # Progress bar
        if CTK_AVAILABLE:
            self.progress = ctk.CTkProgressBar(col, progress_color=C["accent"],
                                               height=8, corner_radius=4)
        else:
            self.progress = tk.ttk.Progressbar(col, length=300, mode="indeterminate")
        self.progress.pack(fill="x", padx=16, pady=4)
        if CTK_AVAILABLE:
            self.progress.set(0)

        self.progress_lbl = _label(col, "Ready to compare", size=9, color=C["subtext"])
        self.progress_lbl.pack()

        # Score ring
        ring_frame = _frame(col)
        ring_frame.pack(fill="x", pady=8)
        _label(ring_frame, "Similarity Score", size=11, bold=True,
               color=C["subtext"]).pack(pady=(12, 4))
        self.score_ring = ScoreRing(ring_frame)
        self.score_ring.pack(pady=8)

        # Metric pills
        pills_frame = tk.Frame(ring_frame, bg=C["card"])
        pills_frame.pack(fill="x", padx=12, pady=(0, 12))
        self._hist_lbl   = self._metric_pill(pills_frame, "Histogram",  "—")
        self._ssim_lbl   = self._metric_pill(pills_frame, "SSIM",       "—")
        self._feat_lbl   = self._metric_pill(pills_frame, "Features",   "—")
        self._hist_lbl.pack(side="left", expand=True, padx=4)
        self._ssim_lbl.pack(side="left", expand=True, padx=4)
        self._feat_lbl.pack(side="left", expand=True, padx=4)

        # Generate report button
        self.report_btn = _button(col, "Generate PDF Report",
                                  command=self._generate_report,
                                  color=C["card2"], width=200, height=34)
        self.report_btn.pack(pady=(8, 4))
        if CTK_AVAILABLE:
            self.report_btn.configure(state="disabled")

    def _metric_pill(self, parent, label, value):
        f = _frame(parent, color=C["card2"], corner=8)
        _label(f, label, size=8, color=C["subtext"]).pack(pady=(6,0))
        v = _label(f, value, size=10, bold=True, color=C["text"])
        v.pack(pady=(0, 6))
        f._val_label = v
        f._cur_label = label
        return f

    def _build_right_panel(self, parent):
        col = _scrollable(parent)
        col.grid(row=0, column=2, sticky="nsew", padx=(6, 0))

        _label(col, "Results Dashboard", size=13, bold=True,
               color=C["text"]).pack(anchor="w", pady=(4, 8))

        # Verification result card
        self.result_card = _frame(col)
        self.result_card.pack(fill="x", pady=4)
        _label(self.result_card, "VERIFICATION RESULT", size=9, bold=True,
               color=C["subtext"]).pack(pady=(12, 2))
        self.result_status_lbl = _label(self.result_card, "—", size=22, bold=True,
                                        color=C["subtext"])
        self.result_status_lbl.pack()
        self.result_label_lbl = _label(self.result_card, "Run comparison to see results",
                                       size=9, color=C["subtext"])
        self.result_label_lbl.pack(pady=(2, 12))

        # Stats grid
        stats_card = _frame(col)
        stats_card.pack(fill="x", pady=4)
        self._stats = {}
        stats_items = [
            ("confidence",    "Confidence Level", "—"),
            ("quality_1",     "Quality — Img 1",  "—"),
            ("quality_2",     "Quality — Img 2",  "—"),
            ("dims_1",        "Dimensions — Img 1","—"),
            ("dims_2",        "Dimensions — Img 2","—"),
            ("proc_time",     "Processing Time",   "—"),
        ]
        for key, label, init in stats_items:
            row = tk.Frame(stats_card, bg=C["card"])
            row.pack(fill="x", padx=12, pady=3)
            _label(row, label, size=9, color=C["subtext"]).pack(side="left")
            v = _label(row, init, size=9, bold=True, color=C["text"])
            v.pack(side="right")
            self._stats[key] = v

        # Error area
        self.error_lbl = _label(col, "", size=9, color=C["error"])
        self.error_lbl.pack(pady=4, padx=8)

    # ── History Tab ────────────────────────────────────────────────────────────

    def _build_history_tab(self, parent):
        top = tk.Frame(parent, bg=C["bg"])
        top.pack(fill="x", padx=8, pady=6)

        _label(top, "Verification History", size=13, bold=True,
               color=C["text"]).pack(side="left")

        # Controls
        ctrl = tk.Frame(top, bg=C["bg"])
        ctrl.pack(side="right")

        self._search_var = tk.StringVar()
        search_entry = _entry(ctrl, textvariable=self._search_var, width=180,
                              placeholder_text="Search by filename…")
        search_entry.pack(side="left", padx=6)
        self._search_var.trace_add("write", lambda *_: self._refresh_history())

        if CTK_AVAILABLE:
            self._status_var = ctk.StringVar(value="All")
            self._status_combo = ctk.CTkComboBox(
                ctrl, values=["All", "Match", "No Match"],
                variable=self._status_var,
                command=lambda _: self._refresh_history(),
                fg_color=C["card2"], border_color=C["border"],
                text_color=C["text"], width=110,
            )
            self._status_combo.pack(side="left", padx=6)
        else:
            self._status_var = tk.StringVar(value="All")

        _button(ctrl, "Refresh", command=self._refresh_history,
                width=80, height=30).pack(side="left", padx=4)
        _button(ctrl, "Export CSV", command=self._export_csv,
                color=C["success"], width=100, height=30).pack(side="left", padx=4)
        _button(ctrl, "Delete", command=self._delete_selected,
                color=C["error"], width=80, height=30).pack(side="left", padx=4)

        # Table
        table_frame = _frame(parent, corner=8)
        table_frame.pack(fill="both", expand=True, padx=8, pady=4)

        cols = ("#", "Image 1", "Image 2", "Score", "Status", "Date/Time", "Time (ms)")
        self._tree = self._make_treeview(table_frame, cols)
        self._refresh_history()

    def _make_treeview(self, parent, cols):
        import tkinter.ttk as ttk
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("FMP.Treeview",
                        background=C["card"],
                        foreground=C["text"],
                        rowheight=28,
                        fieldbackground=C["card"],
                        bordercolor=C["border"],
                        font=("Segoe UI", 9))
        style.configure("FMP.Treeview.Heading",
                        background=C["accent2"],
                        foreground="white",
                        font=("Segoe UI", 9, "bold"))
        style.map("FMP.Treeview",
                  background=[("selected", C["accent"])],
                  foreground=[("selected", "white")])

        frame = tk.Frame(parent, bg=C["card"])
        frame.pack(fill="both", expand=True, padx=2, pady=2)

        tree = ttk.Treeview(frame, columns=cols, show="headings",
                             style="FMP.Treeview", selectmode="browse")
        widths = [40, 160, 160, 80, 80, 160, 80]
        for col, w in zip(cols, widths):
            tree.heading(col, text=col,
                         command=lambda c=col: self._sort_tree(tree, c))
            tree.column(col, width=w, anchor="center")

        sb = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=sb.set)
        tree.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        return tree

    def _refresh_history(self):
        search = self._search_var.get()
        status = self._status_var.get() if hasattr(self, "_status_var") else "All"
        records = self.db.fetch_history(search=search, status_filter=status)
        self._history_records = records

        self._tree.delete(*self._tree.get_children())
        for i, r in enumerate(records, 1):
            score = r.get("similarity_score", 0)
            ts    = format_timestamp(r.get("timestamp"))
            pt    = f"{r.get('processing_time',0)*1000:.1f}"
            tag   = "match" if r.get("match_status") == "Match" else "nomatch"
            self._tree.insert("", "end", iid=r["_id"],
                              values=(i,
                                      short_filename(r.get("image1_name",""), 22),
                                      short_filename(r.get("image2_name",""), 22),
                                      f"{score:.2f}%",
                                      r.get("match_status",""),
                                      ts, pt),
                              tags=(tag,))
        self._tree.tag_configure("match",   background="#0d2f22")
        self._tree.tag_configure("nomatch", background="#2d1515")

    def _sort_tree(self, tree, col):
        items = [(tree.set(k, col), k) for k in tree.get_children("")]
        items.sort(reverse=False)
        for idx, (_, k) in enumerate(items):
            tree.move(k, "", idx)

    def _delete_selected(self):
        sel = self._tree.selection()
        if not sel:
            messagebox.showinfo("Delete", "Select a record first.")
            return
        record_id = sel[0]
        if messagebox.askyesno("Delete Record",
                               "Delete this verification record?"):
            self.db.delete_record(record_id)
            self._refresh_history()

    def _export_csv(self):
        records = getattr(self, "_history_records", [])
        if not records:
            messagebox.showinfo("Export", "No records to export.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv")],
            initialfile=f"FaceMatchPro_History_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        if path:
            export_csv(records, path)
            messagebox.showinfo("Export", f"Exported {len(records)} records to:\n{path}")

    # ── Analytics Tab ──────────────────────────────────────────────────────────

    def _build_analytics_tab(self, parent):
        top = tk.Frame(parent, bg=C["bg"])
        top.pack(fill="x", padx=8, pady=6)
        _label(top, "Analytics Dashboard", size=13, bold=True,
               color=C["text"]).pack(side="left")
        _button(top, "Refresh", command=self._refresh_analytics,
                width=80, height=30).pack(side="right")

        # KPI row
        kpi_frame = tk.Frame(parent, bg=C["bg"])
        kpi_frame.pack(fill="x", padx=8, pady=4)
        for i in range(5):
            kpi_frame.columnconfigure(i, weight=1)

        self._kpis = {}
        kpi_defs = [
            ("total",       "Total Comparisons", C["accent"]),
            ("matches",     "Matches Found",      C["success"]),
            ("no_matches",  "No Matches",         C["error"]),
            ("avg_sim",     "Avg Similarity",     C["warning"]),
            ("today",       "Today",              C["accent2"]),
        ]
        for col_idx, (key, label, colour) in enumerate(kpi_defs):
            card = _frame(kpi_frame, color=C["card"])
            card.grid(row=0, column=col_idx, sticky="nsew", padx=4, pady=4)
            v = _label(card, "—", size=24, bold=True, color=colour)
            v.pack(pady=(12, 2))
            _label(card, label, size=9, color=C["subtext"]).pack(pady=(0, 12))
            self._kpis[key] = v

        # Chart area
        self._chart_frame = _frame(parent, color=C["card"])
        self._chart_frame.pack(fill="both", expand=True, padx=8, pady=4)

        self._refresh_analytics()

    def _refresh_analytics(self):
        data = self.db.get_analytics()
        self._kpis["total"].configure(text=str(data["total"]))
        self._kpis["matches"].configure(text=str(data["matches"]))
        self._kpis["no_matches"].configure(text=str(data["no_matches"]))
        self._kpis["avg_sim"].configure(text=f"{data['avg_similarity']:.1f}%")
        self._kpis["today"].configure(text=str(data["today"]))

        if MPL_AVAILABLE:
            self._render_charts(data)

    def _render_charts(self, data):
        # Clear old charts
        for w in self._chart_frame.winfo_children():
            w.destroy()

        bg_c = "#1E293B"
        fig, axes = plt.subplots(1, 2, figsize=(10, 3.2),
                                 facecolor=bg_c)
        fig.patch.set_facecolor(bg_c)

        # Pie chart
        ax1 = axes[0]
        ax1.set_facecolor(bg_c)
        m  = data["matches"]
        nm = data["no_matches"]
        if m + nm > 0:
            ax1.pie([m, nm],
                    labels=["Match", "No Match"],
                    colors=[C["success"], C["error"]],
                    autopct="%1.0f%%",
                    startangle=90,
                    textprops={"color": "white", "fontsize": 9})
        ax1.set_title("Match Breakdown", color="white", fontsize=10)

        # Bar: daily trend
        ax2 = axes[1]
        ax2.set_facecolor(bg_c)
        trend = data.get("daily_trend", {})
        if trend:
            days   = sorted(trend.keys())[-14:]
            counts = [trend[d] for d in days]
            ax2.bar(days, counts, color=C["accent"], width=0.6)
            ax2.set_facecolor(bg_c)
            ax2.tick_params(colors="white", labelsize=7, axis="both")
            for spine in ax2.spines.values():
                spine.set_edgecolor(C["border"])
            ax2.set_title("Daily Comparisons (last 14 days)",
                          color="white", fontsize=10)
            ax2.set_xticklabels(days, rotation=45, ha="right", fontsize=7)
        else:
            ax2.text(0.5, 0.5, "No data yet",
                     ha="center", va="center", color=C["subtext"],
                     transform=ax2.transAxes)

        fig.tight_layout(pad=1.5)
        canvas = FigureCanvasTkAgg(fig, master=self._chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=6, pady=6)
        plt.close(fig)

    # ── Settings Tab ───────────────────────────────────────────────────────────

    def _build_settings_tab(self, parent):
        scroll = _scrollable(parent)
        scroll.pack(fill="both", expand=True, padx=8, pady=6)

        _label(scroll, "Settings", size=13, bold=True,
               color=C["text"]).pack(anchor="w", pady=(4, 12))

        def section(title):
            f = _frame(scroll)
            f.pack(fill="x", pady=6)
            _label(f, f"  {title}", size=11, bold=True,
                   color=C["accent"]).pack(anchor="w", padx=8, pady=(10, 4))
            return f

        def row(parent, label, widget_fn):
            r = tk.Frame(parent, bg=C["card"])
            r.pack(fill="x", padx=12, pady=4)
            _label(r, label, size=9, color=C["subtext"]).pack(side="left", padx=(0, 16))
            widget_fn(r).pack(side="right")

        # Threshold
        db_sec = section("Database & Thresholds")
        self._thresh_var = tk.DoubleVar(
            value=self.settings.get("similarity_threshold", 60.0))
        def thresh_widget(p):
            f = tk.Frame(p, bg=C["card"])
            if CTK_AVAILABLE:
                sl = ctk.CTkSlider(f, from_=30, to=95, variable=self._thresh_var,
                                   progress_color=C["accent"], width=200)
            else:
                sl = tk.Scale(f, from_=30, to=95, variable=self._thresh_var,
                              orient="horizontal", bg=C["card"], fg=C["text"],
                              highlightthickness=0, length=200)
            sl.pack(side="left")
            lbl = _label(f, f"{self._thresh_var.get():.0f}%", size=9, color=C["text"])
            lbl.pack(side="left", padx=6)
            self._thresh_var.trace_add("write", lambda *_: lbl.configure(
                text=f"{self._thresh_var.get():.0f}%"))
            return f
        row(db_sec, "Similarity Threshold", thresh_widget)

        # MongoDB host
        self._mongo_host_var = tk.StringVar(
            value=self.settings.get("mongo_host", "localhost"))
        def mongo_host_widget(p):
            return _entry(p, textvariable=self._mongo_host_var, width=180)
        row(db_sec, "MongoDB Host", mongo_host_widget)

        self._mongo_port_var = tk.StringVar(
            value=str(self.settings.get("mongo_port", 27017)))
        def mongo_port_widget(p):
            return _entry(p, textvariable=self._mongo_port_var, width=80)
        row(db_sec, "MongoDB Port", mongo_port_widget)

        # Export path
        exp_sec = section("Export")
        self._export_path_var = tk.StringVar(
            value=self.settings.get("export_path", "reports"))
        def export_path_widget(p):
            f = tk.Frame(p, bg=C["card"])
            _entry(f, textvariable=self._export_path_var, width=220).pack(side="left")
            _button(f, "Browse", command=self._browse_export, width=70, height=28).pack(side="left", padx=4)
            return f
        row(exp_sec, "Report Export Path", export_path_widget)

        # Save / Reset
        btn_row = tk.Frame(scroll, bg=C["bg"])
        btn_row.pack(pady=16)
        _button(btn_row, "Save Settings", command=self._save_settings,
                width=140, height=36).pack(side="left", padx=8)
        _button(btn_row, "Reset Defaults", command=self._reset_settings,
                color=C["error"], width=130, height=36).pack(side="left", padx=8)

    def _browse_export(self):
        path = filedialog.askdirectory()
        if path:
            self._export_path_var.set(path)

    def _save_settings(self):
        self.settings.update({
            "similarity_threshold": float(self._thresh_var.get()),
            "mongo_host": self._mongo_host_var.get(),
            "mongo_port": int(self._mongo_port_var.get() or 27017),
            "export_path": self._export_path_var.get(),
        })
        self.matcher.threshold = self.settings.get("similarity_threshold", 60.0)
        messagebox.showinfo("Settings", "Settings saved successfully.")

    def _reset_settings(self):
        if messagebox.askyesno("Reset", "Reset all settings to defaults?"):
            self.settings.reset()
            messagebox.showinfo("Settings", "Settings reset to defaults.")

    # ── Comparison logic ───────────────────────────────────────────────────────

    def _clear_images(self):
        self.card1.clear()
        self.card2.clear()
        self.score_ring.set_score(0)
        self.result_status_lbl.configure(text="—", text_color=C["subtext"])
        self.result_label_lbl.configure(text="Run comparison to see results")
        self.error_lbl.configure(text="")
        for key in self._stats:
            self._stats[key].configure(text="—")
        if CTK_AVAILABLE:
            self.progress.set(0)
        self._result = None
        if CTK_AVAILABLE:
            self.report_btn.configure(state="disabled")

    def _start_comparison(self):
        if self._comparing:
            return
        if not self.card1.path:
            self._show_error("Please upload Image 1 first.")
            return
        if not self.card2.path:
            self._show_error("Please upload Image 2 first.")
            return
        self._comparing = True
        self.error_lbl.configure(text="")
        if CTK_AVAILABLE:
            self.compare_btn.configure(state="disabled", text="Analyzing…")
        self._animate_progress(True)
        t = threading.Thread(target=self._run_comparison, daemon=True)
        t.start()

    def _run_comparison(self):
        try:
            result = self.matcher.compare(self.card1.path, self.card2.path)
            self.root.after(0, self._show_result, result)
        except Exception as e:
            self.root.after(0, self._show_error, str(e))
        finally:
            self.root.after(0, self._end_compare_anim)

    def _end_compare_anim(self):
        self._comparing = False
        self._animate_progress(False)
        if CTK_AVAILABLE:
            self.compare_btn.configure(state="normal", text="⬡  Compare Faces")

    def _animate_progress(self, start: bool):
        if CTK_AVAILABLE:
            if start:
                self.progress.configure(mode="indeterminate")
                self.progress.start()
                self.progress_lbl.configure(text="Analyzing faces…")
            else:
                self.progress.stop()
                self.progress.configure(mode="determinate")
                self.progress.set(1.0 if self._result else 0)
                self.progress_lbl.configure(text="Complete" if self._result else "Ready")

    def _show_result(self, result: Dict[str, Any]):
        if result.get("error"):
            self._show_error(result["error"])
            return

        self._result = result
        score  = result["similarity_score"]
        status = result["match_status"]

        # Ring
        self.score_ring.set_score(score)

        # Status card
        col = C["success"] if status == "Match" else C["error"]
        sign = "✓  Match Found" if status == "Match" else "✗  No Match"
        self.result_status_lbl.configure(text=sign, text_color=col)
        self.result_label_lbl.configure(text=result.get("match_label",""))

        # Stats
        self._stats["confidence"].configure(
            text=f"{result.get('confidence',0):.1f}%")
        self._stats["quality_1"].configure(
            text=f"{result.get('face_quality_1',0):.1f}%")
        self._stats["quality_2"].configure(
            text=f"{result.get('face_quality_2',0):.1f}%")
        d1 = result.get("dims_1",(0,0))
        d2 = result.get("dims_2",(0,0))
        self._stats["dims_1"].configure(text=f"{d1[0]}×{d1[1]}")
        self._stats["dims_2"].configure(text=f"{d2[0]}×{d2[1]}")
        self._stats["proc_time"].configure(
            text=f"{result.get('processing_time',0)*1000:.1f} ms")

        # Metric pills
        self._hist_lbl._val_label.configure(
            text=f"{result.get('histogram_score',0):.1f}%")
        self._ssim_lbl._val_label.configure(
            text=f"{result.get('ssim_score',0):.1f}%")
        self._feat_lbl._val_label.configure(
            text=f"{result.get('feature_score',0):.1f}%")

        # Enable PDF button
        if CTK_AVAILABLE:
            self.report_btn.configure(state="normal")

        # Save to DB
        self.db.save_result(
            image1_name=os.path.basename(self.card1.path),
            image2_name=os.path.basename(self.card2.path),
            similarity_score=score,
            match_status=status,
            processing_time=result.get("processing_time", 0),
        )

    def _show_error(self, msg: str):
        self.error_lbl.configure(text=f"⚠  {msg}")

    # ── PDF report ─────────────────────────────────────────────────────────────

    def _generate_report(self):
        if not self._result:
            messagebox.showinfo("Report", "Run a comparison first.")
            return
        try:
            from pdf_generator import generate_report
            export_dir = self.settings.get("export_path", "reports")
            path = generate_report(
                self._result,
                self.card1.path,
                self.card2.path,
                output_dir=export_dir,
            )
            messagebox.showinfo("Report Generated",
                                f"PDF saved to:\n{path}")
        except RuntimeError as e:
            messagebox.showerror("PDF Error", str(e))
        except Exception as e:
            messagebox.showerror("PDF Error", f"Could not generate report:\n{e}")

    # ── Clock ──────────────────────────────────────────────────────────────────

    def _start_clock(self):
        self._tick()

    def _tick(self):
        now = datetime.datetime.now()
        self.clock_lbl.configure(
            text=now.strftime("%a %d %b %Y  %H:%M:%S"))
        self.root.after(1000, self._tick)

    # ── Run ───────────────────────────────────────────────────────────────────

    def run(self):
        self.root.mainloop()


# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    if not CTK_AVAILABLE:
        print("[WARNING] customtkinter not found – falling back to plain Tkinter.")
        print("          Run:  pip install customtkinter")

    app = FaceMatchApp()
    app.run()
