from config import COSTS

class ProgressionManager:
    def __init__(self):
        self.unlocked = {
            "move": True,
            "till": True,
            "harvest": True,
            "plant": True,
            "loops": False,
            "if_statements": False,
            "functions": False,
            "miner": False,
            "atmo_gen_unlock": False,
            "heater_unlock": False,
        }
        
    def can_use(self, feature: str) -> bool:
        return self.unlocked.get(feature, False)
        
    def buy(self, feature: str, drone) -> bool:
        cost = COSTS.get(feature, 0)
        if drone.resources["Biomass"] >= cost and not self.unlocked[feature]:
            drone.resources["Biomass"] -= cost
            self.unlocked[feature] = True
            return True
        return False
