import ray
import pytest


@pytest.fixture(scope="session", autouse=True)
def ray_session():
    ray.init(ignore_reinit_error=True)
    yield
    ray.shutdown()
