class Token:

    """
    This class is used to handle any token requirements for ease of authentication.
    """

    def __init__(self, name, token):

        """
        The initial method that returns the basic information of the token.
        :param name: Name of person whose token it is.
        :param token: The inserted token at token_goes_here.
        :return: Information.
        """

        self.name = name
        self.__token = token

    def get_token(self):

        """
        This function returns user token only without the name.
        """

        return self.__token

    def set_token(self, token):

        """
        This function sets new tokens that will be used for the authentication.
        """

        self.__token = token

    def __str__(self):

        """
        In the case that the name of the person to whom the token belongs is needed, this function can be used to
        return that name.
        :return: Just the name with informative string.
        """

        return "name: " + self.name
