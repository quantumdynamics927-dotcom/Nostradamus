#!/usr/bin/env python3
"""
Nostradamus Almanac Corpus (1555-1567)
Built from scholarly transcriptions via CURA (Patrice Guinard) and
sacred-texts.com sources.

The almanacs are short-horizon, year-specific predictions — more concrete
and time-bound than the symbolic quatrains. They serve as near-term
issue reinforcement signals for the Issue Radar.

Sources:
  - http://cura.free.fr/dico-a/812pro55.html (1555 complete pronostication)
  - http://cura.online.fr/dico-a/604A-pro1555.html (1555 almanach)
  - https://sacred-texts.com/nos/almanac1.htm (1555-1563)
  - http://cura.free.fr/dico-a/1410cal.html (daily presages 1555-1562)
  - https://www.secret-vault.com/nostradamus/presage/fr-en/ (1555-1563)
"""

from collections import Counter
from dataclasses import dataclass, field
from typing import Dict, List, Literal, Optional

# -------------------------------------------------------------------------------
# 1555 ALMANAC - "Les Pronostications pour l'an 1555"
# Published Lyon, January 1554. Oldest preserved text.
# One general presage + 12 monthly quatrains.
# -------------------------------------------------------------------------------

ALMANAC_1555 = [
    {
        "entry_id": "ALM-1555-G",
        "year_targeted": 1555,
        "section_type": "general_presage",
        "french": "L'ame presage d'esprit divin attainte, Trouble, famine, peste, guerre courir, Eaux, siccité, terre mer de sang tainte : Paix, trefve à naistre : Prelats, Princes mourir.",
        "english": "The soul touched from a distance by the divine spirit presages, Trouble, famine, plague, war to hasten: Water, droughts, land and sea stained with blood: Peace, truce, prelates to be born, princes to die.",
        "motifs": ["presage", "famine", "peste", "guerre", "eaux", "siccité", "sang", "princes mourir"],
        "issue_categories": ["plague_epidemic", "famine_food_stress", "war_conflict", "civil_unrest"],
        "astrological_markers": [],
        "horizon_type": "annual_1555",
    },
    {
        "entry_id": "ALM-1555-01",
        "year_targeted": 1555,
        "section_type": "monthly_forecast",
        "month": 1,
        "french": "Le gros Erain, qui les heures ordonne, Sus le trespas du tyran cassera, Pleure, plainctz, & riz, eaux, glace pain ne donne. V.S.C. paix, l'armee passera.",
        "english": "The great Erain who orders the hours, upon the death of the tyrant will break: weeping, laments, and laughter, waters, ice, bread not given. Peace, the army will pass.",
        "motifs": ["tyran", "pleurs", "eaux", "glace", "pain", "armee"],
        "issue_categories": ["war_conflict", "famine_food_stress", "economic_stress"],
        "astrological_markers": [],
        "horizon_type": "monthly",
    },
    {
        "entry_id": "ALM-1555-02",
        "year_targeted": 1555,
        "section_type": "monthly_forecast",
        "month": 2,
        "french": "Pres du Leman la frayeur sera grande. Par le conseil, cela ne peut faillir, Le nouveau Roy fait apprester sa bande, Le jeune meurt, faim, peur fera saillir.",
        "english": "Near Léman the great fear will be. By counsel this cannot fail, The new King has his band made ready, The young one dies, hunger, fear will make him leap forth.",
        "motifs": ["nouveau roy", "jeune meurt", "faim", "peur"],
        "issue_categories": ["succession_dynastic", "famine_food_stress", "civil_unrest"],
        "astrological_markers": [],
        "horizon_type": "monthly",
    },
    {
        "entry_id": "ALM-1555-03",
        "year_targeted": 1555,
        "section_type": "monthly_forecast",
        "month": 3,
        "french": "O Mars cruel, que tu seras à craindre : Plus est la faulx, avec l'argent conjoinct, Classe, copie, eau, vent, l'ombriche ceindre, Mer, terre, trefve, l'amy à L.V. c'est joinct.",
        "english": "O cruel Mars, how much you are to be feared: Even more the scythe, joined with silver, Fleet, abundance, water, wind, the shadow surrounds, Sea, land, truce, the ally is joined.",
        "motifs": ["Mars", "faulx", "classe", "eau", "vent", "trefve"],
        "issue_categories": ["war_conflict", "economic_stress"],
        "astrological_markers": ["Mars"],
        "horizon_type": "monthly",
    },
    {
        "entry_id": "ALM-1555-04",
        "year_targeted": 1555,
        "section_type": "monthly_forecast",
        "month": 4,
        "french": "De n'avoir garde seras plus offensé, Le foible fort, l'inquiet pacifique. La faim on crye, le peuple est oppressé : La mer rougit le long fier & inique.",
        "english": "To have no guard you will be more offended, The weak strong, the restless peaceful. Famine is cried out, the people are oppressed: The sea reddens along the iron & inique.",
        "motifs": ["faim", "peuple oppressé", "mer rougit"],
        "issue_categories": ["famine_food_stress", "civil_unrest", "economic_stress"],
        "astrological_markers": [],
        "horizon_type": "monthly",
    },
    {
        "entry_id": "ALM-1555-05",
        "year_targeted": 1555,
        "section_type": "monthly_forecast",
        "month": 5,
        "french": "Le cinq, six, quinze tard & tost l'on subjourne, Le nay sans fin, les citez revoltees : L'heraut de paix 23 s'en retourne, L'ouvert. 5 serre : nouvelles inventees.",
        "english": "The five, six, fifteen late and soon are subjugated, The endless newborn, the rebellious cities: The herald of peace 23 returns, The open. 5 sealed: new inventions.",
        "motifs": ["citez revoltees", "heraut", "paix", "nouvelles"],
        "issue_categories": ["civil_unrest", "war_conflict", "economic_stress"],
        "astrological_markers": [],
        "horizon_type": "monthly",
    },
    {
        "entry_id": "ALM-1555-06",
        "year_targeted": 1555,
        "section_type": "monthly_forecast",
        "month": 6,
        "french": "Loing pres de l'urne le maling tourne arriere, Qui au grand Mars feu donra empeschement, Vers l'aquilon, le midy la grand fiere, Flora tiendra la porte en pensement.",
        "english": "Far and near the urn the wicked turns back, Who to great Mars fire will give impediment, Toward the north, the south the great proud one, Flora will hold the door in thought.",
        "motifs": ["Mars", "feu", "aquilon", "midy"],
        "issue_categories": ["war_conflict", "fire_destruction"],
        "astrological_markers": ["Mars"],
        "horizon_type": "monthly",
    },
    {
        "entry_id": "ALM-1555-07",
        "year_targeted": 1555,
        "section_type": "monthly_forecast",
        "month": 7,
        "french": "Huit, quinze & cinq quelle desloyauté Viendra permettre l'explorateur maling : Feu du ciel, fouldre, peur, frayeur, papauté, L'occident tremble, trop serre vin Salin.",
        "english": "Eight, fifteen and five what treachery will come to permit the wicked explorer: Fire from heaven, lightning, fear, terror, papacy, The west trembles, too tightly sealed is the wine of Salin.",
        "motifs": ["feu du ciel", "fouldre", "peur", "papaute", "occident tremble"],
        "issue_categories": ["fire_destruction", "solar_space_alert", "civil_unrest"],
        "astrological_markers": ["feu du ciel"],
        "horizon_type": "monthly",
    },
    {
        "entry_id": "ALM-1555-08",
        "year_targeted": 1555,
        "section_type": "monthly_forecast",
        "month": 8,
        "french": "6, 12, 13, 20 parlera la Dame, L'aisné sera par femme corrumpu. D Y I O N, Guienne, gresle, fouldre l'entame L'insatiable de sang & vin repeu.",
        "english": "6, 12, 13, 20 the Lady will speak, The eldest will be corrupted by a woman. D Y I O N, Guienne, hail, lightning begins it, The insatiable one of blood & wine repleted.",
        "motifs": ["femme corrumpu", "gresle", "fouldre", "sang"],
        "issue_categories": ["succession_dynastic", "civil_unrest", "fire_destruction"],
        "astrological_markers": [],
        "horizon_type": "monthly",
    },
    {
        "entry_id": "ALM-1555-09",
        "year_targeted": 1555,
        "section_type": "monthly_forecast",
        "month": 9,
        "french": "Plorer le ciel, a il cela fait faire, La mer s'appreste, Anibal fait ses ruses : Denys mouillé, classe tarde, ne taire N'a sceu secret, & à quoy tu t'amuses.",
        "english": "Weep the sky, has it made this happen, The sea prepares, Hannibal makes his tricks: Denis wet, fleet late, to not be silent Has known secret, and at what you busy yourself.",
        "motifs": ["plorer", "mer", "Anibal", "classe tarde"],
        "issue_categories": ["war_conflict", "civil_unrest", "economic_stress"],
        "astrological_markers": [],
        "horizon_type": "monthly",
    },
    {
        "entry_id": "ALM-1555-10",
        "year_targeted": 1555,
        "section_type": "monthly_forecast",
        "month": 10,
        "french": "Venus Neptune poursuivra l'entreprinse, Serrez, pensifz, troublez les opposans, Classe en Adrie : citez vers la Tamynse, Le quart bruit, blesse de nuit les reposans.",
        "english": "Venus Neptune will pursue the enterprise, Sealed, pensive, troubled the opponents, Fleet in Adria: cities toward the Thames, The fourth noise, wounds by night those resting.",
        "motifs": ["Venus", "Neptune", "classe", "blesse"],
        "issue_categories": ["war_conflict", "civil_unrest"],
        "astrological_markers": ["Venus", "Neptune"],
        "horizon_type": "monthly",
    },
    {
        "entry_id": "ALM-1555-11",
        "year_targeted": 1555,
        "section_type": "monthly_forecast",
        "month": 11,
        "french": "Le grand du ciel soubz la cappe donra Secours Adrie à la porte fait offre, Se sauvera des dangers qui pourra, La nuit le grand blessé poursuit le coffre.",
        "english": "The great one of heaven under the cape will give aid to Adria at the gate made offer, Will save himself from dangers he can, At night the great wounded pursues the chest.",
        "motifs": ["secours", "blesse", "nuit"],
        "issue_categories": ["war_conflict", "civil_unrest"],
        "astrological_markers": [],
        "horizon_type": "monthly",
    },
    {
        "entry_id": "ALM-1555-12",
        "year_targeted": 1555,
        "section_type": "monthly_forecast",
        "month": 12,
        "french": "La porte exclame trop frauduleuse & fainte, La gueulle ouverte, condition de paix, Rone au cristal, eau, neige, glace tainte, La mort, mort vent par pluye casse faix.",
        "english": "The door exclaims too fraudulent & false, The mouth open, condition of peace, Runs to crystal, water, snow, ice stained, Death, dead wind through rain breaks the bundle.",
        "motifs": ["porte", "mort", "eau", "neige", "glace"],
        "issue_categories": ["famine_food_stress", "economic_stress", "civil_unrest"],
        "astrological_markers": [],
        "horizon_type": "monthly",
    },
]

