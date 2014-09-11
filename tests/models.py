from mongoengine import *

class ReferenceTestDocument(Document):
    name = StringField(required=True)

class EmbeddedTestDocument(EmbeddedDocument):
    email = EmailField(required=True)
    ref = ReferenceField(ReferenceTestDocument)

class TestDocument(Document):
    name = StringField(required=True)
    description = StringField(required=True)
    embed = EmbeddedDocumentField(EmbeddedTestDocument)