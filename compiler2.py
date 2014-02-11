#########################
#    Linell Bonnette    #
#########################

import sys, string

norw = 22      # Number of reserved words
txmax = 100    # Length of identifier table
nmax = 14      # Max number of digits in number
al = 10        # Length of identifiers
CXMAX = 500    # Maximum allowed lines of assembly code
STACKSIZE = 500
a = []
chars = []
rword = []
table = []        # Symbol table
code = []         # Code array
stack = [0] * STACKSIZE     # Interpreter stack
global infile, outfile, ch, sym, id, num, linlen, kk, line, errorFlag, linelen, codeIndx, prevIndx, codeIndx0, lineNumber

#------------- Values to put in the symbol table --------------- # 
class tableValue():                          
    def __init__(self, name, kind, level, adr, value):
        self.name = name
        self.kind = kind
        self.adr = adr
        self.value = value
        self.level = level

#---------- Commands to put in the array of assembly code------- #  #
class Cmd():                            
    def __init__(self, line, cmd, statLinks, value):
        self.line = line
        self.cmd = cmd
        self.statLinks = statLinks
        self.value = value

#------------- unction to generate assembly commands------------ #
def gen(cmd, statLinks, value):            
    global codeIndx, CXMAX
    if codeIndx > CXMAX:
        print >>outfile, "Error, Program is too long"
        exit(0)
    x = Cmd(codeIndx, cmd, statLinks, value)
    code.append(x)
    codeIndx += 1

#--------------function to change jump commands----------------- #
def fixJmp(cx, jmpTo):
    code[cx].value = jmpTo

#--------------Function to print p-Code for a given block------- #
def printCode():
    global codeIndx, codeIndx0
    print>>outfile
    for i  in range(codeIndx0, codeIndx):
        print >>outfile, code[i].line, code[i].cmd, code[i].statLinks, code[i].value
    prevIndx = codeIndx

#-------------Function to find a new base----------------------- #
def Base(statLinks, base):
    b1 = base
    while(statLinks > 0):
        b1 = stack[b1]
        statLinks -= 1
    return b1

#-------------P-Code Interpreter-------------------------------- #
def Interpret():
    print >>outfile, "\nStart PL/0\n"
    top = 0
    base = 1
    pos = 0
    stack[1] = 0
    stack[2] = 0
    stack[3] = 0
    while True:
        print '\nCompiling at position ' + str(pos)
        instr = code[pos]
        pos += 1
        #       LIT COMMAND
        if instr.cmd == "LIT":    
            top += 1
            stack[top] = int(instr.value)
        #       OPR COMMAND
        elif instr.cmd == "OPR":
            if instr.value == 0:         #end
                top = base - 1
                base = stack[top+2]
                pos = stack[top + 3]
            elif instr.value == 1:         #unary minus
                stack[top] = -stack[top]
            elif instr.value == 2:         #addition
                top -= 1
                stack[top] = stack[top] + stack[top+1]
            elif instr.value == 3:         #subtraction
                top -= 1
                stack[top] = stack[top] - stack[top+1]
            elif instr.value == 4:         #multiplication
                top -= 1
                stack[top] = stack[top] * stack[top+1]
            elif instr.value == 5:         #integer division
                top -= 1
                stack[top] = stack[top] / stack[top+1]
            elif instr.value == 6:         #logical odd function
                if stack[top] % 2 == 0:
                    stack[top] = 1
                else:
                    stack[top] = 0
            # case 7 n/a, used to debuge programs
            elif instr.value == 8:        #test for equality if stack[top-1] = stack[top], replace pair with true, otherwise false
                top -= 1
                if stack[top] == stack[top+1]:
                    stack[top] = 1
                else:
                    stack[top] = 0
            elif instr.value == 9:         #test for inequality
                top -= 1
                if stack[top] != stack[top+1]:
                    stack[top] = 1
                else:
                    stack[top] = 0
            elif instr.value == 10:         #test for < (if stack[top-1] < stack[t])
                top -= 1
                if stack[top] < stack[top+1]:
                    stack[top] = 1
                else:
                    stack[top] = 0
            elif instr.value == 11:        #test for >=
                top -= 1
                if stack[top] >= stack[top+1]:
                    stack[top] = 1
                else:
                    stack[top] = 0
            elif instr.value == 12:        #test for >
                top -= 1
                if stack[top] > stack[top+1]:
                    stack[top] = 1
                else:
                    stack[top] = 0
            elif instr.value == 13:        #test for <=
                top -= 1
                if stack[top] <= stack[top+1]:
                    stack[top] = 1
                else:
                    stack[top] = 0
            elif instr.value == 14:        #write/print stack[top]  
                print >>outfile, stack[top],
                top -= 1
            elif instr.value == 15:        #write/print a newline
                print
        #      LOD COMMAND
        elif instr.cmd == "LOD":
            top += 1
            stack[top] = stack[Base(instr.statLinks, base) + instr.value]
        #    STO COMMAND
        elif instr.cmd == "STO":
            stack[Base(instr.statLinks, base) + instr.value] = stack[top]
            top -= 1
        #    CAL COMMAND
        elif instr.cmd == "CAL": 
            stack[top+1] = Base(instr.statLinks, base)
            stack[top+2] = base
            stack[top+3] = pos
            base = top + 1
            pos = instr.value
        #    INT COMMAND
        elif instr.cmd == "INT":
            top = top + instr.value
        #     JMP COMMAND
        elif instr.cmd == "JMP":
            pos = instr.value
        #     JPC COMMAND
        elif instr.cmd == "JPC":
            if stack[top] == instr.statLinks:
                pos = instr.value
            top -= 1
        if pos == 0:
            break
    print >>outfile, "\n\nEnd PL/0\n"

