from dataclasses import dataclass
from enum import Enum


@dataclass
class CollabType(Enum):
    Art = "art"
    Digital = "digital"
    BetterFuture = "better_future"
    Influence = "influence"
    Brands = "brands"
    Hub = "hub"


@dataclass
class WorkStatus(Enum):
    Moderation = "moderation"
    Published = "published"
    Rejected = "rejected"


class WorkTags(Enum):
    Dizain = "дизайн"
    Illiustraciya = "иллюстрация"
    Fotografiia = "фотография"
    ArtObiekty = "арт-объекты"
    DigitalArt = "digital art"
    ThreeD = "3D"
    Esg = "ESG"
    DizainOdezhdy = "дизайн одежды"
    DizainAksessuarov = "дизайн аксессуаров"
    GrafDizain = "графический дизайн"
    Zhivopis = "живопись"
    Grafika = "графика"
    StreetArt = "street art"
    Castomizing = "кастомайзинг"
