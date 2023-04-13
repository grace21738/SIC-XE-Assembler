'''
*****************************************************************
環境: WINDOWS-11
使用語言: python3
1. 使用終端機執行輸入指令:
    $ python3 project.py
2. 輸入要讀入的檔案名稱。
3. 執行結束後，會印出object code並且寫入"object_code.txt"檔案中。
注意事項:
要讀入的指令請都用'TAB'空白分割
******************************************************************
'''
import re

f = None
print("請輸入指令的檔案名: ")
fileName = input()

#建立字典
OPTAB_dic = {
    'ADD':'18',
    'STL':'14',
    'LDB':'68',
    'JSUB':'48',
    'LDA':'00',
    'COMP':'28',
    'JEQ':'30',
    'J':'3C',
    'CLEAR':'B4',
    'LDT':'74',
    'TD':'E0',
    'RD':'D8',
    'COMPR':'A0',
    'STCH':'54',
    'TIXR':'B8',
    'JLT':'38',
    'STX':'10',
    'STA':'0C',
    'RSUB':'4C',
    'LDCH':'50',
    'WD':'DC',
    'LDT':'74'
}

REGTAB = {
    'A':'0',
    'X':'1',
    'S':'4',
    'T':'5'
}


# 檔案開起來
try:
    f = open(fileName, 'r')
except IOError:
    print('ERROR: can not found ' + fileName)
    if f:
        f.close()
isSTART = True
OPTION = 1
LABEL = 0
ARG = 2
CODE = 3
NEWLINE = 9
need_new_line = False
pc = 0
dis = 0
SYMTAB = []
base_reg = 0
object_code = []
start = 0
length = 0
code_cnt = 0
modification = []
all_op_code = []
pos_cut = []

def index_2d(myList, v):
    for i, sublist in enumerate(myList):
        if v in sublist:
            return i
    return -1

def str_16( opcode_16 ):
    opcode_16 = opcode_16[2:]
    opcode_16 = opcode_16.upper()
    if len(opcode_16)%2 == 1:
        object_code = '0' + opcode_16
    else:
        object_code = opcode_16
    return object_code

def location( opcode_16 ):
    tmp = ''
    for i in range (6-len(opcode_16)):
        tmp += '0'
    tmp += opcode_16
    return tmp

def get_digit(all_op_code,pos):
    digit = 0
    #print("pos: ",all_op_code[pos][0])
    t = int(all_op_code[pos][1],16)
    #print("CCC:",t)
    while t != 0:
        t = t >> 8
        digit += 1
    return digit

#建立table -- PASS 1
for line in f.readlines():
    line = line.strip('\n')
    a = line.split('\t')
    symbol =[]
    #GET LABEL
    #GET START
    if a[OPTION]=='START':
        pc = int(a[ARG],16)
        start = '0x' + a[ARG]
        code_str = 'H\t'+a[LABEL]+'\t'+ location( str_16(start) ) +'\t'
        object_code.append(code_str)
    if a[LABEL]!='':
        symbol.append(a[LABEL])
        symbol.append(str_16(hex(pc)))
        SYMTAB.append(symbol)
   
    if isSTART == True:
        isSTART = False
    #FORMAT 4
    elif a[OPTION][0]=='+':
        pc += 4
    elif a[OPTION]=='BYTE':
        #Char
        if a[ARG][0]=='C':
            chr = a[ARG].split('\'')
            pc += len(chr[1])
        elif a[ARG][0]=='X':
            chr = a[ARG].split('\'')
            pc += 1
            #print("chr: ",len(chr[1]))
    #FORMAT 2
    elif a[OPTION]=='CLEAR' or a[OPTION]=='TIXR'or a[OPTION]=='COMPR':
        pc += 2
    elif a[OPTION]=='RESW':
        pc = pc + int(a[ARG])*3
    elif a[OPTION]=='RESB':
        pc += int(a[ARG])
    #FORMAT 3
    elif a[OPTION]!='BASE'and a[OPTION]!='END':
        pc += 3
object_code[0] += str_16(hex(pc-int(start,16)))
# print("code_str: ",object_code[0])

