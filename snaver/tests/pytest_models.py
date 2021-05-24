import pytest
from .factories import CustomUserFactory, BudgetFactory
from snaver.models import CustomUser


@pytest.mark.django_db
def test_if_user_added_correctly(create_test_user):
    user = create_test_user
    assert isinstance(user, CustomUser)


@pytest.mark.django_db
def test_if_budget_added_correctly(create_test_user):
    user = create_test_user
    budget = BudgetFactory(user=user)

    assert budget.user == user


def test_if_homepage_is_200(client):
    response = client.get('/')
    assert response.status_code == 200


@pytest.mark.django_db
def test_authenticated_user_can_see_their_budget(logged_in_user):
    client, user = logged_in_user
    assert b"Current month categories" in client.get("/").content


@pytest.mark.django_db
def test_not_authenticated_user_cannot_see_their_budget(client):
    assert b"This month's budget" not in client.get("/").content


# ARRANGE
@pytest.fixture
def create_test_user():
    user = CustomUserFactory()
    return user


@pytest.fixture
def logged_in_user(client, create_test_user, strong_password):
    test_user = create_test_user
    if test_user is not None:
        client.login(username=test_user.username, password=test_user.password)
        return client, test_user


@pytest.fixture
def strong_password():
    return "AdasKJj23!!!%sd"
