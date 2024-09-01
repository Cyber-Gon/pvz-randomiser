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
window=Tk() #Creates a window object from the Tk class
window.title("Randomiser settings")
challengeMode=False
shopless=False
noRestrictions=False
noAutoSlots=False
imitater=False
randomisePlants=False
seeded=False
upgradeRewards=False
randomWeights=False
randomWavePoints=False
saved=False
startingWave="False"
randomCost=False
randomCooldowns=False
seed=str(random.randint(1,999999999999))



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

def upgradeButtonClick():
    global upgradeRewards
    upgradeRewards=not upgradeRewards
    buttonClick()

def seededButtonClick():
    global seeded
    seeded=not seeded
    buttonClick()

def randomWeightsButtonClick():
    global randomWeights
    randomWeights=not randomWeights
    buttonClick()

def randomWavePointsButtonClick():
    global randomWavePoints
    if randomWavePoints==False:
        randomWavePoints="Normal"
    elif randomWavePoints=="Normal":
        randomWavePoints="EXTREME"
    elif randomWavePoints=="EXTREME":
        randomWavePoints=False
    buttonClick()

def startingWaveButtonClick():
    global startingWave
    if startingWave=="False":
        startingWave="Random"
    elif startingWave=="Random":
        startingWave="Instant"
    elif startingWave=="Instant":
        startingWave="False"
    buttonClick()

def costButtonClick():
    global randomCost
    randomCost=not randomCost
    buttonClick()

def cooldownButtonClick():
    global randomCooldowns
    randomCooldowns=not randomCooldowns
    buttonClick()

def continueButtonClick():
    global seed, challengeMode, shopless, noRestrictions, noAutoSlots, imitater, randomisePlants, seeded, upgradeRewards, randomWeights, randomWavePoints, startingWave, randomCost, randomCooldowns, saved, savePoint, fileInfo, jumpLevel
    seed=fileInfo[0].strip()
    savePoint=int(fileInfo[1].strip())
    WriteMemory("int", int(fileInfo[2].strip()), 0x6A9EC0,0x82C,0x214) #slots
    WriteMemory("int", int(fileInfo[3].strip()), 0x6A9EC0,0x82C,0x28) #money
    challengeMode=eval(fileInfo[4].strip())
    shopless=eval(fileInfo[5].strip())
    noRestrictions=eval(fileInfo[6].strip())
    noAutoSlots=eval(fileInfo[7].strip())
    imitater=eval(fileInfo[8].strip())
    randomisePlants=eval(fileInfo[9].strip())
    #seeded=eval(fileInfo[10].strip())
    seeded=False
    upgradeRewards=eval(fileInfo[11].strip())
    randomWeights=eval(fileInfo[12].strip())
    randomWavePoints=fileInfo[13].strip()
    startingWave=fileInfo[14].strip()
    randomCost=eval(fileInfo[15].strip())
    randomCooldowns=eval(fileInfo[16].strip())
    saved=True
    jumpLevel=""
    if randomWavePoints=="False":
        randomWavePoints=False
    window.destroy()
    
def closeButtonClick():
    getSeed()
    getLevel()
    window.destroy()

def informationButtonClick():
    outputText.delete(0.0, END)
    manipulatedText="Aaronthewinner made the original version that randomised the levels. BulbasaurRepresent created most of the logic, modifiers, and GUI. Vsoup.vx did most of the complex stuff, including making the seed select update to show the right plants. LunarBlessing added the tooltip for the random cooldowns, and made the starting cooldowns scale with their actual cooldowns. REALLY IMPORTANT: If you use either RANDOM WEIGHTS or RAND WAVE POINTS, and then you want to do another run WITHOUT those modifiers, close and reopen the game, otherwise things will be funky. Additionally, if you are continuing a saved run / jumping to a specific level, be aware that SEEDED mode does not work with it, and so is automatically disabled." + " "*spaces + "The jump level box allows you to jump to a specific level in the seed! This is great for recovering from a crash if you know your seed but for some reason the save file got corrupted. Just play 1-1 and then you should be at the same level (although with nothing bought from the shop)." + " "*spaces + "The Continue Last Run button only appears if you have an incomplete run in your save data. If you do, pressing this will close the settings menu and give you the same settings as before. After you play 1-1, you should be at the level you were previously at! You will also have the same plants, same money, and the same amount of slot upgrades. You will NOT save any other things bought from the shop (such as rakes or pre-unlocked upgrade plants)." + " "*spaces + "Challenge Mode gets rid of the tough level restriction. With this disabled, you will not be able to play certain levels (like 5-2) without having 3 good plants. Other levels (like 5-9) will need 5 good plants to play. With this enabled, as soon as you unlock flower pot, you can play both 5-2 and 5-9 (for instance)." + (" " * spaces) + "Shopless mode forces you to play with 6 slots and no automatic pool cleaners / roof cleaners." + (" " * spaces) + "No restrictions mode means that there is no logic as to what levels can be played next - the majority of no restrictions runs are impossible." + (" " * spaces) + "With manual money enabled, you do not get automatic slot upgrades, but your money does not reset to 0 after every level, and so you can purchase the slots yourself - this also means you can buy rakes and upgrade plants!" + (" " * spaces) + "Instant imitater mode gives you access to an imitater immediately, which allows you to choose one of any plant to bring to the stage, even if you haven't unlocked it! This works especially well with no restrictions." + (" " * spaces) + "Random plants means that the plant you get at the end of each level is RANDOMISED, in a similar way to the levels! Instead of unlocking the plant you usually unlock for beating that stage, you get a random one!" + (" " * spaces) + "Seeded means that the seed you enter will not only affect the random plants and levels you get, but also the zombie spawns and other types of RNG, which makes it perfect for races!" + (" " * spaces) + "Random upgrades means that most levels that would usually give you no reward instead gives you an upgrade plant! It is important to note that if you have 4 plants total and one upgrade plant, you will not have 4 seed slots - sorry about that." + (" " * spaces) + "Random Weights means that the likelihood for a zombie to spawn is a random number, and this changes from level to level. Cones might be extremely unlikely one level, and then extremely likely the next one!" + (" " * spaces) + "Random Wave Points has two modes: Normal and EXTREME. Normal mode means that a zombie's wave points can either stay the same, or increase/decrease by 1 wave point if they originally cost less than 5 wave points, 2 wave points if they originally cost 5-7 wave points, and 3 wave points if they originally cost 10 wave points. EXTREME mode means that a zombie's wave point value is a random number from 2 to 7 (or, in rare cases, 10). This changes from level to level, and the basic zombie always costs 1 wave point while the cone zombie always costs either 2 or 3 wave points. There is no guarantee that EXTREME mode is always possible. If you're using either randomised weights or randomised wave points, you can look at the program during the run to see a rundown of what weights and wave points each zombie type had!" + "" * spaces + "The starting wave refers to what wave the zombies can start spawning at. Usually, the day/night zombies can spawn in the first 10 waves while the other zombies cannot. Random mode means that each zombie (except for basics, cones, and newspapers) has a random starting wave from 4 to 10. Vaulters, buckets, and screen-doors have a random starting wave from 1 to 10. Instant mode means that every zombie can immediately spawn from wave 1 (provided there is enough wave points)." +" " * spaces + "Random costs will set the cost of almost every plant to 50-200% of the original price! The only exception is the sunflower (and the peashooter in 1-1)." +" "*spaces +"Random cooldowns will set the cooldown of almost every plant to 50-200% of the original cooldown! The only exceptions are sunflower, puff shroom, and flower pot." 
    outputText.insert(END, manipulatedText)