#--------------Error Messages----------------------------------- #
def error(num, sym, tx):
    global errorFlag;
    errorFlag = 1

    i = position(tx, id)
    symName = table[i].name

    print
    if num == 1: 
        print >>outfile, "Error on line number: " + str(lineNumber) + " on " + sym + "\nUse = instead of :="
    elif num ==2: 
        print >>outfile, "Error on line number: " + str(lineNumber) + " on " + sym + "\n= must be followed by a number."
    elif num ==3: 
        print >>outfile, "Error on line number: " + str(lineNumber) + " on " + sym + "\nIdentifier must be followed by ="
    elif num ==4: 
        print >>outfile, "Error on line number: " + str(lineNumber) + " on " + sym + "\nConst, Var, Procedure must be followed by an identifier."
    elif num ==5: 
        print >>outfile, "Error on line number: " + str(lineNumber) + " on " + sym + "\nSemicolon or comman missing"
    elif num == 6: 
        print >>outfile, "Error on line number: " + str(lineNumber) + " on " + sym + "\nIncorrect symbol after procedure declaration."
    elif num == 7:  
        print >>outfile, "Error on line number: " + str(lineNumber) + " on " + sym + "\nStatement expected."
    elif num == 8:
        print >>outfile, "Error on line number: " + str(lineNumber) + " on " + sym + "\nIncorrect symbol after statment part in block."
    elif num == 9:
        print >>outfile, "Error on line number: " + str(lineNumber) + " on " + sym + "\nPeriod expected."
    elif num == 10: 
        print >>outfile, "Error on line number: " + str(lineNumber) + " on " + sym + "\nSemicolon between statements is missing."
    elif num == 11:  
        print >>outfile, "Error on line number: " + str(lineNumber) + " on " + sym + "\nUndeclard identifier"
    elif num == 12:
        print >>outfile, "Error on line number: " + str(lineNumber) + " on " + sym + "\nAssignment to a constant or procedure is not allowed."
    elif num == 13:
        print >>outfile, "Error on line number: " + str(lineNumber) + " on " + sym + "\nAssignment operator := expected."
    elif num == 14: 
        print >>outfile, "Error on line number: " + str(lineNumber) + " on " + sym + "\ncall must be followed by an identifier"
    elif num == 15:  
        print >>outfile, "Error on line number: " + str(lineNumber) + " on " + sym + "\nCall of a constant or a variable is meaningless."
    elif num == 16:
        print >>outfile, "Error on line number: " + str(lineNumber) + " on " + sym + "\nThen expected"
    elif num == 17:
        print >>outfile, "Error on line number: " + str(lineNumber) + " on " + sym + "\nSemicolon or end expected. "
    elif num == 18: 
        print >>outfile, "Error on line number: " + str(lineNumber) + " on " + sym + "\nDO expected"
    elif num == 19:  
        print >>outfile, "Error on line number: " + str(lineNumber) + " on " + sym + "\nIncorrect symbol following statement"
    elif num == 20:
        print >>outfile, "Error on line number: " + str(lineNumber) + " on " + sym + "\nRelational operator expected."
    elif num == 21:
        print >>outfile, "Error on line number: " + str(lineNumber) + " on " + sym + "\nExpression must not contain a procedure identifier"
    elif num == 22: 
        print >>outfile, "Error on line number: " + str(lineNumber) + " on " + sym + "\nRight parenthesis missing"
    elif num == 23:  
        print >>outfile, "Error on line number: " + str(lineNumber) + " on " + sym + "\nThe preceding factor cannot be followed by this symbol."
    elif num == 24:
        print >>outfile, "Error on line number: " + str(lineNumber) + " on " + sym + "\nAn expression cannot begin with this symbol."
    elif num ==25:
        print >>outfile, "Error on line number: " + str(lineNumber) + " on " + sym + "\nConstant or Number is expected."
    elif num == 26: 
        print >>outfile, "Error on line number: " + str(lineNumber) + " on " + sym + "\nThis number is too large."
    elif num == 27:
        print >>outfile, "Error on line number: " + str(lineNumber) + " on " + sym + "\nLeft parenthesis missing."
    elif num == 404:
        print >>outfile, "Error on line number: " + str(lineNumber) + " on " + sym + "\nThis method has not been implemented yet, sorry."
    exit(0)

