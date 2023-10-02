from neo4j import GraphDatabase

class Neo4jImporter:
    def __init__(self, uri, user, password):
        self._uri = uri
        self._user = user
        self._password = password
        self._driver = None
        try: 
            self._driver = GraphDatabase.driver(uri, auth=(user, password))
        except Exception as e:
            print("Driver creation failed:", e)

    def close(self):
        if self._driver is not None:
            self._driver.close()
    
    # Function to load data from CSV files followed by creation of nodes
    def node_load_data_from_csv(self, session, query_params):
        query_customer_node = """
        LOAD CSV WITH HEADERS FROM ($file_path_root + $file_0) AS row
        WITH row
        WHERE NOT toInteger(trim(row.`CIF`)) IS NULL
        CALL {
        WITH row
        MERGE (n: `Customer` { `CIF`: toInteger(trim(row.`CIF`)) })
        SET n.`Age` = toInteger(trim(row.`Age`))
        SET n.`EmailAddress` = row.`EmailAddress`
        SET n.`FirstName` = row.`FirstName`
        SET n.`LastName` = row.`LastName`
        SET n.`PhoneNumber` = row.`PhoneNumber`
        SET n.`Gender` = row.`Gender`
        SET n.`Address` = row.`Address`
        SET n.`Country` = row.`Country`
        SET n.`JobTitle` = row.`JobTitle`
        } IN TRANSACTIONS OF 1000 ROWS;
        """
        try:
            session.run(query_customer_node, query_params)
        except Exception as e:
            print("Query to create Customer node failed:", e)

        query_account_node = """
        LOAD CSV WITH HEADERS FROM ($file_path_root + $file_0) AS row
        WITH row
        WHERE NOT row.`AccountNumber` IS NULL
        CALL {
        WITH row
        MERGE (n: `Account` { `AccountNumber`: row.`AccountNumber` })
        
        } IN TRANSACTIONS OF 1000 ROWS;
        """
        try:
            session.run(query_account_node, query_params)
        except Exception as e:
            print("Query to create Account node failed:", e)

        query_1_transaction_node = """
        LOAD CSV WITH HEADERS FROM ($file_path_root + $file_1) AS row
        WITH row
        WHERE NOT toInteger(trim(row.`TransactionID`)) IS NULL
        CALL {
        WITH row
        MERGE (n: `Transaction` { `TransactionID`: toInteger(trim(row.`TransactionID`)) })
        } IN TRANSACTIONS OF 1000 ROWS;
        """
        try:
            session.run(query_1_transaction_node, query_params)
        except Exception as e:
            print("Query to create Transaction node failed for transfers.csv file:", e)

        query_2_transaction_node = """
        LOAD CSV WITH HEADERS FROM ($file_path_root + $file_2) AS row
        WITH row
        WHERE NOT toInteger(trim(row.`TransactionID`)) IS NULL
        CALL {
        WITH row
        MERGE (n: `Transaction` { `TransactionID`: toInteger(trim(row.`TransactionID`)) })
        } IN TRANSACTIONS OF 1000 ROWS;
        """
        try:
            session.run(query_2_transaction_node, query_params)
        except Exception as e:
            print("Query to create Transaction node failed for purchases.csv file:", e)

        query_merchant_node = """
        LOAD CSV WITH HEADERS FROM ($file_path_root + $file_2) AS row
        WITH row
        WHERE NOT row.`Merchant` IS NULL
        CALL {
        WITH row
        MERGE (n: `Merchant` { `Merchant`: row.`Merchant` })
        
        } IN TRANSACTIONS OF 1000 ROWS;
        """
        try:
            session.run(query_merchant_node, query_params)
        except Exception as e:
            print("Query to create Merchant node failed:", e)
        
        query_card_node = """
        LOAD CSV WITH HEADERS FROM ($file_path_root + $file_2) AS row
        WITH row
        WHERE NOT row.`CardNumber` IS NULL
        CALL {
        WITH row
        MERGE (n: `Card` { `CardNumber`: row.`CardNumber` })
        SET n.`CardIssuer` = row.`CardIssuer`
        } IN TRANSACTIONS OF 1000 ROWS;
        """
        try:
            session.run(query_card_node, query_params)
        except Exception as e:
            print("Query to create Card node failed:", e)

    # Function to load data from CSV files followed by creation of relationships
    def relationship_load_data_from_csv(self, session, query_params):
        query_has_account_relationship = """
        LOAD CSV WITH HEADERS FROM ($file_path_root + $file_0) AS row
        WITH row 
        CALL {
        WITH row
        MATCH (source: `Customer` { `CIF`: toInteger(trim(row.`CIF`)) })
        MATCH (target: `Account` { `AccountNumber`: row.`AccountNumber` })
        MERGE (source)-[r: `HAS_ACCOUNT`]->(target)
        } IN TRANSACTIONS OF 1000 ROWS;
        """
        try:
            session.run(query_has_account_relationship, query_params)
        except Exception as e:
            print("Query to create HAS_ACCOUNT relationship failed:", e)

        query_has_card_relationship = """
        LOAD CSV WITH HEADERS FROM ($file_path_root + $file_0) AS row
        WITH row 
        CALL {
        WITH row
        MATCH (source: `Customer` { `CIF`: toInteger(trim(row.`CIF`)) })
        MATCH (target: `Card` { `CardNumber`: row.`CardNumber` })
        MERGE (source)-[r: `HAS_CARD`]->(target)
        } IN TRANSACTIONS OF 1000 ROWS;
        """
        try:
            session.run(query_has_card_relationship, query_params)
        except Exception as e:
            print("Query to create HAS_CARD relationship failed:", e)

        query_send_to_relationship = """
        LOAD CSV WITH HEADERS FROM ($file_path_root + $file_1) AS row
        WITH row 
        CALL {
        WITH row
        MATCH (source: `Account` { `AccountNumber`: row.`SenderAccountNumber` })
        MATCH (target: `Transaction` { `TransactionID`: toInteger(trim(row.`TransactionID`)) })
        MERGE (source)-[r: `SEND_TO`]->(target)
        SET r.`Amount` = toFloat(trim(row.`Amount`))
        SET r.`TransferDatetime` = row.`TransferDatetime`
        } IN TRANSACTIONS OF 1000 ROWS;
        """
        try:
            session.run(query_send_to_relationship, query_params)
        except Exception as e:
            print("Query to create SEND_TO relationship failed:", e)

        query_received_in_relationship = """
        LOAD CSV WITH HEADERS FROM ($file_path_root + $file_1) AS row
        WITH row 
        CALL {
        WITH row
        MATCH (source: `Transaction` { `TransactionID`: toInteger(trim(row.`TransactionID`)) })
        MATCH (target: `Account` { `AccountNumber`: row.`ReceiverAccountNumber` })
        MERGE (source)-[r: `RECEIVED_IN`]->(target)
        SET r.`Amount` = toFloat(trim(row.`Amount`))
        SET r.`TransferDatetime` = row.`TransferDatetime`
        } IN TRANSACTIONS OF 1000 ROWS;
        """
        try:
            session.run(query_received_in_relationship, query_params)
        except Exception as e:
            print("Query to create RECEIVED_IN relationship failed:", e)

        query_made_purchase_relationship = """
        LOAD CSV WITH HEADERS FROM ($file_path_root + $file_2) AS row
        WITH row 
        CALL {
        WITH row
        MATCH (source: `Transaction` { `TransactionID`: toInteger(trim(row.`TransactionID`)) })
        MATCH (target: `Merchant` { `Merchant`: row.`Merchant` })
        MERGE (source)-[r: `MADE_PURCHASE`]->(target)
        SET r.`Amount` = toFloat(trim(row.`Amount`))
        SET r.`PurchaseDatetime` = row.`PurchaseDatetime`
        } IN TRANSACTIONS OF 1000 ROWS;
        """
        try:
            session.run(query_made_purchase_relationship, query_params)
        except Exception as e:
            print("Query to create MADE_PURCHASE relationship failed:", e)
        
        query_used_card_relationship = """
        LOAD CSV WITH HEADERS FROM ($file_path_root + $file_2) AS row
        WITH row 
        CALL {
        WITH row
        MATCH (source: `Transaction` { `TransactionID`: toInteger(trim(row.`TransactionID`)) })
        MATCH (target: `Card` { `CardNumber`: row.`CardNumber` })
        MERGE (source)-[r: `USED_CARD`]->(target)
        SET r.`Amount` = toFloat(trim(row.`Amount`))
        SET r.`PurchaseDatetime` = row.`PurchaseDatetime`
        } IN TRANSACTIONS OF 1000 ROWS;
        """
        try:
            session.run(query_used_card_relationship, query_params)
        except Exception as e:
            print("Query to create USED_CARD relationship failed:", e)

