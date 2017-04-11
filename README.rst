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


OpenRefine_ is a great tool for exploring and cleaning datasets prior
to analysing them. It also records an undo history of all actions that
you can export as a sort of script in JSON_ format. However, in order
to execute that script on a new dataset, you need to manually import
it through the graphical interface or set up a BatchRefine_ server,
neither of which is quick.

PyRefine allows you to execute OpenRefine JSON scripts against
datasets without firing up a full Java/OpenRefine server. It has a
commandline tool for quick use, or you can use it as a library to
integrate it into your pandas_-based data analysis pipeline.

More details in `this blog post`_.

**Please note:** PyRefine is still very much alpha-quality. It probably
doesn't work exactly how you're expecting right now. That said, please
try it out, and consider :doc:`contributing`!

.. _OpenRefine: http://openrefine.org
.. _JSON: http://en.wikipedia.org/wiki/JSON
.. _BatchRefine: https://github.com/fusepoolP3/p3-batchrefine
.. _pandas: http://pandas.pydata.org/
.. _`this blog post`: https://erambler.co.uk/blog/introducing-pyrefine-openrefine-python/

* Free software: MIT license
* Documentation: https://pyrefine.readthedocs.io.


Features
--------

* Execute OpenRefine JSON against a dataset from the command line
* Execute OpenRefine JSON from a Python script

Credits
---------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage
