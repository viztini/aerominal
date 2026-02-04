# Aerominal Process Manager
import subprocess, threading, queue, os, signal

class ProcessManager:
    def __init__(self, config):
        self.config = config
        self.output_queue = queue.Queue()
        self.process = None
        self.cwd = os.getcwd()

    def start(self):
        cmd = self.config.get_setting('behavior', 'shell_path') or ('cmd.exe' if os.name == 'nt' else 'bash')
        args = [cmd, '/k'] if os.name == 'nt' and cmd == 'cmd.exe' else [cmd]
        self.process = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1, universal_newlines=True, creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
        threading.Thread(target=self._read, args=(self.process.stdout,), daemon=True).start()
        threading.Thread(target=self._read, args=(self.process.stderr,), daemon=True).start()

    def _read(self, pipe):
        try:
            for line in iter(pipe.readline, ''):
                if line:
                    if "__CWD__:" in line:
                        self.cwd = line.split("__CWD__:", 1)[1].strip()
                        self.output_queue.put(line)
                    else:
                        self.output_queue.put(line)
        except: pass

    def write(self, cmd):
        if self.process:
            if os.name == 'nt':
                full_cmd = f"{cmd} & echo __CWD__:%CD%\n"
            else:
                full_cmd = f"{cmd}; echo __CWD__:$PWD\n"
            self.process.stdin.write(full_cmd)
            self.process.stdin.flush()

    def interrupt(self):
        if self.process:
            if os.name == 'nt': subprocess.call(['taskkill', '/F', '/T', '/PID', str(self.process.pid)])
            else: self.process.send_signal(signal.SIGINT)
            self.start()

    def stop(self):
        if self.process: self.process.terminate()