#---------GET CHARACTER FUNCTION-------------------------------- #
def getch():
    global  whichChar, ch, linelen, line;
    if whichChar == linelen:         #if at end of line
        whichChar = 0
        line = infile.readline()     #get next line
        linelen = len(line)
        sys.stdout.write(line)
    if linelen != 0:
        ch = line[whichChar]
        whichChar += 1
    return ch

#----------GET SYMBOL FUNCTION---------------------------------- # 
def getsym():
    global charcnt, ch, al, a, norw, rword, sym, nmax, id, num, lineNumber
    while ch == " " or ch == "\n" or ch == "\r" or ch == "\t":
        if ch == "\n":
            lineNumber += 1
        getch()
    a = []
    if ch.isalpha():
        k = 0
        while True:
            a.append(string.upper(ch))
            getch()
            if not ch.isalnum():
                break
        id = "".join(a)
        flag = 0
        for i in range(0, norw):
            if rword[i] == id:
                sym = rword[i]
                flag = 1
        if  flag == 0:    #sym is not a reserved word
            sym = "ident"
    elif ch.isdigit():
        k=0
        num=0
        sym = "number"
        while True:
            a.append(ch)
            k += 1
            getch()
            if not ch.isdigit():
                break
        if k>nmax:
            error(30, sym, tx)
        else:
            num = "".join(a)
    elif ch == ':':
        getch()
        if ch == '=':
            sym = "becomes"
            getch()
        else:
            sym = "colon"
    elif ch == '>':
        getch()
        if ch == '=':
            sym = "geq"
            getch()
        else:
            sym = "gtr"
    elif ch == '<':
        getch()
        if ch == '=':
            sym = "leq"
            getch()
        elif ch == '>':
            sym = "neq"
            getch()
        else:
            sym = "lss"
    else:
        sym = ssym[ch]
        getch()

#--------------POSITION FUNCTION-------------------------------- #
def position(tx, id):
    global  table;
    table[0] = tableValue(id, "TEST", "TEST", "TEST", "TEST")
    i = tx
    while table[i].name != id:
        i=i-1
    return i

#---------------ENTER PROCEDURE--------------------------------- #
def enter(tx, k, level, dx):
    global id, num, codeIndx;
    tx[0] += 1
    while (len(table) > tx[0]):
      table.pop()
    if k == "const":
        x = tableValue(id, k, level, "NULL", num)
    elif k == "variable":
        x = tableValue(id, k, level, dx, "NULL")
        dx += 1
    elif k == "procedure":
        x = tableValue(id, k, level, dx, "NULL")
    table.append(x)
    return dx

#--------------CONST DECLARATION-------------------------------- #
def constdeclaration(tx, level):
    global sym, id, num;
    if sym=="ident":
        getsym()
        if sym == "eql":
            getsym()
            if sym == "number":
                enter(tx, "const", level, "null")
                getsym()
            else:
                error(2, sym, tx)
        else:
            error(3, sym, tx)
    else:
        error(4, sym, tx)