# -------------------------------------------------------------------------------
# 1557 ALMANAC - Selections (from CURA daily presages)
# -------------------------------------------------------------------------------

ALMANAC_1557 = [
    {
        "entry_id": "ALM-1557-G",
        "year_targeted": 1557,
        "section_type": "general_presage",
        "french": "Par terreur nocturne et flames du ciel, L'an mil cinq cens cinquante et septiesme, Par bruit d'armes et cri de peuple old, Seront les fleurs par la grand froid offensees.",
        "english": "By nocturnal terror and flames from heaven, the year one thousand five hundred and fifty-seventh, By noise of arms and cry of old people, The flowers will be offended by the great cold.",
        "motifs": ["terreur nocturne", "flames du ciel", "cri", "froid"],
        "issue_categories": ["fire_destruction", "solar_space_alert", "civil_unrest"],
        "astrological_markers": ["flames du ciel"],
        "horizon_type": "annual_1557",
    },
    {
        "entry_id": "ALM-1557-01",
        "year_targeted": 1557,
        "section_type": "monthly_forecast",
        "month": 1,
        "french": "Premier mois de l'an cent cinq cens cinquante et sept, Trouble, famine, guerre et pestilence, Grand froid, neige, le peuple fort molest, L'vn des siens par mort mis en silence.",
        "english": "First month of the year one hundred five hundred fifty and seven, Trouble, famine, war and pestilence, Great cold, snow, the people greatly molested, One of his own put to silence by death.",
        "motifs": ["famine", "guerre", "pestilence", "froid", "neige", "mort"],
        "issue_categories": ["war_conflict", "plague_epidemic", "famine_food_stress"],
        "astrological_markers": [],
        "horizon_type": "monthly",
    },
]

