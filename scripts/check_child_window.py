"""Native-only visual smoke test using mock data and PrintWindow, never the desktop."""
import ctypes
import json
import time
from pathlib import Path
import win32gui as G
import struct
from ctypes import wintypes
from PIL import Image
from agent.child_window import ChildWindow

import argparse
parser = argparse.ArgumentParser(description='Safely check the native child UI without a service or enforcement')
parser.add_argument('--output', type=Path, default=Path('.tmp/child-ui'))
out = parser.parse_args().output
out.mkdir(parents=True, exist_ok=True)
window = ChildWindow(lambda minutes: {}, preview=True)
window.update({'name':'An','remaining_sec':4200,'budget_sec':7200,
               'entertainment_remaining_sec':1500,'entertainment_quota_sec':2700,
               'offline':False,'top_apps':[{'subject':'notepad.exe','value':1200}],
               'top_domains':[{'subject':'example.com','value':3}],
               'audit':[{'icon':'unlock','message':'Ba mẹ đã mở khóa máy.','ts':'2026-11-07T01:00:00+00:00'}]})
window.show()
time.sleep(.3)

def capture(name):
    rect=G.GetWindowRect(window.hwnd); width,height=rect[2]-rect[0],rect[3]-rect[1]
    dc=G.GetWindowDC(window.hwnd); target=G.CreateCompatibleDC(dc)
    bitmap=G.CreateCompatibleBitmap(dc,width,height);old=G.SelectObject(target,bitmap)
    printer=ctypes.windll.user32.PrintWindow
    printer.argtypes=[wintypes.HWND,wintypes.HDC,wintypes.UINT]
    assert printer(window.hwnd,target,2)
    G.SelectObject(target,old)
    info=ctypes.create_string_buffer(struct.pack('<IiiHHIIiiII',40,width,-height,1,32,0,width*height*4,0,0,0,0))
    pixels=ctypes.create_string_buffer(width*height*4)
    getbits=ctypes.windll.gdi32.GetDIBits
    getbits.argtypes=[wintypes.HDC,wintypes.HANDLE,wintypes.UINT,wintypes.UINT,ctypes.c_void_p,ctypes.c_void_p,wintypes.UINT]
    assert getbits(dc,int(bitmap),0,height,pixels,info,0)==height
    Image.frombuffer('RGB',(width,height),pixels.raw,'raw','BGRX',0,1).save(out/name)
    G.DeleteObject(bitmap);G.DeleteDC(target);G.ReleaseDC(window.hwnd,dc)

try:
    capture('child-native.png')
    assert '70 phút' in G.GetWindowText(window.controls[4])
    assert 'notepad.exe' in G.GetWindowText(window.controls[201])
    assert G.SendMessage(window.controls[102],0x146,0,0)==3 # CB_GETCOUNT
    G.SendMessage(window.hwnd,0x111,104,0);time.sleep(.2)
    assert G.IsWindowVisible(window.controls[203]) and not G.IsWindowVisible(window.controls[201])
    assert 'Ba mẹ đã mở khóa' in G.GetWindowText(window.controls[203])
    capture('child-audit.png')
    G.SendMessage(window.hwnd,0x111,103,0)
    G.SetWindowPos(window.hwnd,0,0,0,740,700,0x16);time.sleep(.2)
    _,_,width,height=G.GetClientRect(window.hwnd)
    for key,control in window.controls.items():
        if G.IsWindowVisible(control):
            rect=G.GetWindowRect(control)
            left,top=G.ScreenToClient(window.hwnd,(rect[0],rect[1]))
            right,bottom=G.ScreenToClient(window.hwnd,(rect[2],rect[3]))
            assert left>=0 and top>=0 and right<=width+1 and bottom<=height+1,(key,left,top,right,bottom,width,height)
    capture('child-small.png')
    window.update({});time.sleep(.2)
    assert G.GetWindowText(window.controls[4])=='Đang chờ KidSafe…'
    (out/'native.json').write_text(json.dumps({'window':True,'tabs':True,'request_choices':3,'small_window_controls_fit':True,'unknown_not_zero':True},indent=2))
    print('PASS native window, activity/audit tabs, three request choices, minimum size and disconnected state')
finally:
    window.close();window.thread.join(3)
