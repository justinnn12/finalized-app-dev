class Feedback:
    count_id = 0

    def __init__(self, name, email, feedback):
        Feedback.count_id += 1
        self.__feedback_id = Feedback.count_id
        self.__name = name
        self.__email = email
        self.__feedback = feedback

    def get_feedback_id(self):
        return self.__feedback_id

    def get_name(self):
        return self.__name

    def get_email(self):
        return self.__email

    def get_feedback(self):
        return self.__feedback

    def set_feedback_id(self):
        return self.__feedback_id

    def set_name(self):
        return self.__name

    def set_email(self):
        return self.__email

    def set_feedback(self):
        return self.__feedback
