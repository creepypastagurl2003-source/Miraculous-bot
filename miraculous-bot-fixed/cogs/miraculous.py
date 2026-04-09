import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional

WIKI = "https://miraculous.fandom.com/wiki/Special:FilePath"

CHARACTERS = {
    "marinette": {
        "name": "Marinette Dupain-Cheng",
        "alias": "Ladybug",
        "also_known_as": ["Multimouse", "Lady Noir", "Scarabella"],
        "age": 14,
        "birthday": "July 9",
        "school": "Collège Françoise Dupont",
        "class": "Ms. Bustier's class",
        "nationality": "French-Chinese",
        "miraculous": "Ladybug Miraculous (Earrings)",
        "kwami": "Tikki",
        "power": "Lucky Charm, Miraculous Ladybug",
        "weapon": "Yo-yo",
        "color": 0xFF0000,
        "emoji": "🐞",
        "image": f"{WIKI}/Ladybug_Square.png",
        "image_alt": f"{WIKI}/Marinette_Dupain-Cheng_Square.png",
        "description": (
            "Marinette Dupain-Cheng is the main protagonist. A kind, creative, and clumsy girl "
            "who transforms into the superhero Ladybug. She is the Guardian of the Miraculouses "
            "and a gifted fashion designer. She has a crush on Adrien Agreste."
        ),
        "family": "Tom Dupain (father), Sabine Cheng (mother)",
        "friends": "Alya Césaire (best friend), Nino Lahiffe, Luka Couffaine, Kagami Tsurugi",
        "likes": "Fashion design, baking, gaming, music",
        "voice": "Cristina Vee (EN), Anouck Hautbois (FR)",
        "fun_fact": "She is half French and half Chinese. Her grandfather is Master Fu's old friend Wang Cheng.",
    },
    "adrien": {
        "name": "Adrien Agreste",
        "alias": "Cat Noir",
        "also_known_as": ["Mister Bug", "Cat Walker"],
        "age": 14,
        "birthday": "Unknown",
        "school": "Collège Françoise Dupont",
        "class": "Ms. Bustier's class",
        "nationality": "French",
        "miraculous": "Cat Miraculous (Ring)",
        "kwami": "Plagg",
        "power": "Cataclysm",
        "weapon": "Staff",
        "color": 0x1A1A2E,
        "emoji": "🐱",
        "image": f"{WIKI}/Cat_Noir_Square.png",
        "image_alt": f"{WIKI}/Adrien_Agreste_Square.png",
        "description": (
            "Adrien Agreste is the deuteragonist and Marinette's love interest. "
            "The son of fashion designer Gabriel Agreste (Hawk Moth), he transforms into Cat Noir. "
            "He is caring, playful, and loves to make puns. He is in love with Ladybug."
        ),
        "family": "Gabriel Agreste (father), Emilie Agreste (mother, comatose), Félix Graham de Vanily (cousin)",
        "friends": "Nino Lahiffe (best friend), Marinette, Luka, Kagami",
        "likes": "Fencing, piano, Chinese culture, video games, photography",
        "voice": "Bryce Papenbrook (EN), Benjamin Bollen (FR)",
        "fun_fact": "Adrien was homeschooled before joining Collège Françoise Dupont. His mother Emilie is kept alive in a comatose state.",
    },
    "alya": {
        "name": "Alya Césaire",
        "alias": "Rena Rouge",
        "also_known_as": ["Rena Furtive", "Scarlet Moth's Rena Rouge"],
        "age": 14,
        "birthday": "Unknown",
        "school": "Collège Françoise Dupont",
        "class": "Ms. Bustier's class",
        "nationality": "French-Martiniquaise",
        "miraculous": "Fox Miraculous (Necklace)",
        "kwami": "Trixx",
        "power": "Mirage",
        "weapon": "Flute",
        "color": 0xFF6B00,
        "emoji": "🦊",
        "image": f"{WIKI}/Rena_Rouge_Square.png",
        "image_alt": f"{WIKI}/Alya_C%C3%A9saire_Square.png",
        "description": (
            "Alya Césaire is Marinette's best friend and a passionate blogger. "
            "She runs the Ladyblog, a fan site dedicated to Ladybug. As Rena Rouge, "
            "she uses the power of illusion. She is bold, brave, and fiercely loyal."
        ),
        "family": "Otis Césaire (father), Marlena Césaire (mother), Ella & Etta (twin sisters), Nora (older sister)",
        "friends": "Marinette (best friend), Nino, Adrien, Chloé",
        "likes": "Journalism, blogging, superheroes, her Ladyblog",
        "voice": "Carrie Keranen (EN), Fanny Bloc (FR)",
        "fun_fact": "Alya eventually learns Marinette's identity as Ladybug and becomes a trusted ally who holds the Fox Miraculous permanently.",
    },
    "nino": {
        "name": "Nino Lahiffe",
        "alias": "Carapace",
        "also_known_as": [],
        "age": 14,
        "birthday": "June 2",
        "school": "Collège Françoise Dupont",
        "class": "Ms. Bustier's class",
        "nationality": "French-Moroccan",
        "miraculous": "Turtle Miraculous (Bracelet)",
        "kwami": "Wayzz",
        "power": "Shell-ter",
        "weapon": "Shield",
        "color": 0x2D6A4F,
        "emoji": "🐢",
        "image": f"{WIKI}/Carapace_Square.png",
        "image_alt": f"{WIKI}/Nino_Lahiffe_Square.png",
        "description": (
            "Nino Lahiffe is Adrien's best friend and a passionate DJ. "
            "He is laid-back, friendly, and loves music. As Carapace, he wields "
            "a protective force field called Shell-ter. He is Alya's boyfriend."
        ),
        "family": "Parents and younger siblings",
        "friends": "Adrien (best friend), Alya (girlfriend), Marinette",
        "likes": "Music, DJing, movies, video games",
        "voice": "Ben Diskin (EN), Fédéric Pommier (FR)",
        "fun_fact": "Nino was the first civilian to be akumatized, becoming 'The Bubbler' in the episode of the same name.",
    },
    "chloe": {
        "name": "Chloé Bourgeois",
        "alias": "Queen Bee",
        "also_known_as": ["Queen Wasp", "Miracle Queen"],
        "age": 14,
        "birthday": "Unknown",
        "school": "Collège Françoise Dupont",
        "class": "Ms. Bustier's class",
        "nationality": "French",
        "miraculous": "Bee Miraculous (Comb)",
        "kwami": "Pollen",
        "power": "Venom",
        "weapon": "Spinning top",
        "color": 0xFFD700,
        "emoji": "🐝",
        "image": f"{WIKI}/Queen_Bee_Square.png",
        "image_alt": f"{WIKI}/Chlo%C3%A9_Bourgeois_Square.png",
        "description": (
            "Chloé Bourgeois is the mayor's daughter and the class bully — spoiled, "
            "arrogant, and obsessed with Ladybug. As Queen Bee, she has the power to "
            "paralyze enemies. She was stripped of the Bee Miraculous after revealing "
            "her identity and eventually turned fully villainous as Miracle Queen."
        ),
        "family": "André Bourgeois (father), Audrey Bourgeois (mother), Zoé Lee (half-sister)",
        "friends": "Sabrina Raincomprix (lackey), Adrien (childhood friend)",
        "likes": "Fashion, shopping, Ladybug, being the center of attention",
        "voice": "Selah Victor (EN), Christa Théret (FR)",
        "fun_fact": "Chloé has a half-sister named Zoé who later becomes the new Vesperia. Chloé became the villain Miracle Queen in Season 3.",
    },
    "zoe": {
        "name": "Zoé Lee",
        "alias": "Vesperia",
        "also_known_as": [],
        "age": 14,
        "birthday": "Unknown",
        "school": "Collège Françoise Dupont",
        "class": "Ms. Bustier's class",
        "nationality": "American-French",
        "miraculous": "Bee Miraculous (Comb)",
        "kwami": "Pollen",
        "power": "Venom",
        "weapon": "Spinning top",
        "color": 0xFFD700,
        "emoji": "🐝",
        "image": f"{WIKI}/Vesperia_Square.png",
        "image_alt": f"{WIKI}/Zo%C3%A9_Lee_Square.png",
        "description": (
            "Zoé Lee is Chloé's half-sister who moved from New York to Paris. "
            "Unlike Chloé, she is kind, down-to-earth, and genuine. She became "
            "the new permanent wielder of the Bee Miraculous as Vesperia."
        ),
        "family": "Audrey Bourgeois (mother), André Bourgeois (step-father), Chloé Bourgeois (half-sister)",
        "friends": "Marinette, Alya, the class",
        "likes": "Acting, kindness, fitting in",
        "voice": "Zoe Slusar (EN)",
        "fun_fact": "Zoé originally lived in New York with her father. She was bullied by Chloé before their sisterly bond was established.",
    },
    "luka": {
        "name": "Luka Couffaine",
        "alias": "Viperion",
        "also_known_as": [],
        "age": 15,
        "birthday": "Unknown",
        "school": "Not enrolled (homeschooled)",
        "class": "N/A",
        "nationality": "French",
        "miraculous": "Snake Miraculous (Bracelet)",
        "kwami": "Sass",
        "power": "Second Chance",
        "weapon": "Lyre",
        "color": 0x00838F,
        "emoji": "🐍",
        "image": f"{WIKI}/Viperion_Square.png",
        "image_alt": f"{WIKI}/Luka_Couffaine_Square.png",
        "description": (
            "Luka Couffaine is a calm, empathetic musician who lives on a houseboat. "
            "He is Juleka's twin brother and plays guitar in the band Kitty Section. "
            "As Viperion, he can rewind time by five minutes. He had romantic feelings "
            "for Marinette and briefly dated her."
        ),
        "family": "Anarka Couffaine (mother), Juleka Couffaine (twin sister)",
        "friends": "Juleka, Rose, Marinette, Ivan",
        "likes": "Music, guitar, reading people's emotions",
        "voice": "Austin Lee Matthews (EN)",
        "fun_fact": "Luka can 'read' people's emotions and translate them into music. He is one of the few people who figured out Marinette liked Adrien.",
    },
    "kagami": {
        "name": "Kagami Tsurugi",
        "alias": "Ryuko",
        "also_known_as": [],
        "age": 14,
        "birthday": "Unknown",
        "school": "Collège Françoise Dupont",
        "class": "Ms. Bustier's class",
        "nationality": "Japanese-French",
        "miraculous": "Dragon Miraculous (Earrings)",
        "kwami": "Longg",
        "power": "Elemental powers (water, lightning, wind)",
        "weapon": "Sword",
        "color": 0x003366,
        "emoji": "🐉",
        "image": f"{WIKI}/Ryuko_Square.png",
        "image_alt": f"{WIKI}/Kagami_Tsurugi_Square.png",
        "description": (
            "Kagami Tsurugi is a skilled fencer and Adrien's friend. Serious, disciplined, "
            "and fiercely competitive, she was raised by a strict single mother. As Ryuko, "
            "she wields elemental dragon powers. She briefly dated Adrien."
        ),
        "family": "Tomoe Tsurugi (mother)",
        "friends": "Adrien, Marinette, Luka",
        "likes": "Fencing, discipline, Japanese culture",
        "voice": "Caitlynne Medrek (EN)",
        "fun_fact": "Kagami's mother Tomoe is visually impaired and wears contact lenses with cameras. Kagami was raised with strict samurai values.",
    },
    "gabriel": {
        "name": "Gabriel Agreste",
        "alias": "Hawk Moth / Shadow Moth",
        "also_known_as": ["Monarch", "The Collector"],
        "age": "Adult",
        "birthday": "Unknown",
        "school": "N/A",
        "class": "N/A",
        "nationality": "French",
        "miraculous": "Butterfly Miraculous (Brooch) + Peacock Miraculous (Brooch)",
        "kwami": "Nooroo (Butterfly) + Duusu (Peacock)",
        "power": "Akumatization, Amokization",
        "weapon": "Cane",
        "color": 0x6A0DAD,
        "emoji": "🦋",
        "image": f"{WIKI}/Hawk_Moth_Square.png",
        "image_alt": f"{WIKI}/Gabriel_Agreste_Square.png",
        "description": (
            "Gabriel Agreste is a famous fashion designer and the main antagonist. "
            "As Hawk Moth, he akumatizes people's negative emotions to create supervillains. "
            "His goal is to obtain Ladybug's and Cat Noir's Miraculouses to revive his comatose wife Emilie. "
            "He later combines both the Butterfly and Peacock Miraculouses to become Shadow Moth."
        ),
        "family": "Emilie Agreste (wife, comatose), Adrien Agreste (son), Félix (nephew)",
        "friends": "Nathalie Sancoeur (assistant)",
        "likes": "Fashion, control, his wife, his son (in his own way)",
        "voice": "Keith Silverstein (EN), Antoine Tomé (FR)",
        "fun_fact": "Gabriel wears the damaged Peacock Miraculous which slowly deteriorates his health. His ultimate goal is to make a wish using both Ladybug and Cat Noir's Miraculouses.",
    },
    "nathalie": {
        "name": "Nathalie Sancoeur",
        "alias": "Mayura",
        "also_known_as": [],
        "age": "Adult",
        "birthday": "Unknown",
        "school": "N/A",
        "class": "N/A",
        "nationality": "French",
        "miraculous": "Peacock Miraculous (Brooch)",
        "kwami": "Duusu",
        "power": "Amokization (creates sentimonsters)",
        "weapon": "Fan",
        "color": 0x005F73,
        "emoji": "🦚",
        "image": f"{WIKI}/Mayura_Square.png",
        "image_alt": f"{WIKI}/Nathalie_Sancoeur_Square.png",
        "description": (
            "Nathalie Sancoeur is Gabriel Agreste's loyal personal assistant. "
            "As Mayura, she uses the damaged Peacock Miraculous to create sentimonsters — "
            "creatures made from charged objects. The damaged Miraculous slowly harms her health."
        ),
        "family": "Unknown",
        "friends": "Gabriel Agreste (employer, deeply loyal to)",
        "likes": "Order, efficiency, serving Gabriel",
        "voice": "Sabrina Weisz (EN)",
        "fun_fact": "Because the Peacock Miraculous is damaged, using it slowly weakens Nathalie, causing her to frequently fall ill.",
    },
    "lila": {
        "name": "Lila Rossi",
        "alias": "Volpina (akumatized) / Oni-Chan",
        "also_known_as": ["Chameleon"],
        "age": 14,
        "birthday": "Unknown",
        "school": "Collège Françoise Dupont",
        "class": "Ms. Bustier's class",
        "nationality": "Italian-French",
        "miraculous": "None (not a holder)",
        "kwami": "None",
        "power": "Deception (non-superhero)",
        "weapon": "None",
        "color": 0xB22222,
        "emoji": "🦊",
        "image": f"{WIKI}/Lila_Rossi_Square.png",
        "image_alt": f"{WIKI}/Volpina_Square.png",
        "description": (
            "Lila Rossi is a manipulative and compulsive liar who transferred to Marinette's class. "
            "She fakes friendships and fabricates stories to gain popularity. She is one of Marinette's "
            "main antagonists at school. She has a grudge against Ladybug and works with Hawk Moth."
        ),
        "family": "Italian diplomat mother",
        "friends": "Fake friendships with the whole class (except Marinette and Adrien)",
        "likes": "Lying, manipulation, getting what she wants, Adrien",
        "voice": "Faye Mata (EN)",
        "fun_fact": "Lila was the first person Adrien explicitly called out for lying, though he still refused to expose her to prevent akumatization.",
    },
    "juleka": {
        "name": "Juleka Couffaine",
        "alias": "Purple Tigress",
        "also_known_as": [],
        "age": 14,
        "birthday": "Unknown",
        "school": "Collège Françoise Dupont",
        "class": "Ms. Bustier's class",
        "nationality": "French",
        "miraculous": "Tiger Miraculous (Ring)",
        "kwami": "Roaar",
        "power": "Unknown (Roaar's power)",
        "weapon": "Unknown",
        "color": 0x800080,
        "emoji": "🐯",
        "image": f"{WIKI}/Purple_Tigress_Square.png",
        "image_alt": f"{WIKI}/Juleka_Couffaine_Square.png",
        "description": (
            "Juleka Couffaine is Luka's twin sister, a shy and goth-styled girl. "
            "She is Rose's best friend and girlfriend. She becomes the superhero Purple Tigress "
            "wielding the Tiger Miraculous."
        ),
        "family": "Anarka Couffaine (mother), Luka Couffaine (twin brother)",
        "friends": "Rose Lavillant (girlfriend), Luka, the band Kitty Section",
        "likes": "Dark aesthetics, music, Rose",
        "voice": "Kimberly Woods (EN)",
        "fun_fact": "Juleka suffers from what the class calls the 'Juleka Curse' — she always gets cut out of class photos. Rose helps her overcome this.",
    },
    "rose": {
        "name": "Rose Lavillant",
        "alias": "Pigella",
        "also_known_as": [],
        "age": 14,
        "birthday": "Unknown",
        "school": "Collège Françoise Dupont",
        "class": "Ms. Bustier's class",
        "nationality": "French",
        "miraculous": "Pig Miraculous (Anklet)",
        "kwami": "Daizzi",
        "power": "Gift (shows target their greatest wish)",
        "weapon": "Purse",
        "color": 0xFF69B4,
        "emoji": "🐷",
        "image": f"{WIKI}/Pigella_Square.png",
        "image_alt": f"{WIKI}/Rose_Lavillant_Square.png",
        "description": (
            "Rose Lavillant is a cheerful, sweet, and optimistic girl. "
            "She is Juleka's best friend and girlfriend. As Pigella, she can show "
            "enemies their greatest wish, temporarily immobilizing them with joy."
        ),
        "family": "Unknown",
        "friends": "Juleka Couffaine (girlfriend), Kitty Section bandmates",
        "likes": "Pink, cuteness, her friends, positivity",
        "voice": "Elsie Lovelock (EN)",
        "fun_fact": "Rose has a hidden strength — despite her gentle nature, she stood up to Chloé on multiple occasions.",
    },
    "ivan": {
        "name": "Ivan Bruel",
        "alias": "Minotaurox",
        "also_known_as": [],
        "age": 15,
        "birthday": "Unknown",
        "school": "Collège Françoise Dupont",
        "class": "Ms. Bustier's class",
        "nationality": "French",
        "miraculous": "Ox Miraculous (Belt)",
        "kwami": "Stompp",
        "power": "Unknown (Stompp's power — resilience)",
        "weapon": "Unknown",
        "color": 0x8B0000,
        "emoji": "🐂",
        "image": f"{WIKI}/Minotaurox_Square.png",
        "image_alt": f"{WIKI}/Ivan_Bruel_Square.png",
        "description": (
            "Ivan Bruel is a large but gentle student who plays bass in Kitty Section. "
            "He is Mylène's boyfriend. As Minotaurox, he wields the Ox Miraculous. "
            "He has a gentle heart beneath his intimidating appearance."
        ),
        "family": "Unknown",
        "friends": "Mylène Haprèle (girlfriend), Kim, the class",
        "likes": "Heavy metal, Mylène, his band",
        "voice": "Matt Mercer (EN)",
        "fun_fact": "Ivan was one of the earliest akumatized characters, becoming 'Stoneheart' in the very first episode.",
    },
    "felix": {
        "name": "Félix Graham de Vanily",
        "alias": "Argos / Félix (as villain)",
        "also_known_as": ["Gold Bug (briefly)"],
        "age": 14,
        "birthday": "Unknown",
        "school": "N/A (UK)",
        "class": "N/A",
        "nationality": "British-French",
        "miraculous": "Peacock Miraculous / Multiple",
        "kwami": "Duusu (and others stolen)",
        "power": "Amokization + others",
        "weapon": "Various",
        "color": 0x2C2C54,
        "emoji": "🦸",
        "image": f"{WIKI}/F%C3%A9lix_Graham_de_Vanily_Square.png",
        "image_alt": f"{WIKI}/Argos_Square.png",
        "description": (
            "Félix Graham de Vanily is Adrien's cousin and an antagonist in later seasons. "
            "He is manipulative, calculating, and morally grey. He stole several Miraculouses "
            "for his own mysterious goals related to his mother and a wish."
        ),
        "family": "Amelie Graham de Vanily (mother), Adrien (cousin), Gabriel (uncle)",
        "friends": "Very few — operates alone",
        "likes": "Achieving his goals, his mother",
        "voice": "Bryce Papenbrook (EN) — same VA as Adrien",
        "fun_fact": "Félix looks almost identical to Adrien, which he uses to impersonate him. He has his own Miraculous-related agenda.",
    },
    "master fu": {
        "name": "Wang Fu",
        "alias": "Jade Turtle / The Guardian",
        "also_known_as": ["Master Fu"],
        "age": "186 (kept alive by the Miraculous)",
        "birthday": "Unknown",
        "school": "N/A",
        "class": "N/A",
        "nationality": "Chinese",
        "miraculous": "Turtle Miraculous (Bracelet) — formerly",
        "kwami": "Wayzz — formerly",
        "power": "Shell-ter — formerly",
        "weapon": "Shield — formerly",
        "color": 0x2D6A4F,
        "emoji": "🐢",
        "image": f"{WIKI}/Wang_Fu_Square.png",
        "image_alt": f"{WIKI}/Jade_Turtle_Square.png",
        "description": (
            "Wang Fu is the last known Guardian of the Miraculouses — an ancient order "
            "that protects the magical jewels. He is over 186 years old, kept alive by the "
            "power of the Turtle Miraculous. He eventually passes guardianship to Marinette "
            "and loses his memories of it all."
        ),
        "family": "Unknown",
        "friends": "Marinette (successor), Marianne Lenoir (lost love)",
        "likes": "Chinese chess, wisdom, protecting the Miraculouses",
        "voice": "Paul St. Peter (EN)",
        "fun_fact": "Master Fu accidentally destroyed the Order of the Guardians as a child, making him the sole survivor. He is reunited with his lost love Marianne before losing his memories.",
    },
    "alix": {
        "name": "Alix Kubdel",
        "alias": "Bunnyx",
        "also_known_as": ["Timebreaker (akumatized)"],
        "age": 14,
        "birthday": "February 27",
        "school": "Collège Françoise Dupont",
        "class": "Ms. Bustier's class",
        "nationality": "French",
        "miraculous": "Rabbit Miraculous (Watch)",
        "kwami": "Fluff",
        "power": "Burrow (time travel portals)",
        "weapon": "Umbrella/Hammer",
        "color": 0xC8A2C8,
        "emoji": "🐰",
        "image": f"{WIKI}/Bunnyx_Square.png",
        "image_alt": f"{WIKI}/Alix_Kubdel_Square.png",
        "description": (
            "Alix Kubdel is a tough, tomboyish skater girl. In the future, she becomes "
            "the superhero Bunnyx, a time-travelling hero who uses portals through time. "
            "Her ancestor's pocket watch is the Rabbit Miraculous."
        ),
        "family": "Mr. Kubdel (father), Jalil Kubdel (older brother)",
        "friends": "Kim, the class",
        "likes": "Skateboarding, racing, history (reluctantly — her family is obsessed with it)",
        "voice": "Cassandra Lee Morris (EN)",
        "fun_fact": "Future Bunnyx operates from a 'burrow' — a home inside the time stream itself. She has seen countless timelines.",
    },
    "kim": {
        "name": "Lê Chiến Kim",
        "alias": "King Monkey",
        "also_known_as": ["Dark Cupid (akumatized)"],
        "age": 14,
        "birthday": "Unknown",
        "school": "Collège Françoise Dupont",
        "class": "Ms. Bustier's class",
        "nationality": "French-Vietnamese",
        "miraculous": "Monkey Miraculous (Circlet)",
        "kwami": "Xuppu",
        "power": "Uproar (makes powers malfunction)",
        "weapon": "Staff",
        "color": 0xFFAA00,
        "emoji": "🐒",
        "image": f"{WIKI}/King_Monkey_Square.png",
        "image_alt": f"{WIKI}/L%C3%AA_Chi%E1%BA%BFn_Kim_Square.png",
        "description": (
            "Kim is an athletic, competitive, and sometimes brash student who loves "
            "dares and sports. As King Monkey, his Uproar power causes any superpower "
            "it hits to go completely haywire."
        ),
        "family": "Unknown",
        "friends": "Max Kante (best friend), Ivan, Alix",
        "likes": "Sports, dares, competitions, Ondine",
        "voice": "Alec Medlock (EN)",
        "fun_fact": "Kim once tried to confess his feelings to Chloé with chocolates on Valentine's Day, which she rejected — leading to his akumatization as Dark Cupid.",
    },
    "max": {
        "name": "Max Kante",
        "alias": "Pegasus",
        "also_known_as": [],
        "age": 14,
        "birthday": "Unknown",
        "school": "Collège Françoise Dupont",
        "class": "Ms. Bustier's class",
        "nationality": "French-African",
        "miraculous": "Horse Miraculous (Glasses)",
        "kwami": "Kaalki",
        "power": "Voyage (teleportation portals)",
        "weapon": "Shield",
        "color": 0x8B4513,
        "emoji": "🐴",
        "image": f"{WIKI}/Pegasus_Square.png",
        "image_alt": f"{WIKI}/Max_Kant%C3%A9_Square.png",
        "description": (
            "Max Kante is a tech genius and the smartest student in his class. "
            "He created Markov, a sentient AI robot. As Pegasus, he can open teleportation "
            "portals to any location."
        ),
        "family": "Unknown",
        "friends": "Kim (best friend), Markov (AI creation)",
        "likes": "Technology, coding, video games, logic",
        "voice": "Ben Diskin (EN)",
        "fun_fact": "Max built a fully sentient AI named Markov, who has been akumatized and also helped the heroes. Max was once disqualified from a gaming competition due to being 'too good'.",
    },
}

