import subprocess

from django.contrib.staticfiles.finders import BaseFinder


class CompileFinder(BaseFinder):

    def find(self, path, all=False):
        pass

    def list(self, ignore_patterns):
        """Perform the compile action."""
        self.compile()
        return []

    def compile(self):
        subprocess.call('make')
