import pytest
from .factories import CustomUserFactory

@pytest.mark.django_db
def test_new_user():
    user = CustomUserFactory()
    # print(user_factory.username)
    assert user.name == "Daniel"
