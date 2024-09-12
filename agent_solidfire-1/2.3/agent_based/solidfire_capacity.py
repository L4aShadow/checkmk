#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# (c) Andreas Doehler <andreas.doehler@bechtle.com/andreas.doehler@gmail.com>

# License: GNU General Public License v2
#
# Example Output
#
# <<<slfr_cluster_sessions>>>
# sessions 413

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

def check_mystuff(section):
    if debug.enabled():
        pprint(section)

def parse_solidfire_capacity(string_table):
    print("#### PARSE ######")
    print(string_table)
    parsed = {}
    for line in string_table:
        parsed[line[0]] = line[1]
    return parsed

agent_section_solidfire_capacity = AgentSection(
    name="solidfire_capacity",
    parse_function=parse_solidfire_capacity
)

def discovery_solidfire_capacity(section: Section) -> DiscoveryResult:
    print("DISCOVERY")
    print(section)
    #if debug.enabled():
    #for key in section.keys():
    #    yield Service(item=key)
    yield Service(item="Capacity")
    #yield Service()


def check_solidfire_capacity(item: str, params: Mapping[str, Any], section: Section) -> CheckResult:
    #pprint("#### CHECK ######")
    #pprint(section)
    capacity = section[0][1]
    #pprint(sessions)
    yield Result(state=State.OK, summary=f"Current Capacity: {capacity}")

check_plugin_solidfire_capacity = CheckPlugin(
    name="solidfire_capacity",
    service_name="SLFR-CAPACITY-%s",
    check_ruleset_name="solidfire",
    check_default_parameters={},
    sections=["slfr_cluster_capacity"],
    discovery_function=discovery_solidfire_capacity,
    check_function=check_solidfire_capacity,
)
