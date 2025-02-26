from django.test import TestCase
from .models import YourModel

class YourModelTests(TestCase):

    def setUp(self):
        # Create an instance of YourModel for testing
        self.model_instance = YourModel.objects.create(field1='value1', field2='value2')

    def test_model_creation(self):
        # Test that the model instance was created successfully
        self.assertEqual(self.model_instance.field1, 'value1')
        self.assertEqual(self.model_instance.field2, 'value2')

    def test_model_str(self):
        # Test the string representation of the model
        self.assertEqual(str(self.model_instance), 'Expected String Representation')