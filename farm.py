#Written by Hoshroin, 2023

import os, time, random
import threading
import json

language_data = {}

def langJsonLoad():
    j_in_r = ""
    with open("./lang.json", "r", encoding="UTF-8") as _jf:
        _jf.seek(0)
        j_in_r = _jf.read()
    return json.loads(j_in_r)

language_data = langJsonLoad()

land_size = [10, 10]
land_data = []
crop_data = {}

random_seed = round(time.time())
random.seed(random_seed)

# land_data:
## 0 is normal, 1 is lootable_0, 2 is lootable_1, 3 is crop
## normal can be plantable, lootable_* can generate varient seeds for the first contact
## lootable_0 has seeds on it, lootable_1 is empty
## crop's id is its position, example: position (2, 19) for '0219'

# crop_data:
## 'id': [type, statu, growth]
## type: item_id
## statu: normal (0), or debuff[WIP]
## growth: 0.01 - 1, a progress bar value

# crop_property
## item_id: [wait_time]

for x in range(land_size[0]):
    land_data.append([])
    for y in range(land_size[1]):
        land_data[x].append(0)
for x in range(land_size[0]):
    for y in range(land_size[1]):
        rander = random.randint(0, 5)
        if rander == 3:
            land_data[x][y] = 1

item_id_table = ['wheat', 'potato', 'corn', 'grass']
crop_property = {0: [10], 1: [16], 2: [20], 3: [5]}

ply_pos = [0, 0]
ply_inv = {'wheat': 1, 'potato': 0, 'corn': 0, 'grass': 0}

gameticker_indata = [0]
def readGameData():
    _gd = {}
    _gd_str = ""
    with open("./save.dat", 'r') as _gd_f:
        _gd_f.seek(0)
        _gd_str = _gd_f.read()
    _gd = json.loads(_gd_str)
    global land_size, land_data, crop_data, random_seed, ply_pos, ply_inv, gameticker_indata
    land_size = _gd['land_size']
    land_data = _gd['land_data']
    crop_data = _gd['crop_data']
    random_seed = _gd['random_seed']
    random.seed(random_seed)
    ply_pos = _gd['ply_pos']
    ply_inv = _gd['ply_inv']
    gameticker_indata = [_gd['loot_refresh_timer']]
    print(language_data['info_save_file_loaded'])

if os.path.exists("./save.dat"):
    readGameData()

gameticker_lock = 1
gameticker_callback = []
def gameTicker(_callback, _in_data):
    loot_refresh_timer = _in_data[0]
    while 1:
        if loot_refresh_timer != 300:
            loot_refresh_timer += 1
        else:
            for x in range(land_size[0]):
                for y in range(land_size[1]):
                    if land_data[x][y] == 2:
                        land_data[x][y] = 1

            loot_refresh_timer = 0

        for _c_k in crop_data.keys():
            _c = crop_data[_c_k]
            if _c[2] < 1 and _c[1] == 0:
                crop_data[_c_k][2] += 1 / crop_property[_c[0]][0]
                crop_data[_c_k][2] = round(crop_data[_c_k][2], 6)

        if gameticker_lock == 0:
            break

        time.sleep(1)

    _callback([loot_refresh_timer])

def gameTicker_break(_out_data):
    global gameticker_callback
    gameticker_callback = _out_data

thread_gameticker = threading.Thread(target=gameTicker, args=(gameTicker_break, gameticker_indata,))
thread_gameticker.start()

def playerStoreSeed(_seed_id, _adder):
    seed_name = item_id_table[_seed_id]
    if _seed_id >= 0 and _seed_id < len(item_id_table):
        ply_inv[seed_name] = ply_inv[seed_name] + _adder
    else:
        print("ERROR: playerStoreSeed(): invalid seed_id")
        quit()

def getCropID(_x, _y):
    f_xlength = len(str(land_size[0]))
    f_ylength = len(str(land_size[1]))
    fout_x = str(_x)
    if len(str(_x)) < f_xlength:
        f_xos = f_xlength - len(str(_x))
        for _i in range(f_xos):
            fout_x = "0" + fout_x
    fout_y = str(_y)
    if len(str(_y)) < f_ylength:
        f_yos = f_ylength - len(str(_y))
        for _i in range(f_yos):
            fout_y = "0" + fout_y
    return fout_x + fout_y

def getTargetIDType(_id):
    fout = "null"
    for _i in crop_property.keys():
        if _id == _i:
            fout = "crop"
            break

    return fout

def saveGameExit():
    global gameticker_lock
    gameticker_lock = 0
    thread_gameticker.join()
    save_data = {'land_size': land_size, 'land_data': land_data, 'crop_data': crop_data, 'ply_pos': ply_pos, 'ply_inv': ply_inv, 'loot_refresh_timer': gameticker_callback[0], 'random_seed': random_seed}
    j_gs_o = json.dumps(save_data)
    with open("./save.dat", 'w+') as _jf:
        _jf.write(j_gs_o)
    quit()

