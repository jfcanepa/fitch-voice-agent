"""
gui.py — Tkinter GUI for the Fitch Voice Agent.

Run:
    python gui.py
"""

import threading
import tkinter as tk
from tkinter import messagebox, scrolledtext, simpledialog

from dotenv import load_dotenv

load_dotenv()


class FitchAgentGUI:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Fitch Voice Agent")
        self.root.geometry("820x620")
        self.root.configure(bg="#1e1e2e")
        self.root.resizable(True, True)

        self.voice_enabled = tk.BooleanVar(value=True)
        self._build_ui()

    # ── UI construction ───────────────────────────────────────────────────────

    def _build_ui(self):
        # ── Header ──
        header = tk.Frame(self.root, bg="#181825", pady=10)
        header.pack(fill=tk.X)

        tk.Label(
            header,
            text="Fitch Voice Agent",
            font=("Helvetica", 18, "bold"),
            fg="#cdd6f4",
            bg="#181825",
        ).pack(side=tk.LEFT, padx=16)

        tk.Button(
            header,
            text="+ Add Report",
            command=self._add_report,
            bg="#89b4fa",
            fg="#1e1e2e",
            font=("Helvetica", 11, "bold"),
            relief=tk.FLAT,
            padx=12,
            pady=4,
            cursor="hand2",
        ).pack(side=tk.RIGHT, padx=16)

        tk.Checkbutton(
            header,
            text="Voice",
            variable=self.voice_enabled,
            bg="#181825",
            fg="#a6e3a1",
            selectcolor="#181825",
            activebackground="#181825",
            activeforeground="#a6e3a1",
            font=("Helvetica", 11),
        ).pack(side=tk.RIGHT, padx=4)

        # ── Chat area ──
        chat_frame = tk.Frame(self.root, bg="#1e1e2e")
        chat_frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=(12, 0))

        self.chat = scrolledtext.ScrolledText(
            chat_frame,
            wrap=tk.WORD,
            state=tk.DISABLED,
            bg="#181825",
            fg="#cdd6f4",
            font=("Helvetica", 12),
            relief=tk.FLAT,
            padx=12,
            pady=8,
            insertbackground="#cdd6f4",
        )
        self.chat.pack(fill=tk.BOTH, expand=True)

        # Configure text tags for styling
        self.chat.tag_config("you", foreground="#89b4fa", font=("Helvetica", 12, "bold"))
        self.chat.tag_config("agent", foreground="#a6e3a1", font=("Helvetica", 12, "bold"))
        self.chat.tag_config("system", foreground="#f38ba8", font=("Helvetica", 11, "italic"))
        self.chat.tag_config("body", foreground="#cdd6f4", font=("Helvetica", 12))

        # ── Input area ──
        input_frame = tk.Frame(self.root, bg="#1e1e2e", pady=12)
        input_frame.pack(fill=tk.X, padx=16)

        self.input_var = tk.StringVar()
        self.input_field = tk.Entry(
            input_frame,
            textvariable=self.input_var,
            font=("Helvetica", 13),
            bg="#313244",
            fg="#cdd6f4",
            insertbackground="#cdd6f4",
            relief=tk.FLAT,
            bd=8,
        )
        self.input_field.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=6)
        self.input_field.bind("<Return>", lambda e: self._send())
        self.input_field.focus()

        self.send_btn = tk.Button(
            input_frame,
            text="Ask",
            command=self._send,
            bg="#89b4fa",
            fg="#1e1e2e",
            font=("Helvetica", 12, "bold"),
            relief=tk.FLAT,
            padx=18,
            pady=6,
            cursor="hand2",
        )
        self.send_btn.pack(side=tk.LEFT, padx=(8, 0))

        # ── Status bar ──
        self.status_var = tk.StringVar(value="Ready — type a question or click '+ Add Report'")
        tk.Label(
            self.root,
            textvariable=self.status_var,
            bg="#181825",
            fg="#6c7086",
            font=("Helvetica", 10),
            anchor=tk.W,
            padx=16,
        ).pack(fill=tk.X, side=tk.BOTTOM)

        self._append_system("Welcome! Add a Fitch report with the button above, then ask questions.")

    # ── Chat helpers ──────────────────────────────────────────────────────────

    def _append(self, label: str, tag: str, text: str):
        self.chat.config(state=tk.NORMAL)
        self.chat.insert(tk.END, f"{label} ", tag)
        self.chat.insert(tk.END, f"{text}\n\n", "body")
        self.chat.config(state=tk.DISABLED)
        self.chat.see(tk.END)

    def _append_system(self, text: str):
        self.chat.config(state=tk.NORMAL)
        self.chat.insert(tk.END, f"{text}\n\n", "system")
        self.chat.config(state=tk.DISABLED)
        self.chat.see(tk.END)

    def _set_busy(self, busy: bool):
        state = tk.DISABLED if busy else tk.NORMAL
        self.send_btn.config(state=state)
        self.input_field.config(state=state)
        self.status_var.set("Thinking…" if busy else "Ready")

    # ── Actions ───────────────────────────────────────────────────────────────

    def _send(self):
        query = self.input_var.get().strip()
        if not query:
            return
        self.input_var.set("")
        self._append("You:", "you", query)
        self._set_busy(True)
        threading.Thread(target=self._run_query, args=(query,), daemon=True).start()

    def _run_query(self, query: str):
        try:
            from agent import answer
            response = answer(query)
            self.root.after(0, self._append, "Agent:", "agent", response)

            if self.voice_enabled.get():
                try:
                    from voice import speak
                    speak(response)
                except Exception as e:
                    self.root.after(0, self._append_system, f"Voice error: {e}")
        except Exception as e:
            self.root.after(0, self._append_system, f"Error: {e}")
        finally:
            self.root.after(0, self._set_busy, False)

    def _add_report(self):
        url = simpledialog.askstring(
            "Add Fitch Report",
            "Paste the Fitch report URL:",
            parent=self.root,
        )
        if not url or not url.strip():
            return
        url = url.strip()
        self._append_system(f"Indexing: {url}")
        self._set_busy(True)
        threading.Thread(target=self._run_ingest, args=(url,), daemon=True).start()

    def _run_ingest(self, url: str):
        try:
            from ingest import ingest_url
            count = ingest_url(url)
            if count:
                msg = f"Indexed {count} chunks. You can now ask questions about this report."
            else:
                msg = "Report was already indexed."
            self.root.after(0, self._append_system, msg)
        except Exception as e:
            self.root.after(0, self._append_system, f"Ingest error: {e}")
        finally:
            self.root.after(0, self._set_busy, False)


def main():
    root = tk.Tk()
    app = FitchAgentGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
