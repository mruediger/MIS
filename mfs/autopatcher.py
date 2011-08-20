"""A class that replaces the content of a file by the result of a script"""

import subprocess

class Autopatcher(object):
    
    def __init__(self, configfile):
        self.scripts = dict()
        with open(configfile) as cfile:
            for line in cfile:
                #ignore blank lines
                if line.strip() == "": continue
                #ignore comments
                if line[0] == '#': continue
                k,v = line.split(':')
                self.scripts[k.strip()] = v.strip()
        
    def listFiles(self):
        return self.scripts.keys()

    def getContent(self, filename):
        scriptname = self.scripts[filename]
        process = subprocess.Popen(
            [scriptname], 
            shell=False, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            universal_newlines=True)

        (stdoutdata, stderrdata) = process.communicate()
        if (stderrdata) and (len(stderrdata) > 0):
            raise Exception(stderrdata)
        return stdoutdata
