from cmk.graphing.v1 import Title
from cmk.graphing.v1.metrics import Color, IECNotation, Metric, Unit

UNIT_BYTES = Unit(IECNotation("B"))

metric_solidfire_reads = Metric(
    name = "Bytes_Read",
    title = Title("Bytes Read"),
    unit=UNIT_BYTES,
    color = Color.GREEN,
)

metric_solidfire_writes = Metric(
    name = "Bytes_Write",
    title = Title("Bytes write"),
    unit=UNIT_BYTES,
    color = Color.BLUE,
)

metric_solidfire_cBytesIn = Metric(
    name = "Network_cBytesIn_Delta",
    title = Title("cBytes IN"),
    unit=UNIT_BYTES,
    color = Color.GREEN,
)


metric_solidfire_cBytesOut = Metric(
    name = "Network_cBytesOut_Delta",
    title = Title("cBytes OUT"),
    unit=UNIT_BYTES,
    color = Color.YELLOW,
)

metric_solidfire_mBytesIn = Metric(
    name = "Network_mBytesIn_Delta",
    title = Title("mBytes IN"),
    unit=UNIT_BYTES,
    color = Color.CYAN,
)

metric_solidfire_mBytesOut = Metric(
    name = "Network_mBytesOut_Delta",
    title = Title("mBytes OUT"),
    unit=UNIT_BYTES,
    color = Color.GREEN,
)

metric_solidfire_sBytesIn = Metric(
    name = "Network_sBytesIn_Delta",
    title = Title("sBytes IN"),
    unit=UNIT_BYTES,
    color = Color.PURPLE,
)

metric_solidfire_sBytesOut = Metric(
    name = "Network_sBytesOut_Delta",
    title = Title("sBytes OUT"),
    unit=UNIT_BYTES,
    color = Color.LIGHT_BROWN,
)
