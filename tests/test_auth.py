from os import environ
from pytest import fixture

from paypyl import Client


@fixture
def client_id():
    return environ.get("PAYPAL_CLIENT_ID", "test_client_id")


@fixture
def client_secret():
    return environ.get("PAYPAL_CLIENT_SECRET", "test_client_secret")


@fixture
def client():
    return Client(sandbox=True)
