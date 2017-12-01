
# Wrangle OpenStreetMap Data

### Map Area

Madrid, España, Europe:

- [https://mapzen.com/data/metro-extracts/your-extracts/2ea35c3cfbbe](https://mapzen.com/data/metro-extracts/your-extracts/2ea35c3cfbbe)

Madrid is my hometown and I wanted to make my little homenage obviously my origins. On the other hand I am interested on knowing which people provide this kind of information and how accurated is.

## Problems Encountered in the Map

After making a little investigation with a sample of my hometown Madrid, in a largest file the following problems were found:

- __Nodes rows without user:__ For the main dataset some nodes did not include user and uid attrib
- __Wrong Postal Codes:__ For Madrid all postal code must begin by *"28"* followed by 3 more digits.
- __Values for key "tipo_via":__ Some values did not belong to the admitted values.

Getting deeper, next you can find more detail:

### __Nodes rows without user:__ We have detected nodes without a uid and user assigned:
```python
<node id="26514540" lat="40.4017858" lon="-3.704827" version="1" timestamp="2007-03-13T15:50:20Z" changeset="235530">
<node id="26528737" lat="40.4008137" lon="-3.7022965" version="1" timestamp="2007-03-14T12:08:19Z" changeset="236222">
```
However, the user appears later in the file:
```python
<way id="4353138" version="2" timestamp="2010-03-01T12:50:48Z" changeset="4008305" uid="220932" user="mor">
	<nd ref="26514542"/>
	<nd ref="26514545"/>
	<nd ref="26514546"/>
	<nd ref="26514540"/>
<way id="4354846" version="7" timestamp="2017-10-19T09:59:22Z" changeset="53063848" uid="3638158" user="mdtrooper">
	<nd ref="26528737"/>
```

### __Wrong Postal Codes:__ In all Madrid´s area (even in the peripherical villages) all the postal codes must begin with *"28"* and must be a 5 digit field:
```python
	<tag k="addr:postcode" v="29039"/>
    <tag k="addr:postcode" v="E28016"/>
    <tag k="addr:postcode" v="3"/>
    <tag k="addr:postcode" v="2839"/>
    <tag k="addr:postcode" v="Madrid"/>
```
A function has been created depending on a regular expression:
```python
POSTCODE_PATTERN = re.compile(r'^(E)?(28[0-9]{3})')
```
which will keep value field if it keeps requirements, otherwise it will use default value *"28000"*:
```python
def treat_postcode(string_in):
    string_out = "28000"
    m = POSTCODE_PATTERN.search(string_in)
    if m:
         return m.group(2)
    return string_out
```
### __Values for key "tipo_via":__ There are some cases where the value for a key *"tipo_via"* does not belong to *tipo_via_set*:
```python
    tipo_via_set = ['Avenida', 'Calle', 'Camino', 'Paseo', 'Plaza', 'Carrera', 'Ronda', 'Carretera', 'Pasaje']
    <node id="266170054" lat="40.4193384" lon="-3.7080248" version="4" timestamp="2015-05-12T17:21:14Z" changeset="31059668" uid="718437" user="carlosz22">
		<tag k="name" v="Centro Europeo de Estudios Profesionales II"/>
		<tag k="amenity" v="school"/>
		<tag k="source:url" v="http://educa.madrid.org"/>
		<tag k="educamadrid:tipo" v="Centro Privado de Formación Profesional Específica"/>
		<tag k="educamadrid:comedor" v="no"/>
		<tag k="educamadrid:bilingue" v="no"/>
		<tag k="educamadrid:distrito" v="Centro"/>
		<tag k="educamadrid:telefono" v="915473023 , 915473023"/>
		<tag k="educamadrid:tipo_via" v="Costanilla"/>
        
    <node id="266171143" lat="40.3938707" lon="-3.664914" version="3" timestamp="2015-01-20T03:13:11Z" changeset="28267697" uid="220932" user="mor">
		<tag k="name" v="El Desván"/>
		<tag k="amenity" v="kindergarten"/>
		<tag k="source:url" v="http://educa.madrid.org"/>
		<tag k="educamadrid:tipo" v="Centro Privado de Educación Infantil"/>
		<tag k="educamadrid:comedor" v="no"/>
		<tag k="educamadrid:bilingue" v="no"/>
		<tag k="educamadrid:distrito" v="Puente de Vallecas"/>
		<tag k="educamadrid:telefono" v=","/>
		<tag k="educamadrid:tipo_via" v="Colonia"/>
```
For these cases we will treat the value for tipo via equals to *"wrong value [{value}]"*
```python
    def treat_tipo_via(string_in):
        string_out = string_in
        if not string_out in tipo_via_set:
            string_out = split_by_char(string_out," ",1, 1, tipo_via_set)
            string_out = string_out.upper()[:1] + string_out.lower()[1:]
            if not string_out in tipo_via_set:
                return "wrong value [{}]".format(string_in)
        return string_out
```

## Data Overview

This section contains basic statistics about the dataset, the sqlite queries used to gather them, and some additional ideas about the data in context.

- __First of all take a look files employed for this study:__

```
m2.osm .................................................... 137.325 KB
nodes.csv .................................................. 46.613 KB
nodes_tags.csv .............................................. 8.260 KB
ways.csv .................................................... 5.866 KB
ways_nodes.csv ............................................. 19.921 KB
ways_tags.csv ............................................... 7.877 KB
project.db ................................................. 79.403 KB
```
- __Number of nodes:__
```sql
sqlite> SELECT COUNT(*) FROM nodes
```
```sql
566914
```
- __Number of ways:__
```sql
sqlite> SELECT COUNT(*) FROM ways
```
```sql
96419
```
- __Number of unique users:__
```sql 
sqlite> SELECT COUNT(DISTINCT(user)) AS "USERS" FROM (
SELECT user FROM nodes UNION ALL
SELECT user FROM ways) T
```
```sql
1252
```
- __TOP 10 contributing users:__
``` sql
sqlite> SELECT T.user, count(*) FROM (
SELECT user FROM nodes UNION ALL
SELECT user FROM ways) T
GROUP BY 1
ORDER BY 2 DESC
LIMIT 10
```
```sql
cirdancarpintero	127394
Iván_	71084
mor	67858
carlosz22	66553
Canellone	54490
polkillas	26676
Luiyo	25796
jorvime	20532
Cuenqui	18859
xavi5	11712
```

- __Number of one contribution user:__
```sql
sqlite>SELECT COUNT(*)
FROM(
SELECT T.user, count(*)
FROM
(SELECT user
FROM nodes
UNION ALL
SELECT user
FROM ways
) T
GROUP BY 1
HAVING COUNT(*) = 1
) T2
```
```sql
451
```

## More Data Overview

Lets get deeper on our infomation:

- __TOP 10 APPEARING AMENITY *(of course "bar" is in top 3)*:__
```sql
sqlite>SELECT T.VALUE, COUNT(*)FROM (
SELECT value FROM nodes_tags
WHERE UPPER(key) = 'AMENITY'UNION ALL 
SELECT value FROM ways_tags
WHERE UPPER(key) = 'AMENITY'
) T
GROUP BY 1
ORDER BY 2 DESC
LIMIT 10
```
Due to Madrid is considered a tourist destiny, it offers a lot of restaurant, bars and so on ..
```sql
restaurant	2425
pharmacy	1084
bar	918
bank	787
parking	623
drinking_water	610
bicycle_parking	542
bench	537
cafe	524
school	512
```
- __BIGGEST Religion__
```sql
sqlite>SELECT T1.value, count(distinct(T1.id))
FROM nodes_tags T1, nodes_tags T2
WHERE T1.id = T2.id
AND T2.value = 'place_of_worship'
AND T1.key = 'religion'
GROUP BY 1
ORDER BY 2 DESC
```
It is clear that mostly all spanish population belongs to christian´s religion.
```sql
christian	106
muslim	4
bahai	1
sikh	1
videncia,_tarot_y_magia	1
```

- __MOST Popular cuisines__
```sql
SELECT nodes_tags.value, COUNT(*) as num
FROM nodes_tags JOIN (SELECT DISTINCT(id) FROM nodes_tags WHERE value='restaurant') i
ON nodes_tags.id=i.id WHERE nodes_tags.key='cuisine'
GROUP BY nodes_tags.value
ORDER BY num DESC
LIMIT 10
```
Althought Madrid is more than 6M people living in, most of them come from other regions which makes to have a great quantity of restaurant with regional food.
```sql
regional	478
spanish	77
chinese	76
italian	76
japanese	67
burger	55
mexican	51
asian	43
pizza	37
indian	30
```

## Additional Ideas and Conclusions 

Once this review has been done it’s obvious that Madrid´s area is incomplete, though I believe it has been well cleaned for the purposes of this exercise. Comparing with other maps, it surprises me how a little quantity of user with pattern "*bot*" appear in the list. It means, or maybe thats what I want to think, people make a great effort to update and complete these sources. I think more robust data would need to be provided due to the lack of information I appreciate: number of parks, churches and museums. 

In the first review of this project, the reviewer suggested to encorage users by the use of a popular game like Pokemon GO, something awesome in my opinion, due to the *"Pokemon addiction"* right now is happening in this city. The problems because of this option is to get a collaboration between Pokemon Enterprise and Madrid Council and how to integrate both ideas -- and of course the costs involved.

Other proposal would be trying comercial shops owners try to collaborate, in return they will get a discount in the local bills and a better marketing publicity for their shops.
