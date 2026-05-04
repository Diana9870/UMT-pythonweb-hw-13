import pytest
from unittest.mock import MagicMock
from datetime import date, timedelta

from app.repository.contacts import ContactsRepository
from app.database import Contact, User


@pytest.fixture
def mock_db():
    return MagicMock()


@pytest.fixture
def repo(mock_db):
    return ContactsRepository(mock_db)


@pytest.fixture
def user():
    return User(id=1, email="test@test.com")


@pytest.fixture
def contact():
    return Contact(
        id=1,
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        phone="123456789",
        birthday=date(1990, 1, 1),
        user_id=1,
    )



def test_create_contact(repo, mock_db, user):
    body = MagicMock()
    body.first_name = "John"
    body.last_name = "Doe"
    body.email = "john@example.com"
    body.phone = "123456789"
    body.birthday = date(1990, 1, 1)

    mock_db.add = MagicMock()
    mock_db.commit = MagicMock()
    mock_db.refresh = MagicMock()

    result = repo.create_contact(body, user)

    assert result.first_name == "John"
    assert result.user_id == user.id
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()



def test_get_contacts(repo, mock_db, user):
    contacts = [MagicMock(), MagicMock()]

    mock_db.query().filter().offset().limit().all.return_value = contacts

    result = repo.get_contacts(skip=0, limit=10, user=user)

    assert result == contacts



def test_get_contact_by_id_found(repo, mock_db, user, contact):
    mock_db.query().filter().first.return_value = contact

    result = repo.get_contact_by_id(contact.id, user)

    assert result == contact


def test_get_contact_by_id_not_found(repo, mock_db, user):
    mock_db.query().filter().first.return_value = None

    result = repo.get_contact_by_id(999, user)

    assert result is None



def test_update_contact_found(repo, mock_db, user, contact):
    body = MagicMock()
    body.first_name = "Updated"
    body.last_name = "Doe"
    body.email = "updated@example.com"
    body.phone = "000000000"
    body.birthday = date(2000, 1, 1)

    mock_db.query().filter().first.return_value = contact
    mock_db.commit = MagicMock()
    mock_db.refresh = MagicMock()

    result = repo.update_contact(contact.id, body, user)

    assert result.first_name == "Updated"
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()


def test_update_contact_not_found(repo, mock_db, user):
    mock_db.query().filter().first.return_value = None

    result = repo.update_contact(999, MagicMock(), user)

    assert result is None



def test_delete_contact_found(repo, mock_db, user, contact):
    mock_db.query().filter().first.return_value = contact
    mock_db.delete = MagicMock()
    mock_db.commit = MagicMock()

    result = repo.delete_contact(contact.id, user)

    assert result == contact
    mock_db.delete.assert_called_once_with(contact)
    mock_db.commit.assert_called_once()


def test_delete_contact_not_found(repo, mock_db, user):
    mock_db.query().filter().first.return_value = None

    result = repo.delete_contact(999, user)

    assert result is None



def test_search_contacts(repo, mock_db, user):
    contacts = [MagicMock()]

    mock_db.query().filter().all.return_value = contacts

    result = repo.search_contacts("John", user)

    assert result == contacts


def test_get_upcoming_birthdays(repo, mock_db, user):
    contact = MagicMock()
    contact.birthday = date.today()

    mock_db.query().filter().all.return_value = [contact]

    result = repo.get_upcoming_birthdays(user)

    assert isinstance(result, list)