# CCC-Project

## ElasticSearch

### Accessing the ElasticSearch API and the Kibana User Interface

- Prequisite:
  - Before accessing Kubernetes services, an SSH tunnel to the bastion node has to be opened in a different shell and kept open. In addition, the `openrc` file has to be source and the kubeconfig file put under the `~/.kube` directory (see the READM in the `installation` folder for more details).

To access services on the cluster, one has to use the `port-forward` command of `kubectl` in a new terminal window.

```
kubectl port-forward service/elasticsearch-master -n elastic 9200:9200
```

To access the Kibana user interface, one has to use the `port-forward` command of `kubectl` (another terminal window):

```
kubectl port-forward service/kibana-kibana -n elastic 5601:5601
```

Test the ElasticSearch API:

```
curl -k 'https://127.0.0.1:9200/_cluster/health' --user 'elastic:elastic' | jq '.'
```

Test the Kibana user interface by pointing the browser to: `http://127.0.0.1:5601/` (the default credentials are `elastic:elastic`).

### Operations

#### Search

```bash
curl -XGET -k "https://127.0.0.1:9200/weather/_search"\
  --header 'Content-Type: application/json'\
  --data '{
    "query": {
        "range": {
			"Date": {
			"gte": "20240301",
			"lte": "20240303",
			"format": "yyyyMMdd"
			}
		}
	}
	}'\
  --user 'elastic:elastic' | jq '.'
```

```bash
curl -XGET -k "https://127.0.0.1:9200/weather/_search"\
  --header 'Content-Type: application/json'\
  --data '{
    "query": {
        "match_all": {

		}
	}
	}'\
  --user 'elastic:elastic' | jq '.'
```

```bash
curl -XGET -k "https://127.0.0.1:9200/weather/_search" \
  --header 'Content-Type: application/json' \
  --user 'elastic:elastic' \
  --data '{
    "query": {
        "bool": {
            "must_not": [
                {
                    "exists": {
                        "field": "Date"
                    }
                }
            ]
        }
    }
  }' | jq '.'

```

#### Create Index

```
curl -XPUT -k 'https://127.0.0.1:9200/weather' \

--header 'Content-Type: application/json' \

--data '{

"settings": {

"index": {

"number_of_shards": 3,

"number_of_replicas": 1

}

},

"mappings": {

"properties": {

"Date": {"type": "date", "format": "yyyy-MM-d"},

"Minimum temperature (°C)": {"type": "float"},

"Maximum temperature (°C)": {"type": "float"},

"Rainfall (mm)": {"type": "float"},

"Evaporation (mm)": {"type": "float"},

"Sunshine (hours)": {"type": "float"},

"Speed of maximum wind gust (km/h)": {"type": "float"},

"Time of maximum wind gust": {"type": "text"},

"9am Temperature (°C)": {"type": "float"},

"9am relative humidity (%)": {"type": "integer"},

"9am cloud amount (oktas)": {"type": "integer"},

"9am wind speed (km/h)": {"type": "integer"},

"9am MSL pressure (hPa)": {"type": "float"},

"3pm Temperature (°C)": {"type": "float"},

"3pm relative humidity (%)": {"type": "integer"},

"3pm cloud amount (oktas)": {"type": "integer"},

"3pm wind speed (km/h)": {"type": "integer"},

"3pm MSL pressure (hPa)": {"type": "float"}

}

}

}' \

--user 'elastic:elastic' | jq '.'
```

#### Delete Index

```
curl -XDELETE -k 'https://127.0.0.1:9200/weather' --user 'elastic:elastic' | jq '.'
```

## Fission

### Function

```
fission function create --name weather --env python --code /Users/clarec/Documents/GitHub/CCC_group63_frontend/functions/weather.py

fission function create --name weathertest --env python --code /Users/clarec/Documents/GitHub/CCC_group63_frontend/weathertest.py


fission function update --name weather --code /Users/clarec/Documents/GitHub/CCC_group63_frontend/functions/weather.py

fission fn update --name weather --env python --mincpu 100 --maxcpu 500 --minmemory 100 --maxmemory 500

fission function test --name weather | jq '.'
fission function test --name weathertest | jq '.'

```

### Route

```
fission route create --url /weather --function weather --name weather --createingress

curl "http://127.0.0.1:9090/weather" | jq '.'
```

### Pkg

```
cd functions/addobservations
zip -r addobservations.zip .
mv addobservations.zip ../

cd ../..

fission package create --sourcearchive ./functions/addobservations.zip\
  --env python\
  --name addobservations\
  --buildcmd './build.sh'

fission fn create --name addobservations\
  --pkg addobservations\
  --env python\
  --entrypoint "addobservations.main"

fission route create --url /addobservations --function addobservations --name addobservations --createingress


curl "http://127.0.0.1:9090/addobservations" | jq '.'
```

### Creation of a RestFUL API with YAML specifications

A ReSTful API may look like:

