#modifiers to add: challenge mode (no tough level restrictions), shopless, randomised plants
#automatically add slots versus purchase slots
# NO RESTRICTIONS (not recommended)
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
    
def closeButtonClick():
    getSeed()
    window.destroy()

def buttonClick():
    global noRestrictions, challengeMode, shopless, noAutoSlots
    outputText.delete(0.0, END) #this clears the contents of the text box widget
    if not noRestrictions:
        if not shopless:
            manipulatedText="Challenge Mode: " + str(challengeMode) + "           Shopless: " + str(shopless) + "                  No restrictions (not recommended): " +str(noRestrictions) + "                  Manual Money: " +str(noAutoSlots) #Concatenation
        else:
            manipulatedText="Challenge Mode: " + str(challengeMode) + "           Shopless: " + str(shopless) + "                  No restrictions (not recommended): " +str(noRestrictions) + "                  Manual Money (locked): " +str(noAutoSlots)#Concatenation
    else:
        if not shopless:
            manipulatedText="Challenge Mode (locked): " + str(challengeMode) + "           Shopless: " + str(shopless) + "                  No restrictions (not recommended): " +str(noRestrictions)+ "                  Manual Money: " +str(noAutoSlots)#Concatenation
        else:
            manipulatedText="Challenge Mode (locked): " + str(challengeMode) + "           Shopless: " + str(shopless) + "                  No restrictions (not recommended): " +str(noRestrictions)+ "                  Manual Money (locked): " +str(noAutoSlots)#Concatenation
    outputText.insert(END, manipulatedText) #this inserts the manipulatedText variable into the text box
def getSeed():
    global seed
    seed=entry.get()
    if seed=="":
        seed=str(random.randint(1,999999999999))

#Create a label widget and assign it to a variable
label=Label(window, text="Enter seed: ")
label.grid(row=0, column=0, sticky=W) #Poistioning this widget (now in a variable) on the screen

#create a button widget
challengeButton=Button(window, text="CHALLENGE", width=15, command=challengeButtonClick)
challengeButton.grid(row=1, column=0, sticky=W)
shoplessButton=Button(window, text="SHOPLESS", width=15, command=shoplessButtonClick)
shoplessButton.grid(row=1, column=1, sticky=W)
noRestrictionsButton=Button(window, text="NO RESTRICTIONS", width=15, command=noRestrictionsButtonClick)
noRestrictionsButton.grid(row=1, column=2, sticky=W)
noRestrictionsButton=Button(window, text="MANUAL MONEY", width=15, command=autoSlotsButtonClick)
noRestrictionsButton.grid(row=1, column=3, sticky=W)
closeButton=Button(window, text="SUBMIT SETTINGS", width=15, command=closeButtonClick)
closeButton.grid(row=1, column=4, sticky=W)

#creates an entry widget, assigning it to a variable
entry=Entry(window, width=20, bg="light green")
entry.grid(row=0, column=1, sticky=W) #positioning this widget on the screen

#create a text box widget
outputText=Text(window, width=30, height=10, wrap=WORD, background="yellow")
outputText.grid(row=3, column=0, columnspan=2, sticky=W)
outputText.insert(END, "Challenge Mode: " + str(challengeMode) + "           Shopless: " + str(shopless) + "                  No restrictions (not recommended): " +str(noRestrictions) + "                  Manual Money: " +str(noAutoSlots)) #this inserts the manipulatedText variable into the text box

window.mainloop() #Run the event loop
print(seed)
random.seed(seed)

