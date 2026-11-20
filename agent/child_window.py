"""Child-facing native Windows window; no browser or account credentials.

Only the tray passes sanitized IPC snapshots here. This module never leases the
service, reads its credentials, changes DNS, or performs enforcement.
"""
from __future__ import annotations

import threading
import time
from datetime import datetime


REASONS = {'outside_schedule': 'Bây giờ là giờ nghỉ. Em có thể xin thêm giờ nhé.',
           'quota_exhausted': 'Em đã dùng hết thời gian trên máy này hôm nay.',
           'parent_lock': 'Ba mẹ vừa cho máy nghỉ.',
           'clock_uncertain': 'KidSafe đang chờ kết nối để kiểm tra lại giờ.'}


def minutes(seconds):
    return max(0, int(max(0, seconds) + 59) // 60)


def presentation(data):
    """Pure view model, shared by native rendering and safe unit tests."""
    request = data.get('request') or {}
    statuses = {'queued': 'Lời xin thêm giờ đã lưu. Đang chờ gửi tới ba mẹ.',
                'pending': 'Ba mẹ đã nhận lời xin thêm giờ của em.',
                'sent': 'Ba mẹ đã đồng ý. Máy đang nhận thêm thời gian.',
                'acknowledged': 'Em đã nhận được thời gian ba mẹ cho thêm!'}
    def rows(key, unit):
        return '\r\n\r\n'.join(f"{item['subject']}  ·  {unit(item['value'])}" for item in data.get(key, [])[:10])
    icons = {'lock': '🔒', 'unlock': '🔓', 'clock': '🕒', 'settings': '⚙'}
    def audit_line(item):
        from agent.enforcer import timezone_for
        try:
            at = datetime.fromisoformat(item['ts']).astimezone(timezone_for(data.get('timezone', 'Asia/Ho_Chi_Minh'))).strftime('%H:%M %d/%m')
        except (KeyError, ValueError):
            at = ''
        return f"{icons.get(item.get('icon'), '🕒')} {item['message']}" + (f'\r\n     {at}' if at else '')
    audit = '\r\n\r\n'.join(audit_line(item) for item in data.get('audit', [])[:10])
    return {'title': 'Hôm nay của ' + (data.get('name') or 'em'),
            'remaining': 'Máy đang được mở' if data.get('override_active') else f"Còn {minutes(data['remaining_sec'])} phút" if 'remaining_sec' in data else 'Đang chờ KidSafe…',
            'entertainment': f"Giải trí (Trò chơi & Video): Còn {minutes(data['entertainment_remaining_sec'])} phút" if 'entertainment_remaining_sec' in data else 'Thông tin giải trí sẽ hiện sau khi kết nối.',
            'connection': 'Ba mẹ đang mở máy cho em đến hết hôm nay.' if data.get('override_active') else REASONS.get(data.get('reason'), 'Đang chờ kết nối với ba mẹ.' if data.get('offline', True) else 'Chúc em một ngày vui vẻ!'),
            'request': statuses.get(request.get('status'), 'Nếu cần dùng thêm máy, em hãy gửi lời xin tới ba mẹ nhé.'),
            'apps': rows('top_apps', lambda value: f'{minutes(value)} phút') or 'Chưa có ứng dụng nào được ghi nhận hôm nay. 🐾',
            'domains': rows('top_domains', lambda value: f'{value} lượt') or 'Các trang em đã dùng sẽ hiện ở đây. 🌱',
            'audit': audit or 'Chưa có thay đổi mới từ ba mẹ. 🌿'}


class ChildWindow:
    def __init__(self, request_time, *, preview=False):
        self.request_time = request_time
        self.preview = preview
        self.data = {}
        self.lock = threading.Lock()
        self.ready = threading.Event()
        self.hwnd = None
        self.thread = None
        self.activity = True
        self.sending = False

    def update(self, data):
        with self.lock:
            self.data = dict(data)
        if self.hwnd:
            import win32gui
            win32gui.PostMessage(self.hwnd, 0x8001, 0, 0)

    def show(self):
        if self.thread is None:
            self.thread = threading.Thread(target=self._run, daemon=True)
            self.thread.start()
        if self.ready.wait(3) and self.hwnd:
            import win32gui
            win32gui.PostMessage(self.hwnd, 0x8002, 0, 0)
        elif self.ready.is_set():
            raise RuntimeError('Could not create the KidSafe child window')

    def close(self):
        if self.hwnd:
            import win32gui
            win32gui.PostMessage(self.hwnd, 0x8003, 0, 0)

    def _run(self):
        import ctypes
        import win32api
        import win32con as C
        import win32gui as G
        from PIL import Image, ImageDraw, ImageWin

        self.G, self.C = G, C
        self.controls, self.backgrounds = {}, {}
        self.fonts = []
        for size, weight in ((18, 400), (30, 700), (34, 700), (18, 600)):
            font = G.LOGFONT()
            font.lfFaceName, font.lfHeight, font.lfWeight = 'Segoe UI', -size, weight
            self.fonts.append(G.CreateFontIndirect(font))
        colors = {'page': (244, 248, 246), 'card': (226, 241, 232), 'white': (255, 255, 255)}
        brushes = {key: G.CreateSolidBrush(win32api.RGB(*value)) for key, value in colors.items()}
        self.brushes, self.colors = brushes, colors
        instance = win32api.GetModuleHandle(None)
        cls = G.WNDCLASS()
        cls.hInstance, cls.lpszClassName = instance, 'KidSafeChildPreview' if self.preview else 'KidSafeChildWindow'
        cls.lpfnWndProc = self._message
        cls.hCursor = G.LoadCursor(0, C.IDC_ARROW)
        G.RegisterClass(cls)
        work = win32api.GetMonitorInfo(win32api.MonitorFromPoint((0, 0)))['Work']
        width, height = min(940, work[2] - work[0] - 32), min(840, work[3] - work[1] - 32)
        try:
            self.hwnd = G.CreateWindowEx(0, cls.lpszClassName, 'KidSafe – Xem trước' if self.preview else 'KidSafe – Hôm nay của em',
                                         C.WS_OVERLAPPEDWINDOW | C.WS_CLIPCHILDREN, work[0] + 16, work[1] + 16, width, height, 0, 0, instance, None)
            def control(key, kind, text='', style=0, font=0, background='page'):
                if kind == 'STATIC': style |= C.SS_NOPREFIX | (C.SS_CENTER if key in (1, 2) else 0) | (C.SS_ENDELLIPSIS if key == 1 else 0)
                handle = G.CreateWindowEx(0, kind, text, C.WS_CHILD | C.WS_VISIBLE | style, 0, 0, 10, 10, self.hwnd, key, instance, None)
                G.SendMessage(handle, C.WM_SETFONT, self.fonts[font], True)
                self.controls[key], self.backgrounds[handle] = handle, background
            for key in (1, 2, 3, 4, 5, 6, 7, 8, 9):
                control(key, 'STATIC', font=1 if key == 1 else 2 if key == 4 else 3 if key in (3, 8, 9) else 0,
                        background='card' if key in (3, 4, 5) else 'page')
            control(101, 'BUTTON', '✋ Xin thêm giờ', C.WS_TABSTOP, 3)
            control(102, 'COMBOBOX', style=C.CBS_DROPDOWNLIST | C.WS_VSCROLL | C.WS_TABSTOP)
            for text in ('5 phút', '10 phút', '15 phút'): G.SendMessage(self.controls[102], C.CB_ADDSTRING, 0, text)
            G.SendMessage(self.controls[102], C.CB_SETCURSEL, 1, 0)
            control(103, 'BUTTON', 'Hoạt động hôm nay', C.WS_TABSTOP)
            control(104, 'BUTTON', 'Thay đổi từ ba mẹ', C.WS_TABSTOP)
            for key in (201, 202, 203):
                control(key, 'EDIT', style=C.ES_MULTILINE | C.ES_READONLY | C.ES_AUTOVSCROLL | C.WS_VSCROLL | C.WS_TABSTOP, background='white')
            self._layout()
            self._refresh()
            self.ready.set()
            from ctypes import wintypes
            user32 = ctypes.windll.user32
            user32.GetMessageW.argtypes = [ctypes.POINTER(wintypes.MSG), wintypes.HWND, wintypes.UINT, wintypes.UINT]
            user32.IsDialogMessageW.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.MSG)]
            user32.TranslateMessage.argtypes = [ctypes.POINTER(wintypes.MSG)]
            user32.DispatchMessageW.argtypes = [ctypes.POINTER(wintypes.MSG)]
            user32.DispatchMessageW.restype = ctypes.c_ssize_t
            message = wintypes.MSG()
            while user32.GetMessageW(ctypes.byref(message), None, 0, 0) > 0:
                if message.message == C.WM_KEYDOWN and message.wParam == C.VK_ESCAPE:
                    G.PostMessage(self.hwnd, C.WM_CLOSE, 0, 0)
                elif not user32.IsDialogMessageW(self.hwnd, ctypes.byref(message)):
                    user32.TranslateMessage(ctypes.byref(message))
                    user32.DispatchMessageW(ctypes.byref(message))
        finally:
            self.ready.set()
            self.hwnd = None
            for brush in brushes.values(): G.DeleteObject(brush)
            for font in self.fonts: G.DeleteObject(font)

    def _layout(self):
        G, C = self.G, self.C
        _, _, w, h = G.GetClientRect(self.hwnd)
        move = lambda key, x, y, width, height: G.MoveWindow(self.controls[key], x, y, max(1, width), max(1, height), True)
        for key, y, height in ((1, 18, 44), (2, 68, 30), (6, 386, 46)):
            move(key, 24, y, w - 48, height)
        move(3, 44, 143, w - 160, 25)
        move(4, 44, 173, w - 160, 48)
        move(5, 44, 256, w - 100, 28)
        move(7, 24, 339, 220, 30)
        move(102, 244, 335, 110, 160)
        move(101, 378, 331, max(160, w - 402), 46)
        move(103, 24, 439, (w - 60) // 2, 42)
        move(104, 36 + (w - 60) // 2, 439, (w - 60) // 2, 42)
        move(8, 24, 499, (w - 72) // 2, 30)
        move(9, 48 + (w - 72) // 2, 499, (w - 72) // 2, 30)
        move(201, 36, 543, (w - 96) // 2, h - 575)
        move(202, 60 + (w - 96) // 2, 543, (w - 96) // 2, h - 575)
        move(203, 36, 543, w - 72, h - 575)
        self._tabs()

    def _tabs(self):
        G, C = self.G, self.C
        for key in (9, 201, 202): G.ShowWindow(self.controls[key], C.SW_SHOW if self.activity else C.SW_HIDE)
        G.ShowWindow(self.controls[203], C.SW_HIDE if self.activity else C.SW_SHOW)
        G.SetWindowText(self.controls[8], 'Hôm nay em đã dùng gì?' if self.activity else 'Những thay đổi liên quan đến em')
        G.InvalidateRect(self.hwnd, None, False)

    def _refresh(self):
        if not self.controls: return
        with self.lock: data = dict(self.data)
        view = presentation(data)
        values = {1: view['title'], 2: view['connection'], 3: 'Thời gian trên máy này hôm nay', 4: view['remaining'], 5: view['entertainment'],
                  6: view['request'], 7: 'Em muốn xin thêm:', 9: 'Các trang em đã dùng', 201: view['apps'], 202: view['domains'], 203: view['audit']}
        for key, value in values.items():
            if self.G.GetWindowText(self.controls[key]) != value: self.G.SetWindowText(self.controls[key], value)
        self.G.EnableWindow(self.controls[101], not self.sending and not self.preview)
        self.G.InvalidateRect(self.hwnd, None, False)

    def _send(self):
        if self.sending or self.preview: return
        selected = self.G.SendMessage(self.controls[102], self.C.CB_GETCURSEL, 0, 0)
        minutes_requested = (5, 10, 15)[selected if 0 <= selected < 3 else 1]
        self.sending = True
        self._refresh()
        def work():
            try:
                result = self.request_time(minutes_requested)
                text = 'Em đã gửi lời xin thêm giờ. Hãy đợi ba mẹ trả lời nhé.' if result.get('queued') else 'Em đã gửi lời xin trước đó. Hãy đợi ba mẹ trả lời nhé.'
            except (OSError, ValueError):
                text = 'Chưa gửi được lời xin. Em thử lại sau một lát nhé.'
            self.sending = False
            with self.lock: self.message = text
            if self.hwnd: self.G.PostMessage(self.hwnd, 0x8004, 0, 0)
        threading.Thread(target=work, daemon=True).start()

    def _message(self, hwnd, message, wparam, lparam):
        G, C = self.G, self.C
        if message == C.WM_CLOSE:
            if self.preview: G.DestroyWindow(hwnd)
            else: G.ShowWindow(hwnd, C.SW_HIDE)
            return 0
        if message == C.WM_DESTROY:
            G.PostQuitMessage(0)
            return 0
        if message == C.WM_GETMINMAXINFO:
            import ctypes
            from ctypes import wintypes
            points = ctypes.cast(lparam, ctypes.POINTER(wintypes.POINT * 5)).contents
            points[3].x, points[3].y = 740, 700
            return 0
        if message == C.WM_SIZE and self.controls:
            self._layout()
            return 0
        if message == C.WM_COMMAND:
            key = wparam & 0xffff
            if key == 101: self._send()
            elif key in (103, 104): self.activity = key == 103; self._tabs()
            return 0
        if message == 0x8001: self._refresh(); return 0
        if message == 0x8002:
            G.ShowWindow(hwnd, C.SW_SHOWNORMAL)
            G.ShowWindow(hwnd, C.SW_RESTORE)
            try: G.SetForegroundWindow(hwnd)
            except Exception: pass
            return 0
        if message == 0x8003: G.DestroyWindow(hwnd); return 0
        if message == 0x8004:
            G.SetWindowText(self.controls[6], self.message)
            G.EnableWindow(self.controls[101], True)
            return 0
        if message in (C.WM_CTLCOLORSTATIC, C.WM_CTLCOLOREDIT):
            import win32api
            background = self.backgrounds.get(lparam, 'page')
            G.SetBkColor(wparam, win32api.RGB(*self.colors[background]))
            G.SetTextColor(wparam, win32api.RGB(35, 65, 49))
            return self.brushes[background]
        if message == C.WM_ERASEBKGND: return 1
        if message == C.WM_PAINT:
            from PIL import Image, ImageDraw, ImageWin
            dc, paint = G.BeginPaint(hwnd)
            try:
                _, _, w, h = G.GetClientRect(hwnd)
                image = Image.new('RGB', (max(1,w), max(1,h)), self.colors['page'])
                draw = ImageDraw.Draw(image)
                draw.rounded_rectangle((24, 125, w - 24, 313), 24, fill=self.colors['card'])
                with self.lock: data = dict(self.data)
                for y, value, total, color in ((230, data.get('remaining_sec',0), data.get('budget_sec',0), '#4F9973'),
                                               (291, data.get('entertainment_remaining_sec',0), data.get('entertainment_quota_sec',0), '#A37AC2')):
                    draw.rounded_rectangle((44,y,w-140,y+10),5,fill='#C9DBD0')
                    fraction = min(1,max(0,value/max(1,total)))
                    if fraction: draw.rounded_rectangle((44,y,44+(w-184)*fraction,y+10),5,fill=color)
                draw.ellipse((w-112,154,w-48,218),fill='#F2D393')
                draw.ellipse((w-95,174,w-90,180),fill='#46634A');draw.ellipse((w-71,174,w-66,180),fill='#46634A')
                draw.arc((w-94,177,w-66,202),0,180,fill='#46634A',width=3)
                if self.activity:
                    for x1,x2 in ((24,(w-24)//2),(36+(w-48)//2,w-24)): draw.rounded_rectangle((x1,531,x2,h-20),14,fill='white')
                else: draw.rounded_rectangle((24,531,w-24,h-20),14,fill='white')
                ImageWin.Dib(image).draw(dc,(0,0,w,h))
            finally: G.EndPaint(hwnd,paint)
            return 0
        return G.DefWindowProc(hwnd,message,wparam,lparam)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--preview', action='store_true', required=True)
    parser.parse_args()
    window = ChildWindow(lambda minutes: {}, preview=True)
    window.update({'name': 'An', 'remaining_sec': 4200, 'budget_sec': 7200,
                   'entertainment_remaining_sec': 1500, 'entertainment_quota_sec': 2700,
                   'offline': False, 'top_apps': [{'subject':'notepad.exe','value':1200}],
                   'top_domains':[{'subject':'example.com','value':3}],
                   'audit':[{'icon':'clock','message':'Ba mẹ đã cập nhật lịch sử dụng của em.'}]})
    window.show()
    if window.thread: window.thread.join()
