#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# (c) Christoph Keßler <Christoph.Kessler@prosiebensat1.com/christoph.kessler@posteo.de>

# License: GNU General Public License v2
#
# Example Output
#
# <<<slfr_iops>>>
# currentIOPS 2023
# averageIOPS 1556
# maxIOPS 600000
# peakIOPS 6387

from collections.abc import Mapping, Sequence
from typing import Any, Dict
from pprint import pprint
from cmk.utils import debug
from cmk.agent_based.v2 import (
    AgentSection,
    CheckPlugin,
    CheckResult,
    DiscoveryResult,
    Service,
    Result,
    State,
    Metric,
    check_levels
)

Section = Dict[str, int]

def parse_solidfire_iops(string_table):
    if debug.enabled():
        pprint("##### PARSING ######")
        pprint(string_table)
    parsed = {}
    for line in string_table:
        parsed[line[0]] = line[1]

    if debug.enabled():
        pprint(parsed)

    return parsed
    
agent_section_solidfire_iops = AgentSection(
    name="slfr_iops",
    parse_function=parse_solidfire_iops
)

def discovery_solidfire_iops(section: Section) -> DiscoveryResult:
    if debug.enabled():
        print("DISCOVERY")
        print(section)
    yield Service(item="IOPS")

def check_solidfire_iops(item: str, params: Mapping[str, Any], section: Section) -> CheckResult:
    if debug.enabled():
        pprint("#### CHECK ######")
        pprint(section)

    yield Result(
        state = State.OK,
        summary = f"Current IOPS: {int(section['currentIOPS'])}, AverageIOPS: {int(section['averageIOPS'])}, Peak IOPS: {int(section['peakIOPS'])}"
    )

    yield Metric(name="Current_IOPS", value=int(section['currentIOPS']))
    yield Metric(name="Average_IOPS", value=int(section['averageIOPS']))
    yield Metric(name="Peak_IOPS", value=int(section['peakIOPS']))

check_plugin_solidfire_iops = CheckPlugin(
    name="solidfire_iops",
    service_name="SLFR-%s",
    check_ruleset_name="solidfire",
    check_default_parameters={},
    sections=["slfr_iops"],
    discovery_function=discovery_solidfire_iops,
    check_function=check_solidfire_iops,
)