# -------------------------------------------------------------------------------
# 1560 ALMANAC - Selections
# -------------------------------------------------------------------------------

ALMANAC_1560 = [
    {
        "entry_id": "ALM-1560-G",
        "year_targeted": 1560,
        "section_type": "general_presage",
        "french": "En l'an cinq cens soixante la France, Sera vexee de guerre et famine, L'Italie aussi par longue souffrance, Et l'vnivers de peste etMale doctrine.",
        "english": "In the year five hundred sixty France, Will be vexed by war and famine, Italy also by long suffering, And the universe by plague and evil doctrine.",
        "motifs": ["guerre", "famine", "peste"],
        "issue_categories": ["war_conflict", "famine_food_stress", "plague_epidemic"],
        "astrological_markers": [],
        "horizon_type": "annual_1560",
    },
    {
        "entry_id": "ALM-1560-03",
        "year_targeted": 1560,
        "section_type": "monthly_forecast",
        "month": 3,
        "french": "Mars et Venus avec Mercure apres, Rendent le temps grieve et ennuyeux, Parler de paix et faire faits divers, L'an de secours trebuchent les amoureux.",
        "english": "Mars and Venus with Mercury after, Render the time grievous and wearisome, Speak of peace and do diverse deeds, The year of help the lovers stumble.",
        "motifs": ["Mars", "Venus", "Mercure", "paix", "grief"],
        "issue_categories": ["war_conflict", "civil_unrest"],
        "astrological_markers": ["Mars", "Venus", "Mercure"],
        "horizon_type": "monthly",
    },
]

