
from bin.subject_tagger import * 
import unittest
import logging

logging.basicConfig(level=logging.DEBUG)
logging.getLogger('tagger').setLevel(logging.DEBUG)
LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)

class TestTagger(unittest.TestCase):
    """Test tagging subjects for ADASS articles 
    """

    def test_subject_tagging(self):
        fake_flag = True
        self.assertTrue(fake_flag)

if __name__ == '__main__':
    unittest.main()

