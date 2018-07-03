CITY_NAME_INDEX = 'cityName-index'


class UserDAO:
    def __init__(self, table):
        self.table = table

    def get_user(self, user_id):
        response = self.table.get_item(Key={'id': user_id})

        return response.get('Item')

    def add_user(self, user):
        self.table.put_item(Item=user)

    def update_user(self, user_id, **kwargs):
        if kwargs is None:
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
