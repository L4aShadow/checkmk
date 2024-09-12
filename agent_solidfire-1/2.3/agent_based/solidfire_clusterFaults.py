#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# (c) Christoph Keßler <Christoph.Kessler@prosiebensat1.com/christoph.kessler@posteo.de>

# License: GNU General Public License v2
#
# Example Output
#
# <<<slfr_cluster_members>>>
# ensembleMembers 172.22.41.74, 172.22.41.75, 172.22.41.76, 172.22.41.78, 172.22.41.79

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

#def parse_solidfire_clusterFaults(string_table):
#    print("#### PARSE ######")
#    print(string_table)
#    parsed = {}
#    for line in string_table:
#        parsed[line[0]] = line[1]
#    return parsed

#agent_section_solidfire_clusterFaults = AgentSection(
#    name="solidfire_clusterFaults",
#    parse_function=parse_solidfire_clusterFaults
#)

def discovery_solidfire_clusterFaults(section: Section) -> DiscoveryResult:
    yield Service(item="Faults")


def check_solidfire_clusterFaults(item: str, params: Mapping[str, Any], section: Section) -> CheckResult:
    if debug.enabled():
        pprint("#### CHECK ######")
        pprint(section)
    members = section[0][1]
    yield Result(state=State.OK, summary=f"Faults: {members}")

check_plugin_solidfire_clusterFaults = CheckPlugin(
    name="solidfire_clusterFaults",
    service_name="SLFR-%s",
    check_ruleset_name="solidfire",
    check_default_parameters={},
    sections=["slfr_cluster_faults"],
    discovery_function=discovery_solidfire_clusterFaults,
    check_function=check_solidfire_clusterFaults,
)