code_str = 'T\t'
m_str = ''
#PASS 2
f.close()
f = open(fileName, 'r')
for line in f.readlines():
    line = line.strip('\n')
    a = line.split('\t')
    pos = []
    
    if a[OPTION]!='RESW'and a[OPTION]!='RESB' and a[OPTION]!='BASE' and need_new_line == True:
        code_cnt = 0
        need_new_line = False
        pos_cut.append(hex(pc))
    #GET START
    if a[OPTION]=='START':
        pc = int(a[ARG],16)
    
    if isSTART == True:
        isSTART = False
    #FORMAT 4
    elif a[OPTION][0]=='+':
        pos.append(hex(pc))
        pc += 4
        #SYMBOL
        op = bin(int(OPTAB_dic[a[OPTION][1:]],16)>>2)
        binary = int(op,2)
        binary = binary << 6
        if a[ARG][0] =='#':
            dis = int(a[ARG][1:])
            binary += 17
        else:
            index = index_2d(SYMTAB,a[ARG] )
            if index != -1:
                dis = int(SYMTAB[index][1],16)
                binary += 49
            code_str = 'M\t'+location( str_16(hex(pc-3)) ) + ' 05'
            modification.append(code_str)
        binary = binary << 20
        binary += dis
        pos.append(hex(binary))
        all_op_code.append(pos)
        # print( a )
        # print("obj: ",hex(binary)," ,binary: ",bin(binary),'\n')
    elif a[OPTION]=='BYTE':
        pos.append(hex(pc))
        # Char
        if a[ARG][0]=='C':
            chr = a[ARG].split('\'')
            pc += len(chr[1])
            tstr = ''
            for i in range(len(chr[1])):
                tstr += hex(ord(chr[1][i])).strip('0x')
            binary = int(tstr,16)
        elif a[ARG][0]=='X':
            chr = a[ARG].split('\'')
            pc += 1
            binary = int(chr[1],16)
        # print( a )
        # print("obj: ",hex(binary)," ,binary: ",bin(binary),'\n')
        pos.append(hex(binary))
        all_op_code.append(pos)
    #FORMAT 2
    elif a[OPTION]=='CLEAR' or a[OPTION]=='TIXR'or a[OPTION]=='COMPR':
        pos.append(hex(pc))
        pc += 2
        op = OPTAB_dic[a[OPTION]]
        tstr = op
        if a[OPTION]=='COMPR':
            chr = a[ARG].split(',')
            tstr += REGTAB[chr[0]]
            tstr += REGTAB[chr[1]]
        else:
            tstr += REGTAB[a[ARG]]
            tstr += '0'
        binary = int(tstr,16)
        # print( a )
        # print("obj: ",hex(binary)," ,binary: ",bin(binary),'\n')
        pos.append(hex(binary))
        all_op_code.append(pos)
        
    elif a[OPTION]=='RESW':
        pc = pc + int(a[ARG])*3
        if need_new_line == False:
            need_new_line = True
    elif a[OPTION]=='RESB':
        pc += int(a[ARG])
        if need_new_line == False:
            need_new_line = True
    elif a[OPTION]=='BASE':
        index = index_2d(SYMTAB,a[ARG] )
        if index != -1:
            base_reg = int(SYMTAB[index][1],16)
    #FORMAT 3
    elif a[OPTION]!='BASE'and a[OPTION]!='END'and a[OPTION]!='START':
        pos.append(hex(pc))
        pc += 3
        #SYMBOL
        op = bin(int(OPTAB_dic[a[OPTION]],16)>>2)
        binary = int(op,2)
        binary = binary << 6
        if a[OPTION]=='RSUB':
            dis = 0
            binary += 48
        elif a[ARG][0] =='@':
            index = index_2d(SYMTAB,a[ARG][1:] )
            if index != -1:
                dis = abs(int(SYMTAB[index][1],16)-pc)
                binary += 34
        #Immediate
        elif a[ARG][0] =='#':
            index = index_2d(SYMTAB,a[ARG][1:] )
            if index != -1:
                dis = abs(int(SYMTAB[index][1],16)-pc)
                binary += 18
            #純數字
            else:
                dis = int(a[ARG][1:])
                binary += 16
        else: 
            if a[OPTION]=='STCH' or a[OPTION]=='LDCH':
                tmp = a[ARG].split(',')
                a[ARG] = tmp[0]
            index = index_2d(SYMTAB,a[ARG])
            if index != -1:
                #使用base reg找位址
                if a[OPTION]=='LDT' or a[OPTION]=='STX':
                    dis = abs(int(SYMTAB[index][1],16)-base_reg)
                    binary += 52
                elif a[OPTION]=='STCH' or a[OPTION]=='LDCH':
                    dis = abs(int(SYMTAB[index][1],16)-base_reg)
                    binary += 60
                #一般相對位址
                else:
                    dis = int(SYMTAB[index][1],16)-pc
                    if dis <0:
                        dis = int(hex(dis & 0xFFF),16)
                    binary += 50
                    #print("dis: ",bin(int(hex(dis & 0xFFF),16)))
        binary = binary << 12
        binary += dis
        pos.append(hex(binary))
        all_op_code.append(pos)
    
    if a[OPTION]!='RESW'and a[OPTION]!='START'and a[OPTION]!='RESB' and a[OPTION]!='BASE':
        code_cnt += 1
    if code_cnt == NEWLINE:
        need_new_line = True
   
# print(all_op_code)
# print(pos_cut)
pos_cnt = 0
index = index_2d(all_op_code,pos_cut[pos_cnt] )
code_str = 'T\t'+location( str_16(start) ) + ' '+ str_16(hex( int(all_op_code[index-1][0],16)-int(start,16)+get_digit(all_op_code,index-1)))+'\t'
#OBJECT CODE
for info in all_op_code:
    if info[0]!=pos_cut[pos_cnt]:
        code_str = code_str + str_16(info[1]) + '\t'
    else:
        object_code.append(code_str)
        if pos_cnt < len(pos_cut)-1 :
            pos_cnt += 1
            index = index_2d(all_op_code,pos_cut[pos_cnt] )
            code_str = 'T\t'+location( str_16(info[0]) ) + ' '+ str_16(hex( int(all_op_code[index-1][0],16)-int( info[0],16 )+get_digit(all_op_code,index-1))) + '\t'
        else:
            code_str = 'T\t'+location( str_16(info[0]) ) + ' '+ str_16(hex( int(all_op_code[len(all_op_code)-1][0],16)-int( info[0],16 )+get_digit(all_op_code,len(all_op_code)-1))) + '\t'
        code_str = code_str + str_16(info[1]) + '\t'
f.close()
object_code.append(code_str)
code_str = 'E\t'+ location( str_16(start) )
modification.append(code_str)
print("==============以下為object code================")
# 檔案寫進來
fw = open("object_code.txt", 'w')
for line in object_code:
    fw.write(line+'\n')
    print(line)
for line in modification:
    fw.write(line+'\n')
    print(line)
fw.close()
'''
if len(a)==4:
    print('obj code(16): ',a[CODE],'(2): ',bin(int(a[CODE],16)),'    instruct: ',a)
print("OPTION: ",a[OPTION],"十六進位: ",OPTAB_dic[a[OPTION]],"二進位: ",bin(int(OPTAB_dic[a[OPTION]],16)),"OP: ",op,'\n')
'''