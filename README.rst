===============================
PyRefine
===============================


.. image:: https://img.shields.io/pypi/v/pyrefine.svg
        :target: https://pypi.python.org/pypi/pyrefine

.. image:: https://img.shields.io/travis/jezcope/pyrefine.svg
        :target: https://travis-ci.org/jezcope/pyrefine

.. image:: https://readthedocs.org/projects/pyrefine/badge/?version=latest
        :target: https://pyrefine.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status

.. image:: https://pyup.io/repos/github/jezcope/pyrefine/shield.svg
     :target: https://pyup.io/repos/github/jezcope/pyrefine/
     :alt: Updates


Execute OpenRefine JSON scripts without OpenRefine (or Java).


* Free software: MIT license
* Documentation: https://pyrefine.readthedocs.io.


Features
--------

* TODO: Execute OpenRefine JSON against a dataset from the command line
* TODO: Convert OpenRefine JSON to equivalent Python code
* TODO: Implement standard OpenRefine operations

  * Cell

    * ``core/mass-edit`` ✓
    * ``core/blank-down``
    * ``core/fill-down``
    * ``core/key-value-columnize``
    * ``core/multi-valued-cell-join``
    * ``core/multi-valued-cell-split``
    * ``core/text-transform``
    * ``core/transpose-columns-into-rows``
    * ``core/transpose-rows-into-columns``

  * Column

    * ``core/column-addition-by-fetching-urls``
    * ``core/column-addition``
    * ``core/column-move``
    * ``core/column-removal`` ✓
    * ``core/column-rename`` ✓
    * ``core/column-reorder``
    * ``core/column-split``

  * Reconciliation

    * ``core/recon-clear-similar-cells``
    * ``core/recon-copy-across-columns``
    * ``core/recon-discard-judgments``
    * ``core/recon-judge-similar-cells``
    * ``core/recon-mark-new-topics``
    * ``core/recon-match-best-candidates``
    * ``core/recon-match-specific-topic``
    * ``core/recon``

  * Row

    * ``core/denormalize``
    * ``core/row-flag``
    * ``core/row-removal``
    * ``core/row-reorder``
    * ``core/row-star``

Credits
---------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage

