import pygame # type: ignore
from config import *

class Mission:
    def __init__(self, id, title, description, target_count, reward_biomass=0, reward_minerals=0, hint=""):
        self.id = id
        self.title = title
        self.description = description
        self.target_count = target_count
        self.current_count = 0
        self.reward_biomass = reward_biomass
        self.reward_minerals = reward_minerals
        self.completed = False
        self.hint = hint

    def check_progress(self, action_type, count=1):
        if self.completed: return False
        
        # Mission logic
        if self.id == "move" and action_type == "move":
            self.current_count += count
        elif self.id == "till" and action_type == "till":
            self.current_count += count
        elif self.id == "plant" and action_type == "plant":
            self.current_count += count
        elif self.id == "harvest" and action_type == "harvest":
            self.current_count += count
        elif self.id == "research" and action_type == "research":
            self.current_count += count
            
        if self.current_count >= self.target_count:
            self.completed = True
            return True
        return False

class MissionManager:
    def __init__(self):
        self.missions = [
            Mission("move", "Primeiros Passos", "Aprenda a se mover usando 'drone.move(Direction.RIGHT)' no editor.", 5, 
                    reward_biomass=20, hint="Use drone.move(Direction.RIGHT) para começar."),
            Mission("till", "Preparando o Solo", "Use 'drone.till()' para arar 3 espaços de terra.", 3, 
                    reward_biomass=30, hint="O solo precisa estar arado antes de plantar."),
            Mission("plant", "O Botânico", "Plante 3 sementes de grama usando 'drone.plant(Entities.GRASS)'.", 3, 
                    reward_biomass=50, hint="Grama é a base de toda vida (e biomassa)."),
            Mission("harvest", "Colheita de Dados", "Espere a grama crescer e use 'drone.harvest()' para coletar 3 recursos.", 3, 
                    reward_minerals=20, hint="Recursos permitem desbloquear novas tecnologias."),
            Mission("research", "Expansão Científica", "Abra o Lab de Pesquisa (R) e desbloqueie 'Loops' por 50 Biomassa.", 1, 
                    reward_biomass=100, hint="Automação é a chave para o sucesso.")
        ]
        self.current_idx = 0
        self.active_mission = self.missions[0]
        self.notifications = None # Injected by engine

    def update_progress(self, action_type, drone, count=1):
        if not self.active_mission:
            return

        if self.active_mission.check_progress(action_type, count):
            # Reward
            drone.resources["Biomass"] += self.active_mission.reward_biomass
            drone.resources["Minerals"] += self.active_mission.reward_minerals
            
            if self.notifications:
                self.notifications.add_notification("MISSÃO CONCLUÍDA", f"{self.active_mission.title} finalizada!", color=COLOR_SUCCESS)
            
            drone.log(f"MISSÃO CONCLUÍDA: {self.active_mission.title}!")
            
            # Next mission
            self.current_idx += 1
            if self.current_idx < len(self.missions):
                self.active_mission = self.missions[self.current_idx]
                if self.notifications:
                    self.notifications.add_notification("NOVO OBJETIVO", self.active_mission.title, duration=4.0)
            else:
                self.active_mission = None
                if self.notifications:
                    self.notifications.add_notification("CAPÍTULO 1 COMPLETO", "Você dominou o básico da terraformação!", color=COLOR_SECONDARY)
