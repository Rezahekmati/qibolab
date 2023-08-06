.. title::
   Qibolab


What is Qibolab?
================

.. image:: https://zenodo.org/badge/DOI/10.5281/zenodo.7973899.svg
   :target: https://doi.org/10.5281/zenodo.7973899

Qibolab is the dedicated `Qibo <https://github.com/qiboteam/qibo>`_ backend for
quantum hardware control. This module automates the implementation of quantum
circuits on quantum hardware. Qibolab includes:

1. *Platform API*: support custom allocation of quantum hardware platforms / lab setup.
2. *Drivers*: supports commercial and open-source firmware for hardware control.
3. *Arbitrary pulse API*: provide a library of custom pulses for execution through instruments.
4. *Transpiler*: compiles quantum circuits into pulse sequences matching chip topology.
5. *Quantum Circuit Deployment*: seamlessly deploys quantum circuit models on
   quantum hardware.

Components
----------

.. image:: platform_object.svg

Key features
------------

* Deploy Qibo models on quantum hardware easily.
* Create custom experimental drivers for custom lab setup.
* Support multiple heterogeneous platforms.
* Use existing calibration procedures for experimentalists.

How to Use the Documentation
============================

Welcome to the comprehensive documentation for ``Qibolab``! This guide will help you navigate through the various sections and make the most of the resources available.

1. **Installation and Setup**: Begin by referring to the :doc:`/getting-started/installation` guide to set up the ``Qibolab`` library in your environment. A complete example is also provided in :doc:`/getting-started/experiment`.

2. **Tutorials**: Explore the :doc:`/tutorials/index` section for a range of tutorials that cater to different levels of expertise. These tutorials cover basic examples, real experiments, and guides for extending the library with new instruments.

3. **Main Documentation**: Dive into the :doc:`/main-documentation/qibolab` section, which offers a detailed overview of the main components that constitute the ``Qibolab`` framework. This section provides a comprehensive understanding of the key elements, helping you build a holistic view of the API's capabilities.

4. **API Reference**: For an in-depth exploration, visit the :doc:`/api-reference/qibolab` section. Here, you'll find automatically compiled documentation generated from present docstrings. This reference offers comprehensive insights into the various classes, methods, and attributes available within the library.

Contents
========

.. toctree::
    :maxdepth: 2
    :caption: Introduction

    getting-started/index
    tutorials/index

.. toctree::
    :maxdepth: 2
    :caption: Main documentation

    main-documentation/index
    api-reference/modules
    Developer guides <https://qibo.science/qibo/stable/developer-guides/index.html>

.. toctree::
    :maxdepth: 2
    :caption: Appendix

    Publications <https://qibo.science/qibo/stable/appendix/citing-qibo.html>

.. toctree::
    :maxdepth: 1
    :caption: Documentation links

    Qibo docs <https://qibo.science/qibo/stable/>
    Qibolab docs <https://qibo.science/qibolab/stable/>
    Qibocal docs <https://qibo.science/qibocal/stable/>
    Qibosoq docs <https://qibo.science/qibosoq/stable/>


Indices and tables
==================

* :ref:`genindex`
* :ref:`search`