#-------------VARIABLE DECLARATION------------------------------ # 
def vardeclaration(tx, level, dx):
    global sym;
    if sym=="ident":
        dx = enter(tx, "variable", level, dx)
        getsym()
    else:
        error(4, sym, tx)
    return dx

#-------------BLOCK--------------------------------------------- # 
def block(tableIndex, level):
    global sym, id, codeIndx, codeIndx0;
    tx = [1]
    tx[0] = tableIndex
    tx0 = tableIndex
    dx = 3
    cx1 = codeIndx
    gen("JMP", 0 , 0)
    while sym == "PROCEDURE" or sym == "VAR" or sym == "CONST": 
        if sym == "CONST":
            while True:               #makeshift do while in python
                getsym()
                constdeclaration(tx, level)
                if sym != "comma":
                    break
            if sym != "semicolon":
                error(10, sym, tx);
            getsym()
        if sym == "VAR":
            while True:
                getsym()
                dx = vardeclaration(tx, level, dx)
                if sym != "comma":
                    break
            if sym != "semicolon":
                error(10, sym, tx)
            getsym()
        while sym == "PROCEDURE":
            getsym()
            if sym == "ident":
                enter(tx, "procedure", level, codeIndx)
                getsym()
            else:
                error(4, sym, tx)
            if sym != "semicolon":
                error(10, sym, tx)
            getsym()
            block(tx[0], level+ 1)
        
            if sym != "semicolon":
                error(10, sym, tx)
            getsym()
    fixJmp(cx1, codeIndx)
    if tx0 != 0:
        table[tx0].adr = codeIndx
    codeIndx0 = codeIndx
    gen("INT", 0, dx)
    statement(tx[0], level)
    gen("OPR", 0, 0)
    #print code for this block
    printCode()

#--------------STATEMENT----------------------------------------
def statement(tx, level):
    global sym, id, num;
    if sym == "ident":
        i = position(tx, id)
        if i==0:
            error(11, sym, tx)
        elif table[i].kind != "variable":
            error(12, sym, tx)
        getsym()
        if sym != "becomes":
            error(13, sym, tx)
        getsym()
        expression(tx, level)
        gen("STO", level -table[i].level, table[i].adr)
    elif sym == "CALL":
        getsym()
        if sym != "ident":
            error(14, sym, tx)
        i = position(tx, id)
        if i==0:
            error(11, sym, tx)
        if table[i].kind != "procedure":
            error(15, sym, tx)
        gen("CAL", level - table[i].level, table[i].adr)
        getsym()
    elif sym == "IF":
        getsym()
        condition(tx, level)
        cx1 = codeIndx  # save cx1
        gen("JPC", 0, 0)
        if sym != "THEN":
            error(16, sym, tx)
        getsym()
        statement(tx, level)
        if sym == "ELSE":
            getsym()
            cx2 = codeIndx0
            gen("JPC", 0, 0)
            fixJmp(cx1, codeIndx)
            statement(tx, level)
            fixJmp(cx2, codeIndx)
        else:
            # don't want to call this until we know we have no else
            fixJmp(cx1, codeIndx)
	# place your code for ELSE here
    elif sym == "BEGIN":
        while True:
            getsym()
            statement(tx, level)
            if sym != "semicolon":
                break
        if sym != "END":
            error(17, sym, tx)
        getsym()
    elif sym == "WHILE":
        getsym()
        cx1 = codeIndx
        condition(tx, level)
        cx2 = codeIndx
        gen("JPC", 0, 0)
        if sym != "DO":
            error(18, sym, tx)
        getsym()
        statement(tx, level)
        gen("JMP", 0, cx1)
        fixJmp(cx2, codeIndx)
    elif sym == "REPEAT":
    	error(404, sym, tx)
    elif sym == "FOR":
    	error(404, sym, tx)
    elif sym == "CASE":
    	error(404, sym, tx)
    elif sym == "WRITE" or sym == "WRITELN":
        symTest = sym # save the sym
    	getsym()
        if sym != "lparen":
            error(27, sym, tx)
        while True:
            getsym()
            expression(tx, level)
            gen("OPR", 0, 14)
            if sym != "comma":
                break
        if sym != "rparen":
            error(22, sym, tx)
        if symTest == "WRITELN":
            gen("OPR", 0, 15)
        getsym()


