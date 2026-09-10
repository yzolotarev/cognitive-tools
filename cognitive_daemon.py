#!/usr/bin/env python3
"""
cognitive_daemon.py — Когнитивный слой акселерации мышления (по корпусу Санга / iCanStudy).
Слушает глобальные хоткеи X11, забирает выделение (PRIMARY/CLIPBOARD),
отправляет в OpenAI-совместимый API и отображает GTK-popup у курсора.

Операции:
  Ctrl+Alt+Q -> COMPRESS     (Минимальный инвариант, causal core, X -> Y under Z)
  Ctrl+Alt+R -> RELATE       (Отношения: causes, constrains, enables, contradicts)
  Ctrl+Alt+P -> PREDICT      (Формирование гипотезы до чтения для prediction error)
  Ctrl+Alt+T -> RECONSTRUCT  (Вопросы на реконструкцию вместо простого узнавания)
  Ctrl+Alt+M -> MAP          (Структурные узлы и связи, эвристика 2-4)
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import threading
import time
import urllib.request
from datetime import datetime
from typing import Optional

# ── Fallback на системный Python с PyGObject/Xlib ────────────────────────────
try:
    import gi
    gi.require_version("Gtk", "3.0")
    from gi.repository import GLib, Gtk
    from Xlib import X, display, XK
except (ImportError, ValueError) as exc:
    print(f"[cognitive-tools] Missing GTK/X11 dependencies: {exc}", file=sys.stderr)
    sys.exit(1)

# ── Конфигурация ─────────────────────────────────────────────────────────────
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
POPUP_HELPER = os.path.join(PROJECT_DIR, "cognitive_popup.py")

API_URL = os.environ.get("COGNITIVE_API_URL", "http://127.0.0.1:8081/v1/chat/completions")
API_KEY = os.environ.get("COGNITIVE_API_KEY", "")
MODEL = os.environ.get("COGNITIVE_MODEL", "gemini-flash-lite")
TIMEOUT = int(os.environ.get("COGNITIVE_TIMEOUT", "12"))
MAX_RETRIES = int(os.environ.get("COGNITIVE_RETRIES", "3"))
RETRY_DELAY = float(os.environ.get("COGNITIVE_RETRY_DELAY", "0.8"))

STATE_DIR = os.path.expanduser("~/.local/state/cognitive-tools")
LOG_PATH = os.path.join(STATE_DIR, "cognitive-tools.log")
EVENT_LOG_PATH = os.path.join(STATE_DIR, "cognitive-events.jsonl")
PID_FILE = os.path.join(STATE_DIR, "cognitive_daemon.pid")

os.makedirs(STATE_DIR, exist_ok=True)

# ── Промпты Санга (iCanStudy) ────────────────────────────────────────────────
PROMPTS = {
    "compress": (
        "Ты — движок когнитивной компрессии знания (AX1, AX3, T2).\n"
        "Сожми выделенный текст в его неделимый смысловой инвариант (Core Claim).\n"
        "Правила:\n"
        "1. Удали примеры, вводные слова, риторику и воду.\n"
        "2. Выдели причинно-следственную или функциональную структуру (формат: «X -> Y при условии Z» или «X ограничивает Y»).\n"
        "3. Объем: 1-3 предельно точных предложения. Никаких префиксов вроде 'В тексте говорится...'.\n\n"
        "ТЕКСТ:\n{text}"
    ),
    "relate": (
        "Ты — аналитик реляционной структуры знания (AX2, AX6, R1).\n"
        "Определи системную связь между ключевыми сущностями внутри этого текста (или между текстом и контекстом).\n"
        "Правила:\n"
        "1. Назови главные узлы [A] и [B].\n"
        "2. Укажи тип отношения из списка:\n"
        "   - causes (порождает / влечет)\n"
        "   - constrains (ограничивает / является барьером)\n"
        "   - enables (делает возможным)\n"
        "   - contradicts (опровергает / конфликтует)\n"
        "   - exemplifies (является частным проявлением)\n"
        "   - trade-off (компромисс: усиление одного ослабляет другое)\n"
        "3. Кратко (в 2 предложения) объясни скрытый механизм этой связи.\n\n"
        "ТЕКСТ:\n{text}"
    ),
    "predict": (
        "Ты — генератор когнитивных гипотез и калибровки ошибки предсказания (AX7, T6).\n"
        "Пользователь только начинает читать фрагмент или остановился перед продолжением.\n"
        "Сформулируй 1 конкретную гипотезу/вопрос на предсказание:\n"
        "«Если [условие из текста], то что логически должно произойти дальше?»\n"
        "Дай 3 варианта ответа (A, B, C), где правильный требует глубокого понимания механизма, а дистракторы бьют по типичным заблуждениям.\n\n"
        "ТЕКСТ:\n{text}"
    ),
    "reconstruct": (
        "Ты — экзаменатор уровня Reconstruction (AX9, T7, T8).\n"
        "Создай 1 проверочный вопрос на реконструкцию механизма (не на простое запоминание/Recall).\n"
        "Вопрос обязан содержать стресс-тест структуры:\n"
        "- «Что произойдет с Y, если убрать или инвертировать X?» ИЛИ\n"
        "- «Почему данный механизм перестанет работать при условии W?»\n"
        "Формат: Только сам вопрос и в скобках [Ключевой структурный критерий ответа].\n\n"
        "ТЕКСТ:\n{text}"
    ),
    "map": (
        "Ты — архитектор схем и чанкинга (AX2, H1: эвристика 2-4).\n"
        "Преобразуй текст в иерархическую структуру понятий (Nodes + Relations).\n"
        "Правила:\n"
        "1. Максимум 2-4 верхнеуровневых блока (кластера).\n"
        "2. Внутри каждого блока — ключевые узлы со стрелками отношений (->, -x-, <=>).\n"
        "3. Используй компактный текстовый ASCII-формат дерева/схемы.\n\n"
        "ТЕКСТ:\n{text}"
    ),
}


# ── Логирование ──────────────────────────────────────────────────────────────
def log_msg(msg: str):
    try:
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(f"[{ts}] {msg}\n")
    except Exception:
        pass


def log_event(kind: str, **kwargs):
    try:
        payload = {"ts": datetime.now().isoformat(timespec="seconds"), "kind": kind}
        payload.update(kwargs)
        with open(EVENT_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=False) + "\n")
    except Exception:
        pass


# ── Буфер и X11 ─────────────────────────────────────────────────────────────
def get_selected_text() -> str:
    """Сначала пробуем PRIMARY (выделение мышкой), затем CLIPBOARD."""
    for sel in ("primary", "clipboard"):
        try:
            r = subprocess.run(
                ["xclip", "-selection", sel, "-o"],
                capture_output=True,
                text=True,
                timeout=2,
            )
            val = (r.stdout or "").strip()
            if len(val) >= 2:
                return val
        except Exception:
            pass
    return ""


def get_pointer_xy(root_win) -> tuple[int, int]:
    try:
        qp = root_win.query_pointer()
        return qp.root_x, qp.root_y
    except Exception:
        return 80, 80


# ── Запрос к LLM API ────────────────────────────────────────────────────────
def clean_llm_reply(text: str) -> str:
    text = str(text or "").strip()
    text = re.sub(r"^```[a-zA-Z]*\n", "", text)
    text = re.sub(r"\n```$", "", text)
    text = re.sub(r"^(?:готово|результат|вывод|ответ)[:\-–—]*\s*", "", text, flags=re.I)
    return text.strip()


def query_llm(prompt: str) -> str:
    payload = json.dumps({
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2,
        "max_tokens": 500,
    }).encode("utf-8")

    headers = {"Content-Type": "application/json"}
    if API_KEY:
        headers["Authorization"] = f"Bearer {API_KEY}"

    last_err: Optional[Exception] = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            req = urllib.request.Request(API_URL, data=payload, headers=headers)
            with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                content = data["choices"][0]["message"].get("content", "")
                if content:
                    return clean_llm_reply(content)
                raise ValueError("Empty content returned from LLM")
        except Exception as e:
            last_err = e
            log_msg(f"API attempt {attempt}/{MAX_RETRIES} failed: {e}")
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY * attempt)

    raise RuntimeError(f"Все попытки вызова API исчерпаны: {last_err}")


# ── Запуск Popup ─────────────────────────────────────────────────────────────
def show_popup(mode: str, text: str, x: int, y: int):
    if not os.path.exists(POPUP_HELPER):
        log_msg(f"Popup helper not found at {POPUP_HELPER}")
        return
    try:
        proc = subprocess.Popen(
            [sys.executable, POPUP_HELPER],
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            text=True,
        )
        payload = json.dumps({
            "mode": mode,
            "text": text,
            "x": x,
            "y": y,
            "title": f"Cognitive [{mode.upper()}]",
        })
        proc.communicate(input=payload, timeout=5)
    except Exception as e:
        log_msg(f"Failed to spawn popup: {e}")


# ── Диспетчер действий ───────────────────────────────────────────────────────
class CognitiveEngine:
    def __init__(self, disp, root_win):
        self.disp = disp
        self.root = root_win
        self.last_ts = 0.0

    def handle_action(self, mode: str):
        now = time.monotonic()
        if now - self.last_ts < 0.8:
            return
        self.last_ts = now

        x, y = get_pointer_xy(self.root)
        source_text = get_selected_text()
        log_event("action_triggered", mode=mode, text_len=len(source_text))

        if not source_text:
            show_popup("info", "Выделите текст для анализа!", x, y)
            return

        def _worker():
            try:
                template = PROMPTS.get(mode, PROMPTS["compress"])
                prompt = template.format(text=source_text[:25000])
                t0 = time.time()
                result = query_llm(prompt)
                elapsed = time.time() - t0
                log_event("action_success", mode=mode, elapsed_s=round(elapsed, 2))
                GLib.idle_add(show_popup, mode, result, x, y)
            except Exception as e:
                log_event("action_error", mode=mode, error=str(e))
                GLib.idle_add(show_popup, "error", f"Ошибка: {e}", x, y)

        threading.Thread(target=_worker, daemon=True).start()


# ── X11 Key grabbing ─────────────────────────────────────────────────────────
def resolve_key(disp_obj, key_name: str) -> int:
    keysym = XK.string_to_keysym(key_name)
    if not keysym and len(key_name) == 1:
        keysym = ord(key_name)
    kc = disp_obj.keysym_to_keycode(keysym)
    if not kc:
        raise ValueError(f"Cannot resolve keycode for {key_name}")
    return int(kc)


def grab_all_hotkeys(d_obj, root_win, keycodes: dict[str, int]):
    extra_masks = [
        0,
        X.LockMask,                      # CapsLock
        X.Mod2Mask,                      # NumLock
        X.Mod5Mask,                      # ScrollLock
        X.LockMask | X.Mod2Mask,
        X.LockMask | X.Mod5Mask,
        X.Mod2Mask | X.Mod5Mask,
        X.LockMask | X.Mod2Mask | X.Mod5Mask,
    ]
    # Используем комбинацию Ctrl+Alt (ControlMask | Mod1Mask)
    base_mask = X.ControlMask | X.Mod1Mask

    def _err_handler(*_):
        return 0

    d_obj.set_error_handler(_err_handler)
    for kc in keycodes.values():
        for extra in extra_masks:
            root_win.grab_key(kc, base_mask | extra, True, X.GrabModeAsync, X.GrabModeAsync)
    d_obj.sync()
    d_obj.set_error_handler(None)


def run_trigger(mode: str, text: str) -> None:
    """Run one cognitive action from the CLI without starting the hotkey daemon."""
    mode = mode if mode in PROMPTS else "compress"
    d_obj = display.Display()
    root_win = d_obj.screen().root
    try:
        x, y = get_pointer_xy(root_win)
        prompt = PROMPTS[mode].format(text=text[:25000])
        result = query_llm(prompt)
        show_popup(mode, result, x + 15, y + 15)
    except Exception as exc:
        show_popup("error", f"Ошибка: {exc}", x + 15, y + 15)
    finally:
        try:
            d_obj.close()
        except Exception:
            pass


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--trigger-mode", choices=tuple(PROMPTS))
    parser.add_argument("--text")
    args = parser.parse_args()

    if args.trigger_mode:
        text = args.text if args.text is not None else get_selected_text()
        if not text:
            show_popup("info", "Выделите текст для анализа!", 100, 100)
            return
        run_trigger(args.trigger_mode, text)
        return

    with open(PID_FILE, "w", encoding="utf-8") as f:
        f.write(str(os.getpid()))

    d_obj = display.Display()
    root_win = d_obj.screen().root

    # Назначаем клавиши: q, r, p, t, m
    mapping = {
        "compress": resolve_key(d_obj, "q"),
        "relate": resolve_key(d_obj, "r"),
        "predict": resolve_key(d_obj, "p"),
        "reconstruct": resolve_key(d_obj, "t"),
        "map": resolve_key(d_obj, "m"),
    }
    kc_to_mode = {v: k for k, v in mapping.items()}

    grab_all_hotkeys(d_obj, root_win, mapping)
    engine = CognitiveEngine(d_obj, root_win)

    log_msg(f"Cognitive Daemon запущен. PID={os.getpid()}, Model={MODEL}, Endpoint={API_URL}")

    def x11_poll():
        while d_obj.pending_events():
            ev = d_obj.next_event()
            if ev.type == X.KeyPress:
                ctrl = bool(ev.state & X.ControlMask)
                alt = bool(ev.state & X.Mod1Mask)
                if ctrl and alt and ev.detail in kc_to_mode:
                    mode = kc_to_mode[ev.detail]
                    engine.handle_action(mode)
        return True

    GLib.io_add_watch(d_obj.fileno(), GLib.IO_IN, lambda *_: x11_poll() or True)
    Gtk.main()


if __name__ == "__main__":
    try:
        main()
    finally:
        try:
            os.remove(PID_FILE)
        except Exception:
            pass

