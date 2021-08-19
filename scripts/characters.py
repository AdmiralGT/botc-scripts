from enum import Enum

class CharacterType(Enum):
    TOWNSFOLK = 'Townsfolk'
    OUTSIDER = 'Outsider'
    MINION = 'Minion'
    DEMON = 'Demon'


class Character(Enum):
    AMNESIAC = ('amnesiac', CharacterType.TOWNSFOLK, 'Amnesiac')
    ARTIST = ('artist', CharacterType.TOWNSFOLK, 'Artist')
    BALLOONIST = ('balloonist', CharacterType.TOWNSFOLK, 'Balloonist')
    BOUNTY_HUNTER = ('bountyhunter', CharacterType.TOWNSFOLK, 'Bounty Hunter')
    CANNIBAL = ('cannibal', CharacterType.TOWNSFOLK, 'Cannibal')
    CHAMBERMAID = ('chambermaid', CharacterType.TOWNSFOLK, "Chambermaid")
    CHEF = ('chef', CharacterType.TOWNSFOLK, "Chef")
    CHOIRBOY = ('choirboy', CharacterType.TOWNSFOLK, "Choir Boy")
    CLOCKMAKER = ('clockmaker', CharacterType.TOWNSFOLK, "Clockmaker")
    COURTIER = ('courtier', CharacterType.TOWNSFOLK, "Courtier")
    CULTLEADER = ('cultleader', CharacterType.TOWNSFOLK, "Cult Leader")
    DREAMER = ('dreamer', CharacterType.TOWNSFOLK, "Dreamer")
    EMPATH = ('empath', CharacterType.TOWNSFOLK, "Empath")
    EXORCIST = ('exorcist', CharacterType.TOWNSFOLK, "Exorcist")
    FARMER = ('farmer', CharacterType.TOWNSFOLK, "Farmer")
    FISHERMAN = ('fisherman', CharacterType.TOWNSFOLK, "Fisherman")
    FLOWERGIRL = ('flowergirl', CharacterType.TOWNSFOLK, "Flowergirl")
    FOOL = ('fool', CharacterType.TOWNSFOLK, "Fool")
    FORTUNE_TELLER = ('fortuneteller', CharacterType.TOWNSFOLK, "Fortune Teller")
    GAMBLER = ('gambler', CharacterType.TOWNSFOLK, "Gambler")
    GENERAL = ('general', CharacterType.TOWNSFOLK, "General")
    GOSSIP = ('gossip', CharacterType.TOWNSFOLK, "Gossip")
    GRANDMOTHER = ('grandmother', CharacterType.TOWNSFOLK, "Grandmother")
    HUNTSMAN = ('huntsman', CharacterType.TOWNSFOLK, "Huntsman")
    INNKEEPER = ('innkeeper', CharacterType.TOWNSFOLK, "Innkeeper")
    INVESTIGATOR = ('investigator', CharacterType.TOWNSFOLK, "Investigator")
    JUGGLER = ('juggler', CharacterType.TOWNSFOLK, "Juggler")
    KING = ('king', CharacterType.TOWNSFOLK, "King")
    LIBRARIAN = ('librarian', CharacterType.TOWNSFOLK, "Librarian")
    LYCANTHROPE = ('lycanthrope', CharacterType.TOWNSFOLK, "Lycanthrope")
    MAGICIAN = ('magician', CharacterType.TOWNSFOLK, "Magician")
    MATHEMATICIAN = ('mathematician', CharacterType.TOWNSFOLK, "Mathematician")
    MAYOR = ('mayor', CharacterType.TOWNSFOLK, "Mayor")
    MINSTREL = ('minstrel', CharacterType.TOWNSFOLK, "Minstrel")
    MONK = ('monk', CharacterType.TOWNSFOLK, "Monk")
    NOBLE = ('noble', CharacterType.TOWNSFOLK, "Noble")
    ORACLE = ('oracle', CharacterType.TOWNSFOLK, "Oracle")
    PACIFIST = ('pacifist', CharacterType.TOWNSFOLK, "Pacifist")
    PHILOSOPHER = ('philosopher', CharacterType.TOWNSFOLK, "Philosopher")
    PIXIE = ('pixie', CharacterType.TOWNSFOLK, "Pixie")
    POPPY_GROWER = ('poppygrower', CharacterType.TOWNSFOLK, "Poppy Grower")
    PREACHER = ('preacher', CharacterType.TOWNSFOLK, "Preacher")
    PROFESSOR = ('professor', CharacterType.TOWNSFOLK, "Professor")
    RAVENKEEPER = ('ravenkeeper', CharacterType.TOWNSFOLK, "Ravenkeeper")
    SAGE = ('sage', CharacterType.TOWNSFOLK, "Sage")
    SAILOR = ('sailor', CharacterType.TOWNSFOLK, "Sailor")
    SAVANT = ('savant', CharacterType.TOWNSFOLK, "Savant")
    SEAMSTRESS = ('seamstress', CharacterType.TOWNSFOLK, "Seamstress")
    SLAYER = ('slayer', CharacterType.TOWNSFOLK, "Slayer")
    SNAKE_CHARMER = ('snakecharmer', CharacterType.TOWNSFOLK, "Snake Charmer")
    SOLDIER = ('soldier', CharacterType.TOWNSFOLK, "Soldier")
    TEA_LADY = ('tealady', CharacterType.TOWNSFOLK, "Tea Lady")
    TOWN_CRIER = ('towncrier', CharacterType.TOWNSFOLK, "Town Crier")
    UNDERTAKER = ('undertaker', CharacterType.TOWNSFOLK, "Undertaker")
    VIRGIN = ('virgin', CharacterType.TOWNSFOLK, "Virgin")
    WASHERWOMAN = ('washerwoman', CharacterType.TOWNSFOLK, "Washerwoman")
    ACROBAT = ('acrobat', CharacterType.OUTSIDER, "Acrobat")
    BARBER = ('acrobat', CharacterType.OUTSIDER, "Barber")
    BUTLER = ('acrobat', CharacterType.OUTSIDER, "Butler")
    DAMSEL = ('acrobat', CharacterType.OUTSIDER, "Damsel")
    DRUNK = ('acrobat', CharacterType.OUTSIDER, "Drunk")
    GOOD = ('acrobat', CharacterType.OUTSIDER, "Good")
    HERETIC = ('acrobat', CharacterType.OUTSIDER, "Heretic")
    KLUTZ = ('acrobat', CharacterType.OUTSIDER, "Klutz")
    LUNATIC = ('acrobat', CharacterType.OUTSIDER, "Lunatic")
    MOONCHILD = ('acrobat', CharacterType.OUTSIDER, "Moonchild")
    MUTANT = ('acrobat', CharacterType.OUTSIDER, "Mutant")
    POLITICIAN = ('acrobat', CharacterType.OUTSIDER, "Politician")
    RECLUSE = ('acrobat', CharacterType.OUTSIDER, "Recluse")
    SAINT = ('acrobat', CharacterType.OUTSIDER, "Saint")
    SNITCH = ('acrobat', CharacterType.OUTSIDER, "Snitch")
    SWEETHEART = ('acrobat', CharacterType.OUTSIDER, "Sweetheart")
    TINKER = ('acrobat', CharacterType.OUTSIDER, "Tinker")
    ASSASSIN = ('assassin', CharacterType.MINION, "Assassin")
    BARON = ('baron', CharacterType.MINION, "Baron")
    BOOMDANDY = ('boomdandy', CharacterType.MINION, "Boomdandy")
    CERENOVUS = ('cerenovus', CharacterType.MINION, "Cerenovus")
    DEVILS_ADVOCATE = ('devilsadvocate', CharacterType.MINION, "Devil's Advocate")
    EVIL_TWIN = ('eviltwin', CharacterType.MINION, "Evil Twin")
    GOBLIN = ('goblin', CharacterType.MINION, "Goblin")
    GODFATHER = ('godfather', CharacterType.MINION, "Godfather")
    MARIONETTE = ('marionette', CharacterType.MINION, "Marionette")
    MASTERMIND = ('mastermind', CharacterType.MINION, "Mastermind")
    MEPHIT = ('mephit', CharacterType.MINION, "Mephit")
    PIT_HAG = ('pithag', CharacterType.MINION, "Pit Hag")
    POISONER = ('poisoner', CharacterType.MINION, "Poisoner")
    SCARLET_WOMAN = ('scarletwoman', CharacterType.MINION, "Scarlet Woman")
    SPY = ('spy', CharacterType.MINION, "Spy")
    WIDOW = ('widow', CharacterType.MINION, "Widow")
    WITCH = ('witch', CharacterType.MINION, "Witch")
    FANG_GU = ('fanggu', CharacterType.DEMON, "Fang Gu")
    IMP = ('imp', CharacterType.DEMON, "Imp")
    LEGION = ('legion', CharacterType.DEMON, "Legion")
    LEVIATHAN = ('leviathan', CharacterType.DEMON, "Leviathan")
    LIL_MONSTA = ('lilmonsta', CharacterType.DEMON, "Lil' Monsta")
    LLEECH = ('lleech', CharacterType.DEMON, "Lleech")
    NO_DASHII = ('nodashii', CharacterType.DEMON, "No Dashii")
    PO = ('po', CharacterType.DEMON, "Po")
    PUKKA = ('pukka', CharacterType.DEMON, "Pukka")
    SHABALOTH = ('shabaloth', CharacterType.DEMON, "Shabaloth")
    VIGORMORTIS = ('vigormortis', CharacterType.DEMON, "Vigormortis")
    VORTOX = ('vortox', CharacterType.DEMON, "Vortox")
    ZOMBUUL = ('zombuul', CharacterType.DEMON, "Zombuul")

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
