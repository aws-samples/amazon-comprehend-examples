# Amazon Comprehend Events Tutorial

This repo contains a Jupyter notebook, a helper script, and a sample data set designed to help users make the most of [Comprehend Events](http://). Currently, it contains the following artifacts:

* [comprehend_events_finance_tutorial.ipynb](./notebooks/comprehend_events_finance_tutorial.ipynb). This Jupyter notebook contains functions necessary to transform Comprehend Events service output for various analytic tasks, including highlighting of events and entities in text, tabulation of event structure, and graphing of event structure.
* [events_graph.py](./notebooks/events_graph.py). A helper module for converting Events output to a graph with `networkx` and `pyvis`.
* [sample_finance_dataset.txt](./data/sample_finance_dataset.txt). A set of 117 Amazon press releases in doclines format.

For further information, please see our launch blog post, "[Announcing the launch of Amazon Comprehend Events](http://)".


==============================================

Copyright 2020 Amazon.com, Inc. or its affiliates. All Rights Reserved.

SPDX-License-Identifier: MIT-0
