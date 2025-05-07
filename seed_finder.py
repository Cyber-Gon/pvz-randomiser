import random
import copy
from os import cpu_count
import multiprocessing
from time import perf_counter_ns
from collections import Counter

if __name__ == '__main__':
    # https://randomwordgenerator.com/pictionary.php
    # let s ="";
    # document.querySelectorAll('#result li .support-sentence').forEach((e,ind) => {s += '"' + e.innerHTML + '", ' + ((ind+1)%10==0 ? '\n' : '')});
    # console.log(s);
    SEED_FINDER = True
    SEED_ADJECTIVES = list(set(["bloody", "boorish", "awesome", "deafening", "blushing", "wary", "illustrious", "quirky", "highfalutin", "irate", 
    "infamous", "possible", "mighty", "delicate", "draconian", "superficial", "simple", "deeply", "graceful", "needy", 
    "unhappy", "forgetful", "sassy", "cloudy", "goofy", "disgusting", "accidental", "garrulous", "faithful", "enormous", 
    "knowledgeable", "unfair", "broken", "tricky", "dangerous", "lewd", "tart", "hospitable", "traditional", "needless", 
    "practical", "wooden", "fuzzy", "somber", "bawdy", "alleged", "stormy", "impossible", "melted", "helpful",
    "disgusted", "glamorous", "flamboyant", "frequent", "rusty", "dirty", "nasty", "livid", "rural", "live", 
    "curved", "small ", "mute", "masculine", "normal", "paltry", "free", "harmful", "steady", "scented", 
    "cloudy", "thundering", "spry", "detailed", "tense", "vengeful", "busy", "sunny", "uncommon", "melted", 
    "voluminous", "virtuous", "oversized", "joyful", "yawning", "inborn", "impossible", "alive", "old", "upbeat", 
    "rapid", "average", "milky", "frilly", "high", "some", "tragic", "usable", "thoughtful",
    "fruitful", "united", "intentional", "metallic", "sharp", "respectful", "junior", "ready", "evergreen", "stylish", 
    "submissive and breedable", "youthful", "delightful", "steel", "shameless", "mad", "medical", "creepy", "intent", "alert", 
    "unique", "lean", "imperfect", "shady", "jam-packed", "somber", "verifiable", "heavy", "kind", "huge", 
    "insubstantial", "likely", "likable", "slimy", "neighboring", "polished", "supportive", "mushy", "last", "ancient", 
    "meaty", "successful", "corny", "delicious", "light", "nutritious", "tremendous", "thirsty", "high", "writhing", 
    "half", "famous", "polite", "flamboyant", "peppery", "wandering", "third", "unwitting", "grateful", "respectful", 
    "mediocre", "gruesome", "noteworthy", "specific", "warm", "rewarding", "soft", "deep", "helpful", "scrawny", 
    "purring", "punctual", "agreeable", "tasteless", "front", "judicious", "charming", "klutzy", "idolized", "mindless", 
    "sorrowful", "envious", "motionless", "bad", "unusual", "handmade", "creamy", "jolly", "quizzical", "attractive", 
    "first", "rotating", "extra-large", "wordy", "infantile", "elephantine", "exuberant", "happy-go-lucky", "Spanish", "thoughtful", 
    "right", "uninterested", "urban", "strapping", "vast", "tan", "tired", "unconscious", "ashamed", "extraneous", 
    "flamboyant", "unused", "wrong", "shallow", "tender", "fuzzy", "foreign", "live", "passionate", "helpful", 
    "definite", "scattered", "grotesque", "sneaky", "free", "glorious", "noisy", "unimportant", "incompatible", "obvious", 
    "clear-cut", "fancy", "entire", "irritating", "same", "equatorial", "which", "oversized", "violent", "pointless", 
    "ironclad", "starchy", "silver", "pointy", "robust", "oddball", "yellowish", "ill", "worthwhile", "caring",
    "hospitable", "fortunate", "sweaty", "regular", "creative", "outgoing", "stiff", "shiny", "reflecting", "red", 
    "ideal", "foreign", "super-sized", "leading", "unsteady", "orderly", "immaculate", "good", "dual", "unhappy", 
    "charming", "unripe", "scientific", "unimportant", "oily", "gargantuan", "outlandish", "international", "broken", "worrisome", 
    "few", "reckless", "good-natured", "royal", "kaleidoscopic", "violet", "gigantic", "unwelcome", "occasional", "pointless", 
    "disturbed", "hurt", "fine", "unknown", "variable", "nutritious", "solid", "portly", "grimy", "writhing"]))
    SEED_PLAYERS = ["Peter", "Moo", "Bulbasaur"]
    SEED_NOUNS = list(set(["bulldog", "kitten", "mole", "puppy", "penguin", "hedgehog", "rabbit", "stonefish", "cub", "reindeer", 
    "zebra", "saber-tooth tiger", "octopus", "guppy", "warthog", "shrimp", "stallion", "wolf", "red panda", "puffin", 
    "camel", "mallard", "housecat", "inchworm", "trout", "koala", "meerkat", "ram", "hornet", "pigeon", 
    "crocodile", "doe", "hen", "alpaca", "beaver", "daddy longlegs", "dingo", "turtle", "komodo dragon", "eagle", 
    "goose", "ox", "ferret", "owl", "hyena", "dog", "fox", "panther", "bear", "whale",
    "population", "doctor", "page", "stepmom", "leader", "designer", "child", "monk", "overlord", "despot", 
    "rock star", "chemist", "navigator", "computer programmer", "guy", "teenager", "dictator", "sheik", "saxophonist", "enemy", 
    "half-sister", "disc jockey", "clan", "sultan", "harpist", "scholar", "collaborator", "boss", "people", "garbage worker", 
    "soldier", "preteen", "quadruplets", "cartographer", "bishop", "ally", "heir", "scout", "father-in-law", "attorney", 
    "great-grandfather", "brigadier general", "cousin", "nobility", "geeks", "principal", "oboist", "representative", "customer", "grandchild",
    "emperor", "son", "stepmom", "inhabitant", "vice-president", "pilot", "teacher", "pop star", "researcher", "athletes", 
    "overlord", "accountant", "rock star", "twins", "offspring", "navigator", "guy", "peer", "buddy", "warrior", 
    "duke", "half-sister", "disciplinarian", "cartoonist", "knight", "stockbroker", "author", "son-in-law", "cellist", "electrician", 
    "scientist", "pawnbroker", "magician", "technician", "samurai", "loner", "ambassador", "stepchild", "highway patrol", "sister-in-law", 
    "cop", "half-brother", "children", "retailer", "quintuplets", "pediatrician", "physicist", "adolescent", "marketer", "sword swallower",
    "teacher", "student", "child", "entertainer", "lass", "cardiologist", "freshman", "yodeler", "kid", "offspring", 
    "landlord", "man", "saxophonist", "librarian", "pope", "butcher", "priest", "tyrant", "extended family", "peasant", 
    "contractor", "handyman", "jeweler", "gymnast", "watchmaker", "blood relative", "private detective", "cohort", "officer", "cook", 
    "bishop", "falconer", "sister", "ambassador", "pathologist", "knife thrower", "professor", "doppelganger", "weaver", "surgeon", 
    "general", "chum", "colonel", "mechanic", "maiden", "parent", "adult", "principal", "adolescent", "queen", 
    "Bahamas", "Pakistan", "South Pole", "Mississippi River", "Bangladesh", "Virgin Islands", "Juneau", "Iraq", "North Dakota", "Fiji", 
    "Australia", "American Samoa", "Flagstaff", "Mediterranean Sea", "Ohio", "Sahara Desert", "Arkansas", "Boston", "United Kingdom", "Los Angeles", 
    "Rome", "Afghanistan", "Vermont", "Grand Canyon", "Carson City", "Louisiana", "California", "Miami", "Iowa", "Nashville", 
    "Ayers Rock", "London", "Virginia", "Uganda", "Uruguay", "Argentina", "Pennsylvania", "San Francisco", "Illinois", 
    "Italy", "Sacramento", "Philippines", "China", "Oregon", "Canada", "Montana", "Finland", "Great Barrier Reef", "Indian Ocean",
    "father-in-law", "dad", "shoe", "fake flowers", "emery board", "kitchen knife set", "jeans", "basement", "shower curtain", "hammock", 
    "front lawn", "dry erase board", "dress shirt", "notepad", "car keys", "bathroom scale", "balloon", "cord", "ice cube tray", "novel", 
    "garden", "photograph", "gutter", "wreath", "sticker", "downstairs", "fork", "drawer", "blush", "tissue paper", 
    "ice chest", "mirror", "rocking chair", "vacuum cleaner", "lace", "scuff mark", "children", "candle", "picnic table", "drain", 
    "lawn", "front door", "hairbrush", "eaves", "basket", "snooze button", "closet", "lights", "penny", "scrapbook",
    "sloth", "snail", "donkey", "turtle", "penguin", "fox", "fly", "zebra", "frog", "ladybug", 
    "llama", "rat", "parrot", "seagull", "walrus", "otter", "anteater", "dog", "cockroach", "ant", 
    "squirrel", "pelican", "kangaroo", "raccoon", "hamster", "bat", "owl", "porcupine", "pony", "iguana", 
    "chicken", "rabbit", "sea turtle", "polar bear", "elephant", "rooster", "mole", "jellyfish", "spider", "cow", 
    "moose", "ox", "caterpillar", "chameleon", "dolphin", "mosquito", "reindeer", "bear", "monkey", "gorilla",
    "chia seed", "talon", "brook", "cave", "prickly pear", "bird", "funnel cloud", "bird of prey", "wadi", "cloudy", 
    "grassland", "granite", "feather", "hill", "flora", "tree trunk", "ridge", "violet", "cold-blooded", "diamond", 
    "storm surge", "hurricane", "sea trench", "gale", "cedar tree", "tardigrade", "holly tree", "egg", "star", "winter", 
    "peony", "marshland", "rain forest", "strait", "dew", "cone", "grass", "exoskeleton", "mesa", "reptile", 
    "sand dune", "canyon", "cork oak", "garden", "biome", "wildfire", "cenote", "scrub", "peninsula", "metamorphosis", ]))
    SEED_VERBS = list(set(["breeds", "plays with", "reminds", "divides", "examines", "inhibits", "reviews", "satisfies", "analyses", 
    "gives", "handles", "twists", "matters for",  "reacts to", "reproduces", "enjoys", "kisses", "introduces", 
    "taxes", "calculates", "rises", "instructs", "precedes", "steals", "constitutes", "expresses", "exceeds", "fetches", 
    "tackles", "flings", "shares with", "chats with", "affects", "begins", 
    "stares on", "judges", "condemns", "senses", "repairs", "raises", "maintains", "abolishes",
    "attaches", "comments on", "jests to", "identifies", "licenses", 
    "cracks", "befriends", "tips", "objects to", "pick ups", "surprises", "ticks", "milks", 
    "protects", "abandons", "guesses", "doubts", "quotes", 
    "chokes", "plugs", "follows", "evaporates", "tames", "carries", "rings", "blinds", 
    "finds", "scorches", "makes", "recites", "deceives", "preserves",
    "enjoys", "becomes", "spells", "hangs", "declares", 
    "obeys", "judges", "pays to", "tackles", "arrives with", "sneaks to", "needs", 
    "contends", "zips", "bites", "irritates", "debates", "berates", 
    "drags", "learns", "guarantees", "appears with", "pleads to", "charges", "stuns", "presents", 
    "collects", "feeds", "tracks", "points to", "sends", "preserves",
    "spares", "doubles", "watches", "shoots", "calculates", "delivers", "immigrates to", "fears", 
    "reveals", "protects", "sees", "hails", "loses to", 
    "sails to", "bombs", "races with", "directs", "loves", "avoids", "tests", 
    "reflects", "enchants", "speaks to", "faces", "evaporates", "rings", "builds", 
    "beheads", "finds", "excites", "relates to", "entertains", ]))

    seed_generator_rng = random.Random()

    def next_seed():
        return SEED_ADJECTIVES[seed_generator_rng.randint(0,len(SEED_ADJECTIVES)-1)] + " " + SEED_PLAYERS[seed_generator_rng.randint(0,len(SEED_PLAYERS)-1)] + " " + \
            SEED_VERBS[seed_generator_rng.randint(0,len(SEED_VERBS)-1)] + " the " + SEED_NOUNS[seed_generator_rng.randint(0,len(SEED_NOUNS)-1)]

