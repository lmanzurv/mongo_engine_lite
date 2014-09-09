import sys,os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from unittest import TestCase
from mongoenginelite import connect
from models import TestDocument
import unittest

class ConnectTest(TestCase):
    def test_connect(self):
        connect('test_db')

class DocumentTest(TestCase):
    def test_save(self):
        td = TestDocument()
        td.name = 'Test doc'
        td.description = 'This is a test description for the save function'
        td.save()

if __name__ == '__main__':
    unittest.main()