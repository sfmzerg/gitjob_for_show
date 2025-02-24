import pytest

from dotenv import dotenv_values
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from dirty_equals import IsDict
import testing.postgresql

from app import API_TOKEN
from app.main import app
from app.db import get_db
from app.models.base import Base
from app.models.github import GithubProfile
from app.models.members import CompanySubscription, HrMember


TEST_ECHO = dotenv_values(".env").get("TEST_ECHO") == "1"


@pytest.fixture(scope="session")
def test_db():
    # create a test instance of the database
    postgresql = testing.postgresql.Postgresql(name="gitjob_test_db", port=7654)

    # Get the url to connect to with psycopg2 or equivalent
    test_db_url = postgresql.url()

    engine = create_engine(test_db_url, echo=TEST_ECHO)
    print(f"successfully connected to test database as {test_db_url}")

    Base.metadata.create_all(bind=engine)

    try:
        yield engine
    finally:
        postgresql.stop()


@pytest.fixture(scope="session")
def basic_session(test_db):
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_db)

    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session")
def test_session(basic_session):
    default_objs = [CompanySubscription(type="free"), CompanySubscription(type="paid")]

    for o in default_objs:
        basic_session.add(o)

    basic_session.commit()

    for o in default_objs:
        basic_session.refresh(o)

    yield basic_session


@pytest.fixture(scope="session")
def test_fastapi_app(test_session):
    # lambda is necessary, otherwise the fixture fires immediately and error is received
    app.dependency_overrides[get_db] = lambda: test_session
    return app


@pytest.fixture(scope="session")
def test_app(test_fastapi_app):
    """
    Stub for the old tests dependent on it
    todo: delete when migrated
    """
    client = TestClient(test_fastapi_app)
    return client


@pytest.fixture(scope="session")
def test_client(test_fastapi_app):
    client = TestClient(test_fastapi_app)
    return client


@pytest.fixture(scope="session")
def api_auth():
    """
    Return authorization token for API requests
    """
    return {
        "Authorization": "Bearer " + str(API_TOKEN),
    }


@pytest.fixture(scope="session")
def hr_auth():
    # replicate api auth for now, until proper
    # user auth is implemented
    return {
        "Authorization": "Bearer " + str(API_TOKEN),
    }


@pytest.fixture(scope="function")
def make_github_profile(test_session):
    """
    Create github profile in database
    """
    profiles = []

    def _make_github_profile(id, username, **kwargs):
        profile = GithubProfile(
            github_id=id,
            github_username=username,
            public_repos=None,
            followers=None,
            stars=None,
            profile_updated_at=None,
            hireable=False,
        )

        for k, v in kwargs.items():
            setattr(profile, k, v)

        test_session.add(profile)
        test_session.commit()
        test_session.refresh(profile)

        profiles.append(profile)

        return profile

    yield _make_github_profile

    for p in profiles:
        # delete related objects
        for c in p.historic_contacts:
            test_session.delete(c)
        for page in p.historic_pages:
            test_session.delete(page)

        # delete the profile
        test_session.delete(p)
    test_session.commit()


from pprint import pprint


class IsObject(IsDict):
    def equals(self, other) -> bool:
        other = other.__dict__

        expected = self.expected_values
        if self.partial:
            other = {k: v for k, v in other.items() if k in expected}

        if self.ignore:
            expected = self._filter_dict(self.expected_values)
            other = self._filter_dict(other)

        if other != expected:
            return False

        if self.strict and list(other.keys()) != list(expected.keys()):
            return False

        return True
