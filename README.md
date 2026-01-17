# 🖥️ Specification Shower

A PySide6 desktop application that displays detailed system specifications in a clean tabbed interface.  
It shows information about your CPU, GPU, RAM, storage, disk health (SMART), motherboard, TPM, network, Bluetooth, WiFi, and SIM card.

---

## ✨ Features

- **CPU**: Brand, cores, threads, architecture, frequency  
- **GPU**: NVIDIA GPU details (via GPUtil)  
- **RAM**: Total, available, used memory  
- **Storage**: Mounted partitions, free space  
- **Disk SMART**: Health status via `smartctl`  
- **Network**: Interfaces and IP addresses  
- **Motherboard**: Manufacturer, product, serial (via WMI or dmidecode)  
- **TPM**: Trusted Platform Module info (Windows/Linux)  
- **Bluetooth**: Nearby devices (via PyBluez)  
- **WiFi**: Scan for SSIDs (via PyWiFi)  
- **SIM**: ModemManager integration on Linux  

Each tab includes a **Refresh button** to update the information live.

---

## 📂 Project Structure

```bash
PyPySideSpecifications/
├── main.py
├── README.md
└── requirements.txt
```
Note: Some features may require additional dependencies or permissions. 
