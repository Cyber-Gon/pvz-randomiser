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

ONE_FLAGS = [1,2,3,4,5,6,8,11,13,15,16,18,21,31,33,35,36,38,41]
THREE_FLAGS = [24,27,29,30,40,44,47,49]
strong_zombies = [4,6,7,12,21,23,31,32]

wavepoints_container = { index: element for index,element in enumerate([[x[3]] for x in zombies][:n_of_zombie_strings]) }
zombie_weight_container = { index: element for index,element in enumerate([[x[2]] for x in zombies][:n_of_zombie_strings]) }


def getAvailableStages(plants, used_levels=[]):
    global noRestrictions, challengeMode
    if len(used_levels) == 0:
        level_set = {1}
    elif noRestrictions.get():
        level_set = {
        2,  3,  4,  5,  6,  7,  8,  9,  10,
        11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
        21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
        31, 32, 33, 34, 35, 36, 37, 38, 39, 40,
        41, 42, 43, 44, 45, 46, 47, 48, 49, 50}
    else:
        level_set = {2, 3, 4, 5, 6, 7, 8, 9, 10, 15, 20, 25, 30, 35, 40, 45, 50}
        plant_set = set(plants)
        
        tough_check   = len(plant_set & {2, 6, 7, 15, 17, 20, 29, 31, 35, 39}) #cherry bomb, chomper, repeater, doom, squash, jalapeno, starfruit, magnet, coffee bean, melon pult
        balloon_check = len(plant_set & {2, 15, 20}) + 2 * len(plant_set & {26, 27})
        
        if challengeMode.get():
            tough_check = 9999
        
        has_puff              = 8  in plant_set
        has_lily              = 16 in plant_set
        has_pool_shooter      = 29 in plant_set or 18 in plant_set
        has_seapeater         = (24 in plant_set or 19 in plant_set) and has_pool_shooter #threepeater or starfruit + sea shroom or kelp
        has_fog_plants        = has_puff and (has_lily or 24 in plant_set)
        has_pot               = 33 in plant_set
        has_roof_plant        = 32 in plant_set or 39 in plant_set or has_pot
        
        if has_puff:
            level_set.add(11)
        if has_puff and tough_check >= 3:
            level_set.add(12)
        if has_puff:
            level_set.add(13)
        if has_puff and tough_check >= 3:
            level_set.add(14)
        if has_puff:
            level_set.add(16)
        if has_puff and tough_check >= 3:
            level_set.add(17)
        if has_puff:
            level_set.add(18)
        if has_puff and tough_check >= 3:
            level_set.add(19)
        
        if has_lily or has_pool_shooter:
            level_set.add(21)
        if (has_lily or has_pool_shooter) and tough_check >= 3:
            level_set.add(22)
        if has_lily:
            level_set.add(23)
        if has_lily and tough_check >= 5:
            level_set.add(24)
        if (has_lily or has_pool_shooter) and tough_check >= 3:
            level_set.add(26)
        if has_lily and tough_check >= 5:
            level_set.add(27)
        if has_lily or has_seapeater:
            level_set.add(28)
        if (has_lily or has_seapeater) and tough_check >= 5:
            level_set.add(29)
        
        if has_fog_plants:
            level_set.add(31)
        if has_puff and (has_lily or has_seapeater) and tough_check >= 3:
            level_set.add(32)
        if has_fog_plants:
            level_set.add(33)
        if has_puff and has_lily and balloon_check >= 2 and tough_check >= 3:
            level_set.add(34)
        if has_fog_plants:
            level_set.add(36)
        if has_puff and (has_lily or has_seapeater) and tough_check >= 5:
            level_set.add(37)
        if has_fog_plants:
            level_set.add(38)
        if has_puff and has_lily and balloon_check >= 2 and tough_check >= 5:
            level_set.add(39)
        
        if has_roof_plant or len(used_levels) > 10:
            level_set.add(41)
        if has_pot and tough_check >= 3:
            level_set.add(42)
        if has_roof_plant and tough_check >= 3:
            level_set.add(43)
        if has_pot and tough_check >= 5:
            level_set.add(44)
        if has_roof_plant and tough_check >= 3:
            level_set.add(46)
        if has_pot and tough_check >= 5:
            level_set.add(47)
        if has_pot and tough_check >= 3:
            level_set.add(48)
        if has_pot and tough_check >= 5:
            level_set.add(49)
    
    for i in used_levels:
        if i in level_set:
            level_set.remove(i)
    
    return level_set


