# Neo4j Graph Database Assignment: Banking Use Case

----

In this assignment, we will learn about modeling the RDBMS data (exported as a CSV data based on Banking and Financial Services domain) in the Neo4j Enterprise graph database, and implementing multiple use cases to analyze the financial and customer-related data using Cypher querying language.

----

## Setting up Neo4j Enterprise on Docker

Pre-requisite: Any OS (Linux, MacOS, Windows) with Docker Engine, Python 3.9.x

Run the below command to pull Neo4j Enterprise v5.12 image to Local docker image repository
```
docker pull neo4j:5.12.0-enterprise
```

Run the below command to run Neo4j Enterprise v5.12 as a docker container
```
docker run --env=NEO4J_AUTH=neo4j/neo4j2023 --env=NEO4J_ACCEPT_LICENSE_AGREEMENT=yes --volume=C:\Users\sumit\OneDrive\Documents\neo4j\data:/data -p 7473:7473 -p 7474:7474 -p 7687:7687 -d neo4j:5.12.0-enterprise
```

### Note:

#### Ports
Port 7474 and Port 7687 is binded for HTTP (browser access) and Bolt access to Neo4j Server respectively

#### Env parameters
NEO4J_AUTH - Allow parsing of username and password parameters
NEO4J_ACCEPT_LICENSE_AGREEMENT - Neo4j license agreement

#### Volume mounts
data (C:\Users\sumit\OneDrive\Documents\neo4j\data) - Map local directory for Data storage, you can change it as per your local directory path


## Access Neo4j Browser

To access Neo4j Browser, access the below URL via web browser
```
http://< ip_addr >:7474
```

Enter below credentials to Login (you can enter your own credentials that was configured while running the docker container)
```
username: neo4j
password: neo4j2023
```

## Neo4j Graph Data Model

