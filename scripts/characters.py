from enum import Enum
from scripts.models import Edition


class CharacterType(Enum):
    TOWNSFOLK = "Townsfolk"
    OUTSIDER = "Outsider"
    MINION = "Minion"
    DEMON = "Demon"
    TRAVELLER = "Traveller"
    FABLED = "Fabled"


class Character(Enum):
    # Townsfolk
    ALCHEMIST = ("alchemist", CharacterType.TOWNSFOLK, "Alchemist", Edition.KICKSTARTER)
    AMNESIAC = ("amnesiac", CharacterType.TOWNSFOLK, "Amnesiac", Edition.KICKSTARTER)
    ARTIST = ("artist", CharacterType.TOWNSFOLK, "Artist", Edition.BASE)
    ATHEIST = ("atheist", CharacterType.TOWNSFOLK, "Atheist", Edition.KICKSTARTER)
    BALLOONIST = (
        "balloonist",
        CharacterType.TOWNSFOLK,
        "Balloonist",
        Edition.UNRELEASED,
    )
    BOUNTY_HUNTER = (
        "bounty_hunter",
        CharacterType.TOWNSFOLK,
        "Bounty Hunter",
        Edition.UNRELEASED,
    )
    CANNIBAL = ("cannibal", CharacterType.TOWNSFOLK, "Cannibal", Edition.KICKSTARTER)
    CHAMBERMAID = ("chambermaid", CharacterType.TOWNSFOLK, "Chambermaid", Edition.BASE)
    CHEF = ("chef", CharacterType.TOWNSFOLK, "Chef", Edition.BASE)
    CHOIRBOY = ("choirboy", CharacterType.TOWNSFOLK, "Choir Boy", Edition.KICKSTARTER)
    CLOCKMAKER = ("clockmaker", CharacterType.TOWNSFOLK, "Clockmaker", Edition.BASE)
    COURTIER = ("courtier", CharacterType.TOWNSFOLK, "Courtier", Edition.BASE)
    CULTLEADER = (
        "cult_leader",
        CharacterType.TOWNSFOLK,
        "Cult Leader",
        Edition.UNRELEASED,
    )
    DREAMER = ("dreamer", CharacterType.TOWNSFOLK, "Dreamer", Edition.BASE)
    EMPATH = ("empath", CharacterType.TOWNSFOLK, "Empath", Edition.BASE)
    ENGINEER = ("engineer", CharacterType.TOWNSFOLK, "Engineer", Edition.KICKSTARTER)
    EXORCIST = ("exorcist", CharacterType.TOWNSFOLK, "Exorcist", Edition.BASE)
    FARMER = ("farmer", CharacterType.TOWNSFOLK, "Farmer", Edition.KICKSTARTER)
    FISHERMAN = ("fisherman", CharacterType.TOWNSFOLK, "Fisherman", Edition.UNRELEASED)
    FLOWERGIRL = ("flowergirl", CharacterType.TOWNSFOLK, "Flowergirl", Edition.BASE)
    FOOL = ("fool", CharacterType.TOWNSFOLK, "Fool", Edition.BASE)
    FORTUNE_TELLER = (
        "fortune_teller",
        CharacterType.TOWNSFOLK,
        "Fortune Teller",
        Edition.BASE,
    )
    GAMBLER = ("gambler", CharacterType.TOWNSFOLK, "Gambler", Edition.BASE)
    GENERAL = ("general", CharacterType.TOWNSFOLK, "General", Edition.KICKSTARTER)
    GOSSIP = ("gossip", CharacterType.TOWNSFOLK, "Gossip", Edition.BASE)
    GRANDMOTHER = ("grandmother", CharacterType.TOWNSFOLK, "Grandmother", Edition.BASE)
    HUNTSMAN = ("huntsman", CharacterType.TOWNSFOLK, "Huntsman", Edition.KICKSTARTER)
    INNKEEPER = ("innkeeper", CharacterType.TOWNSFOLK, "Innkeeper", Edition.BASE)
    INVESTIGATOR = (
        "investigator",
        CharacterType.TOWNSFOLK,
        "Investigator",
        Edition.BASE,
    )
    JUGGLER = ("juggler", CharacterType.TOWNSFOLK, "Juggler", Edition.BASE)
    KING = ("king", CharacterType.TOWNSFOLK, "King", Edition.KICKSTARTER)
    LIBRARIAN = ("librarian", CharacterType.TOWNSFOLK, "Librarian", Edition.BASE)
    LYCANTHROPE = (
        "lycanthrope",
        CharacterType.TOWNSFOLK,
        "Lycanthrope",
        Edition.KICKSTARTER,
    )
    MAGICIAN = ("magician", CharacterType.TOWNSFOLK, "Magician", Edition.KICKSTARTER)
    MATHEMATICIAN = (
        "mathematician",
        CharacterType.TOWNSFOLK,
        "Mathematician",
        Edition.BASE,
    )
    MAYOR = ("mayor", CharacterType.TOWNSFOLK, "Mayor", Edition.BASE)
    MINSTREL = ("minstrel", CharacterType.TOWNSFOLK, "Minstrel", Edition.BASE)
    MONK = ("monk", CharacterType.TOWNSFOLK, "Monk", Edition.BASE)
    NIGHTWATCHMAN = (
        "nightwatchman",
        CharacterType.TOWNSFOLK,
        "Nightwatchman",
        Edition.UNRELEASED,
    )
    NOBLE = ("noble", CharacterType.TOWNSFOLK, "Noble", Edition.KICKSTARTER)
    ORACLE = ("oracle", CharacterType.TOWNSFOLK, "Oracle", Edition.BASE)
    PACIFIST = ("pacifist", CharacterType.TOWNSFOLK, "Pacifist", Edition.BASE)
    PHILOSOPHER = ("philosopher", CharacterType.TOWNSFOLK, "Philosopher", Edition.BASE)
    PIXIE = ("pixie", CharacterType.TOWNSFOLK, "Pixie", Edition.KICKSTARTER)
    POPPY_GROWER = (
        "poppy_grower",
        CharacterType.TOWNSFOLK,
        "Poppy Grower",
        Edition.KICKSTARTER,
    )
    PREACHER = ("preacher", CharacterType.TOWNSFOLK, "Preacher", Edition.UNRELEASED)
    PROFESSOR = ("professor", CharacterType.TOWNSFOLK, "Professor", Edition.BASE)
    RAVENKEEPER = ("ravenkeeper", CharacterType.TOWNSFOLK, "Ravenkeeper", Edition.BASE)
    SAGE = ("sage", CharacterType.TOWNSFOLK, "Sage", Edition.BASE)
    SAILOR = ("sailor", CharacterType.TOWNSFOLK, "Sailor", Edition.BASE)
    SAVANT = ("savant", CharacterType.TOWNSFOLK, "Savant", Edition.BASE)
    SEAMSTRESS = ("seamstress", CharacterType.TOWNSFOLK, "Seamstress", Edition.BASE)
    SLAYER = ("slayer", CharacterType.TOWNSFOLK, "Slayer", Edition.BASE)
    SNAKE_CHARMER = (
        "snake_charmer",
        CharacterType.TOWNSFOLK,
        "Snake Charmer",
        Edition.BASE,
    )
    SOLDIER = ("soldier", CharacterType.TOWNSFOLK, "Soldier", Edition.BASE)
    TEA_LADY = ("tea_lady", CharacterType.TOWNSFOLK, "Tea Lady", Edition.BASE)
    TOWN_CRIER = ("town_crier", CharacterType.TOWNSFOLK, "Town Crier", Edition.BASE)
    UNDERTAKER = ("undertaker", CharacterType.TOWNSFOLK, "Undertaker", Edition.BASE)
    VIRGIN = ("virgin", CharacterType.TOWNSFOLK, "Virgin", Edition.BASE)
    WASHERWOMAN = ("washerwoman", CharacterType.TOWNSFOLK, "Washerwoman", Edition.BASE)

    # Outsiders
    ACROBAT = ("acrobat", CharacterType.OUTSIDER, "Acrobat", Edition.UNRELEASED)
    BARBER = ("barber", CharacterType.OUTSIDER, "Barber", Edition.BASE)
    BUTLER = ("butler", CharacterType.OUTSIDER, "Butler", Edition.BASE)
    DAMSEL = ("damsel", CharacterType.OUTSIDER, "Damsel", Edition.KICKSTARTER)
    DRUNK = ("drunk", CharacterType.OUTSIDER, "Drunk", Edition.BASE)
    GOLEM = ("golem", CharacterType.OUTSIDER, "Golem", Edition.KICKSTARTER)
    GOON = ("goon", CharacterType.OUTSIDER, "Goon", Edition.BASE)
    HERETIC = ("heretic", CharacterType.OUTSIDER, "Heretic", Edition.KICKSTARTER)
    KLUTZ = ("klutz", CharacterType.OUTSIDER, "Klutz", Edition.BASE)
    LUNATIC = ("lunatic", CharacterType.OUTSIDER, "Lunatic", Edition.BASE)
    MOONCHILD = ("moonchild", CharacterType.OUTSIDER, "Moonchild", Edition.BASE)
    MUTANT = ("mutant", CharacterType.OUTSIDER, "Mutant", Edition.BASE)
    POLITICIAN = (
        "politician",
        CharacterType.OUTSIDER,
        "Politician",
        Edition.UNRELEASED,
    )
    PUZZLEMASTER = (
        "puzzlemaster",
        CharacterType.OUTSIDER,
        "Puzzlemaster",
        Edition.KICKSTARTER,
    )
    RECLUSE = ("recluse", CharacterType.OUTSIDER, "Recluse", Edition.BASE)
    SAINT = ("saint", CharacterType.OUTSIDER, "Saint", Edition.BASE)
    SNITCH = ("snitch", CharacterType.OUTSIDER, "Snitch", Edition.KICKSTARTER)
    SWEETHEART = ("sweetheart", CharacterType.OUTSIDER, "Sweetheart", Edition.BASE)
    TINKER = ("tinker", CharacterType.OUTSIDER, "Tinker", Edition.BASE)

    # Minion
    ASSASSIN = ("assassin", CharacterType.MINION, "Assassin", Edition.BASE)
    BARON = ("baron", CharacterType.MINION, "Baron", Edition.BASE)
    BOOMDANDY = ("boomdandy", CharacterType.MINION, "Boomdandy", Edition.KICKSTARTER)
    CERENOVUS = ("cerenovus", CharacterType.MINION, "Cerenovus", Edition.BASE)
    DEVILS_ADVOCATE = (
        "devils_advocate",
        CharacterType.MINION,
        "Devil's Advocate",
        Edition.BASE,
    )
    EVIL_TWIN = ("evil_twin", CharacterType.MINION, "Evil Twin", Edition.BASE)
    FEARMONGER = ("fearmonger", CharacterType.MINION, "Fearmonger", Edition.KICKSTARTER)
    GOBLIN = ("goblin", CharacterType.MINION, "Goblin", Edition.UNRELEASED)
    GODFATHER = ("godfather", CharacterType.MINION, "Godfather", Edition.BASE)
    MARIONETTE = ("marionette", CharacterType.MINION, "Marionette", Edition.KICKSTARTER)
    MASTERMIND = ("mastermind", CharacterType.MINION, "Mastermind", Edition.BASE)
    MEZEPHELES = ("mezepheles", CharacterType.MINION, "Mezepheles", Edition.KICKSTARTER)
    PIT_HAG = ("pit-hag", CharacterType.MINION, "Pit Hag", Edition.BASE)
    POISONER = ("poisoner", CharacterType.MINION, "Poisoner", Edition.BASE)
    PSYCHOPATH = ("psychopath", CharacterType.MINION, "Psychopath", Edition.KICKSTARTER)
    SCARLET_WOMAN = (
        "scarlet_woman",
        CharacterType.MINION,
        "Scarlet Woman",
        Edition.BASE,
    )
    SPY = ("spy", CharacterType.MINION, "Spy", Edition.BASE)
    WIDOW = ("widow", CharacterType.MINION, "Widow", Edition.UNRELEASED)
    WITCH = ("witch", CharacterType.MINION, "Witch", Edition.BASE)

    # Demon
    AL_HADIKHIA = (
        "al-hadikhia",
        CharacterType.DEMON,
        "Al-Hadikhia",
        Edition.KICKSTARTER,
    )
    FANG_GU = ("fang_gu", CharacterType.DEMON, "Fang Gu", Edition.BASE)
    IMP = ("imp", CharacterType.DEMON, "Imp", Edition.BASE)
    LEGION = ("legion", CharacterType.DEMON, "Legion", Edition.KICKSTARTER)
    LEVIATHAN = ("leviathan", CharacterType.DEMON, "Leviathan", Edition.KICKSTARTER)
    LIL_MONSTA = ("lil_monsta", CharacterType.DEMON, "Lil' Monsta", Edition.UNRELEASED)
    LLEECH = ("lleech", CharacterType.DEMON, "Lleech", Edition.KICKSTARTER)
    NO_DASHII = ("no_dashii", CharacterType.DEMON, "No Dashii", Edition.BASE)
    PO = ("po", CharacterType.DEMON, "Po", Edition.BASE)
    PUKKA = ("pukka", CharacterType.DEMON, "Pukka", Edition.BASE)
    RIOT = ("riot", CharacterType.DEMON, "Riot", Edition.KICKSTARTER)
    SHABALOTH = ("shabaloth", CharacterType.DEMON, "Shabaloth", Edition.BASE)
    VIGORMORTIS = ("vigormortis", CharacterType.DEMON, "Vigormortis", Edition.BASE)
    VORTOX = ("vortox", CharacterType.DEMON, "Vortox", Edition.BASE)
    ZOMBUUL = ("zombuul", CharacterType.DEMON, "Zombuul", Edition.BASE)

    # Travelers
    APPRENTICE = ("apprentice", CharacterType.TRAVELLER, "Apprentice", Edition.BASE)
    BARISTA = ("barista", CharacterType.TRAVELLER, "Barista", Edition.BASE)
    BEGGAR = ("beggar", CharacterType.TRAVELLER, "Beggar", Edition.BASE)
    BISHOP = ("bishop", CharacterType.TRAVELLER, "Bishop", Edition.BASE)
    BONE_COLLECTOR = (
        "bone_collector",
        CharacterType.TRAVELLER,
        "Bone Collector",
        Edition.BASE,
    )
    BUREAUCRAT = ("bureaucrat", CharacterType.TRAVELLER, "Bureaucrat", Edition.BASE)
    BUTCHER = ("butcher", CharacterType.TRAVELLER, "Butcher", Edition.BASE)
    DEVIANT = ("deviant", CharacterType.TRAVELLER, "Deviant", Edition.BASE)
    GANGSTER = ("gangster", CharacterType.TRAVELLER, "Gangster", Edition.KICKSTARTER)
    GUNSLINGER = ("gunslinger", CharacterType.TRAVELLER, "Gunslinger", Edition.BASE)
    HARLOT = ("harlot", CharacterType.TRAVELLER, "Harlot", Edition.BASE)
    JUDGE = ("judge", CharacterType.TRAVELLER, "Judge", Edition.BASE)
    MATRON = ("matron", CharacterType.TRAVELLER, "Matron", Edition.BASE)
    SCAPEGOAT = ("scapegoat", CharacterType.TRAVELLER, "Scapegoat", Edition.BASE)
    THIEF = ("thief", CharacterType.TRAVELLER, "Thief", Edition.BASE)
    VOUDON = ("voudon", CharacterType.TRAVELLER, "Voudon", Edition.BASE)

    # Fabled
    ANGEL = ("angel", CharacterType.FABLED, "Angel", Edition.BASE)
    BUDDHIST = ("buddhist", CharacterType.FABLED, "Buddhist", Edition.BASE)
    DJINN = ("djinn", CharacterType.FABLED, "Djinn", Edition.BASE)
    DOOMSAYER = ("doomsayer", CharacterType.FABLED, "Doomsayer", Edition.BASE)
    DUCHESS = ("duchess", CharacterType.FABLED, "Duchess", Edition.BASE)
    FIBBIN = ("fibbin", CharacterType.FABLED, "Fibbin", Edition.BASE)
    FIDDLER = ("fiddler", CharacterType.FABLED, "Fiddler", Edition.BASE)
    HELLS_LIBRARIAN = (
        "hells_librarian",
        CharacterType.FABLED,
        "Hell's Librarian",
        Edition.BASE,
    )
    REVOLUTIONARY = (
        "revolutionary",
        CharacterType.FABLED,
        "Revolutionary",
        Edition.BASE,
    )
    SENTINEL = ("sentinel", CharacterType.FABLED, "Sentinel", Edition.BASE)
    SPIRIT_OF_IVORY = (
        "spirit_of_ivory",
        CharacterType.FABLED,
        "Spirit of Ivory",
        Edition.BASE,
    )
    STORM_CATCHER = (
        "storm_catcher",
        CharacterType.FABLED,
        "Storm Catcher",
        Edition.KICKSTARTER,
    )
    TOYMAKER = ("toymaker", CharacterType.FABLED, "Toymaker", Edition.BASE)

    def __init__(self, json_id, character_type, character_name, edition):
        self._json_id = json_id
        self._character_type = character_type
        self._character_name = character_name
        self._edition = edition

    @property
    def json_id(self):
        return self._json_id

    @property
    def character_type(self):
        return self._character_type

    @property
    def character_name(self):
        return self._character_name

    @property
    def edition(self):
        return self._edition

    @classmethod
    def get(self, name):
        try:
            for char in Character:
                if char.json_id == name:
                    return char
        except KeyError:
            return None


def get_characters_by_type(type: CharacterType):
    return [item for item in Character if item.character_type == type]


def get_characters_not_in_edition(edition: Edition):
    return [item for item in Character if item.edition > edition]
