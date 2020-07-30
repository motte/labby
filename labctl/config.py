import strictyaml
from strictyaml import Any, Enum, Map, MapPattern, Seq, Str

SCHEMA = Map(
    {
        "devices": Seq(
            Map(
                {
                    "name": Str(),
                    "type": Enum("psu"),
                    "driver": Str(),
                    "args": MapPattern(Str(), Any()),
                }
            )
        ),
    }
)


class Config:
    config: strictyaml.YAML

    def __init__(self, yaml_contents: str) -> None:
        self.config = strictyaml.load(yaml_contents, SCHEMA)