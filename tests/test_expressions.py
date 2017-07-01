# flake8: noqa

import pytest
from collections.abc import Callable

from pyrefine.expressions import compile_expression, ExpressionError


def test_raises_error_for_unknown_language():
    with pytest.raises(ExpressionError):
        compile_expression('unknown:return value')


def test_raises_error_when_no_language_found():
    with pytest.raises(ExpressionError):
        compile_expression('return value')
        
        
class TestPythonExpression:

    def test_compiled_expression_is_callable(self):
        func = compile_expression('jython:return value')

        assert isinstance(func, Callable)

    @pytest.mark.parametrize('value,expression,expected', [
        (42, 'jython:return value', 42),
        (4, 'jython:return value*3', 12),
        ('2017-06-09',
         'jython:'
         'import re\n'
         'result = re.match(r"\d{4}", value)\n'
         'return result[0]',
         '2017'),
    ])
    def test_executes_correctly(self, value, expression, expected):
        function = compile_expression(expression)

        result = function(value)

        assert result == expected

    def test_raises_syntax_error_for_invalid_code(self):
        with pytest.raises(SyntaxError):
            compile_expression('jython:value +')