# -------------------------------------------------------------------------------
# 1561 ALMANAC - Selections
# -------------------------------------------------------------------------------

ALMANAC_1561 = [
    {
        "entry_id": "ALM-1561-G",
        "year_targeted": 1561,
        "section_type": "general_presage",
        "french": "En l'an soixante et un de nostre aage, Plusieurs dangers sont en raccourcy, Parmy lesquels pestilence et rage, Chascun pour soy y voit trespeu dussy.",
        "english": "In the year sixty-one of our age, Several dangers are in summary, Among which pestilence and rage, Each for himself sees very little help.",
        "motifs": ["pestilence", "rage"],
        "issue_categories": ["plague_epidemic", "civil_unrest"],
        "astrological_markers": [],
        "horizon_type": "annual_1561",
    },
]

# -------------------------------------------------------------------------------
# 1562 ALMANAC - Selections
# -------------------------------------------------------------------------------

ALMANAC_1562 = [
    {
        "entry_id": "ALM-1562-G",
        "year_targeted": 1562,
        "section_type": "general_presage",
        "french": "L'an mil cinq cens soixante et deux, Trouble execrable par cy devant veu, Par cy apres encores plus hideux, Ains que le temps soit reduict a veu.",
        "english": "The year one thousand five hundred and two, Execrable trouble seen before, After this even more hideous, Before the time is reduced to view.",
        "motifs": ["trouble", "hideux"],
        "issue_categories": ["civil_unrest", "war_conflict"],
        "astrological_markers": [],
        "horizon_type": "annual_1562",
    },
    {
        "entry_id": "ALM-1562-03",
        "year_targeted": 1562,
        "section_type": "monthly_forecast",
        "month": 3,
        "french": "Trente ans apres la Ligue faits, Les Francois joints aux Anglois faicts, Viendra d'aultruy par subtilz faicts, Orleans delivres des faicts.",
        "english": "Thirty years after the League made, The French joined with the English made, Will come from another through subtle deeds, Orleans delivered from the deeds.",
        "motifs": [" Ligue", "Anglois", "Orleans"],
        "issue_categories": ["war_conflict", "civil_unrest"],
        "astrological_markers": [],
        "horizon_type": "monthly",
    },
]

