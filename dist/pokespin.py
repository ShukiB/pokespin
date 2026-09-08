#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pokespin - replace Claude Code's thinking-spinner verbs with Pokemon.

Claude Code (>= 2.1.x) supports a `spinnerVerbs` setting:

    "spinnerVerbs": { "mode": "replace" | "append", "verbs": [...] }

It samples one verb uniformly at random each turn, so this tool just installs
the list. Standard library only; no dependencies.

    python pokespin.py install               # gen 1 (Kanto, 151) -- the default
    python pokespin.py install --gen all     # all 9 gens, 1025 verbs
    python pokespin.py install --gen 1-3     # ranges and lists: 1-3, or 2,5,9
    python pokespin.py install --mode append
    python pokespin.py gens                  # list the generations
    python pokespin.py status
    python pokespin.py preview -n 15 --gen 2
    python pokespin.py uninstall
    python pokespin.py install --refresh     # re-pull live from PokeAPI

Restart Claude Code after installing; settings are read at startup.

`autoinstall` is the guarded variant the plugin's SessionStart hook calls: it
installs generation 1 only, runs at most once per machine, never overwrites an
existing spinnerVerbs, and swallows every error so it cannot break a session.
"""
import argparse, io, json, os, random, shutil, sys, time

__version__ = "1.2.0"

# Generation -> verbs. Keys are strings so the embedded JSON round-trips.
GEN_VERBS = json.loads(r'''{"1": ["Bulbasauring", "Ivysauring", "Venusauring", "Charmandering", "Charmeleoning", "Charizarding", "Squirtling", "Wartortling", "Blastoising", "Caterpying", "Metapoding", "Butterfreeing", "Weedling", "Kakunaing", "Beedrilling", "Pidgeying", "Pidgeottoing", "Pidgeoting", "Rattataing", "Raticating", "Spearowing", "Fearowing", "Ekansing", "Arboking", "Pikachuing", "Raichuing", "Sandshrewing", "Sandslashing", "Nidoran-Fing", "Nidorinaing", "Nidoqueening", "Nidoran-Ming", "Nidorinoing", "Nidokinging", "Clefairying", "Clefabling", "Vulpixing", "Ninetalesing", "Jigglypuffing", "Wigglytuffing", "Zubatting", "Golbatting", "Oddishing", "Glooming", "Vilepluming", "Parasing", "Parasecting", "Venonating", "Venomothing", "Digletting", "Dugtrioing", "Meowthing", "Persianing", "Psyducking", "Golducking", "Mankeying", "Primeaping", "Growlithing", "Arcanining", "Poliwaging", "Poliwhirling", "Poliwrathing", "Abraing", "Kadabraing", "Alakazaming", "Machopping", "Machoking", "Machamping", "Bellsprouting", "Weepinbelling", "Victreebeling", "Tentacooling", "Tentacrueling", "Geoduding", "Gravelering", "Goleming", "Ponytaing", "Rapidashing", "Slowpoking", "Slowbroing", "Magnemiting", "Magnetoning", "Farfetch'ding", "Doduoing", "Dodrioing", "Seeling", "Dewgonging", "Grimering", "Muking", "Shelldering", "Cloystering", "Gastlying", "Hauntering", "Gengaring", "Onixing", "Drowzeeing", "Hypnoing", "Krabbying", "Kinglering", "Voltorbing", "Electroding", "Exeggcuting", "Exeggutoring", "Cuboning", "Marowaking", "Hitmonleeing", "Hitmonchaning", "Lickitunging", "Koffinging", "Weezinging", "Rhyhorning", "Rhydoning", "Chanseying", "Tangelaing", "Kangaskhaning", "Horseaing", "Seadraing", "Goldeening", "Seakinging", "Staryuing", "Starmying", "Mr. Miming", "Scythering", "Jynxing", "Electabuzzing", "Magmaring", "Pinsiring", "Taurosing", "Magikarping", "Gyaradosing", "Laprasing", "Dittoing", "Eeveeing", "Vaporeoning", "Jolteoning", "Flareoning", "Porygoning", "Omanyting", "Omastaring", "Kabutoing", "Kabutopsing", "Aerodactyling", "Snorlaxing", "Articunoing", "Zapdosing", "Moltresing", "Dratiniing", "Dragonairing", "Dragoniting", "Mewtwoing", "Mewing"], "2": ["Chikoritaing", "Bayleefing", "Meganiuming", "Cyndaquiling", "Quilavaing", "Typhlosioning", "Totodiling", "Croconawing", "Feraligatring", "Sentretting", "Furretting", "Hoothooting", "Noctowling", "Ledybaing", "Ledianing", "Spinaraking", "Ariadosing", "Crobatting", "Chinchouing", "Lanturning", "Pichuing", "Cleffaing", "Igglybuffing", "Togepiing", "Togeticking", "Natuing", "Xatuing", "Mareeping", "Flaaffying", "Ampharosing", "Bellossoming", "Marilling", "Azumarilling", "Sudowoodoing", "Politoeding", "Hoppipping", "Skiplooming", "Jumpluffing", "Aipoming", "Sunkerning", "Sunfloraing", "Yanmaing", "Woopering", "Quagsiring", "Espeoning", "Umbreoning", "Murkrowing", "Slowkinging", "Misdreavusing", "Unowning", "Wobbuffeting", "Girafariging", "Pinecoing", "Forretressing", "Dunsparcing", "Gligaring", "Steelixing", "Snubbulling", "Granbulling", "Qwilfishing", "Scizoring", "Shuckling", "Heracrossing", "Sneaseling", "Teddiursaing", "Ursaringing", "Slugmaing", "Magcargoing", "Swinubbing", "Piloswining", "Corsolaing", "Remoraiding", "Octillerying", "Delibirding", "Mantining", "Skarmorying", "Houndouring", "Houndooming", "Kingdraing", "Phanpying", "Donphaning", "Porygon2ing", "Stantlering", "Smeargling", "Tyrogueing", "Hitmontoping", "Smoochuming", "Elekiding", "Magbying", "Miltanking", "Blisseying", "Raikouing", "Enteiing", "Suicuning", "Larvitaring", "Pupitaring", "Tyranitaring", "Lugiaing", "Ho-Ohing", "Celebiing"], "3": ["Treeckoing", "Grovyling", "Sceptiling", "Torchicking", "Combuskening", "Blazikening", "Mudkipping", "Marshtomping", "Swamperting", "Poochyenaing", "Mightyenaing", "Zigzagooning", "Linooning", "Wurmpling", "Silcooning", "Beautiflying", "Cascooning", "Dustoxing", "Lotadding", "Lombring", "Ludicoloing", "Seedotting", "Nuzleafing", "Shiftrying", "Taillowing", "Swellowing", "Wingulling", "Pelippering", "Raltsing", "Kirliaing", "Gardevoiring", "Surskitting", "Masqueraining", "Shroomishing", "Brelooming", "Slakothing", "Vigorothing", "Slakinging", "Nincadaing", "Ninjasking", "Shedinjaing", "Whismuring", "Loudredding", "Explouding", "Makuhitaing", "Hariyamaing", "Azurilling", "Nosepassing", "Skittying", "Delcattying", "Sableyeing", "Mawiling", "Aroning", "Laironing", "Aggroning", "Medititing", "Medichaming", "Electriking", "Manectricking", "Plusling", "Minunning", "Volbeating", "Illumising", "Roseliaing", "Gulpining", "Swalotting", "Carvanhaing", "Sharpedoing", "Wailmering", "Wailording", "Numeling", "Camerupting", "Torkoaling", "Spoinking", "Grumpigging", "Spindaing", "Trapinching", "Vibravaing", "Flygoning", "Cacneaing", "Cacturning", "Swabluing", "Altariaing", "Zangoosing", "Sevipering", "Lunatoning", "Solrocking", "Barboaching", "Whiscashing", "Corphishing", "Crawdaunting", "Baltoying", "Claydoling", "Lileeping", "Cradilying", "Anorithing", "Armaldoing", "Feebasing", "Miloticking", "Castforming", "Kecleoning", "Shuppetting", "Banetting", "Duskulling", "Dusclopsing", "Tropiusing", "Chimechoing", "Absoling", "Wynauting", "Snorunting", "Glalying", "Sphealing", "Sealeoing", "Walreining", "Clamperling", "Huntailing", "Gorebyssing", "Relicanthing", "Luvdiscing", "Bagoning", "Shelgoning", "Salamencing", "Belduming", "Metanging", "Metagrossing", "Regirocking", "Regicing", "Registeeling", "Latiasing", "Latiosing", "Kyogring", "Groudoning", "Rayquazaing", "Jirachiing", "Deoxysing"], "4": ["Turtwigging", "Grotling", "Torterraing", "Chimcharing", "Monfernoing", "Infernaping", "Piplupping", "Prinplupping", "Empoleoning", "Starlying", "Staraviaing", "Staraptoring", "Bidoofing", "Bibareling", "Kricketoting", "Kricketuning", "Shinxing", "Luxioing", "Luxraying", "Budewing", "Roserading", "Cranidosing", "Rampardosing", "Shieldoning", "Bastiodoning", "Burmying", "Wormadaming", "Mothiming", "Combeeing", "Vespiquening", "Pachirisuing", "Buizeling", "Floatzeling", "Cherubiing", "Cherriming", "Shellosing", "Gastrodoning", "Ambipoming", "Driflooning", "Drifbliming", "Bunearying", "Lopunnying", "Mismagiusing", "Honchkrowing", "Glameowing", "Puruglying", "Chinglinging", "Stunkying", "Skuntanking", "Bronzoring", "Bronzonging", "Bonslying", "Miming Jr.", "Happinying", "Chatotting", "Spiritombing", "Gibling", "Gabiting", "Garchomping", "Munchlaxing", "Rioluing", "Lucarioing", "Hippopotasing", "Hippowdoning", "Skorupiing", "Drapioning", "Croagunking", "Toxicroaking", "Carnivining", "Finneoning", "Lumineoning", "Mantyking", "Snovering", "Abomasnowing", "Weaviling", "Magnezoning", "Lickilickying", "Rhyperioring", "Tangrowthing", "Electiviring", "Magmortaring", "Togekissing", "Yanmegaing", "Leafeoning", "Glaceoning", "Gliscoring", "Mamoswining", "Porygon-Zing", "Gallading", "Probopassing", "Dusknoiring", "Froslassing", "Rotoming", "Uxying", "Mespritting", "Azelfing", "Dialgaing", "Palkiaing", "Heatraning", "Regigigasing", "Giratinaing", "Cresseliaing", "Phioning", "Manaphying", "Darkraiing", "Shaymining", "Arceusing"], "5": ["Victiniing", "Snivying", "Servining", "Serperioring", "Tepigging", "Pigniting", "Emboaring", "Oshawotting", "Dewotting", "Samurotting", "Patratting", "Watchogging", "Lillipuping", "Herdiering", "Stoutlanding", "Purrloining", "Lieparding", "Pansaging", "Simisaging", "Pansearing", "Simisearing", "Panpouring", "Simipouring", "Munnaing", "Musharnaing", "Pidoving", "Tranquilling", "Unfezanting", "Blitzling", "Zebstrikaing", "Roggenrolaing", "Boldoring", "Gigalithing", "Woobatting", "Swoobatting", "Drilburing", "Excadrilling", "Audinoing", "Timburring", "Gurdurring", "Conkeldurring", "Tympoling", "Palpitoading", "Seismitoading", "Throhing", "Sawking", "Sewaddling", "Swadlooning", "Leavannying", "Venipeding", "Whirlipeding", "Scolipeding", "Cottoneeing", "Whimsicotting", "Petililing", "Lilliganting", "Basculining", "Sandiling", "Krokoroking", "Krookodiling", "Darumakaing", "Darmanitaning", "Maractusing", "Dwebbling", "Crustling", "Scraggying", "Scraftying", "Sigilyphing", "Yamasking", "Cofagrigusing", "Tirtougaing", "Carracostaing", "Archening", "Archeopsing", "Trubbishing", "Garbodoring", "Zoruaing", "Zoroarking", "Minccinoing", "Cinccinoing", "Gothitaing", "Gothoritaing", "Gothitelling", "Solosising", "Duosioning", "Reuniclusing", "Duckletting", "Swannaing", "Vanilliting", "Vanillishing", "Vanilluxing", "Deerlinging", "Sawsbucking", "Emolgaing", "Karrablasting", "Escavaliering", "Foongusing", "Amoongussing", "Frillishing", "Jellicenting", "Alomomolaing", "Joltiking", "Galvantulaing", "Ferroseeding", "Ferrothorning", "Klinking", "Klanging", "Klinklanging", "Tynamoing", "Eelektriking", "Eelektrossing", "Elgyeming", "Beheeyeming", "Litwicking", "Lampenting", "Chandeluring", "Axewing", "Fraxuring", "Haxorusing", "Cubchooing", "Bearticking", "Cryogonaling", "Shelmetting", "Accelgoring", "Stunfisking", "Mienfooing", "Mienshaoing", "Druddigoning", "Goletting", "Golurking", "Pawniarding", "Bisharping", "Bouffalanting", "Ruffletting", "Braviarying", "Vullabying", "Mandibuzzing", "Heatmoring", "Duranting", "Deinoing", "Zweilousing", "Hydreigoning", "Larvestaing", "Volcaronaing", "Cobalioning", "Terrakioning", "Virizioning", "Tornadusing", "Thundurusing", "Reshiraming", "Zekroming", "Landorusing", "Kyureming", "Keldeoing", "Meloettaing", "Genesecting"], "6": ["Chespining", "Quilladining", "Chesnaughting", "Fennekining", "Braixening", "Delphoxing", "Froakying", "Frogadiering", "Greninjaing", "Bunnelbying", "Diggersbying", "Fletchlinging", "Fletchindering", "Talonflaming", "Scatterbuging", "Spewpaing", "Vivilloning", "Litleoing", "Pyroaring", "Flab\u00e9b\u00e9ing", "Floetting", "Florgesing", "Skiddoing", "Gogoating", "Panchamming", "Pangoroing", "Furfrouing", "Espurring", "Meowsticking", "Honedging", "Doublading", "Aegislashing", "Spritzeeing", "Aromatissing", "Swirlixing", "Slurpuffing", "Inkaying", "Malamaring", "Binacling", "Barbaracling", "Skrelping", "Dragalging", "Claunchering", "Clawitzering", "Helioptiling", "Heliolisking", "Tyrunting", "Tyrantruming", "Amauraing", "Aurorusing", "Sylveoning", "Hawluchaing", "Dedenning", "Carbinking", "Goomying", "Sliggooing", "Goodraing", "Klefkiing", "Phantumping", "Trevenanting", "Pumpkabooing", "Gourgeisting", "Bergmiting", "Avalugging", "Noibatting", "Noiverning", "Xerneasing", "Yveltaling", "Zygarding", "Diancying", "Hoopaing", "Volcanioning"], "7": ["Rowletting", "Dartrixing", "Decidueyeing", "Littening", "Torracating", "Incineroaring", "Popplioing", "Brionning", "Primarinaing", "Pikipeking", "Trumbeaking", "Toucannoning", "Yungoosing", "Gumshoosing", "Grubbining", "Charjabuging", "Vikavolting", "Crabrawlering", "Crabominabling", "Oricorioing", "Cutieflying", "Ribombeeing", "Rockruffing", "Lycanrocking", "Wishiwashiing", "Mareanying", "Toxapexing", "Mudbraying", "Mudsdaling", "Dewpidering", "Araquaniding", "Fomantising", "Lurantising", "Morelulling", "Shiinoticking", "Salanditing", "Salazzling", "Stuffuling", "Bewearing", "Bounsweeting", "Steeneeing", "Tsareenaing", "Comfeying", "Oranguruing", "Passimianing", "Wimpodding", "Golisopoding", "Sandygasting", "Palossanding", "Pyukumukuing", "Type-Nulling", "Silvallying", "Minioring", "Komalaing", "Turtonatoring", "Togedemaruing", "Mimikyuing", "Bruxishing", "Drampaing", "Dhelmising", "Jangmo-oing", "Hakamo-oing", "Kommo-oing", "Tapu Kokoing", "Tapu Leling", "Tapu Buluing", "Tapu Finiing", "Cosmogging", "Cosmoeming", "Solgaleoing", "Lunalaing", "Nihilegoing", "Buzzwoling", "Pheromosaing", "Xurkitreeing", "Celesteelaing", "Kartanaing", "Guzzlording", "Necrozmaing", "Magearnaing", "Marshadowing", "Poipoling", "Naganadeling", "Stakatakaing", "Blacephaloning", "Zeraoraing", "Meltaning", "Melmetaling"], "8": ["Grookeying", "Thwackeying", "Rillabooming", "Scorbunnying", "Rabooting", "Cinderacing", "Sobbling", "Drizziling", "Inteleoning", "Skwovetting", "Greedenting", "Rookideeing", "Corvisquiring", "Corviknighting", "Blipbugging", "Dottlering", "Orbeetling", "Nickitting", "Thievuling", "Gossifleuring", "Eldegossing", "Woolooing", "Dubwooling", "Chewtling", "Drednawing", "Yampering", "Boltunding", "Rolycolying", "Carkoling", "Coalossaling", "Applining", "Flappling", "Appletuning", "Silicobraing", "Sandacondaing", "Cramoranting", "Arrokudaing", "Barraskewdaing", "Toxeling", "Toxtricitying", "Sizzlipeding", "Centiskorching", "Clobbopusing", "Grapplocting", "Sinisteaing", "Polteageisting", "Hatennaing", "Hattreming", "Hatterening", "Impidimping", "Morgreming", "Grimmsnarling", "Obstagooning", "Perrserkering", "Cursolaing", "Sirfetch'ding", "Mr. Riming", "Runerigusing", "Milcerying", "Alcremying", "Falinksing", "Pincurchining", "Snoming", "Frosmothing", "Stonjournering", "Eiscueing", "Indeedeeing", "Morpekoing", "Cufanting", "Copperajahing", "Dracozolting", "Arctozolting", "Dracovishing", "Arctovishing", "Duraludoning", "Dreepying", "Drakloaking", "Dragapulting", "Zacianing", "Zamazentaing", "Eternatusing", "Kubfuing", "Urshifuing", "Zaruding", "Regielekiing", "Regidragoing", "Glastriering", "Spectriering", "Calyrexing", "Wyrdeering", "Kleavoring", "Ursalunaing", "Basculegioning", "Sneaslering", "Overqwiling", "Enamorusing"], "9": ["Sprigatitoing", "Floragatoing", "Meowscaradaing", "Fuecocoing", "Crocaloring", "Skeledirging", "Quaxlying", "Quaxwelling", "Quaquavaling", "Lechonking", "Oinkologning", "Tarountulaing", "Spidopsing", "Nymbling", "Lokixing", "Pawmiing", "Pawmoing", "Pawmotting", "Tandemausing", "Mausholding", "Fidoughing", "Dachsbunning", "Smoliving", "Dolliving", "Arbolivaing", "Squawkabillying", "Nacliing", "Naclstacking", "Garganacling", "Charcadeting", "Armarouging", "Ceruledging", "Tadbulbing", "Bellibolting", "Wattreling", "Kilowattreling", "Maschiffing", "Mabosstiffing", "Shroodling", "Grafaiaiing", "Bramblining", "Brambleghasting", "Toedscooling", "Toedscrueling", "Klawfing", "Capsakiding", "Scovillaining", "Relloring", "Rabscaing", "Flittling", "Espathraing", "Tinkatinking", "Tinkatuffing", "Tinkatoning", "Wigletting", "Wugtrioing", "Bombirdiering", "Finizening", "Palafining", "Varooming", "Revavrooming", "Cyclizaring", "Orthworming", "Glimmetting", "Glimmoraing", "Greavarding", "Houndstoning", "Flamigoing", "Cetoddling", "Cetitaning", "Veluzaing", "Dondozoing", "Tatsugiriing", "Annihilaping", "Clodsiring", "Farigirafing", "Dudunsparcing", "Kingambiting", "Great Tusking", "Scream Tailing", "Brute Bonnetting", "Flutter Maning", "Slither Winging", "Sandy Shocksing", "Iron Treadsing", "Iron Bundling", "Iron Handsing", "Iron Jugulising", "Iron Mothing", "Iron Thornsing", "Frigibaxing", "Arctibaxing", "Baxcaliburing", "Gimmighouling", "Gholdengoing", "Wo-Chiening", "Chien-Paoing", "Ting-Luing", "Chi-Yuing", "Roaring Mooning", "Iron Valianting", "Koraidoning", "Miraidoning", "Walking Waking", "Iron Leavesing", "Dipplining", "Poltchageisting", "Sinistchaing", "Okidogiing", "Munkidoriing", "Fezandipitiing", "Ogerponing", "Archaludoning", "Hydrappling", "Gouging Firing", "Raging Bolting", "Iron Bouldering", "Iron Crowning", "Terapagosing", "Pecharunting"]}''')

GEN_NAMES = {1: "Kanto", 2: "Johto", 3: "Hoenn", 4: "Sinnoh", 5: "Unova",
             6: "Kalos", 7: "Alola", 8: "Galar", 9: "Paldea"}

ALL_GENS = sorted(int(g) for g in GEN_VERBS)
DEFAULT_GENS = [1]                      # Kanto only, unless asked otherwise
VERBS = [v for g in ALL_GENS for v in GEN_VERBS[str(g)]]


# ---------------------------------------------------------------- generations

def parse_gens(spec):
    """Turn a --gen spec into a sorted list of ints.

    Accepts: 1 | 1,3 | 1-3 | 2,5-7 | all
    """
    if spec is None:
        return list(DEFAULT_GENS)
    spec = str(spec).strip().lower()
    if spec in ("all", "*"):
        return list(ALL_GENS)
    out = set()
    for part in spec.replace(" ", "").split(","):
        if not part:
            continue
        try:
            if "-" in part:
                lo, hi = part.split("-", 1)
                lo, hi = int(lo), int(hi)
                if lo > hi:
                    lo, hi = hi, lo
                out.update(range(lo, hi + 1))
            else:
                out.add(int(part))
        except ValueError:
            sys.exit("error: could not read --gen %r. Use 1, 1-3, 2,5,9, or all."
                     % spec)
    bad = sorted(g for g in out if g not in ALL_GENS)
    if bad:
        sys.exit("error: no such generation: %s (valid: 1-%d, or 'all')."
                 % (", ".join(str(b) for b in bad), max(ALL_GENS)))
    if not out:
        sys.exit("error: --gen selected nothing.")
    return sorted(out)


def verbs_for(gens):
    return [v for g in gens for v in GEN_VERBS[str(g)]]


def describe_gens(gens):
    if gens == list(ALL_GENS):
        return "all %d generations" % len(ALL_GENS)
    return ", ".join("gen %d (%s)" % (g, GEN_NAMES.get(g, "?")) for g in gens)


# ---------------------------------------------------------------- settings io

def settings_path(scope):
    if scope == "project":
        return os.path.join(os.getcwd(), ".claude", "settings.json")
    return os.path.join(os.path.expanduser("~"), ".claude", "settings.json")


def load_settings(path):
    if not os.path.exists(path):
        return {}
    with io.open(path, encoding="utf-8") as f:
        text = f.read().strip()
    if not text:
        return {}
    try:
        data = json.loads(text)
    except ValueError as e:
        sys.exit("error: %s is not valid JSON (%s).\nFix or move it, then retry."
                 % (path, e))
    if not isinstance(data, dict):
        sys.exit("error: %s must contain a JSON object." % path)
    return data


def save_settings(path, data):
    """Write atomically so a crash can never leave settings.json truncated."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".pokespin.tmp"
    # ensure_ascii keeps accented names (Flabebe) safe on any console codepage.
    with io.open(tmp, "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(data, ensure_ascii=True, indent=2) + "\n")
    os.replace(tmp, path)


def backup(path):
    if not os.path.exists(path):
        return None
    dest = "%s.bak-%s" % (path, time.strftime("%Y%m%d-%H%M%S"))
    shutil.copy2(path, dest)
    return dest


# ---------------------------------------------------------------- verb source

def fetch_live(gens):
    """Re-derive the list from PokeAPI, so new generations can be picked up."""
    import urllib.request
    from concurrent.futures import ThreadPoolExecutor
    try:
        from gerund import gerund
    except ImportError:
        sys.exit("error: --refresh needs gerund.py (the rule engine) beside this file.")

    roman = {"i": 1, "ii": 2, "iii": 3, "iv": 4, "v": 5,
             "vi": 6, "vii": 7, "viii": 8, "ix": 9}
    ua = {"User-Agent": "pokespin/%s" % __version__}

    def get(url, tries=4):
        for a in range(tries):
            try:
                req = urllib.request.Request(url, headers=ua)
                with urllib.request.urlopen(req, timeout=30) as r:
                    return json.load(r)
            except Exception:
                if a == tries - 1:
                    raise
                time.sleep(1.5 * (a + 1))

    index = get("https://pokeapi.co/api/v2/pokemon-species?limit=20000")
    rows = index["results"]
    print("PokeAPI reports %d species; fetching names..." % index["count"])

    def one(row):
        d = get(row["url"])
        en = [n["name"] for n in d["names"] if n["language"]["name"] == "en"]
        gen = roman.get(d["generation"]["name"].split("-")[-1], 0)
        return d["id"], gen, (en[0] if en else d["name"].title())

    with ThreadPoolExecutor(max_workers=12) as ex:
        rec = sorted(ex.map(one, rows))
    want = set(gens)
    return [gerund(name) for _, gen, name in rec if gen in want]


def get_verbs(a):
    gens = parse_gens(getattr(a, "gen", None))
    verbs = fetch_live(gens) if getattr(a, "refresh", False) else verbs_for(gens)
    if not verbs:
        sys.exit("error: empty verb list.")
    return gens, verbs


# ---------------------------------------------------------------- commands

def cmd_install(a):
    gens, verbs = get_verbs(a)
    path = settings_path(a.scope)
    data = load_settings(path)
    prev = data.get("spinnerVerbs")
    data["spinnerVerbs"] = {"mode": a.mode, "verbs": verbs}

    if a.dry_run:
        print("[dry-run] would write %s" % path)
        print("[dry-run] mode=%s gens=%s verbs=%d"
              % (a.mode, ",".join(str(g) for g in gens), len(verbs)))
        return
    b = backup(path)
    save_settings(path, data)
    print("Installed %d Pokemon verbs from %s (mode=%s)"
          % (len(verbs), describe_gens(gens), a.mode))
    print("  settings: %s" % path)
    if b:
        print("  backup:   %s" % b)
    if prev:
        print("  note: replaced an existing spinnerVerbs setting.")
    print("  sample:   %s" % ", ".join(random.sample(verbs, min(6, len(verbs)))))
    print("\nRestart Claude Code to see it.")


def cmd_uninstall(a):
    path = settings_path(a.scope)
    data = load_settings(path)
    if "spinnerVerbs" not in data:
        print("Nothing to remove; spinnerVerbs is not set in %s" % path)
        return
    if a.dry_run:
        print("[dry-run] would remove spinnerVerbs from %s" % path)
        return
    b = backup(path)
    del data["spinnerVerbs"]
    save_settings(path, data)
    print("Removed spinnerVerbs from %s" % path)
    if b:
        print("  backup: %s" % b)
    print("Restart Claude Code to restore the default verbs.")


MARKER = os.path.join(os.path.expanduser("~"), ".claude", ".pokespin-autoinstall")


def cmd_autoinstall(a):
    """One-shot install used by the SessionStart hook.

    Installs DEFAULT_GENS (generation 1). Deliberately conservative: runs at
    most once per machine, never overwrites a spinnerVerbs you already set, and
    can never break a session -- any failure exits 0 silently.
    """
    try:
        if os.path.exists(MARKER):
            return                      # already ran once; an uninstall stays uninstalled
        path = settings_path("user")
        data = load_settings(path)
        if "spinnerVerbs" not in data:  # never clobber the user's own choice
            data["spinnerVerbs"] = {"mode": "replace",
                                    "verbs": verbs_for(DEFAULT_GENS)}
            backup(path)
            save_settings(path, data)
        os.makedirs(os.path.dirname(MARKER), exist_ok=True)
        with io.open(MARKER, "w", encoding="utf-8") as f:
            stamp = time.strftime("%Y-%m-%d %H:%M:%S")
            f.write("pokespin " + __version__ + " installed at " + stamp)
    except (Exception, SystemExit):
        pass       # SystemExit too: load_settings() exits on a corrupt file, and
                   # a cosmetic plugin must never break session startup


def cmd_status(a):
    path = settings_path(a.scope)
    print("settings: %s%s" % (path, "" if os.path.exists(path) else "  (missing)"))
    cfg = load_settings(path).get("spinnerVerbs")
    if not cfg:
        print("status:   not installed (Claude Code is using its default verbs)")
        return
    verbs = cfg.get("verbs", [])
    have = set(verbs)
    print("status:   installed")
    print("mode:     %s" % cfg.get("mode"))
    mine = sum(1 for v in verbs if v in set(VERBS))
    print("verbs:    %d  (%d from this pokedex of %d)" % (len(verbs), mine, len(VERBS)))

    present = []
    for g in ALL_GENS:
        pool = GEN_VERBS[str(g)]
        n = sum(1 for v in pool if v in have)
        if n:
            present.append("%d/%d gen %d (%s)" % (n, len(pool), g, GEN_NAMES[g]))
    print("gens:     %s" % ("; ".join(present) if present else "none recognised"))
    if verbs:
        print("sample:   %s" % ", ".join(random.sample(verbs, min(6, len(verbs)))))


def cmd_preview(a):
    _, verbs = get_verbs(a)
    for v in random.sample(verbs, min(a.number, len(verbs))):
        print(v)


def cmd_gens(a):
    print("gen  region    count  example")
    for g in ALL_GENS:
        pool = GEN_VERBS[str(g)]
        mark = " *" if g in DEFAULT_GENS else "  "
        print("%2d%s %-9s %5d  %s"
              % (g, mark, GEN_NAMES.get(g, "?"), len(pool), pool[0]))
    print("")
    print("%d total. '*' is the default." % len(VERBS))
    print("Select with --gen 1 / --gen 1-3 / --gen 2,5,9 / --gen all")


def main(argv=None):
    p = argparse.ArgumentParser(
        prog="pokespin",
        description="Replace Claude Code's spinner verbs with Pokemon "
                    "(generation 1 by default).")
    p.add_argument("--version", action="version", version="pokespin " + __version__)
    sub = p.add_subparsers(dest="cmd")

    def common(sp, scope=True, gen=True):
        if scope:
            sp.add_argument("--scope", choices=["user", "project"], default="user",
                            help="user = ~/.claude/settings.json (default); "
                                 "project = ./.claude/settings.json")
        if gen:
            sp.add_argument("--gen", "-g", default=None, metavar="SPEC",
                            help="which generations: 1 (default), 1-3, 2,5,9, or all")
        sp.add_argument("--refresh", action="store_true",
                        help="re-pull species live from PokeAPI instead of the "
                             "embedded list")
        sp.add_argument("--dry-run", action="store_true",
                        help="show what would change, write nothing")

    sp = sub.add_parser("install", help="write the verbs into settings.json")
    sp.add_argument("--mode", choices=["replace", "append"], default="replace",
                    help="replace the built-in verbs (default) or add to them")
    common(sp)
    sp.set_defaults(func=cmd_install)

    sp = sub.add_parser("uninstall", help="remove the setting again")
    common(sp, gen=False)
    sp.set_defaults(func=cmd_uninstall)

    sp = sub.add_parser("autoinstall",
                        help="internal: one-shot install used by the SessionStart hook")
    sp.set_defaults(func=cmd_autoinstall, refresh=False, dry_run=False, scope="user")

    sp = sub.add_parser("status", help="show what is currently installed")
    common(sp, gen=False)
    sp.set_defaults(func=cmd_status)

    sp = sub.add_parser("preview", help="print a random sample of verbs")
    sp.add_argument("-n", "--number", type=int, default=10)
    common(sp, scope=False)
    sp.set_defaults(func=cmd_preview)

    sp = sub.add_parser("gens", help="list the generations and their sizes")
    sp.set_defaults(func=cmd_gens)

    a = p.parse_args(argv)
    if not getattr(a, "func", None):
        p.print_help()
        return 0
    a.func(a)
    return 0


if __name__ == "__main__":
    sys.exit(main())
