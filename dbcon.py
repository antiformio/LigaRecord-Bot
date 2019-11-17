import sqlite3

""""
Exemplo de formato de ficheiro a importar por este código:
    Messishow,Chuecos FC
    FC Poukitxo,FC Kombichos
    Black Mamba FC,FCBalasar
    SL Bernardes,Athletic Dafundo
    Virose,FC Chupitos
    ClassOnGrass,TascoFC
    Alphateam,Fonte do Olmo FC
    Atlético Alijoense,Here for Beer
    next
    Messishow,FC Poukitxo
    FC Kombichos,Black Mamba FC
    FCBalasar,SL Bernardes
    Athletic Dafundo,Virose
    FC Chupitos,ClassOnGrass
    TascoFC,Alphateam
    Fonte do Olmo FC,Atlético Alijoense
    Chuecos FC,Here for Beer
    next

Cada bloco contém uma jornada separada pela linha next
"""

db_file = "/Users/filipemartins/Desktop/VScodeProjects/LigaRecord-Bot/db.sqlite"
conn = sqlite3.connect(db_file)
c = conn.cursor()

file = open("testcsv.txt", "r")

jornada = 1
for line in file:
    if "next" in line:
        jornada += 1
        continue
    fields = line.split(",")
    casa = fields[0]
    fora = fields[1].rstrip()
    c.execute(
        f"INSERT INTO JOGO (`id_jornada`,`casa`,`fora`) VALUES ({jornada}, '{str(casa)}', '{str(fora)}')"
    )

conn.commit()
conn.close()
