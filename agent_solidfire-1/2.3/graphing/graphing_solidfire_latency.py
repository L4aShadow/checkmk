#!/usr/bin/env python3
# Copyright (C) 2024 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from cmk.graphing.v1 import graphs, metrics, Title

UNIT_TIME = metrics.Unit(metrics.TimeNotation())

metric_solidfire_latency = metrics.Metric(
    name="Latency_Cluster",
    title=Title("Latency"),
    unit=UNIT_TIME,
    color=metrics.Color.PINK,
)

metric_solidfir_read_latency = metrics.Metric(
    name="Latency_Read",
    title=Title("Read latency"),
    unit=UNIT_TIME,
    color=metrics.Color.BLUE,
)
metric_solidfire_write_latency = metrics.Metric(
    name="Latency_Write",
    title=Title("Write latency"),
    unit=UNIT_TIME,
    color=metrics.Color.GREEN,
)