def randomiseLevels():
    global noRestrictions, challengeMode
    firstLevels=[]
    levels=[0]
    fogCheck=0
    toughLevelCheck=0
    balloonCheck=0
    if noRestrictions:
        for i in range(1, 50):
            levels.append(i)
    toughCheck=[False, False, False, False, False, False, False, False, False, False, False, False] #fog 3, fog 5, pool 3, pool 5, roof 3 no pot, roof 5 pot, night 3, roof 3 pot, balloon fog 3, balloon fog 5, fog no lily, fog lily
    for i in range(0,50):
        levels, firstLevels = addLevel(levels, firstLevels)
        if not noRestrictions:
            if i>=10 and 40 not in firstLevels and 40 not in levels: #if 10 or more plants total, 5-1 is allowed (as long as you haven't already unlocked it)
                levels=addToLevelsList(levels, [40])
            if i==0: #after 1-1, can play any day stage or any x-5 / x-10
                levels=addToLevelsList(levels, [1, 2, 3, 4, 5, 6, 7, 8, 9, 14, 19, 24, 29, 34, 39, 44, 49])
            elif firstLevels[i]==9: #after 1-10, can play any night stage
                if not challengeMode:
                    levels=addToLevelsList(levels, [10, 12, 15, 17])
                else:
                    levels=addToLevelsList(levels, [10, 11, 12, 13, 15, 16, 17, 18])
            elif firstLevels[i]==19: #after 2-10, can play some pool stages
                if not challengeMode:
                    levels=addToLevelsList(levels, [20, 22, 27])
                else:
                    levels=addToLevelsList(levels, [20, 21, 22, 23, 25, 26, 27, 28])
            elif firstLevels[i]==39 and 40 not in firstLevels and 40 not in levels: #after 4-10, if you have not played 5-1, can play 5-1
                if not challengeMode:
                    levels=addToLevelsList(levels, [40])
            elif challengeMode and firstLevels[i]==40 and 41 not in levels and 41 not in firstLevels:
                levels=addToLevelsList(levels, [41, 42, 43, 45, 46, 47, 48])
            if firstLevels[i]==29 or firstLevels[i]==19: 
                fogCheck += 1
            if firstLevels[i]==9:
                fogCheck += 3
            if firstLevels[i] in [1, 17, 24]:
                balloonCheck+=1
            elif firstLevels[i] in [31, 32]:
                balloonCheck+=2
            if balloonCheck>=2:
                balloonCheck = -9999
            if fogCheck>=4: # last three lines: if puff shroom and either sea shroom/lilypad are obtained, unlock 4-1, 4-3, 4-6, and 4-8
                fogCheck=-9999
            if fogCheck<0:
                if not toughCheck[11]:
                    toughCheck[11]=True
                    levels=addToLevelsList(levels, [30, 32, 35, 37])
                if challengeMode:
                    if not toughCheck[10] and 19 in firstLevels:
                        toughCheck[10]=True
                        levels=addToLevelsList(levels, [31, 36])
            if firstLevels[i] in [2, 6, 7, 17, 20, 24, 35, 37, 42, 47]: #cherry bomb, chomper, repeater, doom, squash, jalapeno, starfruit, magnet, coffee bean, melon pult
                toughLevelCheck += 1
            if not challengeMode:
                if toughLevelCheck >= 3:
                    if fogCheck<0:
                        if 19 in firstLevels:
                            if toughCheck[0]==False:
                                toughCheck[0]=True
                                levels=addToLevelsList(levels, [31])
                            if balloonCheck<0 and toughCheck[8]==False:
                                toughCheck[8]=True
                                levels=addToLevelsList(levels, [33])
                    if fogCheck<0 and toughLevelCheck>=5:
                        if 19 in firstLevels:
                            if toughCheck[1]==False:
                                toughCheck[1]=True
                                levels=addToLevelsList(levels, [36])
                            if balloonCheck<0 and toughCheck[9]==False:
                                toughCheck[9]=True
                                levels=addToLevelsList(levels, [38])
                    if 19 in firstLevels:
                        if toughCheck[2]==False:
                            toughCheck[2]=True
                            levels=addToLevelsList(levels, [21, 25])
                        if toughCheck[3]==False and toughLevelCheck>=5:
                            toughCheck[3]=True
                            levels=addToLevelsList(levels, [23, 26, 28])
                    if 39 in firstLevels or 40 in firstLevels:
                        if toughCheck[4]==False:
                            toughCheck[4]=True
                            levels=addToLevelsList(levels, [42, 45])
                        elif toughCheck[7]==False and 40 in firstLevels:
                            toughCheck[7]=True
                            levels=addToLevelsList(levels, [41, 47])
                        if toughCheck[5]==False and toughLevelCheck>=5 and 40 in firstLevels:
                            toughCheck[5]=True
                            levels=addToLevelsList(levels, [43, 46, 48])
                    if toughCheck[6]==False and 9 in firstLevels:
                        toughCheck[6]=True
                        levels=addToLevelsList(levels, [11, 13, 16, 18])
            else:
                if fogCheck<0:
                        if balloonCheck<0 and toughCheck[0]==False and 19 in firstLevels:
                            toughCheck[0]=True
                            levels=addToLevelsList(levels, [33, 38])
    for i in range(0, len(firstLevels)):
        firstLevels[i] +=1
    return firstLevels

def addLevel(levels, firstLevels):
    global noRestrictions
    newLevel=0
    count=0
    countTarget=(len(firstLevels)//5)+1
    if not noRestrictions:
        if 9 in levels or 19 in levels or 29 in levels or 39 in levels or 40 in levels: #add in or 19 again
            while count<2 and newLevel not in [9, 19, 29, 39, 40]:
                count=count+1
                newLevel = random.choice(levels)
        else:
            newLevel = random.choice(levels)
    else:
        if len(firstLevels)==0:
            newLevel=0
        else:
            newLevel = random.choice(levels)
    firstLevels.append(newLevel)
    levels.remove(newLevel)
    return levels, firstLevels

def addToLevelsList(levels, numberList):
    for i in range(0, len(numberList)):
        levels.append(numberList[i])
    return levels
def showAverage(): #balancing purposes
    
    dayAverage=0
    nightAverage=0
    poolAverage=0
    fogAverage=0
    roofAverage=0
    for i in range(0, 50000):
        dayCount=0
        nightCount=0
        poolCount=0
        fogCount=0
        roofCount=0
        levels = randomiseLevels()
        for j in range(40, 50):
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
    print(dayAverage/50000, nightAverage/50000, poolAverage/50000, fogAverage/50000, roofAverage/50000)

#showAverage()
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



#shovel

WriteMemory("unsigned char", 1, 0x530028)
WriteMemory("unsigned char", 1, 0x43c1d1)



#I haven't been bothered to label these yet

WriteMemory("unsigned char", [
0x8b, 0x04, 0x25, 0x90, 0x10, 0x65, 0x00, #movl 0x651090, %eax
0x83, 0xf8, 0x31,                         #cmpl $0x31,    %eax
0x7e, 0x05,                               #jle  0x453ae9
0xb8, 0x31, 0x00, 0x00, 0x00,             #movl $0x31,    %eax
0xc3,                                     #retl
0x90,                                     #nop
0x90                                      #nop
], 0x453ad8)

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
for i in [40,41,42,43,44,45,46,47]:
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

        