def randomiseLevelsAndPlants(seed):
    global noRestrictions, challengeMode
    random.seed(seed)
    
    plants = [1]
    levels = [1]
    unused_plants   = [i        for i in range(2,40)]
    if challengeMode.get() or noRestrictions.get():
        level_plants    = [(-1,1.0) for i in range(0,51)]
    else:
        level_plants    = [(-1,0.8) for i in range(0,51)]
    level_plants[0] =  (0, 0.0)
    level_plants[1] =  (1, 0.0)
    if not noRestrictions.get():
        while 1: #select key plants for only levels you could have unlocked by that point
            current_available = len(getAvailableStages(plants,levels))
            plants.append(0)
            key_plants   = []
            key_weights  = []
            key_weights2 = []
            for i in unused_plants:
                plants[-1] = i
                if current_available < len(getAvailableStages(plants,levels)):
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
            available_levels = sorted(list(getAvailableStages(plants[0:-2], levels)))
            chosen_level     = random.choice(available_levels)
            unused_plants.remove(chosen_plant)
            
            levels.append(chosen_level)
            level_plants[chosen_level] = (chosen_plant,chosen_weight)
        
    for i in unused_plants:
        available_levels = sorted(list(getAvailableStages(plants, levels))) #should return all levels without plants assigned
        chosen_level     = random.choice(available_levels)
        
        levels.append(chosen_level)
        if i==9:
            level_plants[chosen_level] = (i,2.0)
        else:
            level_plants[chosen_level] = (i,1.0)
    
    levels = [1]
    plants = [1]
    world_weights = [0.93, 1.0, 1.0, 1.0, 1.0]
    for i in range(1,50):
        available_levels = sorted(list(getAvailableStages(plants, levels)))
        chosen_level     = random.choices(available_levels, weights=[level_plants[i][1]*world_weights[int((i-1)/10)] for i in available_levels])[0]
        world_weights[int((chosen_level-1)/10)] -= 0.07
        levels.append(chosen_level)
        plants.append(level_plants[chosen_level][0])
    
    level_plants = [i[0] for i in level_plants]
    return levels, level_plants


def generateZombies(seed, levels, level_plants):
    zombies_rng = random.Random(seed+'zombies')
    zombiesToRandomise=[[]]
    plantsInOrder=[]
    for i in range(0, len(levels)):
        plantsInOrder.append(level_plants[levels[i]])
    for i in range(1, len(levels)):
        if levels[i]==50 or levels[i]==15 or levels[i]==35:
            zombiesToRandomise.append([]) # no rando on those levels
            continue
        has_lily              = 16 in plantsInOrder[0:i]
        has_pool_shooter      = 29 in plantsInOrder[0:i] or 18 in plantsInOrder[0:i]
        has_seapeater         = (24 in plantsInOrder[0:i] or 19 in plantsInOrder[0:i]) and has_pool_shooter #threepeater or starfruit + sea shroom or kelp
        has_pot               = 33 in plantsInOrder[0:i]
        has_doom              = 15 in plantsInOrder[0:i] and 35 in plantsInOrder[0:i]
        has_instant           = 2 in plantsInOrder[0:i] or 17 in plantsInOrder[0:i] or 20 in plantsInOrder[0:i] or has_doom
        balloon_check = 26 in plantsInOrder[0:i] or 27 in plantsInOrder[0:i] or (2 in plantsInOrder[0:i] and has_doom) or (2 in plantsInOrder[0:i] and 20 in plantsInOrder[0:i]) or (20 in plantsInOrder[0:i] and has_doom)
        currentZombies=[]
        for j in range(2, 33):
            if j==9 or j==10 or j==24 or j==25:
                continue
            elif zombies_rng.randint(0, 11) != 0:
                continue
            elif (j==11 or j==14) and (levels[i]<21 or levels[i]>40):
                continue
            elif zombies[j][1]==levels[i]:
                continue
            elif levels[i]==45 and j in [11, 12, 13, 14, 16, 17, 18, 20, 22, 23, 32]:
                continue
            elif noRestrictions.get():
                currentZombies.append(j)
            elif (j==11 or j==14) and not(has_lily or has_seapeater):
                continue
            elif j==16 and not balloon_check:
                continue
            elif j==16 and levels[i] in [5, 10, 20, 25, 30, 40]:
                continue
            elif j==17 and levels[i]>40 and not (has_pot):
                continue
            elif j==23 and not (has_instant):
                continue
            elif j==32 and not (has_instant):
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
def zombie_likely_to_spawn(zombie, generated_zombies, level, index_of_level, seeded_wavepoints, seeded_weights):
    if level % 5 == 0:
        return False
    if not zombie_on_level(zombie, generated_zombies, level, index_of_level):
        return False
    weight = seeded_weights[index_of_level][zombie][0]
    wavepoints = seeded_wavepoints[index_of_level][zombie][0]
    spawns_est = 0
    for i in range(3, n_of_flags(level) * 10 + 1, 3):
        if wavepoints > i / 3:
            continue
        total_weight = sum(seeded_weights[index_of_level][z][0] for z in range(33) if seeded_wavepoints[index_of_level][z][0] <= i / 3 \
                           and zombie_on_level(z, generated_zombies, level, index_of_level))
        spawns_est += i / 3 / wavepoints * 3 * (weight / total_weight) # rough estimate, not exactly correct
    return spawns_est > 2 * n_of_flags(level)**0.75


