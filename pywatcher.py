#coding=utf-8
import os
import inspect
import win32serviceutil 
import win32service 
import win32event 

class PythonService(win32serviceutil.ServiceFramework): 
    """
    Usage: 'python pywatcher.py install|remove|start|stop|restart'
    """
    #服务名
    _svc_name_ = "pyWatcher"
    #服务显示名称
    _svc_display_name_ = "Python Process Watcher"
    #服务描述
    _svc_description_ = "Python Process Watcher"

    def __init__(self, args): 
        import pyini

        win32serviceutil.ServiceFramework.__init__(self, args) 
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        
        this_file = inspect.getfile(inspect.currentframe())
        self.startpath = os.path.abspath(os.path.dirname(this_file))
        self.ini = pyini.Ini(os.path.join(self.startpath, 'watcher.ini'))
        self.logger = self._getLogger()
        self.isAlive = True
        
    def _getLogger(self):
        from logfile import RotatingFile
        
        logger = RotatingFile(os.path.join(self.startpath, self.ini.server.get('log_to', 'pywatcher.log')),
            maxBytes=self.ini.server.get('logfile_maxbytes', 50*1024*1024), 
            backupCount=self.ini.server.get('logfile_backups', 10))

        return logger

    def SvcDoRun(self):
        import time
        import subprocess
        
        #from g_server import main
        self.logger.info("started")
        try:
            self.sub = subprocess.Popen('python g_server.py', 
                stdout=self.logger, 
                stderr=self.logger, shell=True, cwd=self.startpath)
        except Exception as e:
            self.logger.exception(e)
            
        while self.isAlive:
            time.sleep(1)
            
        # 等待服务被停止 
        #win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)
        subprocess.call(['taskkill', '/F', '/T', '/PID', str(self.sub.pid)])
        self.logger.info("stopped")
        
    def SvcStop(self): 
        self.logger.info("stopping....")
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING) 
        # 设置事件 
        win32event.SetEvent(self.hWaitStop) 
        self.isAlive = False
        
if __name__=='__main__': 
    win32serviceutil.HandleCommandLine(PythonService)
