import sys
import platform
import subprocess
import psutil
import cpuinfo
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QTextEdit, QTabWidget
)

# Optional imports
try:
    import GPUtil
except ImportError:
    GPUtil = None

try:
    import wmi
except ImportError:
    wmi = None


def get_cpu_info():
    info = cpuinfo.get_cpu_info()
    return f"""CPU: {info.get('brand_raw')}
Cores: {psutil.cpu_count(logical=False)}
Threads: {psutil.cpu_count(logical=True)}
Arch: {platform.machine()}
Freq: {psutil.cpu_freq().current:.2f} MHz"""


def get_gpu_info():
    if GPUtil:
        gpus = GPUtil.getGPUs()
        return "\n".join([f"{gpu.name} | {gpu.memoryTotal}MB | Load: {gpu.load*100:.1f}%" for gpu in gpus])
    return "No NVIDIA GPU detected or GPUtil not installed."


def get_ram_info():
    mem = psutil.virtual_memory()
    return f"Total: {mem.total/1e9:.2f} GB\nAvailable: {mem.available/1e9:.2f} GB\nUsed: {mem.used/1e9:.2f} GB"


def get_storage_info():
    parts = psutil.disk_partitions()
    details = []
    for p in parts:
        try:
            usage = psutil.disk_usage(p.mountpoint)
            details.append(f"{p.device} ({p.mountpoint}) - {usage.total/1e9:.2f} GB total, {usage.free/1e9:.2f} GB free")
        except PermissionError:
            continue
    return "\n".join(details)


def get_smart_info():
    try:
        result = subprocess.run(["smartctl", "-H", "/dev/sda"], capture_output=True, text=True)
        return result.stdout
    except Exception as e:
        return f"SMART info not available: {e}"


def get_network_info():
    addrs = psutil.net_if_addrs()
    return "\n".join([f"{iface}: {', '.join([a.address for a in addr if a.family == 2])}" for iface, addr in addrs.items()])


def get_motherboard_info():
    if platform.system() == "Windows" and wmi:
        c = wmi.WMI()
        board = c.Win32_BaseBoard()[0]
        return f"Manufacturer: {board.Manufacturer}\nProduct: {board.Product}\nSerial: {board.SerialNumber}"
    elif platform.system() == "Linux":
        try:
            result = subprocess.run(["dmidecode", "-t", "baseboard"], capture_output=True, text=True)
            return result.stdout
        except Exception as e:
            return f"dmidecode not available: {e}"
    return "Motherboard info not available."


def get_tpm_info():
    if platform.system() == "Windows":
        try:
            result = subprocess.run(
                ["powershell", "-Command", "Get-WmiObject -Namespace 'Root\\CIMv2\\Security\\MicrosoftTpm'"],
                capture_output=True, text=True
            )
            return result.stdout
        except Exception as e:
            return f"TPM info not available: {e}"
    elif platform.system() == "Linux":
        try:
            result = subprocess.run(["tpm2_getrandom", "8"], capture_output=True, text=True)
            return "TPM available: " + result.stdout
        except Exception as e:
            return f"TPM info not available: {e}"
    return "TPM info not available."


def get_bluetooth_info():
    try:
        import bluetooth
        devices = bluetooth.discover_devices(lookup_names=True)
        return "\n".join([f"{addr} - {name}" for addr, name in devices])
    except Exception as e:
        return f"Bluetooth info not available: {e}"


def get_wifi_info():
    try:
        import pywifi
        wifi = pywifi.PyWiFi()
        iface = wifi.interfaces()[0]
        iface.scan()
        results = iface.scan_results()
        return "\n".join([f"{net.ssid} ({net.bssid})" for net in results])
    except Exception as e:
        return f"WiFi info not available: {e}"


def get_sim_info():
    try:
        result = subprocess.run(["mmcli", "-L"], capture_output=True, text=True)
        return result.stdout
    except Exception as e:
        return f"SIM info not available: {e}"

class SpecShower(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("System Specification Shower")
        self.resize(900, 700)

        # Tabs
        self.tabs = QTabWidget()
        self.info_funcs = [
            get_cpu_info,
            get_gpu_info,
            get_ram_info,
            get_storage_info,
            get_smart_info,
            get_network_info,
            get_motherboard_info,
            get_tpm_info,
            get_bluetooth_info,
            get_wifi_info,
            get_sim_info,
        ]

        # Keep references to text widgets for refresh
        self.text_widgets = []
        for func, name in zip(self.info_funcs,
                              ["CPU","GPU","RAM","Storage","Disk SMART","Network",
                               "Motherboard","TPM","Bluetooth","WiFi","SIM"]):
            self.tabs.addTab(self.create_tab(func), name)

        # Global refresh button
        refresh_all_btn = QPushButton("Refresh All")
        refresh_all_btn.clicked.connect(self.refresh_all)

        # Layout
        container = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.tabs)
        layout.addWidget(refresh_all_btn)
        container.setLayout(layout)
        self.setCentralWidget(container)

    def create_tab(self, info_func):
        widget = QWidget()
        layout = QVBoxLayout()

        text = QTextEdit()
        text.setReadOnly(True)
        text.setText(info_func())

        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(lambda: text.setText(info_func()))

        layout.addWidget(text)
        layout.addWidget(refresh_btn)
        widget.setLayout(layout)

        # Save reference for global refresh
        self.text_widgets.append((text, info_func))
        return widget

    def refresh_all(self):
        for text, func in self.text_widgets:
            text.setText(func())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SpecShower()
    window.show()
    sys.exit(app.exec())