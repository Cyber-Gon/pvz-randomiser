from   tkinter import *
from   tkinter import ttk
import platform
import math
import abc
import copy
from dataclasses import dataclass
from inspect import signature
from statistics import mean, median
from idlelib.tooltip import Hovertip
import atexit
import os

try:
    if platform.system() == "Windows":
        WINDOWS = True
        LINUX   = False
        
        from   pvz import *
        from   pvz.extra import *
        
        def dealloc_rngmem():
            WriteMemory("unsigned int", 0x00000006, 0x5a9936) #raw rng
            WriteMemory("unsigned int", 0xfffffefb, 0x5a9a41) #int rng
            WriteMemory("unsigned int", 0xfffffed5, 0x5a9a67) #flt rng
            try:
                VirtualFreeEx(pvz_handle, rng_addr, 0, 0x8000)
            except:
                print("Could not deallocate rng memory")
    else:
        LINUX   = True
        WINDOWS = False

        class MockMemoryLock:
            def acquire():
                pass
            def release():
                pass
        memory_lock = MockMemoryLock()

        import ctypes
        import struct
        import time
        from os import listdir
        libc = ctypes.CDLL("libc.so.6", use_errno=True)
        
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
        
        def ReadMemory(data_type, *address, array=1):  # most of this is stolen from pvzscripts
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
        
        def WriteMemory(data_type, values, *address):  # most of this is stolen from pvzscripts too
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
    
try:
    saveFile=open('saveFile.txt', 'r')
except:
    saveFile=open('saveFile.txt', 'w')
    saveFile.close()
    saveFile=open('saveFile.txt', 'r')
hasSave=False
fileInfo=saveFile.readlines()
if len(fileInfo)>0:
    hasSave=True
saveFile.close()
savePoint=-5

window=Tk() #Creates a window object from the Tk class
window.title("Randomiser settings")
challengeMode    = BooleanVar(value=False)
shopless         = BooleanVar(value=False)
noRestrictions   = BooleanVar(value=False)
noAutoSlots      = BooleanVar(value=True) # enabled by default
imitater         = BooleanVar(value=False)
randomisePlants  = BooleanVar(value=True) # enabled by default
seeded           = BooleanVar(value=False)
upgradeRewards   = BooleanVar(value=True) # enabled by default
randomWeights    = BooleanVar(value=False)
renderWeights    = BooleanVar(value=False)
randomWavePoints = StringVar(value="False")
renderWavePoints = BooleanVar(value=False)
saved            = BooleanVar(value=False)
startingWave     = StringVar(value="False")
randomCost       = BooleanVar(value=False)
randomCooldowns  = BooleanVar(value=False)
costTextToggle   = BooleanVar(value=False)
cooldownColoring = StringVar(value="False")
randomZombies    = BooleanVar(value=False)
randomConveyors  = StringVar(value="False")
enableDave       = StringVar(value="False")
davePlantsCount  = StringVar(value="3")
randomVarsCatZombieHealth = StringVar(value="Off")
randomVarsCatFireRate = StringVar(value="Off")
limitPreviews    = BooleanVar(value=False)
gamemode         = StringVar(value="adventure")
randomWaveCount  = StringVar(value="False")
randomWorld      = BooleanVar(value=False)
randomWorldChance= IntVar(value=33)
randomShit       = BooleanVar(value=False)
randomSound      = BooleanVar(value=False)
randomSoundChance= IntVar(value=3)

seed=str(random.randint(1,999999999999))

if hasSave:
    if len(fileInfo)<21:
        fileInfo.append("False") # cooldownColoring
    if len(fileInfo)<22:
        fileInfo.append("False") # enableDave
    if len(fileInfo)<23:
        fileInfo.append("3") #davePlantsCount
    if len(fileInfo)<24:
        fileInfo.append("Off") #randomVarsCatZombieHealth
    if len(fileInfo)<25:
        fileInfo.append("Off") #randomVarsCatFireRate
    if len(fileInfo)<26:
        fileInfo.append("False") #renderWeights
    if len(fileInfo)<27:
        fileInfo.append("False") #renderWavePoints
    if len(fileInfo)<28:
        fileInfo.append("False") #limitPreviews
    if len(fileInfo)<29:
        fileInfo.append("adventure") #gamemode
    if len(fileInfo)<30:
        fileInfo.append("False") #randomWavecount
    if len(fileInfo)<31:
        fileInfo.append("False") #randomWorld
    if len(fileInfo)<32:
        fileInfo.append("33") #randomWorldChance
    if len(fileInfo)<33:
        fileInfo.append("False") #randomShit
    if len(fileInfo)<34:
        fileInfo.append("False") #randomSound
    if len(fileInfo)<35:
        fileInfo.append("3") #randomSoundChance
    challengeMode.set(  eval(fileInfo[4].strip()))
    shopless.set(       eval(fileInfo[5].strip()))
    noRestrictions.set( eval(fileInfo[6].strip()))
    noAutoSlots.set(    eval(fileInfo[7].strip()))
    imitater.set(       eval(fileInfo[8].strip()))
    randomisePlants.set(eval(fileInfo[9].strip()))
    seeded.set(         eval(fileInfo[10].strip()))
    upgradeRewards.set( eval(fileInfo[11].strip()))
    randomWeights.set(  eval(fileInfo[12].strip()))
    randomWavePoints.set(    fileInfo[13].strip())
    startingWave.set(        fileInfo[14].strip())
    randomCost.set(     eval(fileInfo[15].strip()))
    randomCooldowns.set(eval(fileInfo[16].strip()))
    costTextToggle.set(eval(fileInfo[17].strip()))
    randomZombies.set(eval(fileInfo[18].strip()))
    randomConveyors.set(str(fileInfo[19].strip()))
    cooldownColoring.set(str(fileInfo[20].strip()))
    enableDave.set(str(fileInfo[21].strip()))
    davePlantsCount.set(str(fileInfo[22].strip()))
    randomVarsCatZombieHealth.set(str(fileInfo[23].strip()))
    randomVarsCatFireRate.set(str(fileInfo[24].strip()))
    renderWeights.set(str(fileInfo[25].strip()))
    renderWavePoints.set(str(fileInfo[26].strip()))
    limitPreviews.set(str(fileInfo[27].strip()) == "True")
    gamemode.set(str(fileInfo[28].strip()))
    randomWaveCount.set(str(fileInfo[29].strip()))
    randomWorld.set(str(fileInfo[30].strip()))
    randomWorldChance.set(int(fileInfo[31].strip()))
    randomShit.set(str(fileInfo[32].strip()) == "True")
    randomSound.set(str(fileInfo[33].strip()) == "True")
    randomSoundChance.set(int(fileInfo[34].strip()))
    if fileInfo[1]=="finished\n":
        hasSave=False

def clamp(n, smallest, largest): return max(smallest, min(n, largest))

def convertToNumber(level):
    if checkValidNumber(level):
        numberString=""
        if len(level)==4:
            numberString+=level[0]
        else:
            numberString+=str(int(level[0])-1)
        lastDigit=level[2]
        if len(level)==4:
            lastDigit="0"
        numberString+=lastDigit
        return int(numberString)

def checkValidNumber(level):
    check=True
    if len(level)!=3 and len(level)!=4:
        check=False
    elif level[0] not in ["1", "2", "3", "4", "5"]:
        check=False
    elif level[1]!="-":
        check=False
    elif level[2] not in ["1", "2", "3", "4", "5", "6", "7", "8", "9"]:
        check=False
    elif len(level)==4:
        if level[3]!="0":
            check=False
    if not check:
        print("Invalid jump level. Use the format x-y.")
    return check

def costButtonClick():
    global costTextToggle, randomCost, costTextButton
    if randomCost.get():
        costTextButton.config(state=NORMAL)
    else:
        costTextToggle.set(False)
        costTextButton.config(state=DISABLED)

def cooldownButtonClick():
    global cooldownColoringToggle, randomCooldowns
    if randomCooldowns.get():
        cooldownColoringToggle.config(state=NORMAL)
        cooldownColoringToggle.state(["readonly"])
    else:
        cooldownColoringToggle.config(state=DISABLED)


def randomWeightsButtonClick():
    if randomWeights.get():
        renderWeightsButton.config(state=NORMAL)
    else:
        renderWeights.set(False)
        renderWeightsButton.config(state=DISABLED)

def randomWavePointsChanged():
    randWavePointsButton.selection_clear()
    if randomWavePoints.get() != 'False':
        renderWavePointsButton.config(state=NORMAL)
    else:
        renderWavePoints.set(False)
        renderWavePointsButton.config(state=DISABLED)


def noRestrictionsButtonClick():
    if noRestrictions.get():
        challengeMode.set(True)
        challengeButton.config(state=DISABLED)
    else:
        challengeButton.config(state=NORMAL)

def shoplessButtonClick():
    if shopless.get():
        noAutoSlots.set(False)
        manualMoneyButton.config(state=DISABLED)
    else:
        manualMoneyButton.config(state=NORMAL)

def continueButtonClick():
    global seed, savePoint, jumpLevel
    seed=fileInfo[0].strip()
    savePoint=int(fileInfo[1].strip())
    WriteMemory("int", int(fileInfo[2].strip()), 0x6A9EC0,0x82C,0x214) #slots
    WriteMemory("int", int(fileInfo[3].strip()), 0x6A9EC0,0x82C,0x28) #money
    challengeMode.set(  eval(fileInfo[4].strip()))
    shopless.set(       eval(fileInfo[5].strip()))
    noRestrictions.set( eval(fileInfo[6].strip()))
    noAutoSlots.set(    eval(fileInfo[7].strip()))
    imitater.set(       eval(fileInfo[8].strip()))
    randomisePlants.set(eval(fileInfo[9].strip()))
    #seeded.set(         eval(fileInfo[10].strip()))
    seeded.set(False)
    upgradeRewards.set( eval(fileInfo[11].strip()))
    randomWeights.set(  eval(fileInfo[12].strip()))
    randomWavePoints.set(    fileInfo[13].strip())
    startingWave.set(        fileInfo[14].strip())
    randomCost.set(     eval(fileInfo[15].strip()))
    randomCooldowns.set(eval(fileInfo[16].strip()))
    costTextToggle.set(eval(fileInfo[17].strip()))
    randomZombies.set(eval(fileInfo[18].strip()))
    randomConveyors.set(str(fileInfo[19].strip()))
    cooldownColoring.set(str(fileInfo[20].strip()))
    enableDave.set(str(fileInfo[21].strip()))
    davePlantsCount.set(str(fileInfo[22].strip()))
    randomVarsCatZombieHealth.set(str(fileInfo[23].strip()))
    randomVarsCatFireRate.set(str(fileInfo[24].strip()))
    renderWeights.set(str(fileInfo[25].strip()))
    renderWavePoints.set(str(fileInfo[26].strip()))
    limitPreviews.set(str(fileInfo[27].strip()) == "True")
    gamemode.set(str(fileInfo[28].strip()))
    randomWaveCount.set(str(fileInfo[29].strip()))
    randomWorld.set(str(fileInfo[30].strip()))
    randomWorldChance.set(int(fileInfo[31].strip()))
    randomShit.set(str(fileInfo[32].strip()) == "True")
    randomSound.set(str(fileInfo[33].strip()) == "True")
    randomSoundChance.set(int(fileInfo[34].strip()))
    saved.set(True)
    jumpLevel=""
    window.destroy()
    

def AdventureClick():
    gamemode.set('adventure')
    getSeed()
    getLevel()
    window.destroy()

def MinigamesClick():
    gamemode.set('minigames')
    getSeed()
    getLevel()
    window.destroy()

def NgPlusClick():
    gamemode.set('ng+')
    getSeed()
    getLevel()
    window.destroy()


def informationButtonClick():
    outputText.delete(0.0, END)
    manipulatedText="Aaronthewinner made the original version that randomised the levels. BulbasaurRepresent created most of the logic, modifiers, and GUI. Vsoup.vx did most of the complex stuff, including making the seed select update to show the right plants. LunarBlessing added the tooltip for the random cooldowns, and made the starting cooldowns scale with their actual cooldowns. REALLY IMPORTANT: If you use either RANDOM WEIGHTS or RAND WAVE POINTS, and then you want to do another run WITHOUT those modifiers, close and reopen the game, otherwise things will be funky. Additionally, if you are continuing a saved run / jumping to a specific level, be aware that SEEDED mode does not work with it, and so is automatically disabled." + " "*spaces + "The jump level box allows you to jump to a specific level in the seed! This is great for recovering from a crash if you know your seed but for some reason the save file got corrupted. Just play 1-1 and then you should be at the same level (although with nothing bought from the shop)." + " "*spaces + "The Continue Last Run button only appears if you have an incomplete run in your save data. If you do, pressing this will close the settings menu and give you the same settings as before. After you play 1-1, you should be at the level you were previously at! You will also have the same plants, same money, and the same amount of slot upgrades. You will NOT save any other things bought from the shop (such as rakes or pre-unlocked upgrade plants)." + " "*spaces + "Challenge Mode gets rid of the tough level restriction. With this disabled, you will not be able to play certain levels (like 5-2) without having 3 good plants. Other levels (like 5-9) will need 5 good plants to play. With this enabled, as soon as you unlock flower pot, you can play both 5-2 and 5-9 (for instance)." + (" " * spaces) + "Shopless mode forces you to play with 6 slots and no automatic pool cleaners / roof cleaners." + (" " * spaces) + "No restrictions mode means that there is no logic as to what levels can be played next - the majority of no restrictions runs are impossible." + (" " * spaces) + "With manual money enabled, you do not get automatic slot upgrades, but your money does not reset to 0 after every level, and so you can purchase the slots yourself - this also means you can buy rakes and upgrade plants!" + (" " * spaces) + "Instant imitater mode gives you access to an imitater immediately, which allows you to choose one of any plant to bring to the stage, even if you haven't unlocked it! This works especially well with no restrictions." + (" " * spaces) + "Random plants means that the plant you get at the end of each level is RANDOMISED, in a similar way to the levels! Instead of unlocking the plant you usually unlock for beating that stage, you get a random one!" + (" " * spaces) + "Seeded means that the seed you enter will not only affect the random plants and levels you get, but also the zombie spawns and other types of RNG, which makes it perfect for races!" + (" " * spaces) + "Random upgrades means that most levels that would usually give you no reward instead gives you an upgrade plant! It is important to note that if you have 4 plants total and one upgrade plant, you will not have 4 seed slots - sorry about that." + (" " * spaces) + "Random Weights means that the likelihood for a zombie to spawn is a random number, and this changes from level to level. Cones might be extremely unlikely one level, and then extremely likely the next one!" + (" " * spaces) + "Random Wave Points has two modes: Normal and EXTREME. Normal mode means that a zombie's wave points can either stay the same, or increase/decrease by 1 wave point if they originally cost less than 5 wave points, 2 wave points if they originally cost 5-7 wave points, and 3 wave points if they originally cost 10 wave points. EXTREME mode means that a zombie's wave point value is a random number from 2 to 7 (or, in rare cases, 10). This changes from level to level, and the basic zombie always costs 1 wave point while the cone zombie always costs either 2 or 3 wave points. There is no guarantee that EXTREME mode is always possible. If you're using either randomised weights or randomised wave points, you can look at the program during the run to see a rundown of what weights and wave points each zombie type had!" + "" * spaces + "The starting wave refers to what wave the zombies can start spawning at. Usually, the day/night zombies can spawn in the first 10 waves while the other zombies cannot. Random mode means that each zombie (except for basics, cones, and newspapers) has a random starting wave from 4 to 10. Vaulters, buckets, and screen-doors have a random starting wave from 1 to 10. Instant mode means that every zombie can immediately spawn from wave 1 (provided there is enough wave points)." +" " * spaces + "Random costs will set the cost of almost every plant to 50-200% of the original price! The only exception is the sunflower (and the peashooter in 1-1)." + " "*spaces + "Coloured cost means that plants that cost less than they usually do will be green, and plants that cost more than usual will be blue!"+" "*spaces +"Random cooldowns will set the cooldown of almost every plant to 50-200% of the original cooldown! The only exceptions are sunflower, puff shroom, and flower pot. The redder the seed during seed select, the worse the cooldown!" + " "*spaces + "Random zombies means that each level can have random zombie show up! Each zombie (including zombotany zombies) has a 1/15 chance to either no longer appear / now appear on a level! Introduction stages will still always have their intro zombies." + " "*spaces + "Random conveyors has two modes - balanced and It's Raining Seeds mode. Balanced mode replaced high dps plants with other high dps plants, instas with other instas, etc. It's Raining Seeds mode creates a random list of 20 plants, and then each of them have the same chance of appearing on the conveyor (except for stuff like lilypads)." 
    outputText.insert(END, manipulatedText)

def getLevel():
    global jumpLevel, saved, seeded
    jumpLevel=jumpEntry.get()
    if jumpLevel!="":
        jumpLevel=convertToNumber(jumpLevel)
        if jumpLevel!="":
            savePoint=jumpLevel
            saved.set(True)
            seeded.set(False)

def getSeed():
    global seed
    seed=entry.get()
    if seed=="":
        seed=str(random.randint(1,999999999999))

#Create a label widget and assign it to a variable
label=Label(window, text="Enter seed: ")
label.grid(row=0, column=0, sticky=W) #Poistioning this widget (now in a variable) on the screen

jumpLabel=Label(window, text="Jump to level: ")
jumpLabel.grid(row=0, column=2, sticky=W)

jumpEntry=Entry(window, width=20, bg="light green")
jumpEntry.grid(row=0, column=3, sticky=W)
Hovertip(jumpEntry, "Allows you to go to the specified level immediately\nFormat is: 3-7 (world-level)\n"\
    "You should create a new save file, beat 1-1, and you will be moved to the specified level", 10)

if hasSave:
    continueButton=Button(window, text="CONTINUE LAST RUN", width=16, command=continueButtonClick)
    continueButton.grid(row=0, column=4, sticky=W)
    Hovertip(continueButton, "Continue last game - all your settings and run seed will be restored,\nYou don't need to input same settings.\n"\
        "You should create a new save file, beat 1-1, and you will be moved to the level you stopped at", 10)

spaces=150

#create a button widget (dear god this is unwieldy)
challengeButton=Checkbutton(window, text="CHALLENGE", width=16, variable=challengeMode, anchor="w")#command=challengeButtonClick)
challengeButton.grid(row=1, column=0, sticky=W)
Hovertip(challengeButton, "Makes level ordering harder - some default limitations are not enabled with this setting", 10)

shoplessButton=Checkbutton(window, text="SHOPLESS", width=16, variable=shopless, anchor="w", command=shoplessButtonClick)
shoplessButton.grid(row=3, column=0, sticky=W)
Hovertip(shoplessButton, "Not recommended. Disables shop - you won't get seed slots or upgrade plants", 10)

noRestrictionsButton=Checkbutton(window, text="NO RESTRICTIONS", width=16, variable=noRestrictions, anchor="w", command=noRestrictionsButtonClick)
noRestrictionsButton.grid(row=2, column=0, sticky=W)
Hovertip(noRestrictionsButton, "Removes all restrictions from level ordering, as well as some other modes.\n"\
    "You might require A LOT of attempts to beat the game with this setting", 10)

manualMoneyButton=Checkbutton(window, text="MANUAL MONEY", width=16, variable=noAutoSlots, anchor="w")#command=autoSlotsButtonClick)
manualMoneyButton.grid(row=3, column=3, sticky=W)
Hovertip(manualMoneyButton, "RECOMMENDED - you will buy items from shop yourself, including seed slots.\nWithout this, your money will disappear after every level", 10)

imitaterButton=Checkbutton(window, text="INSTANT IMITATER", width=16, variable=imitater, anchor="w")#command=imitaterButtonClick)
imitaterButton.grid(row=2, column=4, sticky=W)
Hovertip(imitaterButton, "The imitater is unlocked immediately on game start -\nand it allows you to pick any plant, even not yet unlocked ones.\n"\
    "You also get extra seed slot in the beginning of the game, so you can actually bring imitated plant", 10)

randPlantsButton=Checkbutton(window, text="RANDOM PLANTS", width=16, variable=randomisePlants, anchor="w")#command=randPlantsButtonClick)
randPlantsButton.grid(row=4, column=0, sticky=W)
Hovertip(randPlantsButton, "RECOMMENDED - you get random plant after beating each level, instead of the normal reward.", 10)

seededButton=Checkbutton(window, text="SEEDED", width=16, variable=seeded, anchor="w")#command=seededButtonClick)
seededButton.grid(row=1, column=4, sticky=W)
Hovertip(seededButton, "Enabled seeded RNG in game - things like zombie spawns will be seeded", 10)

upgradeButton=Checkbutton(window, text="UPGRADE REWARDS", width=16, variable=upgradeRewards, anchor="w")#command=upgradeButtonClick)
upgradeButton.grid(row=4, column=3, sticky=W)
Hovertip(upgradeButton, "RECOMMENDED - Some of level rewards, which are normally missing, might be changed to upgrade plants,\nso you don't need to buy them", 10)

soundButton=Checkbutton(window, text="RANDOM SOUNDS", width=16, variable=randomSound, anchor="w")#command=upgradeButtonClick)
soundButton.grid(row=5, column=3, sticky=W)
Hovertip(soundButton, "Changes some sounds randomly, also randomizes music", 10)

randomSoundSlider = Scale(window, from_=1, to=10, orient=HORIZONTAL, length=115, label="Random sound chance", variable=randomSoundChance)
randomSoundSlider.config(font=('Arial', 8))
randomSoundSlider.grid(row=6, column=3, sticky=W)

randWeightsButton=Checkbutton(window, text="RANDOM WEIGHTS", width=16, variable=randomWeights, anchor="w", command=randomWeightsButtonClick)
randWeightsButton.grid(row=1, column=1, sticky=W)
Hovertip(randWeightsButton, "Weights (the chance that game spawns particular type of zombie) are randomised,\n"\
    "so sometimes you might get a lot of zombies of specific type, or almost none at all", 10)

renderWeightsButton=Checkbutton(window, text="SHOW WEIGHT", width=16, variable=renderWeights, anchor="w")#command=randomWeightsButtonClick)
renderWeightsButton.grid(row=2, column=1, sticky=W)
if not randomWeights.get():
    renderWeightsButton.config(state=DISABLED)
Hovertip(renderWeightsButton, "The random weights of zombies are shown on their tooltip in seed selection screen", 10)

randWavePointsLabel=Label(window, text="RAND WAVE POINTS:")
randWavePointsLabel.grid(row=4, column=2, sticky=W)
randWavePointsButton=ttk.Combobox(window, text="RAND WAVE POINTS", width=16, textvariable=randomWavePoints)#command=randomWavePointsButtonClick)
randWavePointsButton["values"] = ["False", "Normal", "EXTREME"]
randWavePointsButton.state(["readonly"])
randWavePointsButton.bind('<<ComboboxSelected>>', lambda e: randomWavePointsChanged())
randWavePointsButton.grid(row=5, column=2, sticky=W)
Hovertip(randWavePointsButton, "How much does it \"cost\" the game to spawn particular types of zombies is randomized", 10)

renderWavePointsButton=Checkbutton(window, text="SHOW WAVEPOINTS", width=16, variable=renderWavePoints, anchor="w")#command=randomWeightsButtonClick)
renderWavePointsButton.grid(row=6, column=2, sticky=W)
if randomWavePoints.get == 'False':
    renderWavePointsButton.config(state=DISABLED)
Hovertip(renderWavePointsButton, "The random wave points of zombies are shown on their tooltip in seed selection screen", 10)

waveStartLabel=Label(window, text="STARTING WAVE:")
waveStartLabel.grid(row=1, column=3, sticky=W)
waveStartButton=ttk.Combobox(window, text="STARTING WAVE", width=16, textvariable=startingWave)#command=startingWaveButtonClick)
waveStartButton["values"] = ["False", "Random", "Instant"]
waveStartButton.state(["readonly"])
waveStartButton.bind('<<ComboboxSelected>>', lambda e: waveStartButton.selection_clear())
waveStartButton.grid(row=2, column=3, sticky=W)
Hovertip(waveStartButton, "Randomizes how early zombie types are allowed to spawn on every level.\nInstant means there are no limitations (except waves 1-3)", 10)

costButton=Checkbutton(window, text="RANDOM COST", width=16, variable=randomCost, anchor="w", command=costButtonClick)
costButton.grid(row=3, column=1, sticky=W)
Hovertip(costButton, "Sun cost of each plant is randomized", 10)

costTextButton=Checkbutton(window, text="COLOURED COST", width=16, variable=costTextToggle, anchor="w")#command=costTextButtonClick)
costTextButton.grid(row=4, column=1, sticky=W)
costTextButton.config(state=DISABLED)
Hovertip(costTextButton, "Sun cost will be colored accordingly to how much it has changed", 10)

cooldownButton=Checkbutton(window, text="RAND COOLDOWNS", width=16, variable=randomCooldowns, anchor="w", command=cooldownButtonClick)
cooldownButton.grid(row=1, column=2, sticky=W)
Hovertip(cooldownButton, "Cooldown of each plant is randomized", 10)

cooldownColoringLabel=Label(window, text="COOLDOWN SEED COLORS:")
cooldownColoringLabel.grid(row=2, column=2, sticky=W)
cooldownColoringToggle=ttk.Combobox(window, text="COOLDOWN SEED COLORS", width=16, textvariable=cooldownColoring)
cooldownColoringToggle["values"] = ["False", "Selection only", "Always on"]
cooldownColoringToggle.state(["readonly"])
cooldownColoringToggle.bind('<<ComboboxSelected>>', lambda e: cooldownColoringToggle.selection_clear())
cooldownColoringToggle.grid(row=3, column=2, sticky=W)
if not randomCooldowns.get():
    cooldownColoringToggle.config(state=DISABLED)
Hovertip(cooldownColoringToggle, "Seed packets will be colored depending on how bad their cooldown is,\ncompared to original", 10)

zombiesButton=Checkbutton(window, text="RANDOM ZOMBIES", width=16, variable=randomZombies, anchor="w")#command=cooldownButtonClick)
zombiesButton.grid(row=3, column=4, sticky=W)
Hovertip(zombiesButton, "Adds or removes random zombie types from each level", 10)

limitPreviewsButton=Checkbutton(window, text="LIMIT PREVIEWS", width=16, variable=limitPreviews, anchor="w")#command=cooldownButtonClick)
limitPreviewsButton.grid(row=4, column=4, sticky=W)
Hovertip(limitPreviewsButton, "Limits each zombie type to appear only once on level preview,\nso you have no idea how many there are of each type", 10)

##zombiesButton=Checkbutton(window, text="RANDOM CONVEYORS", width=16, variable=randomConveyors, anchor="w")#command=cooldownButtonClick)
##zombiesButton.grid(row=4, column=4, sticky=W)

conveyorLabel=Label(window, text="RANDOM CONVEYORS:")
conveyorLabel.grid(row=1, column=5, sticky=W)
conveyorButton=ttk.Combobox(window, text="RANDOM CONVEYORS", width=16, textvariable=randomConveyors )#command=randomConveyorButtonClick)
conveyorButton["values"] = ["False", "Balanced", "It's Raining Seeds"]
conveyorButton.state(["readonly"])
conveyorButton.bind('<<ComboboxSelected>>', lambda e: conveyorButton.selection_clear())
conveyorButton.grid(row=2, column=5, sticky=W)
Hovertip(conveyorButton, "Changes available plants in conveyor levels.\n It's raining seeds means there are almost no limits to what plant you can get", 10)

enableDaveLabel=Label(window, text="CRAZY DAVE:")
enableDaveLabel.grid(row=3, column=5, sticky=W)
enableDaveButton=ttk.Combobox(window, text="CRAZY DAVE", width=16, textvariable=enableDave)
enableDaveButton["values"] = ["False", "On", "On + plant upgrades"]
enableDaveButton.state(["readonly"])
enableDaveButton.bind('<<ComboboxSelected>>', lambda e: enableDaveChanged(enableDaveButton))
enableDaveButton.grid(row=4, column=5, sticky=W)
Hovertip(enableDaveButton, "Makes Crazy Dave pick some plants for you", 10)

randomWavecountLabel=Label(window, text="RANDOM LEVEL LENGTH:")
randomWavecountLabel.grid(row=1, column=6, sticky=W)
randomWavecountButton=ttk.Combobox(window, text="RANDOM LEVEL LENGTH:", width=16, textvariable=randomWaveCount)
randomWavecountButton["values"] = ["False", "Flag count only", "On"]
randomWavecountButton.state(["readonly"])
randomWavecountButton.bind('<<ComboboxSelected>>', lambda e: randomWavecountButton.selection_clear())
randomWavecountButton.grid(row=2, column=6, sticky=W)
Hovertip(randomWavecountButton, """Randomizes the amount of zombie waves on most of levels;
"Flag count only" means that every flag is still 10 waves long, but the amount of flags is random;
"On" means that both flag count and waves per flag is randomized.
Works only in adventure mode.""", 10)

randomWorldButton=Checkbutton(window, text="RANDOM WORLD", width=16, variable=randomWorld, anchor="w")
randomWorldButton.grid(row=3, column=6, sticky=W)
Hovertip(randomWorldButton, "Randomizes world (day, night, pool, fog, roof) for most levels, doesn't work for minigames mode", 10)

randomWorldSlider = Scale(window, from_=0, to=100, orient=HORIZONTAL, length=115, label="Random world chance", variable=randomWorldChance)
randomWorldSlider.config(font=('Arial', 8))
randomWorldSlider.grid(row=4, column=6, sticky=W)

randomShitButton=Checkbutton(window, text="RANDOM STUFF", width=16, variable=randomShit, anchor="w")
randomShitButton.grid(row=6, column=6, sticky=W)
Hovertip(randomShitButton, "Random stuff", 10)

daveAmountLabel=Label(window, text="DAVE PLANTS COUNT:")
daveAmountLabel.grid(row=5, column=5, sticky=W)
daveAmountButton=ttk.Combobox(window, text="DAVE PLANTS COUNT", width=16, textvariable=davePlantsCount )
daveAmountButton["values"] = ["1", "2", "3", "4", "5", "random(1-5)"]
daveAmountButton.state(["readonly"])
daveAmountButton.bind('<<ComboboxSelected>>', lambda e: daveAmountButton.selection_clear())
daveAmountButton.grid(row=6, column=5, sticky=W)
if (enableDave.get() == 'False'):
    daveAmountButton.config(state=DISABLED)
Hovertip(daveAmountButton, "How many plants Dave picks every level. Random means it will be random amount every level", 10)

def enableDaveChanged(button):
    global daveAmountButton, enableDave
    if enableDave.get() != 'False':
        daveAmountButton.config(state=NORMAL)
        daveAmountButton.state(["readonly"])
    else:
        daveAmountButton.config(state=DISABLED)
    button.selection_clear()