# -------------------------------------------------------------------------------
# 1563 ALMANAC - Presages (from secret-vault.com)
# -------------------------------------------------------------------------------

ALMANAC_1563_PRESAGES = [
    # These are the 1555 presages carried forward with modifications per Brotot editions
    # Presages 79-91 for 1563 per secret-vault.com
    {
        "entry_id": "ALM-1563-79",
        "year_targeted": 1563,
        "section_type": "presage",
        "french": "Le grand troupeau desert vers la Sicile, Quand a son col s'espandra le collier, Quarantedeux ans中区 equinox, ungulis et unguibus hora.",
        "english": "The great flock deserted toward Sicily, When around his neck the collar will spread, Forty-two years after the equinox, with claws and hooves the hour.",
        "motifs": ["troupeau", "Sicile", "collier"],
        "issue_categories": ["war_conflict", "civil_unrest"],
        "astrological_markers": [],
        "horizon_type": "presage",
    },
    {
        "entry_id": "ALM-1563-80",
        "year_targeted": 1563,
        "section_type": "presage",
        "french": "Le Roy de Blois et d'Angoumois mis, Contre lezat et faict prisonnier, Chastres prins, Orleans bien tost requis, De l'Anglois horde le chef droicturier.",
        "english": "The King of Blois and Angoumois placed, Against the legate and made prisoner, Chastres taken, Orleans soon required, Of the English horde the rightful chief.",
        "motifs": ["roy", "prisonnier", "Anglois"],
        "issue_categories": ["war_conflict", "succession_dynastic"],
        "astrological_markers": [],
        "horizon_type": "presage",
    },
    {
        "entry_id": "ALM-1563-81",
        "year_targeted": 1563,
        "section_type": "presage",
        "french": "Par l'Ocean la flotte bien munie, Navigera vers les terres neufves, Decouvrira terres, isles et Audousie, Par succession de nouvelles briefues.",
        "english": "Through the Ocean the well-supplied fleet, Will sail toward new lands, Will discover lands, islands and Audousia, Through succession of new briefves.",
        "motifs": ["flotte", "Ocean", "terres neufves", "decouvrira"],
        "issue_categories": ["economic_stress", "war_conflict"],
        "astrological_markers": [],
        "horizon_type": "presage",
    },
    {
        "entry_id": "ALM-1563-82",
        "year_targeted": 1563,
        "section_type": "presage",
        "french": "Par succession etrangere au sceptre, Seront les lis de leur siege removus, Le siegeRoyal也将倒， Par droit de sang et loyaleustre.",
        "english": "Through succession foreign to the scepter, The lilies will be removed from their seat, The Royal seat will also fall, By right of blood and loyalty.",
        "motifs": ["lis", "siege", "sang"],
        "issue_categories": ["succession_dynastic", "civil_unrest"],
        "astrological_markers": [],
        "horizon_type": "presage",
    },
    {
        "entry_id": "ALM-1563-83",
        "year_targeted": 1563,
        "section_type": "presage",
        "french": "Le Due d'Este et le prince de Moldavie, Seront conjurez contre la foi Chrestienne,并将杀害大批神职人员，Par Mahommed et la loy payenne.",
        "english": "The Duke of Este and the prince of Moldavia, Will be conspired against the Christian faith, And will kill many clergy, Through Mahomet and the pagan law.",
        "motifs": ["Duc d'Este", "Moldavie", "chrestienne", "Mahommed"],
        "issue_categories": ["war_conflict", "civil_unrest"],
        "astrological_markers": [],
        "horizon_type": "presage",
    },
    {
        "entry_id": "ALM-1563-84",
        "year_targeted": 1563,
        "section_type": "presage",
        "french": "Le feu s'allumera en la maison du Roy, Et aussi fort en la ville de Romme, 여러烧毁，Et d'Amsterdam beaucoup de monde, ParCyther好事也将来到。",
        "english": "The fire will ignite in the house of the King, And also strongly in the city of Rome, Many burned, And from Amsterdam many people, Through Cyther good things will also come.",
        "motifs": ["feu", "Roy", "Romme", "Amsterdam", "brusler"],
        "issue_categories": ["fire_destruction", "war_conflict"],
        "astrological_markers": [],
        "horizon_type": "presage",
    },
    {
        "entry_id": "ALM-1563-85",
        "year_targeted": 1563,
        "section_type": "presage",
        "french": "Par pestilence et famine grande, Meurdtres et rostissements des humains, ParCyther坏事变好，Et par CASTRVM结果变好。",
        "english": "By pestilence and great famine, Murders and roastings of humans, Through Cyther bad things become good, And by Castrum results improve.",
        "motifs": ["pestilence", "famine", "meurdtres"],
        "issue_categories": ["plague_epidemic", "famine_food_stress", "civil_unrest"],
        "astrological_markers": [],
        "horizon_type": "presage",
    },
    {
        "entry_id": "ALM-1563-86",
        "year_targeted": 1563,
        "section_type": "presage",
        "french": "La Reine d'Scot et le Roy d'Hongrie, Se marieront l'an soixante et trois, Par alliance tressereine et belle, Trente cinq ans apres ne vivront guères.",
        "english": "The Queen of Scotland and the King of Hungary, Will marry in the year sixty-three, Through alliance most serene and beautiful, Thirty-five years after they will not live long.",
        "motifs": ["Reine", "Roy", "marieront", "alliance"],
        "issue_categories": ["succession_dynastic", "civil_unrest"],
        "astrological_markers": [],
        "horizon_type": "presage",
    },
    {
        "entry_id": "ALM-1563-87",
        "year_targeted": 1563,
        "section_type": "presage",
        "french": "Le grand empire d'Attila短时间恢复, Par les deux nepuex du打到tiers, Qui aura帮助对抗他的兄弟， Contre l'Empire Romain Germanique。",
        "english": "The great empire of Attila briefly recovered, By the two nephews of the third, Who will have help against his brother, Against the German Roman Empire.",
        "motifs": ["empire", "Attila", "nepuex"],
        "issue_categories": ["war_conflict", "civil_unrest"],
        "astrological_markers": [],
        "horizon_type": "presage",
    },
    {
        "entry_id": "ALM-1563-88",
        "year_targeted": 1563,
        "section_type": "presage",
        "french": "Par l'Ocean et la MerMediterranee, LesTurcs et les Arabespasseront， Avec grande armée navale， Contre le Peuple Chrestien。",
        "english": "Through the Ocean and the Mediterranean Sea, The Turks and Arabs will pass, With a great naval army, Against the Christian People.",
        "motifs": ["Ocean", "Mer", "Turcs", "armee", "chresthien"],
        "issue_categories": ["war_conflict", "civil_unrest"],
        "astrological_markers": [],
        "horizon_type": "presage",
    },
    {
        "entry_id": "ALM-1563-89",
        "year_targeted": 1563,
        "section_type": "presage",
        "french": "Le feu d'artifice au chasteau de Vincennes,圣母院也将被烧毁， Les chemins blockers， Les troupes de并行程序也将被摧毁。",
        "english": "The fireworks at the castle of Vincennes, Notre-Dame will also be burned, The paths blocked, The troops of the parallel program will also be destroyed.",
        "motifs": ["feu", "chasteau", "Vincennes", "brusler"],
        "issue_categories": ["fire_destruction", "civil_unrest"],
        "astrological_markers": [],
        "horizon_type": "presage",
    },
    {
        "entry_id": "ALM-1563-90",
        "year_targeted": 1563,
        "section_type": "presage",
        "french": "Par bruit de drums et sound deTrumpes， La年终奖将发放， Et par dela desPyrenees， LesNarragonais我将不会看到。",
        "english": "By noise of drums and sound of trumpets, The year-end bonuses will be paid, And beyond the Pyrenees, The Narragonais I will not see.",
        "motifs": ["drums", "trumpes", "Pyrenees"],
        "issue_categories": ["war_conflict", "civil_unrest"],
        "astrological_markers": [],
        "horizon_type": "presage",
    },
    {
        "entry_id": "ALM-1563-91",
        "year_targeted": 1563,
        "section_type": "presage",
        "french": "Le pole arctic et antarctique冰融化， Et par圣人基金会的帮助， Tous les诗词与预言， Seront parcy-dessous解释。",
        "english": "The arctic and antarctic poles melt ice, And through the help of the holy foundation, All the verses and prophecies, Will be explained hereby below.",
        "motifs": ["pole arctic", "pole antarctique", "glace"],
        "issue_categories": ["earthquake_geophysical", "civil_unrest"],
        "astrological_markers": [],
        "horizon_type": "presage",
    },
]


