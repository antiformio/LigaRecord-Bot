def resetTable():
    """
        Function to reset the table to default values. Use carefully because it deletes the previous table.
    """
    readSave = serialize.serialization()
    dataForFrame = {
        "Equipa": [
            "Alphateam",
            "FC Kombichos",
            "Here for Beer",
            "FC Chupitos",
            "ClassOnGrass",
            "Virose",
            "FCBalasar",
            "SL Bernardes",
            "TascoFC",
            "Athletic Dafundo",
            "Chuecos FC",
            "FC Poukitxo",
            "Atlético Alijoense",
            "Black Mamba FC",
            "Fonte do Olmo FC",
            "Messishow",
        ],
        "Pontos": [11, 15, 7, 2, 5, 14, 9, 14, 14, 15, 8, 7, 3, 9, 11, 10],
        "Jogos": [6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6],
        "V": [3, 4, 2, 0, 1, 4, 2, 4, 4, 5, 2, 2, 1, 3, 3, 3],
        "E": [1, 0, 0, 2, 2, 1, 1, 1, 0, 0, 0, 1, 0, 0, 1, 0],
        "D": [2, 2, 4, 4, 3, 1, 3, 1, 2, 1, 4, 3, 5, 3, 2, 3],
        "GM": [
            293,
            292,
            231,
            259,
            231,
            280,
            258,
            293,
            272,
            280,
            271,
            259,
            212,
            234,
            255,
            255,
        ],
        "GS": [
            279,
            279,
            265,
            292,
            246,
            254,
            271,
            247,
            246,
            235,
            289,
            265,
            255,
            240,
            243,
            269,
        ],
        "GA": [14, 13, -34, -33, -15, 26, -13, 46, 26, 45, -18, -6, -43, -6, 12, -14],
    }
    tabela = pd.DataFrame(
        dataForFrame,
        columns=["Equipa", "Pontos", "Jogos", "V", "E", "D", "GM", "GS", "GA"],
    )
    pickle.dump(tabela, open("Tabela", "wb"))
    readSave.AWSupload("Tabela", "Tabela")


def createCalendar():
    """
        Function to create calendar. Eatch file (jornada) consists on a list of tuples. filenames is as following: CalendarioX (X being Ronda)
    """
    readSave = serialize.serialization()
    calendario = [
        ("FC Kombichos", "Messishow"),
        ("FCBalasar", "FC Poukitxo"),
        ("Athletic Dafundo", "Black Mamba FC"),
        ("FC Chupitos", "SL Bernardes"),
        ("TascoFC", "Virose"),
        ("Fonte do Olmo FC", "ClassOnGrass"),
        ("Here for Beer", "Alphateam"),
        ("Chuecos FC", "Atlético Alijoense"),
    ]
    pickle.dump(calendario, open("Calendario7", "wb"))
    readSave.AWSupload("Calendario7", "Calendario7")

