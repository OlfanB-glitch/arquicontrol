from abc import ABC, abstractmethod


class AvanceProyectoStrategy(ABC):
    @abstractmethod
    def calculate(self, project_data: dict) -> float:
        raise NotImplementedError


class AvancePorSeguimientosStrategy(AvanceProyectoStrategy):
    def calculate(self, project_data: dict) -> float:
        seguimientos = [
            item
            for item in project_data.get("seguimientos", [])
            if item.get("isActive", True)
        ]
        if not seguimientos:
            return 0.0
        total = sum(float(item.get("porcentajeAvance", 0)) for item in seguimientos)
        return round(total / len(seguimientos), 2)


class AvancePorFasesStrategy(AvanceProyectoStrategy):
    def calculate(self, project_data: dict) -> float:
        fases = [item for item in project_data.get("fases", []) if item.get("isActive", True)]
        if not fases:
            return 0.0
        total = sum(float(item.get("porcentajeAvance", 0)) for item in fases)
        return round(total / len(fases), 2)


class AvanceStrategyResolver:
    def resolve(self, method: str) -> AvanceProyectoStrategy:
        if method == "FASES":
            return AvancePorFasesStrategy()
        return AvancePorSeguimientosStrategy()