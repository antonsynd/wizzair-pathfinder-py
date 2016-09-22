#!/usr/bin/env python3
"""
2016-09-21
antonsynd
"""

# ======================================
#  Imports
# ======================================

from pyquery import PyQuery as pq
import argparse
import requests

# ======================================
#  Definitions
# ======================================

sc_list = 'list'
sc_info = 'info'
sc_find_route = 'find-route'
wizzair_url = 'https://cdn.static.wizzair.com/en-GB/Map.ashx'


def list_destinations(ds) -> None:
    cities = ds('list > city')

    for ccity in cities:
        cname = ds(ds('name', ccity)[0]).text()
        ciata = ds(ds('iata', ccity)[0]).text()

        print('%s (%s)' % (cname, ciata), flush=True)


def _find_path(map: dict, x, y, path: list, visited: set) -> list:
    if x in map and y in map:
        # At current point x, check if any of its children
        # are in visited, if at least one is not, then
        # go on and push paths for that
        ccity = map[x]

        unvisited = [z for z in ccity['connected'] if z not in visited]

        if len(unvisited) > 0:
            if y in ccity['connected']:
                path.append(x)
                path.append(y)
                return path
            else:
                # No connection, add to visited, add to the current path
                visited.add(x)
                path.append(x)

                valid_paths = []

                for i in unvisited:
                    res = _find_path(map, i, y, path.copy(), visited)

                    if res:
                        valid_paths.append(res)

                if len(valid_paths) == 0:
                    return None
                else:
                    valid_paths.sort(key=lambda z: len(z))

                    return valid_paths[0]
        else:
            # Everything has been visited already, dead-end
            visited.add(x)
            return None
    else:
        # Either start or destination is not being served
        return None


def _build_map(ds) -> tuple:
    # <city>
    #   <name />
    #   <iata />
    #   <connected>
    #       <city>
    #           <iata />
    #       </city>
    #   </connected>
    # </city>
    cities = ds('list > city')
    city_map = dict()

    for ccity in cities:
        cname = ds(ds('name', ccity)[0]).text()
        ciata = ds(ds('iata', ccity)[0]).text()

        cconnected = dict()

        cobj = {
            'iata': ciata,
            'name': cname,
            'connected': cconnected
        }

        connected_cities = ds('connected city iata', ccity)

        for cconnected_city in connected_cities:
            cconnected[ds(cconnected_city).text()] = None

        city_map[ciata] = cobj

    unserved = []

    # Now update each city's map
    for ccity in city_map.values():
        cconnected = ccity['connected']

        for ciata in cconnected:
            if ciata in city_map:
                cconnected[ciata] = city_map[ciata]
            else:
                unserved.append(ciata)

    return city_map, unserved


def find_route(ds, start, end):
    city_map, unserved = _build_map(ds)

    print('The following airports are not being served by Wizz Air at this time: %s' % ', '.join(unserved), flush=True)

    path = _find_path(city_map, start, end, [], set())

    path = ['%s (%s)' % (city_map[i]['name'], i) for i in path]

    print(' -> '.join(path), flush=True)


def print_info(ds, code):
    city_map, _ = _build_map(ds)

    if code in city_map:
        city = city_map[code]

        print('%s (%s)' % (city['name'], code), flush=True)
        print(' -> ' + '; '.join(['%s (%s)' % (ccity['name'], ciata) for ciata, ccity in city['connected'].items() if ccity is not None]))
    else:
        print('\'%s\' is either an invalid or unserved Wizz Air destination' % code)

# ======================================
#  Main
# ======================================

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
            description='Determines the shortest path between current Wizz Air destinations')
    subparser = parser.add_subparsers(dest='subcommand')

    list_parser = subparser.add_parser(sc_list, help='List all available destinations')

    info_parser = subparser.add_parser(sc_info, help='List information about a particular airport')
    info_parser.add_argument('code', help='The IATA code of the airport')

    find_route_parser = subparser.add_parser(sc_find_route, help='Find a route between two airports')
    find_route_parser.add_argument('start', help='The starting point')
    find_route_parser.add_argument('end', help='The end destination')

    args = parser.parse_args()

    response = requests.get(wizzair_url)
    ds = pq(response.content)

    if args.subcommand == sc_list:
        list_destinations(ds)
    elif args.subcommand == sc_find_route:
        find_route(ds, args.start.strip(), args.end.strip())
    elif args.subcommand == sc_info:
        print_info(ds, args.code.strip())
