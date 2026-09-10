#!/usr/bin/env python3
"""
cognitive_popup.py — GTK3 всплывающее окно у курсора для отображения результатов.
Поддерживает авторазмер, скролл, копирование в буфер по клику или Enter,
закрытие по Esc / клику снаружи.
"""

from __future__ import annotations

import json
import subprocess
import sys

try:
    import gi
    gi.require_version("Gtk", "3.0")
    from gi.repository import Gtk, Gdk, GLib, Pango
except Exception as e:
    print(f"popup init error: {e}", file=sys.stderr)
    sys.exit(1)


def get_mouse_position() -> tuple[int, int]:
    try:
        display = Gdk.Display.get_default()
        seat = display.get_default_seat() if display else None
        pointer = seat.get_pointer() if seat else None
        _, px, py = pointer.get_position() if pointer else (None, 100, 100)
        return int(px), int(py)
    except Exception:
        return 100, 100


def copy_to_clipboard(text: str) -> None:
    try:
        proc = subprocess.Popen(
            ["xclip", "-selection", "clipboard"],
            stdin=subprocess.PIPE,
            close_fds=True,
        )
        proc.communicate(input=text.encode("utf-8"))
    except Exception:
        pass


def calculate_dimensions(text: str) -> tuple[int, int]:
    lines = [ln for ln in text.splitlines() if ln.strip()]
    longest = max((len(ln) for ln in lines), default=len(text))
    width = min(max(320, longest * 8 + 40), 620)
    height = min(max(130, max(3, len(lines)) * 22 + 70), 450)
    return width, height


def main():
    try:
        raw = sys.stdin.read().strip()
        data = json.loads(raw) if raw else {}
    except Exception:
        data = {}

    text = str(data.get("text") or "—")
    title = str(data.get("title") or "Cognitive Result")
    mode = str(data.get("mode") or "info").lower()
    px = data.get("x")
    py = data.get("y")

    if px is None or py is None:
        mx, my = get_mouse_position()
        px, py = mx + 15, my + 15

    width, height = calculate_dimensions(text)
    loop = GLib.MainLoop()

    class ResultPopup(Gtk.Window):
        def __init__(self):
            super().__init__(type=Gtk.WindowType.TOPLEVEL)
            self.set_decorated(False)
            self.set_resizable(False)
            self.set_skip_taskbar_hint(True)
            self.set_skip_pager_hint(True)
            self.set_keep_above(True)
            self.set_type_hint(Gdk.WindowTypeHint.POPUP_MENU)
            self.set_border_width(0)

            self.connect("focus-out-event", lambda *_: self._close())
            self.connect("key-press-event", self._on_key)

            outer = Gtk.EventBox()
            outer.set_visible_window(True)
            self.add(outer)

            main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
            main_box.set_margin_top(8)
            main_box.set_margin_bottom(8)
            main_box.set_margin_start(10)
            main_box.set_margin_end(10)
            outer.add(main_box)

            # Header row
            header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
            title_lbl = Gtk.Label(label=f"<b>{title}</b>")
            title_lbl.set_use_markup(True)
            title_lbl.set_xalign(0)
            header.pack_start(title_lbl, True, True, 0)
            main_box.pack_start(header, False, False, 0)

            # Separator
            sep = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
            main_box.pack_start(sep, False, False, 2)

            # Scrollable text area
            scroller = Gtk.ScrolledWindow()
            scroller.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
            scroller.set_shadow_type(Gtk.ShadowType.NONE)

            view = Gtk.TextView()
            view.set_editable(False)
            view.set_cursor_visible(False)
            view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
            view.set_left_margin(4)
            view.set_right_margin(4)
            view.get_buffer().set_text(text)
            scroller.add(view)
            main_box.pack_start(scroller, True, True, 2)

            # Action buttons
            btn_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
            copy_btn = Gtk.Button(label="Копировать (Enter)")
            copy_btn.connect("clicked", lambda *_: self._copy_and_close())
            btn_row.pack_start(copy_btn, True, True, 0)

            close_btn = Gtk.Button(label="Закрыть (Esc)")
            close_btn.connect("clicked", lambda *_: self._close())
            btn_row.pack_start(close_btn, False, False, 0)

            main_box.pack_start(btn_row, False, False, 2)

            self.set_size_request(width, height)
            self.show_all()
            GLib.idle_add(self._position_window)

        def _position_window(self):
            self.move(int(px), int(py))
            self.present()
            return False

        def _copy_and_close(self):
            copy_to_clipboard(text)
            self._close()

        def _close(self):
            self.destroy()
            loop.quit()
            return True

        def _on_key(self, _widget, event):
            if event.keyval in (Gdk.KEY_Escape,):
                return self._close()
            if event.keyval in (Gdk.KEY_Return, Gdk.KEY_KP_Enter):
                self._copy_and_close()
                return True
            return False

    ResultPopup()
    loop.run()


if __name__ == "__main__":
    main()

