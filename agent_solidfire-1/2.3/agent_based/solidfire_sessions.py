#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# (c) Christoph Keßler <Christoph.Kessler@prosiebensat1.com/christoph.kessler@posteo.de>

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

def parse_solidfire_sessions(string_table):
    parsed = {}
    for line in string_table:
        parsed[line[0]] = line[1]
    return parsed

agent_section_solidfire_sessions = AgentSection(
    name="solidfire_sessions",
    parse_function=parse_solidfire_sessions,
    parsed_section_name = "slfr_cluster_sessions" 
)

def discovery_solidfire_sessions(section: Section) -> DiscoveryResult:
    yield Service(item="Sessions")


def check_solidfire_sessions(item: str, params: Mapping[str, Any], section: Section) -> CheckResult:
    sessions = int(section[0][1])
    yield Result(state=State.OK, summary=f"Number of current iSCSI Sessions: {sessions:.0f}")
    yield Metric(name="solidfire_sessions", value=sessions)

check_plugin_solidfire_sessions = CheckPlugin(
    name="solidfire_sessions",
    service_name="SLFR-%s",
    check_ruleset_name="solidfire",
    check_default_parameters={},
    sections=["slfr_cluster_sessions"],
    discovery_function=discovery_solidfire_sessions,
    check_function=check_solidfire_sessions,
)