#--------------EXPRESSION--------------------------------------
def expression(tx, level):
    global sym;
    if sym == "plus" or sym == "minus": 
        addop = sym
        getsym()
        term(tx, level)
        if (addop == "minus"):         #if minus sign, do negate operation
            gen("OPR", 0, 1)
    else:
        term(tx, level)
    
    while sym == "plus" or sym == "minus":
        addop = sym
        getsym()
        term(tx, level)
        
        if(addop == "plus"):
            gen("OPR", 0, 2)       #add operation
        else:
            gen("OPR", 0, 3)       #subtract operation  

#-------------TERM----------------------------------------------------
def term(tx, level):
    global sym;
    factor(tx, level)
    while sym=="times" or sym=="slash":
        mulop = sym
        getsym()
        factor(tx, level)
        if mulop == "times":
            gen("OPR", 0, 4)         #multiply operation
        else:
            gen("OPR", 0, 5)         #divide operation

#-------------FACTOR--------------------------------------------------
def factor(tx, level):
    global sym, num, id;
    if sym == "ident":
        i = position(tx, id)
        if i==0:
            error(11, sym, tx)
        if table[i].kind == "const":
            gen("LIT", 0, table[i].value)
        elif table[i].kind == "variable":
            gen("LOD", level-table[i].level, table[i].adr)
        elif table[i].kind == "procedure":
            error(21, sym, tx)
        getsym()
    elif sym == "number":
        gen("LIT", 0, num)
        getsym()
    elif sym == "lparen":
        getsym()
        expression(tx, level)
        if sym != "rparen":
            error(22, sym, tx)
        getsym()
    else:
        error(24, sym, tx)

#-----------CONDITION-------------------------------------------------
def condition(tx, level):
    global sym;
    if sym == "ODD":
        getsym()
        expression(tx, level)
        gen("OPR", 0, 6)
    else:
        expression(tx, level)
        if not (sym in ["eql","neq","lss","leq","gtr","geq"]):
            error(20, sym, tx)
        else:
            temp = sym
            getsym()
            expression(tx, level)
            if temp == "eql":
                gen("OPR", 0, 8)
            elif temp == "neq":
                gen("OPR", 0, 9)
            elif temp == "lss":
                gen("OPR", 0, 10)
            elif temp == "geq":
                gen("OPR", 0, 11)
            elif temp == "gtr":
                gen("OPR", 0, 12)
            elif temp == "leq":
                gen("OPR", 0, 13)

#-------------------MAIN PROGRAM------------------------------------------------------------#
rword.append('BEGIN')
rword.append('CALL')
rword.append('CONST')
rword.append('DO')
rword.append('END')
rword.append('IF')
rword.append('ODD')
rword.append('PROCEDURE')
rword.append('THEN')
rword.append('VAR')
rword.append('WHILE')
rword.append('ELSE')
rword.append('REPEAT')
rword.append('UNTIL')
rword.append('FOR')
rword.append('TO')
rword.append('DOWNTO')
rword.append('CASE')
rword.append('OF')
rword.append('CEND')
rword.append('WRITE')
rword.append('WRITELN')

ssym = {'+' : "plus",
             '-' : "minus",
             '*' : "times",       
             '/' : "slash",
             '(' : "lparen",
             ')' : "rparen",
             '=' : "eql",
             ',' : "comma",
             '.' : "period",
             '#' : "neq",
             '<' : "lss",
             '>' : "gtr",
             '"' : "leq",
             '@' : "geq",
             ';' : "semicolon",
             ':' : "colon",}

lineNumber = 1
charcnt = 0
whichChar = 0
linelen = 0
ch = ' '
kk = al                
a = []
id= '     '
errorFlag = 0
table.append(0)      # Making the first position in the symbol table empty
sym = ' '       
codeIndx = 0         # First line of assembly code starts at 1
prevIndx = 0
infile = open('Input/test.pas', 'r')   # Path to input file
# Use "a" instead of "w+" if you don't want the file overwritten.
#outfile =  open("Output/compiler_output.txt", "a")     # Path to output file, will create if doesn't already exist
outfile = open("Output/compiler_output.txt", "w+")

getsym()                # Get first symbol
block(0, 0)             # Call block initializing with a table index of zero
if sym != "period":     # Period expected after block is completed
    error(9, sym, tx)
print  
if errorFlag == 0:
    print >>outfile, "Successful compilation!\n"
    
Interpret()