SEARCH_ALIASES = {
    "ladybug": "marinette",
    "cat noir": "adrien",
    "catnoir": "adrien",
    "cat": "adrien",
    "rena rouge": "alya",
    "carapace": "nino",
    "queen bee": "chloe",
    "chloe": "chloe",
    "chloé": "chloe",
    "vesperia": "zoe",
    "zoé": "zoe",
    "viperion": "luka",
    "ryuko": "kagami",
    "hawk moth": "gabriel",
    "hawkmoth": "gabriel",
    "shadow moth": "gabriel",
    "shadowmoth": "gabriel",
    "gabriel agreste": "gabriel",
    "mayura": "nathalie",
    "nathalie": "nathalie",
    "lila rossi": "lila",
    "volpina": "lila",
    "purple tigress": "juleka",
    "pigella": "rose",
    "minotaurox": "ivan",
    "argos": "felix",
    "félix": "felix",
    "wang fu": "master fu",
    "waang fu": "master fu",
    "bunnyx": "alix",
    "king monkey": "kim",
    "pegasus": "max",
    "multimouse": "marinette",
    "mister bug": "adrien",
    "marinette dupain-cheng": "marinette",
    "adrien agreste": "adrien",
    "alya césaire": "alya",
    "nino lahiffe": "nino",
    "luka couffaine": "luka",
    "kagami tsurugi": "kagami",
    "juleka couffaine": "juleka",
    "rose lavillant": "rose",
    "ivan bruel": "ivan",
    "alix kubdel": "alix",
    "lê chiến kim": "kim",
    "max kante": "max",
    "max kanté": "max",
}


