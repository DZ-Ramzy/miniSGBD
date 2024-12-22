from DiskManager import DiskManager
from BufferManager import BufferManager
from DBManager import DBManager
from ColInfo import ColInfo
from Relation import Relation
from DBConfig import DBConfig
from pageId import PageId
import struct
import traceback
import json

class SGBD:
    
    def __init__(self, dbConfig):  
        self.dbConfig = dbConfig
        self.diskManager = DiskManager(dbConfig)  
        self.diskManager.LoadState()
        self.bufferManager = BufferManager(dbConfig,self.diskManager)
        self.dbManager = DBManager(dbConfig) 
        self.dbManager.LoadState()

    def ProcessCreateDatabaseCommand(self, cmd):
        nom = cmd.split()[2]
        self.dbManager.CreateDatabase(nom)

    def ProcessSetCurrentDatabaseCommand(self, cmd):
        nom = cmd.split()[2]
        self.dbManager.SetCurrentDatabase(nom)
    
    def ProcessAddTableToCurrentDatabaseCommand(self, cmd):
        nom = cmd.split()[2] #recuperer le nom
        table = cmd.split()[3] #recupere les cols
        table = table[1:len(table)-1] #eliminer les ()
        tableCol = table.split(",")  #pour les infos des cols
        cols = [] #list to pass to the relation constructer
        var = False
        for i in range(len(tableCol)):
            tableColi = tableCol[i].split(":")
            if(tableColi[1].startswith("VARCHAR")):
                var = True
            cols.append(ColInfo(tableColi[0],tableColi[1]))

        newPage = self.diskManager.AllocPage()
        bufferHeader = self.bufferManager.GetPage(newPage)
        self.bufferManager.buffer_pool[bufferHeader][12:16] = struct.pack("i", 1)
        self.bufferManager.buffer_pool[bufferHeader][20:24] = struct.pack("i", 0)
        self.bufferManager.buffer_pool[bufferHeader][24:28] = struct.pack("i", 0)
        i = 28
        while(i<self.dbConfig.pageSize+28):
            self.bufferManager.buffer_pool[bufferHeader][i:i+1] = struct.pack("c", b"X")
            i += 1
        self.bufferManager.FreePage(newPage,True)
        eader = self.bufferManager.GetPage(newPage)
        relation = Relation(nom,len(tableCol),cols,var,self.bufferManager,newPage)
        self.dbManager.AddTableToCurrentDatabase(relation)

    def ProcessGetTableFromCurrentDatabaseCommand(self, cmd):
        for table in self.dbManager.active_database.tables:
            self.dbManager.GetTableFromCurrentDatabase(table.nom_table)

    def ProcessRemoveTableFromCurrentDatabaseCommand(self, cmd):
        nom = cmd.split()[2]
        try:
            with open("data.json", "r") as file:
                data = json.load(file)
                fid =  data["databases"][{self.dbManager.active_database}][{nom}]["headerPageId"]["FileIdx"]
                ppid = data["databases"][{self.dbManager.active_database}][{nom}]["headerPageId"]["PageIdx"]
                self.bufferManager.FreePage(PageId(fid,ppid))
        except Exception as e:
            i = 1 #just a random line
        self.dbManager.RemoveTableFromCurrentDatabase(nom)

    def ProcessRemoveDatabaseCommand(self, cmd):
        nom = cmd.split()[2]
        self.dbManager.RemoveDatabase(nom)

    def ProcessRemoveTablesFromCurrentDatabaseCommand(self, cmd):
        self.dbManager.RemoveTablesFromCurrentDatabase()

    def ProcessRemoveDatabasesCommand(self, cmd):
        self.dbManager.RemoveDatabases()

    def ProcessListDatabasesCommand(self, cmd):
        self.dbManager.ListDatabases()

    def run(self):
        print("Welcome dans notre SGBD. Tapez une commande ou 'QUIT' pour quitter.")
        while True:
            try:
                # Affiche le prompt "?" et récupère l'entrée du user
                cmd = input("? ").strip()
                if cmd.upper() == "QUIT":
                    print("Sauvegarde de l'état.")
                    self.diskManager.SaveState()
                    self.dbManager.SaveState()
                    print("Ciao !")
                    break  # Quitte la boucle pour arrêter l'application (pas tres cool d'utiliser ça mais bon)

                # Analyse la commande et appelle la méthode appropriée
                action = cmd.split()[0].upper()
                if action == "CREATE" and cmd.split()[1].upper() == "DATABASE":
                    self.ProcessCreateDatabaseCommand(cmd)
                elif action == "SET" and cmd.split()[1].upper() == "DATABASE":
                    self.ProcessSetCurrentDatabaseCommand(cmd)
                elif action == "CREATE" and cmd.split()[1].upper() == "TABLE":
                    self.ProcessAddTableToCurrentDatabaseCommand(cmd)
                elif action == "GET" and cmd.split()[1].upper() == "TABLE":
                    self.ProcessGetTableFromCurrentDatabaseCommand(cmd)
                elif action == "DROP" and cmd.split()[1].upper() == "TABLE":
                    self.ProcessRemoveTableFromCurrentDatabaseCommand(cmd)
                elif action == "DROP" and cmd.split()[1].upper() == "DATABASE":
                    self.ProcessRemoveDatabaseCommand(cmd)
                elif action == "DROP" and cmd.split()[1].upper() == "TABLES":
                    self.ProcessRemoveTablesFromCurrentDatabaseCommand(cmd)
                elif action == "DROP" and cmd.split()[1].upper() == "DATABASES":
                    self.ProcessRemoveDatabasesCommand(cmd)
                elif action == "LIST" and cmd.split()[1].upper() == "DATABASES":
                    self.ProcessListDatabasesCommand(cmd)
                elif action == "LIST" and cmd.split()[1].upper() == "TABLES":
                    self.dbManager.ListTablesInCurrentDatabase()  # Appelle directement depuis dbManager
                else:
                    print("Commande non reconnue :(")
            except Exception as e:
                print(f"Erreur lors du traitement de la commande : {e}")
                #error_message = ''.join(traceback.format_exc())
                #print(error_message)
                

        @staticmethod
    def parseValues(columns_str: str) -> list[ColInfo]:
        columns = []
        column_parts = columns_str[1:-1].split(",")
        for column_part in column_parts:
            columns.append(column_part)

        return columns

    @staticmethod
    def parseColumns(columns_str: str) -> list[ColInfo]:
        columns = []
        column_parts = columns_str[1:-1].split(",")
        for column_part in column_parts:
            name, type_str = column_part.split(":")
            if type_str == "INT":
                columns.append(ColInfo(name, ColInfo.Int()))
            elif type_str == "REAL":
                columns.append(ColInfo(name, ColInfo.Float()))
            elif type_str.startswith("CHAR("):
                size = int(type_str[5:-1])
                columns.append(ColInfo(name, ColInfo.Char(size)))
            elif type_str.startswith("VARCHAR("):
                size = int(type_str[8:-1])
                columns.append(ColInfo(name, ColInfo.VarChar(size)))
        return columns

        
    def processInsertCommand(self,reste: list[str]):
        # Récupérer la table de la base de données courante
            if reste[0].upper() == "INTO" and reste[2].upper() == "VALUES":
                table = self.dbManager.GetTableFromCurrentDatabase(reste[1])
                if table is None:
                    print(f"Table {reste[1]} does not exist.")
                    return
                # Vérifier que le nombre de valeurs correspond au nombre de colonnes
                values = self.parseValues(reste[3])
                if len(values) != table.nb_column:
                    print(f"Number of values does not match the number of columns in table {reste[1]}.")
                    return
                # Convertir les valeurs en types appropriés
                typed_values = []
                for i, value in enumerate(values):
                    column_type = table.columns[i].type
                    if column_type == ColInfo.Int():
                        typed_values.append(int(value))
                    elif column_type == ColInfo.Float():
                        typed_values.append(float(value))
                    elif column_type == ColInfo.Char(column_type.size) and len(value) == column_type.size:
                        typed_values.append(value)
                    elif column_type == ColInfo.VarChar(column_type.size) and len(value) <= column_type.size:
                        typed_values.append(value)
                    else:
                        print("Invalid column type.")
                        return
                print(typed_values)
                # Insérer le tuple dans la table
                table.InsertRecord(typed_values)
                print(f"Record inserted into table {reste[1]}.")
            else:
                print("Invalid INSERT command.")


        def processInsertCommand(self, reste: list[str]):
        if len(reste) < 3:
            print("Invalid command format.")
            return

        # Vérifier si la commande commence par BULKINSERT
        if reste[0].upper() == "BULKINSERT" and reste[1].upper() == "INTO":
            table_name = reste[2]
            csv_file = reste[3]

            # Récupérer la table de la base de données courante
            table = self.dbManager.GetTableFromCurrentDatabase(table_name)
            if table is None:
                print(f"Table {table_name} does not exist.")
                return

            try:
                # Lire le fichier CSV
                with open(csv_file, 'r', encoding='utf-8') as file:
                    for line in file:
                        # Supprimer les espaces et découper la ligne en valeurs
                        values = [value.strip().strip('"') for value in line.split(',')]

                        # Vérifier que le nombre de valeurs correspond au nombre de colonnes
                        if len(values) != table.nb_column:
                            print(f"Number of values does not match the number of columns in table {table_name}.")
                            return

                        # Convertir les valeurs en types appropriés
                        typed_values = []
                        for i, value in enumerate(values):
                            column_type = table.columns[i].type
                            try:
                                if column_type == ColInfo.Int():
                                    typed_values.append(int(value))
                                elif column_type == ColInfo.Float():
                                    typed_values.append(float(value))
                                elif column_type == ColInfo.Char(column_type.size) and len(value) == column_type.size:
                                    typed_values.append(value)
                                elif column_type == ColInfo.VarChar(column_type.size) and len(
                                        value) <= column_type.size:
                                    typed_values.append(value)
                                else:
                                    print(f"Invalid column type for value '{value}' in column {i + 1}.")
                                    return
                            except ValueError as e:
                                print(f"Error converting value '{value}' to type {column_type}: {e}")
                                return

                        # Insérer le tuple dans la table
                        table.InsertRecord(typed_values)

                print(f"Bulk insert into table {table_name} completed successfully.")

            except FileNotFoundError:
                print(f"CSV file {csv_file} not found.")

            except Exception as e:
                print(f"An error occurred during BULKINSERT: {e}")

        else:
            print("Invalid BULKINSERT command.")



    def main(path):
        dbConfig = DBConfig.load_db_config(path)
        sgbd = SGBD(dbConfig)
        sgbd.run()


if __name__ == "__main__":
    SGBD.main("./config.json")
