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

    def test_get(self):
        obj = TestDocument.objects(name='Test doc', pk='5410d82348ad1c18605e60ff')
        print 'Get result: ',obj
        
    def test_update(self):
        td = TestDocument.objects(name='Test doc', pk='5410b90d48ad1c1101ee131c')
        td.update(set__name='Test name change')

    def test_delete(self):
        td = TestDocument.objects(pk='5410ea3b48ad1c1e9451861f')
        td.delete()

if __name__ == '__main__':
    unittest.main()