randomVarsCatZombieHealthLabel=Label(window, text="ZOMBIE HEALTH RANDO:")
randomVarsCatZombieHealthLabel.grid(row=5, column=0, sticky=W)
randomVarsCatZombieHealthButton=ttk.Combobox(window, text="ZOMBIE HEALTH", width=16, textvariable=randomVarsCatZombieHealth )#command=randomConveyorButtonClick)
randomVarsCatZombieHealthButton["values"] = ["Off", "Very weak", "Weak", "Average", "Strong", "Very Strong"] # how strong randomness is
randomVarsCatZombieHealthButton.state(["readonly"])
randomVarsCatZombieHealthButton.bind('<<ComboboxSelected>>', lambda e: randomVarsCatZombieHealthButton.selection_clear())
randomVarsCatZombieHealthButton.grid(row=6, column=0, sticky=W)
Hovertip(randomVarsCatZombieHealthButton, "Random Zombie health - options change how strong and often healths are randomized.", 10)

randomVarsCatFireRateLabel=Label(window, text="FIRE RATE RANDO:")
randomVarsCatFireRateLabel.grid(row=5, column=1, sticky=W)
randomVarsCatFireRateButton=ttk.Combobox(window, text="FIRE RATE RANDO", width=16, textvariable=randomVarsCatFireRate )#command=randomConveyorButtonClick)
randomVarsCatFireRateButton["values"] = ["Off", "Very weak", "Weak", "Average", "Strong", "Very Strong"] # how strong randomness is
randomVarsCatFireRateButton.state(["readonly"])
randomVarsCatFireRateButton.bind('<<ComboboxSelected>>', lambda e: randomVarsCatFireRateButton.selection_clear())
randomVarsCatFireRateButton.grid(row=6, column=1, sticky=W)
Hovertip(randomVarsCatFireRateButton, "Plant Random Fire rates - options change how strong and often fire rates are randomized.", 10)

# closeButton=Button(window, text="SUBMIT SETTINGS", width=16, command=closeButtonClick)
# closeButton.grid(row=0, column=6, sticky=W)
# Hovertip(closeButton, "Begin the game - press this, and go beat 1-1.", 10)

adventureButton=Button(window, text="ADVENTURE", width=16, command=AdventureClick)
adventureButton.grid(row=2, column=7, sticky=W)
Hovertip(adventureButton, "Create a new profile in game, press this, and go beat 1-1 to get going", 10)

minigamesButton=Button(window, text="MINI-GAMES \n+ SURVIVALS", width=16, command=MinigamesClick)
minigamesButton.grid(row=4, column=7, sticky=W)
Hovertip(minigamesButton, "Create a new profile in game, press this, then open 'help' menu in game to refresh, and go play", 10)

ngPlusButton=Button(window, text="NEW GAME+", width=16, command=NgPlusClick)
ngPlusButton.grid(row=6, column=7, sticky=W)
Hovertip(ngPlusButton, "Create a new profile in game, press this, and go play seconds adventure", 10)

informationButton=Button(window, text="INFORMATION", width=16, command=informationButtonClick)
informationButton.grid(row=0, column=7, sticky=W)

#creates an entry widget, assigning it to a variable
entry=Entry(window, width=20, bg="light green")
entry.grid(row=0, column=1, sticky=W) #positioning this widget on the screen
Hovertip(entry, "Seed to use for randomiser and, if enabled, seeded mode.\nEvery playthrough on the same Randomiser version "\
    "with the same settings and\nwith the same seed will produce same randomisation", 10)

#create a text box widget
outputText=Text(window, width=120, height=15, wrap=WORD, background="yellow")
outputText.grid(row=7, column=0, columnspan=10, sticky=W)
outputText.insert(END, "How to play:\nCreate a new save file in game (don't start 1-1 yet).\nChoose settings.\nPress one of game modes buttons on the right.\n"
                  +"If you start adventure, beat 1-1 and then randomization will be on.\nIf you start minigames+survivals, you have to update interface"
                  +" (press \"Help\" in main menu for example) and then you can play mini-games or survivals in any order.\n"
                  +"If you choose new game+, you do it the same as normal adventure mode.\n It's not recommended to play different mode other than selected one."
                  +"\nIf you change settings between different playthrough, you should restart the game.")

if randomCost.get():
    costTextButton.config(state=NORMAL)
if noRestrictions.get():
    challengeButton.config(state=DISABLED)
if shopless.get():
    manualMoneyButton.config(state=DISABLED)
    

window.mainloop() #Run the event loop
print(seed)
print("Game mode:",          str(gamemode.get()))
print("Challenge Mode:",     str(challengeMode.get()))
print("Shopless:",           str(shopless.get()))
print("No Restrictions:",    str(noRestrictions.get()))
print("Manual Money:",       str(noAutoSlots.get()))
print("Instant Imitater:",   str(imitater.get()))
print("Random Plants:",      str(randomisePlants.get()))
print("Seeded:",             str(seeded.get()))
print("Upgrade Rewards:",    str(upgradeRewards.get()))
print("Random Weights:",     str(randomWeights.get()))
print("Show Random Weights:",str(renderWeights.get()))
print("Random Wave Points:", str(randomWavePoints.get()))
print("Show Random Wave Points:", str(renderWavePoints.get()))
print("Starting Wave:",          startingWave.get())
print("Random Cost:",        str(randomCost.get()))
print("Coloured Cost:",      str(costTextToggle.get()))
print("Random Cooldowns:",   str(randomCooldowns.get()))
print("Cooldown seed coloring:",   str(cooldownColoring.get()))
print("Random Zombies:",     str(randomZombies.get()))
print("Limited Previews:",   str(limitPreviews.get()))
print("Random Conveyors:",   str(randomConveyors.get()))
print("Crazy Dave:",         str(enableDave.get()))
print("Dave Plants Count:",  str(davePlantsCount.get()))
print("Zombie Health Random:",str(randomVarsCatZombieHealth.get()))
print("Fire Rate Random:",   str(randomVarsCatFireRate.get()))
print("Random Level Length:",str(randomWaveCount.get()))
print("Random Worlds:",      str(randomWorld.get()))
print("Random World Chance:",str(randomWorldChance.get()))
print("Random Stuff:",       str(randomShit.get()))
print("Random Sound:",       str(randomSound.get()))
print("Random Sound Chance:",str(randomSoundChance.get()))

def settings_lines_to_save():
    return [(challengeMode.get()), (shopless.get()), (noRestrictions.get()), (noAutoSlots.get()), (imitater.get()),
        (randomisePlants.get()), (seeded.get()), (upgradeRewards.get()), (randomWeights.get()),
        (randomWavePoints.get()), startingWave.get(), randomCost.get(), randomCooldowns.get(),
        costTextToggle.get(), randomZombies.get(), randomConveyors.get(), cooldownColoring.get(),
        enableDave.get(), davePlantsCount.get(), randomVarsCatZombieHealth.get(), randomVarsCatFireRate.get(),
        renderWeights.get(), renderWavePoints.get(), limitPreviews.get(), gamemode.get(), randomWaveCount.get(), randomWorld.get(),
        randomWorldChance.get(), randomShit.get(), randomSound.get(), randomSoundChance.get()]

linesToWrite=[seed, (i+1), str(ReadMemory("int", 0x6A9EC0,0x82C,0x214)), str(ReadMemory("int",0x6A9EC0,0x82C, 0x28)), *settings_lines_to_save()]
with open('saveFile.txt', 'w') as saveFile:
    for k in range(len(linesToWrite)):
        linesToWrite[k]=str(linesToWrite[k])+"\n"
    saveFile.writelines(linesToWrite)


######### RANDOM VARS SYSTEM ########
#region

FORMAT_ACTUAL_VALUE = 0
FORMAT_DELTA_CHANGE = 1
FORMAT_PERCENT_CHANGE = 2
FORMAT_PERCENT_OF_DEFAULT_VALUE = 3

class RandomVariable(abc.ABC):
    def __init__(self, name, address, chance, datatype, default, enabled_on_levels = None, multivar_functions=None, needs_reset=False):
        # default can always be a list
        if any(type(x) == list for x in [address, datatype]) and not all(type(x) == list for x in [address, datatype, default, multivar_functions]):
            raise TypeError(f'incompatible types of arguments in constructor for {name}')
        if any(type(x) == list for x in [address, datatype]) and \
        not all(x == len(address) for x in [len(address), len(datatype), len(default), len(multivar_functions) + 1]):
            raise ValueError(f'different list lengths in constructor of {name}')
        self.name = name
        self.address = address
        self.default = default
        self.chance = chance
        self.datatype = datatype
        self.value = copy.deepcopy(default)
        self.written_value = copy.deepcopy(default)
        self.enabled_on_levels = enabled_on_levels
        self.multivar_functions = multivar_functions
        if type(address) == list:
            self.multivar = True
            self.calculate_value = self.calculate_multivar_value
            self.write_value = self.write_multivar_value
        else:
            self.multivar = False
            self.calculate_value = self.get_randomized_value
            self.write_value = self.write_single_value
        self.needs_reset = needs_reset

    def can_be_enabled(self, level):
        if self.enabled_on_levels:
            return self.enabled_on_levels(level)
        return True
    
    def test(self, random: random.Random, chance, level):
        return random.randint(1, 100) <= chance
    
    @abc.abstractmethod
    def get_randomized_value(self, random: random.Random, level):
        pass

    def calculate_multivar_value(self, random: random.Random, level):
        main_value = self.get_randomized_value(random, level)
        values = [main_value]
        for f in self.multivar_functions:
            sig = signature(f)
            if len(sig.parameters) > 1: # deciding how many params to pass
                values.append(f(main_value, level))
            else:
                values.append(f(main_value))
        return values

    def write_single_value(self, address, value, datatype, WriteMemory, writing_defaults: bool):
        try:
            WriteMemory(datatype, value, address)
        except:
            print("error in write_single_value, name=" + str(self.name) + ", value=" + str(value))

    def write_multivar_value(self, addresses, values, datatypes, WriteMemory, writing_defaults: bool):
        order = reversed(range(len(addresses))) if writing_defaults else range(len(addresses))
        for i in order:
            try:
                WriteMemory(datatypes[i], values[i], addresses[i])
            except:
                print("error in write_multivar_value, name=" + str(self.name) + ", value=" + str(values[i]))

    def is_default(self):
        return self.default == self.value
    
    def reset_memory(self, WriteMemory):
        self.write_value(self.address, self.value, self.datatype, WriteMemory, True)

    def current_main_value(self):
        return self.value[0] if self.multivar else self.value
    
    def get_value_str(self, format_type, val, default):
        if (type(val) != float and type(val) != int) or (type(default) != int and type(default) != float):
            print(f"{self.name} get_value_str error: {val}, {default}")
            return f"{self.name} get_value_str error: {val}, {default}"
        if type(val) == float and format_type in [FORMAT_ACTUAL_VALUE, FORMAT_DELTA_CHANGE]:
            if format_type == FORMAT_ACTUAL_VALUE:
                return "{:.1f}".format(abs(val))
            elif format_type == FORMAT_DELTA_CHANGE:
                return "{:.1f}".format(abs(val - default))
        elif format_type == FORMAT_ACTUAL_VALUE:
            return str(abs(val))
        elif format_type == FORMAT_DELTA_CHANGE:
            return str(abs(val - default))
        elif format_type == FORMAT_PERCENT_CHANGE:
            return f"{abs(val/default-1):.0%}"
        elif format_type == FORMAT_PERCENT_OF_DEFAULT_VALUE:
            return F"{val/default:.0%}"
        else:
            print(f"Unknown format_type, {self.name} get_value_str")
            return "unknown"

    def tooltip_values(self, format_type, more_less_words, modify_value_func = None, value_index = 0) -> dict:
        try:
            val = self.value[value_index] if self.multivar else self.value
            default = self.default[value_index] if self.multivar else self.default
            if modify_value_func:
                val = modify_value_func(val)
                default = modify_value_func(default)
            sign = val >= default
            word = more_less_words[int(not sign)] # first word is increase, second is decrease
            value_str = self.get_value_str(format_type, val, default)
            plural = '' if value_str == '1' else 's'
            return {'value': value_str, 'sign': '+' if sign else '-', 'change_word': word, 'plural': plural} 
        except Exception as e:
            print(f"{self.name} tooltip_values exception: {e}")
            return {'value': "error", 'sign': '', 'change_word': '', 'plural': ''}

    def randomize(self, random, level, WriteMemory, do_write):
        if self.test(random, self.chance, level) and self.can_be_enabled(level):
            value = self.calculate_value(random, level)
        else:
            value = copy.deepcopy(self.default)
        self.value = value
        if not do_write:
            return
        self.written_value = copy.deepcopy(value)
        self.write_value(self.address, value, self.datatype, WriteMemory, value==self.default)


class ContinuousVar(RandomVariable):
    def __init__(self, name, address, chance, datatype, default, min, max, enabled_on_levels = None, multivar_functions=None, needs_reset=False):
        super().__init__(name, address, chance, datatype, default, enabled_on_levels, multivar_functions, needs_reset)
        if min > max:
            (min,max) = (max,min)
        self.min = min
        self.max = max

    def get_randomized_value(self, random: random.Random, level):
        datatype = self.datatype[0] if self.multivar else self.datatype
        if datatype == 'float' or datatype == 'double':
            return random.uniform(self.min, self.max)
        return random.randint(int(self.min), int(self.max))


class VarWithRanges(RandomVariable):
    def __init__(self, name, address, chance, datatype, default, ranges:list[tuple], enabled_on_levels = None, multivar_functions=None, needs_reset=False):
        super().__init__(name, address, chance, datatype, default, enabled_on_levels, multivar_functions, needs_reset)
        # ranges is a list of tuples of (weight, min, max)
        assert type(ranges) == list and len(ranges) > 0
        assert all(type(x) == tuple and len(x) == 3 and isinstance(val, (int, float)) for x in ranges for val in x)
        self.weights = [x[0] for x in ranges if x[0] > 0]
        self.value_ranges = [(min(x[1], x[2]), max(x[1], x[2])) for x in ranges if x[0] > 0]
        assert len(self.weights) > 0

    def get_randomized_value(self, random: random.Random, level):
        range = random.choices(self.value_ranges, self.weights)[0] # tuple of (min, max)
        datatype = self.datatype[0] if self.multivar else self.datatype
        if datatype == 'float' or datatype == 'double':
            return random.uniform(range[0], range[1])
        return random.randint(int(range[0]), int(range[1]))


class DiscreteVar(RandomVariable):
    def __init__(self, name, address, chance, datatype, default, choices:list, enabled_on_levels = None, multivar_functions=None, needs_reset=False):
        super().__init__(name, address, chance, datatype, default, enabled_on_levels, multivar_functions, needs_reset)
        assert type(choices) == list and len(choices) > 0
        self.choices = choices

    def get_randomized_value(self, random: random.Random, level):
        return random.choice(self.choices)


class OnOffVar(RandomVariable):
    def __init__(self, name, address, chance, datatype, default, onValue, enabled_on_levels = None, multivar_functions=None, needs_reset=False):
        super().__init__(name, address, chance, datatype, default, enabled_on_levels, multivar_functions, needs_reset)
        self.onValue = onValue

    def get_randomized_value(self, random: random.Random, level):
        return self.onValue
    
    def get_value_str(self, format_type, val, default):
        if type(val) is list or type(default) is list:
            return 'Off' if self.is_default() else 'On'
        return super().get_value_str(format_type, val, default)
    
    def tooltip_values(self, format_type, more_less_words, modify_value_func = None, value_index = 0):
        val = self.value[value_index] if self.multivar else self.value
        default = self.default[value_index] if self.multivar else self.default
        if type(val) is list or type(default) is list:
            return {'value': self.get_value_str(format_type, val, default), 'sign': '', 'change_word': '', 'plural': ''}
        else:
            return super().tooltip_values(format_type, more_less_words, modify_value_func, value_index)


class FireRateVar(VarWithRanges):
    def __init__(self, name, address, chance, datatype, default, ranges, unstable_range: tuple, enabled_on_levels=None, multivar_functions=None, needs_reset=False):
        super().__init__(name, address, chance, datatype, default, ranges, enabled_on_levels, multivar_functions, needs_reset)
        assert type(unstable_range) == tuple and len(unstable_range) == 2
        self.unstable_range = (min(unstable_range), max(unstable_range))

    def randomize(self, random, level, WriteMemory, do_write, allow_unstable=True, max_multiplier=1.0):
        self.allow_unstable = allow_unstable
        self.max_multiplier = max_multiplier
        return super().randomize(random, level, WriteMemory, do_write)

    def fire_rate_randomize_value(self, random, level):
        range = random.choices(self.value_ranges, self.weights)[0] # tuple of (min, max)
        actual_range = (range[0], range[0] + self.max_multiplier * (range[1] - range[0]))
        datatype = self.datatype[0] if self.multivar else self.datatype
        if datatype == 'float' or datatype == 'double':
            value = random.uniform(actual_range[0], actual_range[1])
        else:
            value = random.randint(int(actual_range[0]), int(actual_range[1]))
        return value

    def get_randomized_value(self, random: random.Random, level):
        value = self.fire_rate_randomize_value(random, level)
        if not self.allow_unstable:
            while self.unstable_range[0] <= value <= self.unstable_range[1]:
                value = self.fire_rate_randomize_value(random, level)
        return value


class OutputStringBase(abc.ABC):
    def __init__(self, format_str: str, modify_value_func = None):
        self.format_str = format_str
        self.modify_value_func = modify_value_func
    
    def is_active(self):
        return True
    
    @abc.abstractmethod
    def __str__(self) -> str:
        pass


class SimpleOutputString(OutputStringBase):
    def __init__(self, value_container, format_str: str, modify_value_func = None):
        super().__init__(format_str, modify_value_func)
        if type(value_container) != list:
            self.value_container = [value_container]
        else:
            self.value_container = value_container

    def __str__(self) -> str:
        if type(self.value_container) != list or (type(self.value_container) == list and len(self.value_container) == 0):
            print(f"error in SimpleOutputString __str__, format: {self.format_str}")
            return f"error"
        value = self.value_container[0]
        if self.modify_value_func:
            try:
                value = self.modify_value_func(value)
            except:
                print("Error in modify_func_value, value_container = " + self.value_container)
                return "error"
        try:
            return self.format_str.format(value)
        except:
            return f"error in SimpleOutputString format_str.format, format={self.format_str}"


class FlagCountString(SimpleOutputString):
    def __init__(self, value_container: list[int], current_level_container: list[int], format_str: str, modify_value_func = None):
        super().__init__(value_container, format_str, modify_value_func)
        self.current_level_container = current_level_container

    def is_active(self):
        # -1 is for minigames
        return self.current_level_container[0] not in untouchable_wavecount and self.current_level_container[0] != -1


class VarStr(OutputStringBase):
    def __init__(self, var: RandomVariable, format_str: str, format_value_type: int = FORMAT_ACTUAL_VALUE, format_more_less_words=['more', 'less'], modify_value_func = None, value_index: int = 0):
        super().__init__(format_str, modify_value_func)
        self.var = var
        self.value_index = value_index
        self.format_value_type = format_value_type
        self.format_more_less_words = format_more_less_words

    def is_active(self):
        return not self.var.is_default()
    
    def __str__(self) -> str:
        try:
            return self.format_str.format(**self.var.tooltip_values(self.format_value_type, self.format_more_less_words, self.modify_value_func, self.value_index))
        except: 
            return f"error in VarStr format_str.format, format={self.format_str}"


class FireRateVarStr(VarStr):
    def __init__(self, var: RandomVariable, format_str: str, format_value_type: int = FORMAT_ACTUAL_VALUE, format_more_less_words=['more', 'less'], modify_value_func = None,
                unstable_str: str = "", unstable_range: tuple = (0,0)):
        super().__init__(var, format_str, format_value_type, format_more_less_words, modify_value_func)
        self.unstable_str = unstable_str
        self.unstable_range = unstable_range
    
    def __str__(self) -> str:
        val = self.var.current_main_value()
        ranges = self.var.value_ranges[:]
        if self.unstable_range in ranges:
            ranges.remove(self.unstable_range)
        min_val = 9999
        max_val = 0
        for i in ranges:
            j = self.modify_value_func(i[0])
            k = self.modify_value_func(i[1])
            min_val = min(min_val, min(j,k))
            max_val = max(max_val, max(j,k))
        def_val = self.modify_value_func(self.var.default)
        rng_val = self.modify_value_func(val)
        out_val = 0.5
        if rng_val > def_val:
            out_val = 0.5 + (rng_val-def_val)/(max_val-def_val)*0.5
        elif rng_val < def_val:
            out_val = 0.5 - (rng_val-def_val)/(min_val-def_val)*0.5
        if out_val < 0 or out_val > 1:
            out_val = 0.5
        WriteMemory("unsigned char", int(out_val*8.9999999)*3, 0x651308 + int(self.var.name[12:]))
        if self.unstable_range[0] <= val <= self.unstable_range[1]:
            return self.unstable_str
        return super().__str__()


class IndexedStrContainer:
    def __init__(self, name: str, address: int, max_bytes_per_string: int, string_count: int):
        self.name = name
        self.address = address
        self.bytes_per_string = max_bytes_per_string
        self.string_count = string_count
        self.str_dict = dict(zip(range(string_count), ([] for _ in range(string_count))))

    def add_var(self, var: OutputStringBase, indices):
        if type(indices) != list:
            indices = [indices]
        if any(x not in self.str_dict for x in indices):
            raise ValueError(f"wrong index for {self.name} container, indices: {','.join(str(x) for x in indices)}")
        for i in indices:
            self.str_dict[i].append(var)

    def construct_string(self, index: int):
        if index not in self.str_dict:
            string = f"index {index} is not in {self.name} dictionary on construct_string"
            print(string)
        else:
            vars: list[OutputStringBase] = self.str_dict[index]
            str_list = []
            for v in vars:
                if not v.is_active():
                    continue
                str_list.append(str(v))
            string = '\n'.join(str_list)
        return string
    
    def write_string(self, index: int, string: str, WriteMemory):
        if index not in self.str_dict:
            print(f"index {index} is not in {self.name} dictionary in write_string")
            return
        address = self.address + self.bytes_per_string * index
        if len(string) > self.bytes_per_string - 1:
            string = string[:self.bytes_per_string - 1]
        l = list(string.encode('ascii', 'ignore'))
        l.append(0)
        WriteMemory("unsigned char", l, address)

    def update_strings(self, WriteMemory):
        for i in range(self.string_count):
            string = self.construct_string(i)
            self.write_string(i, string, WriteMemory)


class NonIndexedStrContainer:
    def __init__(self, name: str, address: int, max_bytes_per_string: int, string_count: int, n_of_lines_output_address: int, second_n_of_lines: int):
        self.name = name
        self.address = address
        self.bytes_per_string = max_bytes_per_string
        self.string_count = string_count
        self.n_of_lines_output_address = n_of_lines_output_address
        self.second_n_of_lines = second_n_of_lines
        self.strings = []
        self.n_of_lines_written = 0

    def add_var(self, var: OutputStringBase):
        self.strings.append(var)

    def construct_string(self, var: OutputStringBase):
        if var.is_active():
            return str(var)
        return ""
    
    def write_string(self, index: int, string: str, WriteMemory):
        if index >= self.string_count:
            print(f"Index {index} outside of string_count range for {self.name} in write_string")
            return
        address = self.address + self.bytes_per_string * index
        if len(string) > self.bytes_per_string - 1:
            string = string[:self.bytes_per_string - 1]
        l = list(string.encode('ascii', 'ignore'))
        l.append(0)
        WriteMemory("unsigned char", l, address)
        

    def update_strings(self, WriteMemory):
        free_index = 0
        for v in self.strings:
            if not v.is_active():
                continue
            string = self.construct_string(v)
            self.write_string(free_index, string, WriteMemory)
            free_index = free_index + 1
            if free_index >= self.string_count:
                break
        self.n_of_lines_written = free_index
        self.write_n_of_lines(WriteMemory, free_index, self.n_of_lines_output_address, self.second_n_of_lines)

    def get_amount_of_lines(self):
        return self.n_of_lines_written
    
    def write_n_of_lines(self, WriteMemory, value, address1, address2):
        WriteMemory("int", value, address1)
        WriteMemory("int", max(value-1, 0), address2)


@dataclass
class VarWithStrIndices:
    var_str: OutputStringBase
    plant_indices: list[int] = None
    zombie_indices: list[int] = None
    affects_game_str: bool = False


class VarContainer(abc.ABC):
    def __init__(self, seed, write_memory_func, do_activate_strings, plants_container: IndexedStrContainer, 
                 zombies_container: IndexedStrContainer, game_container: NonIndexedStrContainer):
        assert (do_activate_strings and plants_container and zombies_container and game_container) or not do_activate_strings
        self.WriteMemory = write_memory_func
        self.rng = random.Random(seed)
        self.do_activate_strings = do_activate_strings
        if do_activate_strings:
            self.plant_strings = plants_container
            self.zombie_strings = zombies_container
            self.game_strings = game_container

    @abc.abstractmethod
    def randomize(self, level, do_write):
        pass

    @abc.abstractmethod
    def reset(self):
        pass

    def chance(self, base: float, modifier: float) -> float:
        if modifier <= 0:
            return 0
        if modifier == 5:
            return base
        # modifier of 5 means use base chance; below 5, chance is decreased exponentially
        return base / (1.2 ** (5 - modifier))

    def add_vars_to_string_containers(self, vars: list[VarWithStrIndices]):
        if not self.do_activate_strings:
            return
        for v in vars:
            if v.affects_game_str:
                self.game_strings.add_var(v.var_str)
            if v.plant_indices:
                self.plant_strings.add_var(v.var_str, v.plant_indices)
            if v.zombie_indices:
                self.zombie_strings.add_var(v.var_str, v.zombie_indices)


class FireRateContainer(VarContainer):
    def __init__(self, seed, write_memory_func, do_activate_strings, plants_container, zombies_container, game_container, category):
        super().__init__(seed, write_memory_func, do_activate_strings, plants_container, zombies_container, game_container)
        self.category = category
        self.vars: list[VarWithStrIndices] = []
        self.potentially_unstable_vars: list[VarWithStrIndices] = []
        indices =            [0,   5,   7,   8,    10,  13,  18,  24,   26,  28,  29,  32,  34,  39,  40,   42,   43,   44,  47,   31]
        defaults =           [150, 150, 150, 150,  150, 150, 150, 150,  150, 150, 150, 300, 300, 300, 150,  200,  150,  300, 3000, 1500]
        unstableValues =     [36.5,36.5,29,  30.5, 52.5,0,   35.5,30.5, 0,   0,   42,  0,   0,   0,   45,   131,  36.5, 0,   0,    0]
        canGoBeyondAverage = [True,True,True,True, True,True,True,True, True,True,True,True,True,True,True, False,True, True,True, True]
        canGoVeryStrong =    [True,True,True,False,True,True,True,False,True,True,True,True,True,True,False,False,False,True,True, True]
        addresses = [0x69F2CC + i * 36 for i in indices]
        addresses[-2] = 0x464D4D # cob cannon fire cooldown
        addresses[-1] = 0x46163A # magnet recharge
        assert len(indices) == len(defaults) == len(addresses)
        for i in range(len(indices)):
            ranges = []
            puffMultiplier = 1 - 0.5 * int(indices[i] == 8 or indices[i] == 24)
            isCob = int(indices[i] == 47)
            minDelay = 162 if indices[i] == 42 else 96 if indices[i] == 40 else 97 if indices[i] == 43 else 0
            # weak range - limited at average setting
            ranges.append((100, defaults[i]*(1+(0.06+0.01*min(category,3))*puffMultiplier-0.15*isCob),
                defaults[i]*(1+(0.18+0.06*min(category,3))*puffMultiplier-0.15*isCob)))
            ranges.append((100, max(defaults[i]*(1-(0.05+0.01*min(category,3))*puffMultiplier-0.1*isCob), minDelay),
                max(defaults[i]*(1-(0.14+0.05*min(category,3))*puffMultiplier-0.1*isCob), minDelay)))
            # stronger range
            if category > 3 and canGoBeyondAverage[i]:
                ranges.append(((50+30*(category-4))*puffMultiplier, defaults[i]*(1+0.35*puffMultiplier),
                    defaults[i]*(1+0.7*puffMultiplier)))
                ranges.append(((50+30*(category-4))*puffMultiplier, max(defaults[i]*(1-0.25*puffMultiplier), minDelay),
                    max(defaults[i]*(1-0.42*puffMultiplier), minDelay)))
            # very strong range
            if category > 4 and canGoVeryStrong[i]:
                ranges.append((60, defaults[i]*1.75, defaults[i]*2.1))
                ranges.append((40, defaults[i]*0.47, defaults[i]*0.55))
            # unstable fire rate
            if category > 2 and unstableValues[i] != 0:
                ranges.append((-12 + 12 * category, math.floor(unstableValues[i]), math.ceil(unstableValues[i])))
                unstable_range = (math.floor(unstableValues[i]), math.ceil(unstableValues[i]))
            else:
                unstable_range = (0,0)
            self.potentially_unstable_vars.append(VarWithStrIndices(
                            FireRateVarStr(var=FireRateVar("fire period "+str(indices[i]), address=addresses[i],
                                                chance=puffMultiplier*self.chance(120, category),
                                                datatype="int", default=defaults[i], ranges=ranges, unstable_range=unstable_range),
                                format_str="Fire Rate: {sign}{value}",
                                format_value_type=FORMAT_PERCENT_CHANGE,
                                unstable_range=unstable_range,
                                unstable_str="Fire Rate: *Unstable*",
                                modify_value_func=lambda period:1/(period-7.5)  # reciprocal of time is fire rate, this also takes rng per shot into account -
                                                                                # 0.075 sec is wrong for magnet and cob, but that's fine
                ),
                plant_indices=[indices[i]]
            ))
        # chomper chewing time - can only be decreased, chance is constant (reason - I want it that way)
        self.vars.append(VarWithStrIndices(
                VarStr(var=ContinuousVar("fire period "+str(6), address=0x461551, chance=40, datatype="int",
                                    default=4000, min=4000*(0.65-0.04*category), max=4000*(0.9),
                                    enabled_on_levels=lambda l:l!=45), # disabled on 5-5
                        format_str="Chewing duration {change_word} to {value} sec",
                        format_value_type=FORMAT_ACTUAL_VALUE,
                        format_more_less_words=['increased', 'decreased'],
                        modify_value_func=lambda period:period/100+2 # there's also ~2 sec wakeup animation?
                ),
                plant_indices=[6]
            ))
        # imitater transformation time - there's also animation time (about 1.2 sec) unaffected by this change
        self.vars.append(VarWithStrIndices(
                VarStr(var=ContinuousVar("fire period "+str(48), address=0x45E2D9, chance=self.chance(120, category), datatype="int",
                                    default=200, min=200*(0.1), max=200*(1.9)),
                        format_str="Transformation speed: {sign}{value}",
                        format_value_type=FORMAT_PERCENT_CHANGE,
                        modify_value_func=lambda period:1/(period+120) # add ~1.2 untouched second of animation
                ),
                plant_indices=[48]
            ))
        # coffee transformation time - affects both delay and wake up timer
        self.vars.append(VarWithStrIndices(
                VarStr(var=ContinuousVar("fire period "+str(35), address=[0x45E521,0x466B36], chance=self.chance(120, category), datatype=["int","int"],
                                    default=[100,100], min=20, max=180, multivar_functions=[lambda main:main]),
                                    # multivar_functions allows us to modify several values at the same time, but only if those extra values
                                    # are dependant on main one - in that case wake up timer set to be the same as coffee delay
                        format_str="Transformation speed: {sign}{value}",
                        format_value_type=FORMAT_PERCENT_CHANGE,
                        modify_value_func=lambda period:1/period
                ),
                plant_indices=[35]
            ))
        # tired plants - reduce fire rate of every individual plant after each shot. Too OP with with unstable fire rate, so this takes priority
        self.WriteMemory("unsigned char", [0x53, 0x55, 0xFF, 0x40, 0x5C, 0xEB, 0x07], 0x0045EF09) # replacing CC bytes
        self.WriteMemory("unsigned char", [0xFF, 0x43, 0x5C], 0x0045F29D) # replacing CC bytes
        self.WriteMemory("unsigned char", [0xFF, 0x46, 0x5C], 0x0045F6DD) # replacing CC bytes
        self.tired_var = VarWithStrIndices(
            VarStr(var=OnOffVar("tired plants", address=[0x0045EF15,0x0045F8D1,0x0045F8DD], chance=0,
                                    datatype=["unsigned char","unsigned char","unsigned char"],
                                    default=[[0x53,0x55], [0xe8,0xca,0xf9,0xff,0xff], [0xe8,0xfe,0xfd,0xff,0xff]],
                                    enabled_on_levels=lambda l:l not in [5,15,45] or (l==45 and randomConveyors.get() != 'False'),
                                    onValue=[0xeb,0xf2], # first address
                                    multivar_functions=[lambda _:[0xE8, 0xC7, 0xF9, 0xFF, 0xFF], lambda _:[0xE8, 0xFB, 0xFD, 0xFF, 0xFF]]),
                    format_str="Tired plants: after every shot, each individual plant slows down its fire rate a bit",
            ),
            affects_game_str=True
        )
        self.add_vars_to_string_containers([self.tired_var])
        self.add_vars_to_string_containers(self.vars)
        self.add_vars_to_string_containers(self.potentially_unstable_vars)

    def randomize(self, level, do_write):
        self.tired_var.var_str.var.randomize(self.rng, level, self.WriteMemory, do_write)
        for v in self.vars:
            v.var_str.var.randomize(self.rng, level, self.WriteMemory, do_write)
        allow_unstable = self.tired_var.var_str.var.is_default()
        for v in self.potentially_unstable_vars:
            v.var_str.var.randomize(self.rng, level, self.WriteMemory, do_write, allow_unstable, 1.0 if allow_unstable else 0.7)

    def reset(self):
        for v in self.vars:
            if v.var_str.var.needs_reset:
                v.var_str.var.reset_memory(self.WriteMemory)
        for v in self.potentially_unstable_vars:
            if v.var_str.var.needs_reset:
                v.var_str.var.reset_memory(self.WriteMemory)


