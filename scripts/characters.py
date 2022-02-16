from enum import Enum


class CharacterType(Enum):
    TOWNSFOLK = "Townsfolk"
    OUTSIDER = "Outsider"
    MINION = "Minion"
    DEMON = "Demon"
    TRAVELLER = "Traveller"
    FABLED = "Fabled"


class Character(Enum):
    ALCHEMIST = ("alchemist", CharacterType.TOWNSFOLK, "Alchemist")
    AMNESIAC = ("amnesiac", CharacterType.TOWNSFOLK, "Amnesiac")
    ARTIST = ("artist", CharacterType.TOWNSFOLK, "Artist")
    ATHEIST = ("atheist", CharacterType.TOWNSFOLK, "Atheist")
    BALLOONIST = ("balloonist", CharacterType.TOWNSFOLK, "Balloonist")
    BOUNTY_HUNTER = ("bounty_hunter", CharacterType.TOWNSFOLK, "Bounty Hunter")
    CANNIBAL = ("cannibal", CharacterType.TOWNSFOLK, "Cannibal")
    CHAMBERMAID = ("chambermaid", CharacterType.TOWNSFOLK, "Chambermaid")
    CHEF = ("chef", CharacterType.TOWNSFOLK, "Chef")
    CHOIRBOY = ("choirboy", CharacterType.TOWNSFOLK, "Choir Boy")
    CLOCKMAKER = ("clockmaker", CharacterType.TOWNSFOLK, "Clockmaker")
    COURTIER = ("courtier", CharacterType.TOWNSFOLK, "Courtier")
    CULTLEADER = ("cult_leader", CharacterType.TOWNSFOLK, "Cult Leader")
    DREAMER = ("dreamer", CharacterType.TOWNSFOLK, "Dreamer")
    EMPATH = ("empath", CharacterType.TOWNSFOLK, "Empath")
    ENGINEER = ("engineer", CharacterType.TOWNSFOLK, "Engineer")
    EXORCIST = ("exorcist", CharacterType.TOWNSFOLK, "Exorcist")
    FARMER = ("farmer", CharacterType.TOWNSFOLK, "Farmer")
    FISHERMAN = ("fisherman", CharacterType.TOWNSFOLK, "Fisherman")
    FLOWERGIRL = ("flowergirl", CharacterType.TOWNSFOLK, "Flowergirl")
    FOOL = ("fool", CharacterType.TOWNSFOLK, "Fool")
    FORTUNE_TELLER = ("fortune_teller", CharacterType.TOWNSFOLK, "Fortune Teller")
    GAMBLER = ("gambler", CharacterType.TOWNSFOLK, "Gambler")
    GENERAL = ("general", CharacterType.TOWNSFOLK, "General")
    GOSSIP = ("gossip", CharacterType.TOWNSFOLK, "Gossip")
    GRANDMOTHER = ("grandmother", CharacterType.TOWNSFOLK, "Grandmother")
    HUNTSMAN = ("huntsman", CharacterType.TOWNSFOLK, "Huntsman")
    INNKEEPER = ("innkeeper", CharacterType.TOWNSFOLK, "Innkeeper")
    INVESTIGATOR = ("investigator", CharacterType.TOWNSFOLK, "Investigator")
    JUGGLER = ("juggler", CharacterType.TOWNSFOLK, "Juggler")
    KING = ("king", CharacterType.TOWNSFOLK, "King")
    LIBRARIAN = ("librarian", CharacterType.TOWNSFOLK, "Librarian")
    LYCANTHROPE = ("lycanthrope", CharacterType.TOWNSFOLK, "Lycanthrope")
    MAGICIAN = ("magician", CharacterType.TOWNSFOLK, "Magician")
    MATHEMATICIAN = ("mathematician", CharacterType.TOWNSFOLK, "Mathematician")
    MAYOR = ("mayor", CharacterType.TOWNSFOLK, "Mayor")
    MINSTREL = ("minstrel", CharacterType.TOWNSFOLK, "Minstrel")
    MONK = ("monk", CharacterType.TOWNSFOLK, "Monk")
    NIGHTWATCHMAN = ("nightwatchman", CharacterType.TOWNSFOLK, "Nightwatchman")
    NOBLE = ("noble", CharacterType.TOWNSFOLK, "Noble")
    ORACLE = ("oracle", CharacterType.TOWNSFOLK, "Oracle")
    PACIFIST = ("pacifist", CharacterType.TOWNSFOLK, "Pacifist")
    PHILOSOPHER = ("philosopher", CharacterType.TOWNSFOLK, "Philosopher")
    PIXIE = ("pixie", CharacterType.TOWNSFOLK, "Pixie")
    POPPY_GROWER = ("poppy_grower", CharacterType.TOWNSFOLK, "Poppy Grower")
    PREACHER = ("preacher", CharacterType.TOWNSFOLK, "Preacher")
    PROFESSOR = ("professor", CharacterType.TOWNSFOLK, "Professor")
    RAVENKEEPER = ("ravenkeeper", CharacterType.TOWNSFOLK, "Ravenkeeper")
    SAGE = ("sage", CharacterType.TOWNSFOLK, "Sage")
    SAILOR = ("sailor", CharacterType.TOWNSFOLK, "Sailor")
    SAVANT = ("savant", CharacterType.TOWNSFOLK, "Savant")
    SEAMSTRESS = ("seamstress", CharacterType.TOWNSFOLK, "Seamstress")
    SLAYER = ("slayer", CharacterType.TOWNSFOLK, "Slayer")
    SNAKE_CHARMER = ("snake_charmer", CharacterType.TOWNSFOLK, "Snake Charmer")
    SOLDIER = ("soldier", CharacterType.TOWNSFOLK, "Soldier")
    TEA_LADY = ("tea_lady", CharacterType.TOWNSFOLK, "Tea Lady")
    TOWN_CRIER = ("town_crier", CharacterType.TOWNSFOLK, "Town Crier")
    UNDERTAKER = ("undertaker", CharacterType.TOWNSFOLK, "Undertaker")
    VIRGIN = ("virgin", CharacterType.TOWNSFOLK, "Virgin")
    WASHERWOMAN = ("washerwoman", CharacterType.TOWNSFOLK, "Washerwoman")
    ACROBAT = ("acrobat", CharacterType.OUTSIDER, "Acrobat")
    BARBER = ("barber", CharacterType.OUTSIDER, "Barber")
    BUTLER = ("butler", CharacterType.OUTSIDER, "Butler")
    DAMSEL = ("damsel", CharacterType.OUTSIDER, "Damsel")
    DRUNK = ("drunk", CharacterType.OUTSIDER, "Drunk")
    GOLEM = ("golem", CharacterType.OUTSIDER, "Golem")
    GOON = ("goon", CharacterType.OUTSIDER, "Goon")
    HERETIC = ("heretic", CharacterType.OUTSIDER, "Heretic")
    KLUTZ = ("klutz", CharacterType.OUTSIDER, "Klutz")
    LUNATIC = ("lunatic", CharacterType.OUTSIDER, "Lunatic")
    MOONCHILD = ("moonchild", CharacterType.OUTSIDER, "Moonchild")
    MUTANT = ("mutant", CharacterType.OUTSIDER, "Mutant")
    POLITICIAN = ("politician", CharacterType.OUTSIDER, "Politician")
    PUZZLEMASTER = ("puzzlemaster", CharacterType.OUTSIDER, "Puzzlemaster")
    RECLUSE = ("recluse", CharacterType.OUTSIDER, "Recluse")
    SAINT = ("saint", CharacterType.OUTSIDER, "Saint")
    SNITCH = ("snitch", CharacterType.OUTSIDER, "Snitch")
    SWEETHEART = ("sweetheart", CharacterType.OUTSIDER, "Sweetheart")
    TINKER = ("tinker", CharacterType.OUTSIDER, "Tinker")
    ASSASSIN = ("assassin", CharacterType.MINION, "Assassin")
    BARON = ("baron", CharacterType.MINION, "Baron")
    BOOMDANDY = ("boomdandy", CharacterType.MINION, "Boomdandy")
    CERENOVUS = ("cerenovus", CharacterType.MINION, "Cerenovus")
    DEVILS_ADVOCATE = ("devils_advocate", CharacterType.MINION, "Devil's Advocate")
    EVIL_TWIN = ("evil_twin", CharacterType.MINION, "Evil Twin")
    FEARMONGER = ("fearmonger", CharacterType.MINION, "Fearmonger")
    GOBLIN = ("goblin", CharacterType.MINION, "Goblin")
    GODFATHER = ("godfather", CharacterType.MINION, "Godfather")
    MARIONETTE = ("marionette", CharacterType.MINION, "Marionette")
    MASTERMIND = ("mastermind", CharacterType.MINION, "Mastermind")
    MEZEPHELES = ("mezepheles", CharacterType.MINION, "Mezepheles")
    PIT_HAG = ("pit-hag", CharacterType.MINION, "Pit Hag")
    POISONER = ("poisoner", CharacterType.MINION, "Poisoner")
    PSYCHOPATH = ("psychopath", CharacterType.MINION, "Psychopath")
    SCARLET_WOMAN = ("scarlet_woman", CharacterType.MINION, "Scarlet Woman")
    SPY = ("spy", CharacterType.MINION, "Spy")
    WIDOW = ("widow", CharacterType.MINION, "Widow")
    WITCH = ("witch", CharacterType.MINION, "Witch")
    AL_HADIKHIA = ("al-hadikhia", CharacterType.DEMON, "Al-Hadikhia")
    FANG_GU = ("fang_gu", CharacterType.DEMON, "Fang Gu")
    IMP = ("imp", CharacterType.DEMON, "Imp")
    LEGION = ("legion", CharacterType.DEMON, "Legion")
    LEVIATHAN = ("leviathan", CharacterType.DEMON, "Leviathan")
    LIL_MONSTA = ("lil_monsta", CharacterType.DEMON, "Lil' Monsta")
    LLEECH = ("lleech", CharacterType.DEMON, "Lleech")
    NO_DASHII = ("no_dashii", CharacterType.DEMON, "No Dashii")
    PO = ("po", CharacterType.DEMON, "Po")
    PUKKA = ("pukka", CharacterType.DEMON, "Pukka")
    RIOT = ("riot", CharacterType.DEMON, "Riot")
    SHABALOTH = ("shabaloth", CharacterType.DEMON, "Shabaloth")
    VIGORMORTIS = ("vigormortis", CharacterType.DEMON, "Vigormortis")
    VORTOX = ("vortox", CharacterType.DEMON, "Vortox")
    ZOMBUUL = ("zombuul", CharacterType.DEMON, "Zombuul")
    APPRENTICE = ("apprentice", CharacterType.TRAVELLER, "Apprentice")
    BARISTA = ("barista", CharacterType.TRAVELLER, "Barista")
    BEGGAR = ("beggar", CharacterType.TRAVELLER, "Beggar")
    BISHOP = ("bishop", CharacterType.TRAVELLER, "Bishop")
    BONE_COLLECTOR = ("bone_collector", CharacterType.TRAVELLER, "Bone Collector")
    BUREAUCRAT = ("bureaucrat", CharacterType.TRAVELLER, "Bureaucrat")
    BUTCHER = ("butcher", CharacterType.TRAVELLER, "Butcher")
    DEVIANT = ("deviant", CharacterType.TRAVELLER, "Deviant")
    GANGSTER = ("gangster", CharacterType.TRAVELLER, "Gangster")
    GUNSLINGER = ("gunslinger", CharacterType.TRAVELLER, "Gunslinger")
    HARLOT = ("harlot", CharacterType.TRAVELLER, "Harlot")
    JUDGE = ("judge", CharacterType.TRAVELLER, "Judge")
    MATRON = ("matron", CharacterType.TRAVELLER, "Matron")
    SCAPEGOAT = ("scapegoat", CharacterType.TRAVELLER, "Scapegoat")
    THIEF = ("thief", CharacterType.TRAVELLER, "Thief")
    VOUDON = ("voudon", CharacterType.TRAVELLER, "Voudon")
    ANGEL = ("angel", CharacterType.FABLED, "Angel")
    BUDDHIST = ("buddhist", CharacterType.FABLED, "Buddhist")
    DJINN = ("djinn", CharacterType.FABLED, "Djinn")
    DOOMSAYER = ("doomsayer", CharacterType.FABLED, "Doomsayer")
    DUCHESS = ("duchess", CharacterType.FABLED, "Duchess")
    FIBBIN = ("fibbin", CharacterType.FABLED, "Fibbin")
    FIDDLER = ("fiddler", CharacterType.FABLED, "Fiddler")
    HELLS_LIBRARIAN = ("hells_librarian", CharacterType.FABLED, "Hell's Librarian")
    REVOLUTIONARY = ("revolutionary", CharacterType.FABLED, "Revolutionary")
    SENTINEL = ("sentinel", CharacterType.FABLED, "Sentinel")
    SPIRIT_OF_IVORY = ("spirit_of_ivory", CharacterType.FABLED, "Spirit of Ivory")
    STORM_CATCHER = ("storm_catcher", CharacterType.FABLED, "Storm Catcher")
    TOYMAKER = ("toymaker", CharacterType.FABLED, "Toymaker")

    def __init__(self, json_id, character_type, character_name):
        self._json_id = json_id
        self._character_type = character_type
        self._character_name = character_name

    @property
    def json_id(self):
        return self._json_id

    @property
    def character_type(self):
        return self._character_type

    @property
    def character_name(self):
        return self._character_name

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
