from pvz import *
from pvz.extra import *
import random

seed=input("Input the seed (case sensitive). Leave empty for a random seed. ")
if seed=="":
    seed=str(random.randint(1,999999999999))
print(seed)
random.seed(seed)
def randomiseLevels():
    firstLevels=[]
    levels=[0]
    fogCheck=0
    toughLevelCheck=0
    balloonCheck=0
    toughCheck=[False, False, False, False, False, False, False, False, False, False] #fog 3, fog 5, pool 3, pool 5, roof 3 no pot, roof 5 pot, night 3, roof 3 pot, balloon fog 3, balloon fog 5
    for i in range(0,50):
        levels, firstLevels = addLevel(levels, firstLevels)
        if i>=10 and 40 not in firstLevels and 40 not in levels: #if 10 or more plants total, 5-1 is allowed (as long as you haven't already unlocked it)
            levels=addToLevelsList(levels, [40])
        if i==0: #after 1-1, can play any day stage or any x-5 / x-10
            levels=addToLevelsList(levels, [1, 2, 3, 4, 5, 6, 7, 8, 9, 14, 19, 24, 29, 34, 39, 44, 49])
        elif firstLevels[i]==9: #after 1-10, can play any night stage
            levels=addToLevelsList(levels, [10, 12, 15, 17])
        elif firstLevels[i]==19: #after 2-10, can play some pool stages
            levels=addToLevelsList(levels, [20, 22, 27])
        elif firstLevels[i]==39 and 40 not in firstLevels and 40 not in levels: #after 4-10, if you have not played 5-1, can play 5-1
            levels=addToLevelsList(levels, [40])
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
            levels=addToLevelsList(levels, [30, 32, 35, 37])
            fogCheck = -9999
        if firstLevels[i] in [2, 6, 7, 17, 20, 24, 35, 37, 39, 42, 47]: #cherry bomb, chomper, repeater, doom, squash, jalapeno, starfruit, magnet, coffee bean, melon pult
            toughLevelCheck += 1
        if toughLevelCheck >= 3:
            if fogCheck<0:
                if toughCheck[0]==False:
                    toughCheck[0]=True
                    levels=addToLevelsList(levels, [31])
                if balloonCheck<0 and toughCheck[8]==False:
                    toughCheck[8]=True
                    levels=addToLevelsList(levels, [33])
            if fogCheck<0 and toughLevelCheck>=5:
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
    for i in range(0, len(firstLevels)):
        firstLevels[i] +=1
    return firstLevels

def addLevel(levels, firstLevels):
    newLevel=0
    count=0
    countTarget=(len(firstLevels)//5)+1
    if 9 in levels or 19 in levels or 29 in levels or 39 in levels or 40 in levels:
        while count<2 and newLevel not in [9, 19, 29, 39, 40]:
            count=count+1
            newLevel = random.choice(levels)
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
print(levels)

#WriteMemory("unsigned char", [
#0x8b, 0x45, 0x48,                         #movl  0x8(%ebp),    %eax
#0x6a, 0x00,                               #pushl $0x0
#0x6a, 0x01,                               #pushl $0x1
#0x6a, 0x00,                               #pushl $0x0
#0x6a, 0xff,                               #pushl $-0x1
#0xff, 0x34, 0xb5, 0x98, 0x10, 0x65, 0x00, #pushl $0x400408(,%esi,4)
#0xdb, 0x44, 0x24, 0x30,                   #fildl 0x30(%esp)
#0xdb, 0x44, 0x24, 0x34,                   #fildl 0x34(%esp)
#0x50,                                     #pushl %eax
#0xd9, 0x1c, 0x24,                         #fstps (%esp)
#0x50,                                     #pushl %eax
#0xd9, 0x1c, 0x24,                         #fstps (%esp)
#0xb9, 0x37, 0x00, 0x00, 0x00,             #movl  $0x37,        %ecx
#0x50                                      #pushl %eax
#], 0x484893)

WriteMemory("unsigned char", [
0x8b, 0x43, 0x20,                               #movl    0x20(%ebx),        %eax
0x83, 0x7b, 0x24, 0x00,                         #cmpl    $0x0,        0x24(%ebx)
0x0f, 0x43, 0x04, 0x85, 0x98, 0x10, 0x65, 0x00, #cmovncl 0x400408(,%eax,4), %eax #I originally thought a cmp and cmov were required for this but was too lazy to remove them so the cmov activates every time
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
0x8b, 0x93, 0x14, 0x0d, 0x00, 0x00,       #movl  0xd14(%ebx),       %edx
0x8b, 0x3c, 0x85, 0x98, 0x10, 0x65, 0x00, #movl  0x400408(,%eax,4), %edi
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

WriteMemory("unsigned char", [
0x8b, 0x04, 0x25, 0x90, 0x10, 0x65, 0x00, #movl 0x400400, %eax
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
0x8b, 0x0c, 0x8d, 0x98, 0x10, 0x65, 0x00, #movl 0x400408(,%ecx,4), %ecx
0x83, 0xf9, 0x30,                         #cmpl $0x30,             %ecx
0xeb, 0x85                                #jmp  0x484402
], 0x484471)

WriteMemory("int",0x07e27c-0x7,0x40b8d0) #call 0x489b49

WriteMemory("unsigned char", [
0x8b, 0x3c, 0xbd, 0x98, 0x10, 0x65, 0x00, #movl 0x400408(,%edi,4), %edi
], 0x489b49)

WriteMemory("unsigned char", [
0xeb, 0x0b,                   #jmp  0x40bdf8
0x3d, 0x01, 0x00, 0x00, 0x00, #cmpl $0x1,      %eax #used to be 6
0x7f, 0xe8,                   #jg   0x40bddc
0x32, 0xc0,                   #xorb %al,        %al
0x5e,                         #popl %esi
0xc3,                         #retl
0xa1, 0x90, 0x10, 0x65, 0x00, #movl 0x400400, %eax
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

#for i in range(len(plants_array)):
#	WriteMemory("int", plants_array[i], 0x400404 + i*4)

plants_unlocked = 1
WriteMemory("int", plants_array, 0x651094)

for i in range(50):
    if i!=1 or True:
        WriteMemory("int",plants_unlocked,0x651090)
        newlevel=levels[i]
        if(i == 0):
            while(ReadMemory("int",0x6A9EC0,0x82C, 0x24) != 1): # current level
                Sleep(0.1)
        WriteMemory("int",0,0x6A9EC0,0x82C, 0x28)
        WriteMemory("int",newlevel,0x6A9EC0,0x82C, 0x24)
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
        if(i >= 24 and plants_unlocked > 7): # slots
            WriteMemory("int",2,0x6A9EC0,0x82C,0x214)
        elif(i >= 14 and plants_unlocked > 6):
            WriteMemory("int",1,0x6A9EC0,0x82C,0x214)
        else:
            WriteMemory("int",0,0x6A9EC0,0x82C,0x214)
        if(i == 0):
            while(game_ui() != 3):
                Sleep(0.1)
        Sleep(1000)
        while(game_ui() != 3 or ReadMemory("bool",0x6A9EC0,0x768, 0x5603)):
            Sleep(0.1)

        