def main():
    # Credentials of Docker container running Neo4j Enterprise server 
    uri = "neo4j://localhost:7687"
    user = "neo4j"
    password = "neo4j2023"

    importer = Neo4jImporter(uri, user, password)

    # Create node uniqueness constraints
    with importer._driver.session() as session:
        query_customer_contraint = """
        CREATE CONSTRAINT `imp_uniq_Customer_CIF` IF NOT EXISTS
        FOR (n: `Customer`)
        REQUIRE (n.`CIF`) IS UNIQUE;
        """
        session.run(query_customer_contraint)
        query_account_constraint = """
        CREATE CONSTRAINT `imp_uniq_Account_AccountNumber` IF NOT EXISTS
        FOR (n: `Account`)
        REQUIRE (n.`AccountNumber`) IS UNIQUE;
        """
        session.run(query_account_constraint)
        query_transaction_contraint = """
        CREATE CONSTRAINT `imp_uniq_Transaction_TransactionID` IF NOT EXISTS
        FOR (n: `Transaction`)
        REQUIRE (n.`TransactionID`) IS UNIQUE;
        """
        session.run(query_transaction_contraint)
        query_merchant_constraint = """
        CREATE CONSTRAINT `imp_uniq_Merchant_Merchant` IF NOT EXISTS
        FOR (n: `Merchant`)
        REQUIRE (n.`Merchant`) IS UNIQUE;
        """
        session.run(query_merchant_constraint)
        query_card_contraint = """
        CREATE CONSTRAINT `imp_uniq_Card_CardNumber` IF NOT EXISTS
        FOR (n: `Card`)
        REQUIRE (n.`CardNumber`) IS UNIQUE;
        """
        session.run(query_card_contraint)


    # Load data from CSV files
    with importer._driver.session() as session:
        query_params = {
            "file_path_root": "https://gist.githubusercontent.com/kesseract/19bf6eb6f6a5adecddedf2a081b51789/raw/f6800464bf4125b8dd218bc6168447a129205fdc/",
            'file_0': 'customers.csv', 
            'file_1': 'transfers.csv', 
            'file_2': 'purchases.csv'
        }

        # Create nodes after loading the data from CSV files
        importer.node_load_data_from_csv(session, query_params)
        # Create relationships after loading the data from CSV files
        importer.relationship_load_data_from_csv(session, query_params)

    importer.close()

if __name__ == "__main__":
    main()