def zombie_spammable(zombie, generated_zombies, level, index_of_level, seeded_wavepoints, seeded_weights):
    if level % 5 == 0:
        return False
    if not zombie_on_level(zombie, generated_zombies, level, index_of_level):
        return False
    weight = seeded_weights[index_of_level][zombie][0]
    wavepoints = seeded_wavepoints[index_of_level][zombie][0]
    spawns_est = 0
    for i in range(3, n_of_flags(level) * 10 + 1, 3):
        if wavepoints > i / 3:
            continue
        total_weight = sum(seeded_weights[index_of_level][z][0] for z in range(33) if seeded_wavepoints[index_of_level][z][0] <= i / 3 \
                           and zombie_on_level(z, generated_zombies, level, index_of_level))
        spawns_est += i / 3 / wavepoints * 3 * (weight / total_weight) # rough estimate, not exactly correct
    return spawns_est > 2.5**(0.85 * n_of_flags(level)) + 1


def can_spawn_only_at_level_end(zombie, generated_zombies, level, index_of_level, seeded_wavepoints):
    if level % 5 == 0:
        return True
    if not zombie_on_level(zombie, generated_zombies, level, index_of_level):
        return True
    wavepoints = seeded_wavepoints[index_of_level][zombie][0]
    return (level in THREE_FLAGS and wavepoints >= 10) or (level in ONE_FLAGS and wavepoints >= 4) or (n_of_flags(level) == 2 and wavepoints >= 7)


def is_dangerous_night_level(generated_zombies, level, index_of_level, seeded_wavepoints, seeded_weights):
    if level % 5 == 0 or level < 11 or level > 20 or level in ONE_FLAGS:
        return False
    count = 0
    for z in strong_zombies:
        if zombie_spammable(z, generated_zombies, level, index_of_level, seeded_wavepoints, seeded_weights):
            return True
        if zombie_likely_to_spawn(z, generated_zombies, level, index_of_level, seeded_wavepoints, seeded_weights):
            count += 1
            if count == 3:
                return True
    return False


def is_dangerous_fog_level(generated_zombies, level, index_of_level, seeded_wavepoints, seeded_weights):
    if level % 5 == 0 or level < 31 or level > 40 or level in ONE_FLAGS:
        return False
    count = 0
    for z in strong_zombies:
        if zombie_spammable(z, generated_zombies, level, index_of_level, seeded_wavepoints, seeded_weights):
            return True
        if zombie_likely_to_spawn(z, generated_zombies, level, index_of_level, seeded_wavepoints, seeded_weights):
            count += 1
            if count == 2:
                return True
    return False


# represents levels beatable with starfruit/threepeater
def is_pool_level_passable_without_aquatic_plants(generated_zombies, level, index_of_level, seeded_wavepoints, seeded_weights):
    if level % 5 == 0 or level < 21 or level > 40:
        return True
    if level in THREE_FLAGS or (31<=level<=40 and level not in ONE_FLAGS):
        return False
    # 2 flag pools or 1 flag fog remaining
    return can_spawn_only_at_level_end(11, generated_zombies, level, index_of_level, seeded_wavepoints) \
        and can_spawn_only_at_level_end(14, generated_zombies, level, index_of_level, seeded_wavepoints) \
        and not zombie_likely_to_spawn(4, generated_zombies, level, index_of_level, seeded_wavepoints, seeded_weights) \
        and not zombie_likely_to_spawn(31, generated_zombies, level, index_of_level, seeded_wavepoints, seeded_weights)