def buttonClick():
    global noRestrictions, challengeMode, shopless, noAutoSlots, imitater, randomisePlants, spaces, seeded
    outputText.delete(0.0, END) #this clears the contents of the text box widget
    if not noRestrictions:
        manipulatedText="Challenge Mode: " + str(challengeMode) + (" " * spaces) + "Shopless: " + str(shopless) + (" " * spaces) + "No restrictions: " + str(noRestrictions) + (" " * spaces) + "Manual Money: " + str(noAutoSlots) + (" " * spaces) + "Instant Imitater: " + str(imitater) + (" " * spaces) + "Random Plants: " + str(randomisePlants) + (" " * spaces) + "Seeded: " + str(seeded)+ (" " * spaces) + "Upgrade Rewards: " + str(upgradeRewards)+ (" " * spaces) + "Random Weights: " + str(randomWeights)+ (" " * spaces) + "Random Wave Points: " + str(randomWavePoints)+ (" " * spaces) + "Starting Wave: " + startingWave+ (" " * spaces) + "Random Cost: " + str(randomCost)+ (" " * spaces) + "Random Cooldowns: " + str(randomCooldowns)#Concatenation
    else:
        manipulatedText="Challenge Mode (locked): " + str(challengeMode) + (" " * spaces) + "Shopless: " + str(shopless) + (" " * spaces) + "No restrictions: " + str(noRestrictions) + (" " * spaces) + "Manual Money: " + str(noAutoSlots) + (" " * spaces) + "Instant Imitater: " + str(imitater) + (" " * spaces) + "Random Plants: " + str(randomisePlants) + (" " * spaces) + "Seeded: " + str(seeded)+ (" " * spaces) + "Upgrade Rewards: " + str(upgradeRewards)+ (" " * spaces) + "Random Weights: " + str(randomWeights)+ (" " * spaces) + "Random Wave Points: " + str(randomWavePoints)+ (" " * spaces) + "Starting Wave: " + startingWave+ (" " * spaces) + "Random Cost: " + str(randomCost)+ (" " * spaces) + "Random Cooldowns: " + str(randomCooldowns)#Concatenation
    outputText.insert(END, manipulatedText) #this inserts the manipulatedText variable into the text box

def getLevel():
    global jumpLevel, saved, seeded
    jumpLevel=jumpEntry.get()
    if jumpLevel!="":
        jumpLevel=convertToNumber(jumpLevel)
        if jumpLevel!="":
            savePoint=jumpLevel
            saved=True
            seeded=False

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

if hasSave:
    continueButton=Button(window, text="CONTINUE LAST RUN", width=15, command=continueButtonClick)
    continueButton.grid(row=0, column=4, sticky=W)

spaces=150

#create a button widget (dear god this is unwieldy)
challengeButton=Button(window, text="CHALLENGE", width=15, command=challengeButtonClick)
challengeButton.grid(row=1, column=0, sticky=W)

shoplessButton=Button(window, text="SHOPLESS", width=15, command=shoplessButtonClick)
shoplessButton.grid(row=1, column=1, sticky=W)

noRestrictionsButton=Button(window, text="NO RESTRICTIONS", width=15, command=noRestrictionsButtonClick)
noRestrictionsButton.grid(row=1, column=2, sticky=W)

manualMoneyButton=Button(window, text="MANUAL MONEY", width=15, command=autoSlotsButtonClick)
manualMoneyButton.grid(row=1, column=3, sticky=W)

imitaterButton=Button(window, text="INSTANT IMITATER", width=15, command=imitaterButtonClick)
imitaterButton.grid(row=1, column=4, sticky=W)

randPlantsButton=Button(window, text="RANDOM PLANTS", width=15, command=randPlantsButtonClick)
randPlantsButton.grid(row=1, column=5, sticky=W)

seededButton=Button(window, text="SEEDED", width=15, command=seededButtonClick)
seededButton.grid(row=2, column=0, sticky=W)

upgradeButton=Button(window, text="UPGRADE REWARDS", width=15, command=upgradeButtonClick)
upgradeButton.grid(row=2, column=1, sticky=W)

randWeightsButton=Button(window, text="RANDOM WEIGHTS", width=15, command=randomWeightsButtonClick)
randWeightsButton.grid(row=2, column=2, sticky=W)

randWavePointsButton=Button(window, text="RAND WAVE POINTS", width=15, command=randomWavePointsButtonClick)
randWavePointsButton.grid(row=2, column=3, sticky=W)

waveStartButton=Button(window, text="STARTING WAVE", width=15, command=startingWaveButtonClick)
waveStartButton.grid(row=2, column=4, sticky=W)

costButton=Button(window, text="RANDOM COST", width=15, command=costButtonClick)
costButton.grid(row=2, column=5, sticky=W)

cooldownButton=Button(window, text="RAND COOLDOWNS", width=15, command=cooldownButtonClick)
cooldownButton.grid(row=2, column=6, sticky=W)

closeButton=Button(window, text="SUBMIT SETTINGS", width=15, command=closeButtonClick)
closeButton.grid(row=1, column=6, sticky=W)

informationButton=Button(window, text="INFORMATION", width=15, command=informationButtonClick)
informationButton.grid(row=1, column=7, sticky=W)

#creates an entry widget, assigning it to a variable
entry=Entry(window, width=20, bg="light green")
entry.grid(row=0, column=1, sticky=W) #positioning this widget on the screen

