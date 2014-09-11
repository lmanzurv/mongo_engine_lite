import sys,os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from unittest import TestCase
from mongoenginelite import connect
from models import TestDocument, EmbeddedTestDocument, ReferenceTestDocument
import unittest

class ConnectTest(TestCase):
    def test_connect(self):
        connect('test_db')

class DocumentTest(TestCase):
    def test_save(self):
        td = TestDocument()
        td.name = 'Test doc'
        td.description = 'This is a test description for the save function'
        
        ref = ReferenceTestDocument()
        ref.name = 'Reference test name'
        ref.save()

        td.embed = EmbeddedTestDocument(email='test@test.com')
        td.embed.ref = ref

        td.save()

        self.assertTrue('id' in td._data)
        self.assertTrue(td.embed._data is not None)
        self.assertTrue('id' in td.embed.ref._data)

    def test_get(self):
        res = TestDocument.objects(name='Test doc', pk='5410d82348ad1c18605e60ff')
        _id = str(res[0].pk)

        self.assertTrue(len(res) == 1)
        self.assertEquals('5410d82348ad1c18605e60ff', _id)
        
    def test_update(self):
        td = TestDocument.objects(name='Test doc', pk='5410b90d48ad1c1101ee131c')
        td.update(set__name='Test name change')

        upd = TestDocument.objects(pk='5410b90d48ad1c1101ee131c')
        
        self.assertEquals('Test name change', upd[0].name)

    def test_delete(self):
        td = TestDocument.objects(pk='5410ea3b48ad1c1e9451861f')
        td.delete()

if __name__ == '__main__':
    unittest.main()