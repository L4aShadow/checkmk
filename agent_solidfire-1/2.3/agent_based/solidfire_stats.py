#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# (c) Christoph Keßler <Christoph.Kessler@prosiebensat1.com/christoph.kessler@posteo.de>

# License: GNU General Public License v2
#
# Example Output
#
# <<<slfr_stats>>>
# clientQueueDepth 1
# latencyUSec 47
# readLatencyUSec 5
# writeLatencyUSec 41
# unalignedReads 28980
# unalignedWrites 1174956
# readBytes 10528856780379648
# writeBytes 16507296572481536

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
    render,
    get_rate,
    get_value_store,
    GetRateError
)

Section = Dict[str, int]

def parse_solidfire_stats(string_table):
    #if debug.enabled():
    #    pprint("##### PARSING ######")
    #    pprint(string_table)
    parsed = {}
    for line in string_table:
        parsed[line[0]] = line[1]

    #if debug.enabled():
    #    pprint(parsed)

    return parsed
    
agent_section_solidfire_stats = AgentSection(
    name="slfr_stats",
    parse_function=parse_solidfire_stats
)

def discovery_solidfire_stats(section: Section) -> DiscoveryResult:
    yield Service(item="Stats")

def check_solidfire_stats(item: str, params: Mapping[str, Any], section: Section) -> CheckResult:
    if debug.enabled():
        pprint("#### CHECK ######")
        pprint(section)

    store = get_value_store() 
    #print ("Store: ", store)
    now = time.time()

    try:
        currentReadDelta = get_rate(store, "readBytes", now, int(section['readBytes']))
        currentWriteDelta = get_rate(store, "writeBytes", now, int(section['writeBytes']))
    except GetRateError as e:
        raise e

    currentReadDeltaPretty = render.bytes(currentReadDelta)
    currentReadDeltaPretty = render.bytes(currentWriteDelta)

    yield Result(
        state = State.OK,
        summary = f"Latency: {int(section['latencyUSec'])} ms, clientQueue: {int(section['clientQueueDepth'])}, Reads: {currentReadDeltaPretty}, Writes: {currentReadDeltaPretty}",
        details = f"Read Latency: {int(section['readLatencyUSec'])} ms, Write Latency: {int(section['writeLatencyUSec'])} ms" 
    )

    # Convert the number into a ms for rendering
    LatencyMS = int(section['latencyUSec']) / 1000
    readLatencyMS = int(section['readLatencyUSec']) / 1000
    writeLatencyMS = int(section['writeLatencyUSec']) / 1000

    yield Metric(name="Latency_Cluster", value=LatencyMS)
    yield Metric(name="Latency_Read", value=readLatencyMS)
    yield Metric(name="Latency_Write", value=writeLatencyMS)
    yield Metric(name="Client_Queue_Depth", value=int(section['clientQueueDepth']))
    yield Metric(name="Bytes_Read", value=currentReadDelta)
    yield Metric(name="Bytes_Write", value=currentWriteDelta)

check_plugin_solidfire_stats = CheckPlugin(
    name="solidfire_stats",
    service_name="SLFR-%s",
    check_ruleset_name="solidfire",
    check_default_parameters={},
    sections=["slfr_stats"],
    discovery_function=discovery_solidfire_stats,
    check_function=check_solidfire_stats,
)