#create a text box widget
outputText=Text(window, width=120, height=15, wrap=WORD, background="yellow")
outputText.grid(row=3, column=0, columnspan=10, sticky=W)
outputText.insert(END, "Challenge Mode: " + str(challengeMode) + (" " * spaces) + "Shopless: " + str(shopless) + (" " * spaces) + "No restrictions: " + str(noRestrictions) + (" " * spaces) + "Manual Money: "  + str(noAutoSlots) + (" " * spaces) + "Instant Imitater: " + str(imitater)+ (" " * spaces) + "Random Plants: " + str(randomisePlants) + (" " * spaces) + "Seeded: " + str(seeded)+ (" " * spaces) + "Upgrade Rewards: " + str(upgradeRewards)+ (" " * spaces) + "Random Weights: " + str(randomWeights)+ (" " * spaces) + "Random Wave Points: " + str(randomWavePoints)+ (" " * spaces) + "Starting Wave: " + startingWave+ (" " * spaces) + "Random Cost: " + str(randomCost)+ (" " * spaces) + "Random Cooldowns: " + str(randomCooldowns))

window.mainloop() #Run the event loop
print(seed)
print("Challenge Mode:", str(challengeMode))
print("Shopless:", str(shopless))
print("No Restrictions:", str(noRestrictions))
print("Manual Money:", str(noAutoSlots))
print("Instant Imitater:", str(imitater))
print("Random Plants:", str(randomisePlants))
print("Seeded:", str(seeded))
print("Upgrade Rewards:", str(upgradeRewards))
print("Random Weights:", str(randomWeights))
print("Random Wave Points:", str(randomWavePoints))
print("Starting Wave:", startingWave)
print("Random Cost:", str(randomCost))
print("Random Cooldowns:", str(randomCooldowns))

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
        has_seapeater         = (24 in plant_set or 19 in plant_set) and has_pool_shooter #threepeater or starfruit + sea shroom or kelp
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


def randomiseWeights():
    for i in range(0, 24):
        if i!=1 and i!=9:
            if i>2:
                weight=random.randint(1, 60)
            elif i==23:
                weight=random.randint(1, 50)
            else:
                weight=random.randint(1, 45)
            if weight>50:
                weight=weight*1000
            elif weight<5:
                weight=weight*10
            else:
                weight=weight*100
            WriteMemory("int", weight, 0x69DA94 + 0x1C*i)
    WriteMemory("int", 0, 0x69DA94 + 0x1C*1)
    WriteMemory("int", 0, 0x69DA94 + 0x1C*9)

wavePointArray=[1, 1, 2, 2, 4, 2, 4, 7, 5, 0, 1, 3, 7, 3, 3, 3, 2, 4, 4, 4, 3, 4, 5, 10, 0]

def randomiseWavePoints():
    global randomWavePoints, wavePointArray
    for i in range(2, 24):
        if i!=9:
            addWavePoint=0
            randomCheck=0
            while addWavePoint==0 and not randomCheck:
                if randomWavePoints=="EXTREME":
                    if i==5:
                        wavePoint=(random.randint(10,83))//10
                    elif i==2:
                        wavePoint=2+random.randint(0,1)
                    else:
                        wavePoint=(random.randint(20,82))//10
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
                    addWavePoint=random.randint(lowerBound, upperBound)
                    wavePoint=wavePoint+addWavePoint
                    if wavePoint<2 and i!=5:
                        wavePoint=2
                randomCheck=random.randint(0,2)
                if i==2:
                    randomCheck=1
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
        for i in range(0, 24):
            WriteMemory("int", 1, 0x69DA90 + 0x1C*i)
    else:
        for i in range(3, 24):
            if i<7 and i!=5:
                WriteMemory("int", random.randint(1,10), 0x69DA90 + 0x1C*i)
            elif i!=5:
                WriteMemory("int", random.randint(4,10), 0x69DA90 + 0x1C*i)
