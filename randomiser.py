from   tkinter import *
import platform
try:
    if platform.system() == "Windows":
        WINDOWS = True
        LINUX   = False
        
        from   pvz import *
        from   pvz.extra import *
        import atexit
        
        def dealloc_rngmem():
            try:
                VirtualFreeEx(pvz_handle, rng_addr, 0, 0x8000)
            except:
                print("Could not deallocate rng memory")
    else:
        LINUX   = True
        WINDOWS = False
        
        import ctypes
        import struct
        import time
        from os import listdir
        libc = ctypes.CDLL("libc.so.6",use_errno=True)
        
        from ctypes import c_int     as INT
        from ctypes import c_void_p  as VOIDP
        from ctypes import c_ulong   as ULONG
        from ctypes import c_ssize_t as SSIZE_T
        from ctypes import c_size_t  as SIZE_T
        from ctypes import c_uint    as UINT
        from ctypes import c_char_p  as CHARP
        
        pwrite          = libc.pwrite
        pwrite.argtypes = [INT,VOIDP,SIZE_T,VOIDP]
        pwrite.restype  = SSIZE_T
        
        pread          = libc.pread
        pread.argtypes = [INT,VOIDP,SIZE_T,VOIDP]
        pread.restype  = SSIZE_T
        
        c_open          = libc.open
        c_open.argtypes = [CHARP,INT,UINT]
        c_open.restype  = INT
        
        cpp_typename = {
            "char": "b",
            "signed char": "b",
            "int8_t": "b",
            "unsigned char": "B",
            "byte": "B",
            "uint8_t": "B",
            "bool": "?",
            "short": "h",
            "int16_t": "h",
            "unsigned short": "H",
            "uint16_t": "H",
            "int": "i",
            "int32_t": "i",
            "intptr_t": "i",
            "unsigned int": "I",
            "uint32_t": "I",
            "uintptr_t": "I",
            "size_t": "I",
            "long": "l",
            "unsigned long": "L",
            "long long": "q",
            "int64_t": "q",
            "intmax_t": "q",
            "unsigned long long": "Q",
            "uint64_t": "Q",
            "uintmax_t": "Q",
            "float": "f",
            "double": "d",
        }
        
        def openPVZ():
            procfiles = listdir("/proc/")
            processes = []
            for i in procfiles:
                if i.isdigit():
                    processes.append(i)
            
            pvz_proc = None
            for i in processes:
                with open("/proc/"+i+"/comm", "rb") as namefile:
                    name = namefile.read()
                if name == b"popcapgame1.exe\n":
                    pvz_proc = i
                elif name == b"PlantsVsZombies\n":
                    if not pvz_proc:
                        pvz_proc = i
            
            if not pvz_proc:
                raise ImportError("pvz not found!")
            
            print(pvz_proc)
            pvz_memfd = c_open(b'/proc/'+bytes(pvz_proc,'utf-8')+b'/mem',0x1B6,0)
            
            return pvz_memfd
        
        def ReadMemory(data_type, *address, array=1): #most of this is stolen from pvzscripts
            level      = len(address)
            offset     = VOIDP()
            buffer     = UINT()
            bytes_read = ULONG()

            for i in range(level):
                offset.value = buffer.value + address[i]

                if i != level - 1:
                    size = ctypes.sizeof(buffer)
                    bytes_read.value = pread(pvz_memfd,ctypes.byref(buffer),size,offset)
                    if bytes_read.value != size:
                        raise AttributeError("ReadMemory Error " + str(-ctypes.get_errno()))

                else:
                    fmt_str = "<" + str(array) + cpp_typename[data_type]
                    size = struct.calcsize(fmt_str)
                    buff = ctypes.create_string_buffer(size)
                    bytes_read.value = pread(pvz_memfd,ctypes.byref(buff),size,offset)
                    if bytes_read.value != size:
                        raise AttributeError("ReadMemory Error " + str(-ctypes.get_errno()))

                    result = struct.unpack(fmt_str, buff.raw)
            if array == 1:
                return result[0]
            else:
                return result
        
        def WriteMemory(data_type, values, *address): #most of this is stolen from pvzscripts too
            if not isinstance(values, (tuple, list)):
                values = [values]

            level         = len(address)
            offset        = VOIDP()
            buffer        = UINT()
            bytes_read    = ULONG()
            bytes_written = ULONG()

            for i in range(level):
                offset.value = buffer.value + address[i]

                if i != level - 1:
                    size = ctypes.sizeof(buffer)
                    bytes_read.value = pread(pvz_memfd,ctypes.byref(buffer),size,offset)
                    if bytes_read.value != size:
                        raise AttributeError("WriteMemory Error " + str(-ctypes.get_errno()))

                else:
                    array = len(values)
                    fmt_str = "<" + str(array) + cpp_typename[data_type]
                    size = struct.calcsize(fmt_str)
                    buff = ctypes.create_string_buffer(size)
                    buff.value = struct.pack(fmt_str, *values)
                    bytes_written.value = pwrite(pvz_memfd,ctypes.byref(buff),size,offset)
                    if bytes_written.value != size:
                        raise AttributeError("WriteMemory Error " + str(-ctypes.get_errno()))
        
        def Sleep(time_cs): #this is stolen too, idk why its part of pvztools but it is
            if time_cs > 0.0:
                time.sleep(time_cs / 100)
            elif time_cs == 0.0:
                pass
            else:
                error("The thread sleep time cannot be less than zero.")
        
        def game_ui():
            return ReadMemory("int", 0x6A9EC0, 0x7FC)
        
        pvz_memfd = openPVZ()
except:
    print("pvz not found!")
import random

window=Tk() #Creates a window object from the Tk class
window.title("Randomiser settings")
challengeMode=False
shopless=False
noRestrictions=False
noAutoSlots=False
imitater=False
randomisePlants=False
seeded=False
seed=str(random.randint(1,999999999999))

def challengeButtonClick():
    global noRestrictions, challengeMode
    if not noRestrictions:
        challengeMode=not challengeMode
    buttonClick()
def shoplessButtonClick():
    global shopless
    shopless=not shopless
    buttonClick()

def noRestrictionsButtonClick():
    global noRestrictions, challengeMode
    noRestrictions=not noRestrictions
    if noRestrictions:
        challengeMode=True
    buttonClick()

def autoSlotsButtonClick():
    global noAutoSlots, shopless
    if not shopless:
        noAutoSlots=not noAutoSlots
    buttonClick()

def imitaterButtonClick():
    global imitater
    imitater=not imitater
    buttonClick()

def randPlantsButtonClick():
    global randomisePlants
    randomisePlants=not randomisePlants
    buttonClick()

def seededButtonClick():
    global seeded
    seeded=not seeded
    buttonClick()
    
def closeButtonClick():
    getSeed()
    window.destroy()

def informationButtonClick():
    outputText.delete(0.0, END)
    manipulatedText="Challenge Mode gets rid of the tough level restriction. With this disabled, you will not be able to play certain levels (like 5-2) without having 3 good plants. Other levels (like 5-9) will need 5 good plants to play. With this enabled, as soon as you unlock flower pot, you can play both 5-2 and 5-9 (for instance). Shopless mode forces you to play with 6 slots and no automatic pool cleaners / roof cleaners. No restrictions mode means that there is no logic as to what levels can be played next - the majority of no restrictions runs are impossible. With manual money enabled, you do not get automatic slot upgrades, but your money does not reset to 0 after every level, and so you can purchase the slots yourself - this also means you can buy rakes and upgrade plants! Instant imitater mode gives you access to an imitater immediately, which allows you to choose one of any plant to bring to the stage, even if you haven't unlocked it! This works especially well with no restrictions. Random plants means that the plant you get at the end of each level is RANDOMISED, in a similar way to the levels! Instead of unlocking the plant you usually unlock for beating that stage, you get a random one!"
    outputText.insert(END, manipulatedText)