class HealthContainer(VarContainer):
    def __init__(self, seed, write_memory_func, do_activate_strings, plants_container, zombies_container, game_container, category):
        super().__init__(seed, write_memory_func, do_activate_strings, plants_container, zombies_container, game_container)
        self.category = category
        self.vars: list[VarWithStrIndices] = []
        # special cases are balloon, zomboss. Doesn't change default body health (270),
        # so normals, snorkels, backups, boblseds, peashooter, gatling, squash are untouched

        # idea is: very strong is 100% chance overall + some chance for bigger changes + chance for no restrictions style changes.
        # strong is 100% chance overall + some chance for bigger changes, but no no restrictions style
        # average is <100% overall chance + slim chance for bigger changes
        # everything below has less chance for any change + smaller range of changes
        # every change should be sizeable, let's make no like +1% changes
        indices =           [2,   4,   6,   19,   20,   7,   17,  3,    14,   23,   32,   12,   22,   15,   18,   5,   8,    24,   21,   27,  28,   31]
        defaults =          [370, 1100,1100,1350, 450,  1400,100, 500,  500,  3000, 6000, 1350, 850,  500,  500,  150, 500,  70,   500,  1100,500,  2200]
        isArmorHP =         [True,True,True,False,False,True,True,False,False,False,False,False,False,False,False,True,False,False,False,True,False,True]
        changeMultipliers = [1,   0.7, 0.7, 0.7,  1,    0.7, 0.2, 1,    1,    0.38, 0.20, 0.7,  1,    1,    1,    1,   1,    2.5,  0.85, 0.7, 1,    0.45]
        addresses = [0x00522892,0x0052292B,0x00522949,0x0052296E,0x00522A1B,0x00522BB0,0x00522BEF,0x00522CBF,0x00522D64,0x00523D26,0x00523E4A,
                        0x00522DE1,0x00522E8D,0x00522FC7,0x00523300,0x0052337D,0x00523530,0x005235AC,0x0052299C,0x0052382B,0x00523A87,0x0052395D]
        assert len(indices) == len(defaults) == len(isArmorHP) == len(changeMultipliers) == len(addresses)
        for i in range(len(indices)):
            # note, we use 180 and not 270 because players are generally interested in how long it takes to kill zombie with firepower, so use hp without head
            ranges = []
            # weakest changes
            if isArmorHP[i]:
                min_m = (0.075 + 0.005 * category) / (defaults[i] / (180 + defaults[i])) * changeMultipliers[i]
                max_m = (0.09 + 0.06 * category) / (defaults[i] / (180 + defaults[i])) * changeMultipliers[i]
            else:
                min_m = (0.075 + 0.005 * category) * changeMultipliers[i]
                max_m = (0.09 + 0.06 * category) * changeMultipliers[i]
            ranges.append((100, defaults[i]*(1+min_m), defaults[i]*(1+max_m)))
            ranges.append((100, max(defaults[i]*(1-max_m*0.88), 5), max(defaults[i]*(1-min_m*0.88), 5))) # never set less than 5 hp
            if category > 2:
                # stronger changes:
                if isArmorHP[i]:
                    min_m = (0.05 + 0.04 * category) / (defaults[i] / (180 + defaults[i])) * changeMultipliers[i]
                    max_m = (0.4 + 0.05 * category) / (defaults[i] / (180 + defaults[i])) * changeMultipliers[i]
                else:
                    min_m = (0.05 + 0.04 * category) * changeMultipliers[i]
                    max_m = (0.4 + 0.05 * category) * changeMultipliers[i]
                ranges.append((-60 + 30 * category, defaults[i]*(1+min_m), defaults[i]*(1+max_m)))
                ranges.append((-60 + 30 * category, max(defaults[i]*(1-max_m*0.8), 5), max(defaults[i]*(1-min_m*0.8), 5))) # never set less than 5 hp
            if category > 4 and ((defaults[i] > 400 and isArmorHP[i]) or not isArmorHP[i]):
                # very strong changes
                if isArmorHP[i]:
                    min_m = (0.9) / (defaults[i] / (180 + defaults[i])) * changeMultipliers[i]**0.7
                    max_m = (1.3) / (defaults[i] / (180 + defaults[i])) * changeMultipliers[i]**0.7
                else:
                    min_m = (0.9) * changeMultipliers[i]**0.7
                    max_m = (1.3) * changeMultipliers[i]**0.7
                ranges.append((53, defaults[i]*(1+min_m), defaults[i]*(1+max_m)))
                ranges.append((47, max(defaults[i]*(1-max_m*0.66), 5), max(defaults[i]*(1-min_m*0.66), 5))) # never set less than 5 hp
            args = { 'var': VarWithRanges("zombie health "+str(indices[i]), address=addresses[i], chance=self.chance(120, category), datatype="int",
                                    default=defaults[i], ranges=ranges),
                        'format_str': "Health change: {sign}{value}",
                        'format_value_type': FORMAT_PERCENT_CHANGE
            }
            if isArmorHP[i]:
                args['modify_value_func'] = lambda h:h+180 # body health for zombies with armor - but account only for health needed to depcaitate zombie
            self.vars.append(VarWithStrIndices(
                VarStr(**args),
                zombie_indices=[indices[i]]
            ))
        # ballon has special formatting
        balloon_choices = [40, 60]
        if category > 1:
            balloon_choices.extend([40,60,80])
        if category > 3:
            balloon_choices.extend([60,80,100,100])
        self.vars.append(VarWithStrIndices(
                VarStr(var=DiscreteVar("zombie health "+str(16), address=0x005234BF, chance=45+5*category, datatype="int",
                                    default=20, choices=balloon_choices,
                                    enabled_on_levels=lambda l:l==-1 or (l in [33,34,39,40] and (not randomZombies.get() or not 16 in currentZombies))\
                                        or (l not in [33,34,39,40] and randomZombies.get() and 16 in currentZombies)),
                        format_str="Balloon requires extra {value} hit{plural} to pop",
                        format_value_type=FORMAT_DELTA_CHANGE,
                        modify_value_func=lambda h:h//20 # modify_value_func changes value (and default) before formatting, it doesn't affect actual randomization
                ),
                zombie_indices=[16],
                plant_indices=[26, 43] # show it on cactus and cattail tooltip as well
        ))
        # dr zomboss
        self.vars.append(VarWithStrIndices(
                VarStr(var=VarWithRanges("zombie health "+str(25), address=0x00523624, chance=50+category*17, datatype="int", default=40000,
                                    ranges=[(100, 33000-1000*category, 36000),
                                            (15+12*category, 42000, 44000+4000*int(category==5 and randomConveyors.get() != "It's Raining Seeds"))],
                                    enabled_on_levels=lambda l:l==50), # triggered only on 5-10
                        format_str="Zomboss has {value} hp {change_word} than usual",
                        format_value_type=FORMAT_PERCENT_CHANGE,
                        format_more_less_words=['more', 'less']
                ),
                affects_game_str=True
        ))
        self.add_vars_to_string_containers(self.vars)

    def randomize(self, level, do_write):
        for v in self.vars:
            v.var_str.var.randomize(self.rng, level, self.WriteMemory, do_write)

    def reset(self):
        for v in self.vars:
            if v.var_str.var.needs_reset:
                v.var_str.var.reset_memory(self.WriteMemory)


class ShitContainer(VarContainer):
    def __init__(self, seed, write_memory_func, do_activate_strings, plants_container, zombies_container, game_container):
        super().__init__(seed, write_memory_func, do_activate_strings, plants_container, zombies_container, game_container)
        self.vars: list[VarWithStrIndices] = []
        plant_on_graves = VarWithStrIndices(
            VarStr(var=OnOffVar("plant_on_graves", address=0x0040E162, chance=25,
                                datatype="unsigned char",
                                default=[0x74],
                                onValue=[0xEB],
                                enabled_on_levels=lambda l:l != -1 and level_worlds[l] == 1 and l != 35,
                                ),
                    format_str="Can plant on graves",
            ),
            affects_game_str=True
        )
        upgrades_placed_anywhere = VarWithStrIndices(
            VarStr(var=OnOffVar("upgrades_free_planting", address=[0x0040E47A, 0x0041D7D6], chance=20,
                                datatype=["unsigned char", "unsigned char"],
                                default=[[0x08], [0x75, 0x16, 0x8D, 0x58, 0xDF]], # jne 0041D7EE; lea ebx,[eax-21]
                                onValue=[0x00],
                                multivar_functions=[lambda _: [0xE9, 0xB4, 0x00, 0x00, 0x00]] # jmp 0041D88F
                                ),
                    format_str="Upgrade plants don't require base plant",
            ),
            affects_game_str=True,
            plant_indices=[40, 41, 42, 43, 44, 45, 46, 47]
        )
        invisible_zombies = VarWithStrIndices(
            VarStr(var=OnOffVar("invisible_zombies", address=[0x0052E356, 0x0053402A], chance=11,
                                datatype=["unsigned char", "unsigned char"],
                                default=[[0x15, 0x75], [0x15, 0x75]],
                                onValue=[0x50, 0x74],
                                multivar_functions=[lambda _: [0x50, 0x74]],
                                enabled_on_levels=lambda l:l == -1 or flags_per_level[l] == 1,
                                needs_reset=True
                                ),
                    format_str="Zombies are invisible",
            ),
            affects_game_str=True,
        )
        shrooms_wake_up = VarWithStrIndices(
            VarStr(var=ContinuousVar("shrooms_wake_up", address=[0x004108CC, 0x0040E140], chance=28,
                                    datatype=["unsigned int", "unsigned char"],
                                    default=[0, [0x7F, 0x0D]], # wake up timer, jmp if wake up timer already active
                                    min=1500, # wake up timer
                                    max=3000, # wake up timer
                                    enabled_on_levels=lambda l:(l == -1 or level_worlds[l] in [0, 2, 4]) and l not in [15, 35],
                                    multivar_functions=[lambda _:[0x90, 0x90]] # allow to plant if wake up timer active
                                    ),
                    format_str="Mushrooms wake up after {value} seconds",
                    format_value_type=FORMAT_ACTUAL_VALUE,
                    modify_value_func=lambda time:time/100

            ),
            affects_game_str=True,
            plant_indices=[8, 9, 10, 12, 13, 14, 15, 24, 31, 42]
        )
        autoscroll_rule = VarWithStrIndices(
            VarStr(var=VarWithRanges("autoscroll_rule", address=[0x004140CA,0x004140C0], chance=22,
                                    datatype=["unsigned int","unsigned int"],
                                    default=[2500, 600], # base + random
                                    ranges=[(40, 900, 1200), (60, 1200, 1700)], # (weight, min, max)
                                    enabled_on_levels=lambda l:l == -1 or (l != 15 and l != 25 and l != 35 and l != 50),
                                    multivar_functions=[lambda main:int(main/2500*600)] # calculate random part
                                    ),
                    format_str="Autoscroll rule reduced to {value} sec",
                    format_value_type=FORMAT_ACTUAL_VALUE,
                    modify_value_func=lambda time:time/100
            ),
            affects_game_str=True,
        )
        more_wavepoints = VarWithStrIndices(
            VarStr(var=OnOffVar("more_wavepoints", address=0x00409748, chance=22,
                                datatype="unsigned char",
                                default=[0xB8, 0x56, 0x55, 0x55, 0x55, 0xF7, 0xEB, 0x8B, 0xC2],
                                onValue=[0x8B, 0xCB, 0xD1, 0xE9, 0x8D, 0x49, 0x01, 0xEB, 0x07],
                                enabled_on_levels=lambda l:gamemode.get() != 'ng+' and (l == -1 or l not in [15,35,50]),
                                needs_reset=True
                                ),
                    format_str="Wave points increase per 2 waves instead of 3",
            ),
            affects_game_str=True,
        )
        spawn_coords = VarWithStrIndices(
            # most zombies x-pos, random for most zombies x-pos, vaulters, gargs, zamboni, catapult, bobsled, flag
            VarStr(var=ContinuousVar("spawn_coords", address=[0x005225A5, 0x00522598, 0x00522CE1, 0x00523D3E, 0x00522DF5, 0x00522E97,
                                                              float_rebase(0x005230FB, 'float', 880.0), float_rebase(0x0052327E, 'float', 800.0)],
                                    chance=25,
                                    datatype=["unsigned int", "unsigned int", "unsigned int", "unsigned int", "unsigned int", "unsigned int", "float", "float"],
                                    default=[780, 40, 870, 845, 800, 825, 880.0, 800.0],
                                    min=580,
                                    max=700,
                                    enabled_on_levels=lambda l:l == -1 or l not in [15,35,45,50],
                                    multivar_functions=[lambda main:40, lambda main:870-(780-main), lambda main:845-(780-main), lambda main:800-(780-main),
                                                        lambda main:825-(780-main), lambda main:880.0-(780-main), lambda main:800.0-(780-main)],
                                    needs_reset=True
                                    ),
                    format_str="Zombies spawn {value} more left",
                    format_value_type=FORMAT_PERCENT_CHANGE
            ),
            affects_game_str=True,
        )
        extra_slots = VarWithStrIndices(
            VarStr(var=DiscreteVar("extra_slots", address=[0x0041BFE9, 0x0041C004, 0x0041BFF7], chance=30,
                                    datatype=["unsigned char", "unsigned char", "unsigned char"],
                                    default=[6, [0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC, 0xCC], [0x5E, 0xC3]],
                                    choices=[7, 7, 8],
                                    enabled_on_levels=lambda l:l % 5 != 0 and ((gamemode.get() != 'adventure' and shopless.get()) or (gamemode.get() == 'adventure' and global_level_index >= 6)),
                                    multivar_functions=[lambda _:[0x83, 0xF8, 0x0A, 0x7E, 0x05, 0xB8, 0x0A, 0x00, 0x00, 0x00, 0x5E, 0xC3],
                                                        lambda _:[0xEB, 0x0B]],
                                    ),
                    format_str="Extra {value} slot{plural}",
                    format_value_type=FORMAT_DELTA_CHANGE
            ),
            affects_game_str=True,
        )
        fifty_percent_rule = VarWithStrIndices(
            VarStr(var=VarWithRanges("50_percent", address=[float_rebase(0x00414080, "float", 0.5), float_rebase(0x00414073, "float", 0.65)],
                                    chance=30,
                                    datatype=["float", "float"],
                                    default=[0.5, 0.65],
                                    ranges=[(80, 0.60, 0.75), (50, 0.35, 0.40), (50, 0.75, 0.90)],
                                    enabled_on_levels=lambda l:l!=15 and l!=35 and l!=50,
                                    multivar_functions=[lambda main:main+0.3*(1-main)],
                                    needs_reset=True
                                    ),
                    format_str="50% rule changed to {value}% rule",
                    format_value_type=FORMAT_ACTUAL_VALUE,
                    modify_value_func=lambda v:(1-v)*100
            ),
            affects_game_str=True,
        )
        random_zombie_sizes_var = VarWithStrIndices(
            VarStr(var=OnOffVar("zombie_sizes", address=0x5226DD, chance=20,
                                datatype="unsigned char",
                                default=[0xD9, 0xE8, 0x88, 0x5F, 0x78],
                                onValue=[0xE9, *(random_zombie_size_address-0x005226E2).to_bytes(4,"little",signed=True)], # jmp to new code
                                enabled_on_levels=lambda l:l!=25,
                                needs_reset=True
                                ),
                    format_str="Random zombie sizes",
            ),
            affects_game_str=True,
        )
        extra_plant_hp = VarWithStrIndices(
            # most plants, garlic, spikerock
            VarStr(var=OnOffVar("extra_plant_hp", address=[0x0045DC55, 0x0045E242, 0x0045E5C3], chance=25,
                                datatype=["unsigned int", "unsigned int", "unsigned int"],
                                default=[300, 400, 450],
                                onValue=[600],
                                multivar_functions=[lambda main:800, lambda main:900]
                                ),
                    format_str="Normal plants have double hp (not nuts/pumpkins)",
            ),
            affects_game_str=True,
        )
        class StartingSunVar(DiscreteVar):
            def test(self, random: random.Random, chance, level):
                if gamemode.get() != 'minigames' and (level_worlds[level] == 1 or level_worlds[level] == 3 or level_worlds[level] == 5):
                    chance = (chance / 100)**0.5 * 100 # increase chance on night levels
                return super().test(random, chance, level)
        starting_sun = VarWithStrIndices(
            VarStr(
                var=StartingSunVar("starting sun", 0x0040b09b, chance=60, datatype="int",
                                    default=50, choices=[75, 75, 100], enabled_on_levels=lambda l: l % 5 != 0),
                format_str="Starting sun: {value}",
                format_value_type=FORMAT_ACTUAL_VALUE),
            affects_game_str=True
        )
        lose_sun_on_plant_death = VarWithStrIndices(
            # jump to code; enable writing negative sun in seed bank; reset n of lost plants to 0; amount of sun lost
            VarStr(var=OnOffVar("lose_sun_on_plant_death",
                                address=[0x0041605E, 0x0048983A, lose_sun_on_plant_death_address_data, lose_sun_on_plant_death_address+0x34],
                                chance=22,
                                datatype=["unsigned char", "unsigned char", "unsigned int", "unsigned char"],
                                default=[[0x89, 0x85, 0x5C, 0x55, 0x00, 0x00], 0xC8, 0, 40],
                                onValue=[0xE9, *(lose_sun_on_plant_death_address-0x416063).to_bytes(4,"little",signed=True), 0x90],
                                enabled_on_levels=lambda l:l%5!=0,
                                multivar_functions=[lambda main:0xC0, lambda main:0,
                                                    lambda main,level:int(self.rng.randint(15,50) * (1 if (level == -1 or level_worlds[level] in [0,2,4]) else 0.34))]
                                ),
                    format_str="Lose {value} sun when plant dies/shoveled",
                    value_index=3 # sun lost per plant
            ),
            affects_game_str=True,
        )
        click_on_sun_plant = VarWithStrIndices(
            VarStr(var=OnOffVar("click_on_sun_plant", address=0x00466390, chance=25,
                                datatype="unsigned char",
                                default=[0x83, 0x7E, 0x3C, 0x25, 0x57],
                                onValue=[0xE9, *(click_on_sun_plant_address-0x466395).to_bytes(4,"little",signed=True)],
                                enabled_on_levels=lambda l:l%5!=0,
                                ),
                    format_str="Clicking on sun plants accelerates production",
            ),
            affects_game_str=True,
        )
        advance_cd_on_zombie_death = VarWithStrIndices(
            VarStr(var=OnOffVar("advance_cd_on_zombie_death", address=0x00530633, chance=25,
                                datatype="unsigned char",
                                default=[0x5F, 0x8B, 0xE5, 0x5D, 0xC3],
                                onValue=[0xE9, *(advance_cd_on_zombie_death_address-0x530638).to_bytes(4,"little",signed=True)],
                                enabled_on_levels=lambda l:l%5!=0,
                                ),
                    format_str="Killing zombies advances cooldowns by 2 seconds",
            ),
            affects_game_str=True,
        )
        self.vars.append(plant_on_graves)
        self.vars.append(upgrades_placed_anywhere)
        self.vars.append(invisible_zombies)
        self.vars.append(shrooms_wake_up)
        self.vars.append(autoscroll_rule)
        self.vars.append(more_wavepoints)
        self.vars.append(spawn_coords)
        self.vars.append(extra_slots)
        self.vars.append(fifty_percent_rule)
        self.vars.append(random_zombie_sizes_var)
        self.vars.append(extra_plant_hp)
        self.vars.append(lose_sun_on_plant_death)
        self.vars.append(click_on_sun_plant)
        self.vars.append(advance_cd_on_zombie_death)
        self.vars.append(starting_sun)

        self.add_vars_to_string_containers(self.vars)


    def randomize(self, level, do_write):
        for v in self.vars:
            v.var_str.var.randomize(self.rng, level, self.WriteMemory, do_write)

    def reset(self):
        for v in self.vars:
            if v.var_str.var.needs_reset:
                v.var_str.var.reset_memory(self.WriteMemory)


class RandomVars(VarContainer):
    def __init__(self, seed, write_memory_func, do_activate_strings, plants_container: IndexedStrContainer, 
                 zombies_container: IndexedStrContainer, game_container: NonIndexedStrContainer, code_address,
                 catZombieHealth: int, catFireRate: int, randomShit:bool):
        super().__init__(seed, write_memory_func, do_activate_strings, plants_container, zombies_container, game_container)
        self.seed = seed
        catFireRate = max(catFireRate, 0)
        catZombieHealth = max(catZombieHealth, 0)
        randomShit = int(randomShit) * 5
        self.code_address = code_address
        self.catZombieHealth = catZombieHealth
        self.catFireRate = catFireRate
        self.vars: list[VarWithStrIndices] = []
        self.unprintable_vars: list[RandomVariable] = []
        self.var_containers: list[VarContainer] = []
        self.any_category_enabled = catZombieHealth or catFireRate or randomShit # use to make sure that system is enabled for randomization and not just for string rendering
        if catZombieHealth:
            self.var_containers.append(HealthContainer(self.seed+"health", write_memory_func, do_activate_strings, plants_container,
                                        zombies_container, game_container, catZombieHealth))
        if catFireRate:
            self.var_containers.append(FireRateContainer(self.seed+"firerate", write_memory_func, do_activate_strings, plants_container,
                                        zombies_container, game_container, catFireRate))
        if randomShit:
            self.var_containers.append(ShitContainer(self.seed+"shit", write_memory_func, do_activate_strings, plants_container,
                                        zombies_container, game_container))
        self.add_vars_to_string_containers(self.vars)
            

    def randomize(self, level, do_write):
        for v in self.vars:
            v.var_str.var.randomize(self.rng, level, self.WriteMemory, do_write)
        for v in self.unprintable_vars:
            v.randomize(self.rng, level, self.WriteMemory, do_write)
        for c in self.var_containers:
            c.randomize(level, do_write)
        if do_write and self.do_activate_strings: # as this is a main container, it also updates strings
            self.plant_strings.update_strings(self.WriteMemory)
            self.zombie_strings.update_strings(self.WriteMemory)
            self.game_strings.update_strings(self.WriteMemory)
            if self.game_strings.get_amount_of_lines() > 1: # first line is always hotkey hint
                self.WriteMemory("unsigned char", [1], self.code_address) # force printing

    def reset(self):
        for v in self.vars:
            if v.var_str.var.needs_reset:
                v.var_str.var.reset_memory(self.WriteMemory)
        for v in self.unprintable_vars:
            if v.needs_reset:
                v.reset_memory(self.WriteMemory)
        for c in self.var_containers:
            c.reset()


float_rebase_current_offset = 0
def float_rebase(address: int, datatype: str, original_value: float):
    global float_rebase_current_offset
    if datatype != 'float' and datatype != 'double':
        raise TypeError('Wrong datatype')
    if datatype == 'double' and float_rebase_current_offset % 8 != 0:
        float_rebase_current_offset = float_rebase_current_offset // 8 + 8
    write_address = float_rebases_address + float_rebase_current_offset
    WriteMemory(datatype, [original_value], write_address)
    WriteMemory("unsigned int", [write_address], address)
    float_rebase_current_offset += (8 if datatype == 'double' else 4)
    return write_address

#endregion
######### END OF RANDOM VARS SYSTEM ########


daveActualPlantCount = 3 if enableDave.get() == "False" or davePlantsCount.get() == "random(1-5)" else int(davePlantsCount.get())
actualRandomVarsZombieHealth = ["Off", "Very weak", "Weak", "Average", "Strong", "Very Strong"].index(randomVarsCatZombieHealth.get())
actualRandomVarsFireRate = ["Off", "Very weak", "Weak", "Average", "Strong", "Very Strong"].index(randomVarsCatFireRate.get())
randomVarsSystemEnabled = True

weights_rng = random.Random(seed+'weight')
cost_rng = random.Random(seed+'cost')
cooldown_rng = random.Random(seed+'cooldown')
wavepoint_rng = random.Random(seed+'wavepoint')
startingwave_rng = random.Random(seed+'startingwave')
zombies_rng = random.Random(seed+'zombies')
dave_rng = random.Random(seed+'dave')
upgrade_rng = random.Random(seed+'upgrade')
wavecount_rng = random.Random(seed+'wavecount')
worlds_rng = random.Random(seed+'worlds')
sounds_rng = random.Random(seed+'sounds')

# level order and plants use random.seed to reseed global random object, so I don't make separate Random for them

LEVEL_PLANTS = [
    0,
    1,  2,  3,  -1, 4,  5,  6,  7,  -1,  8,
    9,  10, 11, -1, 12, 13, 14, 15, -1, 16,
    17, 18, 19, -1, 20, 21, 22, 23, -1, 24,
    25, 26, 27, -1, 28, 29, 30, 31, -1, 32,
    33, 34, 35, -1, 36, 37, 38, 39, -1, -1
]

CONVEYOR_DEFAULTS = {
    "1-10": (0x422f60, [( 0, 20), ( 2, 20), ( 3, 15), ( 7, 20), ( 5, 10), ( 6,  5), ( 4, 10)], 10),
    "2-10": (0x422f98, [(11, 20), (14, 15), (15, 15), (12, 10), (13, 15), (10, 15), ( 8, 10)], 20),
    "3-10": (0x422fd0, [(16, 25), (17,  5), (18, 25), (19,  5), (20, 10), (21, 10), (22, 10), (23, 10)], 30),
    "4-10": (0x423008, [(16, 25), (24, 10), (31,  5), (27,  5), (26, 15), (29, 25), (28,  5), (30, 10)], 40),
    "5-10": (0x423040, [(33, 55), (39, 10), (20, 12), (32, 10), (34,  5), (14,  8)], 50),
    "shov": (0x423078, [( 0,100)]),
    "wnb2": (0x4230b0, [( 3, 85), (49, 15), (50, 15)]),
    "wnb1": (0x4230e8, [( 3, 85), (49, 15)], 5),
    "btlz": (0x423120, [(16, 25), ( 3, 15), ( 0, 25), ( 2, 35)], 25),
    "strm": (0x423158, [(16, 30), (26, 10), ( 0, 20), ( 8, 15), ( 2, 25)]),
    " 5-5": (0x423190, [(33, 50), ( 6, 25), (30, 15), ( 2, 10)], 45),
    "prtl": (0x4231c8, [( 0, 25), ( 7, 20), (22, 10), (26, 15), ( 3, 15), ( 2, 15)]),
    "clmn": (0x423200, [(33,155), (39,  5), ( 6,  5), (30, 15), (20, 10), (17, 10)]),
    "invs": (0x423238, [( 0, 25), ( 3, 15), (34,  5), (17, 15), (16, 30), (14, 10)]),
}

SEED_STRINGS = [
    "Peashooter",   "Sunflower",      "Cherry Bomb",   "Wall-nut",     "Potato Mine",  "Snow Pea",       "Chomper",    "Repeater",
    "Puff-shroom",  "Sun-shroom",     "Fume-shroom",   "Grave Buster", "Hypno-shroom", "Scaredy-shroom", "Ice-shroom", "Doom-shroom",
    "Lily Pad",     "Squash",         "Threepeater",   "Tangle Kelp",  "Jalapeno",     "Spikeweed",      "Torchwood",  "Tall-nut",
    "Sea-shroom",   "Plantern",       "Cactus",        "Blover",       "Split Pea",    "Starfruit",      "Pumpkin",    "Magnet-shroom",
    "Cabbage-pult", "Flower Pot",     "Kernel-pult",   "Coffee Bean",  "Garlic",       "Umbrella Leaf",  "Marigold",   "Melon-pult",
    "Gatling Pea",  "Twin Sunflower", "Gloom-shroom",  "Cattail",      "Winter Melon", "Gold Magnet",    "Spikerock",  "Cob Cannon",
    "Imitater",     "Explode-o-nut",  "Giant wallnut", "NONE"
]

LEVEL_STRINGS = ["Not a level",
    "1-1", "1-2", "1-3", "1-4", "1-5", "1-6", "1-7", "1-8", "1-9", "1-10",
    "2-1", "2-2", "2-3", "2-4", "2-5", "2-6", "2-7", "2-8", "2-9", "2-10",
    "3-1", "3-2", "3-3", "3-4", "3-5", "3-6", "3-7", "3-8", "3-9", "3-10",
    "4-1", "4-2", "4-3", "4-4", "4-5", "4-6", "4-7", "4-8", "4-9", "4-10",
    "5-1", "5-2", "5-3", "5-4", "5-5", "5-6", "5-7", "5-8", "5-9", "5-10"
]