plants=[[100, 750], [50, 750], [150, 5000], [50, 3000], [25, 3000], [175, 750], [150, 750], [200, 750], [0, 750], [25, 750], [75, 750], [75, 750], [75, 3000], [25, 750], [75, 5000], [125, 5000], [25, 750], [50, 3000], [325, 750], [25, 3000], [125, 5000], [100, 750], [175, 750], [125, 5000], [0, 3000], [25, 3000], [125, 750], [100, 750], [125, 750], [125, 750], [125, 3000], [100, 750], [100, 750], [25, 750], [100, 750], [75, 750], [50, 750], [100, 750], [50, 3000], [300, 750], [250, 5000], [150, 5000], [150, 5000], [225, 5000], [200, 5000], [50, 5000], [125, 5000], [500, 5000]]
for i in range(0, 48):
    WriteMemory("int", plants[i][0], 0x69F2C0 + 0x24*i)
    WriteMemory("int", plants[i][1], 0x69F2C4 + 0x24*i)
    
def randomiseCost():
    for i in range(0, 48):
        if i!=1:
            divider=random.uniform(1,2)
            power=random.choice([-1, 1])
            newCost=int(plants[i][0]*(divider**power))
            WriteMemory("int", newCost , 0x69F2C0 + 0x24*i)

def randomiseCooldown():
    for i in range(0, 48):
        if i!=1 and i!=8 and i!=33:
            divider=random.uniform(1,2)
            power=random.choice([-1, 1])
            newCooldown=int(plants[i][1]*(divider**power))
            WriteMemory("int", newCooldown , 0x69F2C4 + 0x24*i)
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

WriteMemory("unsigned char", 0, 0x530028)
WriteMemory("unsigned char", 1, 0x43c1d1)

# scaling starting cooldowns when random cooldowns on:
if randomCooldowns:
    WriteMemory("unsigned char", [0x66, 0x90], 0x489C00)        # 2 byte nop - to make upgrade plants follow common path for cooldown
    WriteMemory("unsigned char", [
        0x3D, 0xE8,0x03,0x00,0x00,  #cmp eax,#1000 // 10 sec  for no cooldown     
        0x7E,0x33,                  #jle 489C43
        0x2D,0xE8,0x03,0x00,0x00,   # sub eax, #1000
        0xB9,0x09,0x00,0x00,0x00,   # mov ecx,9
        0xF7,0xE1,                  #mul ecx
        0x31,0xD2,                  #xor edx,edx
        0xB9,0x0A,0x00,0x00,0x00,   # mov ecx,#10
        0xF7,0xF1,                  #div ecx
        0x5D,                       #pop ebp
        0x89,0x46,0x28,             # mov[esi+28],eax
        0xC6,0x46,0x49,0x01,        # mov byte[esi+49],1
        0xC6,0x46,0x48,0x00,        # mov byte[esi+48],0
        0x5B,                       #pop ebx
        0xC3                        #ret
    ],                      
        0x489C09)
    
# actiavte code for changing plant names to their cooldown when random cooldowns are on
if randomCooldowns:
    WriteMemory("unsigned char", [
        0xE9,0x49,0x9F,0x1E,0x00,   # jmp 651C00
        0x0F,0x1F,0x00              # 3 byte nop
    ],
        0x467CB2)
    WriteMemory("unsigned char", [
        0xE9,0xC4,0x9F,0x1E,0x00,       # jmp 651C24
        0x66,0x0F,0x1F,0x44,0x00,0x00,  # 6 byte nop
    ],
        0x467C5B)

