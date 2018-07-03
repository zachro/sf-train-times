class UserController:
    def __init__(self, user_dao):
        self.user_dao = user_dao

    def get_user(self, user_id):
        return self.user_dao.get_user(user_id)

    def add_user(self, user):
        return self.user_dao.add_user(user)

    def update_user(self, user_id, **kwargs):
        return self.user_dao.update_user(user_id, **kwargs)