class MockSetting:
    def __init__(self, value):
        self.value = value
    def get(self):
        return self.value
    def __bool__(self):
        return bool(self.value)

challengeMode    = MockSetting(value=True)
shopless         = MockSetting(value=False)
noRestrictions   = MockSetting(value=True)
noAutoSlots      = MockSetting(value=True)
imitater         = MockSetting(value=False)
randomisePlants  = MockSetting(value=True)
seeded           = MockSetting(value=False)
upgradeRewards   = MockSetting(value=True)
randomWeights    = MockSetting(value=True)
renderWeights    = MockSetting(value=False)
randomWavePoints = MockSetting(value="EXTREME")
renderWavePoints = MockSetting(value=False)
saved            = MockSetting(value=False)
startingWave     = MockSetting(value="Instant")
randomCost       = MockSetting(value=True)
randomCooldowns  = MockSetting(value=True)
costTextToggle   = MockSetting(value=True)
cooldownColoring = MockSetting(value="False")
randomZombies    = MockSetting(value=True)
randomConveyors  = MockSetting(value="It's raining seeds")
enableDave       = MockSetting(value="False")
davePlantsCount  = MockSetting(value="3")
randomVarsCatZombieHealth = MockSetting(value="Very Strong")
randomVarsCatFireRate = MockSetting(value="Very Strong")
limitPreviews    = MockSetting(value=False)
gamemode         = MockSetting(value="adventure")
randomWaveCount  = MockSetting(value=True)
randomWorld      = MockSetting(value=True)
randomWorldChance= MockSetting(value=100)
randomShit       = MockSetting(value=True)
randomSound      = MockSetting(value=True)
randomSoundChance= MockSetting(value=3)

# Mock
def WriteMemory(type, data, *address):
    return

wavePointArray=[1, 1, 2, 2, 4, 2, 4, 7, 5, 0, 1, 3, 7, 3, 3, 3, 2, 4, 4, 4, 3, 4, 5, 10, 10, 0, 1, 4, 3, 3, 3, 7, 10]