#code for changing plant names to their cooldown
WriteMemory("unsigned char", [ 
        0x57,                                   # push edi
        0x8B,0xBC,0x24,0xA0,0x00,0x00,0x00,     # mov edi,[esp+000000A0]
        0x83,0xFF,0x30,                         # cmp edi,30
        0x74,0x09,                              # je 651C16
        0x0F,0x1F,0x40,0x00,                    # nop dword ptr [eax+00]
        0xE8,0x30,0x00,0x00,0x00,               # call 651C46 // call make_string
        0x5F,                                   # pop edi
        0xC6,0x84,0x24,0x8C,0x00,0x00,0x00,0x03, # mov byte ptr [esp+0000008C],03
        0xE9,0x96,0x60,0xE1,0xFF,               # jmp 467CBA // return to original code
        0x83,0xFD,0x30,                         # cmp ebp,30
        0x74,0x0D,                              # je 651C36
        0x0F,0x1F,0x40,0x00,                    # nop dword ptr [eax+00]
        0x57,                                   # push edi
        0x8B,0xFD,                              # mov edi,ebp
        0xE8,0x11,0x00,0x00,0x00,               # call 651C46 // call make_string
        0x5F,                                   # pop edi
        0x83,0xFD,0x30,                         # cmp ebp,30
        0xC6,0x84,0x24,0x8C,0x00,0x00,0x00,0x01, # mov byte ptr [esp+0000008C],01
        0xE9,0x20,0x60,0xE1,0xFF,               # jmp 467C66 // return to original code
        # make_string function:
        0x60,                                   # pushad 
        0x83,0xFF,0x30,                         # cmp edi,30
        0x75,0x07,                              # jne 651C53
        0x0F,0x1F,0x40,0x00,                       # nop dword ptr [eax+00]
        0x8B,0x7B,0x34,                         # mov edi,[ebx+34]
        0x8D,0x1C,0xFF,                         # lea ebx,[edi+edi*8]
        0x8B,0x1C,0x9D,0xC4,0xF2,0x69,0x00,     # mov ebx,[ebx*4+69F2C4]
        0x83,0xC0,0x04,                         # add eax,04
        0x8B,0xF8,                              # mov edi,eax
        0xC7,0x00,0x63,0x64,0x3A,0x20,          # mov [eax],'cd: '
        0x83,0xC0,0x04,                         # add eax,04
        0x68,0x0A,0x00,0x00,0x00,               # push 0000000A // base 10
        0x68,0x08,0x00,0x00,0x00,               # push 00000008 // buffer length
        0x50,                                   # push eax
        0x53,                                   # push ebx
        0xE8,0x70,0x49,0xFD,0xFF,               # call 6265EC (itoa_s)
        0x83,0xC4,0x10,                         # add esp,10
        0x57,                                   # push edi
        0xE8,0xBB,0xFA,0xFC,0xFF,               # call 621740 (strlen)
        0x5F,                                   # pop edi
        0x8D,0x34,0x38,                         # lea esi,[eax+edi]
        0x83,0xEE,0x02,                         # sub esi,02
        0x8A,0x0E,                              # mov cl,[esi]
        0xC6,0x06,0x2C,                         # mov byte ptr [esi],2C
        0x46,                                   # inc esi
        0x88,0x0E,                              # mov [esi],cl
        0x46,                                   # inc esi
        0xC7,0x06,0x20,0x73,0x65,0x63,          # mov [esi],' sec'
        0x83,0xC6,0x04,                         # add esi,04
        0xC6,0x06,0x00,                         # mov byte ptr [esi],00
        0x83,0xC0,0x04,                         # add eax,04
        0x89,0x47,0x10,                         # mov [edi+10],eax
        0xC7,0x47,0x14,0x0F,0x00,0x00,0x00,     # mov [edi+14],0000000F
        0x61,                                   # popad 
        0xC3,                                   # ret 
    ],
        0x651C00)

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
WriteMemory("int", plants_array2, 0x651194) #ends at 0x65125c
WriteMemory("int",0,0x65115c)
upgradePlants=[0x1C4, 0x1C2, 0x1C8, 0x1D4, 0x1CC, 0x1D8, 0x1E0, 0x1D0, 0x1DC, "nothing", "nothing2"] #twin, gatling, gloom, gold, cattail, spike, imitater, winter, cob
zombies=["Basic", "Flag (ignore)", "Cone", "Vaulter", "Bucket", "Newspaper", "Screen-Door", "Footballer", "Dancer", "Backup (ignore)", "Ducky-Tube (ignore)", "Snorkel", "Zomboni", "Bobsled", "Dolphin", "Jack", "Balloon", "Digger", "Pogo", "Yeti (ignore)", "Bungee", "Ladder", "Catapult", "Gargantuar"]
if startingWave=="Instant":
    randomiseStartingWave(startingWave)
if saved and jumpLevel!="":
    for a in range(len(levels)):
        if levels[a]==jumpLevel:
            savePoint=a+1
