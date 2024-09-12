#!/usr/bin/env python3
# -*- encoding: utf-8; py-indent-offset: 4 -*-

# (c) Christoph Keßler <Christoph.Kessler@prosiebensat1.com/christoph.kessler@posteo.de>

# License: GNU General Public License v2
#
# Example Output
#
# <<<slfr_cluster_nodes:sep(59)>>>
# ifs-sfire1-p8-12;15,55384830344370,53569840524774,55384830344370,53569840524774,55384830344370,53569840524774
# ifs-sfire1-p9-14;6,39827603990324,41347096750576,39827603990324,41347096750576,39827603990324,41347096750576
# ifs-sfire1-p10-15;4,42198315350576,36010635039469,42198315350576,36010635039469,42198315350576,36010635039469
# ifs-sfire1-p6-16;1,40489147953029,44307500303040,40489147953029,44307500303040,40489147953029,44307500303040
# ifs-sfire1-p5-17;5,45303888261816,32837891733970,45303888261816,32837891733970,45303888261816,32837891733970
# ifs-sfire1-p7-18;9,45077444855739,60896878083513,45077444855739,60896878083513,45077444855739,60896878083513

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

def parse_solidfire_nodes(string_table):
    #if debug.enabled():
    #    pprint("##### PARSING ######")
    #    pprint(string_table)
    parsed = {}
    column_names = [
        "node",
        "cpu",
        "cBytesIn",
        "cBytesOut",
        "mBytesIn",
        "mBytesOut",
        "sBytesIn",
        "sBytesOut"
    ]
    for line in string_table:
        parsed[line[0]] = {}
        for n in range(1, len(column_names)):
            parsed[line[0]][column_names[n]] = line[n]
    #if debug.enabled():
    #    pprint(parsed)
    return parsed

agent_section_solidfire_nodes = AgentSection(
    name="slfr_cluster_nodes",
    parse_function=parse_solidfire_nodes
)

def discovery_solidfire_nodes(section: Section) -> DiscoveryResult:
    #if debug.enabled():
    #    pprint("##### DISCOVERY ######")
    #    pprint(section)
    for key in section.keys():
        if key != "":
            yield Service(item=key)

def check_solidfire_nodes(item: str, params: Mapping[str, Any], section: Section) -> CheckResult:
    #if debug.enabled():
    #    pprint("#### CHECK ######")
    #    pprint(section)
    attr = section.get(item)
    if not attr:
        yield Result(state=State.UNKNOWN, summary="Node is missing or has been deleted")
        return

    # Create a store for storing the actual value for the next poll
    store = get_value_store() 
    #print ("Store: ", store)
    now = time.time()
    try:
        cBytesInTemp = get_rate(store, item + "_cBytesInTemp", now, int(attr['cBytesIn']))
        cBytesOutTemp = get_rate(store, item + "_cBytesOutTemp", now, int(attr['cBytesOut']))
        mBytesInTemp = get_rate(store, item + "_mBytesInTemp", now, int(attr['mBytesIn']))
        mBytesOutTemp = get_rate(store, item + "_mBytesOutTemp", now, int(attr['mBytesOut']))
        sBytesInTemp = get_rate(store, item + "_sBytesInTemp", now, int(attr['sBytesIn']))
        sBytesOutTemp = get_rate(store, item + "_sBytesOutTemp", now, int(attr['sBytesOut']))
    except GetRateError as e:
        raise e

    cBytesInDelta = render.bytes(cBytesInTemp)
    cBytesOutDelta = render.bytes(cBytesOutTemp)
    mBytesInDelta = render.bytes(mBytesInTemp)
    mBytesOutDelta = render.bytes(mBytesOutTemp)
    sBytesInDelta = render.bytes(sBytesInTemp)
    sBytesOutDelta = render.bytes(sBytesOutTemp)

    yield Result(
        state = State.OK,
        summary = f"CPU utilization: {attr['cpu']}, cBytesInDelta: {cBytesInDelta}, cBytesOutDelta: {cBytesOutDelta}",
        details = f"mBytesIn: {mBytesInDelta}, mBytesOut: {mBytesOutDelta}, sBytesIn: {sBytesInDelta}, sBytesOut: {sBytesOutDelta}" 
    )

    yield from check_levels(
        int(attr['cpu']),
        levels_upper= ("fixed", (90.0, 80.0)),
        #metric_name = "solidfire_sessions",
        label = "CPU usage is high",
        render_func=lambda v: "%.0f" % v,
        boundaries = (0.0, 100.0),
        notice_only = True,
    )
    
    yield Metric(name="CPU_utilization", value=int(attr['cpu']))
    yield Metric(name="Network_cBytesIn_Delta", value=cBytesInTemp)
    yield Metric(name="Network_cBytesOut_Delta", value=cBytesOutTemp)
    yield Metric(name="Network_mBytesIn_Delta", value=mBytesInTemp)
    yield Metric(name="Network_mBytesOut_Delta", value=mBytesOutTemp)
    yield Metric(name="Network_sBytesIn_Delta", value=sBytesInTemp)
    yield Metric(name="Network_sBytesOut_Delta", value=sBytesOutTemp)

check_plugin_solidfire_nodes = CheckPlugin(
    name="solidfire_nodes",
    service_name="SLFR-NODE-%s",
    check_ruleset_name="solidfire",
    check_default_parameters={},
    sections=["slfr_cluster_nodes"],
    discovery_function=discovery_solidfire_nodes,
    check_function=check_solidfire_nodes,
)
