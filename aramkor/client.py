import sys
import json
import copy

try:
    #json átalakítása python objectté
    with open(sys.argv[1], 'r') as file:
        data = json.load(file)
        #adatok kinyerése
        end_points = data["end-points"]
        switches = data["switches"]
        links = data["links"]
        possible_circuits = data["possible-circuits"]
        duration = data["simulation"]["duration"]
        demands = data["simulation"]["demands"]
    
    #élek jelenlegi kapacitásának eltárolása (kezdetben mindnek nulla)
    for link in links:
        link["current"] = 0.0

    for i in range(len(possible_circuits)):
        possible_circuits[i] = [possible_circuits[i], "free", -1]

    #print(possible_circuits)

    #összes allokáció/deallokáció kimentése időrendi sorrendben
    all_demands = []
    ID = 0
    #allokációk sorrendben történő beillesztése
    for demand in demands:
        index = 0
        for i in range(len(all_demands)):
            if all_demands[i]["time"] > demand["start-time"]:
                index = i
                break

        demand_start = copy.deepcopy(demand)
        del demand_start["end-time"]
        demand_start["time"] = demand_start["start-time"]
        del demand_start["start-time"]
        demand_start["type"] = "start"
        demand_start["ID"] = ID
        if index > 0:
            all_demands.insert(index, demand_start)
        else:
            all_demands.append(demand_start)
        ID += 1
    #deallokációk sorrendben történő beillesztése
    ID = 0
    for demand in demands:
        index = 0
        for i in range(len(all_demands)):
            if all_demands[i]["time"] > demand["end-time"]:
                index = i
                break

        demand_end = copy.deepcopy(demand)
        del demand_end["start-time"]
        demand_end["time"] = demand_end["end-time"]
        del demand_end["end-time"]
        demand_end["type"] = "end"
        demand_end["ID"] = ID
        if index > 0:
            all_demands.insert(index, demand_end)
        else:
            all_demands.append(demand_end)
        ID += 1

    #for demand in all_demands:
    #    print(demand)

    event_number = 1
    #allokálás/deallokálás
    for demand in all_demands:
        if demand["type"] == "start": #allokálás
            #mindkét pont bennevan-e az adatbázisban?
            if demand["end-points"][0] not in end_points or demand["end-points"][1] not in end_points:
                print(str(event_number) + ". igény foglalás: " + demand["end-points"][0] + "<->" + demand["end-points"][1] + " st:" + str(demand["time"]) + " - sikertelen")
            else:
                #kigyűjtjük az összes lehetséges és még nem lefoglalt utat
                all_possible_paths = []
                circuits_indices = []
                temp_index = 0
                for circuit in possible_circuits:
                    if (circuit[0][0] == demand["end-points"][0]) and (circuit[0][len(circuit[0])-1] == demand["end-points"][1]) and circuit[1] == "free":
                        all_possible_paths.append(circuit)
                        circuits_indices.append(temp_index)
                    temp_index += 1
                #kigyűjtött utak vizsgálata, le lehet-e egyáltalán egyet foglalni
                if len(all_possible_paths) == 0: #ha nincs is a két végpont között elérhető út
                    print(str(event_number) + ". igény foglalás: " + demand["end-points"][0] + "<->" + demand["end-points"][1] + " st:" + str(demand["time"]) + " - sikertelen")
                else: #ha van
                    temp_index = 0
                    for path in all_possible_paths:
                        correct_path = True
                        links_to_occupy = []
                        for i in range(len(path[0])-1):
                            correct_link = False
                            for link in links:
                                if ([path[0][i], path[0][i+1]] == link["points"] or [path[0][i], path[0][i+1]] == link["points"][::-1]) and link["current"] + demand["demand"] <= link["capacity"]:
                                    correct_link = True
                                    links_to_occupy.append(link)
                                    break
                            if correct_link is False:
                                correct_path = False
                                break
                        if correct_path is True:
                            all_possible_paths[temp_index][1] = "occupied"
                            all_possible_paths[temp_index][2] = demand["ID"]
                            for link in links_to_occupy:
                                link["current"] += demand["demand"]
                            print(str(event_number) + ". igény foglalás: " + demand["end-points"][0] + "<->" + demand["end-points"][1] + " st:" + str(demand["time"]) + " - sikeres")
                            break
                        temp_index += 1 
                    if correct_path is False:
                        print(str(event_number) + ". igény foglalás: " + demand["end-points"][0] + "<->" + demand["end-points"][1] + " st:" + str(demand["time"]) + " - sikertelen") 
        else: #deallokálás
            for circuit in possible_circuits:
                if circuit[2] == demand["ID"]:
                    circuit[2] = -1
                    circuit[1] = "free"
                    for i in range(len(circuit[0])-1):
                        for link in links:
                            if [circuit[0][i], circuit[0][i+1]] == link["points"] or [circuit[0][i], circuit[0][i+1]] == link["points"][::-1]:
                                link["current"] -= demand["demand"]
                    print(str(event_number) + ". igény felszabadítás: " + demand["end-points"][0] + "<->" + demand["end-points"][1] + " st:" + str(demand["time"]))
                    break

        event_number += 1

except IndexError:
    print("Hiba: Nem lett fájlnév megadva!")
    sys.exit()
except FileNotFoundError:
    print("Hiba: A megadott fájl nem található!")
    sys.exit()
