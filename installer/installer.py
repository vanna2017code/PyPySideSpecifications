import sys
import subprocess
from PySide6.QtCore import QObject, Signal, Slot, QThread
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine


class InstallerWorker(QThread):
    log_signal = Signal(str)
    finished_signal = Signal(bool)

    def __init__(self, repo_url: str, install_dir: str):
        super().__init__()
        self.repo_url = repo_url
        self.install_dir = install_dir

    def run(self):
        try:
            # Clone repo
            self.log_signal.emit(f"Cloning {self.repo_url} into {self.install_dir}...\n")
            clone_cmd = ["git", "clone", self.repo_url, self.install_dir]
            proc = subprocess.Popen(clone_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            for line in proc.stdout:
                self.log_signal.emit(line)
            proc.wait()
            if proc.returncode != 0:
                self.finished_signal.emit(False)
                return

            # Install with pip
            self.log_signal.emit("\nRunning pip install . ...\n")
            pip_cmd = [sys.executable, "-m", "pip", "install", "."]
            proc = subprocess.Popen(pip_cmd, cwd=self.install_dir,
                                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            for line in proc.stdout:
                self.log_signal.emit(line)
            proc.wait()
            self.finished_signal.emit(proc.returncode == 0)

        except Exception as e:
            self.log_signal.emit(f"Error: {e}")
            self.finished_signal.emit(False)


class InstallerBridge(QObject):
    logOutput = Signal(str)
    installFinished = Signal(bool)

    @Slot(str, str)
    def runInstall(self, repo_url, install_dir):
        self.worker = InstallerWorker(repo_url, install_dir)
        self.worker.log_signal.connect(self.logOutput)
        self.worker.finished_signal.connect(self.installFinished)
        self.worker.start()

    @Slot(str)
    def launchApp(self, app_dir):
        try:
            subprocess.Popen([sys.executable, "spec_shower.py"], cwd=app_dir)
            self.logOutput.emit("🚀 Launched SpecShower app!\n")
        except Exception as e:
            self.logOutput.emit(f"Failed to launch app: {e}\n")


if __name__ == "__main__":
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()

    installer = InstallerBridge()
    engine.rootContext().setContextProperty("installer", installer)

    engine.load("main.qml")
    if not engine.rootObjects():
        sys.exit(-1)

    sys.exit(app.exec())
