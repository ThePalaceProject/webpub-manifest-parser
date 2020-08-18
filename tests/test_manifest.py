"""Verify that our Readium Web Publication Manifest implements the spec.

https://github.com/readium/webpub-manifest
"""

from . import Test
from nose.tools import set_trace
from ..rwpm import Manifest

class EndToEndTest(Test):

    def test_spec_example(self):
        """Load the RWPM given as an example in the spec."""
        manifest = self.load_resource("rwpm/spec_example.json")
        Manifest.

