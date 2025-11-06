from enum import Enum

class FreeActorPricingInfoPricingModel(str, Enum):
    FREE = "FREE"

    def __str__(self) -> str:
        return str(self.value)
