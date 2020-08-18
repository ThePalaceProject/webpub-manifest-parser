import os
from unittest import TestCase

class Test(TestCase):

    def load_resource(self, path):
        base_path = os.path.split(__file__)[0]
        path = os.path.join(base_path, "files", path)
        return open(path, 'rb').read()
