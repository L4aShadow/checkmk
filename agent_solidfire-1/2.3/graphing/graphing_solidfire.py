from cmk.graphing.v1 import Title
from cmk.graphing.v1.graphs import Graph, MinimalRange
from cmk.graphing.v1.metrics import Color, DecimalNotation, Metric, Unit
from cmk.graphing.v1.perfometers import Closed, FocusRange, Open, Perfometer

metric_solidfire_sessions = Metric(
    name = "solidfire_sessions",
    title = Title("Number of current Sessions."),
    unit = Unit(DecimalNotation(" ")),
    color = Color.ORANGE,
)

metric_solidfire_network = Metric(
    name = "solidfire_network",
    title = Title("Network Traffic"),
    unit = Unit(SINotation("bytes")(" "))
    color = Color.ORANGE,
)
