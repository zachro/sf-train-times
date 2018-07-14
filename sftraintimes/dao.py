import boto3
from os import environ


class UserDAO:
    """Contains methods for getting, adding, and updating users in the database."""
    USER_TABLE_NAME = 'User-' + environ.get('STAGE', 'dev')

    def __init__(self, table):
        """
        Constructs a new UserDAO instance.
        :param table: A boto3.resources.factory.dynamodb.Table instance representing the user table.
        """
        self.table = table

    def get_user(self, user_id):
        """
        Gets a user from the database.
        :param user_id: The ID of the user to retrieve.
        :return: A dict representing the user, or None if the user_id could not be found.
        """
        response = self.table.get_item(Key={'id': user_id})

        return response.get('Item')

    def add_user(self, user):
        """
        Adds a user to the database.
        :param user: A dict representing the user, containing at minimum an 'id' value.
        """
        self.table.put_item(Item=user)

    def update_user(self, user_id, **kwargs):
        """
        Updates a user in the database, or adds the user if it does not exist.
        :param user_id: The ID for the user to update.
        :param kwargs: Key-value pairs for each field to update in the database. If the field does not already exist, it
                       will be added.
        """
        if not kwargs:
            return

        update_expression = 'SET '
        expression_attribute_names = {}
        expression_attribute_values = {}

        for key, value in kwargs.items():
            key_placeholder = '#{}'.format(key)
            value_placeholder = ':{}'.format(value.replace(' ', ''))
            expression_attribute_names[key_placeholder] = key
            expression_attribute_values[value_placeholder] = value
            update_expression += '{} = {}, '.format(key_placeholder, value_placeholder)

        update_expression = update_expression[: -2]

        self.table.update_item(
            Key={'id': user_id},
            UpdateExpression=update_expression,
            ExpressionAttributeNames=expression_attribute_names,
            ExpressionAttributeValues=expression_attribute_values
        )
