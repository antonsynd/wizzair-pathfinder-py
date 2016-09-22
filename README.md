# wizzair-pathfinder-py
Determines the shortest path between current Wizz Air destinations

```
usage: wizzair-pathfinder.py [-h] {list,info,find-route} ...

Determines the shortest path between current Wizz Air destinations

positional arguments:
  {list,info,find-route}
    list                List all available destinations
    info                List information about a particular airport
    find-route          Find a route between two airports

optional arguments:
  -h, --help            show this help message and exit
```

## Examples
```
python wizzair-pathfinder.py info VAR
Varna (VAR)
 -> Sofia (SOF); London Luton (LTN)
```

```
python wizzair-pathfinder.py find-route VAR WRO
The following airports are not being served by Wizz Air at this time: FAO, SUF, VXO, SUJ, LGW
Varna (VAR) -> London Luton (LTN) -> Wroclaw (WRO)
```
