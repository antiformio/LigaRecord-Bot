import sqlite3, json


class WriteToDb:
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

    def readCredentials(self):
        with open("credentials.json") as f:
            data = json.load(f)
        return data["sqlite_path"]

    def __init__(self):
        self.db_file = self.readCredentials()
        self.conn = sqlite3.connect(self.db_file)
        self.c = self.conn.cursor()

    def txt_to_db(self):
        file = open("testcsv.txt", "r")

        self.jornada = 1
        for line in file:
            if "next" in line:
                jornada += 1
                continue
            fields = line.split(",")
            casa = fields[0]
            fora = fields[1].rstrip()
            try:
                self.c.execute(
                    f"INSERT INTO JOGO (`id_jornada`,`casa`,`fora`) VALUES ({jornada}, '{str(casa)}', '{str(fora)}')"
                )
            except Exception:
                print("Erro ao gravar calendario para a BD")
                return

        self.conn.commit()
        self.conn.close()


class ReadFromDB:
    def readCredentials(self):
        with open("credentials.json") as f:
            data = json.load(f)
        return data["sqlite_path"]

    def __init__(self):
        self.db_file = self.readCredentials()
        self.conn = sqlite3.connect(self.db_file)
        self.c = self.conn.cursor()

    def select_database(self, fields, table, column, value):
        self.c.execute(f'SELECT {fields} FROM {table} WHERE {column}="{value}"')
        data = self.c.fetchall()
        self.conn.close()
        return data

    def get_calendario(self, jornada):
        table_name = "JOGO"
        column_to_search = "id_jornada"
        data = self.select_database("*", table_name, column_to_search, str(jornada))
        return data

