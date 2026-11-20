"""Windows adapters; none of these functions run during import or ordinary tests."""
from __future__ import annotations

import ctypes
import os
from pathlib import Path


def require_windows():
    if os.name != "nt":
        raise OSError("Windows 10/11 x64 required")


def apply_service_acl(directory):
    """Only SYSTEM/Administrators may access service secrets and SQLite files."""
    require_windows()
    import ntsecuritycon
    import win32security
    target = Path(directory).resolve(strict=True)
    system = win32security.CreateWellKnownSid(win32security.WinLocalSystemSid, None)
    admins = win32security.CreateWellKnownSid(win32security.WinBuiltinAdministratorsSid, None)
    acl = win32security.ACL()
    flags = win32security.OBJECT_INHERIT_ACE | win32security.CONTAINER_INHERIT_ACE
    for sid in (system, admins):
        acl.AddAccessAllowedAceEx(win32security.ACL_REVISION, flags, ntsecuritycon.FILE_ALL_ACCESS, sid)
    win32security.SetNamedSecurityInfo(str(target), win32security.SE_FILE_OBJECT, win32security.DACL_SECURITY_INFORMATION | win32security.PROTECTED_DACL_SECURITY_INFORMATION, None, None, acl, None)


def protect_secret(value: bytes):
    require_windows()
    import win32crypt
    # Current-user DPAPI scope: service secrets must be enrolled as LocalSystem.
    return win32crypt.CryptProtectData(value, "KidSafe service secret", None, None, None, 0)


def unprotect_secret(value: bytes):
    require_windows()
    import win32crypt
    return win32crypt.CryptUnprotectData(value, None, None, None, 0)[1]


def idle_seconds():
    require_windows()
    class LastInput(ctypes.Structure):
        _fields_ = [("cbSize", ctypes.c_uint), ("dwTime", ctypes.c_uint)]
    info = LastInput()
    info.cbSize = ctypes.sizeof(info)
    if not ctypes.windll.user32.GetLastInputInfo(ctypes.byref(info)):
        raise ctypes.WinError()
    return ((ctypes.windll.kernel32.GetTickCount() - info.dwTime) & 0xFFFFFFFF) / 1000


def session_locked():
    require_windows()
    from ctypes import wintypes
    user32 = ctypes.WinDLL('user32', use_last_error=True)
    user32.OpenInputDesktop.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    user32.OpenInputDesktop.restype = wintypes.HANDLE
    user32.GetUserObjectInformationW.argtypes = [wintypes.HANDLE, ctypes.c_int, wintypes.LPVOID, wintypes.DWORD, ctypes.POINTER(wintypes.DWORD)]
    user32.GetUserObjectInformationW.restype = wintypes.BOOL
    user32.CloseDesktop.argtypes = [wintypes.HANDLE]
    user32.CloseDesktop.restype = wintypes.BOOL
    # Read the active input-desktop name; never switch the user's desktop.
    desktop = user32.OpenInputDesktop(0, False, 0x0001)
    if not desktop:
        return True
    try:
        name = ctypes.create_unicode_buffer(512)
        needed = wintypes.DWORD()
        if not user32.GetUserObjectInformationW(desktop, 2, name, ctypes.sizeof(name), ctypes.byref(needed)):
            return True
        return name.value.casefold() != 'default'
    finally:
        user32.CloseDesktop(desktop)


def lock_workstation():
    require_windows()
    if not ctypes.windll.user32.LockWorkStation():
        raise ctypes.WinError()


def verify_tray_peer(payload, address, *, port, python_exe, tray_script, tray_config, username, base_python=None):
    """Bind the lease to the actual TCP owner, trusted isolated Python, and user."""
    import psutil
    import pywintypes
    try:
        owners = {item.pid for item in psutil.net_connections(kind="tcp") if item.laddr and item.raddr and item.laddr.ip == "127.0.0.1" and item.laddr.port == address[1] and item.raddr.port == port}
        pid = payload.get("pid")
        if pid not in owners or pid is None:
            return False
        process = psutil.Process(pid)
        expected = [str(Path(python_exe).resolve()), "-I", str(Path(tray_script).resolve()), "--config", str(Path(tray_config).resolve())]
        actual = process.cmdline()
        if len(actual) != len(expected) or any(a.casefold() != b.casefold() for a, b in zip(actual[1:], expected[1:])):
            return False
        executable = Path(process.exe()).resolve()
        launcher = Path(python_exe).resolve()
        if executable == launcher:
            if Path(actual[0]).resolve() != launcher:
                return False
        else:
            # Windows venv python.exe is a redirector: the TCP owner is its
            # base-python child. Authenticate both protected processes.
            if not base_python or executable != Path(base_python).resolve() or Path(actual[0]).resolve() != executable:
                return False
            parent = process.parent()
            if not parent or Path(parent.exe()).resolve() != launcher or [part.casefold() for part in parent.cmdline()] != [part.casefold() for part in expected]:
                return False
        if process.username().casefold() != username.casefold():
            return False
        import win32api
        import win32security
        handle = win32api.OpenProcess(0x1000, False, pid)
        try:
            token = win32security.OpenProcessToken(handle, win32security.TOKEN_QUERY)
            try:
                admins = win32security.CreateWellKnownSid(win32security.WinBuiltinAdministratorsSid, None)
                if any(group == admins for group, attributes in win32security.GetTokenInformation(token, win32security.TokenGroups)):
                    return False
            finally:
                token.Close()
        finally:
            handle.Close()
        session = ctypes.c_uint()
        return bool(ctypes.windll.kernel32.ProcessIdToSessionId(pid, ctypes.byref(session))) and session.value != 0
    except (OSError, psutil.Error, pywintypes.error):
        return False