def pool_requiring_lily(generated_zombies, level, index_of_level, seeded_wavepoints, seeded_weights):
    if level % 5 == 0 or level < 21 or level > 40:
        return False
    if level in THREE_FLAGS:
        return True
    return zombie_spammable(11, generated_zombies, level, index_of_level, seeded_wavepoints, seeded_weights) \
        or zombie_spammable(14, generated_zombies, level, index_of_level, seeded_wavepoints, seeded_weights) \
        or (zombie_likely_to_spawn(11, generated_zombies, level, index_of_level, seeded_wavepoints, seeded_weights) \
            and zombie_likely_to_spawn(14, generated_zombies, level, index_of_level, seeded_wavepoints, seeded_weights))


def roof_requiring_pot(generated_zombies, level, index_of_level, seeded_wavepoints, seeded_weights, insta_levels):
    if level % 5 == 0 or level < 41:
        return False
    if level in THREE_FLAGS:
        return True
    if any(not can_spawn_only_at_level_end(z, generated_zombies, level, index_of_level, seeded_wavepoints) for z in [23,28,32]):
        return True
    enough_instas = sum(zombie_likely_to_spawn(z, generated_zombies, level, index_of_level, seeded_wavepoints, seeded_weights) \
        + zombie_spammable(z, generated_zombies, level, index_of_level, seeded_wavepoints, seeded_weights)
        for z in range(33) if (z==28 or z==18 or z in strong_zombies)) - 1
    return  n_of_instas_by_level(insta_levels, index_of_level) < 1 or n_of_instas_by_level(insta_levels, index_of_level) < enough_instas


def balloon_requires_lily_or_blover(generated_zombies, level, index_of_level, seeded_wavepoints, seeded_weights):
    if level % 5 == 0 or level < 21 or level > 40:
        return False
    if level not in ONE_FLAGS and zombie_likely_to_spawn(16, generated_zombies, level, index_of_level, seeded_wavepoints, seeded_weights):
        return True
    if level in ONE_FLAGS and zombie_spammable(16, generated_zombies, level, index_of_level, seeded_wavepoints, seeded_weights):
        return True
    return False


def n_of_flags(level):
    if level in THREE_FLAGS:
        return 3
    if level in ONE_FLAGS:
        return 1
    return 2


def n_of_instas_by_level(insta_levels, index_of_level):
    # insta_levels is sorted
    n = 0
    iterator = iter(insta_levels)
    while next(iterator, 60) < index_of_level:
        n += 1
    return n


