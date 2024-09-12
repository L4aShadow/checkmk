#!/usr/bin/env python3
# author: Christoph Kessler christoph.kessler@prosiebensat1.com

from cmk.rulesets.v1 import Title, Help
from cmk.rulesets.v1.form_specs import (
    CascadingSingleChoice,
    CascadingSingleChoiceElement,
    DefaultValue,
    DictElement,
    Dictionary,
    FixedValue,
    InputHint,
    Integer,
    LevelDirection,
    migrate_to_integer_simple_levels,
    Password,
    SimpleLevels,
    SingleChoice,
    SingleChoiceElement,
    String,
)
from cmk.rulesets.v1.rule_specs import CheckParameters, Topic, HostCondition, SpecialAgent
from cmk.rulesets.v1.form_specs.validators import LengthInRange, NetworkPort, ValidationError

def _form_spec_special_agents_solidfire() -> Dictionary:
    return Dictionary(
        title=Title("Base configuration for NetApp REST API"),
        elements={
            "user": DictElement(
                parameter_form=String(
                    title=Title("Username"),
                    custom_validate=[
                        LengthInRange(min_value=1),
                    ],
                ),
                required=True,
            ),
            "password": DictElement(
                parameter_form=Password(
                    title=Title("Password"),
                    custom_validate=[
                        LengthInRange(min_value=1),
                    ],
                ),
                required=True,
            ),
            "port": DictElement(
                parameter_form=Integer(
                    title=Title("Port"),
                    help_text=Help(
                        "The TCP port the REST API is listen to."
                    ),
                    prefill=DefaultValue(443),

                ),
                required=True,
            ),
            "iptype": DictElement(
                parameter_form=SingleChoice(
                    title=Title("IP Type"),
                    prefill=DefaultValue("mvip"),
                    help_text=Help(
                        "IP Type of Connection"
                    ),
                    elements=[
                        SingleChoiceElement(
                            name="mvip",
                            title=Title("Cluster"),
                        ),
                        SingleChoiceElement(
                            name="node",
                            title=Title("Node"),
                        ),
                    ],
                ),
                required=True,
            ),
        },
    )

rule_spec_solidfire = SpecialAgent(
    topic=Topic.STORAGE,
    name="solidfire",
    title=Title("NetApp Solidfire Devices"),    
    parameter_form=_form_spec_special_agents_solidfire,
    help_text=(
        "This rule configures the Agend Solidfire instead of the normal Check_MK Agent "
        "which collects the data through the NetApp Solidfire REST API"
    ),
)
