from unittest import TestCase

from webpub_manifest_parser.core.parsers import StringParser
from webpub_manifest_parser.core.properties import PropertiesGrouping, Property


class PropertiesGroupingTest(PropertiesGrouping):
    type = Property(key="@type", required=True, parser=StringParser())


class TestPropertiesGroupingTest(TestCase):
    def test_get_class_properties_returns_correct_result(self):
        # Act
        class_properties = PropertiesGrouping.get_class_properties(
            PropertiesGroupingTest
        )

        # Assert
        self.assertEqual(1, len(class_properties))

        [class_property] = class_properties
        class_property_name, class_property = class_property
        self.assertEqual("type", class_property_name)
        self.assertEqual("@type", class_property.key)
        self.assertEqual(True, class_property.required)
        self.assertIsInstance(class_property.parser, StringParser)