def buttonClick():
    global noRestrictions, challengeMode, shopless, noAutoSlots, imitater, randomisePlants, spaces, seeded
    outputText.delete(0.0, END) #this clears the contents of the text box widget
    if not noRestrictions:
        manipulatedText="Challenge Mode: " + str(challengeMode) + (" " * spaces) + "Shopless: " + str(shopless) + (" " * spaces) + "No restrictions: " + str(noRestrictions) + (" " * spaces) + "Manual Money: " + str(noAutoSlots) + (" " * spaces) + "Instant Imitater: " + str(imitater) + (" " * spaces) + "Random Plants: " + str(randomisePlants) + (" " * spaces) + "Seeded: " + str(seeded)#Concatenation
    else:
        manipulatedText="Challenge Mode (locked): " + str(challengeMode) + (" " * spaces) + "Shopless: " + str(shopless) + (" " * spaces) + "No restrictions: " + str(noRestrictions) + (" " * spaces) + "Manual Money: " + str(noAutoSlots) + (" " * spaces) + "Instant Imitater: " + str(imitater) + (" " * spaces) + "Random Plants: " + str(randomisePlants) + (" " * spaces) + "Seeded: " + str(seeded)#Concatenation
    outputText.insert(END, manipulatedText) #this inserts the manipulatedText variable into the text box
def getSeed():
    global seed
    seed=entry.get()
    if seed=="":
        seed=str(random.randint(1,999999999999))

#Create a label widget and assign it to a variable
label=Label(window, text="Enter seed: ")
label.grid(row=0, column=0, sticky=W) #Poistioning this widget (now in a variable) on the screen

spaces=150

#create a button widget
challengeButton=Button(window, text="CHALLENGE", width=15, command=challengeButtonClick)
challengeButton.grid(row=1, column=0, sticky=W)
shoplessButton=Button(window, text="SHOPLESS", width=15, command=shoplessButtonClick)
shoplessButton.grid(row=1, column=1, sticky=W)
noRestrictionsButton=Button(window, text="NO RESTRICTIONS", width=15, command=noRestrictionsButtonClick)
noRestrictionsButton.grid(row=1, column=2, sticky=W)
noRestrictionsButton=Button(window, text="MANUAL MONEY", width=15, command=autoSlotsButtonClick)
noRestrictionsButton.grid(row=1, column=3, sticky=W)
imitaterButton=Button(window, text="INSTANT IMITATER", width=15, command=imitaterButtonClick)
imitaterButton.grid(row=1, column=4, sticky=W)
randPlantsButton=Button(window, text="RANDOM PLANTS", width=15, command=randPlantsButtonClick)
randPlantsButton.grid(row=1, column=5, sticky=W)
seededButton=Button(window, text="SEEDED", width=15, command=seededButtonClick)
seededButton.grid(row=2, column=0, sticky=W)
closeButton=Button(window, text="SUBMIT SETTINGS", width=15, command=closeButtonClick)
closeButton.grid(row=1, column=6, sticky=W)
informationButton=Button(window, text="INFORMATION", width=15, command=informationButtonClick)
informationButton.grid(row=1, column=7, sticky=W)

#creates an entry widget, assigning it to a variable
entry=Entry(window, width=20, bg="light green")
entry.grid(row=0, column=1, sticky=W) #positioning this widget on the screen

#create a text box widget
outputText=Text(window, width=120, height=8, wrap=WORD, background="yellow")
outputText.grid(row=3, column=0, columnspan=10, sticky=W)
outputText.insert(END, "Challenge Mode: " + str(challengeMode) + (" " * spaces) + "Shopless: " + str(shopless) + (" " * spaces) + "No restrictions: " + str(noRestrictions) + (" " * spaces) + "Manual Money: "  + str(noAutoSlots) + (" " * spaces) + "Instant Imitater: " + str(imitater)+ (" " * spaces) + "Random Plants: " + str(randomisePlants) + (" " * spaces) + "Seeded: " + str(seeded))

window.mainloop() #Run the event loop
print(seed)
#random.seed(seed)

LEVEL_PLANTS = [
0,
1,  2,  3,  -1, 4,  5,  6,  7,  -1,  8,
9,  10, 11, -1, 12, 13, 14, 15, -1, 16,
17, 18, 19, -1, 20, 21, 22, 23, -1, 24,
25, 26, 27, -1, 28, 29, 30, 31, -1, 32,
33, 34, 35, -1, 36, 37, 38, 39, -1, -1
]

