"""Run visibly in the child's interactive Windows session, never in Session 0."""
from __future__ import annotations

import argparse
import json
import os
import threading
import time
import sys
from pathlib import Path

# -I excludes user site/PYTHONPATH; this file must live in an admin-owned install.
if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from urllib.request import Request, urlopen


def run(config_path):
    from PIL import Image, ImageDraw
    import pystray
    from pystray._util import win32 as tray_win32
    from agent.windows import idle_seconds, lock_workstation, session_locked
    from agent.child_window import ChildWindow
    config = json.loads(open(config_path, encoding="utf-8-sig").read())
    if config.get("lab_enforcement") is not True:
        raise RuntimeError("This tray must only run in an explicitly configured child lab")
    if os.name != "nt":
        raise RuntimeError("Windows tray required")
    import hashlib
    import win32api
    import win32event
    import win32gui
    identity = hashlib.sha256(str(Path(config_path).resolve()).casefold().encode()).hexdigest()[:16]
    singleton = win32event.CreateMutex(None, False, 'Local\\KidSafeTray-' + identity)
    if win32api.GetLastError() == 183:
        existing = win32gui.FindWindow('KidSafeChildWindow', None)
        if existing:
            win32gui.PostMessage(existing, 0x8002, 0, 0)
        return
    stop = threading.Event()
    image = Image.new("RGBA", (64, 64), "#F5EFE6")
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((12, 8, 52, 56), radius=12, fill="#46634A")
    draw.text((24, 22), "K", fill="white")
    def request(path, body=None):
        data = json.dumps({"pid": os.getpid(), **(body or {})}).encode()
        req = Request(f"http://127.0.0.1:{config.get('ipc_port',17843)}" + path, data=data, headers={"Authorization": "Bearer " + config["ipc_token"], "Content-Type": "application/json"})
        with urlopen(req, timeout=2) as response:
            return json.load(response)
    child_window = ChildWindow(lambda minutes: request('/request-time', {'minutes': minutes}))
    def open_child(icon, item):
        try:
            child_window.show()
        except RuntimeError:
            icon.notify('Chưa mở được màn hình của em. Hãy nhờ ba mẹ kiểm tra KidSafe nhé.', 'KidSafe')
    def quit_icon(icon, item):
        stop.set()
        icon.stop()
    class VisibleIcon(pystray.Icon):
        def _message(self, code, flags, **kwargs):
            # pystray's Windows adapter ignores Shell_NotifyIcon's BOOL result.
            # Require OS acknowledgment instead of trusting the visible property.
            import ctypes
            data = tray_win32.NOTIFYICONDATAW(cbSize=ctypes.sizeof(tray_win32.NOTIFYICONDATAW), hWnd=self._hwnd, hID=id(self), uFlags=flags, **kwargs)
            if not tray_win32.Shell_NotifyIcon(code, data):
                raise OSError('Windows could not display or update the KidSafe tray icon')
    icon = VisibleIcon("KidSafe", image, "KidSafe đang hoạt động", pystray.Menu(pystray.MenuItem("Hôm nay của em", open_child, default=True), pystray.MenuItem("Xin thêm giờ", open_child), pystray.MenuItem("Thoát (agent cũng dừng)", quit_icon)))
    def setup(tray):
        previous_reason = None
        explanation = None
        explanation_ack = None
        previous_notice_windows = set()
        failures = 0
        opened = False
        try:
            tray.visible = True
            while not stop.is_set() and tray.visible:
                import ctypes
                import win32gui
                import win32process
                # Explorer/icon loss must stop leasing even if Python's flag is stale.
                tray._message(tray_win32.NIM_MODIFY, tray_win32.NIF_TIP, szTip=tray.title)
                foreground_window = win32gui.GetForegroundWindow()
                foreground_pid = win32process.GetWindowThreadProcessId(foreground_window)[1] if foreground_window else 0
                locked = session_locked()
                try:
                    response = request("/lease", {"icon_visible": bool(tray.visible), "idle_seconds": idle_seconds(), "locked": locked, "foreground_pid": foreground_pid, "explanation_ack": explanation_ack})
                    failures = 0
                except OSError:
                    child_window.update({})
                    failures += 1
                    if failures >= 60:
                        break
                    stop.wait(1)
                    continue
                reason = response.get("reason")
                child_window.update(response.get('child_view', {}))
                if not opened:
                    open_child(tray, None)
                    opened = True
                if reason != previous_reason and reason:
                    tray.notify("Em hãy lưu bài nhé. Đã đến giờ nghỉ hoặc ngoài lịch sử dụng.", "KidSafe")
                for warning in response.get("warnings", []):
                    tray.notify(f"Em còn {warning // 60} phút. Hãy nhớ lưu bài, hoặc xin thêm giờ nhé.", "KidSafe")
                notice = response.get("explanation")
                if notice:
                    title = "KidSafe – " + notice["subject"]
                    windows = []
                    win32gui.EnumWindows(lambda hwnd, _: windows.append(hwnd) if win32gui.IsWindowVisible(hwnd) and win32process.GetWindowThreadProcessId(hwnd)[1] == os.getpid() and win32gui.GetWindowText(hwnd) == title else None, None)
                    if explanation != notice["id"]:
                        explanation = notice["id"]
                        explanation_ack = None
                        previous_notice_windows = set(windows)
                        threading.Thread(target=lambda text=notice["text"], caption=title: ctypes.windll.user32.MessageBoxW(None, text, caption, 0x40 | 0x1000), daemon=True).start()
                    elif set(windows) - previous_notice_windows:
                        explanation_ack = explanation
                if reason and not response.get("stop") and not locked:
                    lock_workstation()
                if response.get("stop"):
                    break
                previous_reason = reason
                stop.wait(1)
        except (OSError, ValueError):
            # No successful visible lease => service will shut itself down.
            pass
        finally:
            stop.set()
            child_window.close()
            tray.stop()
    icon.run(setup)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    run(parser.parse_args().config)
