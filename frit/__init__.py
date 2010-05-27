#!/usr/bin/python

class Evidence(object):
    """
    This is the basic class for evidence files.
    It have to be overriden for different format of evidence files:
    dd,aff,e0 ...
    """
    def __init__(self, name=None):
        self.name = name

    def mount(self):
        """
        A function to mount the evidence.
        If not needed, just leave it empty.
        """
        pass

class DdEvidence(Evidence):
    pass

class AffEvidence(Evidence):
    pass

class EwfEvidence(Evidence):
    pass
