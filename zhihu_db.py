import mongoengine

mongoengine.connect('zhihu_data')

class Zhihu_User_Profile(mongoengine.Document):
    user_name = mongoengine.StringField()
    user_gender = mongoengine.StringField()
    user_location = mongoengine.StringField()
    user_education_school = mongoengine.StringField()
    user_education_subject = mongoengine.StringField()
    user_employment = mongoengine.StringField()
    user_employment_extra = mongoengine.StringField()
    user_following_num = mongoengine.StringField()
    user_follower_num = mongoengine.StringField()
    user_be_agreed_num = mongoengine.StringField()
    user_be_thanked_num = mongoengine.StringField()
    user_info = mongoengine.StringField()
    user_introduction = mongoengine.StringField()