SUCCESS = 0
FAILURE_GOOD_PLANTS = 1
FAILURE_POOL_1 = 2
FAILURE_POOL_2 = 3
FAILURE_POOL_3 = 4
FAILURE_POOL_4 = 5
FAILURE_POT_1 = 6
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

    levels, plants = randomiseLevelsAndPlants(seed)
    
    # check for good plants other than pot/lily/puff/sunshroom
    levels_with_good_plants = [levels.index(plants.index(x)) for x in [2,6,7,10,13,15,17,18,20,24,29,32,35,39]]
    count_of_good = len([x for x in levels_with_good_plants if x < 18])
    if count_of_good < 5:
        return FAILURE_GOOD_PLANTS
    
    # pool check
    lily_level = levels.index(plants.index(16))
    kelp_level = levels.index(plants.index(19))
    star_3peater = min(levels.index(plants.index(18)), levels.index(plants.index(29)))
    pool_three_flag_level = next(x for x in range(50) if levels[x] in [24,27,29])
    if pool_three_flag_level <= lily_level:
        return FAILURE_POOL_1
    any_pool_level = next(x for x in range(50) if levels[x] % 5 != 0 and 21 <= levels[x] <= 40)
    if any_pool_level <= min(lily_level, kelp_level, star_3peater):
        return FAILURE_POOL_2
    
    gen_zombies = generateZombies(seed, levels, plants)
    wavepoint_rng = random.Random(seed+'wavepoint')
    weights_rng = random.Random(seed+'weight')
    for i in range(51):
        randomiseWavePoints() # gets randomised before 1st level
        seeded_wavepoints.append(copy.deepcopy(wavepoints_container))
        randomiseWeights() # gets randomised before 1st level
        seeded_weights.append(copy.deepcopy(zombie_weight_container))

    # pool check
    pool_level_requiring_aquatic = next(x for x in range(50) if not is_pool_level_passable_without_aquatic_plants(
        gen_zombies, levels[x], x, seeded_wavepoints, seeded_weights))
    if pool_level_requiring_aquatic <= min(lily_level, kelp_level):
        return FAILURE_POOL_3
    pool_requiring_lily_special = next(x for x in range(50) if pool_requiring_lily( # snorkel dolphin spam
        gen_zombies, levels[x], x, seeded_wavepoints, seeded_weights))
    if pool_requiring_lily_special <= lily_level:
        return FAILURE_POOL_4

    coffee_index = levels.index(plants.index(35))
    doom_index = max(levels.index(plants.index(15)), coffee_index) # doom is counted only after coffee
    insta_levels = sorted([*[levels.index(plants.index(x)) for x in [2,6,17,20]], doom_index])

    # pot check
    pot_level = levels.index(plants.index(33))
    pult_level = min(levels.index(plants.index(32)), levels.index(plants.index(39)))
    if any(levels[x] % 5 != 0 and levels[x] >= 41 for x in range(1, min(pult_level, pot_level) + 1)):
        return FAILURE_POT_1
    bad_roof_level = next((x for x in range(50) if roof_requiring_pot(gen_zombies, levels[x], x, seeded_wavepoints, seeded_weights, insta_levels)), 60)
    if bad_roof_level <= pot_level:
        return FAILURE_POT_2
    
    # gargs check
    if any(zombie_likely_to_spawn(z, gen_zombies, levels[x], x, seeded_wavepoints, seeded_weights) for z in [23,32] for x in range(1,15) if x not in ONE_FLAGS) \
        or any(zombie_spammable(z, gen_zombies, levels[x], x, seeded_wavepoints, seeded_weights) for z in [23,32] for x in range(1,15) if x in ONE_FLAGS) \
        or any(zombie_spammable(z, gen_zombies, levels[x], x, seeded_wavepoints, seeded_weights) for z in [23,32] for x in range(15,30)):
        return FAILURE_GARGS

    # balloon check
    anti_balloon = min(levels.index(plants.index(x)) for x in [2,20,26,27])
    anti_balloon = min(doom_index, anti_balloon)
    anti_balloon_spam = min(levels.index(plants.index(26)), levels.index(plants.index(27)))
    blover_level = levels.index(plants.index(27))
    if any(not can_spawn_only_at_level_end(16, gen_zombies, levels[x], x, seeded_wavepoints) for x in range(1, anti_balloon+1))\
        or any(zombie_spammable(16, gen_zombies, levels[x], x, seeded_wavepoints, seeded_weights) for x in range(1, anti_balloon_spam+1)):
        return FAILURE_BALLOON_1
    if any(levels[x] <= lily_level and levels[x] <= blover_level \
               and balloon_requires_lily_or_blover(
                   gen_zombies, levels[x], x, seeded_wavepoints, seeded_weights
               ) for x in range(1, min(lily_level, blover_level) + 1)):
        return FAILURE_BALLOON_2
    
    # sunshroom+puff check
    sunshroom_level = levels.index(plants.index(9))
    puff_level = levels.index(plants.index(8))
    night_two_flag = next((x for x in range(1,50) if is_dangerous_night_level(gen_zombies, levels[x], x, seeded_wavepoints, seeded_weights)), 60)
    fog_two_flag = next((x for x in range(1,50) if is_dangerous_fog_level(gen_zombies, levels[x], x, seeded_wavepoints, seeded_weights)), 60)
    if min(night_two_flag, fog_two_flag) <= min(sunshroom_level, puff_level) or puff_level >= fog_two_flag:
        return FAILURE_SHROOMS
    
    # instas check
    level_with_strong_zombies = next(x for x in range(1,50) if (at_least(2, (1 for z in strong_zombies if \
                                                                    zombie_likely_to_spawn(z, gen_zombies, levels[x], x, seeded_wavepoints, seeded_weights))))\
                                                                or any(zombie_spammable(z, gen_zombies, levels[x], x, seeded_wavepoints, seeded_weights)\
                                                                    for z in strong_zombies))
    if level_with_strong_zombies <= insta_levels[0]:
        return FAILURE_INSTA
    
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
        seeds = ["impossible Bulbasaur pick ups the child"]
        for s in seeds:
            checkLevels(s)
        exit(0)
    parallel_count = cpu_count() if cpu_count() else 4
    print("Parallel count = ", parallel_count)
    while True:
        n_per_iteration = 1000000
        pool = multiprocessing.Pool(parallel_count)
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

