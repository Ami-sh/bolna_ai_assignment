import pytest
from service.feed_manager import RssAtomFeeds


def test_singleton_instance():
    """
    Ensure RssAtomFeeds follows singleton pattern.
    """
    manager1 = RssAtomFeeds()
    manager2 = RssAtomFeeds()

    assert manager1 is manager2