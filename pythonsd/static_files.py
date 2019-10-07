from django.contrib.staticfiles.finders import BaseFinder

import tasks


class CompileFinder(BaseFinder):

    def find(self, path, all=False):
        return []

    def list(self, ignore_patterns):
        """Perform the compile action."""
        self.compile()
        return []

    def compile(self):
        tasks.build()
