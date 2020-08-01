import strictyaml
from strictyaml import Any, Enum, Map, MapPattern, Seq, Str
from typing import Sequence

from labctl.hw.core import Device


SCHEMA = Map(
    {
        "devices": Seq(
            Map(
                {
                    "name": Str(),
                    "type": Enum("power_supply"),
                    "driver": Str(),
                    "args": MapPattern(Str(), Any()),
                }
            )
        ),
    }
)


class Config:
    config: strictyaml.YAML
    devices: Sequence[Device]

    def __init__(self, yaml_contents: str) -> None:
        self.config = strictyaml.load(yaml_contents, SCHEMA)
        self.devices = [
            Device.create(device["name"], device["driver"].data, device["args"].data)
            for device in self.config["devices"]
        ]

    def get_devices(self) -> Sequence[Device]:
        return self.devices
