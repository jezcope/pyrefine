"""Handle the expressions found in OpenRefine operations.

Currently, only Jython is supported inasmuch as it is passed directly
to the current Python interpreter.

.. autosummary::

    compile_expression
    ExpressionError
"""

from itertools import chain


class ExpressionError(RuntimeError):
    """Raised when an error occurs parsing an expression."""

    pass


def _indent_lines(lines, size=4):
    """Indent each line given by size spaces."""
    return ((' ' * size) + line for line in lines)


_ERROR_HANDLERS = {
    'set-to-blank': '    return None',
    'store-error': '    return e',
    'keep-original': '    return value',
}


def _handle_errors(lines, on_error):
    """Wrap the given source lines in an error-handling block."""
    yield 'try:'
    yield from _indent_lines(lines)
    yield 'except Exception as e:'
    yield _ERROR_HANDLERS[on_error]


def compile_expression(expression, on_error='set-to-blank'):
    """Compile the given expression into a callable function."""
    try:
        language, code = expression.split(':', 1)
    except ValueError as error:
        raise ExpressionError(f'No language given in expression: {expression}',
                              error)

    if language != 'jython':
        raise ExpressionError(f'Unknown expression language: {language}')

    func_body = _handle_errors(
                      code.splitlines(),
                      on_error)
    func_code = '\n'.join(chain(['def expression_func(value):'],
                                _indent_lines(func_body)))
    context = {}
    eval(compile(func_code, 'pyrefine_exp', 'exec'), None, context)
    return context['expression_func']
