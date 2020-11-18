import os
import subprocess

class sh(object):
    
    def __init__(self, args, output=False):
        self.__run(args, output)
    
    def __run(self, cmd, output):
        result = subprocess.run(
            cmd,
            capture_output=not output, 
            shell=True, 
            encoding="utf8")

        self.code = result.returncode
        self.value = result.stdout
        self.error = result.stderr
    
    def clear():
        os.system('clear')