ADVENTURE_NODES = {
    "1_start": {
        "type": "narrative",
        "scene": "dorf",
        "narrative": "Willkommen in Dämmerbruch! Der Händler Finnian tritt auf euch zu.\n\n'Ihr seht aus wie Abenteurer! Seit Wochen verschwinden Vorräte aus dem Dorf. Die Schattenwichte der vergessenen Zitadelle sind schuld, da bin ich sicher. Ich biete eine ordentliche Belohnung, wenn ihr das Problem löst!'",
        "audio_text": "Willkommen in Dämmerbruch! Der Händler Finnian bittet um Hilfe.",
        "options": ["Nach den Schattenwichten fragen", "Nach dem Weg fragen", "Die Karte annehmen"],
        "transitions": {
            "schattenwichten": "1_ask_about_shadows",
            "fragen": "1_ask_about_shadows",
            "weg": "1_ask_way",
            "karte": "1_ask_way",
            "annehmen": "1_ask_way",
            "weiter": "1_forest",
            "gehen": "1_forest"
        }
    },
    "1_ask_about_shadows": {
        "type": "dialogue",
        "narrative": "Finnian erklärt: 'Die Schattenwichte kommen nachts aus der alten Zitadelle im Flüsterwald. Sie schleichen durch die Gassen und stehlen alles. Licht scheint sie zu vertreiben!'\n\nEin kleines Mädchen namens Elara tugt an deinem Ärmel: 'Ich war mal im Flüsterwald! Da hab ich seltsame Lichter gesehen... Blau, dann Rot, dann Grün, dann Gelb. Und dann ging ein Stein auf!'",
        "audio_text": "Finnian erzählt von den Schattenwichten und Elara gibt einen Hinweis.",
        "options": ["Zum Flüsterwald aufbrechen", "Nach dem Weg zur Zitadelle fragen"],
        "transitions": {
            "wald": "1_forest",
            "flüsterwald": "1_forest",
            "weg": "1_ask_way",
            "zitadelle": "1_ask_way",
            "aufbrechen": "1_forest",
            "gehen": "1_forest"
        }
    },
    "1_ask_way": {
        "type": "dialogue",
        "narrative": "Finnian kratzt sich am Kopf. 'Der Haupteingang der Zitadelle ist versiegelt. Aber es heißt, es gäbe einen geheimen Pfad durch die alten Minen. Der Eingang soll hinter einem Wasserfall im Flüsterwald versteckt sein.'",
        "audio_text": "Finnian erklärt den Weg durch die alten Minen.",
        "options": ["Zum Wasserfall aufbrechen", "Zurück zum Dorfplatz"],
        "transitions": {
            "wasserfall": "1_forest",
            "aufbrechen": "1_forest",
            "gehen": "1_forest",
            "dorf": "1_start"
        }
    },
    "1_forest": {
        "type": "narrative",
        "scene": "forest",
        "narrative": "Ihr betretet den Flüsterwald. Uralte Bäume ragen über euch auf, ihre Kronen verdecken fast das gesamte Sonnenlicht. Ein leises Flüstern begleitet euch...\n\nBald steht ihr vor einer tiefen Schlucht. Eine zerfallene Holzbrücke führt hinüber, aber sie sieht alles andere als vertrauenswürdig aus.",
        "audio_text": "Ihr erreicht den Flüsterwald. Vor euch eine tiefe Schlucht mit einer morschen Brücke.",
        "options": ["Die Brücke überqueren", "Einen Baum fällen", "Einen anderen Weg suchen", "Die Schlucht entlanggehen"],
        "transitions": {
            "brücke": "1_bridge_cross",
            "baum": "1_bridge_fall_tree",
            "fällen": "1_bridge_fall_tree",
            "weg": "1_forest_continue",
            "schlucht": "1_forest_continue"
        },
        "puzzle": {
            "type": "skill_check",
            "skill": "athletik",
            "keywords": ["baum", "fällen", "stark", "umlegen"],
            "success": "Ihr fällt einen mächtigen Baum, der genau über die Schlucht fällt!",
            "failure": "Der Baum ist zu massiv."
        }
    },
    "1_bridge_fall_tree": {
        "type": "narrative",
        "narrative": "Ihr fällt einen mächtigen Baum, der genau über die Schlucht fällt - eine perfekte Brücke!",
        "audio_text": "Der Baum fällt und bildet eine Brücke.",
        "options": ["Weitergehen"],
        "transitions": {
            "weiter": "1_forest_continue",
            "gehen": "1_forest_continue"
        }
    },
    "1_bridge_cross": {
        "type": "skill_check",
        "narrative": "Vorsichtig betretet ihr die Brücke. Sie ächzt und knarrt unter eurem Gewicht...",
        "audio_text": "Die Brücke ächzt bedrohlich.",
        "options": ["Weitergehen", "Zurückweichen"],
        "dc": 10,
        "success": "Ihr kommt sicher auf der anderen Seite an.",
        "failure": "Ein morsches Brett bricht! Ihr stürzt und nehmt Schaden.",
        "transitions": {
            "weiter": "1_forest_continue"
        }
    },
    "1_forest_continue": {
        "type": "narrative",
        "narrative": "Hinter der Schlucht lichtet sich der Wald. Ihr hört das Rauschen von Wasser - ein Wasserfall! Dahinter müsste der Mineneingang sein.\n\nDoch plötzlich raschelt es im Gebüsch...",
        "audio_text": "Ihr erreicht einen Wasserfall. Aber etwas raschelt im Gebüsch.",
        "options": ["Nachsehen", "Weitergehen"],
        "transitions": {
            "nachsehen": "1_forest_combat",
            "weiter": "1_forest_combat"
        }
    },
    "1_forest_combat": {
        "type": "combat",
        "narrative": "Zwei Spinnenkrabben schießen aus dem Unterholz hervor! Ihre Scheren klappern bedrohlich.",
        "audio_text": "Zwei Spinnenkrabben greifen an!",
        "enemies": [{"id": "spinnenkrabbe", "count": 2}],
        "next_on_success": "1_waterfall",
        "options": ["Angreifen!", "Verteidigen"],
        "transitions": {
            "angreifen": "1_waterfall",
            "verteidigen": "1_waterfall"
        }
    },
    "1_waterfall": {
        "type": "narrative",
        "scene": "waterfall",
        "narrative": "Hinter dem tosenden Wasserfall entdeckt ihr tatsächlich einen verborgenen Stolleneingang! Eine massive Steintür versperrt den Weg.\n\nIn den Stein sind vier Symbole gemeißelt: Eine Sonne, ein Mond, ein Stern und eine Wolke.\n\nDarunter steht: 'Wenn der Tag zur Ruhe kommt und das Licht erlischt, erscheine ich. In der tiefsten Dunkelheit leuchte ich am hellsten. Was bin ich?'",
        "audio_text": "Ein geheimer Eingang mit einer Steintür und einem Rätsel.",
        "options": ["Mond", "Sonne", "Stern", "Wolke"],
        "puzzle": {
            "type": "riddle",
            "keywords": ["mond", "moon"],
            "success": "Das Mondsymbol leuchtet auf! Mit einem tiefen Grollen öffnet sich die Steintür und gibt den Weg in die Minen frei.",
            "failure": "Nichts passiert."
        },
        "transitions": {
            "mond": "1_mine_entrance",
            "moon": "1_mine_entrance",
            "solved": "1_mine_entrance"
        }
    },
    "1_mine_entrance": {
        "type": "narrative",
        "scene": "mines",
        "narrative": "Die Stollen sind dunkel und feucht. Hier und da liegen verrostete Spitzhacken und zerbrochene Wagen.\n\nIn einer Sackgasse findet ihr einen alten, verstaubten Schrein. Auf dem Altar liegt eine leuchtende Feder, die ein sanftes, goldenes Licht ausstrahlt.",
        "audio_text": "Ihr betretet die Minen. In einer Nische liegt eine leuchtende Feder.",
        "options": ["Die Feder annehmen", "Weitergehen"],
        "transitions": {
            "feder": "1_mine_exit",
            "annehmen": "1_mine_exit",
            "weiter": "1_mine_exit"
        },
        "loot": [{"item": "Leuchtende Feder", "effect": "Lichtquelle, +5 gegen Schattenwichte"}]
    },
    "1_mine_exit": {
        "type": "narrative",
        "narrative": "Nach einer Weile seht ihr wieder Tageslicht. Der Minenausgang führt direkt in den Hinterhof der vergessenen Zitadelle! Überwuchert von Efeu und Moos erhebt sich das uralte Gemäuer vor euch.\n\nEine Falltür im Boden ist der einzige Weg hinein - aber sie ist mit einem Zahlenrätsel gesichert: 'Drei Rätsel, drei Zahlen. Was ist die Kombination?'",
        "audio_text": "Ihr erreicht die Zitadelle. Eine Falltür mit Zahlenrätsel.",
        "options": ["354 eingeben", "Umgebung untersuchen"],
        "transitions": {
            "354": "2_great_hall",
            "drei fünf vier": "2_great_hall",
            "untersuchen": "1_mine_exit",
            "kombination": "1_mine_exit"
        },
        "puzzle": {
            "type": "number_riddle",
            "keywords": ["354", "drei fünf vier"],
            "success": "KLICK! Die Falltür entriegelt sich!",
            "failure": "Ein rostiges Zischen ertönt - Giftgas strömt aus!"
        }
    },
    "2_great_hall": {
        "type": "narrative",
        "chapter": 2,
        "scene": "great_hall",
        "narrative": "Die Falltür führt in eine große, düstere Halle. Hohe Säulen tragen das Deckengewölbe.\n\nIn der Mitte der Halle lagern drei Goblins und ein massiger Ork-Krieger um ein Feuer. Sie haben euch noch nicht bemerkt...",
        "audio_text": "Ihr betretet die große Halle. Drei Goblins und ein Ork am Feuer.",
        "options": ["Angreifen!", "Einschleichen", "Verhandeln", "Umgehen"],
        "transitions": {
            "angreifen": "2_great_hall_combat",
            "schleichen": "2_great_hall_combat",
            "verhandeln": "2_great_hall_combat",
            "umgehen": "2_library"
        }
    },
    "2_great_hall_combat": {
        "type": "combat",
        "narrative": "Der Kampf beginnt! Drei Goblins und ein Ork-Krieger stürmen auf euch zu.",
        "audio_text": "Kampf beginnt!",
        "enemies": [{"id": "goblin", "count": 3}, {"id": "ork", "count": 1}],
        "next_on_success": "2_library",
        "options": ["Angreifen!", "Verteidigen"],
        "transitions": {
            "weiter": "2_library"
        }
    },
    "2_library": {
        "type": "narrative",
        "chapter": 2,
        "scene": "library",
        "narrative": "Hinter der Halle liegt eine verstaubte Bibliothek. In der Mitte steht ein steinerner Tisch mit drei Vertiefungen.\n\nAn der Wand hängt eine Inschrift:\n'Der weise Magier besitzt drei Schätze.\nDas erste ist unsichtbar, doch schwerer als ein Berg.\nDas zweite ist leise, doch lauter als ein Donner.\nDas dritte reist um die Welt, doch bleibt am selben Ort.'",
        "audio_text": "Eine Bibliothek mit einem Rätsel um drei Schätze.",
        "options": ["Wissen", "Geduld", "Briefmarke", "Bücherregale durchsuchen"],
        "transitions": {
            "wissen": "3_shadows_combat",
            "geduld": "3_shadows_combat",
            "briefmarke": "3_shadows_combat",
            "buch": "2_library",
            "regal": "2_library"
        },
        "puzzle": {
            "type": "exploration_puzzle",
            "keywords": ["wissen", "geduld", "briefmarke"],
            "success": "Als ihr die drei Gegenstände in die Vertiefungen legt, öffnet sich der Boden!",
            "failure": "Das scheint nicht der richtige Gegenstand zu sein."
        }
    },
    "3_shadows_combat": {
        "type": "combat",
        "chapter": 3,
        "scene": "treasure_approach",
        "narrative": "Ein letzter Gang führt zur Schatzkammer. Aber der Weg wird von drei Schattenkreaturen bewacht! Sie flackern im Dunkeln.",
        "audio_text": "Drei Schattenkreaturen versperren den Weg!",
        "enemies": [{"id": "schattenkreatur", "count": 3}],
        "next_on_success": "3_treasure_room",
        "options": ["Angreifen!", "Verteidigen", "Licht einsetzen"],
        "transitions": {
            "weiter": "3_treasure_room"
        }
    },
    "3_treasure_room": {
        "type": "narrative",
        "chapter": 3,
        "scene": "treasure",
        "narrative": "Die Schatzkammer öffnet sich - ein Raum voller Gold, Juwelen und uralter Artefakte!\n\nIn der Mitte thront ein Kristallschädel auf einem Podest, der ein sanftes blaues Licht ausstrahlt.\n\nWas tut ihr mit dem Schatz?",
        "audio_text": "Ihr habt die Schatzkammer gefunden!",
        "options": ["Mit dem Dorf teilen", "Kristallschädel zerstören", "Alles behalten", "Nur Nötigste nehmen"],
        "transitions": {
            "teilen": "3_return",
            "dorf": "3_return",
            "zerstören": "3_return",
            "behalten": "3_return",
            "nehmen": "3_return",
            "nötigste": "3_return"
        },
        "loot": [{"item": "Gold", "amount": "10"}, {"item": "Seltene Waffe", "chance": 0.5}]
    },
    "3_return": {
        "type": "narrative",
        "chapter": 3,
        "scene": "return",
        "narrative": "Ihr kehrt triumphierend nach Dämmerbruch zurück! Die Dorfbewohner empfangen euch mit Jubel.\n\nFinnian hält sein Versprechen: 'Hier ist eure Belohnung, und ihr seid immer willkommen!'\n\nDas Abenteuer 'Der Schatten-Schatz der vergessenen Zitadelle' ist abgeschlossen!",
        "audio_text": "Das Abenteuer ist abgeschlossen!",
        "options": ["Zum Dashboard zurückkehren"],
        "adventure_complete": True
    }
}
