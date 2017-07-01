"""
"""

from itertools import chain


class ExpressionError(RuntimeError):
    pass


def compile_expression(expression):
    try:
        language, code = expression.split(':', 1)
    except ValueError as error:
        raise ExpressionError(f'No language given in expression: {expression}',
                              error)

    if language != 'jython':
        raise ExpressionError(f'Unknown expression language: {language}')

    func_code = '\n'.join(chain(['def expression_func(value):'],
                                ('    ' + line for line in code.splitlines())))
    context = {}
    eval(compile(func_code, 'pyrefine_exp', 'exec'), None, context)
    return context['expression_func']
