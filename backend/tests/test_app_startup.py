from app.main import app


def test_app_created():
    assert app.title is not None


def test_health_route_registered():
    routes = [route.path for route in app.routes]
    assert "/health" in routes