def randomiseLevels2(seed):
    global noRestrictions, challengeMode
    random.seed(seed)
    firstLevels=[]
    levels=[1]
    toughLevelCheck=0
    balloonCheck=0
    if noRestrictions:
        for i in range(2, 51):
            levels.append(i)
    for i in range(0,50):
        levels, firstLevels = addLevel(levels, firstLevels)
        if not noRestrictions:
            if i==0: #after 1-1, can play any day stage or any x-5 / x-10
                levels=addToLevelsList(levels, [2, 3, 4, 5, 6, 7, 8, 9, 10, 15, 20, 25, 30, 35, 40, 45, 50])
            if firstLevels[i] in [2, 7, 8, 18, 21, 25, 36, 38, 43, 48]: #cherry bomb, chomper, repeater, doom, squash, jalapeno, starfruit, magnet, coffee bean, melon pult
                    toughLevelCheck += 1
            if firstLevels[i] in [2, 18, 25]:
                balloonCheck+=1
            elif firstLevels[i] in [32, 33]:
                balloonCheck+=2
            has_puff              = 10 in firstLevels
            has_lily              = 20 in firstLevels
            has_fog_plants        = has_puff and (has_lily or 30 in firstLevels)
            has_pot               = 41 in firstLevels
            has_roof_plant        = 40 in firstLevels or has_pot
            for j in range(1, 51):
                if j not in levels and j not in firstLevels:
                    if j==11:
                        if has_puff:
                            levels=addToLevelsList(levels, j)
                    elif j==12:
                        if has_puff:
                            if not challengeMode:
                                if toughLevelCheck>=3:
                                    levels=addToLevelsList(levels, j)
                            else:
                                levels=addToLevelsList(levels, j)
                    elif j==13:
                        if has_puff:
                            levels=addToLevelsList(levels, j)
                    elif j==14:
                        if has_puff:
                            if not challengeMode:
                                if toughLevelCheck>=3:
                                    levels=addToLevelsList(levels, j)
                            else:
                                levels=addToLevelsList(levels, j)
                    elif j==16:
                        if has_puff:
                            levels=addToLevelsList(levels, j)
                    elif j==17:
                        if has_puff:   
                            if not challengeMode:
                                if toughLevelCheck>=3:
                                    levels=addToLevelsList(levels, j)
                            else:
                                levels=addToLevelsList(levels, j)
                    elif j==18:
                        if has_puff:
                            levels=addToLevelsList(levels, j)
                    elif j==19:
                        if has_puff:
                            if not challengeMode:
                                if toughLevelCheck>=3:
                                    levels=addToLevelsList(levels, j)
                            else:
                                levels=addToLevelsList(levels, j)
                    elif j==21:
                        if has_lily or 36 in firstLevels:
                            levels=addToLevelsList(levels, j)
                    elif j==22:
                        if has_lily or 36 in firstLevels:
                            if not challengeMode:
                                if toughLevelCheck>=3:
                                    levels=addToLevelsList(levels, j)
                            else:
                                levels=addToLevelsList(levels, j)
                    elif j==23:
                        if has_lily:
                            levels=addToLevelsList(levels, j)
                    elif j==24:
                        if has_lily:
                            if not challengeMode:
                                if toughLevelCheck>=5:
                                    levels=addToLevelsList(levels, j)
                            else:
                                levels=addToLevelsList(levels, j)
                    elif j==26:
                        if has_lily or 36 in firstLevels:
                            if not challengeMode:
                                if toughLevelCheck>=3:
                                    levels=addToLevelsList(levels, j)
                            else:
                                levels=addToLevelsList(levels, j)
                    elif j==27:
                        if has_lily:
                            if not challengeMode:
                                if toughLevelCheck>=5:
                                    levels=addToLevelsList(levels, j)
                            else:
                                levels=addToLevelsList(levels, j)
                    elif j==28:
                        if has_lily or ((22 in firstLevels or 36 in firstLevels) and 30 in firstLevels):
                            levels=addToLevelsList(levels, j)
                    elif j==29:
                        if has_lily or ((22 in firstLevels or 36 in firstLevels) and 30 in firstLevels): #if you have lilypad, OR if you have sea shroom + threepeater or starfruit
                            if not challengeMode:
                                if toughLevelCheck>=5:
                                    levels=addToLevelsList(levels, j)
                            else:
                                levels=addToLevelsList(levels, j)
                    elif j==31:
                        if has_fog_plants:
                            levels=addToLevelsList(levels, j)
                    elif j==32:
                        if has_puff:
                            if has_lily or (30 in firstLevels and (22 in firstLevels or 36 in firstLevels)): #if you have lilypad, OR if you have sea shroom + threepeater or starfruit
                                if not challengeMode:
                                    if toughLevelCheck>=3:
                                        levels=addToLevelsList(levels, j)
                                else:
                                    levels=addToLevelsList(levels, j)
                    elif j==33:
                        if has_fog_plants:
                            levels=addToLevelsList(levels, j)
                    elif j==34:
                        if has_puff:
                            if has_lily:
                                if balloonCheck>=2:
                                    if not challengeMode:
                                        if toughLevelCheck>=3:
                                            levels=addToLevelsList(levels, j)
                                    else:
                                        levels=addToLevelsList(levels, j)
                    elif j==36:
                        if has_fog_plants:
                            levels=addToLevelsList(levels, j)
                    elif j==37:
                        if has_puff:
                            if has_lily or (30 in firstLevels and (22 in firstLevels or 36 in firstLevels)): #if you have lilypad, OR if you have sea shroom + threepeater or starfruit
                                if not challengeMode:
                                    if toughLevelCheck>=5:
                                        levels=addToLevelsList(levels, j)
                                else:
                                    levels=addToLevelsList(levels, j)
                    elif j==38:
                        if has_fog_plants:
                                levels=addToLevelsList(levels, j)
                    elif j==39:
                        if has_puff:
                            if has_lily:
                                if balloonCheck>=2:
                                    if not challengeMode:
                                        if toughLevelCheck>=5:
                                            levels=addToLevelsList(levels, j)
                                    else:
                                        levels=addToLevelsList(levels, j)
                    elif j==41:
                        if i>=10 or 40 in firstLevels:
                            levels=addToLevelsList(levels, j)
                    elif j==42:
                        if has_pot:
                            if not challengeMode:
                                if toughLevelCheck>=3:
                                    levels=addToLevelsList(levels, j)
                            else:
                                levels=addToLevelsList(levels, j)
                    elif j==43:
                        if has_roof_plant:
                            if not challengeMode:
                                if toughLevelCheck>=3:
                                    levels=addToLevelsList(levels, j)
                            else:
                                levels=addToLevelsList(levels, j)
                    elif j==44:
                        if has_pot:
                            if not challengeMode:
                                if toughLevelCheck>=5:
                                    levels=addToLevelsList(levels, j)
                            else:
                                levels=addToLevelsList(levels, j)
                    elif j==46:
                        if has_roof_plant:
                            if not challengeMode:
                                if toughLevelCheck>=3:
                                    levels=addToLevelsList(levels, j)
                            else:
                                levels=addToLevelsList(levels, j)
                    elif j==47:
                        if has_pot:
                            if not challengeMode:
                                if toughLevelCheck>=5:
                                    levels=addToLevelsList(levels, j)
                            else:
                                levels=addToLevelsList(levels, j)
                    elif j==48:
                        if has_pot:
                            if not challengeMode:
                                if toughLevelCheck>=3:
                                    levels=addToLevelsList(levels, j)
                            else:
                                levels=addToLevelsList(levels, j)
                    elif j==49:
                        if has_pot:
                            if not challengeMode:
                                if toughLevelCheck>=5:
                                    levels=addToLevelsList(levels, j)
                            else:
                                levels=addToLevelsList(levels, j)
    return firstLevels

def randomiseLevels(seed):
    global noRestrictions, challengeMode
    random.seed(seed)
    firstLevels=[]
    levels=[1]
    toughLevelCheck=0
    balloonCheck=0
    if noRestrictions:
        for i in range(2, 51):
            levels.append(i)
    for i in range(0,50):
        levels, firstLevels = addLevel(levels, firstLevels)
        levels = sorted(list(getAvailableStages(getDefaultPlantArrayFromLevels(firstLevels), firstLevels)))
    return firstLevels

def randomiseLevelsAndPlants(seed):
    global noRestrictions, challengeMode
    random.seed(seed)
    
    plants = [1]
    levels = [1]
    unused_plants   = [i        for i in range(2,40)]
    if challengeMode or noRestrictions:
        level_plants    = [(-1,1.0) for i in range(0,51)]
    else:
        level_plants    = [(-1,0.8) for i in range(0,51)]
    level_plants[0] =  (0, 0.0)
    level_plants[1] =  (1, 0.0)
    if not noRestrictions:
        while 1: #select key plants for only levels you could have unlocked by that point
            current_available = len(getAvailableStages(plants,levels))
            plants.append(0)
            key_plants   = []
            key_weights  = []
            key_weights2 = []
            for i in unused_plants:
                plants[-1] = i
                if current_available < len(getAvailableStages(plants,levels)):
                    key_plants.append(i)
                    key_weights.append(1.0)
                    key_weights2.append(3.0)
                elif i in {2, 6, 7, 15, 17, 20, 29, 31, 35, 39}:
                    key_plants.append(i)
                    key_weights.append(0.23)
                    if challengeMode:
                        key_weights2.append(1.0)
                    else:
                        key_weights2.append(1.3)
            
            if not key_plants:
                break
            
            chosen_plant     = random.choices(key_plants, weights=key_weights)[0]
            chosen_weight    = key_weights2[key_plants.index(chosen_plant)]
            plants[-1]       = chosen_plant
            available_levels = sorted(list(getAvailableStages(plants[0:-2], levels)))
            chosen_level     = random.choice(available_levels)
            unused_plants.remove(chosen_plant)
            
            levels.append(chosen_level)
            level_plants[chosen_level] = (chosen_plant,chosen_weight)
        
    for i in unused_plants:
        available_levels = sorted(list(getAvailableStages(plants, levels))) #should return all levels without plants assigned
        chosen_level     = random.choice(available_levels)
        
        levels.append(chosen_level)
        if i==9:
            level_plants[chosen_level] = (i,2.0)
        else:
            level_plants[chosen_level] = (i,1.0)
    
    levels = [1]
    plants = [1]
    world_weights = [0.93, 1.0, 1.0, 1.0, 1.0]
    for i in range(1,50):
        available_levels = sorted(list(getAvailableStages(plants, levels)))
        chosen_level     = random.choices(available_levels, weights=[level_plants[i][1]*world_weights[int((i-1)/10)] for i in available_levels])[0]
        world_weights[int((chosen_level-1)/10)] -= 0.07
        levels.append(chosen_level)
        plants.append(level_plants[chosen_level][0])
    
    level_plants = [i[0] for i in level_plants]
    return levels, level_plants

def getDefaultPlantArrayFromLevels(levels):
    global LEVEL_PLANTS
    plants = []
    for i in levels:
        if LEVEL_PLANTS[i] != -1:
            plants.append(LEVEL_PLANTS[i])
    return plants

