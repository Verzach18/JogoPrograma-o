from config import COSTS, RESEARCH_TREE

class ProgressionManager:
    def __init__(self):
        self.unlocked = {
            "move": True, "till": True, "harvest": True, "plant": True,
            "if_statements": False,
            "loops": False,
            "functions": False,
            "navigation_unlock": False,
            "inspector_unlock": False,
            "speed_upgrade_1": False,
            "speed_upgrade_2": False,
            "battery_1": False,
            "battery_2": False,
            "miner_unlock": False,
            "atmo_gen_unlock": False,
            "heater_unlock": False,
        }
        
    def can_use(self, feature: str) -> bool:
        return self.unlocked.get(feature, False)
        
    def is_visible(self, feature: str) -> bool:
        # Tech is visible if all dependencies are met
        deps = RESEARCH_TREE.get(feature, [])
        return all(self.unlocked.get(d, False) for d in deps)

    def buy(self, feature: str, drone) -> bool:
        if self.unlocked.get(feature, True): return False
        if not self.is_visible(feature): return False
        
        cost = COSTS.get(feature, 0)
        # Some things might cost minerals later? For now Biomass
        if drone.resources["Biomass"] >= cost:
            drone.resources["Biomass"] -= cost
            self.unlocked[feature] = True
            
            # Apply immediate effects
            if feature == "battery_1": drone.max_energy += 50; drone.energy += 50
            if feature == "battery_2": drone.max_energy += 100; drone.energy += 100
            
            return True
        return False
