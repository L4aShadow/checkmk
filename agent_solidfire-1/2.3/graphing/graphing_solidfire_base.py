#!/usr/bin/env python3
# Copyright (C) 2024 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from cmk.graphing.v1 import graphs, metrics, Title

UNIT_PERCENT = metrics.Unit(metrics.DecimalNotation("%"))

metric_solidfire_latency = metrics.Metric(
    name="CPU_utilization",
    title=Title("CPU Utilization"),
    unit=UNIT_PERCENT,
    color=metrics.Color.PINK,
)
