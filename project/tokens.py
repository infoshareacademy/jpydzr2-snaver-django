import six
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import PasswordResetTokenGenerator

User = get_user_model()

class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, User, timestamp):
        return (
            six.text_type(User.pk) + six.text_type(timestamp) +
            six.text_type(User.email_confirmed)
        )

account_activation_token = AccountActivationTokenGenerator()