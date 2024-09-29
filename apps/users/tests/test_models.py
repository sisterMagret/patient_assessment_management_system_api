import pytest
from datetime import date
from django.contrib.auth.models import Group
from ..models import User, Address, UserType, GenderType


@pytest.fixture
def address():
    """Fixture to create an Address object."""
    return Address.objects.create(
        country="USA",
        state="California",
        city="Los Angeles",
        zip_code="90001",
        address="123 Test Ave",
    )


@pytest.fixture
def user(address):
    """Fixture to create a User object."""
    return User.objects.create(
        username="testuser",
        phone_number="1234567890",
        email="testuser@example.com",
        address=address,
        gender=GenderType.MALE,
        date_of_birth=date(1990, 1, 1),
        is_verified=True,
        first_name="John",
        last_name="Doe",
        user_role=UserType.USER,
    )


@pytest.mark.django_db
def test_user_creation(user):
    """Test user creation and field values."""
    assert user.username == "testuser"
    assert user.phone_number == "1234567890"
    assert user.email == "testuser@example.com"
    assert user.address.city == "Los Angeles"
    assert user.gender == GenderType.MALE
    assert user.is_verified is True


@pytest.mark.django_db
def test_user_str(user):
    """Test the __str__ method of the User model."""
    assert str(user) == f"1234567890 John Doe {user.id} user"


@pytest.mark.django_db
def test_user_group(user):
    """Test the group method for a user with no groups."""
    assert user.group() == "user"


@pytest.mark.django_db
def test_user_group_with_group(user):
    """Test the group method for a user belonging to a group."""
    group = Group.objects.create(name="Admin")
    user.groups.add(group)
    assert user.group() == "Admin"


@pytest.mark.django_db
def test_user_age(user):
    """Test the age property."""
    expected_age = date.today().year - 1990
    if date.today() < date(
        date.today().year, 1, 1
    ):  # Adjust if today is before the birthday
        expected_age -= 1
    assert user.age == expected_age


@pytest.mark.django_db
def test_phone_number_uniqueness(user, address):
    """Test the uniqueness constraint on phone_number."""
    with pytest.raises(Exception):
        User.objects.create(
            username="anotheruser",
            phone_number="1234567890",  # Duplicate phone number
            email="another@example.com",
            address=address,
        )