To create a Neo4j graph data model using the [provided CSV files](https://gist.github.com/kesseract/19bf6eb6f6a5adecddedf2a081b51789), you can define nodes and relationships based on the data. Neo4j is a graph database, and it works with nodes to represent entities and relationships to represent connections between entities. Here's a simplified graph data model based on CSV headers:

1. **Customers Node:**

   - Node Label: `Customer`
   - Properties: `CIF, Age, EmailAddress, FirstName, LastName, PhoneNumber, Gender, Address, Country, JobTitle`

2. **Accounts Node:**

   - Node Label: `Account`
   - Properties: `AccountNumber`

3. **Transactions Node:**

   - Node Label: `Transaction`
   - Properties: `TransactionID`

4. **Merchants Node:**

   - Node Label: `Merchant`
   - Properties: `Merchant`

5. **Card Node:**

   - Node Label: `Card`
   - Properties: `CardNumber, CardIssuer`

6. **Relationships:**

   - `[:HAS_ACCOUNT]` from Customer to Account (connecting each customer to their account(s)).
   - `[:SEND_TO]` from Account to Transaction (connecting accounts to transactions). Properties for this relationship: `Amount, TransferDatetime`
   - `[:RECEIVED_IN]` from Transaction to Account (connecting sender and receiver accounts to transactions in the transfers.csv). Properties for this relationship: `Amount, TransferDatetime`
   - `[:MADE_PURCHASE]` from Transaction to Merchant (connecting transactions to merchants in the purchases.csv). Properties for this relationship: `Amount, PurchaseDatetime`
   - `[:USED_CARD]` from Transaction to Card (connecting transactions to cards in the purchases.csv). Properties for this relationship: `Amount, PurchaseDatetime`
   - `[:HAS_CARD]` from Customer to Card (connecting each customer to their card(s)).
   

You can use [Arrows.app](https://arrows.app) to create and visualize the above the graph model. See this graph model on [this arrows link](https://arrows.app/#/local/id=O2IO-EDDFIVxVdglYGIB). JSON file (`Arrows_Data_Model.json`) is also added in this github repo which could be imported to Arrows app.
   

## Import the [CSV data](https://gist.github.com/kesseract/19bf6eb6f6a5adecddedf2a081b51789) based on the Graph Data Model using Python script

Pre-requisite: Install Neo4j python library

```
pip3 install neo4j
```

First step is to create node uniqueness contraints, ensuring no duplicates for the given node label and ID property exist in the database. This also ensures no duplicates are introduced in future.

And then, define the functions to load data from the CSV files followed by creation of nodes and relationships. 

You can find the Python script (`Neo4jImporter.py`) added in this repo to import the CSV data based on the graph data model defined in arrows app. Please make sure to update your Neo4j server URI and User credentials in the same script as below:
    
    # Credentials of Docker container running Neo4j Enterprise server 
    uri = "neo4j://localhost:7687"
    user = "neo4j"
    password = "neo4j2023"
	
	
Run this Python script using below command:

```
python3 Neo4jImporter.py
```

	
## Exploring Banking Use Cases using Cypher Queries

Once, CSV data is successfully imported and modeled into Neo4j server, the graph data model we've described can be used to implement a variety of use cases involving financial transactions, customer information, and card usage. Here are some potential use cases and examples of Cypher queries:


1. **Customer Segmentation:**

   - *Use Case:* Grouping customers based on common characteristics for targeted marketing.

   - *Example Cypher Query:*
     ```cypher
     MATCH (c:Customer)
     WHERE c.Age > 20 AND c.Country =  ‘India’
     RETURN c.FirstName, c.LastName
     ```

2. **Transaction Timeline or Purchase History**

   - *Use Case:* Visualizing the timeline of transfers or purchases for a specific customer.

   - *Example Cypher Queries:*
     ```cypher
	 MATCH (c:Customer)-[:HAS_ACCOUNT]->(a:Account)-[t:SEND_TO]->(:Transaction)
	 WHERE c.CIF = 1
	 RETURN a.AccountNumber, t.TransferDatetime, t.Amount
	 ORDER BY t.TransferDatetime DESC
     ```
     ```cypher
	 MATCH (c:Customer)-[:HAS_CARD]->(card:Card)<-[t:USED_CARD]->(:Transaction)-[:MADE_PURCHASE]->(m:Merchant)
	 WHERE c.CIF = 1 
	 RETURN c.CIF, card.CardNumber, t.Amount, t.PurchaseDatetime
	 ORDER BY t.PurchaseDatetime DESC
     ```
	 
3. **Customer Analytics:**

   - *Use Case:* Analyzing customer behavior and demographics.

   - *Example Cypher Query:*
     ```cypher
     MATCH (c:Customer)
     RETURN c.Gender, AVG(c.Age) AS AvgAge, COUNT(c) AS CustomerCount
     ```
	 
4. **Customer Recommendations:**

   - *Use Case:* Recommending products or services to customers based on their purchase history with a particular merchant.

   - *Example Cypher Query:*
     ```cypher
     MATCH (c:Customer)-[:HAS_CARD]->(card:Card)<-[:USED_CARD]->(:Transaction)-[:MADE_PURCHASE]->(m:Merchant)
     WHERE m.Merchant = 'Amazon.com'
     RETURN c.FirstName, c.LastName
     ```

5. **Fraud Detection:**
   
   - *Use Case:* Detecting suspicious transactions or patterns of activity to enhance transaction scoring and identify fraudulent patterns.
   
   - *Example Cypher Query:*
     ```cypher
	 MATCH (c:Customer)-[:HAS_ACCOUNT]->(a:Account)-[t:SEND_TO]->(:Transaction)
	 WHERE t.Amount > 10000
	 RETURN c, a, t
     ```

6. **Merchant Insights:**

   - *Use Case:* Analyzing transaction data by merchant.

   - *Example Cypher Query:*
     ```cypher
	 MATCH (m:Merchant)<-[a:MADE_PURCHASE]-(:Transaction)
	 RETURN m.Merchant, AVG(a.Amount) AS AvgTransactionAmount
     ```

7. **Card Issuer Analysis:**

   - *Use Case:* Studying customer preferences of card issuers.

   - *Example Cypher Query:*
     ```cypher
	 MATCH (c:Customer)-[:HAS_CARD]->(card:Card)
     RETURN card.CardIssuer, COUNT(c) AS CustomerCount
     ```

8. **Card Usage Analysis:**

    - *Use Case:* Analyzing card issuer performance by the card usage count.

    - *Example Cypher Query:*
      ```cypher
	  MATCH (card:Card)<-[:USED_CARD]-(t:Transaction)
	  RETURN card.CardIssuer, COUNT(t) AS TransactionCount
      ```
	 
9. **Payment Network Analysis:**

   - *Use Case:* Understanding the flow of payments between accounts and customers.

   - *Example Cypher Query:*
     ```cypher
	 MATCH path = (sender:Account)-[t:SEND_TO]->(:Transaction)-[:RECEIVED_IN]->(receiver:Account)
	 WHERE t.Amount > 100000
	 RETURN path
     ```	 


These are just a few examples of the use cases that can be implemented with this graph data model. The flexibility and versatility of Neo4j and graph databases allow you to query and analyze financial and customer-related data in various ways to support different business needs. Depending on your specific requirements, you can create more complex queries and analytics to gain deeper insights into your financial data and make data-driven decisions.
