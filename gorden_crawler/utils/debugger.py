'''
Created on Oct 16, 2015

@author: scorpion
'''

from gorden_crawler.settings import PDB_TRACE

def trace():
    if PDB_TRACE:
        import pdb;pdb.set_trace()