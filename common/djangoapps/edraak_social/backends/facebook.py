from social.backends.facebook import FacebookOAuth2


class EdraakFacebookOAuth2(FacebookOAuth2):
    REDIRECT_STATE = False

