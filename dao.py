

CITY_NAME_INDEX = 'cityName-index'


class UserDAO:
    def __init__(self, table):
        self.table = table

    def get_user(self, user_id):
        response = self.table.get_item(Key={'id': user_id})

        return response['Item']

    def add_user(self, user):
        self.table.put_item(Item=user)

    def update_user(self, user_id, attribute, new_value):
        update_expression = 'SET #attribute = :value'
        expression_attribute_names = {'#attribute': attribute}
        expression_attribute_values = {':value': new_value}

        self.table.update_item(
            Key={'id': user_id},
            UpdateExpression=update_expression,
            ExpressionAttributeNames=expression_attribute_names,
            ExpressionAttributeValues=expression_attribute_values
        )
