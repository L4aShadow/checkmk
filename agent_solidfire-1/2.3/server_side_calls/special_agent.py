#!/usr/bin/env python3
# Copyright (C) 2019 Checkmk GmbH - License: GNU General Public License v2
# This file is part of Checkmk (https://checkmk.com). It is subject to the terms and
# conditions defined in the file COPYING, which is part of this source code package.

from collections.abc import Iterator, Mapping, Sequence

from pydantic import BaseModel

from cmk.server_side_calls.v1 import (
    HostConfig,
    Secret,
    SpecialAgentCommand,
    SpecialAgentConfig,
)

class SolidfireParams(BaseModel):
    user: str | None = None
    password: Secret | None = None
    port: int | None = None
    iptype: str | None = None

def solidfire_arguments(
    params: SolidfireParams,
    host_config: HostConfig,
) -> Iterator[SpecialAgentCommand]:
    args: list[str | Secret] = []
    if params.user is not None:
        args += ["-u", params.user]

    if params.password is not None:
        args += ["-pw", "checkmk123"] #params.password]

    if params.port is not None:
        args += ["-p", str(params.port)]

    if params.iptype is not None:
        args += ["-type", params.iptype]
    
    args.append(host_config.primary_ip_config.address or host_config.name)
    yield SpecialAgentCommand(command_arguments=args)

    yield SpecialAgentCommand(command_arguments=args)

special_agent_solidfire = SpecialAgentConfig(
    name="solidfire",
    parameter_parser=SolidfireParams.model_validate,
    commands_function=solidfire_arguments,
)