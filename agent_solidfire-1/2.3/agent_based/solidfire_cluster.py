#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# (c) Christoph Keßler <Christoph.Kessler@prosiebensat1.com/christoph.kessler@posteo.de>

# License: GNU General Public License v2
#
# Example Output
#
# <<<slfr_cluster>>>
# totalOps 639507702952
# clusterRecentIOSize 24644
# currentIOPS 1351
# zeroBlocks 48929752631
# nonZeroBlocks 25812235721
# uniqueBlocks 20139176926
# uniqueBlocksUsedSpace 47985797330485
# timestamp 2024-08-16T05:55:00Z

import time
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
    check_levels,
    get_rate,
    get_value_store,
    GetRateError
)

Section = Dict[str, int]

def parse_solidfire_cluster(string_table):
    #if debug.enabled():
    #    pprint("##### PARSING ######")
    #    pprint(string_table)
    parsed = {}
    for line in string_table:
        parsed[line[0]] = line[1]

    #if debug.enabled():
    #    pprint(parsed)

    return parsed
    
agent_section_solidfire_cluster = AgentSection(
    name="slfr_cluster",
    parse_function=parse_solidfire_cluster
)

def discovery_solidfire_cluster(section: Section) -> DiscoveryResult:
    #if debug.enabled():
    #    print("DISCOVERY")
    #    print(section)
    yield Service(item="Cluster")

def check_solidfire_cluster(item: str, params: Mapping[str, Any], section: Section) -> CheckResult:
    #if debug.enabled():
    #    pprint("#### CHECK ######")
    #    pprint(section)

    store = get_value_store() 
    #print ("Store: ", store)
    now = time.time()

    try:
        currentIOPSDelta = get_rate(store, "Total_Ops", now, int(section['currentIOPS']))
    except GetRateError as e:
        raise e

    # Calculate the factors
    # https://docs.netapp.com/us-en/element-software/api/reference_element_api_getclustercapacity.html
    thinProvisioningFactor = ( int(section['nonZeroBlocks']) + int(section['zeroBlocks'])) / int(section['nonZeroBlocks'])
    deDuplicationFactor = int(section['nonZeroBlocks'])/ int(section['uniqueBlocks'])
    compressionFactor = (int(section['uniqueBlocks']) * 4096) / (int(section['uniqueBlocksUsedSpace']) * 0.93)
    efficiencyFactor = thinProvisioningFactor * deDuplicationFactor * compressionFactor

    yield Result(
        state = State.OK,
        summary = f"Total Ops: {currentIOPSDelta:.2f}, Efficiency: {efficiencyFactor:.2f}, ThinProv: {thinProvisioningFactor:.2f}, DeDup: {deDuplicationFactor:.2f}, Compress: {compressionFactor:.2f}"
    )

    yield Metric(name="Thin_Provisioning_Factor", value=thinProvisioningFactor)
    yield Metric(name="DeDuplication_Factor", value=deDuplicationFactor)
    yield Metric(name="Compression_Factor", value=compressionFactor)
    yield Metric(name="Efficiency_Factor", value=efficiencyFactor)
    yield Metric(name="Total_Ops", value=currentIOPSDelta)

check_plugin_solidfire_cluster = CheckPlugin(
    name="solidfire_cluster",
    service_name="SLFR-%s",
    check_ruleset_name="solidfire",
    check_default_parameters={},
    sections=["slfr_cluster"],
    discovery_function=discovery_solidfire_cluster,
    check_function=check_solidfire_cluster,
)
