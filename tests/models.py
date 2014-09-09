from mongoengine import *

class TestDocument(Document):
    name = StringField(required=True)
    description = StringField(required=True)

class OtherTestDocument(Document):
    email = EmailField(required=True)