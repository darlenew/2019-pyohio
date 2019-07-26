import pytest


@pytest.mark.performance
def test_foo():
    """This is the foo test"""
    assert False

@pytest.mark.high
def test_bar():
    """The bar test"""
    assert True

def test_baz():
    """The baz test
    Make sure we get multiline formatting right.
    """
    assert True

class TestFoo():

    @pytest.mark.high
    @pytest.mark.performance
    def test_a(self):
        """The TestFoo.a test.
        Make it a multiline docstring.
        """
        assert False

    def test_b(self):
        """The TestFoo.b test"""
        assert True
