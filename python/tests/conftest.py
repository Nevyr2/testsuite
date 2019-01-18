# content of testsuite.py
import pytest
import subprocess
import signal
import os
import sys

#import warnings
#warnings.filterwarnings("ignore")
time = [0,1,2,3,4,5,6,7,8,9]
sanity = 0
category = 0
timeout = 0

def options():
    global time
    global sanity
    global category
    global timeout
    next_one = 0
    my_file = open("py_file", "r")
    for lines in my_file.readlines():
        if next_one:
            print(lines)
            timeout = lines
            next_one = 0
            continue
        if lines[0:-1] == "-c" or lines[0:-1] == "--category":
            category = 1
        if lines[0:-1] == "-l" or lines[0:-1] == "--list":
            ls = os.listdir('../tests/category')
            print("\n\nList of Test Categories : \n")
            for j in ls:
                print("-> " + j[0:-4])
            print("\n")
        if lines[0:-1] == "-s" or lines[0:-1] == "--sanity":
            sanity = 1
        if lines[0:-1] == "-t":
            next_one=1
        mixed_type = (sanity, category, timeout)
    return (sanity, category, timeout)

options()

def pytest_collect_file(parent, path):
    global category
    if category == 1:
        my_file = open("py_file", "r")
        for lines in my_file.readlines():
            if path.ext == ".yml" and path.basename.startswith(lines[0:-1]) \
            and lines[0] != '-':
                while lines[0] not in time:
                    return YamlFile("../tests/category/" + 
                        lines[0:-1] + ".yml", parent)
            my_file.close()
    else:
        if path.ext == ".yml" and path.basename.startswith("test"):
                return YamlFile(path, parent)

class YamlFile(pytest.File):
    def collect(self):
        import yaml
        raw = yaml.safe_load(self.fspath.open())
        for name, spec in sorted(raw.items()):
            if spec['type'] == "command_diff":
                yield CommandDiffItem(name, self, spec)
            elif spec['type'] == "output_diff":
                yield OutputDiffItem(name, self, spec)
            else:
                yield CommandDiffItem(name, self, spec)

class YamlItem(pytest.Item):
    def __init__(self, name, parent, spec):
        super(YamlItem, self).__init__(name, parent)
        self.spec = spec
        self.command = str.encode(self.spec['command'])
        if 'expected' in self.spec:
            self.expected = self.spec['expected']

    def runtest(self):
        global sanity
        global timeout
        global out
        global err
        if sanity == 1:
            process = subprocess.Popen(["valgrind", "./42sh"],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            stdin=subprocess.PIPE)
        else:
            process = subprocess.Popen(["./42sh"],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            stdin=subprocess.PIPE)
        if timeout != 0:
            signal.alarm(timeout)
            try:
                out, err = process.communicate(input=self.command + 
                        str.encode("\n"))
            except:
                os.kill(process, signal.SIGTERM)
                os.waitpid(process)
                print("\nTimed Out !!!\n")
        
        else:
            out, err = process.communicate(input=self.command + 
                    str.encode("\n"))

        if 'stdout' in self.expected:
            if self.expected['stdout'] != out:
                raise YamlException('stdout', self.expected['stdout'], out)
        elif out:
            raise YamlException('stdout', b'(empty)', out)
        if 'stderr' in self.expected:
            if out:
                raise YamlException(b'stderr', self.expected['stderr'], err)
        elif err:
            raise YamlException(b'stderr', b'(empty)', err)
        if 'rvalue' in self.expected:
            if int(process.returncode) != int(self.expected['rvalue']):
                raise YamlException('return value',
                str(self.expected['rvalue']),
                str(process.returncode))

    def repr_failure(self, excinfo):
        global sanity
        if isinstance(excinfo.value, YamlException):
            instance = excinfo.value
            if sanity == 1:
                return "\n".join(
                    [
                        "\033[31m\nusecase execution failed:\n\033[0m"
                        "\033[36m\ncommand :\033[0m %s\033[33m\n\nexpected\033[0m '%s'"
                        "\033[35m\n\ngot\033[0m '%s'\n" % (self.command,
                                                      instance.expected_value,
                                                      instance.output_value[350:480])
                    ])
            else:
                return "\n".join(
                    [
                        "\033[31m\nusecase execution failed:\n\033[0m"
                        "\033[36m\ncommand :\033[0m %s\033[33m\n\nexpected\033[0m '%s'"
                        "\033[35m\n\ngot\033[0m '%s'\n" % (self.command,
                                                      instance.expected_value,
                                                      instance.output_value)
                    ])

    def reportinfo(self):
        return self.fspath, 0, "usercase : %s" % self.name


class CommandDiffItem(YamlItem):
    def __init__(self, name, parent, spec):
        super().__init__(name, parent, spec)
        bash_process = subprocess.Popen(["bash"],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                stdin=subprocess.PIPE)
        out, err = bash_process.communicate(input=self.command)
        self.expected= {}
        if out:
            self.expected['stdout'] = out
        if err:
            self.expected['stderr'] = err
        self.expected['rvalue'] = bash_process.returncode

class OutputDiffItem(YamlItem):
    def __init__(self, name, parent, spec):
        super().__init__(name, parent, spec)
        for item in self.expected:
            if item == "rvalue":
                self.expected['rvalue'] = int(self.expected['rvalue'])


class YamlException(Exception):
    """ custom exception for error reporting. """
    def __init__(self, expected_type, expected_value, output_value):
        self.expected_type = expected_type
        self.expected_value = expected_value
        self.output_value = output_value
