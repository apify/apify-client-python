from enum import Enum

class PayPerEventActorPricingInfoPricingModel(str, Enum):
    PAY_PER_EVENT = "PAY_PER_EVENT"

    def __str__(self) -> str:
        return str(self.value)