for i in range(50):
    if saved:
        if savePoint-1==i:
            saved=False
    if not saved and i!=0:
        linesToWrite=[seed, (i+1), str(ReadMemory("int", 0x6A9EC0,0x82C,0x214)), str(ReadMemory("int",0x6A9EC0,0x82C, 0x28)), (challengeMode), (shopless), (noRestrictions), (noAutoSlots), (imitater), (randomisePlants), (seeded), (upgradeRewards), (randomWeights), (randomWavePoints), startingWave, randomCost, randomCooldowns]
        saveFile=open('saveFile.txt', 'w')
        for k in range(len(linesToWrite)):
            linesToWrite[k]=str(linesToWrite[k])
            linesToWrite[k]=linesToWrite[k]+"\n"
        saveFile.writelines(linesToWrite)
        saveFile.close()
        if i!=0 and (randomWavePoints!=False or randomWeights):
            print(" "*100)
            print("Level:", convertToLevel(levels[i-1]))
            zombies_type_offset = ReadMemory("unsigned int", 0x6A9EC0, 0x768) + 0x54D4
            zombies_type = ReadMemory("bool",zombies_type_offset,array=33)
            for j in range(0, 24):
                if(zombies_type[j]):
                    print(zombies[j], str(ReadMemory("int", 0x69DA88 + 0x1C*j)), ReadMemory("int", 0x69DA94 + 0x1C*j),ReadMemory("int", 0x69DA90 + 0x1C*j))
    print(str(i+1))
    WriteMemory("int",plants_unlocked,0x651090)
    if seeded and not saved:
        WriteMemory("int", [0 for j in range(1024)], rng_addr+0x10)
        WriteMemory("int", rng_addr+0x1010, rng_addr)
    newlevel=levels[i]
    if(i == 0) and not saved:
        try:
            while(ReadMemory("int",0x6A9EC0,0x82C, 0x24) != 1): # current level
                Sleep(0.1)
        except:
            print("oops")
    if not noAutoSlots or shopless:
        WriteMemory("int",0,0x6A9EC0,0x82C, 0x28)
    if upgradeRewards:
        if i!=0:
            if(level_plants[lastlevel] == -1):
                if randomisePlants:
                    if len(upgradePlants)!=0:
                        newUpgrade=random.choice(upgradePlants)
                        upgradePlants.remove(newUpgrade)
                        if newUpgrade!="nothing" and newUpgrade!="nothing2":
                            WriteMemory("bool",True,0x6A9EC0,0x82C,newUpgrade)
                else:
                    if lastlevel!=49 and lastlevel!=50:
                        WriteMemory("bool",True,0x6A9EC0,0x82C,upgradePlants[lastlevel//5])
        lastlevel=newlevel
    if imitater and i != 0:
        WriteMemory("bool",True,0x6A9EC0,0x82C,0x1E0)
        WriteMemory("int", 0, 0x453aea)
    if not saved:
        WriteMemory("int",newlevel,0x6A9EC0,0x82C, 0x24)
    if randomWeights:
        randomiseWeights()
    if randomWavePoints!=False:
        randomiseWavePoints()
    if i!=0:
        randomiseCost()
        if randomCooldowns:
            randomiseCooldown()
    if startingWave=="Random":
        randomiseStartingWave(startingWave)
    if not saved:
        WriteMemory("int",newlevel,0x651190)
    if not shopless:
        WriteMemory("bool",True,0x6A9EC0,0x82C,0x21C)
        WriteMemory("bool",True,0x6A9EC0,0x82C,0x218)
    if(i != 0) and not saved: 
        Sleep(1)
    if(level_plants[newlevel] != -1):
        plants_unlocked += 1
    if(i >= 24 and plants_unlocked > 7 and not (shopless or noAutoSlots)): # slots
        WriteMemory("int",2,0x6A9EC0,0x82C,0x214)
    elif(i >= 14 and plants_unlocked > 6 and not (shopless or noAutoSlots)):
        WriteMemory("int",1,0x6A9EC0,0x82C,0x214)
    if(i == 0) and not saved:
        while(game_ui() != 3):
            Sleep(0.1)
    if saved:
        Sleep(1)
    else:
        Sleep(500)
    if not noAutoSlots or shopless:
        WriteMemory("int",0,0x6A9EC0,0x82C, 0x28)
    if saved:
        Sleep(1)
    else:
        Sleep(500)
    if not noAutoSlots or shopless:
        WriteMemory("int",0,0x6A9EC0,0x82C, 0x28)
    while(game_ui() != 3 or ReadMemory("bool",0x6A9EC0,0x768, 0x5603)):
        Sleep(0.1)
    WriteMemory("int",i,0x65115c)

WriteMemory("int",0,0x651190)

saveFile=open('saveFile.txt', 'w')
saveFile.write("")
saveFile.close()

while True:
    Sleep(10)
    WriteMemory("bool",True,0x6A9EC0,0x82C,0x21C)