def getAvailableStages(plants, used_levels=[]):
    global noRestrictions, challengeMode
    if len(used_levels) == 0:
        level_set = {1}
    elif noRestrictions:
        level_set = {
        2,  3,  4,  5,  6,  7,  8,  9,  10,
        11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
        21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
        31, 32, 33, 34, 35, 36, 37, 38, 39, 40,
        41, 42, 43, 44, 45, 46, 47, 48, 49, 50}
    else:
        level_set = {2, 3, 4, 5, 6, 7, 8, 9, 10, 15, 20, 25, 30, 35, 40, 45, 50}
        plant_set = set(plants)
        
        tough_check   = len(plant_set & {2, 6, 7, 15, 17, 20, 29, 31, 35, 39}) #cherry bomb, chomper, repeater, doom, squash, jalapeno, starfruit, magnet, coffee bean, melon pult
        balloon_check = len(plant_set & {2, 15, 20}) + 2 * len(plant_set & {26, 27})
        
        if challengeMode:
            tough_check = 9999
        
        has_puff              = 8  in plant_set
        has_lily              = 16 in plant_set
        has_pool_shooter      = 29 in plant_set or 18 in plant_set
        has_seapeater         = 24 in plant_set and has_pool_shooter #threepeater or starfruit + sea shroom
        has_fog_plants        = has_puff and (has_lily or 24 in plant_set)
        has_pot               = 33 in plant_set
        has_roof_plant        = 32 in plant_set or 39 in plant_set or has_pot
        
        if has_puff:
            level_set.add(11)
        if has_puff and tough_check >= 3:
            level_set.add(12)
        if has_puff:
            level_set.add(13)
        if has_puff and tough_check >= 3:
            level_set.add(14)
        if has_puff:
            level_set.add(16)
        if has_puff and tough_check >= 3:
            level_set.add(17)
        if has_puff:
            level_set.add(18)
        if has_puff and tough_check >= 3:
            level_set.add(19)
        
        if has_lily or has_pool_shooter:
            level_set.add(21)
        if (has_lily or has_pool_shooter) and tough_check >= 3:
            level_set.add(22)
        if has_lily:
            level_set.add(23)
        if has_lily and tough_check >= 5:
            level_set.add(24)
        if (has_lily or has_pool_shooter) and tough_check >= 3:
            level_set.add(26)
        if has_lily and tough_check >= 5:
            level_set.add(27)
        if has_lily or has_seapeater:
            level_set.add(28)
        if (has_lily or has_seapeater) and tough_check >= 5:
            level_set.add(29)
        
        if has_fog_plants:
            level_set.add(31)
        if has_puff and (has_lily or has_seapeater) and tough_check >= 3:
            level_set.add(32)
        if has_fog_plants:
            level_set.add(33)
        if has_puff and has_lily and balloon_check >= 2 and tough_check >= 3:
            level_set.add(34)
        if has_fog_plants:
            level_set.add(36)
        if has_puff and (has_lily or has_seapeater) and tough_check >= 5:
            level_set.add(37)
        if has_fog_plants:
            level_set.add(38)
        if has_puff and has_lily and balloon_check >= 2 and tough_check >= 5:
            level_set.add(39)
        
        if has_roof_plant or len(used_levels) > 10:
            level_set.add(41)
        if has_pot and tough_check >= 3:
            level_set.add(42)
        if has_roof_plant and tough_check >= 3:
            level_set.add(43)
        if has_pot and tough_check >= 5:
            level_set.add(44)
        if has_roof_plant and tough_check >= 3:
            level_set.add(46)
        if has_pot and tough_check >= 5:
            level_set.add(47)
        if has_pot and tough_check >= 3:
            level_set.add(48)
        if has_pot and tough_check >= 5:
            level_set.add(49)
    
    for i in used_levels:
        if i in level_set:
            level_set.remove(i)
    
    return level_set

