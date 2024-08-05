#modifiers to add: challenge mode (no tough level restrictions), shopless, randomised plants
#automatically add slots versus purchase slots
#NO RESTRICTIONS (not recommended)
#WriteMemory("int",0,0x6A9EC0,0x82C, 0x28) sets money to 0

from tkinter import *
from pvz import *
from pvz.extra import *
import random

window=Tk() #Creates a window object from the Tk class
window.title("Randomiser settings")
challengeMode=False
shopless=False
noRestrictions=False
noAutoSlots=False
imitater=False
seed=str(random.randint(1,999999999999))

def challengeButtonClick():
    global noRestrictions, challengeMode
    if not noRestrictions:
        challengeMode=not challengeMode
    buttonClick()
def shoplessButtonClick():
    global shopless, noAutoSlots
    shopless=not shopless
    if shopless:
        noAutoSlots=True
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
    
def closeButtonClick():
    getSeed()
    window.destroy()

def informationButtonClick():
    outputText.delete(0.0, END)
    manipulatedText="Challenge Mode gets rid of the tough level restriction. With this disabled, you will not be able to play certain levels (like 5-2) without having 3 good plants. Other levels (like 5-9) will need 5 good plants to play. With this enabled, as soon as you unlock flower pot, you can play both 5-2 and 5-9 (for instance). Shopless mode forces you to play with 6 slots and no automatic pool cleaners / roof cleaners. No restrictions mode means that there is no logic as to what levels can be played next - the majority of no restrictions runs are impossible. With manual money enabled, you do not get automatic slot upgrades, but your money does not reset to 0 after every level, and so you can purchase the slots yourself - this also means you can buy rakes and upgrade plants!"
    outputText.insert(END, manipulatedText)

def buttonClick():
    global noRestrictions, challengeMode, shopless, noAutoSlots, imitater, spaces
    outputText.delete(0.0, END) #this clears the contents of the text box widget
    if not noRestrictions:
        if not shopless:
            manipulatedText="Challenge Mode: " + str(challengeMode) + (" " * spaces) + "Shopless: " + str(shopless) + (" " * spaces) + "No restrictions: " + str(noRestrictions) + (" " * spaces) + "Manual Money: " + str(noAutoSlots) + (" " * spaces) + "Instant Imitater: " + str(imitater)#Concatenation
        else:
            manipulatedText="Challenge Mode: " + str(challengeMode) + (" " * spaces) + "Shopless: " + str(shopless) + (" " * spaces) + "No restrictions: " + str(noRestrictions) + (" " * spaces) + "Manual Money (locked): " + str(noAutoSlots) + (" " * spaces) + "Instant Imitater: " + str(imitater)#Concatenation
    else:
        if not shopless:
            manipulatedText="Challenge Mode (locked): " + str(challengeMode) + (" " * spaces) + "Shopless: " + str(shopless) + (" " * spaces) + "No restrictions: " + str(noRestrictions) + (" " * spaces) + "Manual Money: " + str(noAutoSlots) + (" " * spaces) + "Instant Imitater: " + str(imitater)#Concatenation
        else:
            manipulatedText="Challenge Mode (locked): " + str(challengeMode) + (" " * spaces) + "Shopless: " + str(shopless) + (" " * spaces) + "No restrictions: " + str(noRestrictions) + (" " * spaces) + "Manual Money (locked): " + str(noAutoSlots) + (" " * spaces) + "Instant Imitater: " + str(imitater)#Concatenation
    outputText.insert(END, manipulatedText) #this inserts the manipulatedText variable into the text box
def getSeed():
    global seed
    seed=entry.get()
    if seed=="":
        seed=str(random.randint(1,999999999999))

#Create a label widget and assign it to a variable
label=Label(window, text="Enter seed: ")
label.grid(row=0, column=0, sticky=W) #Poistioning this widget (now in a variable) on the screen

spaces=100

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
closeButton=Button(window, text="SUBMIT SETTINGS", width=15, command=closeButtonClick)
closeButton.grid(row=1, column=5, sticky=W)
informationButton=Button(window, text="INFORMATION", width=15, command=informationButtonClick)
informationButton.grid(row=1, column=6, sticky=W)

#creates an entry widget, assigning it to a variable
entry=Entry(window, width=20, bg="light green")
entry.grid(row=0, column=1, sticky=W) #positioning this widget on the screen

#create a text box widget
outputText=Text(window, width=100, height=10, wrap=WORD, background="yellow")
outputText.grid(row=3, column=0, columnspan=10, sticky=W)
outputText.insert(END, "Challenge Mode: " + str(challengeMode) + (" " * spaces) + "Shopless: " + str(shopless) + (" " * spaces) + "No restrictions: " + str(noRestrictions) + (" " * spaces) + "Manual Money: "  + str(noAutoSlots) + (" " * spaces) + "Instant Imitater: " + str(imitater))

window.mainloop() #Run the event loop
print(seed)
random.seed(seed)

def randomiseLevels():
    global noRestrictions, challengeMode
    firstLevels=[]
    levels=[1]
    toughLevelCheck=0
    balloonCheck=0
    if noRestrictions:
        for i in range(1, 50):
            levels.append(i)
    for i in range(0,50):
        levels, firstLevels = addLevel(levels, firstLevels)
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
    
    dayAverage=0
    nightAverage=0
    poolAverage=0
    fogAverage=0
    roofAverage=0
    averageTarget=10000
    for i in range(0, averageTarget):
        dayCount=0
        nightCount=0
        poolCount=0
        fogCount=0
        roofCount=0
        levels = randomiseLevels()
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
levels = randomiseLevels()
#print(levels)

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

LEVEL_PLANTS = [
0,
1,  2,  3,  -1, 4,  5,  6,  7,  -1,  8,
9,  10, 11, -1, 12, 13, 14, 15, -1, 16,
17, 18, 19, -1, 20, 21, 22, 23, -1, 24,
25, 26, 27, -1, 28, 29, 30, 31, -1, 32,
33, 34, 35, -1, 36, 37, 38, 39, -1, -1
]
plants_array = [-1,0]
for i in levels:
    if LEVEL_PLANTS[i] != -1:
        plants_array.append(LEVEL_PLANTS[i])
for i in [40,41,42,43,44,45,46,47,48]:
    plants_array.append(i)

plants_unlocked = 1
WriteMemory("int", plants_array, 0x651094)

for i in range(50):
    WriteMemory("int",plants_unlocked,0x651090)
    newlevel=levels[i]
    if(i == 0):
        while(ReadMemory("int",0x6A9EC0,0x82C, 0x24) != 1): # current level
            Sleep(0.1)
    if not noAutoSlots or shopless:
        WriteMemory("int",0,0x6A9EC0,0x82C, 0x28)
    if imitater and i != 0:
        WriteMemory("bool",True,0x6A9EC0,0x82C,0x1E0)
        WriteMemory("int", 0, 0x453aea)
    WriteMemory("int",newlevel,0x6A9EC0,0x82C, 0x24)
    if not shopless:
        WriteMemory("bool",True,0x6A9EC0,0x82C,0x21C)
        WriteMemory("bool",True,0x6A9EC0,0x82C,0x218)
    if(i != 0): 
        WriteMemory("int",newlevel-1,0x6A9EC0,0x768, 0x5550)
    if(LEVEL_PLANTS[newlevel] != -1):
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

while True:
    Sleep(10)
    WriteMemory("bool",True,0x6A9EC0,0x82C,0x21C)