while 1:
    print(language_data["info_current_player_position"] + "%d, %d" % (ply_pos[0], ply_pos[1]))
    cmd = input("> ")
    if cmd == "up":
        if ply_pos[1] > 0:
            ply_pos[1] = ply_pos[1] - 1
        else:
            print(language_data["error_cannot_move_further"])
    elif cmd == "down":
        if ply_pos[1] < land_size[1]:
            ply_pos[1] = ply_pos[1] + 1
        else:
            print(language_data["error_cannot_move_further"])
    elif cmd == "left":
        if ply_pos[0] > 0:
            ply_pos[0] = ply_pos[0] - 1
        else:
            print(language_data["error_cannot_move_further"])
    elif cmd == "right":
        if ply_pos[0] < land_size[0]:
            ply_pos[0] = ply_pos[0] + 1
        else:
            print(language_data["error_cannot_move_further"])

    elif cmd == "check":
        cur_land = land_data[ply_pos[0]][ply_pos[1]]
        if cur_land < 3:
            print(language_data["info_check_current_land_" + str(cur_land)])
        else:
            cur_crop = crop_data[getCropID(ply_pos[0], ply_pos[1])]
            print(language_data["info_check_current_crop"] % (language_data["name_" + item_id_table[cur_crop[0]]]))
            remain_time = round((1 - cur_crop[2]) / (1 / crop_property[cur_crop[0]][0]))
            print(language_data["info_check_current_crop_detail"] % (language_data["name_" + item_id_table[cur_crop[0]]], language_data["name_crop_statu_" + str(cur_crop[1])], str(remain_time)))
    elif cmd == "pick":
        cur_land = land_data[ply_pos[0]][ply_pos[1]]
        if cur_land == 1:
            land_data[ply_pos[0]][ply_pos[1]] = 2
            rand_seed_id = random.randint(0, 3)
            rand_quantity = random.randint(1, 4)
            playerStoreSeed(rand_seed_id, rand_quantity)
            print(language_data["info_pickup_lootable"] % (language_data["name_" + item_id_table[rand_seed_id]] + "*" + str(rand_quantity)))
        elif cur_land == 3:
            cur_crop = crop_data[getCropID(ply_pos[0], ply_pos[1])]
            if cur_crop[1] == 0 and int(cur_crop[2]) >= 1:
                playerStoreSeed(cur_crop[0], 2)
                print(language_data["info_pickup_crop"] % (language_data["name_" + item_id_table[cur_crop[0]]] + "*2"))
                land_data[ply_pos[0]][ply_pos[1]] = 0
                crop_data.pop(getCropID(ply_pos[0], ply_pos[1]))
            else:
                remain_time = round((1 - cur_crop[2]) / (1 / crop_property[cur_crop[0]][0]))
                print(language_data["error_pickup_crop_too_early"] % remain_time)
        else:
            print(language_data["error_nothing_to_pick_" + str(cur_land)])

    elif cmd == "quit":
        saveGameExit()

    elif len(cmd.split(" ")) > 1:
        scmd = cmd.split(" ")[0]
        if scmd == "plant":
            cur_land = land_data[ply_pos[0]][ply_pos[1]]
            target_cropid = 0
            try:
                target_cropid = int(cmd.split(" ")[1])
            except ValueError:
                print(language_data["error_invalid_input_01"])
                continue
            if target_cropid < 0 or target_cropid >= len(item_id_table):
                print(language_data["error_invalid_input_01"])
                continue
            elif getTargetIDType(target_cropid) != "crop":
                print(language_data["error_invalid_input_01"])
                continue
            else:
                if cur_land != 0:
                    print(language_data["error_cannot_plant_here"])
                else:
                    if ply_inv[item_id_table[target_cropid]] < 1:
                        print(language_data["error_not_enough_item"] % (language_data["name_" + item_id_table[target_cropid]] + "*1"))
                    else:
                        ply_inv[item_id_table[target_cropid]] -= 1
                        land_data[ply_pos[0]][ply_pos[1]] = 3
                        crop_data.update({getCropID(ply_pos[0], ply_pos[1]): [target_cropid, 0, 0]})
                        print(language_data["info_plant_success"] % (language_data["name_" + item_id_table[target_cropid]], str(crop_property[target_cropid][0])))

        elif scmd == "inv":
            if cmd.split(" ")[1] == "check":
                inv_output = ""
                for _i in ply_inv.keys():
                    inv_output += language_data["name_" + _i] + "*" + str(ply_inv[_i]) + ", "
                print(language_data["info_check_inventory"] + inv_output[:-2])
            elif cmd.split(" ")[1] == "discard":
                if len(cmd.split(" ")) != 4:
                    print(language_data["error_invalid_input_02"])
                else:
                    target_id = 0
                    target_amount = 0
                    try:
                        target_id = int(cmd.split(" ")[2])
                        target_amount = int(cmd.split(" ")[3])
                    except:
                        print(language_data["error_invalid_input_02"])
                        continue
                    if target_id < 0 or target_id >= len(item_id_table):
                        print(language_data["error_invalid_input_01"])
                        continue
                    if target_amount <= 0:
                        print(language_data["error_invalid_input_02"])
                        continue
                    if target_amount > ply_inv[item_id_table[target_id]]:
                        print(language_data["error_not_enough_item"] % (language_data["name_" + item_id_table[target_id]] + "*" + str(target_amount)))
                    else:
                        ply_inv[item_id_table[target_id]] -= target_amount
                        print(language_data["info_discard_item_success"] % (language_data["name_" + item_id_table[target_id]] + "*" + str(target_amount)))

        elif scmd == "goto":
            if len(cmd.split(" ")) != 3:
                print(language_data["error_invalid_input_02"])
            else:
                target_pos_x = 0
                target_pos_y = 0
                try:
                    target_pos_x = int(cmd.split(" ")[1])
                    target_pos_y = int(cmd.split(" ")[2])
                except:
                    print(language_data["error_invalid_input_02"])
                    continue
                if target_pos_x >= land_size[0] or target_pos_x < 0 or target_pos_y >= land_size[1] or target_pos_y < 0:
                    print(language_data["error_cannot_goto_position"])
                    continue
                else:
                    ply_pos[0] = target_pos_x
                    ply_pos[1] = target_pos_y

        else:
            print(language_data["error_unknown_command"])
    else:
        print(language_data["error_unknown_command"])