def find_character(query: str) -> Optional[dict]:
    q = query.lower().strip()
    if q in CHARACTERS:
        return CHARACTERS[q]
    if q in SEARCH_ALIASES:
        return CHARACTERS[SEARCH_ALIASES[q]]
    for key in CHARACTERS:
        if q in key:
            return CHARACTERS[key]
    for alias, key in SEARCH_ALIASES.items():
        if q in alias:
            return CHARACTERS[key]
    return None


def build_character_embed(char: dict) -> discord.Embed:
    embed = discord.Embed(
        title=f"{char['emoji']} {char['name']}",
        description=char["description"],
        color=char["color"],
    )
    embed.add_field(name="🦸 Hero / Villain Name", value=char["alias"], inline=True)
    if char.get("also_known_as"):
        embed.add_field(name="🔄 Also Known As", value=", ".join(char["also_known_as"]), inline=True)
    embed.add_field(name="🎂 Age", value=str(char["age"]), inline=True)
    if char.get("birthday") and char["birthday"] != "Unknown":
        embed.add_field(name="📅 Birthday", value=char["birthday"], inline=True)
    embed.add_field(name="🌍 Nationality", value=char["nationality"], inline=True)
    if char.get("school") and char["school"] != "N/A":
        embed.add_field(name="🏫 School", value=char["school"], inline=True)
    embed.add_field(name="✨ Miraculous", value=char["miraculous"], inline=True)
    embed.add_field(name="🦋 Kwami", value=char["kwami"], inline=True)
    embed.add_field(name="⚡ Power", value=char["power"], inline=True)
    if char.get("weapon") and char["weapon"] not in ("Unknown", "None", "Various"):
        embed.add_field(name="⚔️ Weapon", value=char["weapon"], inline=True)
    embed.add_field(name="👨‍👩‍👧 Family", value=char["family"], inline=False)
    embed.add_field(name="👥 Friends / Relationships", value=char["friends"], inline=False)
    embed.add_field(name="❤️ Likes", value=char["likes"], inline=False)
    if char.get("voice"):
        embed.add_field(name="🎙️ Voice Actor", value=char["voice"], inline=False)
    if char.get("fun_fact"):
        embed.add_field(name="💡 Fun Fact", value=char["fun_fact"], inline=False)
    if char.get("image"):
        embed.set_image(url=char["image"])
    if char.get("image_alt"):
        embed.set_thumbnail(url=char["image_alt"])
    embed.set_footer(
        text="Miraculous: Tales of Ladybug & Cat Noir",
        icon_url=f"{WIKI}/Miraculous_Ladybug_logo.png",
    )
    return embed


class MiraculousCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    miraculous_group = app_commands.Group(name="miraculous", description="Miraculous Ladybug info commands")

    @miraculous_group.command(name="character", description="Look up a Miraculous Ladybug character!")
    @app_commands.describe(name="Character name or hero/villain alias")
    async def character(self, interaction: discord.Interaction, name: str):
        await interaction.response.defer()
        char = find_character(name)
        if not char:
            all_names = ", ".join(f"`{c['name']}`" for c in CHARACTERS.values())
            await interaction.followup.send(
                f"❌ Character **{name}** not found.\n\nAvailable characters: {all_names}",
                ephemeral=True,
            )
            return
        embed = build_character_embed(char)
        await interaction.followup.send(embed=embed)

    @miraculous_group.command(name="list", description="List all available Miraculous Ladybug characters.")
    async def list_characters(self, interaction: discord.Interaction):
        await interaction.response.defer()
        embed = discord.Embed(
            title="✨ Miraculous Ladybug Characters",
            description="Use `/miraculous character [name]` to look up any character!",
            color=0xFF0000,
        )
        embed.set_thumbnail(url=f"{WIKI}/Ladybug_Square.png")

        villain_keys = {"gabriel", "nathalie", "lila", "felix"}
        neutral_keys = {"master fu"}

        hero_lines = [
            f"{c['emoji']} **{c['name']}** — *{c['alias']}*"
            for k, c in CHARACTERS.items()
            if k not in villain_keys and k not in neutral_keys
        ]
        villain_lines = [
            f"{c['emoji']} **{c['name']}** — *{c['alias']}*"
            for k, c in CHARACTERS.items()
            if k in villain_keys
        ]
        other_lines = [
            f"{c['emoji']} **{c['name']}** — *{c['alias']}*"
            for k, c in CHARACTERS.items()
            if k in neutral_keys
        ]

        embed.add_field(name="🦸 Heroes", value="\n".join(hero_lines) or "None", inline=False)
        embed.add_field(name="🦹 Villains & Antagonists", value="\n".join(villain_lines + other_lines), inline=False)
        embed.set_footer(text=f"{len(CHARACTERS)} characters available • Miraculous: Tales of Ladybug & Cat Noir")
        await interaction.followup.send(embed=embed)

    @miraculous_group.command(name="random", description="Get info on a random Miraculous Ladybug character!")
    async def random_character(self, interaction: discord.Interaction):
        await interaction.response.defer()
        import random as _random
        key = _random.choice(list(CHARACTERS.keys()))
        char = CHARACTERS[key]
        embed = build_character_embed(char)
        embed.title = f"🎲 Random Character: {char['emoji']} {char['name']}"
        await interaction.followup.send(embed=embed)

    @miraculous_group.command(name="kwami", description="Find a character by their kwami!")
    @app_commands.describe(kwami_name="Name of the kwami (e.g. Tikki, Plagg, Wayzz)")
    async def by_kwami(self, interaction: discord.Interaction, kwami_name: str):
        await interaction.response.defer()
        q = kwami_name.lower().strip()
        match = None
        for char in CHARACTERS.values():
            kwami_val = char.get("kwami", "")
            if kwami_val and "None" not in kwami_val and q in kwami_val.lower():
                match = char
                break
        if not match:
            await interaction.followup.send(
                f"❌ No character found with kwami named **{kwami_name}**.", ephemeral=True
            )
            return
        embed = build_character_embed(match)
        await interaction.followup.send(embed=embed)

    @miraculous_group.command(name="compare", description="Compare two Miraculous Ladybug characters side by side!")
    @app_commands.describe(character1="First character name", character2="Second character name")
    async def compare(self, interaction: discord.Interaction, character1: str, character2: str):
        await interaction.response.defer()
        c1 = find_character(character1)
        c2 = find_character(character2)

        if not c1:
            await interaction.followup.send(f"❌ Character **{character1}** not found.", ephemeral=True)
            return
        if not c2:
            await interaction.followup.send(f"❌ Character **{character2}** not found.", ephemeral=True)
            return
        if c1 is c2:
            await interaction.followup.send("❌ Please choose two different characters!", ephemeral=True)
            return

        embed = discord.Embed(
            title=f"⚔️ {c1['name']} vs {c2['name']}",
            color=0xFF69B4,
        )
        embed.add_field(
            name=f"{c1['emoji']} {c1['name']}",
            value=(
                f"**Alias:** {c1['alias']}\n"
                f"**Miraculous:** {c1['miraculous']}\n"
                f"**Kwami:** {c1['kwami']}\n"
                f"**Power:** {c1['power']}\n"
                f"**Nationality:** {c1['nationality']}\n"
                f"**Age:** {c1['age']}"
            ),
            inline=True,
        )
        embed.add_field(name="\u200b", value="\u200b", inline=True)
        embed.add_field(
            name=f"{c2['emoji']} {c2['name']}",
            value=(
                f"**Alias:** {c2['alias']}\n"
                f"**Miraculous:** {c2['miraculous']}\n"
                f"**Kwami:** {c2['kwami']}\n"
                f"**Power:** {c2['power']}\n"
                f"**Nationality:** {c2['nationality']}\n"
                f"**Age:** {c2['age']}"
            ),
            inline=True,
        )
        if c1.get("image"):
            embed.set_thumbnail(url=c1["image"])
        if c2.get("image"):
            embed.set_image(url=c2["image"])
        embed.set_footer(text="Miraculous: Tales of Ladybug & Cat Noir")
        await interaction.followup.send(embed=embed)

    @character.autocomplete("name")
    async def character_autocomplete(self, interaction: discord.Interaction, current: str):
        current_lower = current.lower()
        results = []
        seen = set()
        for key, char in CHARACTERS.items():
            if current_lower in char["name"].lower() or current_lower in char["alias"].lower():
                if key not in seen:
                    seen.add(key)
                    results.append(app_commands.Choice(name=f"{char['name']} ({char['alias']})", value=char["name"]))
        for alias, key in SEARCH_ALIASES.items():
            if current_lower in alias and key not in seen:
                seen.add(key)
                char = CHARACTERS[key]
                results.append(app_commands.Choice(name=f"{char['name']} ({char['alias']})", value=char["name"]))
        return results[:25]

    @by_kwami.autocomplete("kwami_name")
    async def kwami_autocomplete(self, interaction: discord.Interaction, current: str):
        seen = set()
        kwami_names = []
        for char in CHARACTERS.values():
            kw = char.get("kwami", "")
            if kw and "None" not in kw:
                for k in kw.split(" + "):
                    k = k.strip().split(" (")[0]
                    if k not in seen and current.lower() in k.lower():
                        seen.add(k)
                        kwami_names.append(app_commands.Choice(name=k, value=k))
        return kwami_names[:25]


async def setup(bot: commands.Bot):
    await bot.add_cog(MiraculousCog(bot))
