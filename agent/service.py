"""Windows service entry point; installing is an explicit child-lab operation."""
from pathlib import Path
import os
import threading
import sys

# SCM may import by absolute file path; never depend on SYSTEM's current dir.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import win32service
import win32serviceutil


class KidSafeService(win32serviceutil.ServiceFramework):
    _svc_name_ = 'KidSafe'
    _svc_display_name_ = 'KidSafe visible child lab agent'
    _svc_description_ = 'Stops enforcement when the visible child tray disappears.'

    def __init__(self, args):
        super().__init__(args)
        self.stop_event = threading.Event()

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        self.stop_event.set()

    def SvcDoRun(self):
        from agent.runtime import Runtime
        config = Path(os.environ.get('ProgramData', r'C:\ProgramData')) / 'KidSafe/service/config.json'
        runtime = Runtime(config, self.stop_event)
        if runtime.config.get('setup_pending'):
            runtime.store.close()
            config.with_name('setup-ready').touch()
            return
        runtime.run()


if __name__ == '__main__':
    if sys.argv[1:] == ['--run-service']:
        import servicemanager
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(KidSafeService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(KidSafeService)