zombies_allowed = [
		[
			1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
			1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
			1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
			1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
			1, 1, 1, 1, 1, 1, 1, 1, 1, 1,],
		    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
			1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
			1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
			1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
			1, 1, 1, 1, 1, 1, 1, 1, 1, 1,],
		    [0, 0, 1, 1, 1, 1, 1, 1, 1, 1,
			0, 1, 1, 1, 1, 1, 1, 1, 1, 1,
			1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
			1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
			1, 1, 1, 1, 1, 1, 1, 1, 1, 1,],
			[0, 0, 0, 0, 0, 1, 1, 0, 1, 1,
			0, 0, 0, 1, 1, 0, 0, 0, 0, 0,
			0, 0, 0, 1, 0, 0, 0, 0, 1, 0,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 1, 0, 0, 0, 0, 0, 0, 0, 0,],
			[0, 0, 0, 0, 0, 0, 0, 1, 1, 1,
			0, 1, 0, 0, 1, 0, 0, 0, 0, 0,
			0, 1, 0, 1, 0, 0, 1, 0, 1, 1,
			0, 0, 0, 0, 0, 0, 1, 0, 1, 1,
			0, 1, 0, 0, 1, 0, 0, 0, 1, 1,],
			[0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			1, 1, 0, 0, 1, 0, 0, 0, 0, 0,
			0, 1, 0, 1, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
			[0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 1, 1, 0, 0, 1, 0, 1, 1,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
			[0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 1, 1, 0, 0, 1,
			0, 1, 0, 0, 1, 0, 0, 0, 0, 0,
			0, 1, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 1, 0, 0, 0, 0, 0, 0,],
			[0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 0, 0, 1, 1, 1,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
			[0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 0, 0, 1, 1, 1,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
	        [],
			[0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 1, 1, 1, 0, 1, 0, 0, 1,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
			[0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 1, 1, 0, 1, 1,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
			[0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 1, 1, 0, 1, 1,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
			[0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 0, 0, 1, 1, 1,
			0, 0, 0, 1, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
			[0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			1, 1, 0, 0, 0, 0, 1, 0, 0, 1,
			0, 0, 0, 0, 0, 0, 0, 0, 1, 1,],
			[0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 1, 1, 0, 0, 0, 0, 1, 1,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
			[0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 1, 1, 0, 0, 1,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
			[0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 0, 0, 1, 1, 1,
			0, 0, 0, 1, 0, 0, 0, 0, 0, 0,],
            [],
			[0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			1, 1, 0, 0, 0, 0, 1, 0, 1, 1,],
			[0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 1, 1, 1, 0, 1, 0, 1, 1,],
			[0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 1, 1, 0, 1, 1,],
			[0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 0, 0, 1, 1, 1,],
			[0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 0, 0, 1, 1, 1,],
            [], [], [], [], [], [], [], []
]

def is_zombie_allowed(zombie, level):
    if not zombies_allowed[zombie]:
        return False
    return zombies_allowed[zombie][level-1]

zombies=[['Basic', 1, 4000, 1, 1], ['Flag (ignore)', 1, 0, 1, 1], ['Cone', 3, 4000, 2, 1], ['Vaulter', 6, 2000, 2, 5], ['Bucket', 8, 3000, 4, 1], ['Newspaper', 11, 1000, 2, 1], ['Screen-Door', 13, 3500, 4, 5], ['Footballer', 16, 2000, 7, 5], ['Dancer', 18, 1000, 5, 5], ['Backup (ignore)', 18, 0, 1, 1], ['Ducky-Tube (ignore)', 21, 0, 1, 5], ['Snorkel', 23, 2000, 3, 10], ['Zomboni', 26, 2000, 7, 10], ['Bobsled', 26, 1500, 3, 10], ['Dolphin', 28, 1500, 3, 10], ['Jack', 31, 1000, 3, 10], ['Balloon', 33, 2000, 2, 10], ['Digger', 36, 1000, 4, 10], ['Pogo', 38, 1000, 4, 10], ['Yeti', 40, 1, 4, 1], ['Bungee', 41, 1000, 3, 10], ['Ladder', 43, 1000, 4, 10], ['Catapult', 46, 1500, 5, 10], ['Gargantuar', 48, 1500, 10, 15], ['Imp', 1, 0, 10, 1], ['Zomboss', 50, 0, 10, 1], ['Peashooter', 99, 4000, 1, 1], ['Wall-Nut', 99, 3000, 4, 1], ['Jalapeno', 99, 1000, 3, 10], ['Gatling Pea', 99, 2000, 3, 10], ['Squash', 99, 2000, 3, 10], ['Tall Nut', 99, 2000, 7, 10], ['Giga Gargantuar', 48, 6000, 10, 15]]
plants=[[100, 750], [50, 750], [150, 5000], [50, 3000], [25, 3000], [175, 750], [150, 750], [200, 750], [0, 750], [25, 750], [75, 750], [75, 750], [75, 3000], [25, 750], [75, 5000], [125, 5000], [25, 750], [50, 3000], [325, 750], [25, 3000], [125, 5000], [100, 750], [175, 750], [125, 3000], [0, 3000], [25, 3000], [125, 750], [100, 750], [125, 750], [125, 750], [125, 3000], [100, 750], [100, 750], [25, 750], [100, 750], [75, 750], [50, 750], [100, 750], [50, 3000], [300, 750], [250, 5000], [150, 5000], [150, 5000], [225, 5000], [200, 5000], [50, 5000], [125, 5000], [500, 5000]]
bytes_per_plant_string = 512 # should be a power of 2
bytes_per_zombie_string = 512 # should be a power of 2
bytes_per_game_string = 128 # should be a power of 2
n_of_plant_strings = 50 # 49 normal plants + 1 dummy string for other unusual plants
n_of_zombie_strings = 33
n_of_game_strings = 24 # more than 24 won't fit on screen

# ONE_FLAGS = [1,2,3,4,5,6,8,11,13,15,16,18,21,31,33,35,36,38,41]
# THREE_FLAGS = [24,27,29,30,40,44,47,49]
strong_zombies = [4,6,7,12,21,23,31,32]

wavepoints_container = { index: element for index,element in enumerate([[x[3]] for x in zombies][:n_of_zombie_strings]) }
zombie_weight_container = { index: element for index,element in enumerate([[x[2]] for x in zombies][:n_of_zombie_strings]) }


def getAvailableStages(plants, used_levels=[], wavecount_per_level=None, level_worlds=None, snorkel_levels=None, dolphin_levels=None, level_with_5_pots=0):
    global noRestrictions, challengeMode
    # buckets, screendoors, ladders, pogos, catapults:
    buckets_are_present = [8, 9, 12, 13, 14, 17, 19, 22, 24, 27, 29, 37, 38, 39, 42, 43, 44, 46, 47, 49]
    playable_non_pot = [2, 3, 4, 6, 7, 11, 13, 14, 18, 19, 21, 23, 28, 31, 33, 34, 41, 43, 46, 47]
    # footballers, zambonis, catapults, gargs:
    footballers_are_present = [16, 17, 22, 26, 27, 29, 32, 44, 46, 47, 48, 49]
    if len(used_levels) == 0:
        level_set = {1}
    elif noRestrictions.get():
        level_set = {
        2,  3,  4,  5,  6,  7,  8,  9,  10,
        11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
        21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
        31, 32, 33, 34, 35, 36, 37, 38, 39, 40,
        41, 42, 43, 44, 45, 46, 47, 48, 49, 50 }
    else:
        level_set = {5, 10, 15, 20, 25, 30, 35, 40, 45, 50} # conveyors
        plant_set = set(plants)
        
        tough_check   = len(plant_set & {2, 6, 7, 15, 17, 20, 29, 31, 35, 39}) #cherry bomb, chomper, repeater, doom, squash, jalapeno, starfruit, magnet, coffee bean, melon pult
        
        if challengeMode.get():
            tough_check = 9999
        
        has_puff              = 8  in plant_set
        has_lily              = 16 in plant_set
        has_pool_shooter      = 29 in plant_set or 18 in plant_set
        has_seapeater         = (24 in plant_set or 19 in plant_set) and has_pool_shooter #threepeater or starfruit + sea shroom or kelp
        has_fog_plants        = has_puff and (has_lily or 24 in plant_set)
        has_pot               = 33 in plant_set
        has_roof_plant        = 32 in plant_set or 39 in plant_set or has_pot

        # generalized tough check rules:
        #   1 flag: no check
        #   2 flag without bucket-type zombies: no check; but fog/roof-night level: check >= 3
        #   2 flag and bucket-type zombies are present: check >= 3; (don't care about football-type zombies); fog/roof-night level: check >= 5
        #   3 flag without bucket or football type of zombies: check >= 3; fog/roof-night level: check >= 4
        #   3 flag and either bucket or football type of zombies are present: check >= 4;  fog/roof-night level: check >= 5
        #   3 flag and both bucket and football type of zombies are present: check >= 5;  fog/roof-night level: check >= 5
        #   4 flag without bucket or football type of zombies: check >= 4; fog/roof-night level: check >= 5
        #   4 flag with either bucket or football type of zombies: check >= 5
        #   5 flag: check >= 6

        def tough_check_test(level):
            one_flag = wavecount_per_level[level] < 16
            two_flag = 16 <= wavecount_per_level[level] < 28
            three_flag = 28 <= wavecount_per_level[level] < 40
            four_flag = 40 <= wavecount_per_level[level] < 50
            if one_flag:
                requirement = 0
            elif two_flag and level not in buckets_are_present:
                requirement = 0
                if level in fog_levels or level in roof_night_levels:
                    requirement = 2 # 1 will be added later
            elif two_flag and level in buckets_are_present:
                requirement = 3
                if level in fog_levels or level in roof_night_levels:
                    requirement = 4 # 1 will be added later
            elif three_flag and level not in buckets_are_present and level not in footballers_are_present:
                requirement = 3
            elif three_flag and level in buckets_are_present and level in footballers_are_present:
                requirement = 5
            elif three_flag and (level in buckets_are_present or level in footballers_are_present):
                requirement = 4
            elif four_flag and (level not in buckets_are_present and level not in footballers_are_present):
                requirement = 4
            elif four_flag:
                requirement = 5
            else:
                requirement = 6
            if (level in fog_levels or level in roof_night_levels) and requirement < 5:
                requirement += 1
            return tough_check >= requirement

        def balloon_test(level):
            if level not in [33, 34, 39]:
                return True
            if wavecount_per_level[level] < 11 and startingWave.get() != "Instant":
                return True
            has_doom = 15 in plant_set and (35 in plant_set or level_worlds[level] in [1,3,5])
            balloon_check = len(plant_set & {2, 20}) + 2 * len(plant_set & {26, 27}) + int(has_doom)
            unreliable_cactus = balloon_check == 2 and 26 in plant_set and 16 not in plant_set
            # if cactus is the only counter without lily, check for pool/fog
            result = balloon_check >= 2 and (level_worlds[level] not in [2,3] or not unreliable_cactus)
            return result

        # day levels: nothing special
        for l in day_levels.difference({1}):
            if tough_check_test(l) and balloon_test(l):
                level_set.add(l)
                
        # night levels: puff required
        if has_puff:
            for l in night_levels:
                if tough_check_test(l) and balloon_test(l):
                    level_set.add(l)

        # pool levels:
        #   if no snorkels and dolphins, either lily or has_pool_shooter is enough
        #   if has snorkel, lily is required
        #   if has dolphin, either lily or has_seapeater is enough - but more than 30 waves require lily
        #   snorkel + dolphin require lily
        for l in pool_levels:
            a_lot_of_flags = wavecount_per_level[l] > 30
            snorkel = l in snorkel_levels
            dolphin = l in dolphin_levels
            if dolphin and not has_lily and a_lot_of_flags:
                continue
            aquatic_zombie_check_passed = (not snorkel and not dolphin and (has_lily or has_pool_shooter)) \
                or (snorkel and not dolphin and has_lily) or (dolphin and not snorkel and (has_lily or has_seapeater)) \
                or (snorkel and dolphin and has_lily)
            if aquatic_zombie_check_passed and tough_check_test(l) and balloon_test(l):
                level_set.add(l)
        
        # fog levels: 
        #   1-flag requires has_fog_plants
        #   2-flag requires has_puff and (has_lily or has_seapeater) instead
        #   3-flag or more requires has_puff and has_lily instead
        if has_puff:
            for l in fog_levels:
                one_flag = wavecount_per_level[l] < 16
                two_flag = 16 <= wavecount_per_level[l] < 28
                a_lot_of_flags = 28 <= wavecount_per_level[l]
                plant_test = (one_flag and has_fog_plants) \
                    or (two_flag and has_puff and (has_lily or has_seapeater)) \
                    or (a_lot_of_flags and has_puff and has_lily)
                snorkel = l in snorkel_levels
                dolphin = l in dolphin_levels
                aquatic_zombie_check_passed = (not snorkel and not dolphin and (has_lily or has_pool_shooter)) \
                    or (snorkel and not dolphin and has_lily) or (dolphin and not snorkel and (has_lily or has_seapeater)) \
                    or (snorkel and dolphin and has_lily)
                if plant_test and aquatic_zombie_check_passed and balloon_test(l) and tough_check_test(l):
                    level_set.add(l)
        
        # Roof levels:
        # some levels require pot and catapults are enough for some (if < 3 flags)
        # digger levels not allowed if no pot
        # special case for 5-1 (or random level with 5 pots if it's 1 flag)
        for l in roof_levels:
            one_flag = wavecount_per_level[l] < 16
            a_lot_of_flags = 24 <= wavecount_per_level[l]
            plant_test = has_pot or (l in playable_non_pot and not a_lot_of_flags and has_roof_plant)
            digger_test = has_pot or l not in [36,37]
            five_one_special_test = l == level_with_5_pots and one_flag and (has_roof_plant or len(used_levels) > 10)
            if ((plant_test and tough_check_test(l)) or five_one_special_test) and balloon_test(l) and digger_test:
                level_set.add(l)

        # Roof night levels:
        # puff and pot required + sunshroom or catapult
        if has_puff and has_pot and (9 in plant_set or has_roof_plant):
            for l in roof_night_levels:
                if tough_check_test(l) and balloon_test(l):
                    level_set.add(l)

    for l in used_levels:
        if l in level_set:
            level_set.remove(l)
    return level_set


def randomiseLevelsAndPlants(seed, level_worlds, wavecount_per_level, snorkel_levels, dolphin_levels, level_with_5_pots):
    global noRestrictions, challengeMode
    random.seed(seed)
    
    plants = [1]
    levels = [1]
    unused_plants   = [i for i in range(2,40)]
    if challengeMode.get() or noRestrictions.get():
        level_plants    = [(-1,1.0) for i in range(0,51)]
    else:
        level_plants    = [(-1,0.8) for i in range(0,51)]
    level_plants[0] =  (0, 0.0)
    level_plants[1] =  (1, 0.0)
    if not noRestrictions.get():
        while 1: #select key plants for only levels you could have unlocked by that point
            current_available = len(getAvailableStages(plants,levels, wavecount_per_level, level_worlds, snorkel_levels, dolphin_levels, level_with_5_pots))
            plants.append(0)
            key_plants   = []
            key_weights  = []
            key_weights2 = []
            for i in unused_plants:
                plants[-1] = i
                if current_available < len(getAvailableStages(plants,levels, wavecount_per_level, level_worlds, snorkel_levels, dolphin_levels, level_with_5_pots)):
                    key_plants.append(i)
                    key_weights.append(1.0)
                    key_weights2.append(3.0)
                elif i in {2, 6, 7, 15, 17, 20, 29, 31, 35, 39}:
                    key_plants.append(i)
                    key_weights.append(0.23)
                    if challengeMode.get():
                        key_weights2.append(1.0)
                    else:
                        key_weights2.append(1.3)
            
            if not key_plants:
                break
            
            chosen_plant     = random.choices(key_plants, weights=key_weights)[0]
            chosen_weight    = key_weights2[key_plants.index(chosen_plant)]
            plants[-1]       = chosen_plant
            available_levels = sorted(list(getAvailableStages(plants[0:-2], levels, wavecount_per_level, level_worlds, snorkel_levels, dolphin_levels, level_with_5_pots)))
            chosen_level     = random.choice(available_levels)
            unused_plants.remove(chosen_plant)
            
            levels.append(chosen_level)
            level_plants[chosen_level] = (chosen_plant,chosen_weight)
        
    for i in unused_plants:
        available_levels = sorted(list(getAvailableStages(plants, levels, wavecount_per_level, level_worlds, snorkel_levels, dolphin_levels, level_with_5_pots))) #should return all levels without plants assigned
        chosen_level     = random.choice(available_levels)
        
        levels.append(chosen_level)
        if i==9:
            level_plants[chosen_level] = (i,2.0)
        else:
            level_plants[chosen_level] = (i,1.0)
    
    levels = [1]
    plants = [1]
    world_weights = [0.93, 1.0, 1.0, 1.0, 1.0, 0.8]
    for i in range(1,50):
        available_levels = sorted(list(getAvailableStages(plants, levels, wavecount_per_level, level_worlds, snorkel_levels, dolphin_levels, level_with_5_pots)))
        chosen_level     = random.choices(available_levels, weights=[level_plants[l][1]*world_weights[level_worlds[l]] for l in available_levels])[0]
        world_weights[level_worlds[chosen_level]] -= 0.07 * 10 / world_counts[level_worlds[chosen_level]]
        levels.append(chosen_level)
        plants.append(level_plants[chosen_level][0])
    
    level_plants = [i[0] for i in level_plants]
    return levels, level_plants


def generateZombies(seed, levels, level_plants, level_worlds, wavecount_per_level):
    zombies_rng = random.Random(seed+'zombies')
    zombiesToRandomise=[[]]
    plantsInOrder=[]
    for i in range(0, len(levels)):
        plantsInOrder.append(level_plants[levels[i]])
    for i in range(1, len(levels)):
        level = levels[i]
        if level==50 or level==15 or level==35:
            zombiesToRandomise.append([]) # no rando on those levels
            continue
        current_plants = set(plantsInOrder[0:i])
        has_lily              = 16 in current_plants
        has_pool_shooter      = 29 in current_plants or 18 in current_plants
        has_seapeater         = (24 in current_plants or 19 in current_plants) and has_pool_shooter #threepeater or starfruit + sea shroom or kelp
        has_pot               = 33 in current_plants
        has_doom              = 15 in current_plants and (35 in current_plants or level_worlds[level] in [1,3,5])
        has_instant           = 2 in current_plants or 17 in current_plants or 20 in current_plants or has_doom
        balloon_check = len(current_plants & {2, 20}) + 2 * len(current_plants & {26, 27}) + int(has_doom)
        unreliable_cactus = balloon_check == 2 and 26 in current_plants and 16 not in current_plants
        # if cactus is the only counter, check for pool/fog
        balloon_test = balloon_check >= 2 and (level_worlds[level] not in [2,3] or not unreliable_cactus)
        currentZombies=[]
        for j in range(2, 33):
            if level == 5: # let's not make conveyor basically impossible to beat even in no restriction
                if j == 11 or j == 14:
                    continue
            if j==9 or j==10 or j==24 or j==25:
                continue
            elif zombies_rng.randint(0, 11) != 0:
                continue
            elif (j==11 or j==14) and level_worlds not in [2,3]:
                continue
            elif zombies[j][1]==level:
                continue
            elif level==45 and j in [11, 12, 13, 14, 16, 17, 18, 20, 22, 23, 32]:
                continue
            elif noRestrictions.get():
                currentZombies.append(j)
            elif j==11 and not has_lily:
                continue
            elif j==14 and not (has_lily or has_seapeater):
                continue
            elif j==14 and wavecount_per_level[level] >= 30 and not has_lily:
                continue
            elif j==16 and not balloon_test:
                continue
            elif j==16 and level % 5 == 0:
                continue
            elif j==17 and level_worlds[level] in [4,5] and not has_pot:
                continue
            # gargs and giga-gargs are excluded from extremenly long levels + can get removed from 5-9 in such case
            elif j==23 and (not has_instant or (wavecount_per_level[level] > 45 and level not in [48,49])):
                continue
            elif j==32 and (not has_instant or wavecount_per_level[level] > 45):
                continue
            else:
                if j==32:
                    if not zombies_rng.randint(0, 6):
                        currentZombies.append(j)
                else:
                    currentZombies.append(j)
        zombiesToRandomise.append(currentZombies)
    return zombiesToRandomise


def at_least(n, gen):
    s = 0
    for x in gen:
        s += x
        if (s>=n):
            return True
    return False


def n_of_strong_zombies(generated_zombies, level, index_of_level):
    return len([z for z in strong_zombies if zombie_on_level(z, generated_zombies, level, index_of_level)])


def zombie_on_level(zombie, generated_zombies, level, index_of_level):
    return (is_zombie_allowed(zombie, level) and zombie not in generated_zombies[index_of_level])\
        or (not is_zombie_allowed(zombie, level) and zombie in generated_zombies[index_of_level])


# all zombies are considered safe on conveyor levels
def zombie_likely_to_spawn(zombie, generated_zombies, level, index_of_level, seeded_wavepoints, seeded_weights, flags_per_level):
    if level % 5 == 0:
        return False
    if not zombie_on_level(zombie, generated_zombies, level, index_of_level):
        return False
    weight = seeded_weights[index_of_level][zombie][0]
    wavepoints = seeded_wavepoints[index_of_level][zombie][0]
    spawns_est = 0
    for i in range(3, flags_per_level[level] * 10 + 1, 3):
        if wavepoints > i / 3:
            continue
        total_weight = sum(seeded_weights[index_of_level][z][0] for z in range(33) if seeded_wavepoints[index_of_level][z][0] <= i / 3 \
                           and zombie_on_level(z, generated_zombies, level, index_of_level))
        spawns_est += i / 3 / wavepoints * 3 * (weight / total_weight) # rough estimate, not exactly correct
    return spawns_est > 3 * flags_per_level[level]**1.3


def zombie_spammable(zombie, generated_zombies, level, index_of_level, seeded_wavepoints, seeded_weights, flags_per_level):
    if level % 5 == 0:
        return False
    if not zombie_on_level(zombie, generated_zombies, level, index_of_level):
        return False
    weight = seeded_weights[index_of_level][zombie][0]
    wavepoints = seeded_wavepoints[index_of_level][zombie][0]
    spawns_est = 0
    for i in range(3, flags_per_level[level] * 10 + 1, 3):
        if wavepoints > i / 3:
            continue
        total_weight = sum(seeded_weights[index_of_level][z][0] for z in range(33) if seeded_wavepoints[index_of_level][z][0] <= i / 3 \
                           and zombie_on_level(z, generated_zombies, level, index_of_level))
        spawns_est += i / 3 / wavepoints * 3 * (weight / total_weight) # rough estimate, not exactly correct
    return spawns_est > 4 * flags_per_level[level]**1.4


def can_spawn_only_at_level_end(zombie, generated_zombies, level, index_of_level, seeded_wavepoints, waves_per_level):
    if level % 5 == 0:
        return True
    if not zombie_on_level(zombie, generated_zombies, level, index_of_level):
        return True
    wavepoints = seeded_wavepoints[index_of_level][zombie][0]
    max_wavepoints = waves_per_level[level] // 3 - 1
    return wavepoints > max_wavepoints


def is_dangerous_night_level(generated_zombies, level, index_of_level, seeded_wavepoints, seeded_weights, level_worlds, flags_per_level):
    if level % 5 == 0 or level_worlds[level] not in [1, 5] or flags_per_level[level] == 1:
        return False
    count = 0
    for z in strong_zombies:
        if zombie_spammable(z, generated_zombies, level, index_of_level, seeded_wavepoints, seeded_weights, flags_per_level):
            return True
        if zombie_likely_to_spawn(z, generated_zombies, level, index_of_level, seeded_wavepoints, seeded_weights, flags_per_level):
            count += 1
            if count == 3:
                return True
    return False


def is_dangerous_fog_level(generated_zombies, level, index_of_level, seeded_wavepoints, seeded_weights, level_worlds, flags_per_level):
    if level % 5 == 0 or level_worlds[level] != 3 or flags_per_level[level] == 1:
        return False
    count = 0
    for z in strong_zombies:
        if zombie_spammable(z, generated_zombies, level, index_of_level, seeded_wavepoints, seeded_weights, flags_per_level):
            return True
        if zombie_likely_to_spawn(z, generated_zombies, level, index_of_level, seeded_wavepoints, seeded_weights, flags_per_level):
            count += 1
            if count == 2:
                return True
    return False


# represents levels beatable with starfruit/threepeater
def is_pool_level_passable_without_aquatic_plants(generated_zombies, level, index_of_level, seeded_wavepoints, seeded_weights, level_worlds, flags_per_level, waves_per_level):
    if level % 5 == 0 or level_worlds[level] not in [2,3]:
        return True
    if flags_per_level[level] > 2 or (level_worlds[level] == 3 and flags_per_level[level] > 1):
        return False
    # 2 flag pools or 1 flag fog remaining
    return can_spawn_only_at_level_end(11, generated_zombies, level, index_of_level, seeded_wavepoints, waves_per_level) \
        and can_spawn_only_at_level_end(14, generated_zombies, level, index_of_level, seeded_wavepoints, waves_per_level) \
        and not zombie_likely_to_spawn(4, generated_zombies, level, index_of_level, seeded_wavepoints, seeded_weights, flags_per_level) \
        and not zombie_likely_to_spawn(31, generated_zombies, level, index_of_level, seeded_wavepoints, seeded_weights, flags_per_level)


def pool_requiring_lily(generated_zombies, level, index_of_level, seeded_wavepoints, seeded_weights, level_worlds, flags_per_level):
    if level % 5 == 0 or level_worlds[level] not in [2,3]:
        return False
    if flags_per_level[level] > 2:
        return True
    return zombie_spammable(11, generated_zombies, level, index_of_level, seeded_wavepoints, seeded_weights, flags_per_level) \
        or zombie_spammable(14, generated_zombies, level, index_of_level, seeded_wavepoints, seeded_weights, flags_per_level) \
        or (zombie_likely_to_spawn(11, generated_zombies, level, index_of_level, seeded_wavepoints, seeded_weights, flags_per_level) \
            and zombie_likely_to_spawn(14, generated_zombies, level, index_of_level, seeded_wavepoints, seeded_weights, flags_per_level))


def roof_requiring_pot(generated_zombies, level, index_of_level, seeded_wavepoints, seeded_weights, insta_levels, level_worlds, flags_per_level, waves_per_level):
    if level % 5 == 0 or level_worlds[level] < 4:
        return False
    if flags_per_level[level] > 3:
        return True
    if any(not can_spawn_only_at_level_end(z, generated_zombies, level, index_of_level, seeded_wavepoints, waves_per_level) for z in [23,28,32]):
        return True
    if flags_per_level[level] == 1:
        return False
    enough_instas = sum(zombie_likely_to_spawn(z, generated_zombies, level, index_of_level, seeded_wavepoints, seeded_weights, flags_per_level) \
        + zombie_spammable(z, generated_zombies, level, index_of_level, seeded_wavepoints, seeded_weights, flags_per_level)
        for z in range(33) if (z==28 or z==18 or z in strong_zombies)) - 1
    return flags_per_level[level] == 3 and n_of_instas_by_level(insta_levels, index_of_level) == 0
    return False


def balloon_requires_lily_or_blover(generated_zombies, level, index_of_level, seeded_wavepoints, seeded_weights, level_worlds, flags_per_level):
    if level % 5 == 0 or level_worlds[level] not in [2,3]:
        return False
    if flags_per_level[level] > 1 and zombie_likely_to_spawn(16, generated_zombies, level, index_of_level, seeded_wavepoints, seeded_weights, flags_per_level):
        return True
    if flags_per_level[level] == 1 and zombie_spammable(16, generated_zombies, level, index_of_level, seeded_wavepoints, seeded_weights, flags_per_level):
        return True
    return False


def n_of_instas_by_level(insta_levels, index_of_level):
    # insta_levels is sorted
    n = 0
    iterator = iter(insta_levels)
    while next(iterator, 60) < index_of_level:
        n += 1
    return n

def randomiseLevelWorlds(worlds_rng):
    global day_levels, night_levels, pool_levels, fog_levels, roof_levels, roof_night_levels, world_counts

    default_worlds = {**{k:(k-1)//10 for k in range(1, 50)}, 35:1, 50:5}

    def filter_candidates(level, candidates):
        candidates = set(candidates)
        if level == 5:
            candidates.discard(3)
            candidates.discard(4)
            candidates.discard(5)
            if shopless.get() or gamemode.get() != "adventure":
                candidates.discard(2) # no pool cleaners or level too long in ng+
        if level == 15:
            candidates.discard(4)
            candidates.discard(5)
        if level == 25:
            candidates.discard(4)
            candidates.discard(5)
        if level == 45: # bungee drops are bugged with pool (work fine on day/night apparently)
            candidates.discard(2)
            candidates.discard(3)
        return list(candidates)
    
    worlds = {}
    untouchable = {1, 2, 3, 4, 35, 50}
    if not randomisePlants.get():
        untouchable.add(41)
    if randomConveyors.get() == "False":
        for i in range(1, 51):
            if i % 5 == 0:
                untouchable.add(i)
    balance = [0, 0, 0, 0, 0]
    levels = [j * 10 + i + 1 for i in range(10) for j in range(5)] # 1, 11, 21, 31, 41, 2, 12...
    for i in levels:
        if i in untouchable or worlds_rng.randint(1, 100) > randomWorldChance.get():
            worlds[i] = default_worlds[i]
            continue
        candidates = filter_candidates(i, [k for k,v in enumerate(balance) if v < 0 and k != default_worlds[i]])
        if len(candidates) == 0:
            candidates = filter_candidates(i, [k for k,v in enumerate(balance) if v == 0 and k != default_worlds[i]])
        if len(candidates) > 0:
            new_world = worlds_rng.choice(candidates)
        else:
            candidates = filter_candidates(i, [x for x in range(5) if x != default_worlds[i]])
            max_balance = max(balance) + 1
            new_world = worlds_rng.choices(candidates, weights=[max_balance-balance[x] for x in candidates])[0]
        balance[default_worlds[i]] -= 1
        balance[new_world] += 1
        worlds[i] = new_world
    roof_with_5_pots = 41 if worlds[41] == 4 else worlds_rng.choice([k for k,v in worlds.items() if v == 4 and k % 5 != 0])
    # change some fog levels to roof night, because fog is boring
    roof_night_candidates = [k for k,v in worlds.items() if v == 3 and k not in untouchable and k not in [5,25,40]]
    if len(roof_night_candidates) > 0:
        roof_night_levels = worlds_rng.sample(roof_night_candidates, min(3, len(roof_night_candidates)))
        for l in roof_night_levels:
            worlds[l] = 5
    assert len(worlds) == 50
    assert worlds[roof_with_5_pots] == 4
    day_levels = {k for k,v in worlds.items() if v == 0}
    night_levels = {k for k,v in worlds.items() if v == 1}
    pool_levels = {k for k,v in worlds.items() if v == 2}
    fog_levels = {k for k,v in worlds.items() if v == 3}
    roof_levels = {k for k,v in worlds.items() if v == 4}
    roof_night_levels = {k for k,v in worlds.items() if v == 5}
    world_counts = [len(day_levels), len(night_levels), len(pool_levels), len(fog_levels), len(roof_levels), len(roof_night_levels)]
    return (worlds, roof_with_5_pots)


def redistribute_aquatic_zombies(worlds_rng):
    # snorkel appears on 5 of pool levels, and none of fog levels
    # dolphins appear on 3 of pool levels, and 1 of fog levels
    # we also change starting level to make sure they don't spawn on 3-3/3-8
    
    # find snorkels and dolphins which are allowed to stay
    snorkel_levels = (pool_levels & {23, 24, 25, 27, 30}) | (fog_levels & {23, 24, 25, 27, 30})
    snorkel_count = len(snorkel_levels)
    dolphin_levels = (pool_levels & {28, 29, 30, 34}) | (fog_levels & {28, 29, 30, 34})
    dolphin_count = len(dolphin_levels)
    # add remaining snorkels and dolphins - 1-5 is forbidden from having them
    snorkel_potential_levels = pool_levels.difference({5, 23, 24, 25, 27, 30})
    dolphin_potential_levels = pool_levels.difference({5, 28, 29, 30, 34})
    dolphin_add_to_fog_level = 34 not in fog_levels
    for i in range(5 - snorkel_count):
        level = worlds_rng.choice(list(snorkel_potential_levels))
        snorkel_levels.add(level)
        snorkel_potential_levels.remove(level)
    for i in range(4 - dolphin_count - int(dolphin_add_to_fog_level)):
        level = worlds_rng.choice(list(dolphin_potential_levels))
        dolphin_levels.add(level)
        dolphin_potential_levels.remove(level)
    if dolphin_add_to_fog_level:
        potential_levels = fog_levels.difference({5, 34})
        level = worlds_rng.choice(list(potential_levels))
        dolphin_levels.add(level)
    # write levels to memory
    for i in range(1,51):
        # WriteMemory("int", int(i in snorkel_levels), 0x6A35B0 + 0xCC*11 + 4*i)
        # WriteMemory("int", int(i in dolphin_levels), 0x6A35B0 + 0xCC*14 + 4*i)
        zombies_allowed[11][i-1] = int(i in snorkel_levels)
        zombies_allowed[14][i-1] = int(i in dolphin_levels)

     # set starting level
    if 23 not in pool_levels and 23 not in fog_levels:
        WriteMemory("int", min(snorkel_levels), 0x69DA8C + 0x1C*11)
        zombies[11][1] = min(snorkel_levels)
    if 28 not in pool_levels and 28 not in fog_levels:
        WriteMemory("int", min(dolphin_levels), 0x69DA8C + 0x1C*14)
        zombies[14][1] = min(dolphin_levels)
    
    return (snorkel_levels, dolphin_levels)


default_flags = [1, 1, 1, 1, 1, 1, 2, 1, 2, 2, 1, 2, 1, 2, 1, 1, 2, 1, 2, 2, 1, 2, 2, 3, 2, 2, 3, 2, 3, 3, 1, 2, 1, 2, 2, 1, 2, 1, 2, 2, 1, 2, 2, 3, 2, 2, 3, 2, 3, 3]
default_wavecount = [4, 6, 8, 10, 8] + [default_flags[x] * 10 for x in range(5, 50)]
default_flags = {k+1: v for k, v in enumerate(default_flags)}
default_wavecount = {k+1: v for k, v in enumerate(default_wavecount)}
default_waves_per_flag = {x+1: 10 for x in range(50)}


def randomiseWaveCount(level_worlds, seed):
    untouchable_wavecount = [1, 15, 35, 50]

    wavecount_rng = random.Random(seed+'wavecount')
    # add_level mutates changeable_levels and flags_balance, and adds results to flags_per_level, waves_per_flag, wavecount_per_level dictionaries
    def add_level(level, flag_count):
        try:
            changeable_levels.remove(level)
        except:
            pass
        flags_balance[0] += flag_count - default_flags[level]
        flags_per_level[level] = flag_count
        # unchangeable levels
        if level in untouchable_wavecount:
            flags_per_level[level] = default_flags[level]
            waves_per_flag[level] = 10 # default value - leave it at 10
            wavecount_per_level[level] = default_wavecount[level]
        # 1-2, 1-3 and 1-5 with random waves per flag (if random waves per flag is disabled, they will be in untouchable list)
        elif default_wavecount[level] < 10:
            if level == 5:
                wavecount_per_level[level] = wavecount_rng.choice([6, 7, 7, 8, 8, 9, 9, 10, 11, 12])
                waves_per_flag[level] = wavecount_per_level[level]
            else:
                default = default_wavecount[level]
                wavecount_per_level[level] = wavecount_rng.choice([int(default / 2), default - 2, default - 1, default, default + 1, default + 2, 10])
                waves_per_flag[level] = wavecount_per_level[level]
        # most of levels go here without random waves per flag:
        elif randomWaveCount.get() == "Flag count only":
            waves_per_flag[level] = 10 # default value
            wavecount_per_level[level] = waves_per_flag[level] * flags_per_level[level]
        # most of levels go here with random waves per flag:
        else:
            if wavecount_rng.randint(1, 100) <= 45: # 40.5% chance for different waves per flag
                waves_per_flag[level] = wavecount_rng.randint(6, 15)
            else:
                waves_per_flag[level] = 10
            wavecount_per_level[level] = waves_per_flag[level] * flags_per_level[level]
        # 3-5 without interesting conveyors is boring, so let's not make it any longer - but 
        # let's also not introduce dependency of level order generation on conveyor mode; so we want
        # to do all randomisation anyway, and only then check for conveyor
        if level == 25 and randomConveyors.get() != "It's Raining Seeds":
            waves_per_flag[level] = 10
            wavecount_per_level[level] = 20
            flags_per_level[level] = 2

    if randomWaveCount.get() == "Flag count only":
        untouchable_wavecount.extend([2, 3])
    if randomWaveCount.get() == "Flag count only" or level_worlds[5] not in [0, 1]:
        untouchable_wavecount.append(5)
    if not randomisePlants.get():
        untouchable_wavecount.append(41)
    changeable_levels = [x for x in range(1, 51) if x not in untouchable_wavecount] # modified in add_level
    flags_per_level = {1: 1}
    waves_per_flag = {1: 10} # 10 is globally default value in vanilla (levels with < 10 waves just have a special condition)
    wavecount_per_level = {1: 4}
    flags_balance = [0] # needs to be a list because it's modified in add_level

    # choose 1 3-flag to promoto to 5-flag
    # choose 2 3-flag to demote to 1-flag
    # choose 2 2-flags to promote to 4-flag
    # choose 2 1-flags to promote to 3-flag
    # But: conveyors are forbidden to go up by 2 flags or down by 2 flags,
    #   (3-4, 3-7, 3-9, 5-4, 5-7, 5-9 are quite likely to move +- 2 flags because of that).
    # + levels 1-2, 1-3, 1-5 are fobidden to go up in amount of flags
    # that makes balance = +6 flags
    # choose 6 other levels to demote by 1 flag to restore the balance
    # choose 6 other levels to demote by 1 flag and 6 other levels to promote by 1 flag
    # 25 levels to change in total
    for l in untouchable_wavecount:
        add_level(l, default_flags[l])

    flexible_three_flags = [24, 27, 29, 44, 47, 49]
    plus_or_minus_two_flags = wavecount_rng.sample(flexible_three_flags, 3)
    add_level(plus_or_minus_two_flags[0], 5)
    add_level(plus_or_minus_two_flags[1], 1)
    add_level(plus_or_minus_two_flags[2], 1)

    four_flag_candidates = [x for x in range(1, 51) if default_flags[x] == 2 and x not in untouchable_wavecount and x % 5 != 0]
    four_flags = wavecount_rng.sample(four_flag_candidates, 2)
    add_level(four_flags[0], 4)
    add_level(four_flags[1], 4)

    three_flag_candidates = [x for x in range(1, 51) if default_flags[x] == 1 and default_wavecount[x] >= 10\
        and x not in untouchable_wavecount and x % 5 != 0 and (x != 41 or randomisePlants.get())]
    three_flags = wavecount_rng.sample(three_flag_candidates, 2)
    add_level(three_flags[0], 3)
    add_level(three_flags[1], 3)

    remove_flag_candidates = [x for x in changeable_levels if default_flags[x] > 1]
    flag_removals = wavecount_rng.sample(remove_flag_candidates, 6)
    for l in flag_removals:
        add_level(l, default_flags[l] - 1)
        
    random_removals_candidates = [x for x in changeable_levels if default_flags[x] > 1]
    random_flag_removals = wavecount_rng.sample(random_removals_candidates, 6)
    for l in random_flag_removals:
        add_level(l, default_flags[l] - 1)

    random_extra_flag_candidates = [x for x in changeable_levels if default_wavecount[x] >= 10]
    random_extra_flags = wavecount_rng.sample(random_extra_flag_candidates, 6)
    for l in random_extra_flags:
        add_level(l, default_flags[l] + 1)

    remaining_levels = changeable_levels[:] # add_level mutates changeable_levels, so we can't just use for loop
    for l in remaining_levels:
        add_level(l, default_flags[l])
    
    assert len(changeable_levels) == 0 and flags_balance[0] == 0

    return (flags_per_level, wavecount_per_level, waves_per_flag)


SUCCESS = 0
FAILURE_GOOD_PLANTS = 1
FAILURE_POOL_1 = 2
FAILURE_POOL_2 = 3
FAILURE_POOL_3 = 4
FAILURE_POOL_4 = 5
FAILURE_ROOF_1 = 6
FAILURE_POT_2 = 7
FAILURE_GARGS = 8
FAILURE_BALLOON_1 = 9
FAILURE_BALLOON_2 = 10
FAILURE_SHROOMS = 11
FAILURE_INSTA = 12
FAILURES_COUNT = 13


def checkLevels(seed):
    seeded_wavepoints = []
    seeded_weights = []
    worlds_rng = random.Random(seed+'worlds')

    def randomiseWavePoints(minigames=False):
        global randomWavePoints, wavePointArray
        for i in range(2, 33):
            if i==26 and minigames: # peashooter zombie in minigames will always have 1 point, because on Zombotany levels there are no normals
                WriteMemory("int", 1, 0x69DA88 + 0x1C*i)
                if i in wavepoints_container:
                    wavepoints_container[i][0] = 1
                continue
            if i!=9 and i!=25:
                addWavePoint=0
                randomCheck=0
                while addWavePoint==0 and not randomCheck:
                    if randomWavePoints.get()=="EXTREME":
                        if i==5:
                            wavePoint=(wavepoint_rng.randint(10,83))//10
                        elif i==2:
                            wavePoint=2+wavepoint_rng.randint(0,1)
                        else:
                            wavePoint=(wavepoint_rng.randint(20,82))//10
                        if wavePoint>=8:
                            wavePoint=10    
                    else:
                        wavePoint=wavePointArray[i]
                        if wavePoint==10:
                            lowerBound=-3
                            upperBound=0
                        elif wavePoint>4:
                            lowerBound=-2
                            upperBound=2
                        elif wavePoint==2 and i!=5:
                            lowerBound=0
                            upperBound=1
                        else:
                            lowerBound=-1
                            upperBound=1
                        addWavePoint=wavepoint_rng.randint(lowerBound, upperBound)
                        wavePoint=wavePoint+addWavePoint
                        if wavePoint<2 and i!=5:
                            wavePoint=2
                    randomCheck=wavepoint_rng.randint(0,2)
                    if i==2:
                        randomCheck=1
                if i in wavepoints_container:
                    wavepoints_container[i][0] = wavePoint
                WriteMemory("int", wavePoint, 0x69DA88 + 0x1C*i)

    def randomiseWeights(minigames=False):
        for i in range(0, 33):
            if i!=1 and i!=9 and i!=25:
                if minigames and i == 26: # peashooter zombies in minigames are like normals
                    weight=weights_rng.randint(1, 45)
                elif i>2:
                    weight=weights_rng.randint(1, 60)
                #elif i==23:
                #    weight=weights_rng.randint(1, 50)
                else:
                    weight=weights_rng.randint(1, 45)

                if i==19:
                    weight=weights_rng.randint(1, 30) # yeti's final weight
                elif weight>50:
                    weight=weight*1000
                elif weight<5:
                    weight=weight*10
                else:
                    weight=weight*100
                if i in zombie_weight_container:
                    zombie_weight_container[i][0] = weight
                WriteMemory("int", weight, 0x69DA94 + 0x1C*i)
        WriteMemory("int", 0, 0x69DA94 + 0x1C*1)
        WriteMemory("int", 0, 0x69DA94 + 0x1C*9)


    (level_worlds, level_with_5_pots) = randomiseLevelWorlds(worlds_rng)
    (snorkel_levels, dolphin_levels) = redistribute_aquatic_zombies(worlds_rng)
    (flags_per_level, wavecount_per_level, waves_per_flag) = randomiseWaveCount(level_worlds, seed)

    levels, plants = randomiseLevelsAndPlants(seed, level_worlds, wavecount_per_level, snorkel_levels, dolphin_levels, level_with_5_pots)
    
    # check for good plants other than pot/lily/puff/sunshroom
    levels_with_good_plants = [levels.index(plants.index(x)) for x in [2,6,7,10,13,15,17,18,20,24,29,32,35,39]]
    count_of_good = len([x for x in levels_with_good_plants if x < 18])
    if count_of_good < 4:
        return FAILURE_GOOD_PLANTS
    
    # pool check
    lily_level = levels.index(plants.index(16))
    kelp_level = levels.index(plants.index(19))
    star_3peater = min(levels.index(plants.index(18)), levels.index(plants.index(29)))
    pool_three_flag_level = next((x for x in range(50) if levels[x] % 5 != 0 and level_worlds[levels[x]] in [2,3] and flags_per_level[levels[x]] > 2), 60)
    if pool_three_flag_level <= lily_level:
        return FAILURE_POOL_1
    any_pool_level = next(x for x in range(50) if levels[x] % 5 != 0 and level_worlds[levels[x]] in [2,3])
    if any_pool_level <= min(lily_level, kelp_level, star_3peater):
        return FAILURE_POOL_2
    
    gen_zombies = generateZombies(seed, levels, plants, level_worlds, wavecount_per_level)
    wavepoint_rng = random.Random(seed+'wavepoint')
    weights_rng = random.Random(seed+'weight')
    for i in range(51):
        randomiseWavePoints() # gets randomised before 1st level
        seeded_wavepoints.append(copy.deepcopy(wavepoints_container))
        randomiseWeights() # gets randomised before 1st level
        seeded_weights.append(copy.deepcopy(zombie_weight_container))

    # pool check
    pool_level_requiring_aquatic = next((x for x in range(50) if not is_pool_level_passable_without_aquatic_plants(
        gen_zombies, levels[x], x, seeded_wavepoints, seeded_weights, level_worlds, flags_per_level, wavecount_per_level)), 60)
    if pool_level_requiring_aquatic <= min(lily_level, kelp_level):
        return FAILURE_POOL_3
    pool_requiring_lily_special = next((x for x in range(50) if pool_requiring_lily( # snorkel dolphin spam
        gen_zombies, levels[x], x, seeded_wavepoints, seeded_weights, level_worlds, flags_per_level)), 60)
    if pool_requiring_lily_special <= lily_level:
        return FAILURE_POOL_4

    coffee_index = levels.index(plants.index(35))
    doom_index = max(levels.index(plants.index(15)), coffee_index) # doom is counted only after coffee
    insta_levels = sorted([*[levels.index(plants.index(x)) for x in [2,6,17,20]], doom_index])

    # pot check
    pot_level = levels.index(plants.index(33))
    pult_level = min(levels.index(plants.index(32)), levels.index(plants.index(39)))
    if any(levels[x] % 5 != 0 and level_worlds[levels[x]] in [4,5] and levels[x] != level_with_5_pots and flags_per_level[levels[x]] > 2 and \
           any(zombie_likely_to_spawn(z, gen_zombies, levels[x], x, seeded_wavepoints, seeded_weights, flags_per_level) for z in strong_zombies)\
            for x in range(1, min(pult_level, pot_level) + 1)):
        return FAILURE_ROOF_1
    bad_roof_level = next((x for x in range(50) if roof_requiring_pot(gen_zombies, levels[x], x, seeded_wavepoints, seeded_weights, insta_levels,
                                                                      level_worlds, flags_per_level, wavecount_per_level)), 60)
    if bad_roof_level <= pot_level:
        return FAILURE_POT_2
    
    # gargs check
    if any(zombie_likely_to_spawn(z, gen_zombies, levels[x], x, seeded_wavepoints, seeded_weights, flags_per_level) for z in [23,32] for x in range(1,25) if levels[x] % 5 != 0 and flags_per_level[levels[x]] > 1)\
        or any(zombie_spammable(z, gen_zombies, levels[x], x, seeded_wavepoints, seeded_weights, flags_per_level) for z in [23,32] for x in range(1,35) if levels[x] % 5 != 0 and flags_per_level[levels[x]] == 1):
        return FAILURE_GARGS

    # balloon check
    anti_balloon = min(levels.index(plants.index(x)) for x in [2,20,26,27])
    anti_balloon = min(doom_index, anti_balloon)
    anti_balloon_spam = min(levels.index(plants.index(26)), levels.index(plants.index(27)))
    blover_level = levels.index(plants.index(27))
    if any(not can_spawn_only_at_level_end(16, gen_zombies, levels[x], x, seeded_wavepoints, wavecount_per_level) for x in range(1, anti_balloon+1))\
        or any(zombie_spammable(16, gen_zombies, levels[x], x, seeded_wavepoints, seeded_weights, flags_per_level) for x in range(1, anti_balloon_spam+1)):
        return FAILURE_BALLOON_1
    if any(levels[x] <= lily_level and levels[x] <= blover_level \
               and balloon_requires_lily_or_blover(
                   gen_zombies, levels[x], x, seeded_wavepoints, seeded_weights, level_worlds, flags_per_level
               ) for x in range(1, min(lily_level, blover_level) + 1)):
        return FAILURE_BALLOON_2
    
    # sunshroom+puff check
    # sunshroom_level = levels.index(plants.index(9))
    # puff_level = levels.index(plants.index(8))
    # night_two_flag = next((x for x in range(1,50) if is_dangerous_night_level(gen_zombies, levels[x], x, seeded_wavepoints, seeded_weights, level_worlds, flags_per_level)), 60)
    # fog_two_flag = next((x for x in range(1,50) if is_dangerous_fog_level(gen_zombies, levels[x], x, seeded_wavepoints, seeded_weights, level_worlds, flags_per_level)), 60)
    # if min(night_two_flag, fog_two_flag) <= min(sunshroom_level, puff_level) or puff_level >= fog_two_flag:
    #     return FAILURE_SHROOMS
    
    # instas check
    level_with_strong_zombies = next((x for x in range(1,50) if (at_least(2, (1 for z in strong_zombies if \
                                                                    zombie_likely_to_spawn(z, gen_zombies, levels[x], x, seeded_wavepoints, seeded_weights, flags_per_level))))\
                                                                or any(zombie_spammable(z, gen_zombies, levels[x], x, seeded_wavepoints, seeded_weights, flags_per_level)\
                                                                    for z in strong_zombies)), 60)
    # if level_with_strong_zombies <= insta_levels[0]:
    #     return FAILURE_INSTA
    with lock:
        print (f"{seed}")
    return SUCCESS


def checkLength(seed):
    levels, plants = randomiseLevelsAndPlants(seed)
    length = 0
    for i in range(len(levels)):
        if levels[i] == i + 1:
            length += 1
        else:
            break
    return (length, seed)

def lock_init(l):
    global lock
    lock = l

if __name__ == '__main__':
    # finding longest start with normal level order
    # max_length = 0
    # while True:
    #     seeds = [next_seed() for _ in range(100_000)]
    #     pool = multiprocessing.Pool(cpu_count() if cpu_count() else 4)
    #     start = perf_counter_ns()
    #     l = pool.map(checkLength, seeds)
    #     end = perf_counter_ns()
    #     print(f"{(end - start) / 1_000_000_000:.1f} sec")
    #     best = max(l, key=lambda x:x[0])
    #     if best[0] >= max_length:
    #         max_length = best[0]
    #         best_seeds = [x for x in l if x[0] == best[0]]
    #         print(best_seeds)

    if False: # non-parallel version for debugging/checking specicifc list of seeds
        lock_init(multiprocessing.Lock())
        seeds = ["gargantuan Moo inhibits the California"]
        for s in seeds:
            res = checkLevels(s)
        exit(0)
    parallel_count = cpu_count() if cpu_count() else 4
    print("Parallel count = ", parallel_count)
    while True:
        n_per_iteration = 100000
        pool = multiprocessing.Pool(parallel_count, initializer=lock_init, initargs=(multiprocessing.Lock(),))
        seeds = [next_seed() for _ in range(n_per_iteration)]
        start = perf_counter_ns()
        reasons_list = pool.map(checkLevels, seeds, chunksize=int(n_per_iteration / parallel_count / 8))
        end = perf_counter_ns()
        print(f"{(end - start) / 1_000_000_000:.1f} sec")
        print("Success rates:") # will be correct only if failures can occur in ascending order
        reasons = dict(Counter(reasons_list).items())
        successes = reasons.get(SUCCESS, 0)
        n_of_times_got_to_check = [n_per_iteration, n_per_iteration]
        remaining_seeds_to_check = n_per_iteration
        for k in range(2, FAILURES_COUNT):
            n_of_times_got_to_check.append(remaining_seeds_to_check - reasons.get(k-1, 0))
            remaining_seeds_to_check -= reasons.get(k-1, 0)
        success_rates = [1]
        for k in range(1, FAILURES_COUNT-1):
            success_rates.append(n_of_times_got_to_check[k+1] / max(n_of_times_got_to_check[k], 1))
        success_rates.append(successes / max(n_of_times_got_to_check[FAILURES_COUNT-1], 1))
        for i,s in enumerate(success_rates):
            if i != SUCCESS:
                print(f"{i}: {s:.1%}")