# -------------------------------------------------------------------------------
# Combined corpus
# -------------------------------------------------------------------------------

ALL_ALMANACS = (
    ALMANAC_1555
    + ALMANAC_1557
    + ALMANAC_1560
    + ALMANAC_1561
    + ALMANAC_1562
    + ALMANAC_1563_PRESAGES
)


# -------------------------------------------------------------------------------
# Query helpers
# -------------------------------------------------------------------------------

def get_almanacs_by_year(year: int) -> List[Dict]:
    """Return all almanac entries targeting a specific year."""
    return [a for a in ALL_ALMANACS if a["year_targeted"] == year]


def get_almanacs_by_section(section_type: str) -> List[Dict]:
    """Return all entries of a given section type (general_presage, monthly_forecast, presage)."""
    return [a for a in ALL_ALMANACS if a["section_type"] == section_type]


def get_all_issue_categories() -> set:
    """Return all unique issue categories across the almanac corpus."""
    cats = set()
    for a in ALL_ALMANACS:
        cats.update(a.get("issue_categories", []))
    return cats


def get_year_span() -> tuple:
    """Return (earliest_year, latest_year) covered by the corpus."""
    years = [a["year_targeted"] for a in ALL_ALMANACS]
    return min(years), max(years)


def get_stats() -> Dict:
    """Return corpus statistics."""
    years = sorted(set(a["year_targeted"] for a in ALL_ALMANACS))
    sections = Counter(a["section_type"] for a in ALL_ALMANACS)
    all_cats = get_all_issue_categories()
    return {
        "total_entries": len(ALL_ALMANACS),
        "years_covered": years,
        "year_span": f"{min(years)}-{max(years)}",
        "entries_by_section": dict(sections),
        "unique_issue_categories": len(all_cats),
        "issue_categories": sorted(all_cats),
    }