def addLevel(levels, firstLevels):
    global noRestrictions
    newLevel=1
    count=0
    countTarget=(len(firstLevels)//5)+1
    if not noRestrictions:
        if 10 in levels or 20 in levels or 30 in levels or 40 in levels or 41 in levels:
            while count<countTarget and newLevel not in [10, 20, 30, 40, 41]:
                count=count+1
                newLevel = random.choice(levels)
        else:
            newLevel = random.choice(levels)
        if 11 in levels and newLevel in [12, 13, 14, 16, 17, 18, 19, 31, 32, 33, 34, 36, 37, 38, 39]: #if 2-1 hasn't been played and the next level is a night/fog level with seed select
            nightTimeLevels=[]
            count=0
            nightCount=0
            for i in range(0, len(levels)):
                if levels[i] in [12, 13, 14, 16, 17, 18, 19, 31, 32, 33, 34, 36, 37, 38, 39]:
                    nightTimeLevels.append(levels[i])
            for j in range(0, len(firstLevels)):
                if firstLevels[j] in [12, 13, 14, 16, 17, 18, 19, 31, 32, 33, 34, 36, 37, 38, 39]:
                    nightCount+=1
            countTarget=nightCount//3
            nightTimeLevels.append(11)
            while count<countTarget and newLevel!=11:
                newLevel = random.choice(nightTimeLevels)
                count+=1
    else:
        if len(firstLevels)==0:
            newLevel=1
        else:
            newLevel = random.choice(levels)
    firstLevels.append(newLevel)
    levels.remove(newLevel)
    return levels, firstLevels

def addToLevelsList(levels, numberList):
    if type(numberList)==int:
        numberList=[numberList]
    for i in range(0, len(numberList)):
        levels.append(numberList[i])
    return levels

def showAverage(): #balancing purposes
    global randomisePlants
    dayAverage=0
    nightAverage=0
    poolAverage=0
    fogAverage=0
    roofAverage=0
    averageTarget=10000
    random_seeds = [random.getrandbits(32) for i in range(0,averageTarget)]
    for i in random_seeds:
        dayCount=0
        nightCount=0
        poolCount=0
        fogCount=0
        roofCount=0
        if randomisePlants:
            levels, _ = randomiseLevelsAndPlants(i)
        else:
            levels = randomiseLevels(i)
        for j in range(30, 50):
            if levels[j]>30 and levels[j]<40 and levels[j]!=35:
                fogCount+=1
            elif levels[j]>40 and levels[j]!=50 and levels[j]!=45:
                roofCount+=1
            elif levels[j]>20 and levels[j]<30 and levels[j]!=25:
                poolCount+=1
            elif levels[j]>10 and levels[j]<20 and levels[j]!=15:
                nightCount+=1
            elif levels[j]>0 and levels[j]<10 and levels[j]!=5:
                dayCount+=1
        dayAverage+=dayCount
        nightAverage+=nightCount
        poolAverage+=poolCount
        fogAverage+=fogCount
        roofAverage+=roofCount
    print(dayAverage/averageTarget, nightAverage/averageTarget, poolAverage/averageTarget, fogAverage/averageTarget, roofAverage/averageTarget)

def nightAverage():

    nightAverage=0
    lastTotal=0
    for i in range(0, 100000):
        nightLevels=0
        levels=randomiseLevels()
        for i in range(0, len(levels)):
            if levels[i] in [12, 13, 14, 16, 17, 18, 19, 31, 32, 33, 34, 36, 37, 38, 39]:
                nightLevels+=1
            elif levels[i]==11:
                if nightLevels==15:
                    lastTotal+=1
                break
        nightAverage+=nightLevels
    print(nightAverage/100000, lastTotal)

#showAverage()
#nightAverage()
if randomisePlants:
    levels, level_plants = randomiseLevelsAndPlants(seed)
else:
    levels = randomiseLevels(seed)
    level_plants = LEVEL_PLANTS

plants_array  = [-1,0]
plants_array2 = []
for i in levels:
    if level_plants[i] != -1:
        plants_array2.append(level_plants[i])
        plants_array.append(level_plants[i])
    else:
        plants_array2.append(0x4b) #nothing plant, costs 6977196 sun
for i in [40,41,42,43,44,45,46,47,48]:
    plants_array.append(i)

SEED_STRINGS = [
    "Peashooter",   "Sunflower",      "Cherry Bomb",  "Wall-nut",     "Potato Mine",  "Snow Pea",       "Chomper",    "Repeater",
    "Puff-shroom",  "Sun-shroom",     "Fume-shroom",  "Grave Buster", "Hypno-shroom", "Scaredy-shroom", "Ice-shroom", "Doom-shroom",
    "Lily Pad",     "Squash",         "Threepeater",  "Tangle Kelp",  "Jalapeno",     "Spikeweed",      "Torchwood",  "Tall-nut",
    "Sea-shroom",   "Plantern",       "Cactus",       "Blover",       "Split Pea",    "Starfruit",      "Pumpkin",    "Magnet-shroom",
    "Cabbage-pult", "Flower Pot",     "Kernel-pult",  "Coffee Bean",  "Garlic",       "Umbrella Leaf",  "Marigold",   "Melon-pult",
    "Gatling Pea",  "Twin Sunflower", "Gloom-shroom", "Cattail",      "Winter Melon", "Gold Magnet",    "Spikerock",  "Cob Cannon",
    "Imitater",     "NONE"
]

LEVEL_STRINGS = ["Not a level",
    "1-1", "1-2", "1-3", "1-4", "1-5", "1-6", "1-7", "1-8", "1-9", "1-10",
    "2-1", "2-2", "2-3", "2-4", "2-5", "2-6", "2-7", "2-8", "2-9", "2-10",
    "3-1", "3-2", "3-3", "3-4", "3-5", "3-6", "3-7", "3-8", "3-9", "3-10",
    "4-1", "4-2", "4-3", "4-4", "4-5", "4-6", "4-7", "4-8", "4-9", "4-10",
    "5-1", "5-2", "5-3", "5-4", "5-5", "5-6", "5-7", "5-8", "5-9", "5-10"
]

##for i in levels:
##    print(LEVEL_STRINGS[i], SEED_STRINGS[level_plants[i]])

#Seed packet rendering on the seed select screen

WriteMemory("unsigned char", [
0x8b, 0x45, 0x08,                         #movl  0x8(%ebp),    %eax
0x6a, 0x00,                               #pushl $0x0
0x6a, 0x01,                               #pushl $0x1
0x6a, 0x00,                               #pushl $0x0
0x6a, 0xff,                               #pushl $-0x1
0xff, 0x34, 0xb5, 0x98, 0x10, 0x65, 0x00, #pushl 0x651098(,%esi,4)
0xdb, 0x44, 0x24, 0x30,                   #fildl 0x30(%esp)
0xdb, 0x44, 0x24, 0x34,                   #fildl 0x34(%esp)
0x50,                                     #pushl %eax
0xd9, 0x1c, 0x24,                         #fstps (%esp)
0x50,                                     #pushl %eax
0xd9, 0x1c, 0x24,                         #fstps (%esp)
0xb9, 0x37, 0x00, 0x00, 0x00,             #movl  $0x37,        %ecx
0x50                                      #pushl %eax
], 0x484893)
WriteMemory("unsigned char", [
0x8b, 0x43, 0x20,                               #movl    0x20(%ebx),        %eax
0x83, 0x7b, 0x24, 0x00,                         #cmpl    $0x0,        0x24(%ebx)
0x0f, 0x43, 0x04, 0x85, 0x98, 0x10, 0x65, 0x00, #cmovncl 0x651098(,%eax,4), %eax #I originally thought a cmp and cmov were required for this but was too lazy to remove them so I made the cmov activate every time
0x6a, 0x00,                                     #pushl   $0x0
0x6a, 0x01,                                     #pushl   $0x1
0x6a, 0x00,                                     #pushl   $0x0
0xff, 0x73, 0x34,                               #pushl   $0x34(%ebx)
0x50,                                           #pushl   %eax
0xdb, 0x44, 0x24, 0x30,                         #fildl   0x30(%esp)
0xdb, 0x44, 0x24, 0x2c,                         #fildl   0x2C(%esp)
0x50,                                           #pushl   %eax
0xd9, 0x1c, 0x24,                               #fstps   (%esp)
0x50,                                           #pushl   %eax
0xd9, 0x1c, 0x24,                               #fstps   (%esp)
0x31, 0xc9,                                     #xorl    %ecx, %ecx
0x80, 0x7c, 0x24, 0x2f, 0x01,                   #cmpb    $0x1,        0x2f(%esp)
0x18, 0xc9,                                     #sbbb    %cl,                %cl
0x80, 0xc9, 0x73,                               #orb     $0x73,              %cl
0xff, 0x75, 0x08,                               #pushl   0x8(%ebp)
0x90,                                           #nop
], 0x484a93)
WriteMemory("unsigned char", [
0x8b, 0x50, 0x20,                         #movl  0x20(%eax), %edx
0x6a, 0x00,                               #pushl $0x0
0x6a, 0x01,                               #pushl $0x1
0x6a, 0x00,                               #pushl $0x0
0xff, 0x74, 0x20, 0x34,                   #pushl 0x34(%eax)
0xff, 0x34, 0x95, 0x98, 0x10, 0x65, 0x00, #pushl 0x651098(,%edx,4)
0xdb, 0x00,                               #fildl (%eax)
0xdb, 0x40, 0x04,                         #fildl 0x4(%eax)
0x50,                                     #pushl %eax
0xd9, 0x1c, 0x24,                         #fstps (%esp)
0x50,                                     #pushl %eax
0xd9, 0x1c, 0x24,                         #fstps (%esp)
0xb9, 0xff, 0x00, 0x00, 0x00,             #movl  $0xff, %ecx
0x8b, 0x45, 0x08,                         #movl  0x8(%ebp), %eax
0x50,                                     #pushl %eax
], 0x484b48)



#Plant select warnings

WriteMemory("unsigned char", [
0x39, 0x41, 0x04,                         #cmpl %eax, 0x4(%ecx)
0x75, 0x17,                               #jne  0x486d0a <.text+0x85d0a>
0x8b, 0x11,                               #movl (%ecx), %edx
0x8b, 0x14, 0x95, 0x98, 0x10, 0x65, 0x00, #movl 0x651098(,%edx,4), %edx
0x3b, 0xd7,                               #cmpl %edi, %edx
0x74, 0x16,                               #je   0x486d16 <.text+0x85d16>
0x83, 0xfa, 0x30,                         #cmpl $0x30, %edx
0x75, 0x05,                               #jne  0x486d0a <.text+0x85d0a>
0x39, 0x79, 0x14,                         #cmpl %edi, 0x14(%ecx)
0x74, 0x0c,                               #je   0x486d16 <.text+0x85d16>
0x03, 0xf0,                               #addl %eax, %esi
0x83, 0xc1, 0x3c,                         #addl $0x3c, %ecx
0x83, 0xfe, 0x31,                         #cmpl $0x31, %esi
0x7c, 0xda,                               #jl   0x486cee <.text+0x85cee>
0x32, 0xc0,                               #xorb %al, %al
0x5e,                                     #popl %esi
0xc3                           	          #retl
], 0x486cee)

WriteMemory("unsigned char", [
0xeb, 0x32 #jmp  0x484614
], 0x4845e0)
WriteMemory("unsigned char", [
0x53,                                     #pushl %ebx
0x55,                                     #pushl %ebp
0x8b, 0x34, 0xb5, 0x98, 0x10, 0x65, 0x00, #movl 0x651098(,%esi,4), %esi
0xeb, 0xc3,                               #jmp  0x4845e2
], 0x484614)

WriteMemory("int", 0x41cc59 - 0x4849fc, 0x4849f8) #call 0x41cc59
WriteMemory("unsigned char", [
0x8b, 0x34, 0xb5, 0x98, 0x10, 0x65, 0x00, #movl 0x651098(,%esi,4), %esi
], 0x41cc59)



#Translate seeds from the seed select screen to the actual seeds that will be used during the level

WriteMemory("unsigned char", [
0x8b, 0x93, 0x14, 0x0d, 0x00, 0x00,       #movl  0xd14(%ebx),       %edx
0x8b, 0x3c, 0x85, 0x98, 0x10, 0x65, 0x00, #movl  0x651098(,%eax,4), %edi
0x6b, 0xcf, 0x0f,                         #imull $0xf,        %edi, %ecx
0x8d, 0x6c, 0x8b, 0x70,                   #leal  0x70(%ebx,%ecx,4), %ebp
0x8b, 0x8a, 0x44, 0x01, 0x00, 0x00,       #movl  0x144(%edx),       %ecx
0x8b, 0x54, 0x24, 0x10,                   #movl  0x10(%esp),        %edx
0x8d, 0x74, 0x11, 0x28,                   #leal  0x28(%ecx,%edx),   %esi
0x8b, 0x55, 0x68,                         #movl  0x68(%ebp),        %edx
0x90,                                     #nop
0xe8, 0xd5, 0x2d, 0x00, 0x00,             #calll 0x489b50
0x80, 0x7d, 0x60, 0x00,                   #cmpb  $0x0,        0x60(%ebp)
0x8d, 0x6d, 0x90                          #leal  -0x70(%ebp),       %ebp
], 0x486d50)



#Get number of seeds unlocked function

if imitater:
    WriteMemory("unsigned char", [
    0xa1, 0x90, 0x10, 0x65, 0x00,             #movl  0x651090,    %eax
    0x81, 0x3c, 0x24, 0x1e, 0x3c, 0x45, 0x00, #cmpl  $0x453c1e, (%esp)
    0x0f, 0x95, 0xc1,                         #setne %cl
    0x81, 0x3c, 0x24, 0xef, 0xbf, 0x41, 0x00, #cmpl  $0x41bfef, (%esp)
    0x74, 0x02,                               #jne   0x453af2
    0x00, 0xc8,                               #addb  %cl,          %al
    0x83, 0xf8, 0x31,                         #cmpl  $0x31,       %eax
    0x7e, 0x05,                               #jle   0x453afc
    0xb8, 0x31, 0x00, 0x00, 0x00,             #movl  $0x31,       %eax
    0xc3,                                     #retl
    0x90,                                     #nop
    ], 0x453ad8)
else:
    WriteMemory("unsigned char", [
    0xa1, 0x90, 0x10, 0x65, 0x00, #movl 0x651090, %eax
    0x83, 0xf8, 0x31,             #cmpl $0x31,    %eax
    0x7e, 0x05,                   #jle  0x453ae7
    0xb8, 0x31, 0x00, 0x00, 0x00, #movl $0x31,    %eax
    0xc3,                         #retl
    ], 0x453ad8)



#Seed select plant descriptions

WriteMemory("unsigned char", [
0x8b, 0x44, 0x24, 0x04,                   #movl 0x4(%esp),         %eax
0x8b, 0x04, 0x85, 0x98, 0x10, 0x65, 0x00, #movl 0x651098(,%eax,4), %eax
0x89, 0x44, 0x24, 0x04,                   #movl %eax,         0x4(%esp)
0xe9, 0xc0, 0x5d, 0xe1, 0xff              #jmp  0x467db0
], 0x651fdc)
WriteMemory("unsigned char", [
0x8b, 0x44, 0x24, 0x0c,                   #movl 0xc(%esp),         %eax
0x8b, 0x04, 0x85, 0x98, 0x10, 0x65, 0x00, #movl 0x651098(,%eax,4), %eax
0x89, 0x44, 0x24, 0x0c,                   #movl %eax,         0xc(%esp)
0xc3                                      #retl
], 0x651ff0)
WriteMemory("unsigned char", [
0xe8, 0xf0, 0xa3, 0x1e, 0x00 #call 0x651ff0
], 0x467bfb)
WriteMemory("int", 0x651fdc - 0x486515, 0x486511) #call 0x651fdc
WriteMemory("int", 0x467bfb - 0x4864e2, 0x4864de) #call 0x467bfb



#Imitater

WriteMemory("unsigned char",[
0xb8, 0x01, 0x00, 0x00, 0x00 #movl $0x1, %eax
], 0x482d5d)
WriteMemory("unsigned char",[
0xb8, 0x01, 0x00, 0x00, 0x00 #movl $0x1, %eax
], 0x482f05)



#Credits  (bugged right now)

##WriteMemory("unsigned char", [
##levels[-1],
##0x74 #je
##], 0x452551)
##WriteMemory("unsigned char", [
##levels[-1]
##], 0x452561)



#shovel

WriteMemory("unsigned char", 1, 0x530028)
WriteMemory("unsigned char", 1, 0x43c1d1)



#chacha8 (for rng)

WriteMemory("unsigned char", [
0x65, 0x78, 0x70, 0x71, 0x6e, 0x64, 0x20, 0x33, 0x32, 0x2d, 0x62, 0x79, 0x74, 0x65, 0x20, 0x6b #expand 32-byte k
], 0x651160)
random.seed(seed)
WriteMemory("unsigned int", [random.getrandbits(32) for i in range(8)], 0x651170)
WriteMemory("int",1,0x651190)
WriteMemory("unsigned char", [
                                                      #chacha8:
0xb8, 0x90, 0x11, 0x65, 0x00,                         #        movl   $0x651190,      %eax
0xff, 0x42, 0x08,                                     #        incl   0x8(%edx)
0x66, 0x0f, 0x1f, 0x44, 0x00, 0x00,                   #        nop
0x66, 0x0f, 0x6f, 0x1a,                               #        movdqa (%edx),        %xmm3
0x66, 0x0f, 0xc4, 0x58, 0x00, 0x06,                   #        pinsrw $6, 0x0(%eax), %xmm3
0x66, 0x0f, 0xc4, 0x58, 0x02, 0x07,                   #        pinsrw $7, 0x2(%eax), %xmm3
0x66, 0x0f, 0x6f, 0x04, 0x25, 0x60, 0x11, 0x65, 0x00, #        movdqa 0x651160, %xmm0
0x66, 0x0f, 0x6f, 0x0c, 0x25, 0x70, 0x11, 0x65, 0x00, #        movdqa 0x651170, %xmm1
0x66, 0x0f, 0x6f, 0x14, 0x25, 0x80, 0x11, 0x65, 0x00, #        movdqa 0x651180, %xmm2
0x66, 0x0f, 0x7f, 0xdd,                               #        movdqa %xmm3,    %xmm5
0x6a, 0x04,                                           #        pushl  $0x4
0x8f, 0xc1,                                           #        popl   %ecx
                                                      #        chacha8.loopA:
0xe8, 0x59, 0x00, 0x00, 0x00,                         #                call   chacharound
0x66, 0x0f, 0x70, 0xc9, 0x93,                         #                pshufd $0x93, %xmm1, %xmm1
0x66, 0x0f, 0x70, 0xd2, 0x4e,                         #                pshufd $0x4e, %xmm2, %xmm2
0x66, 0x0f, 0x70, 0xdb, 0x39,                         #                pshufd $0x39, %xmm3, %xmm3
0xe8, 0x45, 0x00, 0x00, 0x00,                         #                call   chacharound
0x66, 0x0f, 0x70, 0xc9, 0x39,                         #                pshufd $0x39, %xmm1, %xmm1
0x66, 0x0f, 0x70, 0xd2, 0x4e,                         #                pshufd $0x4e, %xmm2, %xmm2
0x66, 0x0f, 0x70, 0xdb, 0x93,                         #                pshufd $0x93, %xmm3, %xmm3
0xe2, 0xd6,                                           #        loop   chacha8.loopA
0x66, 0x0f, 0xfe, 0x04, 0x25, 0x60, 0x11, 0x65, 0x00, #        paddd  0x651160,   %xmm0
0x66, 0x0f, 0xfe, 0x0c, 0x25, 0x70, 0x11, 0x65, 0x00, #        paddd  0x651170,   %xmm1
0x66, 0x0f, 0xfe, 0x14, 0x25, 0x80, 0x11, 0x65, 0x00, #        paddd  0x651180,   %xmm2
0x66, 0x0f, 0xfe, 0xdd,                               #        paddd  %xmm5,      %xmm3
0x66, 0x0f, 0x7f, 0x42, 0x10,                         #        movdqa %xmm0, 0x10(%edx)
0x66, 0x0f, 0x7f, 0x4a, 0x20,                         #        movdqa %xmm1, 0x20(%edx)
0x66, 0x0f, 0x7f, 0x52, 0x30,                         #        movdqa %xmm2, 0x30(%edx)
0x66, 0x0f, 0x7f, 0x5a, 0x40,                         #        movdqa %xmm3, 0x40(%edx)
0xc3,                                                 #        retl

                                                      #chacharound:
0x66, 0x0f, 0xfe, 0xc1,                               #        paddd   %xmm1, %xmm0
0x66, 0x0f, 0xef, 0xd8,                               #        pxor    %xmm0, %xmm3
0xf3, 0x0f, 0x70, 0xdb, 0xb1,                         #        pshufhw $0xb1, %xmm3, %xmm3
0xf2, 0x0f, 0x70, 0xdb, 0xb1,                         #        pshuflw $0xb1, %xmm3, %xmm3
0x66, 0x0f, 0xfe, 0xd3,                               #        paddd   %xmm3, %xmm2
0x66, 0x0f, 0xef, 0xca,                               #        pxor    %xmm2, %xmm1
0x66, 0x0f, 0x7f, 0xcc,                               #        movdqa  %xmm1, %xmm4
0x66, 0x0f, 0x72, 0xf1, 0x0c,                         #        pslld   $12,   %xmm1
0x66, 0x0f, 0x72, 0xd4, 0x14,                         #        psrld   $20,   %xmm4
0x66, 0x0f, 0xeb, 0xcc,                               #        por     %xmm4, %xmm1
0x66, 0x0f, 0xfe, 0xc1,                               #        paddd   %xmm1, %xmm0
0x66, 0x0f, 0xef, 0xd8,                               #        pxor    %xmm0, %xmm3
0x66, 0x0f, 0x7f, 0xdc,                               #        movdqa  %xmm3, %xmm4
0x66, 0x0f, 0x72, 0xf3, 0x08,                         #        pslld   $8,    %xmm3
0x66, 0x0f, 0x72, 0xd4, 0x18,                         #        psrld   $24,   %xmm4
0x66, 0x0f, 0xeb, 0xdc,                               #        por     %xmm4, %xmm3
0x66, 0x0f, 0xfe, 0xd3,                               #        paddd   %xmm3, %xmm2
0x66, 0x0f, 0xef, 0xca,                               #        pxor    %xmm2, %xmm1
0x66, 0x0f, 0x7f, 0xcc,                               #        movdqa  %xmm1, %xmm4
0x66, 0x0f, 0x72, 0xf1, 0x07,                         #        pslld   $7,    %xmm1
0x66, 0x0f, 0x72, 0xd4, 0x19,                         #        psrld   $25,   %xmm4
0x66, 0x0f, 0xeb, 0xcc,                               #        por     %xmm4, %xmm1
0xc3                                                  #        retl
], 0x651edc)



#seeded rng stuff

WriteMemory("unsigned char",[
0xd1, 0xe0,            #shll $1, %eax
0xf7, 0x64, 0x24, 0x04 #mull 0x4(%esp)
], 0x5a9a45)

WriteMemory("unsigned char", [
                                          #rng_raw:
0x6a, 0x04,                               #        pushl $0x4
0xeb, 0x06,                               #        jmp   rng
                                          #rng_int:
0x6a, 0x04,                               #        pushl $0x4
0xeb, 0x02,                               #        jmp   rng
                                          #rng_flt:
0x6a, 0x18,                               #        pushl $0x18
                                          #rng:
0x58,                                     #        popl  %eax
0x8b, 0x04, 0x04,                         #        movl (%esp,%eax), %eax

0x3d, 0x56, 0x9a, 0x5a, 0x00,             #        cmpl $0x5a9a56,   %eax
0x75, 0x04,                               #        jne  rng.locG
0x8b, 0x44, 0x24, 0x0c,                   #                movl 0xc(%esp), %eax
                                          #        rng.locG:

0x3d, 0x40, 0x15, 0x51, 0x00,             #        cmpl $0x511540,   %eax
0x75, 0x04,                               #        jne  rng.locA
0x8b, 0x44, 0x24, 0x14,                   #                movl 0x14(%esp),  %eax
                                          #        rng.locA:

0x3d, 0x90, 0x15, 0x51, 0x00,             #        cmpl $0x511590,   %eax
0x75, 0x04,                               #        jne  rng.locB
0x8b, 0x44, 0x24, 0x14,                   #                movl 0x14(%esp),  %eax
                                          #        rng.locB:

0x3d, 0xc9, 0x1c, 0x51, 0x00,             #        cmpl $0x511cc9,   %eax
0x75, 0x04,                               #        jne  rng.locC
0x8b, 0x44, 0x24, 0x20,                   #                movl 0x20(%esp), %eax
                                          #        rng.locC:

0x3d, 0xad, 0xce, 0x41, 0x00,             #        cmpl $0x41cead,   %eax
0x75, 0x04,                               #        jne  rng.locD
0x03, 0x44, 0x24, 0x2c,                   #                addl 0x2c(%esp), %eax #this should add the zombie weight to the coin rng RA
                                          #        rng.locD:

0x3d, 0x20, 0x02, 0x53, 0x00,             #        cmpl $0x530220,   %eax
0x75, 0x02,                               #        jne  rng.locH
0x03, 0xc6,                               #                addl %esi, %eax #this should add the zombie weight to the BTLZ 1/4 coin chance RA
                                          #        rng.locH:

0xba, 0xff, 0x03, 0x00, 0x00,             #        movl $0x3ff,            %edx
0x21, 0xc2,                               #        andl %eax,              %edx
0x8b, 0x0c, 0x95, 0x00, 0x00, 0x00, 0x00, #        movl 0x??????(,%edx,4), %ecx #patch +0x10 at +0x58

0xe3, 0x2a,                               #        jecxz rng.locF
                                          #        rng.loopA:
0x39, 0x01,                               #                cmpl %eax,    (%ecx)
0x74, 0x07,                               #                je   rng.exloopA
0x8b, 0x49, 0x0c,                         #                movl 0xc(%ecx), %ecx
0xe3, 0x21,                               #                jecxz rng.locF
0xeb, 0xf5,                               #        jmp rng.loopA
                                          #        rng.exloopA:

0x8b, 0x51, 0x04,                         #        movl  0x4(%ecx), %edx
0xff, 0xca,                               #        decl  %edx
0x79, 0x0e,                               #        jns   rng.locE
0x89, 0xca,                               #                movl %ecx, %edx
0xe8, 0x3f, 0x00, 0x00, 0x00,             #                call chacha8
0x8b, 0xca,                               #                movl %edx, %ecx
0xba, 0x0f, 0x00, 0x00, 0x00,             #                movl $0xf, %edx
                                          #        rng.locE:
0x89, 0x51, 0x04,                         #        movl  %edx,         0x4(%ecx)
0x8b, 0x44, 0x91, 0x10,                   #        movl  0x10(%ecx,%edx,4), %eax
0xd1, 0xe8,                               #        shrl  $0x1,              %edx
0xc3,                                     #        retl

                                          #        rng.locF:
0x50,                                     #        pushl %eax
0x8b, 0x0c, 0x25, 0x5c, 0x11, 0x65, 0x00, #        movl  0x??????,          %ecx #patch at +0x8c
0x8d, 0x41, 0x50,                         #        leal  0x50(%ecx),        %eax
0xa3, 0x5c, 0x11, 0x65, 0x00,             #        movl  %eax,          0x?????? #patch at +0x94
0x8b, 0x04, 0x95, 0x00, 0x00, 0x00, 0x00, #        movl  0x??????(,%edx,4), %eax #patch +0x10 at +0x9b
0x89, 0x0c, 0x95, 0x00, 0x00, 0x00, 0x00, #        movl  %ecx, 0x??????(,%edx,4) #patch +0x10 at +0xa2
0x89, 0x41, 0x0c,                         #        movl  %eax,         0xc(%ecx)
0x31, 0xc0,                               #        xorl  %eax,              %eax
0x89, 0x41, 0x08,                         #        movl  %eax,         0x8(%ecx)
0x89, 0x41, 0x04,                         #        movl  %eax,         0x4(%ecx)
0x58,                                     #        popl  %eax
0x89, 0x01,                               #        movl  %eax,         0xc(%ecx)
0xeb, 0xb3                                #        jmp   rng.exloopA
], 0x651e26)
if seeded:
    if LINUX:
        rng_addr = 0x200000
    else:
        rng_addr = VirtualAllocEx(pvz_handle, None, 0x30000, 0x1000, 0x40)
        atexit.register(dealloc_rngmem)
    WriteMemory("int", 0x651e26-0x5a993a, 0x5a9936) #raw rng
    WriteMemory("int", 0x651e2a-0x5a9a45, 0x5a9a41) #int rng
    WriteMemory("int", 0x651e2e-0x5a9a6b, 0x5a9a67) #flt rng
    WriteMemory("int", rng_addr+0x10, 0x651e26+0x58)
    WriteMemory("int", rng_addr,      0x651e26+0x8c)
    WriteMemory("int", rng_addr,      0x651e26+0x94)
    WriteMemory("int", rng_addr+0x10, 0x651e26+0x9b)
    WriteMemory("int", rng_addr+0x10, 0x651e26+0xa2)



#Show correct seed packet in level transition

WriteMemory("unsigned char", [
0x75, 0x29,                               #jne   0x431804 <.text+0x30804>
0x8b, 0x80, 0x2c, 0x08, 0x00, 0x00,       #movl  0x82c(%eax), %eax
0x85, 0xc0,                               #testl %eax, %eax
0x74, 0x06,                               #je    0x4317eb <.text+0x307eb>
0x83, 0x78, 0x2c, 0x00,                   #cmpl  $0x0, 0x2c(%eax)
0x7f, 0x19,                               #jg    0x431804 <.text+0x30804>
0x8b, 0x41, 0x04,                         #movl  0x4(%ecx), %eax
0x85, 0xc0,                               #testl %eax, %eax
0x74, 0x12,                               #je    0x431804 <.text+0x30804>
0x8b, 0x80, 0x50, 0x55, 0x00, 0x00,       #movl  0x5550(%eax), %eax
0x83, 0xf8, 0x32,                         #cmpl  $0x32, %eax
0x7f, 0x07,                               #jg    0x431804 <.text+0x30804>
0xa1, 0x5c, 0x11, 0x65, 0x00,             #movl  0x65115c, %eax
0xeb, 0x04,                               #jmp   0x431808 <.text+0x30808>
0x83, 0xc8, 0xff,                         #orl   $-0x1, %eax
0xc3,                                     #retl
0x8b, 0x04, 0x85, 0x94, 0x11, 0x65, 0x00, #movl 0x651194(,%eax,4), %eax
0xc3                                      #retl
], 0x4317d9)
for i in [0x52ffe2, 0x52ffeb, 0x52fff4, 0x52fff9, 0x52fffe, 0x530037, 0x530046, 0x530055, 0x530064]:
    WriteMemory("unsigned char", 0x00, i)


#I haven't been bothered to label these yet

WriteMemory("unsigned char", [
0xeb, 0x6f, #jmp  0x484471
0x90        #nop
], 0x484400)
WriteMemory("unsigned char", [
0x8b, 0x0c, 0x8d, 0x98, 0x10, 0x65, 0x00, #movl 0x651098(,%ecx,4), %ecx
0x83, 0xf9, 0x30,                         #cmpl $0x30,             %ecx
0xeb, 0x85                                #jmp  0x484402
], 0x484471)

WriteMemory("int",0x07e27c-0x7,0x40b8d0) #call 0x489b49
WriteMemory("unsigned char", [
0x8b, 0x3c, 0xbd, 0x98, 0x10, 0x65, 0x00, #movl 0x651098(,%edi,4), %edi
], 0x489b49)

WriteMemory("unsigned char", [
0xeb, 0x0b,                   #jmp  0x40bdf8
0x3d, 0x01, 0x00, 0x00, 0x00, #cmpl $0x1,      %eax #used to be 6
0x7f, 0xe8,                   #jg   0x40bddc
0x32, 0xc0,                   #xorb %al,        %al
0x5e,                         #popl %esi
0xc3,                         #retl
0xa1, 0x90, 0x10, 0x65, 0x00, #movl 0x651090, %eax
0xeb, 0xee                    #jmp  0x40bded
], 0x40bdeb)

plants_unlocked = 1
WriteMemory("int", plants_array, 0x651094)
WriteMemory("int", plants_array2, 0x651194)
WriteMemory("int",0,0x65115c)

for i in range(50):
    WriteMemory("int",plants_unlocked,0x651090)
    if seeded:
        WriteMemory("int", [0 for j in range(1024)], rng_addr+0x10)
        WriteMemory("int", rng_addr+0x1010, rng_addr)
    newlevel=levels[i]
    if(i == 0):
        try:
            while(ReadMemory("int",0x6A9EC0,0x82C, 0x24) != 1): # current level
                Sleep(0.1)
        except:
            print("oops")
    if not noAutoSlots or shopless:
        WriteMemory("int",0,0x6A9EC0,0x82C, 0x28)
    if imitater and i != 0:
        WriteMemory("bool",True,0x6A9EC0,0x82C,0x1E0)
        WriteMemory("int", 0, 0x453aea)
    WriteMemory("int",newlevel,0x6A9EC0,0x82C, 0x24)
    if seeded:
        WriteMemory("int",newlevel,0x651190)
    if not shopless:
        WriteMemory("bool",True,0x6A9EC0,0x82C,0x21C)
        WriteMemory("bool",True,0x6A9EC0,0x82C,0x218)
    if(i != 0): 
        WriteMemory("int",newlevel-1,0x6A9EC0,0x768, 0x5550)
    if(level_plants[newlevel] != -1):
        plants_unlocked += 1
    #if(newlevel >= 44): # gloom shroom
        #WriteMemory("bool",True,0x6A9EC0,0x82C,0x1C8)
    #else:
        #WriteMemory("bool",False,0x6A9EC0,0x82C,0x1C8)
    if(i >= 24 and plants_unlocked > 7 and not (shopless or noAutoSlots)): # slots
        WriteMemory("int",2,0x6A9EC0,0x82C,0x214)
    elif(i >= 14 and plants_unlocked > 6 and not (shopless or noAutoSlots)):
        WriteMemory("int",1,0x6A9EC0,0x82C,0x214)
    if(i == 0):
        while(game_ui() != 3):
            Sleep(0.1)
    Sleep(500)
    if not noAutoSlots or shopless:
        WriteMemory("int",0,0x6A9EC0,0x82C, 0x28)
    Sleep(500)
    if not noAutoSlots or shopless:
        WriteMemory("int",0,0x6A9EC0,0x82C, 0x28)
    while(game_ui() != 3 or ReadMemory("bool",0x6A9EC0,0x768, 0x5603)):
        Sleep(0.1)
    WriteMemory("int",i,0x65115c)

while True:
    Sleep(10)
    WriteMemory("bool",True,0x6A9EC0,0x82C,0x21C)