global_level_index = 0

default_flags = [1, 1, 1, 1, 1, 1, 2, 1, 2, 2, 1, 2, 1, 2, 1, 1, 2, 1, 2, 2, 1, 2, 2, 3, 2, 2, 3, 2, 3, 3, 1, 2, 1, 2, 2, 1, 2, 1, 2, 2, 1, 2, 2, 3, 2, 2, 3, 2, 3, 3]
default_wavecount = [4, 6, 8, 10, 8] + [default_flags[x] * 10 for x in range(5, 50)]
default_flags = {k+1: v for k, v in enumerate(default_flags)}
default_wavecount = {k+1: v for k, v in enumerate(default_wavecount)}
default_waves_per_flag = {x+1: 10 for x in range(50)}

# these can be changed in randomiseLevelWorlds
day_levels = set(range(1, 11))
night_levels = set(range(11, 21))
pool_levels = set(range(21, 31))
fog_levels = set(range(31, 41))
roof_levels = set(range(41, 50))
roof_night_levels = {50}
world_counts = [10, 10, 10, 10, 9, 1]

default_worlds = {**{k:(k-1)//10 for k in range(1, 50)}, 35:1, 50:5}

MINIGAMES_ZOMBIE_APPEARANCES = [[26,27], [0,2,3,4,5], [0,2,4], [0,2,4,5,6,7,15,20], [0,2,4,5,6,7], [0,2,4,12,14,15],
    [0,2,4], [0,2,4], [0,2,4,5,6,7], [0,2,7,11], [0,4,7,16], [0,2,4,7], [12,13], [0,2,3,14], [0,2,4], [0,2,3,4,5,6,7,14,15,21],
    [26,27,28,29,30,31], [0,2,3,4,5,6,8], [18], [0,2,4], [0,2,4], [0,2,3,4,7,15], [0,2,4], [0,2,4,6,7,15], [0,2,4],
    [16], [0,2,4], [0,2,4], [0,2,4,6,16], [0,2,4], [0,2], [0,2,14,16], [0,2,4,21]]
AQUATIC_MINIGAMES = [3, 5, 9, 12, 13, 15, 16, 25, 31]

bytes_per_plant_string = 512 # should be a power of 2
bytes_per_zombie_string = 512 # should be a power of 2
bytes_per_game_string = 128 # should be a power of 2
n_of_plant_strings = 50 # 49 normal plants + 1 dummy string for other unusual plants
n_of_zombie_strings = 33
n_of_game_strings = 24 # more than 24 won't fit on screen

plants=[[100, 750], [50, 750], [150, 5000], [50, 3000], [25, 3000], [175, 750], [150, 750], [200, 750], [0, 750], [25, 750], [75, 750], [75, 750], [75, 3000], [25, 750], [75, 5000], [125, 5000], [25, 750], [50, 3000], [325, 750], [25, 3000], [125, 5000], [100, 750], [175, 750], [125, 3000], [0, 3000], [25, 3000], [125, 750], [100, 750], [125, 750], [125, 750], [125, 3000], [100, 750], [100, 750], [25, 750], [100, 750], [75, 750], [50, 750], [100, 750], [50, 3000], [300, 750], [250, 5000], [150, 5000], [150, 5000], [225, 5000], [200, 5000], [50, 5000], [125, 5000], [500, 5000]]
zombies=[['Basic', 1, 4000, 1, 1], ['Flag (ignore)', 1, 0, 1, 1], ['Cone', 3, 4000, 2, 1], ['Vaulter', 6, 2000, 2, 5], ['Bucket', 8, 3000, 4, 1], ['Newspaper', 11, 1000, 2, 1], ['Screen-Door', 13, 3500, 4, 5], ['Footballer', 16, 2000, 7, 5], ['Dancer', 18, 1000, 5, 5], ['Backup (ignore)', 18, 0, 1, 1], ['Ducky-Tube (ignore)', 21, 0, 1, 5], ['Snorkel', 23, 2000, 3, 10], ['Zomboni', 26, 2000, 7, 10], ['Bobsled', 26, 1500, 3, 10], ['Dolphin', 28, 1500, 3, 10], ['Jack', 31, 1000, 3, 10], ['Balloon', 33, 2000, 2, 10], ['Digger', 36, 1000, 4, 10], ['Pogo', 38, 1000, 4, 10], ['Yeti', 40, 1, 4, 1], ['Bungee', 41, 1000, 3, 10], ['Ladder', 43, 1000, 4, 10], ['Catapult', 46, 1500, 5, 10], ['Gargantuar', 48, 1500, 10, 15], ['Imp', 1, 0, 10, 1], ['Zomboss', 50, 0, 10, 1], ['Peashooter', 99, 4000, 1, 1], ['Wall-Nut', 99, 3000, 4, 1], ['Jalapeno', 99, 1000, 3, 10], ['Gatling Pea', 99, 2000, 3, 10], ['Squash', 99, 2000, 3, 10], ['Tall Nut', 99, 2000, 7, 10], ['Giga Gargantuar', 48, 6000, 10, 15]]

plant_names_container = SEED_STRINGS[:n_of_plant_strings-1] + ['Some plant'] # constant, so can pass string and not a list
plant_cooldowns_container = { index: element for index,element in enumerate([[x[1]] for x in plants][:n_of_plant_strings-1]) } # not a constant, so passing a list to keep a reference
zombie_names_container = [x[0].replace(' (ignore)', '') for x in zombies][:n_of_zombie_strings] # constant, so can pass string and not a list
wavepoints_container = { index: element for index,element in enumerate([[x[3]] for x in zombies][:n_of_zombie_strings]) } # not a constant, so passing a list to keep a reference
zombie_weight_container = { index: element for index,element in enumerate([[x[2]] for x in zombies][:n_of_zombie_strings]) } # not a constant, so passing a list to keep a reference
current_level_container = [-1]
current_level_flag_count = [1]
current_level_waves_per_flag = [10]

def randomiseLevels(seed, ngplus=False):
    global noRestrictions
    random.seed(seed)
    if ngplus:
        r = list(range(2, 51))
        random.shuffle(r)
        return [1] + r
    firstLevels=[]
    levels=[1]
    if noRestrictions.get():
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
    unused_plants   = [i for i in range(2,40)]
    if challengeMode.get() or noRestrictions.get():
        level_plants    = [(-1,1.0) for i in range(0,51)]
    else:
        level_plants    = [(-1,0.8) for i in range(0,51)]
    level_plants[0] =  (0, 0.0)
    level_plants[1] =  (1, 0.0)
    if not noRestrictions.get():
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
                    if challengeMode.get():
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
    world_weights = [0.93, 1.0, 1.0, 1.0, 1.0, 0.8]
    for i in range(1,50):
        available_levels = sorted(list(getAvailableStages(plants, levels)))
        chosen_level     = random.choices(available_levels, weights=[level_plants[l][1]*world_weights[level_worlds[l]] for l in available_levels])[0]
        world_weights[level_worlds[chosen_level]] -= 0.07 * 10 / world_counts[level_worlds[chosen_level]]
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
    # buckets, screendoors, ladders, pogos, catapults:
    buckets_are_present = [8, 9, 12, 13, 14, 17, 19, 22, 24, 27, 29, 37, 38, 39, 42, 43, 44, 46, 47, 49]
    playable_non_pot = [2, 3, 4, 6, 7, 11, 13, 14, 18, 19, 21, 23, 28, 31, 33, 34, 41, 43, 46, 47]
    # footballers, zambonis, catapults, gargs:
    footballers_are_present = [16, 17, 22, 26, 27, 29, 32, 44, 46, 47, 48, 49]
    if len(used_levels) == 0:
        level_set = {1}
    elif noRestrictions.get():
        level_set = {
        2,  3,  4,  5,  6,  7,  8,  9,  10,
        11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
        21, 22, 23, 24, 25, 26, 27, 28, 29, 30,
        31, 32, 33, 34, 35, 36, 37, 38, 39, 40,
        41, 42, 43, 44, 45, 46, 47, 48, 49, 50 }
    else:
        level_set = {5, 10, 15, 20, 25, 30, 35, 40, 45, 50} # conveyors
        plant_set = set(plants)
        
        tough_check   = len(plant_set & {2, 6, 7, 15, 17, 20, 29, 31, 35, 39}) #cherry bomb, chomper, repeater, doom, squash, jalapeno, starfruit, magnet, coffee bean, melon pult
        
        if challengeMode.get():
            tough_check = 9999
        
        has_puff              = 8  in plant_set
        has_lily              = 16 in plant_set
        has_pool_shooter      = 29 in plant_set or 18 in plant_set
        has_seapeater         = (24 in plant_set or 19 in plant_set) and has_pool_shooter #threepeater or starfruit + sea shroom or kelp
        has_fog_plants        = has_puff and (has_lily or 24 in plant_set)
        has_pot               = 33 in plant_set
        has_roof_plant        = 32 in plant_set or 39 in plant_set or has_pot

        # generalized tough check rules:
        #   1 flag: no check
        #   2 flag without bucket-type zombies: no check; but fog/roof-night level: check >= 3
        #   2 flag and bucket-type zombies are present: check >= 3; (don't care about football-type zombies); fog/roof-night level: check >= 5
        #   3 flag without bucket or football type of zombies: check >= 3; fog/roof-night level: check >= 4
        #   3 flag and either bucket or football type of zombies are present: check >= 4;  fog/roof-night level: check >= 5
        #   3 flag and both bucket and football type of zombies are present: check >= 5;  fog/roof-night level: check >= 5
        #   4 flag without bucket or football type of zombies: check >= 4; fog/roof-night level: check >= 5
        #   4 flag with either bucket or football type of zombies: check >= 5
        #   5 flag: check >= 6

        def tough_check_test(level):
            one_flag = wavecount_per_level[level] < 16
            two_flag = 16 <= wavecount_per_level[level] < 28
            three_flag = 28 <= wavecount_per_level[level] < 40
            four_flag = 40 <= wavecount_per_level[level] < 50
            if one_flag:
                requirement = 0
            elif two_flag and level not in buckets_are_present:
                requirement = 0
                if level in fog_levels or level in roof_night_levels:
                    requirement = 2 # 1 will be added later
            elif two_flag and level in buckets_are_present:
                requirement = 3
                if level in fog_levels or level in roof_night_levels:
                    requirement = 4 # 1 will be added later
            elif three_flag and level not in buckets_are_present and level not in footballers_are_present:
                requirement = 3
            elif three_flag and level in buckets_are_present and level in footballers_are_present:
                requirement = 5
            elif three_flag and (level in buckets_are_present or level in footballers_are_present):
                requirement = 4
            elif four_flag and (level not in buckets_are_present and level not in footballers_are_present):
                requirement = 4
            elif four_flag:
                requirement = 5
            else:
                requirement = 6
            if (level in fog_levels or level in roof_night_levels) and requirement < 5:
                requirement += 1
            return tough_check >= requirement

        def balloon_test(level):
            if level not in [33, 34, 39]:
                return True
            if wavecount_per_level[level] < 11 and startingWave.get() != "Instant":
                return True
            has_doom = 15 in plant_set and (35 in plant_set or level_worlds[level] in [1,3,5])
            balloon_check = len(plant_set & {2, 20}) + 2 * len(plant_set & {26, 27}) + int(has_doom)
            unreliable_cactus = balloon_check == 2 and 26 in plant_set and 16 not in plant_set
            # if cactus is the only counter without lily, check for pool/fog
            result = balloon_check >= 2 and (level_worlds[level] not in [2,3] or not unreliable_cactus)
            return result

        # day levels: nothing special
        for l in day_levels.difference({1}):
            if tough_check_test(l) and balloon_test(l):
                level_set.add(l)
                
        # night levels: puff required
        if has_puff:
            for l in night_levels:
                if tough_check_test(l) and balloon_test(l):
                    level_set.add(l)

        # pool levels:
        #   if no snorkels and dolphins, either lily or has_pool_shooter is enough
        #   if has snorkel, lily is required
        #   if has dolphin, either lily or has_seapeater is enough - but more than 30 waves require lily
        #   snorkel + dolphin require lily
        for l in pool_levels:
            a_lot_of_flags = wavecount_per_level[l] > 30
            snorkel = l in snorkel_levels
            dolphin = l in dolphin_levels
            if dolphin and not has_lily and a_lot_of_flags:
                continue
            aquatic_zombie_check_passed = (not snorkel and not dolphin and (has_lily or has_pool_shooter)) \
                or (snorkel and not dolphin and has_lily) or (dolphin and not snorkel and (has_lily or has_seapeater)) \
                or (snorkel and dolphin and has_lily)
            if aquatic_zombie_check_passed and tough_check_test(l) and balloon_test(l):
                level_set.add(l)
        
        # fog levels: 
        #   1-flag requires has_fog_plants
        #   2-flag requires has_puff and (has_lily or has_seapeater) instead
        #   3-flag or more requires has_puff and has_lily instead
        if has_puff:
            for l in fog_levels:
                one_flag = wavecount_per_level[l] < 16
                two_flag = 16 <= wavecount_per_level[l] < 28
                a_lot_of_flags = 28 <= wavecount_per_level[l]
                plant_test = (one_flag and has_fog_plants) \
                    or (two_flag and has_puff and (has_lily or has_seapeater)) \
                    or (a_lot_of_flags and has_puff and has_lily)
                snorkel = l in snorkel_levels
                dolphin = l in dolphin_levels
                aquatic_zombie_check_passed = (not snorkel and not dolphin and (has_lily or has_pool_shooter)) \
                    or (snorkel and not dolphin and has_lily) or (dolphin and not snorkel and (has_lily or has_seapeater)) \
                    or (snorkel and dolphin and has_lily)
                if plant_test and aquatic_zombie_check_passed and balloon_test(l) and tough_check_test(l):
                    level_set.add(l)
        
        # Roof levels:
        # some levels require pot and catapults are enough for some (if < 3 flags)
        # digger levels not allowed if no pot
        # special case for 5-1 (or random level with 5 pots if it's 1 flag)
        for l in roof_levels:
            one_flag = wavecount_per_level[l] < 16
            a_lot_of_flags = 24 <= wavecount_per_level[l]
            plant_test = has_pot or (l in playable_non_pot and not a_lot_of_flags and has_roof_plant)
            digger_test = has_pot or l not in [36,37]
            five_one_special_test = l == level_with_5_pots and one_flag and (has_roof_plant or len(used_levels) > 10)
            if ((plant_test and tough_check_test(l)) or five_one_special_test) and balloon_test(l) and digger_test:
                level_set.add(l)

        # Roof night levels:
        # puff and pot required + sunshroom or catapult
        if has_puff and has_pot and (9 in plant_set or has_roof_plant):
            for l in roof_night_levels:
                if tough_check_test(l) and balloon_test(l):
                    level_set.add(l)

    for l in used_levels:
        if l in level_set:
            level_set.remove(l)
    return level_set

# this function is for no random plants only, and it weights and picks levels from a passed set of available stages
def addLevel(levels, firstLevels):
    # levels are levels which are available based on current plant set
    # firstLevels are levels which were picked already
    global noRestrictions
    newLevel=1
    count=0
    countTarget=(len(firstLevels)//5)+1
    if not noRestrictions.get():
        if 10 in levels or 20 in levels or 30 in levels or 40 in levels or 41 in levels:
            while count<countTarget and newLevel not in [10, 20, 30, 40, 41]:
                count=count+1
                newLevel = random.choice(levels)
        else:
            newLevel = random.choice(levels)
        night_non_conveyors_non_2_1_levels = [l for l in (night_levels | fog_levels | roof_night_levels) if l != 11 and l % 5 != 0]
        if 11 in levels and newLevel in night_non_conveyors_non_2_1_levels: #if 2-1 hasn't been played and the next level is a night/fog level with seed select
            nightTimeLevels=[]
            count=0
            nightCount=0
            for i in range(0, len(levels)):
                if levels[i] in night_non_conveyors_non_2_1_levels:
                    nightTimeLevels.append(levels[i])
            for j in range(0, len(firstLevels)):
                if firstLevels[j] in night_non_conveyors_non_2_1_levels:
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
        if randomisePlants.get():
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


def randomiseWeights(minigames=False):
    for i in range(0, 33):
        if i!=1 and i!=9 and i!=25:
            if minigames and i == 26: # peashooter zombies in minigames are like normals
                weight=weights_rng.randint(1, 45)
            elif i>2:
                weight=weights_rng.randint(1, 60)
            #elif i==23:
            #    weight=weights_rng.randint(1, 50)
            else:
                weight=weights_rng.randint(1, 45)

            if i==19:
                weight=weights_rng.randint(1, 30) # yeti's final weight
            elif weight>50:
                weight=weight*1000
            elif weight<5:
                weight=weight*10
            else:
                weight=weight*100
            if i in zombie_weight_container:
                zombie_weight_container[i][0] = weight
            WriteMemory("int", weight, 0x69DA94 + 0x1C*i)
    WriteMemory("int", 0, 0x69DA94 + 0x1C*1)
    WriteMemory("int", 0, 0x69DA94 + 0x1C*9)

wavePointArray=[1, 1, 2, 2, 4, 2, 4, 7, 5, 0, 1, 3, 7, 3, 3, 3, 2, 4, 4, 4, 3, 4, 5, 10, 10, 0, 1, 4, 3, 3, 3, 7, 10]

def randomiseWavePoints(minigames=False):
    global randomWavePoints, wavePointArray
    for i in range(2, 33):
        if i==26 and minigames: # peashooter zombie in minigames will always have 1 point, because on Zombotany levels there are no normals
            WriteMemory("int", 1, 0x69DA88 + 0x1C*i)
            if i in wavepoints_container:
                wavepoints_container[i][0] = 1
            continue
        if i!=9 and i!=25:
            addWavePoint=0
            randomCheck=0
            while addWavePoint==0 and not randomCheck:
                if randomWavePoints.get()=="EXTREME":
                    if i==5:
                        wavePoint=(wavepoint_rng.randint(10,83))//10
                    elif i==2:
                        wavePoint=2+wavepoint_rng.randint(0,1)
                    else:
                        wavePoint=(wavepoint_rng.randint(20,82))//10
                    if wavePoint>=8:
                        wavePoint=10    
                else:
                    wavePoint=wavePointArray[i]
                    if wavePoint==10:
                        lowerBound=-3
                        upperBound=0
                    elif wavePoint>4:
                        lowerBound=-2
                        upperBound=2
                    elif wavePoint==2 and i!=5:
                        lowerBound=0
                        upperBound=1
                    else:
                        lowerBound=-1
                        upperBound=1
                    addWavePoint=wavepoint_rng.randint(lowerBound, upperBound)
                    wavePoint=wavePoint+addWavePoint
                    if wavePoint<2 and i!=5:
                        wavePoint=2
                randomCheck=wavepoint_rng.randint(0,2)
                if i==2:
                    randomCheck=1
            if i in wavepoints_container:
                wavepoints_container[i][0] = wavePoint
            WriteMemory("int", wavePoint, 0x69DA88 + 0x1C*i)

def convertToLevel(level):
    levelString=""
    levelString=levelString+str(((level-1)//10)+1)
    levelString=levelString+"-"
    secondChar=str(level)[-1]
    if secondChar=="0":
        secondChar="10"
    levelString=levelString+secondChar
    return levelString

def randomiseStartingWave(startingWave):
    if startingWave=="Instant":
        for i in range(0, 33):
            WriteMemory("int", 1, 0x69DA90 + 0x1C*i)
    else:
        for i in range(3, 33):
            if i<7 and i!=5:
                WriteMemory("int", startingwave_rng.randint(1,10), 0x69DA90 + 0x1C*i)
            elif i!=5:
                WriteMemory("int", startingwave_rng.randint(4,10), 0x69DA90 + 0x1C*i)
    
def randomiseCost():
    color_array = []
    for i in range(0, 48):
        if i!=1 and i!=8 and i!=24: #sunflower, puff, seashroom are exceptions
            divider=cost_rng.uniform(1,2)
            power=cost_rng.choice([-1, 1])
            color_array.append(round(((divider-1.0)**0.5)*127) + ((1-power)<<6))
            newCost=round(plants[i][0]*(divider**power))
            WriteMemory("int", newCost , 0x69F2C0 + 0x24*i)
        else:
            color_array.append(0)
    if costTextToggle.get():
        WriteMemory("unsigned char", color_array, 0x651290)

def randomiseCooldown():
    color_array = []
    for i in range(0, 48):
        if i!=1 and i!=8 and i!=33: #sunflower, puff, pot are exceptions
            divider=cooldown_rng.uniform(1,2)
            power=cooldown_rng.choice([1, -1])
            x = divider**power
            newCooldown=round(plants[i][1] * x)
            if i in plant_cooldowns_container:
                plant_cooldowns_container[i][0] = newCooldown
            min_green_blue_value = 110 # the smaller, the redder plants will be, 0#255 range
            # color has less green and blue components the bigger cooldown relative to base cooldown is. But also, bigger default cooldowns become redder a little bit faster
            color = clamp(1 - ((max(x, 0.5) - 0.5) / 1.5), 0, 1) \
                    * (255 - min_green_blue_value) + min_green_blue_value
            color_array.append(round(clamp(color, 0, 255)))
            WriteMemory("int", newCooldown , 0x69F2C4 + 0x24*i)
        else:
            color_array.append(255)
    WriteMemory("unsigned char", color_array, 0x6512C2)

def randomiseDavePlantCount():
    global daveActualPlantCount
    daveActualPlantCount = dave_rng.randint(1,5)
    WriteMemory("unsigned char", [
        daveActualPlantCount    # max amount of iterations to pick a plant
        ], 
        0x48420B)
    if enableDave.get() == "On + plant upgrades":
        WriteMemory("unsigned char", [
            daveActualPlantCount + 1 - daveActualPlantCount // 5
            ], 
            0x484045)

def random_sound():
    s = sounds_rng.randint(0, 103)
    while s in [14, 33, 49]: # endless sounds
        s = sounds_rng.randint(0, 103)
    return s

def sounds_decorator(f):
    addresses = {0x40d06e: 52, 0x40d0d2: 7, 0x410f44: 9, 0x4110c3: 9, 0x4111a0: 9, 0x4111cf: 8, 0x411cdc: 75, 0x41cfcd: 4,
                0x41d286: 4, 0x432a71: 94, 0x432ae0: 87, 0x432be8: 31, 0x44e196: 80, 0x44e889: 47,
                0x44e7e4: 48, 0x4585bf: 64, 0x4586c1: 1, 0x458e1d: 36, 0x458e67: 2, 0x45e313: 57, 0x45e39b: 54,
                0x45ee68: 1, 0x45f771: 3, 0x45fa9e: 4, 0x45fc0f: 63, 0x45ff04: 80, 0x4600d5: 68, 0x460aa7: 41,
                0x460d46: 40, 0x460ee4: 57, 0x4611d1: 76, 0x46130d: 63, 0x46141e: 61, 0x462c7f: 21, 0x4631f7: 83,
                0x466764: 55, 0x4667be: 65, 0x4668df: 56, 0x466933: 65, 0x466b64: 69, 0x466e6a: 30, 0x466f74: 3, 0x466fa5: 29,
                0x466ff5: 27, 0x46dd8e: 32, 0x46dded: 43, 0x46de52: 38, 0x46deb0: 62, 0x46df22: 46, 0x46df8a: 58, 0x46dfdc: 1,
                0x46ed11: 39, 0x46ee62: 3, 0x46d7f8: 1, 0x46d77d: 73, 0x46d712: 1, 0x524e1a: 68, 0x524f87: 44,
                0x52502c: 73, 0x52531f: 74, 0x5255e6: 26, 0x5257c7: 37, 0x525d7f: 66, 0x525fb0: 48, 0x526087: 74,
                0x5260f4: 78, 0x52635e: 53, 0x52645c: 50, 0x526468: 52, 0x5268f2: 53, 0x526bad: 34, 0x526c0b: 23,
                0x526e8b: 40, 0x526f9a: 47, 0x52718c: 88, 0x5274de: 3, 0x527628: 56, 0x52767c: 65, 0x527883: 3, 0x527eb3: 40,
                0x5283b0: 80, 0x528404: 83, 0x5285e9: 80, 0x52894f: 79, 0x528e9d: 100, 0x529ea1: 25, 0x52a455: 25, 0x52b3c6: 70,
                0x52b717: 72, 0x52b7c2: 72, 0x52b9c3: 68, 0x52ba7c: 5, 0x52bad1: 6, 0x52bb21: 5, 0x52ea04: 22, 0x52ebde: 23,
                0x52ec5d: 22, 0x52ed8b: 23, 0x52f80d: 19, 0x52f852: 52, 0x530696: 51, 0x5306f8: 60, 0x530756: 16, 0x5309b3: 18,
                0x53139c: 46, 0x53348f: 91, 0x53397a: 28, 0x533e66: 23}
    # this addresses are used in 1 place of so in whole game, so we always randomize them so that on the only level you hear these sounds they are different
    always_change_addresses = {0x421b91: 47, 0x421c97: 46, 0x421d04: 58, 0x421d84: 48, 0x423727: 17,
                               0x424ba0: 4, 0x462e45: 55, 0x462f2d: 20, 0x533bbd: 45, 0x533c8a: 45,
                               0x533ce2: 40, 0x534b72: 89, 0x534d8c: 89, 0x534f3a: 89, 0x5350ab: 40,
                               0x535177: 89, 0x5351cb: 44, 0x535420: 89, 0x535a4b: 93, 0x535c47: 89,
                               0x536058: 91, 0x53614e: 40, 0x536695: 40}
    if gamemode.get() == 'minigames':
        always_change_addresses |= {0x4205e7: 68, 0x42097f: 68, 0x420f60: 15, 0x4254ef: 15, 0x44e33f: 82}
    # chech for debugging - instruction is either mov esi,value or mov eax,value (use with minigames mode so all addresses are checked)
    # if instruction is esi, have to check whether esi register used down the line to not overwrite something important
    # for k in addresses|always_change_addresses:
    #     instruction = ReadMemory("unsigned char", k-1)
    #     assert(instruction in [0xBE, 0xB8])

    # random music code
    WriteMemory("unsigned char", [
        0xE8, 0x7B, 0x1B, 0xE0, 0xFF, 0x84, 0xC0, 0x0F, 0x85, 0x9B, 0x9A, 0xE0, 0xFF, 0xE9, 0x53, 0x9B, 0xE0, 0xFF, 0x90,
    ],0x651DA0)
    WriteMemory("unsigned char", [0xE9, 0x1B, 0x66, 0x1F, 0x00, 0x90], 0x45B780) # jmp 651DA0
    def wrapper(*args, **kwargs):
        f(*args, addresses=addresses, always_change_addresses=always_change_addresses, **kwargs)
    return wrapper

@sounds_decorator
def randomiseSounds(**kwargs):
    if 'addresses' not in kwargs or 'always_change_addresses' not in kwargs:
        raise ValueError('missing addresses or always_change_addresses key in kwargs')
    for addr in kwargs['addresses']:
        if sounds_rng.randint(1,100) <= 3 + randomSoundChance.get() * 7:
            WriteMemory("unsigned int", [random_sound()], addr)
        else:
            WriteMemory("unsigned int", [kwargs['addresses'][addr]], addr) # reset
    for addr in kwargs['always_change_addresses']:
        WriteMemory("unsigned int", [random_sound()], addr)
    music_track = sounds_rng.randint(1,12) # track 13 crashes for some reason
    if gamemode != 'minigames' and global_level_index == 49:
        music_track = 12 # brainiac maniac
    WriteMemory("unsigned char", [music_track], 0x45B908)
    WriteMemory("unsigned int", [music_track], 0x45B914)

untouchable_wavecount = [1, 15, 35, 50]

def randomiseWaveCount():
    # with current implementation it's impossible to make 2 flag with < 10 total waves (vanilla code will force it to be 1 flag)
    global untouchable_wavecount

    # add_level mutates changeable_levels and flags_balance, and adds results to flags_per_level, waves_per_flag, wavecount_per_level dictionaries
    def add_level(level, flag_count):
        global untouchable_wavecount
        try:
            changeable_levels.remove(level)
        except:
            pass
        flags_balance[0] += flag_count - default_flags[level]
        flags_per_level[level] = flag_count
        # unchangeable levels
        if level in untouchable_wavecount:
            flags_per_level[level] = default_flags[level]
            waves_per_flag[level] = 10 # default value - leave it at 10
            wavecount_per_level[level] = default_wavecount[level]
        # 1-2, 1-3 and 1-5 with random waves per flag (if random waves per flag is disabled, they will be in untouchable list)
        elif default_wavecount[level] < 10:
            if level == 5:
                wavecount_per_level[level] = wavecount_rng.choice([6, 7, 7, 8, 8, 9, 9, 10, 11, 12])
                waves_per_flag[level] = wavecount_per_level[level]
            else:
                default = default_wavecount[level]
                wavecount_per_level[level] = wavecount_rng.choice([int(default / 2), default - 2, default - 1, default, default + 1, default + 2, 10])
                waves_per_flag[level] = wavecount_per_level[level]
        # most of levels go here without random waves per flag:
        elif randomWaveCount.get() == "Flag count only":
            waves_per_flag[level] = 10 # default value
            wavecount_per_level[level] = waves_per_flag[level] * flags_per_level[level]
        # most of levels go here with random waves per flag:
        else:
            if wavecount_rng.randint(1, 100) <= 45: # 40.5% chance for different waves per flag
                waves_per_flag[level] = wavecount_rng.randint(6, 15)
            else:
                waves_per_flag[level] = 10
            wavecount_per_level[level] = waves_per_flag[level] * flags_per_level[level]
        # 3-5 without interesting conveyors is boring, so let's not make it any longer - but 
        # let's also not introduce dependency of level order generation on conveyor mode; so we want
        # to do all randomisation anyway, and only then check for conveyor
        if level == 25 and randomConveyors.get() != "It's Raining Seeds":
            waves_per_flag[level] = 10
            wavecount_per_level[level] = 20
            flags_per_level[level] = 2

    if randomWaveCount.get() == "Flag count only":
        untouchable_wavecount.extend([2, 3])
    if randomWaveCount.get() == "Flag count only" or level_worlds[5] not in [0, 1]:
        untouchable_wavecount.append(5)
    if not randomisePlants.get():
        untouchable_wavecount.append(41)
    changeable_levels = [x for x in range(1, 51) if x not in untouchable_wavecount] # modified in add_level
    flags_per_level = {1: 1}
    waves_per_flag = {1: 10} # 10 is globally default value in vanilla (levels with < 10 waves just have a special condition)
    wavecount_per_level = {1: 4}
    flags_balance = [0] # needs to be a list because it's modified in add_level

    # choose 1 3-flag to promoto to 5-flag
    # choose 2 3-flag to demote to 1-flag
    # choose 2 2-flags to promote to 4-flag
    # choose 2 1-flags to promote to 3-flag
    # But: conveyors are forbidden to go up by 2 flags or down by 2 flags,
    #   (3-4, 3-7, 3-9, 5-4, 5-7, 5-9 are quite likely to move +- 2 flags because of that).
    # + levels 1-2, 1-3, 1-5 are fobidden to go up in amount of flags
    # that makes balance = +6 flags
    # choose 6 other levels to demote by 1 flag to restore the balance
    # choose 6 other levels to demote by 1 flag and 6 other levels to promote by 1 flag
    # 25 levels to change in total
    for l in untouchable_wavecount:
        add_level(l, default_flags[l])

    flexible_three_flags = [24, 27, 29, 44, 47, 49]
    plus_or_minus_two_flags = wavecount_rng.sample(flexible_three_flags, 3)
    add_level(plus_or_minus_two_flags[0], 5)
    add_level(plus_or_minus_two_flags[1], 1)
    add_level(plus_or_minus_two_flags[2], 1)

    four_flag_candidates = [x for x in range(1, 51) if default_flags[x] == 2 and x not in untouchable_wavecount and x % 5 != 0]
    four_flags = wavecount_rng.sample(four_flag_candidates, 2)
    add_level(four_flags[0], 4)
    add_level(four_flags[1], 4)

    three_flag_candidates = [x for x in range(1, 51) if default_flags[x] == 1 and default_wavecount[x] >= 10\
        and x not in untouchable_wavecount and x % 5 != 0 and (x != 41 or randomisePlants.get())]
    three_flags = wavecount_rng.sample(three_flag_candidates, 2)
    add_level(three_flags[0], 3)
    add_level(three_flags[1], 3)

    remove_flag_candidates = [x for x in changeable_levels if default_flags[x] > 1]
    flag_removals = wavecount_rng.sample(remove_flag_candidates, 6)
    for l in flag_removals:
        add_level(l, default_flags[l] - 1)
        
    random_removals_candidates = [x for x in changeable_levels if default_flags[x] > 1]
    random_flag_removals = wavecount_rng.sample(random_removals_candidates, 6)
    for l in random_flag_removals:
        add_level(l, default_flags[l] - 1)

    random_extra_flag_candidates = [x for x in changeable_levels if default_wavecount[x] >= 10]
    random_extra_flags = wavecount_rng.sample(random_extra_flag_candidates, 6)
    for l in random_extra_flags:
        add_level(l, default_flags[l] + 1)

    remaining_levels = changeable_levels[:] # add_level mutates changeable_levels, so we can't just use for loop
    for l in remaining_levels:
        add_level(l, default_flags[l])
    
    assert len(changeable_levels) == 0 and flags_balance[0] == 0

    return (flags_per_level, wavecount_per_level, waves_per_flag)


def randomiseLevelWorlds():
    global day_levels, night_levels, pool_levels, fog_levels, roof_levels, roof_night_levels, world_counts

    def filter_candidates(level, candidates):
        candidates = set(candidates)
        if level == 5:
            candidates.discard(3)
            candidates.discard(4)
            candidates.discard(5)
            if shopless.get() or gamemode.get() != "adventure":
                candidates.discard(2) # no pool cleaners or level too long in ng+
        if level == 15:
            candidates.discard(4)
            candidates.discard(5)
        if level == 25:
            candidates.discard(4)
            candidates.discard(5)
        if level == 45: # bungee drops are bugged with pool (work fine on day/night apparently)
            candidates.discard(2)
            candidates.discard(3)
        return list(candidates)
    
    worlds = {}
    untouchable = {1, 2, 3, 4, 35, 50}
    if not randomisePlants.get():
        untouchable.add(41)
    if randomConveyors.get() == "False":
        for i in range(1, 51):
            if i % 5 == 0:
                untouchable.add(i)
    balance = [0, 0, 0, 0, 0]
    levels = list(range(1,51))
    worlds_rng.shuffle(levels)
    for i in levels:
        if i in untouchable or worlds_rng.randint(1, 100) > randomWorldChance.get():
            worlds[i] = default_worlds[i]
            continue
        candidates = filter_candidates(i, [k for k,v in enumerate(balance) if v < 0 and k != default_worlds[i]])
        if len(candidates) == 0:
            candidates = filter_candidates(i, [k for k,v in enumerate(balance) if v == 0 and k != default_worlds[i]])
        if len(candidates) > 0:
            new_world = worlds_rng.choice(candidates)
        else:
            candidates = filter_candidates(i, [x for x in range(5) if x != default_worlds[i]])
            max_balance = max(balance) + 1
            new_world = worlds_rng.choices(candidates, weights=[max_balance-balance[x] for x in candidates])[0]
        balance[default_worlds[i]] -= 1
        balance[new_world] += 1
        worlds[i] = new_world
    roof_with_5_pots = 41 if worlds[41] == 4 else worlds_rng.choice([k for k,v in worlds.items() if v == 4 and k % 5 != 0])
    # change some fog levels to roof night, because fog is boring
    roof_night_candidates = [k for k,v in worlds.items() if v == 3 and k not in untouchable and k not in [5,25,40]]
    if len(roof_night_candidates) > 0:
        roof_night_levels = worlds_rng.sample(roof_night_candidates, min(3, len(roof_night_candidates)))
        for l in roof_night_levels:
            worlds[l] = 5
    assert len(worlds) == 50
    assert worlds[roof_with_5_pots] == 4
    day_levels = {k for k,v in worlds.items() if v == 0}
    night_levels = {k for k,v in worlds.items() if v == 1}
    pool_levels = {k for k,v in worlds.items() if v == 2}
    fog_levels = {k for k,v in worlds.items() if v == 3}
    roof_levels = {k for k,v in worlds.items() if v == 4}
    roof_night_levels = {k for k,v in worlds.items() if v == 5}
    world_counts = [len(day_levels), len(night_levels), len(pool_levels), len(fog_levels), len(roof_levels), len(roof_night_levels)]
    return (worlds, roof_with_5_pots)

def reset_zombie_spawn():
    zombies_allowed = [
		[
			1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
			1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
			1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
			1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
			1, 1, 1, 1, 1, 1, 1, 1, 1, 1,],
		    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
			1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
			1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
			1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
			1, 1, 1, 1, 1, 1, 1, 1, 1, 1,],
		    [0, 0, 1, 1, 1, 1, 1, 1, 1, 1,
			0, 1, 1, 1, 1, 1, 1, 1, 1, 1,
			1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
			1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
			1, 1, 1, 1, 1, 1, 1, 1, 1, 1,],
			[0, 0, 0, 0, 0, 1, 1, 0, 1, 1,
			0, 0, 0, 1, 1, 0, 0, 0, 0, 0,
			0, 0, 0, 1, 0, 0, 0, 0, 1, 0,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 1, 0, 0, 0, 0, 0, 0, 0, 0,],
			[0, 0, 0, 0, 0, 0, 0, 1, 1, 1,
			0, 1, 0, 0, 1, 0, 0, 0, 0, 0,
			0, 1, 0, 1, 0, 0, 1, 0, 1, 1,
			0, 0, 0, 0, 0, 0, 1, 0, 1, 1,
			0, 1, 0, 0, 1, 0, 0, 0, 1, 1,],
			[0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			1, 1, 0, 0, 1, 0, 0, 0, 0, 0,
			0, 1, 0, 1, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
			[0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 1, 1, 0, 0, 1, 0, 1, 1,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
			[0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 1, 1, 0, 0, 1,
			0, 1, 0, 0, 1, 0, 0, 0, 0, 0,
			0, 1, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 1, 0, 0, 0, 0, 0, 0,],
			[0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 0, 0, 1, 1, 1,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
			[0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 0, 0, 1, 1, 1,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
	        [],
			[0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 1, 1, 1, 0, 1, 0, 0, 1,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
			[0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 1, 1, 0, 1, 1,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
			[0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 1, 1, 0, 1, 1,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
			[0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 0, 0, 1, 1, 1,
			0, 0, 0, 1, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
			[0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			1, 1, 0, 0, 0, 0, 1, 0, 0, 1,
			0, 0, 0, 0, 0, 0, 0, 0, 1, 1,],
			[0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 1, 1, 0, 0, 0, 0, 1, 1,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
			[0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 1, 1, 0, 0, 1,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0,],
			[0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 0, 0, 1, 1, 1,
			0, 0, 0, 1, 0, 0, 0, 0, 0, 0,],
            [],
			[0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			1, 1, 0, 0, 0, 0, 1, 0, 1, 1,],
			[0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 1, 1, 1, 0, 1, 0, 1, 1,],
			[0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 1, 1, 0, 1, 1,],
			[0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 0, 0, 1, 1, 1,],
			[0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 0, 0, 1, 1, 1,],
            [], [], [], [], [], [], [], []
    ]
    write_list = []
    for idx,val in enumerate(zombies_allowed):
        write_list.append(idx)
        if len(val) == 0:
            write_list.extend([0] * 50)
        else:
            write_list.extend(val)
        WriteMemory("int", write_list, 0x6A35B0)

def reset_from_random_worlds():
    snorkel = [1 if i in [23, 24, 25, 27, 30] else 0 for i in range(1,51)] #default snorkels
    dolphin = [1 if i in [28, 29, 30, 34] else 0 for i in range(1,51)] # default dolphins
    WriteMemory("int", snorkel, 0x6A35B4 + 0xCC*11)
    WriteMemory("int", dolphin, 0x6A35B4 + 0xCC*14)
    WriteMemory("int", 23, 0x69DA8C + 0x1C*11) # starting level
    WriteMemory("int", 28, 0x69DA8C + 0x1C*14) # starting level
    # default code for choosing level world
    WriteMemory("unsigned char", 
    [
        0x83, 0xFA, 0x0A, 0x7F, 0x0F, 0xC7, 0x86, 0x4C, 0x55, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xE9,
        0x97, 0x00, 0x00, 0x00, 0x83, 0xFA, 0x14, 0x7F, 0x0B, 0x89, 0xAE, 0x4C, 0x55, 0x00, 0x00, 0xE9,
        0x87, 0x00, 0x00, 0x00, 0x83, 0xFA, 0x1E,
    ], 0x40A58A)
    # default graves
    WriteMemory("unsigned char", [11] ,0x40A94D)
    WriteMemory("unsigned char", [12] ,0x40A956)
    WriteMemory("unsigned char", [13] ,0x40A95F)
    WriteMemory("unsigned char", [14] ,0x40A968)
    WriteMemory("unsigned char", [16] ,0x40A971)
    WriteMemory("unsigned char", [17] ,0x40A983)
    WriteMemory("unsigned char", [18] ,0x40A97A)
    WriteMemory("unsigned char", [19] ,0x40A988)
    WriteMemory("unsigned char", [20] ,0x40A98D)
    # default fog
    WriteMemory("unsigned char", [31] ,0x41C1E9)
    WriteMemory("unsigned char", [32] ,0x41C1EE)
    WriteMemory("unsigned char", [36] ,0x41C1F3)
    WriteMemory("unsigned char", [37] ,0x41C1F8)
    WriteMemory("unsigned char", [40] ,0x41C1FD)
    WriteMemory("unsigned char", [31] ,0x40B96B)
    WriteMemory("unsigned char", [32] ,0x40B970)
    WriteMemory("unsigned char", [36] ,0x40B975)
    WriteMemory("unsigned char", [37] ,0x40B97A)
    WriteMemory("unsigned char", [40] ,0x40B97F)
    WriteMemory("unsigned char", [31] ,0x41A492)
    WriteMemory("unsigned char", [32] ,0x41A49C)
    WriteMemory("unsigned char", [36] ,0x41A4AB)
    WriteMemory("unsigned char", [37] ,0x41A4AF)
    WriteMemory("unsigned char", [40] ,0x41A4B4)
    # default pool ambush
    WriteMemory("unsigned char", [21] ,0x412916)
    WriteMemory("unsigned char", [22] ,0x41291B)
    WriteMemory("unsigned char", [31] ,0x412920)
    WriteMemory("unsigned char", [32] ,0x412925)
    WriteMemory("unsigned char", [23] ,0x41292A)
    WriteMemory("unsigned char", [24] ,0x41292F)
    WriteMemory("unsigned char", [25] ,0x412934)
    WriteMemory("unsigned char", [33] ,0x412939)
    WriteMemory("unsigned char", [34] ,0x41293E)
    WriteMemory("unsigned char", [35] ,0x412943)
    # default roof ambush
    WriteMemory("unsigned char", [41] ,0x412C4E)
    WriteMemory("unsigned char", [42] ,0x412C53)
    WriteMemory("unsigned char", [43] ,0x412C58)
    WriteMemory("unsigned char", [44] ,0x412C5D)
    WriteMemory("unsigned char", [45] ,0x412C62)
    # pots
    WriteMemory("unsigned char", [41] ,0x43B709)
    WriteMemory("unsigned char", [42] ,0x43B71D)
    WriteMemory("unsigned char", [43] ,0x43B72C)
    WriteMemory("unsigned char", [50] ,0x43B731)

def redistribute_aquatic_zombies():
    # snorkel appears on 5 of pool levels, and none of fog levels
    # dolphins appear on 3 of pool levels, and 1 of fog levels
    # we also change starting level to make sure they don't spawn on 3-3/3-8
    
    # find snorkels and dolphins which are allowed to stay
    snorkel_levels = (pool_levels & {23, 24, 25, 27, 30}) | (fog_levels & {23, 24, 25, 27, 30})
    snorkel_count = len(snorkel_levels)
    dolphin_levels = (pool_levels & {28, 29, 30, 34}) | (fog_levels & {28, 29, 30, 34})
    dolphin_count = len(dolphin_levels)
    # add remaining snorkels and dolphins - 1-5 is forbidden from having them
    snorkel_potential_levels = pool_levels.difference({5, 23, 24, 25, 27, 30})
    dolphin_potential_levels = pool_levels.difference({5, 28, 29, 30, 34})
    dolphin_add_to_fog_level = 34 not in fog_levels
    for i in range(5 - snorkel_count):
        level = worlds_rng.choice(list(snorkel_potential_levels))
        snorkel_levels.add(level)
        snorkel_potential_levels.remove(level)
    for i in range(4 - dolphin_count - int(dolphin_add_to_fog_level)):
        level = worlds_rng.choice(list(dolphin_potential_levels))
        dolphin_levels.add(level)
        dolphin_potential_levels.remove(level)
    if dolphin_add_to_fog_level:
        potential_levels = fog_levels.difference({5, 34})
        level = worlds_rng.choice(list(potential_levels))
        dolphin_levels.add(level)
    # write levels to memory
    for i in range(1,51):
        WriteMemory("int", int(i in snorkel_levels), 0x6A35B0 + 0xCC*11 + 4*i)
        WriteMemory("int", int(i in dolphin_levels), 0x6A35B0 + 0xCC*14 + 4*i)

     # set starting level
    if 23 not in pool_levels and 23 not in fog_levels:
        WriteMemory("int", min(snorkel_levels), 0x69DA8C + 0x1C*11)
        zombies[11][1] = min(snorkel_levels)
    if 28 not in pool_levels and 28 not in fog_levels:
        WriteMemory("int", min(dolphin_levels), 0x69DA8C + 0x1C*14)
        zombies[14][1] = min(dolphin_levels)
    
    return (snorkel_levels, dolphin_levels)
    
def randomiseGraves():
    # graves are restored in reset_from_random_worlds
    # there are 3 slots for a bit of graves, 2 for average graves, and 3 for a lot of graves - everything else gets max graves (default 2-10)
    # I don't want to write code for preserving min graves for 2-1 if it's night, but changing it if it's not night, etc for other night levels
    night_non_conveyors = [l for l in night_levels if l % 5 != 0]
    worlds_rng.shuffle(night_non_conveyors)
    a_bit_of_graves = night_non_conveyors[:3]
    average_graves = night_non_conveyors[3:5]
    a_lot_of_graves = night_non_conveyors[5:8] # slices don't throw if index out of bounds
    # writing exactly 1 byte per number
    WriteMemory("unsigned char", [a_bit_of_graves[0] if len(a_bit_of_graves) > 0 else 0] ,0x40A94D)
    WriteMemory("unsigned char", [a_bit_of_graves[1] if len(a_bit_of_graves) > 1 else 0] ,0x40A956)
    WriteMemory("unsigned char", [a_bit_of_graves[2] if len(a_bit_of_graves) > 2 else 0] ,0x40A95F)
    WriteMemory("unsigned char", [average_graves[0] if len(average_graves) > 0 else 0] ,0x40A968)
    WriteMemory("unsigned char", [average_graves[1] if len(average_graves) > 1 else 0] ,0x40A971)
    WriteMemory("unsigned char", [a_lot_of_graves[0] if len(a_lot_of_graves) > 0 else 0] ,0x40A983)
    WriteMemory("unsigned char", [a_lot_of_graves[1] if len(a_lot_of_graves) > 1 else 0] ,0x40A97A)
    WriteMemory("unsigned char", [a_lot_of_graves[2] if len(a_lot_of_graves) > 2 else 0] ,0x40A988)
    WriteMemory("unsigned char", [0] ,0x40A98D) # max graves, but we change >= 20 condition to >= 0 to actually catch every other level

def randomiseFog():
    # fog is restored in reset_from_random_worlds
    # there's one level with min fog, range of levels with average fog, and a range with max fog
    # if 1-5 is a fog, it is guaranteed to be min fog - else random conveyor other than 4-10 - else 4-1 is min fog - else random level
    # the rest of levels are split in half at median point between average and big fog
    if level_worlds[5] == 3:
        min_fog = 5
    else:
        fog_conveyors = [l for l in fog_levels if l % 5 == 0 and l != 40]
        if len(fog_conveyors) > 0:
            min_fog = worlds_rng.choice(fog_conveyors)
        else:
            if level_worlds[31] == 3:
                min_fog = 31
            else:
                candidates = [l for l in fog_levels if l != 40]
                min_fog = worlds_rng.choice(candidates)
    remaining_fog_levels = [l for l in fog_levels if l != min_fog and l != 40]
    median_point = int(median(remaining_fog_levels))
    # there are 3 places where we need to write it, because of some inlined function calls
    # LeftFogColumn
    WriteMemory("unsigned char", [min_fog] ,0x41C1E9)
    WriteMemory("unsigned char", [0] ,0x41C1EE)
    WriteMemory("unsigned char", [median_point] ,0x41C1F3)
    WriteMemory("unsigned char", [median_point+1] ,0x41C1F8)
    WriteMemory("unsigned char", [60] ,0x41C1FD)
    # InitLevel
    WriteMemory("unsigned char", [min_fog] ,0x40B96B)
    WriteMemory("unsigned char", [0] ,0x40B970)
    WriteMemory("unsigned char", [median_point] ,0x40B975)
    WriteMemory("unsigned char", [median_point+1] ,0x40B97A)
    WriteMemory("unsigned char", [60] ,0x40B97F)
    # ClearFogAroundPlant
    WriteMemory("unsigned char", [min_fog] ,0x41A492)
    WriteMemory("unsigned char", [0] ,0x41A49C)
    WriteMemory("unsigned char", [median_point] ,0x41A4AB)
    WriteMemory("unsigned char", [median_point+1] ,0x41A4AF)
    WriteMemory("unsigned char", [60] ,0x41A4B4)

def randomisePoolAmbush():
    # is restored in reset_from_random_worlds
    # 2 pool levels + 2 fog levels with min ambush, 3 pool + 3 fog levels with average ambush, and the rest is max ambush
    pool = list(pool_levels)
    fog = list(fog_levels)
    worlds_rng.shuffle(pool)
    worlds_rng.shuffle(fog)
    min_ambush = pool[:2] + fog[:2]
    average_ambush = pool[2:5] + fog[2:5]
    WriteMemory("unsigned char", [min_ambush[0] if len(min_ambush) > 0 else 0] ,0x412916)
    WriteMemory("unsigned char", [min_ambush[1] if len(min_ambush) > 1 else 0] ,0x41291B)
    WriteMemory("unsigned char", [min_ambush[2] if len(min_ambush) > 2 else 0] ,0x412920)
    WriteMemory("unsigned char", [min_ambush[3] if len(min_ambush) > 3 else 0] ,0x412925)
    WriteMemory("unsigned char", [average_ambush[0] if len(average_ambush) > 0 else 0] ,0x41292A)
    WriteMemory("unsigned char", [average_ambush[1] if len(average_ambush) > 1 else 0] ,0x41292F)
    WriteMemory("unsigned char", [average_ambush[2] if len(average_ambush) > 2 else 0] ,0x412934)
    WriteMemory("unsigned char", [average_ambush[3] if len(average_ambush) > 3 else 0] ,0x412939)
    WriteMemory("unsigned char", [average_ambush[4] if len(average_ambush) > 4 else 0] ,0x41293E)
    WriteMemory("unsigned char", [average_ambush[5] if len(average_ambush) > 5 else 0] ,0x412943)

def randomiseRoofAmbush():
    # is restored in reset_from_random_worlds
    # 2 levels with min ambush, 3 levels with average, the rest is max ambush
    candidates = list(roof_levels | roof_night_levels)
    worlds_rng.shuffle(candidates)
    min_ambush = candidates[:2]
    average_ambush = candidates[2:5]
    WriteMemory("unsigned char", [min_ambush[0] if len(min_ambush) > 0 else 0] ,0x412C4E)
    WriteMemory("unsigned char", [min_ambush[1] if len(min_ambush) > 1 else 0] ,0x412C53)
    WriteMemory("unsigned char", [average_ambush[0] if len(average_ambush) > 0 else 0] ,0x412C58)
    WriteMemory("unsigned char", [average_ambush[1] if len(average_ambush) > 1 else 0] ,0x412C5D)
    WriteMemory("unsigned char", [average_ambush[2] if len(average_ambush) > 2 else 0] ,0x412C62)

def randomisePots():
    # is restored in reset_from_random_worlds
    # level with 5 pots is predetermined because it can be used in level order generation and world/wavecount rando
    # level with 4 pots is random, everything else will have 3 pots.
    # game doesn't check whether level is roof before calling the function we modify, so we set range of levels to 0-0,
    # so it never triggers - and down the line code comes to else if (mBoard->StageHasRoof()), where it will make 3 pots
    WriteMemory("unsigned char", [level_with_5_pots] ,0x43B709)
    candidates = [l for l in (roof_levels | roof_night_levels) if l != level_with_5_pots]
    four_pots = worlds_rng.choice(candidates)
    WriteMemory("unsigned char", [four_pots] ,0x43B71D)
    WriteMemory("unsigned char", [0] ,0x43B72C)
    WriteMemory("unsigned char", [0] ,0x43B731)

def generateZombies(levels, level_plants):
    zombiesToRandomise=[[]]
    plantsInOrder=[]
    for i in range(0, len(levels)):
        plantsInOrder.append(level_plants[levels[i]])
    for i in range(1, len(levels)):
        level = levels[i]
        if level==50 or level==15 or level==35:
            zombiesToRandomise.append([]) # no rando on those levels
            continue
        current_plants = set(plantsInOrder[0:i])
        has_lily              = 16 in current_plants
        has_pool_shooter      = 29 in current_plants or 18 in current_plants
        has_seapeater         = (24 in current_plants or 19 in current_plants) and has_pool_shooter #threepeater or starfruit + sea shroom or kelp
        has_pot               = 33 in current_plants
        has_doom              = 15 in current_plants and (35 in current_plants or level_worlds[level] in [1,3,5])
        has_instant           = 2 in current_plants or 17 in current_plants or 20 in current_plants or has_doom
        balloon_check = len(current_plants & {2, 20}) + 2 * len(current_plants & {26, 27}) + int(has_doom)
        unreliable_cactus = balloon_check == 2 and 26 in current_plants and 16 not in current_plants
        # if cactus is the only counter, check for pool/fog
        balloon_test = balloon_check >= 2 and (level_worlds[level] not in [2,3] or not unreliable_cactus)
        currentZombies=[]
        for j in range(2, 33):
            if level == 5: # let's not make conveyor basically impossible to beat even in no restriction
                if j == 11 or j == 14:
                    continue
            if j==9 or j==10 or j==24 or j==25:
                continue
            elif zombies_rng.randint(0, 11) != 0:
                continue
            elif (j==11 or j==14) and level_worlds not in [2,3]:
                continue
            elif zombies[j][1]==level:
                continue
            elif level==45 and j in [11, 12, 13, 14, 16, 17, 18, 20, 22, 23, 32]:
                continue
            elif noRestrictions.get():
                currentZombies.append(j)
            elif j==11 and not has_lily:
                continue
            elif j==14 and not (has_lily or has_seapeater):
                continue
            elif j==14 and wavecount_per_level[level] >= 30 and not has_lily:
                continue
            elif j==16 and not balloon_test:
                continue
            elif j==16 and level % 5 == 0:
                continue
            elif j==17 and level_worlds[level] in [4,5] and not has_pot:
                continue
            # gargs and giga-gargs are excluded from extremenly long levels + can get removed from 5-9 in such case
            elif j==23 and (not has_instant or (wavecount_per_level[level] > 45 and level not in [48,49])):
                continue
            elif j==32 and (not has_instant or wavecount_per_level[level] > 45):
                continue
            else:
                if j==32:
                    if not zombies_rng.randint(0, 6):
                        currentZombies.append(j)
                else:
                    currentZombies.append(j)
        zombiesToRandomise.append(currentZombies)
    return zombiesToRandomise

def randomiseZombies(zombiesToRandomise, currentLevel, levels):
    for i in range(0, 33):
        WriteMemory("int", zombies[i][1], 0x69DA8C + 0x1C*i)
    currentZombies=zombiesToRandomise[currentLevel]
    for i in range(0, len(currentZombies)):
        zombieState=ReadMemory("bool", 0x6A35B0 + 0xCC*currentZombies[i] + 0x4*levels[currentLevel])
        WriteMemory("int", 1, 0x69DA8C + 0x1C*currentZombies[i])     
        WriteMemory("bool", not zombieState, 0x6A35B0 + 0xCC*currentZombies[i] + 0x4*levels[currentLevel])
    return currentZombies

def randomiseZombiesMinigames():
    base_address = 0x4258aa
    for i in range(33):
        address = base_address + i * 33
        default_zombies = MINIGAMES_ZOMBIE_APPEARANCES[i]
        result = [(1 if x in default_zombies else 0) for x in range(33)]
        for j in range(2,33):
            if j in default_zombies and 0 not in default_zombies: # levels like pogo party, bobsled, zombotany
                continue
            if j==9 or j==10 or j==24 or j==25:
                continue
            if (j==11 or j==14) and (i not in AQUATIC_MINIGAMES):
                continue
            if i==32 and j in [11, 12, 13, 14, 16, 17, 18, 20, 22, 23, 32]: # bungee blitz
                continue
            if j==16 and i in [1, 9, 17, 31]: # balloon
                continue
            if zombies_rng.randint(0, (9 if i != 12 and i != 25 and i != 18 else 15)) != 0: # bonanza, pogo, air raid are different
                continue
            if j==32:
                if not zombies_rng.randint(0, 3):
                    result[j] = 1
            else:
                result[j] = 1 - result[j]
        WriteMemory("unsigned char", result, address)

def writeConveyor(addr, conveyor_data):
    out    = [0 for i in range(56)]
    for i in conveyor_data:
        scale     = max(int(math.log2(max(i[1],1)))-5,0)
        out[i[0]] = (scale<<6) + (i[1]>>scale)
    WriteMemory("unsigned char", out, addr)

def randspread(n, k):
    r          = [random.random() for i in range(k)]
    m          = n / sum(r)
    normalised = [i * m for i in r]
    if isinstance(n, int):
        normalised = [int(i) for i in normalised]
        modify     = n-sum(normalised)
        for i in range(modify):
            normalised[random.randint(0,k-1)] += 1
    return normalised

def randomiseConveyors(in_seed):
    seed      = in_seed + "conveyor"
    rng_state = random.getstate() #save rng state
    random.seed(seed)
    
    for level in CONVEYOR_DEFAULTS:
        to_randomise = CONVEYOR_DEFAULTS[level][1]
        d_plant_set = set()
        d_dict      = {}
        r_plant_set = {38}    #every level should have marigolds!
        r_dict      = {38: 2} #with a weight of like 2 tho

        for i in to_randomise: # loading default plants for this level
            d_plant_set.add(i[0])
            d_dict[i[0]] = i[1]
        
        d_balloon_counters  = sorted(list(d_plant_set & {26,27,43}))                #cactus, blover, cattail
        d_pea_s_plants      = sorted(list(d_plant_set & {0, 5, 8, 13,24,28,32,34})) #peashooter, snow pea, puff, scaredy, seashroom, split pea, cabbage, kernel
        d_pea_s_high_plants = sorted(list(d_plant_set & {7, 10,18,29,39}))          #repeater, fume, threepeater, starfruit, melon
        d_znuts             = sorted(list(d_plant_set & {3, 23,30, 36}))                #wallnut, tallnut, pumpkin, garlic
        d_instas            = sorted(list(d_plant_set & {4, 12,14,19,21}))          #mine, hypno, ice, kelp, spikeweed
        d_ginstas           = sorted(list(d_plant_set & {2, 15,17,20,31}))          #cherry, doom, squash, jalapeno, magnet
        #d_zomboss           = sorted(list(d_plant_set & {2, 10, 15, 30}))
        d_passthrough       = sorted(list(d_plant_set & {6, 11,16,22,32,33,49,50}))    #chomper, grave buster, lily, torchwood, cabbage, pot, explode o nut, giant wallnut        
        blackened_chance = random.choices([0.2,1.0],weights=[1,19])[0]
        peter_chance     = random.choices([0.2,1.0],weights=[1,19])[0]
        
        if randomWorld.get() and len(CONVEYOR_DEFAULTS[level]) > 2 and gamemode.get() != 'minigames': # has an extra field specifying adventure mode level
            has_water = level_worlds[CONVEYOR_DEFAULTS[level][2]] in [2,3]
            on_roof = level_worlds[CONVEYOR_DEFAULTS[level][2]] in [4,5]
            at_night = level_worlds[CONVEYOR_DEFAULTS[level][2]] in [1,3,5]
            # removing lily/pot/buster from d_passthrough if they are not allowed
            if not has_water and 16 in d_passthrough:
                d_passthrough.remove(16)
            if not on_roof and 33 in d_passthrough:
                d_passthrough.remove(33)
            if (not at_night or (at_night and has_water)) and 11 in d_passthrough:
                d_passthrough.remove(11)
            if has_water and 16 not in d_passthrough:
                d_passthrough.append(16)
                d_dict[16] = 40
            if on_roof and 33 not in d_passthrough:
                d_passthrough.append(33)
                d_dict[33] = 80
            if at_night and not has_water and 11 not in d_passthrough:
                d_passthrough.append(11)
                d_dict[11] = 25
        else:
            has_water           = 16 in d_plant_set
            on_roof             = 33 in d_plant_set
            at_night            = len(d_plant_set & {8,10,11,12,13,14,15,24,31}) > 0   #puff, fume, grave buster, hypno, scaredy, ice, doom, seashroom, magnet
        

        if randomConveyors.get()!="It's Raining Seeds":

            for i in d_passthrough: #keep a few plants the same
                r_plant_set.add(i)
                r_dict[i] = int(d_dict[i] * random.uniform(0.7,1.3))
            
            if level != "wnb1" and level != "wnb2":
                if len(d_balloon_counters) > 0:
                    balloon_weights    = 0.
                    allowed_b_counters = [26,27,43] if has_water else [26,27]
                    wmul               = [1.0,2.0,0.4]
                    for i in d_balloon_counters:
                        balloon_weights += d_dict[i]/wmul[allowed_b_counters.index(i)]
                    balloon_weights *= random.uniform(0.9,1.3) * blackened_chance
                    n_of_plants = min(len(d_balloon_counters), len(allowed_b_counters))
                    r_balloon_counters = random.sample(allowed_b_counters, k=n_of_plants)
                    r_balloon_weights  = randspread(int(balloon_weights), n_of_plants)
                    for i in range(n_of_plants):
                        r_plant_set.add(r_balloon_counters[i])
                        r_dict[r_balloon_counters[i]] = int(r_balloon_weights[i]*wmul[allowed_b_counters.index(r_balloon_counters[i])])
                
                if len(d_pea_s_plants) > 0:
                    peas_weight  = 0.
                    allowed_peas = ([0, 5, 26,28,32,34,8, 13,24] if has_water else [0, 5, 26,28,32,34,8, 13]) if at_night else [0, 5, 26,28,32,34]
                    for i in d_pea_s_plants:
                        peas_weight += d_dict[i]
                    if 26 in r_dict:
                        peas_weight = max(0,peas_weight-r_dict[26])
                    peas_weight  *= random.uniform(0.6,1.4)
                    n_of_plants = min(len(d_pea_s_plants), len(allowed_peas))
                    r_peas        = random.sample(allowed_peas, k=n_of_plants)
                    r_pea_weights = randspread(int(peas_weight), n_of_plants)
                    for i in range(n_of_plants):
                        r_plant_set.add(r_peas[i])
                        if r_peas[i] in r_dict:
                            r_dict[r_peas[i]] += r_pea_weights[i]
                        else:
                            r_dict[r_peas[i]]  = r_pea_weights[i]
                
                if len(d_pea_s_high_plants) == 1:
                    allowed_hpeas = [7, 10,18,29,39]
                    weights       = [1.,1.,1.,1.,1.]
                    wmul          = [1.5,1.5,1.0,2.0,1.0]
                    weights[allowed_hpeas.index(d_pea_s_high_plants[0])] *= 3.
                    if d_pea_s_high_plants[0] == 39: #if melon is the strong dps plant, its probably a good idea to keep it that way
                        weights = [0.,0.,0.,0.,1.]
                    if not at_night:
                        weights[1] = 0.
                    d_pea_s_high_plant = random.choices(allowed_hpeas,weights=weights)[0]
                    r_plant_set.add(d_pea_s_high_plant)
                    r_dict[d_pea_s_high_plant] = int(d_dict[d_pea_s_high_plants[0]] * wmul[allowed_hpeas.index(d_pea_s_high_plant)] / wmul[allowed_hpeas.index(d_pea_s_high_plants[0])] * random.uniform(0.8,1.2) * peter_chance)
                
                if len(d_znuts) > 0:
                    nuts_weight  = 0.
                    allowed_nuts = [3,23,30,36]
                    for i in d_znuts:
                        nuts_weight += d_dict[i]
                    nuts_weight  *= random.uniform(0.6,1.4)
                    n_of_plants = min(len(d_znuts), len(allowed_nuts))
                    r_nuts        = random.sample(allowed_nuts, k=n_of_plants)
                    r_nut_weights = randspread(int(nuts_weight), n_of_plants)
                    for i in range(n_of_plants):
                        r_plant_set.add(r_nuts[i])
                        r_dict[r_nuts[i]]  = r_nut_weights[i]
                
                if level != "5-10":
                    if len(d_instas) > 0:
                        instas_weight  = 0.
                        allowed_instas = ([4,  19, 12, 14]  if has_water else [4,  12, 14]) if at_night else ([4,  19] if has_water else [4])
                        wmul           =  [2.0,2.0,1.4,1.0] if has_water else [2.0,1.4,1.0]
                        for i in d_instas:
                            if i in allowed_instas:
                                instas_weight += d_dict[i]/wmul[allowed_instas.index(i)]
                            else:
                                instas_weight += d_dict[i]/2.5
                        instas_weight     *= random.uniform(0.6,1.4)
                        n_of_plants = min(len(d_instas), len(allowed_instas))
                        r_instas           = random.sample(allowed_instas, k=n_of_plants)
                        r_instas_weights   = randspread(int(instas_weight), n_of_plants)
                        for i in range(n_of_plants):
                            r_plant_set.add(r_instas[i])
                            r_dict[r_instas[i]] = int(r_instas_weights[i]*wmul[allowed_instas.index(r_instas[i])])
                    
                    if len(d_ginstas) > 0:
                        ginstas_weight  = 0.
                        allowed_ginstas = [2,  17, 20, 15, 31] if at_night else [2,  17, 20]
                        wmul            = [0.7,1.2,1.0,0.4,0.5]
                        for i in d_ginstas:
                            if i in allowed_ginstas:
                                ginstas_weight += d_dict[i]/wmul[allowed_ginstas.index(i)]
                            else:
                                ginstas_weight += d_dict[i]/2.5
                        ginstas_weight     *= random.uniform(0.9,1.3)
                        n_of_plants = min(len(d_ginstas), len(allowed_ginstas))
                        r_ginstas           = random.sample(allowed_ginstas, k=n_of_plants)
                        r_ginstas_weights   = randspread(int(ginstas_weight),n_of_plants)
                        for i in range(n_of_plants):
                            r_plant_set.add(r_ginstas[i])
                            r_dict[r_ginstas[i]] = int(r_ginstas_weights[i]*wmul[allowed_ginstas.index(r_ginstas[i])])
                    random_bs = random.sample([(36,10),(37,3),(25,4),(28,8),(21,8),(38, 8),(22, 8),(33, 8)], int((random.random()**2)*4)) #garlic, umbrella leaf, plantern, split pea, spikeweed, more marigolds, torchwood, pot

                else:
                    random_bs = random.sample([(36,10),(37,3),(25,4),(28,8),(21,8),(38, 8),(22, 8),(33, 8)], int((random.random()**2)*4)) #garlic, umbrella leaf, plantern, split pea, spikeweed, more marigolds, torchwood, pot
                    r_plant_set.add(14)
                    #r_dict[14]    =  8*(len(r_plant_set)-5)
                    r_dict[14]    =  8
                    r_plant_set.add(20)
                    #r_dict[20]    = 10*(len(r_plant_set)-6)
                    r_dict[20]    = 12
                    #r_dict[39]    = 10*(len(r_plant_set)-6)

            else:
                random_bs = [(3,random.randint(60,90))]
            
            for i in random_bs:
                r_plant_set.add(i[0])
                if i[0] in r_dict:
                    r_dict[i[0]] += i[1]
                else:
                    r_dict[i[0]]  = i[1]
            
            if on_roof and 21 in r_plant_set:
                r_plant_set.remove(21)
            if 22 in r_plant_set and len(r_plant_set & {0,5,7,18,28}) == 0:
                r_plant_set.remove(22)
            
        else:
            if level!= "5-10" and level!="wnb1" and level!="wnb2":
                r_plant_set={0,2,3,4,5,6,7,8,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,42,43,44,46,47} #no sunflower, sun shroom, twin sun, or gold magnet
                r_dict={0:5, 2:5, 3:5, 4:5, 5:5, 6:5, 7:5, 8:2, 10:2, 11:2, 12:2, 13:2, 14:2, 15:2, 16:0, 17:5, 18:5, 19:0, 20:6, 21:5, 22:5, 23:5, 24:0, 25:0, 26:5, 27:0, 28:5, 29:5, 30:5, 31:5, 32:5, 33:0, 34:5, 35:80, 36:5, 37:5, 38:5, 39:5, 40:3, 42:3, 43:3, 44:3, 46:3, 47:2}
                if has_water:
                    r_dict[16]=60
                    r_dict[19]=5
                    if at_night:
                        r_dict[24]=5
                        if level != "4-10" and level != "invs": # 4-10 hardcoded to not have fog, but with random worlds other conveyors can have fog
                            r_dict[25]=7 # add plantern
                if at_night:
                    for i in range(8, 16):
                        if i!=9 and not(i==11 and has_water):
                            if i==11:
                                r_dict[11]=20
                            else:
                                r_dict[i]=5
                    r_dict[31]=5
                if on_roof:
                    r_dict[33]=200
                    r_dict[32]=20
                    r_dict[34]=20
                    r_dict[39]=20
                    r_dict[21]=0
                if level=="4-10":
                    r_dict[26]=30
                    r_dict[27]=20
            elif level == "5-10":
                r_plant_set={0,2,3,5,6,7,8,10,12,13,14,15,17,18,20,23,26,28,29,30,31,32,33,34,36,37,38,39,40,44,47}
                r_dict={0:1, 2:5, 3:1, 5:4, 6:1, 7:8, 8:1, 10:10, 12:1, 13:4, 14:50, 15:10, 17:1, 18:3, 20:70, 23:1, 26:1, 28:1, 29:1, 30:3, 31:1, 32:21, 33:400, 34:37, 36:1, 37:2, 38:2, 39:40, 40:80, 44:15, 47:160} #garbage:22, semi-garbage:26, ice:80, other instas:120, pot:255, cabbage:42, kernel:75, melon:80, total:700

        if (level=="wnb1" or level=="wnb2") and randomConveyors.get()=="It's Raining Seeds":            
            randomised=CONVEYOR_DEFAULTS[level][1]
        else:           
            randomised   = [(i, r_dict[i]) for i in sorted(list(r_plant_set))]                  
            
        writeConveyor(CONVEYOR_DEFAULTS[level][0], randomised)
        
##        print()
##        print(level+":")
##        for i in randomised:
##            print(SEED_STRINGS[i[0]]+": "+str(i[1]))
    random.setstate(rng_state)

#showAverage()
#nightAverage()

reset_zombie_spawn() # resets from random zombies mode
reset_from_random_worlds() # writes default code for selecting world/graves/etc
if randomWorld.get() and gamemode.get() != "minigames":
    (level_worlds, level_with_5_pots) = randomiseLevelWorlds()
    (snorkel_levels, dolphin_levels) = redistribute_aquatic_zombies()
    randomiseGraves()
    randomiseFog()
    randomisePoolAmbush()
    randomiseRoofAmbush()
    randomisePots()
else:
    (level_worlds, snorkel_levels, dolphin_levels, level_with_5_pots) = (default_worlds, [23, 24, 25, 27, 30], [28, 29, 30, 34], 41)
if randomWaveCount.get() != "False" and gamemode.get() == "adventure":
    (flags_per_level, wavecount_per_level, waves_per_flag) = randomiseWaveCount()
else:
    (flags_per_level, wavecount_per_level, waves_per_flag) = (default_flags, default_wavecount, default_waves_per_flag)
if gamemode.get() != 'adventure':
    levels = randomiseLevels(seed, gamemode.get() == "ng+")
    level_plants = LEVEL_PLANTS
else:
    if randomisePlants.get():
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
if randomZombies:
    zombiesToRandomise=generateZombies(levels, level_plants)

if randomConveyors.get()!="False":
    randomiseConveyors(seed)
    WriteMemory("unsigned char", [2], 0x42335E) # changes pot weight curve from linear to quad, so it doesn't decrease so quickly
else:
    for i in CONVEYOR_DEFAULTS:
        writeConveyor(CONVEYOR_DEFAULTS[i][0], CONVEYOR_DEFAULTS[i][1])
    WriteMemory("unsigned char", [1], 0x42335E) # reset pot weight curve to linear

#for i in levels:
    #print(LEVEL_STRINGS[i], SEED_STRINGS[level_plants[i]])

for i in range(0, 48):
    WriteMemory("int", plants[i][0], 0x69F2C0 + 0x24*i)
    WriteMemory("int", plants[i][1], 0x69F2C4 + 0x24*i)
for i in range(0, 33):
    WriteMemory("int", zombies[i][3], 0x69DA88 + 0x1C*i)
    WriteMemory("int", zombies[i][2], 0x69DA94 + 0x1C*i)
    WriteMemory("int", zombies[i][4], 0x69DA90 + 0x1C*i)
    WriteMemory("int", zombies[i][1], 0x69DA8C + 0x1C*i)

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

if imitater.get():
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

WriteMemory("unsigned char", 0, 0x530028)
WriteMemory("unsigned char", 1, 0x43c1d1)

# scaling starting cooldowns when random cooldowns are on (starting cd is 0.9*(cd - 10sec)):
if randomCooldowns.get():
    WriteMemory("unsigned char", [0x66, 0x90], 0x489C00) # 2 byte nop - to make upgrade plants follow common path for cooldown
    WriteMemory("unsigned char", [
        0x3D, 0xE8,0x03,0x00,0x00,  #cmp eax,#1000 // 10 sec  for no cooldown     
        0x7E,0x33,                  #jle 489C43
        0x89,0x46,0x28,             # mov[esi+28],eax // store total cooldown as starting cooldown
        0x2D,0xE8,0x03,0x00,0x00,   # sub eax, #1000
        0x31,0xD2,                  # xor edx,edx
        0xB9,0x0A,0x00,0x00,0x00,   # mov ecx,#10
        0xF7,0xF1,                  # div ecx
        0x05,0xE8,0x03,0x00,0x00,   # add eax,000003E8
        0x89,0x46,0x24,             # mov [esi+24],eax // set recharge progress
        0x5D,                       # pop ebp
        0xC6,0x46,0x49,0x01,        # mov byte[esi+49],1
        0xC6,0x46,0x48,0x00,        # mov byte[esi+48],0
        0x5B,                       #pop ebx
        0xC3                        #ret
    ],                      
        0x489C09)
    
    
# Plant::GetTooltip # show cooldown instead of tooltip when random cooldowns are on
if randomCooldowns.get() and not randomVarsSystemEnabled:
    WriteMemory("unsigned char", [ 
        0x8B,0x44,0x24,0x04,                # mov eax,[esp+04] // plant index
        0x56,                               # push esi // preserve
        0x8B,0xF1,                          # mov esi,ecx // string obj
        0x8D,0x04,0xC0,                     # lea eax,[eax+eax*8]
        0xDB,0x04,0x85,0xC4,0xF2,0x69,0x00, # fild dword ptr [eax*4+popcapgame1.exe+29F2C4] // load cooldown
        0xDA,0x35,0xD0,0x54,0x65,0x00,      # fidiv dword ptr [popcapgame1.exe+2554D0] // div by 100
        0x51,                               # push ecx // temp storage for double
        0x51,                               # push ecx // temp storage for double
        0xDD,0x1C,0x24,                     # fstp qword ptr [esp] // store cooldown in seconds
        0x68,0xDC,0x7D,0x46,0x00,           # push popcapgame1.exe+67DDC // format string
        0xE8,0xCA,0x8E,0x14,0x00,           # call popcapgame1.exe+1B0CA0 // StrFormat
        0x83,0xC4,0x0C,                     # add esp,0C // flush params
        0x5E,                               # pop esi // restore
        0xC3,                               # ret 
        0xCC,                               # int 3 
        0x63,0x64,0x3A,0x20,0x25,0x2E,0x31,0x66,0x20,0x73,0x65,0x63,0x00   # "cd: %.1f sec" // format string
        ],
        0x467DB0)

# code for changing plant name to plant tooltip in seed bank
WriteMemory("unsigned char", [ 
    0x80,0xFA,0xFF,             # cmp dl,-01
    0x0F,0x45,0xC2,             # cmovne eax,edx // eax = plant index
    0x8D,0x4C,0x24,0x30,        # lea ecx,[esp+30] // string object
    0x50,                       # push eax
    0xE8,0xB8,0x60,0xE1,0xFF,   # call popcapgame1.exe+67DB0 // GetTooltip
    0x83,0xC4,0x04,             # add esp,04 // flush param
    0xE9,0x1E,0xDA,0xDB,0xFF,   # jmp popcapgame1.exe+F71E // continue normal code
    ],
    0x651ce8)

# activate code for changing plant name to plant tooltip in seed bank
if randomCooldowns.get() or randomVarsSystemEnabled:
    WriteMemory("unsigned char", [ 
    0xE9,0xD4,0x25,0x24,0x00,   # jmp 651ce8
    0x90,                       # nop
    ],
    0x40F70F)

# code for coloring seeds based on cooldown
WriteMemory("unsigned char", [ 
    0x8B,0x84,0x24,0xF4,0x00,0x00,0x00, # mov eax,[esp+000000F4] // return address
    0x3C,0x77,                          # cmp al,-77
    0x74,0x0E,                          # je popcapgame1.exe+251C8D
    0x3C,0xC0,                          # cmp al,-40
    0x74,0x0A,                          # je popcapgame1.exe+251C8D
    0x3C,0xD1,                          # cmp al,-2F
    0x74,0x06,                          # je popcapgame1.exe+251C8D
    0x3C,0xFF,                          # cmp al,-01
    0x74,0x02,                          # je popcapgame1.exe+251C8D
    0xEB,0x4C,                          # jmp popcapgame1.exe+251CD9
    0x8B,0x84,0x24,0xF4,0x00,0x00,0x00, # mov eax,[esp+000000F4] // either always draw mode is on, or we are in plant selection screen
    0x3C,0x9F,                          # cmp al,-61 // check if it's level end screen
    0x74,0x41,                          # je popcapgame1.exe+251CD9
    0x83,0xFD,0x30,                     # cmp ebp,30
    0x7D,0x3C,                          # jnl popcapgame1.exe+251CD9 // don't do anything for plants > imitater
    0xC7,0x46,0x3C,0xFF,0x00,0x00,0x00, # mov [esi+3C],000000FF // 255 alpha
    0x8A,0x46,0x48,                     # mov al,[esi+48] // check if ColorizeImage is on
    0x84,0xC0,                          # test al,al
    0x0F,0xB6,0x85,0xC2,0x12,0x65,0x00, # movzx eax,byte ptr [ebp+popcapgame1.exe+2512C2] // load preferred green/blue value
    0x74,0x16,                          # je popcapgame1.exe+251CC6
    0x50,                               # push eax // load green/blue into fpu
    0xDB,0x04,0x24,                     # fild dword ptr [esp]
    0xDA,0x35,0xB0,0xEC,0x75,0x00,      # fidiv dword ptr [popcapgame1.exe+35ECB0]
    0xDA,0x4E,0x34,                     # fimul [esi+34] // adjust already set green\blue values, so greyed out plants are still dark, but reddish. Red stays the same
    0xDB,0x56,0x34,                     # fist dword ptr [esi+34] // green
    0xDB,0x5E,0x38,                     # fistp dword ptr [esi+38] // blue
    0x58,                               # pop eax // restore stack
    0xEB,0x11,                          # jmp popcapgame1.exe+251CD9 // continue normal code
    0xC6,0x46,0x48,0x01,                # mov byte ptr [esi+48],01 // set ColorizeImage
    0xC7,0x46,0x30,0xFF,0x00,0x00,0x00, # mov [esi+30],000000FF // 255 red
    0x89,0x46,0x34,                     # mov [esi+34],eax // preferred green
    0x89,0x46,0x38,                     # mov [esi+38],eax // preferred blue
    0x83,0xFB,0x30,                     # cmp ebx,30 // default code
    0x0F,0x85,0xA9,0x5A,0xE3,0xFF,      # jne popcapgame1.exe+8778B // default code
    0xE9,0xA0,0x5A,0xE3,0xFF,           # jmp popcapgame1.exe+87787 // default code
    ],
    0x651c74)

# activate code for coloring seeds on selection screen based on their cooldown
if randomCooldowns.get() and cooldownColoring.get() != 'False':
    if cooldownColoring.get() == 'Selection only':
        WriteMemory("unsigned char", [
            0xE9,0xED,0xA4,0x1C,0x00,    # jmp popcapgame1.exe+251C74
            ], 
            0x487782)
    elif cooldownColoring.get() == 'Always on':
        WriteMemory("unsigned char", [
            0xE9,0x06,0xA5,0x1C,0x00,    # jmp popcapgame1.exe+251C8D
            ], 
            0x487782)


WriteMemory("unsigned char", [
0xe8, 0x1a, 0x9a, 0x1c, 0x00, #call  0x651be0
0x8d, 0x54, 0x24, 0x3c,       #leal  0x3c(%esp), %edx
0x52,                         #pushl %edx
0x50,                         #pushl %eax
0x8d, 0x54, 0x24, 0x7c,       #leal  0x7c(%esp), %edx
0x56,                         #pushl %esi
], 0x4881c1)
WriteMemory("unsigned char", 0x20, 0x4881d8)
WriteMemory("unsigned char", [
0xdd, 0xd8,                         #fstp  %st(0)
0x31, 0xc0,                         #xorl  %eax,              %eax
0x8d, 0x7c, 0x24, 0x4c,             #leal  0x4c(%esp),        %edi
0xab,                               #stosd
0xab,                               #stosd
0xab,                               #stosd
0xb0, 0xff,                         #movb  $0xff,              %al
0xab,                               #stosd
0x8a, 0x85, 0x90, 0x12, 0x65, 0x00, #movb  0x651290(%ebp),    %edx
0xd0, 0xe0,                         #shlb  $0x1,               %al
0x19, 0xc9,                         #sbbl  %ecx,              %ecx
0x89, 0x44, 0x8c, 0x54,             #movl  %eax, 0x54(%esp,%ecx,4)
0x8b, 0xfe,                         #movl  %esi,              %edi
0x66, 0x0f, 0x1f, 0x44, 0x00, 0x00, #nop   (6 bytes)
0x8b, 0x35, 0x98, 0x74, 0x6a, 0x00, #movl  0x6a7498,          %esi
0x0f, 0x1f, 0x44, 0x00, 0x00,       #nop   (5 bytes)
0x8d, 0x54, 0x24, 0x60,             #leal  0x60(%esp),        %edx
0x8d, 0x7c, 0x24, 0x28,             #leal  0x28(%esp),        %edi
], 0x4880ba)
WriteMemory("unsigned char", [
0x0f, 0xb6, 0x95, 0x90, 0x12, 0x65, 0x00, #movzbl 0x651290(%ebp),   %edx
0x6a, 0x00,                               #pushl  $0x0
0x6a, 0x00,                               #pushl  $0x0
0x6a, 0x00,                               #pushl  $0x0
0xd0, 0xe2,                               #shlb   $0x1,              %dl
0x19, 0xc9,                               #sbbl   %ecx,             %ecx
0x89, 0x54, 0x8c, 0x08,                   #movl   %edx, 0x8(%esp,%ecx,4)
0xb2, 0xff,                               #movb   $0xff,             %dl
0x87, 0x54, 0x24, 0x0c,                   #xchgl  %edx,        0xc(%esp)
0x89, 0xe1,                               #movl   %esp,             %ecx
0x51,                                     #pushl  %ecx
0xff, 0xe2                                #jmp    *%edx
], 0x651be0)



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
if seeded.get():
    if LINUX:
        rng_addr = 0x200000
    else:
        rng_addr = VirtualAllocEx(pvz_handle, None, 0x30000, 0x1000, 0x40)
        atexit.register(dealloc_rngmem)
    WriteMemory("int", rng_addr+0x10, 0x651e26+0x58)
    WriteMemory("int", rng_addr,      0x651e26+0x8c)
    WriteMemory("int", rng_addr,      0x651e26+0x94)
    WriteMemory("int", rng_addr+0x10, 0x651e26+0x9b)
    WriteMemory("int", rng_addr+0x10, 0x651e26+0xa2)
    WriteMemory("int", 0x651e26-0x5a993a, 0x5a9936) #raw rng
    WriteMemory("int", 0x651e2a-0x5a9a45, 0x5a9a41) #int rng
    WriteMemory("int", 0x651e2e-0x5a9a6b, 0x5a9a67) #flt rng



#Level transition

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

WriteMemory("unsigned int", 0x679890, 0x430f79)
WriteMemory("unsigned int", 0x679890, 0x431007)
WriteMemory("unsigned int", 0x651268, 0x430fd9)
WriteMemory("unsigned int", 0x651264, 0x430fad)
WriteMemory("unsigned int", 280, 0x430f4c)
WriteMemory("unsigned char", [
0xd9, 0x5e, 0x28,            #fstps 0x28(%esi)
0x0f, 0x1f, 0x00,            #nop
0xe8, 0x13, 0x0d, 0x22, 0x00 #call 0x651dc0
], 0x4310a2)
WriteMemory("unsigned char", [
0xd9, 0x5e, 0x28,            #fstps 0x28(%esi)
0x0f, 0x1f, 0x00,            #nop
0xe8, 0xe3, 0x0c, 0x22, 0x00 #call 0x651dc0
], 0x4310d2)
WriteMemory("unsigned char", [
0xd9, 0x5e, 0x28,            #fstps 0x28(%esi)
0x0f, 0x1f, 0x00,            #nop
0xe8, 0xa2, 0x0c, 0x22, 0x00 #call 0x651dc0
], 0x431113)
WriteMemory("float",  [0.01, 150.0, 4.0], 0x65125c)
WriteMemory("double", [2.99], 0x651268)
WriteMemory("unsigned char", [
0x8b, 0x46, 0x54,                   #movl   0x54(%esi), %eax
0x05, 0x51, 0xff, 0xff, 0xff,       #addl   $-175,      %eax
0x19, 0xc9,                         #sbbl   %ecx,       %ecx
0x21, 0xc8,                         #andl   %ecx,       %eax
0xb9, 0x32, 0x00, 0x00, 0x00,       #movl   $100,       %ecx #used to be 300, but that was dumb
0x39, 0xc1,                         #cmpl   %eax,       %ecx
0x0f, 0x42, 0xc1,                   #cmovcl %ecx,       %eax
0x50,                               #pushl  %eax
0xdb, 0x04, 0x24,                   #fildl  (%esp)
0xd8, 0x0d, 0x5c, 0x12, 0x65, 0x00, #fmuls  0x65125c
0xd9, 0x1c, 0x24,                   #fstps  (%esp)
0xe8, 0xd8, 0xfa, 0xeb, 0xff,       #call   0x5118c0 #offset 0x28
0xd9, 0x1c, 0x24,                   #fstps  (%esp)
0xe8, 0xd0, 0xfa, 0xeb, 0xff,       #call   0x5118c0 #offset 0x30
0xd8, 0x0d, 0x60, 0x12, 0x65, 0x00, #fmuls  0x651260
0xd8, 0x6e, 0x24,                   #fsubrs 0x24(%esi)
0xd9, 0x5e, 0x24,                   #fstps  0x24(%esi)
0x58,                               #popl   %eax
0xc3,                               #retl
], 0x651dc0)

WriteMemory("unsigned char", [
0x8b, 0xc8,                  #movl  %eax, %ecx
0x8b, 0xc6,                  #movl  %esi, %eax
0x50,                        #pushl %eax
0xd9, 0x14, 0x24,            #fsts  (%esp)
0x50,                        #pushl %eax
0xd9, 0x1c, 0x24,            #fstps (%esp)
0x50,                        #pushl %eax
0xd9, 0x45, 0x34,            #flds  0x34(%ebp)
0xd9, 0x14, 0x24,            #fsts  (%esp)
0x50,                        #pushl %eax
0xd9, 0x1c, 0x24,            #fstps (%esp)
0xe8, 0xcd, 0x01, 0x22, 0x00 #call  0x651d00 #431b33
], 0x431b17)
WriteMemory("unsigned char", [
0x81, 0x7d, 0x54, 0xaf, 0x00, 0x00, 0x00, #cmpl   $175, 0x54(%ebp)
0x73, 0x01,                               #jnc    +0x1
0xc3,                                     #retl
0x50,                                     #pushl  %eax
0x51,                                     #pushl  %ecx
0x52,                                     #pushl  %edx

0x8b, 0xc6,                               #movl   %esi,      %eax
0xb1, 0x01,                               #movl   $0x1,       %cl
0xe8, 0xfa, 0x4f, 0xf3, 0xff,             #call   0x586d10        #SetColorizeImages #586d10-651d16

0x31, 0xc0,                               #xorl   %eax,      %eax
0xb0, 0xff,                               #movl   $255,       %al
0x50,                                     #pushl  %eax
0xb0, 0xff,                               #movl   $0xff,      %al #blue
0x50,                                     #pushl  %eax
0xb0, 0xbb,                               #movl   $0xbb,      %al #green
0x50,                                     #pushl  %eax
0xb0, 0xdd,                               #movl   $0xdd,      %al #red
0x50,                                     #pushl  %eax
0x8b, 0xc4,                               #movl   %esp,      %eax
0x8b, 0xce,                               #movl   %esi,      %ecx
0xe8, 0x93, 0x4f, 0xf3, 0xff,             #call   0x586cc0        #SetColor #0x586cc0-651d2d
0x83, 0xc4, 0x10,                         #addl   $0x10,     %esp

0x8b, 0x0d, 0x14, 0x77, 0x6a, 0x00,       #movl   0x6a7714,  %ecx #FONT_HOUSEOFTERROR28
0x8b, 0xc6,                               #movl   %esi,      %eax
0xe8, 0x73, 0x4f, 0xf3, 0xff,             #call   0x586cb0        #SetFont #586cb0-651d3d

0x68, 0xfa, 0x00, 0x00, 0x00,             #pushl  $250
0x68, 0xee, 0x02, 0x00, 0x00,             #pushl  $750
0xdb, 0x04, 0x24,                         #fildl  (%esp)
0xd9, 0x45, 0x24,                         #flds   0x24(%ebp)
0xde, 0xe9,                               #fsubp  %st(1)
0xdb, 0x1c, 0x24,                         #fistpl (%esp)
0x68, 0x70, 0x12, 0x65, 0x00,             #pushl  $0x651270
0x8b, 0xc6,                               #movl   %esi,      %eax
0xe8, 0xc2, 0x53, 0xf3, 0xff,             #call   0x587120        #DrawString #587120-651d5e

0x83, 0xc4, 0xc0,                         #addl   $-0x40,    %esp #I was too lazy to do a real subtraction
0x8b, 0xc4,                               #movl   %esp,      %eax
0x8b, 0x0d, 0x90, 0x11, 0x65, 0x00,       #movl   0x651190,  %ecx
0xe8, 0x02, 0x19, 0xe0, 0xff,             #call   0x453670       #GetStageString #453670-651d6e
0x68, 0x1d, 0x01, 0x00, 0x00,             #pushl  $285
0x68, 0xee, 0x02, 0x00, 0x00,             #pushl  $750
0xdb, 0x04, 0x24,                         #fildl  (%esp)
0xd9, 0x45, 0x24,                         #flds   0x24(%ebp)
0xde, 0xe9,                               #fsubp  %st(1)
0xdb, 0x1c, 0x24,                         #fistpl (%esp)
0x50,                                     #pushl  %eax
0x8b, 0xc6,                               #movl   %esi,      %eax
0xe8, 0x95, 0x53, 0xf3, 0xff,             #call   0x587120        #DrawString #587120-651d8b
0x83, 0xc4, 0x40,                         #addl   $0x40,     %esp

0x8b, 0xc6,                               #movl   %esi,      %eax
0xb1, 0x00,                               #movl   $0x0,      %cl
0xe8, 0x79, 0x4f, 0xf3, 0xff,             #call   0x586d10       #SetColorizeImages #586d10-651d97
0x5a,                                     #popl   %edx
0x59,                                     #popl   %ecx
0x58,                                     #popl   %eax
0xc3                                      #retl
], 0x651d00)
WriteMemory("unsigned int", [0, 0x4e207055, 0x3a747865, 0, 0, 8], 0x651270)

WriteMemory("unsigned char", [
0x8b, 0x0d, 0x90, 0x11, 0x65, 0x00 #movl 0x651190, %ecx
], 0x452331)
WriteMemory("unsigned char", 0, 0x452339)
WriteMemory("unsigned char", 0, 0x452365)



#Random conveyors

WriteMemory("unsigned char", [
0x75, 0x0a,                         #jne   conveyor.locB
0xbf, 0x60, 0x2f, 0x42, 0x00,       #        movl $0x422f60, %edi #1-10
0xe9, 0xef, 0x00, 0x00, 0x00,       #jmp  conveyor.locA #422e3b
                                    #conveyor.locB:

0x3b, 0xc6,                         #cmpl %esi, %eax
0x75, 0x0a,                         #jne  conveyor.locC
0xbf, 0x98, 0x2f, 0x42, 0x00,       #        movl $0x422f98, %edi #2-10
0xe9, 0xe1, 0x00, 0x00, 0x00,       #jmp  conveyor.locA #422e49
                                    #conveyor.locC:

0x83, 0xf8, 0x1e,                   #cmpl $0x1e, %eax
0x75, 0x0a,                         #jne  conveyor.locD
0xbf, 0xd0, 0x2f, 0x42, 0x00,       #        movl $0x422fd0, %edi #3-10
0xe9, 0xd2, 0x00, 0x00, 0x00,       #jmp  conveyor.locA #422e58
                                    #conveyor.locD:

0x83, 0xf8, 0x28,                   #cmpl $0x28, %eax
0x75, 0x0a,                         #jne  conveyor.locE
0xbf, 0x08, 0x30, 0x42, 0x00,       #        movl $0x423008, %edi #4-10
0xe9, 0xc3, 0x00, 0x00, 0x00,       #jmp  conveyor.locA #422e67
                                    #conveyor.locE:

0x8b, 0x4c, 0x24, 0x10,             #movl  0x10(%esp), %ecx
0xe8, 0x60, 0x0b, 0x03, 0x00,       #call  0x4539d0 #422e70
0x84, 0xc0,                         #testb %al,         %al
0x74, 0x0a,                         #je    conveyor.locF
0xbf, 0x40, 0x30, 0x42, 0x00,       #        movl $0x423040, %edi #5-10
0xe9, 0xac, 0x00, 0x00, 0x00,       #jmp   conveyor.locA #422e7e
                                    #conveyor.locF:

0x8b, 0xc1,                         #movl  %ecx, %eax
0xe8, 0x9b, 0x09, 0x03, 0x00,       #call  0x453820 #422e85
0x84, 0xc0,                         #testb %al,   %al
0x74, 0x0a,                         #je    conveyor.locG
0xbf, 0x78, 0x30, 0x42, 0x00,       #        movl $0x423078, %edi #shovel level????? wtf is that
0xe9, 0x97, 0x00, 0x00, 0x00,       #jmp   conveyor.locA #422e93
                                    #conveyor.locG:

0x8b, 0x81, 0xf8, 0x07, 0x00, 0x00, #movl 0x7f8(%ecx), %eax
0x83, 0xf8, 0x21,                   #cmpl $0x21,       %eax
0x89, 0x44, 0x24, 0x14,             #movl %eax,  0x14(%esp)
0x75, 0x0a,                         #jne  conveyor.locH
0xbf, 0xb0, 0x30, 0x42, 0x00,       #        movl $0x4230b0, %edi #wnb2
0xe9, 0x7e, 0x00, 0x00, 0x00,       #jmp  conveyor.locA #422eac
                                    #conveyor.locH:

0xe8, 0x8f, 0x09, 0x03, 0x00,       #call  0x453840 #422eb1
0x84, 0xc0,                         #testb %al, %al
0x74, 0x0a,                         #je    conveyor.locI
0xbf, 0xe8, 0x30, 0x42, 0x00,       #        movl $0x4230e8, %edi #wnb1 and 1-5
0xe9, 0x6b, 0x00, 0x00, 0x00,       #jmp   conveyor.locA #422ebf
                                    #conveyor.locI:

0xe8, 0xfc, 0x09, 0x03, 0x00,       #call  0x4538c0 #422ec4
0x84, 0xc0,                         #testb %al, %al
0x74, 0x0a,                         #je    conveyor.locJ
0xbf, 0x20, 0x31, 0x42, 0x00,       #        movl $0x423120, %edi #btlz
0xe9, 0x58, 0x00, 0x00, 0x00,       #jmp   conveyor.locA #422ed2
                                    #conveyor.locJ:

0xe8, 0x49, 0x0a, 0x03, 0x00,       #call  0x453920 #422ed7
0x84, 0xc0,                         #testb %al, %al
0x74, 0x0a,                         #je    conveyor.locK
0xbf, 0x58, 0x31, 0x42, 0x00,       #        movl $0x423158, %edi #stormy night
0xe9, 0x45, 0x00, 0x00, 0x00,       #jmp   conveyor.locA #422ee5
                                    #conveyor.locK:

0xe8, 0x66, 0x0a, 0x03, 0x00,       #call  0x453950 #422eea
0x84, 0xc0,                         #testb %al, %al
0x74, 0x0a,                         #je    conveyor.locL
0xbf, 0x90, 0x31, 0x42, 0x00,       #        movl $0x423190, %edi #bungee blitz
0xe9, 0x32, 0x00, 0x00, 0x00,       #jmp   conveyor.locA #422ef8
                                    #conveyor.locL:

0x8b, 0x44, 0x24, 0x14,             #movl 0x14(%esp), %eax
0x83, 0xf8, 0x1a,                   #cmpl $0x1a,      %eax
0x75, 0x0a,                         #jne  conveyor.locM
0xbf, 0xc8, 0x31, 0x42, 0x00,       #        movl $0x4231c8, %edi #portal
0xe9, 0x1f, 0x00, 0x00, 0x00,       #jmp  conveyor.locA #422f0b
                                    #conveyor.locM:

0x83, 0xf8, 0x1b,                   #cmpl $0x1b, %eax
0x75, 0x0a,                         #jne  conveyor.locN
0xbf, 0x00, 0x32, 0x42, 0x00,       #        movl $0x423200, %edi #column
0xe9, 0x10, 0x00, 0x00, 0x00,       #jmp  conveyor.locA #422f1a
                                    #conveyor.locN:

0x83, 0xf8, 0x15,                   #cmpl $0x15, %eax
0x75, 0x0a,                         #jne  conveyor.locO
0xbf, 0x38, 0x32, 0x42, 0x00,       #        movl $0x423238, %edi #invisighoul
0xe9, 0x01, 0x00, 0x00, 0x00,       #jmp  conveyor.locA #422f29
                                    #conveyor.locO:

0xcc,                               #int3 #code execution should never reach here

                                    #conveyor.locA: #422f2a
0xb9, 0x38, 0x00, 0x00, 0x00,       #movl $56, %ecx
                                    #conveyor.loopA:
0x0f, 0xb6, 0x44, 0x0f, 0xff,       #        movzbl -1(%edi,%ecx),     %eax
0x51,                               #        pushl  %ecx
0x88, 0xc1,                         #        movb   %al,                %cl
0xc0, 0xe9, 0x06,                   #        shrb   $6,                 %cl
0x24, 0x3f,                         #        andb   $0x3f,              %al
0xd3, 0xe0,                         #        shll   %cl,               %eax
0x59,                               #        popl   %ecx
0x8d, 0x51, 0xff,                   #        leal   -1(%ecx),          %edx
0x89, 0x54, 0xcc, 0x10,             #        movl   %edx, 0x10(%esp,%ecx,8)
0x89, 0x44, 0xcc, 0x14,             #        movl   %eax, 0x14(%esp,%ecx,8)
0xe2, 0xe3,                         #loop conveyor.loopA
                                    #conveyor.exloopA:
0x8d, 0x79, 0x38,                   #leal 56(%ecx), %edi
0xe9, 0x57, 0x03, 0x00, 0x00        #jmp  0x4232ab #422f54
], 0x422e2f)
for i in [0x422cd8, 0x4232d8, 0x4233a9, 0x423440]:
    tmp = ReadMemory("unsigned int", i) + 0x120
    WriteMemory("unsigned int", tmp, i)

WriteMemory("unsigned char", [
0x74, 0x11,                                     #je     0x4233a3
0x85, 0xc9,                                     #testl  %ecx, %ecx
0x90,                                           #nop    (1 byte)
0x75, 0x7f,                                     #jne    0x423416
0x8b, 0x80, 0x2c, 0x08, 0x00, 0x00,             #movl   0x82c(%eax),    %eax
0x83, 0x78, 0x24, 0x32,                         #cmpl   $0x32,    0x24(%eax)
0x75, 0x73,                                     #jne    0x423416
0x0f, 0xb6, 0x9c, 0x24, 0xdc, 0x01, 0x00, 0x00, #movzbl 0x1dc(%esp),    %ebx
0x8b, 0xc3,                                     #movl   %ebx,           %eax
0x83, 0xe3, 0x07,                               #andl   $0x7,           %ebx
0xc1, 0xe8, 0x03,                               #shrl   $0x3,           %eax
0x0f, 0xa3, 0x98, 0x91, 0x34, 0x42, 0x00,       #btl    %ebx, 0x423491(%eax)
0x73, 0x40                                      #jnc    0x4233fc
], 0x423390)
WriteMemory("unsigned char", [
0xab, 0x2f, 0xc4, 0x7f, 0xfd, 0x00
], 0x423491)

WriteMemory("unsigned char", [
0x7e, 0x32,                               #jle  0x42344f <.text+0x2244f>
0x8b, 0x44, 0x24, 0x10,                   #movl 0x10(%esp),  %eax
0x83, 0xf8, 0x04,                         #cmpl $0x4,        %eax
0x7c, 0x09,                               #jl   0x42342f <.text+0x2242f>
0xc7, 0x46, 0x04, 0x01, 0x00, 0x00, 0x00, #movl $0x1,   0x4(%esi)
0xeb, 0x20,                               #jmp  0x42344f <.text+0x2244f>
0x83, 0xf8, 0x03,                         #cmpl $0x3,        %eax
0x7c, 0x09,                               #jl   0x42343d <.text+0x2243d>
0xc7, 0x46, 0x04, 0x05, 0x00, 0x00, 0x00, #movl $0x5,   0x4(%esi)
0xeb, 0x12,                               #jmp  0x42344f <.text+0x2244f>
0x8b, 0x8c, 0x24, 0xdc, 0x01, 0x00, 0x00, #movl 0x1dc(%esp), %ecx
0x8b, 0xd7,                               #movl %edi,        %edx
0x3b, 0x4a, 0x68,                         #cmpl 0x68(%edx),  %ecx
0x75, 0x04,                               #jne  0x42344f <.text+0x2244f>
0xd1, 0x6e, 0x04,                         #shrl $1,     0x4(%esi)
0x90,                                     #nop  (1 byte)
0x8b, 0x06,                               #movl (%esi),      %eax
0xe8, 0xaa, 0xe7, 0x22, 0x00              #call 0x651c00 #-0x423456
], 0x42341b)
WriteMemory("unsigned char", [ #upgrade plant + bean weight logic
0x53,                                     #pushl %ebx
0x2c, 0x28,                               #subb  $40,  %al
0x72, 0x28,                               #jc    weightLogic.locA
0x3c, 0x07,                               #cmpb  $7,   %al
0x77, 0x24,                               #ja    weightLogic.locA
0x9c,                                     #        pushfd
0x0f, 0xb6, 0x98, 0x00, 0x13, 0x65, 0x00, #        movzbl 0x651300(%eax), %ebx
0x8b, 0x45, 0x08,                         #        movl   0x8(%ebp), %eax
0x8b, 0x50, 0x04,                         #        movl   0x4(%eax), %edx
0xe8, 0xd4, 0xb7, 0xdb, 0xff,             #        call   0x40d3f0 #-0x651c1c
0x9d,                                     #        popfd
0x75, 0x02,                               #        jne    weightLogic.locB
0xd1, 0xe8,                               #                shrl $0x1, %eax
                                          #        weightLogic.locB:
0x3b, 0x44, 0x24, 0x18,                   #        cmpl   0x18(%esp), %eax
0x77, 0x04,                               #        ja     weightLogic.locC
0xc6, 0x46, 0x04, 0x00,                   #                movb $0, 0x4(%esi)
                                          #        weightLogic.locC:
0x5b,                                     #popl  %ebx
0xc3,                                     #retl

                                          #weightLogic.locA:
0x04, 0x05,                               #addb $5, %al
0x75, 0xfa,                               #jne  weightLogic.locC
0x8b, 0x45, 0x08,                         #        movl  0x8(%ebp), %eax
0x8b, 0x50, 0x04,                         #        movl  0x4(%eax), %edx
0x33, 0xdb,                               #        xorl  %ebx,      %ebx
0x56,                                     #        pushl %esi
0x53,                                     #        pushl %ebx
0x89, 0xe6,                               #        movl  %esp,      %esi
0x89, 0x1c, 0x24,                         #        movl  %ebx,    (%esp)
0xe8, 0x0b, 0xad, 0xdc, 0xff,             #        call  0x41c950 #-0x651c45
0x84, 0xc0,                               #        testb %al,        %al
0x74, 0x19,                               #        je    weightLogic.exloopA:
                                          #        weightLogic.loopA:
0x8b, 0x04, 0x24,                         #                movl  (%esp),      %eax
0x80, 0xb8, 0x43, 0x01, 0x00, 0x00, 0x01, #                cmpl  $0x1, 0x143(%eax)
0xf5,                                     #                cmc
0x83, 0xd3, 0x00,                         #                adcl  $0x0,        %ebx
0x89, 0xe6,                               #                movl  %esp,        %esi
0xe8, 0xf2, 0xac, 0xdc, 0xff,             #                call  0x41c950 #-0x651c5e
0x84, 0xc0,                               #                testb %al, %al
0x75, 0xe7,                               #        jne   weightLogic.loopA
                                          #        weightLogic.exloopA:
0x58,                                     #        popl %eax
0x5e,                                     #        popl %esi
0x3b, 0x5c, 0x24, 0x18,                   #        cmpl 0x18(%esp), %ebx
0x77, 0x04,                               #        ja   weightLogic.locD
0xc6, 0x46, 0x04, 0x00,                   #                movb $0, 0x4(%esi)
                                          #        weightLogic.locD:
0x5b,                                     #popl  %ebx
0xc3                                      #retl

], 0x651c00)
WriteMemory("unsigned char", [ #upgrade plant table
 7,  1, 10, 16, 39, 31, 21, 34 #repeater, sunflower, fume, lily, melon, magnet, spikeweed, kernel
], 0x651300)



#Random firerates indicator

WriteMemory("unsigned char", [12 for i in range(56)], 0x651308)
WriteMemory("unsigned char",[ #color lookup table
0x44,0x00,0x00,
0x88,0x11,0x22,
0xcc,0x22,0x44,
0xff,0x66,0x66,
0x88,0x88,0x88,
0x88,0xbb,0x88,
0x99,0xff,0x99,
0xcc,0xff,0xaa,
0xee,0xaa,0x22
], 0x651340)
WriteMemory("unsigned int", [0,0x2b,0,0,0,1,0,0, 0,0x20,0,0,0,1,0,0, 0,0x2d,0,0,0,1,0,0,], 0x651360) #ends at 0x6513c0
WriteMemory("unsigned char", [
0x8b, 0xc7,                                     #movl   %edi,           %eax
0xb1, 0x01,                                     #movb   $0x1,            %cl
0xe8, 0x37, 0x52, 0xf3, 0xff,                   #call   0x586d10             #SetColorizeImages #586d10-651ad9

0x31, 0xc0,                                     #xorl   %eax,           %eax
0x6a, 0x03,                                     #pushl  $3
0xb0, 0xff,                                     #movb   $0xff,           %al
0x59,                                           #popl   %ecx
0x50,                                           #pushl  %eax
0x8a, 0x85, 0x08, 0x13, 0x65, 0x00,             #movb   0x651308(%ebp),  %al

                                                #firerateRender.loopA:
0x0f, 0xb6, 0x94, 0x08, 0x3f, 0x13, 0x65, 0x00, #        movzbl 0x65133f(%eax,%ecx), %edx
0x52,                                           #        pushl  %edx
0xe2, 0xf5,                                     #loop firerateRender.loopA

0x3c, 0x0c,                                     #cmpb   $12,             %al
0x0f, 0x94, 0xc2,                               #sete   %dl
0x0f, 0x92, 0xc1,                               #setc   %cl
0x8d, 0x14, 0x4a,                               #leal   (%edx,%ecx,2),  %edx
0x8b, 0xc4,                                     #movl   %esp,           %eax
0x8b, 0xcf,                                     #movl   %edi,           %ecx
0x52,                                           #pushl  %edx
0xe8, 0xb9, 0x51, 0xf3, 0xff,                   #call   0x586cc0             #SetColor #0x586cc0-651b07

0x8b, 0xce,                                     #movl   %esi,           %ecx #FONT_PICO129
0x8b, 0xc7,                                     #movl   %edi,           %eax
0xe8, 0xa0, 0x51, 0xf3, 0xff,                   #call   0x586cb0             #SetFont #586cb0-651b10

0x58,                                           #popl   %eax
0x6a, 0x32,                                     #pushl  $50
0xdb, 0x04, 0x24,                               #fildl  (%esp)
0xd8, 0x84, 0x24, 0x18, 0x01, 0x00, 0x00,       #fadds  0x118(%esp)
0xdb, 0x1c, 0x24,                               #fistpl (%esp)
0x6a, 0x26,                                     #pushl  $38
0xdb, 0x04, 0x24,                               #fildl  (%esp)
0xd8, 0x84, 0x24, 0x18, 0x01, 0x00, 0x00,       #fadds  0x118(%esp)
0xdb, 0x1c, 0x24,                               #fistpl (%esp)
0xc1, 0xe0, 0x05,                               #shll   $5,             %eax
0x05, 0x60, 0x13, 0x65, 0x00,                   #addl   $0x651360,      %eax
0x50,                                           #pushl  %eax
0x8b, 0xc7,                                     #movl   %edi,           %eax
0xe8, 0xe1, 0x55, 0xf3, 0xff,                   #call   0x587120             #DrawString #587120-651b3f
0x83, 0xc4, 0x10,                               #addl   $0x10,          %esp

0x8b, 0xc7,                                     #movl   %edi,           %eax
0xb1, 0x00,                                     #movb   $0x0,            %cl
0xe8, 0xc5, 0x51, 0xf3, 0xff,                   #call   0x586d10             #SetColorizeImages #586d10-651b4b
0xc3                                            #retl
], 0x651ad0)
if randomVarsCatFireRate.get() != "Off":
    WriteMemory("unsigned char", [
    0xe8, 0xe7, 0x99, 0x1c, 0x00 #call 0x651ad0
    ], 0x4880e4)


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


# Limit previews
if limitPreviews.get():
    WriteMemory("unsigned char", [
        0x66, 0x90, # nop 2
    ], 0x43A608)
    WriteMemory("unsigned char", [
        0x83, 0xC4, 0x04, # add esp,4
        0x66, 0x90,       # nop 2
    ], 0x43A66C)


# Crazy Dave stuff
# I know this is a lot of code, but I'm not sure how to make it better - a lot of it is for umbrella/blover/torchwood.
# We need a lot of bytes to check whether umbrella/blover/torchwood are unlocked to make it work like in vanilla,
# and vanilla assumes these plants are unlocked already
WriteMemory("unsigned char", [
0x56,                                   # push esi // store original index
0x8B,0x34,0xB5,0x98,0x10,0x65,0x00,     # mov esi,[esi*4+popcapgame1.exe+251098] // load real plant
0xE8,0x03,0xB1,0xDC,0xFF,               # call popcapgame1.exe+1CC60 
0xE9,0x31,0x24,0xE3,0xFF,               # jmp popcapgame1.exe+83F93
0xC7,0x44,0xF4,0x14,0x00,0x00,0x00,0x00, # mov [esp+esi*8+14],00000000 // store 0 for weight
0xE9,0x14,0x25,0xE3,0xFF,               # jmp popcapgame1.exe+84083
0xC7,0x44,0xF4,0x14,0x01,0x00,0x00,0x00, # mov [esp+esi*8+14],00000001 // store 1 for weight
0xE9,0xFD,0x24,0xE3,0xFF,               # jmp popcapgame1.exe+84079
0x83,0x3D,0x90,0x10,0x65,0x00,(plants_array.index(37)-1),     # cmp dword ptr [popcapgame1.exe+251090],umbrella // umbrella workaround
0x0F,0x8E,0x2C,0x25,0xE3,0xFF,          # jng popcapgame1.exe+840B5
0x80,0xB8,0xEA,0x54,0x00,0x00,0x00,     # cmp byte ptr [eax+000054EA],00
0xE9,0x0A,0x25,0xE3,0xFF,               # jmp popcapgame1.exe+8409F
0x83,0x3D,0x90,0x10,0x65,0x00,(plants_array.index(27)-1),     # cmp dword ptr [popcapgame1.exe+251090],blover // blover workaround
0x0F,0x8E,0x63,0x25,0xE3,0xFF,          # jng popcapgame1.exe+84105
0x80,0xB8,0xE4,0x54,0x00,0x00,0x00,     # cmp byte ptr [eax+000054E4],00
0xE9,0x0E,0x25,0xE3,0xFF,               # jmp popcapgame1.exe+840BC
0xA1,0x90,0x10,0x65,0x00,               # mov eax,[651090] // check for whether we're leaving at least 1 slot free
0x48,                                   # dec eax
0x39,0xC7,                              # cmp edi,eax
0x0F,0x8C,0xC2,0x25,0xE3,0xFF,          # jl 0048417E // next iteration
0x5f,                                   # pop edi // original code
0xE9,0x51,0x26,0xE3,0xFF,               # jmp 00484213 // terminate picking plants
0x90,0x90,0x90,0x90,                    # nops // before rework, there were instructions
0x83,0xF9,0x31,                         # cmp ecx,31 // fix for when Dave is unable to pick any more plants - terminate iteration
0x75,0x0A,                              # jne popcapgame1.exe+251BD5
0xB9,0x01,0x00,0x00,0x00,               # mov ecx,00000001
0xE9,0x32,0x26,0xE3,0xFF,               # jmp popcapgame1.exe+84207
0x8B,0x45,0x08,                         # mov eax,[ebp+08]
0x8B,0xCB,                              # mov ecx,ebx
0xE9,0xDC,0x25,0xE3,0xFF,               # jmp popcapgame1.exe+841BB
], 
0x651b50)

# deactivate Dave
WriteMemory("unsigned char", [
            0x7e, 0x06, # original code  
            ],
            0x483F2A)
WriteMemory("unsigned char", [
            0x75, 0x16, # original code  
            ],
            0x483F1A)

# activate Dave
if enableDave.get() != 'False' or gamemode.get() == 'ng+':
    WriteMemory("unsigned char", [
        0x66, 0x90, # nop 2 // removes jump if this is first adventure
        ], 
        0x483F2A)
    WriteMemory("unsigned char", [
        0x66, 0x90, # nop 2 // removes jump if this is not an adventure
        ], 
        0x483F1A)
    WriteMemory("unsigned char", [
        0xE9,0xBD,0xDB,0x1C,0x00  # jmp popcapgame1.exe+251B50
        ], 
        0x483F8E)
    WriteMemory("unsigned char", [
        0xE9,0x0B,0xDA,0x1C,0x00  # jmp popcapgame1.exe+251BC6
        ], 
        0x4841B6)
    WriteMemory("unsigned char", [
        0x8B,0x5C,0x24,0x04       # mov ebx,[esp+04]
        ], 
        0x453b1c)
    WriteMemory("unsigned char", [
        0x89,0x5C,0x24,0x10       # mov [esp+10],ebx // stack adjustment
        ], 
        0x483f98)
    WriteMemory("unsigned char", [
        0x89,0x5C,0x24,0x10       # mov [esp+10],ebx // stack adjustment
        ], 
        0x483fd8)
    WriteMemory("unsigned char", [
        0x8B,0x5C,0x24,0x10       # mov ebx,[esp+10] // stack adjustment
        ], 
        0x484003)
    WriteMemory("unsigned char", [
        0xE8,0x19,0xFB,0xFC,0xFF  # call popcapgame1.exe+53B1C
        ], 
        0x483ffe)
    WriteMemory("unsigned char", [
        0x5E,                     # pop esi
        0xE9,0xF8,0xDA,0x1C,0x00, # jmp popcapgame1.exe+251B6F
        0x66,0x90                 # nop 2
        ], 
        0x484071)
    WriteMemory("unsigned char", [
        0x5E,                     # pop esi
        0xE9,0xE1,0xDA,0x1C,0x00, # jmp popcapgame1.exe+251B62
        0x66,0x90                 # nop 2
        ], 
        0x48407B)
    WriteMemory("unsigned char", [
        0xE9,0xDF,0xDA,0x1C,0x00, # jmp popcapgame1.exe+251B7C
        0x66,0x90                 # nop 2
        ], 
        0x484098)
    WriteMemory("unsigned char", [
        0xE9,0xDB,0xDA,0x1C,0x00, # jmp popcapgame1.exe+251B95
        0x66,0x90                 # nop 2
        ], 
        0x4840b5)
    # WriteMemory("unsigned char", [
    #     0xE9,0xA4,0xDA,0x1C,0x00, # jmp popcapgame1.exe+251BAE
    #     0x90                      # nop
    #     ], 
    #     0x484105)
    WriteMemory("unsigned char", [
        0xE9,0xF3,0x2C,0x00,0x00, # jmp popcapgame1.exe+86F10 // jump to UpdateAfterPurchase function to enable start button if needed,
        0x90                      # nop                       // stack is aligned in exact way needed to jump to that function as if it's the call
        ], 
        0x484218)
    WriteMemory("unsigned char", [
        daveActualPlantCount    # max amount of iterations to pick a plant
        ], 
        0x48420B)
    WriteMemory("unsigned char", [
        0x7D,0x05,                # jnl 484213 // picked max allowed count of plants
        0xE9,0x9B,0xD9,0x1C,0x00, # jmp 651BAE // check if we're leaving at least 1 slot free
        ], 
        0x48420C)
    WriteMemory("unsigned int", [
        (plants_array.index(37)-1)*8+20 # umbrella position on stack of weights
        ], 
        0x4840ad)
    WriteMemory("unsigned int", [
        (plants_array.index(27)-1)*8+20 # blover position on stack of weights
        ], 
        0x4840fd)
    WriteMemory("unsigned int", [
        (plants_array.index(22)-1)*8+20 # torchwood position on stack of weights
        ], 
        0x484118)
    
    if enableDave.get() == 'On + plant upgrades':
        WriteMemory("unsigned char", [
            0x83,0xFE,0x28,                     # cmp esi,28
            0x7C,0x23,                          # jl 00484062
            0x83,0x3D,0x90,0x10,0x65,0x00,(daveActualPlantCount + 1 - daveActualPlantCount // 5), # cmp dword ptr [00651090],picks_count
            0x7E,0x33,                          # jle 0048407B
            0x0F,0xB6,0x9E,0x32,0x40,0x48,0x00, # movzx ebx,byte ptr [esi+00484032]
            0xE8,0xCC,0xFA,0xFC,0xFF,           # call 00453B20
            0x84,0xC0,                          # test al,al
            0x74,0x23,                          # je 0048407B
            0xEB,0x08,                          # jmp 00484062
            (plants_array.index(7)-1),
            (plants_array.index(1)-1),
            (plants_array.index(10)-1),
            (plants_array.index(16)-1),
            (plants_array.index(39)-1),
            (plants_array.index(31)-1),
            (plants_array.index(21)-1),
            (plants_array.index(34)-1),
            ], 
            0x48403A)


if randomWorld.get() and gamemode.get() != "minigames":
    # hardcodes the next world for adventure mode: address for the world itself to change in main loop is 0x40a599
    WriteMemory("unsigned char", 
    [
        0x83, 0xFA, 0x32, 0x0F, 0x87, 0x0F, 0x00, 0x00, 0x00, 0xC7, 0x86, 0x4C, 0x55, 0x00, 0x00, 0x00, 0x00,
        0x00, 0x00, 0xE9, 0x93, 0x00, 0x00, 0x00, 0xC7, 0x86, 0x4C, 0x55, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
        0xE9, 0x84, 0x00, 0x00, 0x00
    ], 0x40A58A)

# random vars setup
if randomVarsSystemEnabled:
    if WINDOWS:
        # I pupposefully don't dealloc memory, because game will crash if player resets while still in level (and not in main menu),
        # it leaks ~192 kB of memory per reset, and it's year 2024
        string_stuff_address: int = VirtualAllocEx(pvz_handle, None, 0x30000, 0x1000, 0x40)
    else:
        string_stuff_address: int = 0x215010
    # +0: printing on board enabled (hotkey-toggleable)
    # +4: n of lines outputted onto board (since it doesn't support newline character) written by container
    # +8: n of lines outputted onto selection screen, which is n of lines on board minus 1
    # +0x100: hotkey code
    # +0x120: printing on lawn code
    # +0x1C0: printing on selection screen code
    hotkey_code_address = string_stuff_address + 0x100
    string_code_address = string_stuff_address + 0x120
    string_code_address_2 = string_stuff_address + 0x1C0 # used to print on selection screen
    random_zombie_size_address = string_stuff_address + 0x280
    random_zombie_size_address_max = random_zombie_size_address + 0x28
    random_zombie_size_address_min = random_zombie_size_address + 0x2C
    lose_sun_on_plant_death_address = random_zombie_size_address + 0x40
    lose_sun_on_plant_death_address_data = lose_sun_on_plant_death_address + 0x40
    click_on_sun_plant_address = lose_sun_on_plant_death_address + 0x50
    advance_cd_on_zombie_death_address = click_on_sun_plant_address + 0x30
    float_rebases_address = string_stuff_address + 0x800
    plants_string_address = string_stuff_address + 4 * 1024
    zombies_string_address = plants_string_address + 26 * 1024
    game_string_address = zombies_string_address + 18 * 1024
    plants_string_container = IndexedStrContainer("plants", plants_string_address, bytes_per_plant_string, n_of_plant_strings)
    zombies_string_container = IndexedStrContainer("zombies", zombies_string_address, bytes_per_zombie_string, n_of_zombie_strings)
    game_string_container = NonIndexedStrContainer("game", game_string_address, bytes_per_game_string, n_of_game_strings, string_stuff_address+4, string_stuff_address+8)
    game_string_container.add_var(SimpleOutputString(["Press Enter to show/hide"], "{}"))
    if randomWaveCount.get() != "False" and gamemode.get() == 'adventure':
        game_string_container.add_var(FlagCountString(current_level_flag_count, current_level_container, "Flags: {}"))
    if randomWaveCount.get() == "On" and gamemode.get() == 'adventure':
        game_string_container.add_var(FlagCountString(current_level_waves_per_flag, current_level_container, "Waves per flag: {}"))
    for index, el in enumerate(plant_names_container):
        plants_string_container.add_var(SimpleOutputString(el, "{}"), [index])
    for index, el in enumerate(zombie_names_container):
        zombies_string_container.add_var(SimpleOutputString(el, "{}"), [index])
    if randomCooldowns.get():
        for _, (index, el) in enumerate(plant_cooldowns_container.items()):
            # it's important we pass the same object as the object we modify in randomiseCooldowns, same for other non-constant values
            plants_string_container.add_var(SimpleOutputString(el, "cd: {:.1f} sec", modify_value_func=lambda cd: cd / 100), [index])
    if randomWavePoints.get() != 'False' and renderWavePoints.get():
        for _, (index, el) in enumerate(wavepoints_container.items()):
            if index == 10: #ducky
                continue
            zombies_string_container.add_var(SimpleOutputString(el, "Wave points: {}"), [index])
    if randomWeights.get() and renderWeights.get():
        for _, (index, el) in enumerate(zombie_weight_container.items()):
            if index == 10: # ducky
                continue
            zombies_string_container.add_var(SimpleOutputString(el, "Weight: {}"), [index])
    # Plant tooltip
    WriteMemory("unsigned char", [
        0x8B, 0x44, 0x24, 0x04, 0x83, 0xF8, 0x30, 0x7E, 0x05, 0xB8, 0x31, 0x00, 0x00, 0x00,
        0xC1, 0xE0, int(math.log2(bytes_per_plant_string)), 0x8D, 0x80, *list(plants_string_address.to_bytes(4, "little")),
        0x50, 0xE8, 0x83, 0xC6, 0xF9, 0xFF, 0xC3,
        ],
        0x467DB0)
    # Zombie tooltip
    WriteMemory("unsigned char", [
        0xC1, 0xE0, int(math.log2(bytes_per_zombie_string)), 0x8D, 0x80, *list(zombies_string_address.to_bytes(4, "little")),
        0x50, 0x8D, 0x74, 0x24, 0x34, 0x8B, 0xCE, 0xE8, 0xEE, 0x53, 0xFF, 0xFF, 0xEB, 0x12,
        ],
        0x40F04D)
    WriteMemory("unsigned char", [
        0xE8, 0x45, 0xB8, 0x10, 0x00, #SetLabel instead of SetTitle
        ],
        0x40F086)
    WriteMemory("unsigned char", [
        0x0F, 0x1F, 0x44, 0x00, 0x00, # nop 5 instead of call
        ],
        0x40f0d2)
    # enable tooltip for zombotany guys
    WriteMemory("unsigned char", [
        0xEB,
        ],
        0x40E7E8)
    # increase width of tooltips
    WriteMemory("unsigned char", [
        0x7F,
        ],
        0x51A77A)
    WriteMemory("unsigned char", [
        0x90, 0x90
        ],
        0x51A77B)
    WriteMemory("unsigned char", [
        0x00, 0x01
        ],
        0x51A77E)
    # Rendering strings on board
    string_print_x_coord = 50
    string_print_y_coord = 116 # can't be higher than 127 with current implementation!
    string_print_x_coord_seed_selection = 860
    string_print_y_coord_seed_selection = 105 # can't be higher than 127 with current implementation!
    WriteMemory("unsigned char", [
        0xA1,*list(string_stuff_address.to_bytes(4,"little")),0x85,0xC0,0x74,0x7C,0x8B,0x4C,0x24,0x08,0xA1,0xEC,
        0x72,0x6A,0x00,0x89,0x41,0x40,0x68,0xFF,0x00,0x00,0x00,0x68,0xFF,0x00,0x00,
        0x00,0x68,0xFF,0x00,0x00,0x00,0x68,0xFF,0x00,0x00,0x00,0x8B,0xC4,0xE8,
        *list((0x586CC0-string_code_address-0x30).to_bytes(4,"little",signed=True)),
        0x83,0xC4,0x10,0x56,0x8B,0x35,*list((string_stuff_address+4).to_bytes(4,"little")),0x68,
        *list(game_string_address.to_bytes(4,"little")),0x6A,string_print_y_coord,0x85,0xF6,0x74,0x3C,0x83,0xEC,0x1C,0x8B,0xCC,0x8B,0x44,
        0x24,0x20,0x50,0xE8,*list((0x404450-string_code_address-0x54).to_bytes(4,"little",signed=True)),0x50,0x8B,0x54,0x24,0x20,0x52,0x68,
        *(string_print_x_coord.to_bytes(4,"little",signed=True)),0x50,0x8B,0x44,0x24,0x40,0xE8,*list((0x587120-string_code_address-0x69).to_bytes(4,"little",signed=True)),
        0x59,0xE8,*list((0x404420-string_code_address-0x6F).to_bytes(4,"little",signed=True)),
        0x83,0xC4,0x1C,0x5A,0x83,0xC2,0x16,0x58,0x05,*list(bytes_per_game_string.to_bytes(4,"little",signed=True)),0x50,0x52,
        0x4E,0x75,0xC4,0x83,0xC4,0x08,0x5E,
        0xE9,*list((0x41AA45-string_code_address-0x8A).to_bytes(4,"little",signed=True)),
        ],
        string_code_address)
    # Rendering strings on selection screen
    WriteMemory("unsigned char", [
        0xB8,0x01,0x00,0x00,0x00,0x85,0xC0,0x74,0x7C,0x8B,0x4C,0x24,0x08,0xA1,0x30,
        0x76,0x6A,0x00,0x89,0x41,0x40,0x68,0xFF,0x00,0x00,0x00,0x68,0x00,0x00,0x00,
        0x00,0x68,0x00,0x00,0x00,0x00,0x68,0xFF,0x00,0x00,0x00,0x8B,0xC4,0xE8,
        *list((0x586CC0-string_code_address_2-0x30).to_bytes(4,"little",signed=True)),
        0x83,0xC4,0x10,0x56,0x8B,0x35,*list((string_stuff_address+8).to_bytes(4,"little")),0x68,
        *list((game_string_address+bytes_per_game_string).to_bytes(4,"little")),0x6A,string_print_y_coord_seed_selection,0x85,0xF6,0x74,0x3C,0x83,0xEC,0x1C,0x8B,0xCC,0x8B,0x44,
        0x24,0x20,0x50,0xE8,*list((0x404450-string_code_address_2-0x54).to_bytes(4,"little",signed=True)),0x50,0x8B,0x54,0x24,0x20,0x52,0x68,
        *(string_print_x_coord_seed_selection.to_bytes(4,"little",signed=True)),0x50,0x8B,0x44,0x24,0x40,0xE8,*list((0x587120-string_code_address_2-0x69).to_bytes(4,"little",signed=True)),
        0x59,0xE8,*list((0x404420-string_code_address_2-0x6F).to_bytes(4,"little",signed=True)),
        0x83,0xC4,0x1C,0x5A,0x83,0xC2,0x10,0x58,0x05,*list(bytes_per_game_string.to_bytes(4,"little",signed=True)),0x50,0x52,
        0x4E,0x75,0xC4,0x83,0xC4,0x08,0x5E,0x6A,0xFF,0x64,0xA1,0x00,0x00,0x00,0x00,0x68,0xD8,0xE5,0x64,0x00,
        0xE9,*list((0x41AA4D-string_code_address_2-0x97).to_bytes(4,"little",signed=True)),
        ],
        string_code_address_2)
    WriteMemory("unsigned char", [
        0xE9, *list((string_code_address-0x41AA45).to_bytes(4,"little",signed=True)),
        0xE9, *list((string_code_address_2-0x41AA4A).to_bytes(4,"little",signed=True)),
        0x0F, 0x1F, 0x00,
        ],
        0x41AA40)
    # Hotkey for switching string printing
    WriteMemory("unsigned char", [
        0x83, 0xFF, 0x0D, 0x75, 0x07, 0x83, 0x35, *list(string_stuff_address.to_bytes(4, "little")), 0x01,
        0x83, 0xFF, 0x20, 0x0F, 0x84, *list((0x41B86C-hotkey_code_address-0x15).to_bytes(4,"little",signed=True)),
        0xE9, *list((0x41B867-hotkey_code_address-0x1A).to_bytes(4,"little",signed=True)),
        ],
        hotkey_code_address)
    WriteMemory("unsigned char", [
        0xE9, *list((hotkey_code_address-0x41B867).to_bytes(4,"little",signed=True)),
        ],
        0x41B862)
    
    # Random zombie sizes effect
    WriteMemory("unsigned char", [
        0x88, 0x5F, 0x78, 0xD9, 0x05, *random_zombie_size_address_max.to_bytes(4,"little",signed=True), 0x51, 0xD9, 0x1C, 0x24,
        0xD9, 0x05, *random_zombie_size_address_min.to_bytes(4,"little",signed=True),
        0x51, 0xD9, 0x1C, 0x24, 0xE8, *(0x511CB0-random_zombie_size_address-0x1C).to_bytes(4,"little",signed=True),
        0x83, 0xC4, 0x08, 0xE9, *(0x5226E2-random_zombie_size_address-0x24).to_bytes(4,"little",signed=True),
    ],
    random_zombie_size_address)
    WriteMemory("float", [1.5], random_zombie_size_address_max)
    WriteMemory("float", [0.5], random_zombie_size_address_min)

    # lose sun on plant death
    WriteMemory("unsigned char", [
        0x89, 0x85, 0x5C, 0x55, 0x00, 0x00, 0x8B, 0x85, 0x00, 0x56, 0x00, 0x00, 0x85, 0xC0, 0x7D, 0x28, 0x8B, 0x85, 0x98, 0x57, 0x00, 0x00, 0x03, 0x85,
        0x9C, 0x57, 0x00, 0x00, 0x2B, 0x05, *lose_sun_on_plant_death_address_data.to_bytes(4,"little",signed=True), 0x0F, 0x8E, 0x10, 0x00,
        0x00, 0x00, 0x01, 0x05, *lose_sun_on_plant_death_address_data.to_bytes(4,"little",signed=True), 0x83, 0xAD, 0x60, 0x55, 0x00, 0x00,
        0x32, 0x48, 0x7F, 0xF6, 0xE9, *(0x416064-lose_sun_on_plant_death_address-0x3D).to_bytes(4,"little",signed=True)
    ],
    lose_sun_on_plant_death_address)
    WriteMemory("unsigned int", [0], lose_sun_on_plant_death_address_data)

    # Click on sun plants
    countdown_removed_per_click = 35 # max is 127
    WriteMemory("unsigned char", [
        0x83, 0x7E, 0x24, 0x01, 0x74, 0x0C, 0x83, 0x7E, 0x24, 0x09, 0x74, 0x06, 0x83,
        0x7E, 0x24, 0x29, 0x75, 0x04, 0x83, 0x6E, 0x58, countdown_removed_per_click, 0x83, 0x7E, 0x3C, 0x25,
        0x57, 0xE9, *(0x466395-click_on_sun_plant_address-0x20).to_bytes(4,"little",signed=True)
    ],
    click_on_sun_plant_address)

    # Advance cooldowns on zombie death
    advance = 200
    WriteMemory("unsigned char", [
        0x8B, 0x47, 0x6C, 0x85, 0xC0, 0x7C, 0x24, 0x8B, 0x47, 0x04, 0x8B, 0x80, 0x44, 0x01, 0x00, 0x00,
        0x83, 0xC0, 0x28, 0xB9, 0x0A, 0x00, 0x00, 0x00, 0x80, 0x78, 0x49, 0x00, 0x74, 0x07, 0x81, 0x40,
        0x24, *(advance).to_bytes(4,"little",signed=True), 0x83, 0xC0, 0x50, 0x49, 0x7F, 0xED, 0x5F, 0x8B, 0xE5, 0x5D, 0xC3,
        0xE9, *(0x530638-advance_cd_on_zombie_death_address-0x35).to_bytes(4,"little",signed=True),
    ],
    advance_cd_on_zombie_death_address)

    random_vars = RandomVars(seed, WriteMemory, True, plants_string_container, zombies_string_container, game_string_container,
                             code_address=string_stuff_address, catZombieHealth=actualRandomVarsZombieHealth, catFireRate=actualRandomVarsFireRate,
                             randomShit=randomShit.get())
    random_vars.reset()

if randomCooldowns.get():
    WriteMemory("unsigned char",[255,255],0x6512C2) # make peashooter/sunflower not red on first level
WriteMemory("int",[150],0x69F2CC) # reset peashooter fire rate
plants_unlocked = 1
WriteMemory("int", plants_array, 0x651094)
WriteMemory("int", plants_array2, 0x651194) #ends at 0x65125c
WriteMemory("int",0,0x65115c)
upgradePlants=[0x1C4, 0x1C2, 0x1C8, 0x1D4, 0x1CC, 0x1D8, 0x1E0, 0x1D0, 0x1DC, "nothing", "nothing2"] #twin, gatling, gloom, gold, cattail, spike, imitater, winter, cob
WriteMemory("unsigned int", [wavecount_per_level[x] for x in sorted(list(wavecount_per_level.keys()))], 0x6A34E8) # waves per level; that also resets them to default if randomWavecount is off
WriteMemory("unsigned int", 10, 0x40907B) # reset waves per flag
WriteMemory("unsigned int", 10, 0x4090D2) # reset waves per flag
if startingWave.get()=="Instant":
    randomiseStartingWave(startingWave.get())
if saved.get() and jumpLevel!="":
    for a in range(len(levels)):
        if levels[a]==jumpLevel:
            savePoint=a+1

if gamemode.get() != 'adventure':
    # get golden sunflower + buy items
    WriteMemory("int", [2], 0x6A9EC0, 0x82c, 0x2c) # 2 adventure completions
    for i in range(33):
        WriteMemory("int", [1], 0x6A9EC0, 0x82c, 0x6c+4*i) # mini-games
    for i in range(9):
        WriteMemory("int", [1], 0x6A9EC0, 0x82c, 0xf8+4*i) # vasebreakers
    for i in range(9):
        WriteMemory("int", [1], 0x6A9EC0, 0x82c, 0x120+4*i) # i zombies
    for i in range(5):
        WriteMemory("int", [5], 0x6A9EC0, 0x82c, 0x30+4*i) # survivals
    for i in range(5):
        WriteMemory("int", [10], 0x6A9EC0, 0x82c, 0x44+4*i) # hard survivals
    if not shopless.get():
        for i in range(9):
            WriteMemory("int", [1], 0x6A9EC0, 0x82c, 0x1c0+4*i) # shop
        WriteMemory("int",[4],0x6A9EC0,0x82C, 0x214) # slots
        WriteMemory("int",[1],0x6A9EC0,0x82C,0x21C) # cleaners
        WriteMemory("int",[1],0x6A9EC0,0x82C,0x218) # cleaners
        WriteMemory("int",[1],0x6A9EC0,0x82C,0x234) # first aid
        WriteMemory("int",[200],0x6A9EC0,0x82C, 0x28) # money
    WriteMemory("unsigned char", [0x38], 0x42df5d) # limbo
    plants_unlocked = 40
    WriteMemory("int",plants_unlocked,0x651090) # needed for Dave I think

def should_keep_sleeping():
    if gamemode.get() == "minigames":
        return game_ui() != 3 or ReadMemory("int",0x6A9EC0,0x768) == 0 or \
                    (ReadMemory("int",0x6A9EC0,0x768, 0x5600) < 100 and \
                    ReadMemory("int",0x6A9EC0,0x768, 0x5604) < 100)
    else:
        return game_ui() != 3 or ReadMemory("bool",0x6A9EC0,0x768, 0x5603)

def wait_level_end_or_game_close():
    # so, there was a restart bug, when randomiser falsely detected the end of level - probably because the game board is deleted and initialized
    # when level restarts - and reading memory at the same moment might cause a false positive. So, we have to check if the level is really over
    # by checking twice with a small delay in between.
    # However, there's also a possibility for read to produce an exception (probably because board is being NULL for some time, or if game is closed).
    # So we have to catch those exceptions. And if we catch a lot of them in a row, we assume the game is closed.
    # But, if reading/writing makes an exception, pvz module doesn't release a memory lock, so we have to release it manually - or
    # rando will be stuck forever waiting for a lock to be released. For linux we use fake lock, so releasing it does nothing, just keeps code clean.
    # However, sometimes pvz module detects that game is closed, and in such case reading memory doesn't acquire lock before throwing exception,
    # so releasing that lock produces another exception - and we have to catch that one too in order to detect that game closed and to not crash rando.
    # And we got that code mess as a result.
    exception_counter = 0   # using it to detect user closing the game
    sleep_cond = True
    while sleep_cond:
        if exception_counter > 5:
            print("game closed")
            input()
            exit()
        Sleep(0.1)
        try: # detecting the end of level
            sleep_cond = should_keep_sleeping()
            exception_counter = 0
        except: # exception might happen when restarting the level, in which case we continue to sleep, but also have to release pvz module lock
            print('caught exception')
            exception_counter += 1
            sleep_cond = True
            try: # sometimes on windows, if game is closed, pvz module doesn't acquire lock, and releasing it produces an exception
                memory_lock.release()
            except:
                print("game closed")
                input()
                exit()
        if not sleep_cond and not saved.get(): # here we detect level end again to make sure we are not encoutering restart bug
            Sleep(5)
            try:
                old_sleep_cond = sleep_cond
                sleep_cond = should_keep_sleeping()
                if old_sleep_cond != sleep_cond:
                    print('caught restart bug')
                    sleep_cond = True
            except:
                print('caught exception 2')
                sleep_cond = True
                try: # sometimes on windows, if game is closed, pvz module doesn't acquire lock, and releasing it produces an exception
                    memory_lock.release()
                except:
                    print("game closed")
                    input()
                    exit()


if gamemode.get() == 'minigames':
    if randomZombies.get():
        WriteMemory("unsigned char", [ # minigames random zombies
            0x57,                          # push edi
            0x56,                          # push esi
            0xB9, 0x21,0x00,0x00,0x00,     # mov ecx,00000021
            0x83, 0xEA, 0x10,              # sub edx,10
            0x0F,0xAF, 0xD1,               # imul edx,ecx
            0x8B, 0x7E, 0x04,              # mov edi,[esi+04]
            0x81, 0xC7, 0xD4,0x54,0x00,0x00, # add edi,000054D4
            0x8D, 0xB2, 0xAA,0x58,0x42,0x00, # lea esi,[edx+popcapgame1.exe+258AA]
            0xF3, 0xA4,                    # repe movsb 
            0x5E,                          # pop esi
            0x5F,                          # pop edi
            0xE9, 0x73,0x04,0x00,0x00,     # jmp popcapgame1.exe+25D1D
            ], 0x425885)
        WriteMemory("unsigned char",[0xEB], 0x42585C) # survivals enable first flag rando
        WriteMemory("unsigned char",[0x66, 0x0F, 0x1F, 0x44, 0x00, 0x00,], 0x425752) # survivals allow digger on roof
        WriteMemory("unsigned char",[0x66, 0x0F, 0x1F, 0x44, 0x00, 0x00,], 0x42575B) # survivals allow dancer on roof
        WriteMemory("unsigned char",[0x66, 0x0F, 0x1F, 0x44, 0x00, 0x00,], 0x42576F) # survivals allow zamboni on graves
        WriteMemory("unsigned char",[0x66, 0x0F, 0x1F, 0x44, 0x00, 0x00,], 0x425799) # survivals allow bungee everywhere
        if noRestrictions.get():
            WriteMemory("unsigned char",[0x66, 0x90,], 0x4257C0) # survivals allow giga gargs always
        else:
            WriteMemory("unsigned char",[0x07,], 0x4257BA) # survivals allow giga gargs after 7 flags instead of default 10
        WriteMemory("unsigned char",[0x66, 0x90,], 0x4257DD) # survivals allow zombies after snorkel spawn on day-pool normal survivals
        WriteMemory("unsigned char",[0x66, 0x90,], 0x4257E2) # survivals allow bobsleds
        WriteMemory("unsigned char",[0x66, 0x90,], 0x4257F6) # survivals allow zombotanies
        WriteMemory("unsigned char",[0x66, 0x90,], 0x4257FB) # survivals allow zombotanies
        WriteMemory("unsigned char",[0x66, 0x90,], 0x425800) # survivals allow zombotanies
        WriteMemory("unsigned char",[0x66, 0x90,], 0x425805) # survivals allow zombotanies
        WriteMemory("unsigned char",[0x66, 0x90,], 0x42580A) # survivals allow zombotanies
        WriteMemory("unsigned char",[0x66, 0x90,], 0x42580F) # survivals allow zombotanies

    if enableDave.get() != 'False':
        WriteMemory("unsigned char",[0xEB],0x483EC3) # Dave seeing stars fix
    if savePoint > 150:
        savePoint = 150
    for i in range(1000000):
        global_level_index = i
        if saved.get():
            if savePoint-1==i:
                saved.set(False)
        if not saved.get():
            linesToWrite=[seed, str(i+1), "0", "0", *settings_lines_to_save()]
            saveFile=open('saveFile.txt', 'w')
            for k in range(len(linesToWrite)):
                linesToWrite[k]=str(linesToWrite[k])
                linesToWrite[k]=linesToWrite[k]+"\n"
            saveFile.writelines(linesToWrite)
            saveFile.close()
        print(str(i+1))
        if randomZombies.get():
            randomiseZombiesMinigames()
        if randomWeights.get():
            randomiseWeights(minigames=True)
        if randomWavePoints.get()!="False":
            randomiseWavePoints(minigames=True)
        if randomCost.get():
            randomiseCost()
        if randomCooldowns.get():
            randomiseCooldown()
        if enableDave.get() != "False" and davePlantsCount.get() == "random(1-5)":
            randomiseDavePlantCount()
        if startingWave.get()=="Random":
            randomiseStartingWave(startingWave)
        if randomVarsSystemEnabled:
            # optimization - we don't actually write random vars and strings when using jump-to-level, but still randomize then (so seed works)
            WriteMemory("unsigned char", [12 for i in range(56)], 0x651308)
            random_vars.randomize(-1, do_write=not saved.get())
        if not saved.get() and randomSound.get():
            randomiseSounds()
        if saved.get():
            Sleep(1)
        else:
            Sleep(500)
        if shopless.get():
            WriteMemory("int",0,0x6A9EC0,0x82C, 0x28)
        if saved.get():
            Sleep(1)
        else:
            Sleep(500)
        if shopless.get():
            WriteMemory("int",0,0x6A9EC0,0x82C, 0x28)
        wait_level_end_or_game_close() # if game is closed, tha function exits the program after waiting for an input
             
else:
    #WriteMemory("int", [2], 0x409326) # make 2-5 short
    for i in range(50):
        global_level_index = i
        current_level_container[0] = levels[i]
        if gamemode.get() == 'adventure':
            if i == 0:
                WriteMemory("int", 50, 0x69F2CC) # quicken level 1-1
                WriteMemory("int", 10, 0x41523D) # quicken level 1-1
                WriteMemory("int", 10, 0x413F4B) # quicken level 1-1
                WriteMemory("int", 2, 0x6A34E8) # quicken level 1-1
            elif i == 1:
                WriteMemory("int", 150, 0x69F2CC) # reset from level 1-1
                WriteMemory("int", 200, 0x413F4B) # reset from level 1-1
                WriteMemory("int", 4, 0x6A34E8) # reset from level 1-1
        if saved.get():
            if savePoint-1==i:
                saved.set(False)
        if not saved.get() and i!=0:
            linesToWrite=[seed, (i+1), str(ReadMemory("int", 0x6A9EC0,0x82C,0x214)), str(ReadMemory("int",0x6A9EC0,0x82C, 0x28)), *settings_lines_to_save()]
            saveFile=open('saveFile.txt', 'w')
            for k in range(len(linesToWrite)):
                linesToWrite[k]=str(linesToWrite[k])+"\n"
            saveFile.writelines(linesToWrite)
            saveFile.close()
            if i!=0 and (randomWavePoints.get()!="False" or randomWeights.get()):
                print(" "*100)
                print("Level:", convertToLevel(levels[i-1]))
                zombies_type_offset = ReadMemory("unsigned int", 0x6A9EC0, 0x768) + 0x54D4
                zombies_type = ReadMemory("bool",zombies_type_offset,array=33)
                for j in range(0, 33):
                    if(zombies_type[j]):
                        print(zombies[j][0], str(ReadMemory("int", 0x69DA88 + 0x1C*j)), ReadMemory("int", 0x69DA94 + 0x1C*j),ReadMemory("int", 0x69DA90 + 0x1C*j))
        print(str(i+1))
        if gamemode.get() == 'adventure':
            WriteMemory("int",plants_unlocked,0x651090)
        if seeded.get() and not saved.get():
            WriteMemory("int", [0 for j in range(1024)], rng_addr+0x10)
            WriteMemory("int", rng_addr+0x1010, rng_addr)
        newlevel=levels[i]
        if(i == 0) and not saved.get():
            try:
                while(ReadMemory("int",0x6A9EC0,0x82C, 0x24) != 1): # current level
                    Sleep(0.1)
            except:
                print("oops")
        if not noAutoSlots.get() or shopless.get():
            WriteMemory("int",0,0x6A9EC0,0x82C, 0x28)
        if randomZombies.get():
            if i!=0:
                currentZombies=randomiseZombies(zombiesToRandomise, i-1, levels)
            currentZombies=randomiseZombies(zombiesToRandomise, i, levels)
        if upgradeRewards.get() and gamemode.get() == 'adventure':
            if i!=0:
                if(level_plants[lastlevel] == -1):
                    if randomisePlants.get():
                        if len(upgradePlants)!=0:
                            newUpgrade=upgrade_rng.choice(upgradePlants)
                            upgradePlants.remove(newUpgrade)
                            if newUpgrade!="nothing" and newUpgrade!="nothing2":
                                WriteMemory("bool",True,0x6A9EC0,0x82C,newUpgrade)
                    else:
                        if lastlevel!=49 and lastlevel!=50:
                            WriteMemory("bool",True,0x6A9EC0,0x82C,upgradePlants[lastlevel//5])
            lastlevel=newlevel
        if imitater.get() and i != 0 and gamemode.get() == 'adventure':
            WriteMemory("bool",True,0x6A9EC0,0x82C,0x1E0)
            WriteMemory("int", 0, 0x453aea)
        if not saved.get():
            WriteMemory("int",newlevel,0x6A9EC0,0x82C, 0x24)
        if randomWeights.get():
            randomiseWeights()
        if randomWavePoints.get()!="False":
            randomiseWavePoints()
        if randomWaveCount.get() != "False" and gamemode.get() == 'adventure':
            WriteMemory("unsigned int", [waves_per_flag[levels[i]]], 0x40907B)
            WriteMemory("unsigned int", [waves_per_flag[levels[i]]], 0x4090D2)
            current_level_flag_count[0] = flags_per_level[levels[i]]
            current_level_waves_per_flag[0] = waves_per_flag[levels[i]]
        if randomWorld.get():
            WriteMemory("unsigned int", level_worlds[levels[i]], 0x40A599)
        if i!=0 or gamemode.get() == 'ng+':
            if randomCost.get():
                randomiseCost()
            if randomCooldowns.get():
                randomiseCooldown()
            if enableDave.get() != "False" and davePlantsCount.get() == "random(1-5)":
                randomiseDavePlantCount()
        if startingWave.get()=="Random":
            randomiseStartingWave(startingWave)
        if not saved.get():
            WriteMemory("int",newlevel,0x651190)
        if randomVarsSystemEnabled and (i!=0 or gamemode.get() == 'ng+'):
            # optimization - we don't actually write random vars and strings when using jump-to-level, but still randomize then (so seed works)
            WriteMemory("unsigned char", [12 for i in range(56)], 0x651308)
            random_vars.randomize(levels[i], do_write=not saved.get())
        if not shopless.get():
            WriteMemory("bool",True,0x6A9EC0,0x82C,0x21C)
            WriteMemory("bool",True,0x6A9EC0,0x82C,0x218)
        if (i == 0 or not saved.get()) and randomSound.get():
            randomiseSounds()
        if(i != 0) and not saved.get(): 
            Sleep(1)
        if gamemode.get() == 'adventure' and (level_plants[newlevel] != -1):
            plants_unlocked += 1
        if(i >= 24 and not (shopless.get() or noAutoSlots.get())): # slots
            WriteMemory("int",2,0x6A9EC0,0x82C,0x214)
        elif(i >= 14 and not (shopless.get() or noAutoSlots.get())):
            WriteMemory("int",1,0x6A9EC0,0x82C,0x214)
        if(i == 0) and not saved.get():
            while(game_ui() != 3):
                Sleep(0.1)
        if saved.get():
            Sleep(1)
        else:
            Sleep(500)
        if not noAutoSlots.get() or shopless.get():
            WriteMemory("int",0,0x6A9EC0,0x82C, 0x28)
        if saved.get():
            Sleep(1)
        else:
            Sleep(500)
        if not noAutoSlots.get() or shopless.get():
            WriteMemory("int",0,0x6A9EC0,0x82C, 0x28)
        wait_level_end_or_game_close() # if game is closed, tha function exits the program after waiting for an input
        WriteMemory("int",i,0x65115c)

WriteMemory("int",0,0x651190)

linesToWrite=[seed, "finished", str(ReadMemory("int", 0x6A9EC0,0x82C,0x214)), str(ReadMemory("int",0x6A9EC0,0x82C, 0x28)), *settings_lines_to_save()]
saveFile=open('saveFile.txt', 'w')
for k in range(len(linesToWrite)):
    linesToWrite[k]=str(linesToWrite[k])
    linesToWrite[k]=linesToWrite[k]+"\n"
saveFile.writelines(linesToWrite)
saveFile.close()

if randomZombies.get():
    randomiseZombies(zombiesToRandomise, 49, levels)

for i in range(0, 48):
    WriteMemory("int", plants[i][0], 0x69F2C0 + 0x24*i)
    WriteMemory("int", plants[i][1], 0x69F2C4 + 0x24*i)
for i in range(0, 33):
    WriteMemory("int", zombies[i][3], 0x69DA88 + 0x1C*i)
    WriteMemory("int", zombies[i][2], 0x69DA94 + 0x1C*i)
    WriteMemory("int", zombies[i][4], 0x69DA90 + 0x1C*i)
    WriteMemory("int", zombies[i][1], 0x69DA8C + 0x1C*i)

while True:
    Sleep(10)
    WriteMemory("bool",True,0x6A9EC0,0x82C,0x21C)
