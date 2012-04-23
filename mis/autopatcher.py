# Copyright 2011 Mathias Ruediger <ruediger@blueboot.org>
# See LICENSE for details.
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

    def getContent(self, filename, url, patchargs=[]):
        scriptname = self.scripts[filename]
        process = subprocess.Popen(
            [scriptname, url] + patchargs, 
            shell=False, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE)

        (stdoutdata, stderrdata) = process.communicate()
        if stderrdata:
            raise Exception(stderrdata)
        return stdoutdata
