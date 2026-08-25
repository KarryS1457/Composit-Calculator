import tkinter as tk

from core.utils import ScrollableFrame


class WhatsNew(tk.Toplevel):
    """Окно «Что нового» — показывается один раз после обновления."""

    def __init__(self, parent, entries, version):
        super().__init__(parent)
        self.title(f"Что нового в версии {version}")
        self.geometry("640x560")
        self.minsize(480, 400)
        self.transient(parent)

        try:
            from view import _resource_path
            self.iconbitmap(_resource_path("icon.ico"))
        except Exception:
            pass  # без иконки окно все равно работает

        header = tk.Frame(self, bg="#2c3e50")
        header.pack(fill="x")
        tk.Label(header, text="ПРОГРАММА ОБНОВЛЕНА", bg="#2c3e50", fg="white",
                 font=("Arial", 14, "bold"), pady=12).pack()
        tk.Label(header, text=f"версия {version}", bg="#2c3e50", fg="#bdc3c7",
                 font=("Arial", 9), pady=(0)).pack(pady=(0, 12))

        body = ScrollableFrame(self)
        body.pack(fill="both", expand=True, padx=16, pady=12)
        inner = body.inner_frame

        for ver, date, blocks in entries:
            if len(entries) > 1:
                tk.Label(inner, text=f"Версия {ver} от {date}",
                         font=("Arial", 12, "bold"), fg="#2c3e50",
                         anchor="w").pack(fill="x", pady=(10, 4))
            else:
                tk.Label(inner, text=f"от {date}", font=("Arial", 9),
                         fg="#95a5a6", anchor="w").pack(fill="x")

            for title, items in blocks:
                tk.Label(inner, text=title, font=("Arial", 11, "bold"),
                         fg="#2c3e50", anchor="w").pack(fill="x", pady=(14, 6))
                for text in items:
                    row = tk.Frame(inner)
                    row.pack(fill="x", pady=3)
                    tk.Label(row, text="•", font=("Arial", 10), fg="#7f8c8d",
                             anchor="nw", width=2).pack(side="left", anchor="n")
                    tk.Label(row, text=text, font=("Arial", 10), justify="left",
                             anchor="w", wraplength=520).pack(side="left",
                                                              fill="x", expand=True)

        body.bind_mouse_scroll(inner, recursive=True)

        bottom = tk.Frame(self)
        bottom.pack(fill="x", padx=16, pady=(0, 14))
        tk.Button(bottom, text="ПОНЯТНО", bg="#2c3e50", fg="white",
                  font=("Arial", 11, "bold"), command=self.destroy).pack(
            fill="x", ipady=6)

        self.update_idletasks()
        self._center_on(parent)

    def _center_on(self, parent):
        try:
            px, py = parent.winfo_rootx(), parent.winfo_rooty()
            pw, ph = parent.winfo_width(), parent.winfo_height()
            w, h = self.winfo_width(), self.winfo_height()
            self.geometry(f"+{px + (pw - w) // 2}+{py + (ph - h) // 2}")
        except Exception:
            pass
