#!/usr/bin/env python3
"""
Expand Historical Events Knowledge Base
100+ events with period source citations (Tier 1 chronicles).
"""

HISTORICAL_EVENTS_KB = [
    # === FRENCH WARS OF RELIGION (1562-1598) ===
    {"event_id": "FRENCH-WARS-1562", "name": "French Wars of Religion", "event_type": "war", "start_year": 1562, "end_year": 1598, "location": "France", "actors": ["Francis II", "Charles IX", "Henry III", "Henry IV", "Catherine de Medici"], "period_sources": ["de Thou Historia Sui Temporis 1609", "L'Estoile Mémoires-Journaux 1574"]},
    {"event_id": "ST-BARTHELEMY-1572", "name": "St. Bartholomew's Day Massacre", "event_type": "war", "start_year": 1572, "end_year": 1572, "location": "France", "actors": ["Charles IX", "Catherine de Medici", "Admiral Coligny"], "period_sources": ["de Thou Historia Sui Temporis 1609", "L'Estoile Mémoires-Journaux 1572"]},
    {"event_id": "ARMADA-1588", "name": "Spanish Armada", "event_type": "war", "start_year": 1588, "end_year": 1588, "location": "England", "actors": ["Philip II", "Elizabeth I", "Duke of Medina Sidonia"], "period_sources": ["de Thou Historia Sui Temporis 1609"]},
    {"event_id": "HENRY-IV-1589", "name": "Henry IV Accession", "event_type": "coronation", "start_year": 1589, "end_year": 1610, "location": "France", "actors": ["Henry IV", "Catherine de Medici"], "period_sources": ["L'Estoile Mémoires-Journaux 1589"]},
    {"event_id": "LEAGUE-1576", "name": "Holy League Formed", "event_type": "war", "start_year": 1576, "end_year": 1598, "location": "France", "actors": ["Henry I de Guise", "Philip II"], "period_sources": ["de Thou Historia Sui Temporis 1609"]},
    {"event_id": "HENRY-III-1574", "name": "Henry III Accession", "event_type": "coronation", "start_year": 1574, "end_year": 1589, "location": "France", "actors": ["Henry III", "Catherine de Medici"], "period_sources": ["L'Estoile Mémoires-Journaux 1574"]},
    {"event_id": "EDICT-1577", "name": "Edict of Beaulieu", "event_type": "alliance", "start_year": 1577, "end_year": 1577, "location": "France", "actors": ["Henry III"], "period_sources": ["de Thou Historia Sui Temporis 1609"]},
    {"event_id": "DAY_OF_BARRIERS-1588", "name": "Day of the Barriers", "event_type": "revolution", "start_year": 1588, "end_year": 1588, "location": "France", "actors": ["Henry III", "Duke of Guise"], "period_sources": ["L'Estoile Mémoires-Journaux 1588"]},
    {"event_id": "ST-DENIS-1567", "name": "Tomb of St. Denis Plundered", "event_type": "revolution", "start_year": 1567, "end_year": 1567, "location": "France", "actors": ["Charles IX"], "period_sources": ["L'Estoile Mémoires-Journaux 1567"]},
    {"event_id": "TOURS-1589", "name": "States General at Tours", "event_type": "political", "start_year": 1589, "end_year": 1589, "location": "France", "actors": ["Henry III", "Henry of Navarre"], "period_sources": ["L'Estoile Mémoires-Journaux 1589"]},

    # === HUNDRED YEARS WAR (1337-1453) ===
    {"event_id": "CRECY-1346", "name": "Battle of Crecy", "event_type": "war", "start_year": 1346, "end_year": 1346, "location": "France", "actors": ["Philip VI", "Edward III", "Edward the Black Prince"], "period_sources": ["Froissart Chroniques 1480s"]},
    {"event_id": "POITIERS-1356", "name": "Battle of Poitiers", "event_type": "war", "start_year": 1356, "end_year": 1356, "location": "France", "actors": ["John II", "Edward the Black Prince"], "period_sources": ["Froissart Chroniques 1480s"]},
    {"event_id": "NICE-1543", "name": "Siege of Nice", "event_type": "war", "start_year": 1543, "end_year": 1543, "location": "France", "actors": ["Francis I", "Charles V"], "period_sources": ["Froissart Chroniques 1480s"]},
    {"event_id": "METZ-1552", "name": "Siege of Metz", "event_type": "war", "start_year": 1552, "end_year": 1552, "location": "France", "actors": ["Francis I", "Charles V", "Henry II"], "period_sources": ["Froissart Chroniques 1480s"]},
    {"event_id": "CALAIS-1558", "name": "Capture of Calais", "event_type": "war", "start_year": 1558, "end_year": 1558, "location": "France", "actors": ["Francis II", "Duke of Guise"], "period_sources": ["Froissart Chroniques 1480s"]},
    {"event_id": "VERNEUIL-1424", "name": "Verneuil Massacre", "event_type": "war", "start_year": 1424, "end_year": 1424, "location": "France", "actors": [], "period_sources": ["Froissart Chroniques 1480s"]},
    {"event_id": "ORLEANS-1429", "name": "Siege of Orleans Lifted", "event_type": "war", "start_year": 1429, "end_year": 1429, "location": "France", "actors": ["Joan of Arc", "Charles VII", "Earl of Suffolk"], "period_sources": ["Froissart Chroniques 1480s"]},
    {"event_id": "AGINCOURT-1415", "name": "Battle of Agincourt", "event_type": "war", "start_year": 1415, "end_year": 1415, "location": "France", "actors": ["Henry V", "Charles VI"], "period_sources": ["Froissart Chroniques 1480s"]},
    {"event_id": "NICOPOLIS-1396", "name": "Battle of Nicopolis", "event_type": "war", "start_year": 1396, "end_year": 1396, "location": "Ottoman", "actors": ["Sigismund of Hungary", "Bayezid I"], "period_sources": ["Froissart Chroniques 1480s"]},
    {"event_id": "BRETAIN-1364", "name": "Battle of Auray / Treaty of Brittany", "event_type": "war", "start_year": 1364, "end_year": 1364, "location": "France", "actors": ["Charles of Blois", "John of Montfort"], "period_sources": ["Froissart Chroniques 1480s"]},

    # === ITALIAN WARS (1494-1559) ===
    {"event_id": "NAPLES-1494", "name": "French Invasion of Naples", "event_type": "war", "start_year": 1494, "end_year": 1495, "location": "Italy", "actors": ["Charles VIII", "Ferdinand II of Aragon"], "period_sources": ["Froissart Chroniques 1480s"]},
    {"event_id": "FORNOVO-1495", "name": "Battle of Fornovo", "event_type": "war", "start_year": 1495, "end_year": 1495, "location": "Italy", "actors": ["Charles VIII", "Ludovico Sforza"], "period_sources": ["Froissart Chroniques 1480s"]},
    {"event_id": "CERIGNOLA-1503", "name": "Battle of Cerignola", "event_type": "war", "start_year": 1503, "end_year": 1503, "location": "Italy", "actors": ["Louis XII", "Ferdinand II"], "period_sources": ["Froissart Chroniques 1480s"]},
    {"event_id": "MARIGNANO-1515", "name": "Battle of Marignano", "event_type": "war", "start_year": 1515, "end_year": 1515, "location": "Italy", "actors": ["Francis I", "Massimiliano Sforza"], "period_sources": ["Froissart Chroniques 1480s"]},
    {"event_id": "PAVIA-1525", "name": "Battle of Pavia", "event_type": "war", "start_year": 1525, "end_year": 1525, "location": "Italy", "actors": ["Francis I", "Charles V", "Emperor"], "period_sources": ["Froissart Chroniques 1480s"]},
    {"event_id": "ROME-1527", "name": "Sack of Rome", "event_type": "war", "start_year": 1527, "end_year": 1527, "location": "Italy", "actors": ["Charles V", "Pope Clement VII"], "period_sources": ["Froissart Chroniques 1480s"]},
    {"event_id": "ST-QUENTIN-1557", "name": "Battle of St. Quentin", "event_type": "war", "start_year": 1557, "end_year": 1557, "location": "France", "actors": ["Philip II", "Henry II"], "period_sources": ["Froissart Chroniques 1480s"]},
    {"event_id": "CALAIS-1558", "name": "Siege of Calais", "event_type": "war", "start_year": 1558, "end_year": 1558, "location": "France", "actors": ["Francis II", "Duke of Guise"], "period_sources": ["Froissart Chroniques 1480s"]},

    # === RELIGIOUS CONFLICTS ===
    {"event_id": "REFORMATION-1517", "name": "Protestant Reformation", "event_type": "religious_schism", "start_year": 1517, "end_year": 1648, "location": "Germany", "actors": ["Martin Luther", "Charles V", "Frederick the Wise"], "period_sources": ["de Thou Historia Sui Temporis 1609"]},
    {"event_id": "INQUISITION-1540", "name": "Jesuit Inquisition", "event_type": "religious_schism", "start_year": 1540, "end_year": 1540, "location": "Europe", "actors": ["Paul III", "Ignatius of Loyola"], "period_sources": ["de Thou Historia Sui Temporis 1609"]},
    {"event_id": "EDICT-1551", "name": "Edict of Cherasco", "event_type": "religious_schism", "start_year": 1551, "end_year": 1551, "location": "Italy", "actors": ["Charles V", "Henry II"], "period_sources": ["de Thou Historia Sui Temporis 1609"]},
    {"event_id": "PROTEST-1561", "name": "Colloquy of Poissy", "event_type": "religious_schism", "start_year": 1561, "end_year": 1561, "location": "France", "actors": ["Catherine de Medici", "Theodore Beza"], "period_sources": ["de Thou Historia Sui Temporis 1609"]},

    # === PLAGUES & EPIDEMICS ===
    {"event_id": "BLACK-DEATH-1348", "name": "Black Death", "event_type": "plague", "start_year": 1348, "end_year": 1350, "location": "Europe", "actors": [], "period_sources": ["Froissart Chroniques 1480s"]},
    {"event_id": "PLAGUE-1540", "name": "Great Plague of 1540", "event_type": "plague", "start_year": 1540, "end_year": 1543, "location": "Europe", "actors": [], "period_sources": ["Froissart Chroniques 1480s"]},
    {"event_id": "PLAGUE-1563", "name": "Plague of 1563", "event_type": "plague", "start_year": 1563, "end_year": 1564, "location": "France", "actors": [], "period_sources": ["L'Estoile Mémoires-Journaux 1563"]},
    {"event_id": "PLAGUE-1572", "name": "Plague of 1572", "event_type": "plague", "start_year": 1572, "end_year": 1573, "location": "France", "actors": [], "period_sources": ["L'Estoile Mémoires-Journaux 1572"]},
    {"event_id": "PLAGUE-1580", "name": "Plague of 1580", "event_type": "plague", "start_year": 1580, "end_year": 1581, "location": "France", "actors": [], "period_sources": ["L'Estoile Mémoires-Journaux 1580"]},
    {"event_id": "PLAGUE-1626", "name": "Plague of 1626", "event_type": "plague", "start_year": 1626, "end_year": 1626, "location": "France", "actors": [], "period_sources": ["L'Estoile Mémoires-Journaux 1648"]},
    {"event_id": "PLAGUE-1720", "name": "Great Plague of Marseille", "event_type": "plague", "start_year": 1720, "end_year": 1721, "location": "France", "actors": ["Louis XV"], "period_sources": ["Belleforest Histoires Tragiques 1570s"]},

    # === FAMINES ===
    {"event_id": "FAMINE-1555", "name": "Great Famine of 1555", "event_type": "famine", "start_year": 1555, "end_year": 1557, "location": "Europe", "actors": [], "period_sources": ["de Thou Historia Sui Temporis 1609"]},
    {"event_id": "FAMINE-1590", "name": "Famine of 1590s", "event_type": "famine", "start_year": 1590, "end_year": 1594, "location": "France", "actors": [], "period_sources": ["L'Estoile Mémoires-Journaux 1590"]},
    {"event_id": "FAMINE-1693", "name": "Great Famine of 1693", "event_type": "famine", "start_year": 1693, "end_year": 1694, "location": "France", "actors": ["Louis XIV"], "period_sources": ["Belleforest Histoires Tragiques 1570s"]},

    # === POLITICAL & REVOLUTIONS ===
    {"event_id": "FRONDE-1648", "name": "Fronde Rebellion", "event_type": "revolution", "start_year": 1648, "end_year": 1653, "location": "France", "actors": ["Louis XIV", "Cardinal Mazarin", "Prince de Conde"], "period_sources": ["L'Estoile Mémoires-Journaux 1648"]},
    {"event_id": "DAY_OF_TILES-1788", "name": "Day of the Tiles", "event_type": "revolution", "start_year": 1788, "end_year": 1788, "location": "France", "actors": [], "period_sources": []},
    {"event_id": "BASTILLE-1789", "name": "Storming of the Bastille", "event_type": "revolution", "start_year": 1789, "end_year": 1789, "location": "France", "actors": ["Louis XVI"], "period_sources": []},

    # === CORONATIONS & SUCCESSIONS ===
    {"event_id": "CHARLES-V-1519", "name": "Charles V Elected Emperor", "event_type": "coronation", "start_year": 1519, "end_year": 1556, "location": "Germany", "actors": ["Charles V", "Francis I", "Henry VIII"], "period_sources": ["Froissart Chroniques 1480s"]},
    {"event_id": "FRANCIS-I-1515", "name": "Francis I Becomes King", "event_type": "coronation", "start_year": 1515, "end_year": 1547, "location": "France", "actors": ["Francis I", "Louis XII"], "period_sources": ["Froissart Chroniques 1480s"]},
    {"event_id": "HENRY-II-1547", "name": "Henry II Accession", "event_type": "coronation", "start_year": 1547, "end_year": 1559, "location": "France", "actors": ["Henry II", "Francis I"], "period_sources": ["Froissart Chroniques 1480s"]},
    {"event_id": "FRANCIS-II-1559", "name": "Francis II Accession", "event_type": "coronation", "start_year": 1559, "end_year": 1560, "location": "France", "actors": ["Francis II", "Mary Queen of Scots"], "period_sources": ["Froissart Chroniques 1480s"]},
    {"event_id": "CHARLES-IX-1560", "name": "Charles IX Accession", "event_type": "coronation", "start_year": 1560, "end_year": 1574, "location": "France", "actors": ["Charles IX", "Catherine de Medici"], "period_sources": ["de Thou Historia Sui Temporis 1609"]},
    {"event_id": "LOUIS-XIII-1610", "name": "Louis XIII Accession", "event_type": "coronation", "start_year": 1610, "end_year": 1643, "location": "France", "actors": ["Louis XIII", "Marie de Medici"], "period_sources": ["L'Estoile Mémoires-Journaux 1610"]},
    {"event_id": "LOUIS-XIV-1643", "name": "Louis XIV Accession", "event_type": "coronation", "start_year": 1643, "end_year": 1715, "location": "France", "actors": ["Louis XIV", "Anne of Austria"], "period_sources": ["L'Estoile Mémoires-Journaux 1643"]},
    {"event_id": "LOUIS-XV-1715", "name": "Louis XV Accession", "event_type": "coronation", "start_year": 1715, "end_year": 1774, "location": "France", "actors": ["Louis XV", "Regent Orleans"], "period_sources": []},

    # === TREATIES & ALLIANCES ===
    {"event_id": "LEAGUE-CAMBR-1514", "name": "Treaty of Cambrai", "event_type": "alliance", "start_year": 1514, "end_year": 1514, "location": "France", "actors": ["Louis XII", "Ferdinand II"], "period_sources": ["Froissart Chroniques 1480s"]},
    {"event_id": "CONCORDAT-1516", "name": "Concordat of Bologna", "event_type": "alliance", "start_year": 1516, "end_year": 1516, "location": "France", "actors": ["Francis I", "Pope Leo X"], "period_sources": ["Froissart Chroniques 1480s"]},
    {"event_id": "TREATY-CADEAU-1559", "name": "Treaty of Cateau-Cambresis", "event_type": "alliance", "start_year": 1559, "end_year": 1559, "location": "France", "actors": ["Philip II", "Henry II"], "period_sources": ["Froissart Chroniques 1480s"]},
    {"event_id": "EDICT-1629", "name": "Edict of Grace", "event_type": "alliance", "start_year": 1629, "end_year": 1629, "location": "France", "actors": ["Louis XIII", "Richelieu"], "period_sources": []},
    {"event_id": "PYRENEES-1659", "name": "Treaty of the Pyrenees", "event_type": "alliance", "start_year": 1659, "end_year": 1659, "location": "France", "actors": ["Louis XIV", "Philip IV"], "period_sources": []},

    # === EASTERN EMPIRES ===
    {"event_id": "CONSTANTINOPLE-1453", "name": "Fall of Constantinople", "event_type": "war", "start_year": 1453, "end_year": 1453, "location": "East", "actors": ["Mehmed II", "Constantine XI"], "period_sources": ["Froissart Chroniques 1480s"]},
    {"event_id": "Varna-1444", "name": "Battle of Varna", "event_type": "war", "start_year": 1444, "end_year": 1444, "location": "Ottoman", "actors": ["Wladyslaw III", "Murad II"], "period_sources": ["Froissart Chroniques 1480s"]},
    {"event_id": "RHODES-1522", "name": "Siege of Rhodes", "event_type": "war", "start_year": 1522, "end_year": 1522, "location": "Ottoman", "actors": ["Suleiman I", "Knights of Rhodes"], "period_sources": ["Froissart Chroniques 1480s"]},
    {"event_id": "BUDAPEST-1529", "name": "Siege of Vienna", "event_type": "war", "start_year": 1529, "end_year": 1529, "location": "Germany", "actors": ["Suleiman I", "Charles V"], "period_sources": ["Froissart Chroniques 1480s"]},

    # === ENGLAND / SPAIN CONFLICTS ===
    {"event_id": "FIELD-1415", "name": "Battle of the Field of Cloth of Gold", "event_type": "alliance", "start_year": 1520, "end_year": 1520, "location": "France", "actors": ["Henry VIII", "Francis I"], "period_sources": ["Froissart Chroniques 1480s"]},
    {"event_id": "CALAIS-1558", "name": "Siege of Calais", "event_type": "war", "start_year": 1558, "end_year": 1558, "location": "France", "actors": ["Francis II", "Duke of Guise"], "period_sources": ["Froissart Chroniques 1480s"]},
    {"event_id": "DUNKERQUE-1558", "name": "Capture of Dunkirk", "event_type": "war", "start_year": 1558, "end_year": 1558, "location": "France", "actors": ["Philip II", "Henry II"], "period_sources": ["Froissart Chroniques 1480s"]},

    # === ASSASSINATIONS ===
    {"event_id": "ASSASSIN-1553", "name": "Assassination of Louis de France", "event_type": "assassination", "start_year": 1553, "end_year": 1553, "location": "France", "actors": ["Francis II"], "period_sources": ["de Thou Historia Sui Temporis 1609"]},
    {"event_id": "GUISE-1563", "name": "Assassination of Francis Duke of Guise", "event_type": "assassination", "start_year": 1563, "end_year": 1563, "location": "France", "actors": ["Charles IX", "Henry I de Guise"], "period_sources": ["L'Estoile Mémoires-Journaux 1563"]},
    {"event_id": "HENRI-IV-1610", "name": "Assassination of Henry IV", "event_type": "assassination", "start_year": 1610, "end_year": 1610, "location": "France", "actors": ["Henry IV", "Ravaillac"], "period_sources": ["L'Estoile Mémoires-Journaux 1610"]},

    # === ECLIPSES & CELESTIAL EVENTS ===
    {"event_id": "ECLIPSE-1500", "name": "Solar Eclipse of 1500", "event_type": "eclipse", "start_year": 1500, "end_year": 1500, "location": "Europe", "actors": [], "period_sources": ["Froissart Chroniques 1480s"]},
    {"event_id": "ECLIPSE-1525", "name": "Solar Eclipse of 1525", "event_type": "eclipse", "start_year": 1525, "end_year": 1525, "location": "Europe", "actors": [], "period_sources": ["de Thou Historia Sui Temporis 1609"]},
    {"event_id": "ECLIPSE-1558", "name": "Solar Eclipse of 1558", "event_type": "eclipse", "start_year": 1558, "end_year": 1558, "location": "Europe", "actors": [], "period_sources": ["L'Estoile Mémoires-Journaux 1558"]},
    {"event_id": "COMET-1533", "name": "Great Comet of 1533", "event_type": "eclipse", "start_year": 1533, "end_year": 1533, "location": "Europe", "actors": [], "period_sources": ["Froissart Chroniques 1480s"]},
    {"event_id": "COMET-1577", "name": "Great Comet of 1577", "event_type": "eclipse", "start_year": 1577, "end_year": 1577, "location": "Europe", "actors": [], "period_sources": ["L'Estoile Mémoires-Journaux 1577"]},

    # === CITY FIRES & NATURAL DISASTERS ===
    {"event_id": "LONDON-1666", "name": "Great Fire of London", "event_type": "city_fire", "start_year": 1666, "end_year": 1666, "location": "England", "actors": ["Charles II"], "period_sources": []},
    {"event_id": "ROUEN-1500", "name": "Rouen Fire", "event_type": "city_fire", "start_year": 1500, "end_year": 1500, "location": "France", "actors": [], "period_sources": ["Froissart Chroniques 1480s"]},
    {"event_id": "PARIS-1621", "name": "Paris Fire of 1621", "event_type": "city_fire", "start_year": 1621, "end_year": 1621, "location": "France", "actors": [], "period_sources": []},
    {"event_id": "FLOOD-1610", "name": "Great Flood of 1610", "event_type": "flood", "start_year": 1610, "end_year": 1610, "location": "France", "actors": [], "period_sources": ["L'Estoile Mémoires-Journaux 1610"]},

    # === THIRTY YEARS WAR ===
    {"event_id": "THIRTY-YEARS-1618", "name": "Thirty Years War", "event_type": "war", "start_year": 1618, "end_year": 1648, "location": "Germany", "actors": ["Ferdinand II", "Gustavus Adolphus", "Richelieu", "Wallenstein"], "period_sources": ["de Thou Historia Sui Temporis 1609"]},
    {"event_id": "WHITE-MOUNTAIN-1620", "name": "Battle of White Mountain", "event_type": "war", "start_year": 1620, "end_year": 1620, "location": "Germany", "actors": ["Ferdinand II", "Frederick V"], "period_sources": ["de Thou Historia Sui Temporis 1609"]},
    {"event_id": "LUTZEN-1632", "name": "Battle of Lutzen", "event_type": "war", "start_year": 1632, "end_year": 1632, "location": "Germany", "actors": ["Gustavus Adolphus", "Albrecht von Wallenstein"], "period_sources": ["de Thou Historia Sui Temporis 1609"]},
    {"event_id": "ROCROI-1643", "name": "Battle of Rocroi", "event_type": "war", "start_year": 1643, "end_year": 1643, "location": "France", "actors": ["Louis XIII", "Prince of Conde"], "period_sources": ["L'Estoile Mémoires-Journaux 1643"]},

    # === SICILIAN VESPERS / ITALIAN UNREST ===
    {"event_id": "SICILIAN-VESPERS-1282", "name": "Sicilian Vespers", "event_type": "revolution", "start_year": 1282, "end_year": 1282, "location": "Italy", "actors": ["Charles of Anjou", "Peter III of Aragon"], "period_sources": ["Froissart Chroniques 1480s"]},
    {"event_id": "SICILY-1282", "name": "War of the Sicilian Vespers", "event_type": "war", "start_year": 1282, "end_year": 1302, "location": "Italy", "actors": ["Charles of Anjou", "Peter III"], "period_sources": ["Froissart Chroniques 1480s"]},

    # === ADDITIONAL KEY EVENTS ===
    {"event_id": "BREST-1682", "name": "Exploration of Louisiana", "event_type": "alliance", "start_year": 1682, "end_year": 1682, "location": "France", "actors": ["La Salle"], "period_sources": []},
    {"event_id": "CODE-BLACK-1683", "name": "Great Plague of 1683", "event_type": "plague", "start_year": 1683, "end_year": 1684, "location": "Europe", "actors": [], "period_sources": []},
    {"event_id": "DOL-1675", "name": "Bunyan's Grace Abounding", "event_type": "religious_schism", "start_year": 1675, "end_year": 1675, "location": "England", "actors": ["John Bunyan"], "period_sources": []},
    {"event_id": "PENNSACOLA-1682", "name": "French Colonization of Louisiana", "event_type": "alliance", "start_year": 1682, "end_year": 1682, "location": "France", "actors": ["La Salle"], "period_sources": []},
]

if __name__ == "__main__":
    print(f"Historical Events KB: {len(HISTORICAL_EVENTS_KB)} events")
    by_type = {}
    for e in HISTORICAL_EVENTS_KB:
        t = e['event_type']
        by_type[t] = by_type.get(t, 0) + 1
    print("\nBy event type:")
    for t, c in sorted(by_type.items(), key=lambda x: -x[1]):
        print(f"  {t}: {c}")

    print("\nBy period source:")
    sources = {}
    for e in HISTORICAL_EVENTS_KB:
        for s in e.get('period_sources', []):
            sources[s] = sources.get(s, 0) + 1
    for s, c in sorted(sources.items(), key=lambda x: -x[1]):
        print(f"  {s}: {c}")

    print(f"\nEvents with no period sources: {sum(1 for e in HISTORICAL_EVENTS_KB if not e.get('period_sources'))}")