```
/temperature/{date}
```

#### Route creation

We start by using the fission commands to create the YAML files defining the routes/HTTPTriggers:

```
fission route create --name avgtempday --function avgtemp \
    --method GET \
    --url '/temperature/days/{date:[0-9][0-9][0-9][0-9]-[0-1][0-9]-[0-3][0-9]}'

fission route create --name searchweatherdate --method GET --url "/searchweather/dates/{start_date}/{end_date}" --function searchweather


```

### 删除三件套

```
fission function delete --name weather
fission route delete --name weather
fission pkg list
fission pkg delete --name

fission function delete --name addobservations
fission route delete --name addobservations
fission pkg delete --name addobservations
```

#### getweather

- Create

```
cd functions/getweather
zip -r getweather.zip .
mv getweather.zip ../

cd ../..

fission package create --sourcearchive ./functions/getweather.zip\
  --env python\
  --name getweather\
  --buildcmd './build.sh'

fission fn create --name getweather\
  --pkg getweather\
  --env python\
  --entrypoint "getweather.main"

fission route create --url /getweather --function getweather --name getweather --createingress


curl "http://127.0.0.1:9090/getweather" | jq '.'
```

- Delete

```
fission function delete --name getweather
fission route delete --name getweather
fission pkg delete --name getweather
```

#### searchweather

- Create

```bash
cd functions/searchweather
zip -r searchweather.zip .
mv searchweather.zip ../

cd ../..

fission package create --sourcearchive ./functions/searchweather.zip\
  --env python\
  --name searchweather\
  --buildcmd './build.sh'

fission fn create --name searchweather\
  --pkg searchweather\
  --env python\
  --entrypoint "searchweather.main"

fission httptrigger create --method GET \
    --url "/searchweather/{StartDate}/{EndDate}" --function searchweather --name searchweatherdates

curl "http://127.0.0.1:9090/searchweather/2024-03-01/2024-03-11" | jq '.'

```

fission route create --url /searchweather --function searchweather --name searchweather --createingress

curl "http://127.0.0.1:9090/searchweather" | jq '.'

fission route create --name searchweatherdate --method GET --url "/searchweather/{start_date}/{end_date}" --function searchweather

- Delete

```
fission function delete --name searchweather
fission pkg delete --name searchweather
fission route delete --name searchweatherdates
```

fission route delete --name searchweather

#### getaccidents

- Create

```bash
cd functions/getaccidents
zip -r getaccidents.zip .
mv getaccidents.zip ../

cd ../..

fission package create --sourcearchive ./functions/getaccidents.zip\
  --env python\
  --name getaccidents\
  --buildcmd './build.sh'

fission fn create --name getaccidents\
  --pkg getaccidents\
  --env python\
  --entrypoint "getaccidents.main"

fission route create --url /getaccidents --function getaccidents --name getaccidents --createingress

curl "http://127.0.0.1:9090/getaccidents" | jq '.'
```

- Delete

```bash
fission function delete --name getaccidents
fission route delete --name getaccidents
fission pkg delete --name getaccidents
```

#### extractdata

- Create

```
cd functions/extractdata
zip -r extractdata.zip .
mv extractdata.zip ../

cd ../..

fission package create --sourcearchive ./functions/extractdata.zip\
  --env python\
  --name extractdata\
  --buildcmd './build.sh'

fission fn create --name extractdata\
  --pkg extractdata\
  --env python\
  --entrypoint "extractdata.main"

fission route create --url /extractdata --function extractdata --name extractdata --createingress


curl "http://127.0.0.1:9090/extractdata" | jq '.'
```

- Delete

```
fission function delete --name extractdata
fission route delete --name extractdata
fission pkg delete --name extractdata
```

#### storeweather

```
cd functions/storeweather
zip -r storeweather.zip .
mv storeweather.zip ../

cd ../..

fission package create --sourcearchive ./functions/storeweather.zip\
  --env python\
  --name storeweather\
  --buildcmd './build.sh'

fission fn create --name storeweather\
  --pkg storeweather\
  --env python\
  --entrypoint "storeweather.main"

fission route create --url /storeweather --function storeweather --name storeweather --createingress


curl "http://127.0.0.1:9090/storeweather" | jq '.'
```

- Delete

```
fission function delete --name storeweather
fission route delete --name storeweather
fission pkg delete --name storeweather
```

#### combo

```
cd functions/combo
zip -r combo.zip .
mv combo.zip ../

cd ../..

fission package create --sourcearchive ./functions/combo.zip\
  --env python\
  --name combo\
  --buildcmd './build.sh'

fission fn create --name combo\
  --pkg combo\
  --env python\
  --entrypoint "combo.main"

fission route create --url /combo --function combo --name combo --createingress


curl "http://127.0.0.1:9090/combo" | jq '.'
```

- Delete

```
fission function delete --name combo
fission route delete --name combo
fission pkg delete --name combo
```
