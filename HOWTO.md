# How to's

## Backend

The backend contains logic for conversion, generation and benchmarking of datasets and its corresponding rdf's and 
property graph's

## How to import 

Generated csv's from the ``community_infrastructure`` are in the ``property_graphs``-directory. To be able to display 
its graph, move the files to the follow path as to be able to see it in neo4j:

``C:\Users\tobig\.Neo4jDesktop2\Data\dbmss\<YOUR_DB>\import``

In the case of ``json_to_property_graph.py``, the following files get generated:
* ``communities.csv``
* ``community_subject.csv``
* ``subjects.csv``

## Cypher commands

```
LOAD CSV WITH HEADERS FROM "file:///communities.csv" AS row
CREATE (:Community {
  id: row.`communityId:ID`,
  acronym: row.acronym,
  name: row.name,
  description: row.description,
  type: row.type
});
```

```
LOAD CSV WITH HEADERS FROM "file:///subjects.csv" AS row
CREATE (:Subject { name: row.`subjectName:ID` });
```

```
LOAD CSV WITH HEADERS FROM "file:///community_subject.csv" AS row
MATCH (c:Community { id: row.`:START_ID` })
MATCH (s:Subject { name: row.`:END_ID` })
CREATE (c)-[:HAS_SUBJECT]->(s);
```