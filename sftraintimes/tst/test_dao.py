from unittest import TestCase
from unittest.mock import Mock

from botocore.exceptions import ClientError

from sftraintimes.dao import UserDAO


class UserDAOTest(TestCase):
    USER_ID = 'userId'
    USER = {'id': 'userId'}
    USER_KEY = {'id': 'userId'}

    def setUp(self):
        self.mock_table = type('Table', (), {})
        self.user_dao = UserDAO(self.mock_table)
        ClientError.__init__ = Mock(return_value=None)

    def test_get_user(self):
        item = {'Item': self.USER}
        self.mock_table.get_item = Mock(return_value=item)

        result = self.user_dao.get_user(self.USER_ID)

        self.assertEqual(result, self.USER)
        self.mock_table.get_item.assert_called_with(Key=self.USER_KEY)

    def test_get_user__dynamodb_exception(self):
        mock_client_error = ClientError('foo', 'bar')
        self.mock_table.get_item = Mock(side_effect=mock_client_error)

        with self.assertRaises(ClientError):
            self.user_dao.get_user(self.USER_ID)
        self.mock_table.get_item.assert_called_with(Key=self.USER_KEY)

    def test_add_user(self):
        self.mock_table.put_item = Mock()

        self.user_dao.add_user(self.USER)

        self.mock_table.put_item.assert_called_with(Item=self.USER)

    def test_add_user__dynamodb_exception(self):
        mock_client_error = ClientError('foo', 'bar')
        self.mock_table.put_item = Mock(side_effect=mock_client_error)

        with self.assertRaises(ClientError):
            self.user_dao.add_user(self.USER)
        self.mock_table.put_item.assert_called_with(Item=self.USER)

    def test_update_user(self):
        kwargs = {'firstAttribute': 'firstValue', 'secondAttribute': 'secondValue'}
        expected_exp_attr_names = {'#firstAttribute': 'firstAttribute', '#secondAttribute': 'secondAttribute'}
        expected_exp_attr_values = {':firstValue': 'firstValue', ':secondValue': 'secondValue'}
        expected_update_expression = 'SET #firstAttribute = :firstValue, #secondAttribute = :secondValue'
        self.mock_table.update_item = Mock()

        self.user_dao.update_user(self.USER_ID, **kwargs)

        self.mock_table.update_item.assert_called_with(Key=self.USER_KEY,
                                                       UpdateExpression=expected_update_expression,
                                                       ExpressionAttributeNames=expected_exp_attr_names,
                                                       ExpressionAttributeValues=expected_exp_attr_values)

    def test_update_user__no_kwargs(self):
        self.mock_table.update_item = Mock()

        self.user_dao.update_user(self.USER_ID)

        self.mock_table.update_item.assert_not_called()

    def test_update_user__dynamodb_exception(self):
        kwargs = {'attribute': 'value'}
        mock_client_error = ClientError('foo', 'bar')
        self.mock_table.update_item = Mock(side_effect=mock_client_error)

        with self.assertRaises(ClientError):
            self.user_dao.update_user(self.USER_ID, **kwargs)
        self.mock_table.update_item.assert_called()
