import pytest

from pytest_factoryboy import register
from .factories import CustomUserFactory

register(CustomUserFactory)