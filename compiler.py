#########################
#    Linell Bonnette    #
#########################

import sys, string, argparse, copy, random

# Set up command line arguments
parser = argparse.ArgumentParser(description='P-Code generator and compiler created for CSC408 and CSC415 at USM.')
parser.add_argument('-i', '--input', help='Pascal file to be used as input.', default='Input/input.pas')
parser.add_argument('-o', '--output', help='Text file to which p-code and executed code will be sent to.', default='Output/output.txt')
parser.add_argument('-w', '--write', help='If the write flag is set to true, the output file will not be overwritten. Default behavior is to overwrite on each run of the compiler.', default=False)
args = vars(parser.parse_args())
# Parse command line arguments
if args['input'] != 'Input/input.pas':
    INFILE = args['input']
else:
    INFILE = 'Input/input.pas'

if args['output'] != 'Output/output.txt':
    OUTFILE = args['output']
else:
    OUTFILE = 'Output/output.txt'

if args['write'] != False:
    WRITEFLAG = 'a'
else:
    WRITEFLAG = 'w+'

norw = 30      # Number of reserved words
txmax = 100    # Length of identifier table
nmax = 14      # Max number of digits in number
al = 10        # Length of identifiers
CXMAX = 500    # Maximum allowed lines of assembly code
STACKSIZE = 500
a = []
chars = []
rword = []
table = []     # Symbol table
code = []      # Code array
stack = [0] * STACKSIZE     # Interpreter stack
globalStack = []            # This is a 'global stack' that is used to hold other stacks during concurrency
globalStack.append(stack)   # Put stack[0] onto the global stack
global infile, outfile, ch, sym, id, num, linlen, kk, line, errorFlag, linelen, codeIndx, prevIndx, codeIndx0, lineNumber, inFuncBody

#------------- Values to put in the symbol table --------------- # 
class tableValue():                          
    def __init__(self, name, kind, level, adr, value):
        self.name = name
        self.kind = kind
        self.adr = adr
        self.value = value
        self.level = level
        self.params = [0] * 10

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
def Base(statLinks, base, stackIndex):
    b1 = base
    while(statLinks > 0):
        b1 = globalStack[stackIndex][b1]
        statLinks -= 1
    return b1

#-------------P-Code Interpreter-------------------------------- #
def Interpret():
    print >>outfile, "\nStart PL/0\n"
    topStack = []
    baseStack = []
    posStack = []
    makeConcurrent = False
    concurrent = False
    stackIndex = 0       # We want to use the 0-th stack from the very beginning
    topStack.append(0)   # Setting this to five means we have four concurrent
    baseStack.append(1)  #  stacks (plus the main one, cause yah trick)
    posStack.append(0)
    globalStack[stackIndex][1] = 0
    globalStack[stackIndex][2] = 0
    globalStack[stackIndex][3] = 0
    while True:
        #print 'Compiling at position ' + str(posStack[stackIndex]) + ' on stack ' + str(stackIndex)
        if concurrent: # If we're running concurrently, pick a random stack to run
            stackIndex = random.randrange(0, len(globalStack))# concurrent
        else:
            stackIndex = 0 # We still need to do this in case we kill a stack.
        instr = code[posStack[stackIndex]]
        posStack[stackIndex] += 1
        #    LIT COMMAND
        if instr.cmd == "LIT":    
            topStack[stackIndex] += 1
            globalStack[stackIndex][topStack[stackIndex]] = int(instr.value)
        #    OPR COMMAND
        elif instr.cmd == "OPR":
            if instr.value == 0:         #end
                topStack[stackIndex] = baseStack[stackIndex] - 1
                baseStack[stackIndex] = globalStack[stackIndex][topStack[stackIndex]+2]
                posStack[stackIndex] = globalStack[stackIndex][topStack[stackIndex] + 3]
            elif instr.value == 1:         #unary minus
                globalStack[stackIndex][topStack[stackIndex]] = -globalStack[stackIndex][topStack[stackIndex]]
            elif instr.value == 2:         #addition
                topStack[stackIndex] -= 1
                globalStack[stackIndex][topStack[stackIndex]] = globalStack[stackIndex][topStack[stackIndex]] + globalStack[stackIndex][topStack[stackIndex]+1]
            elif instr.value == 3:         #subtraction
                topStack[stackIndex] -= 1
                globalStack[stackIndex][topStack[stackIndex]] = globalStack[stackIndex][topStack[stackIndex]] - globalStack[stackIndex][topStack[stackIndex]+1]
            elif instr.value == 4:         #multiplication
                topStack[stackIndex] -= 1
                globalStack[stackIndex][topStack[stackIndex]] = globalStack[stackIndex][topStack[stackIndex]] * globalStack[stackIndex][topStack[stackIndex]+1]
            elif instr.value == 5:         #integer division
                topStack[stackIndex] -= 1
                globalStack[stackIndex][topStack[stackIndex]] = globalStack[stackIndex][topStack[stackIndex]] / globalStack[stackIndex][topStack[stackIndex]+1]
            elif instr.value == 6:         #logical odd function
                if globalStack[stackIndex][topStack[stackIndex]] % 2 == 0:
                    globalStack[stackIndex][topStack[stackIndex]] = 1
                else:
                    globalStack[stackIndex][topStack[stackIndex]] = 0
            # case 7 n/a, used to debuge programs
            elif instr.value == 8:        #test for equality if globalStack[stackIndex][topStack[stackIndex]-1] = globalStack[stackIndex][topStack[stackIndex]], replace pair with true, otherwise false
                topStack[stackIndex] -= 1
                if globalStack[stackIndex][topStack[stackIndex]] == globalStack[stackIndex][topStack[stackIndex]+1]:
                    globalStack[stackIndex][topStack[stackIndex]] = 1
                else:
                    globalStack[stackIndex][topStack[stackIndex]] = 0
            elif instr.value == 9:         #test for inequality
                topStack[stackIndex] -= 1
                if globalStack[stackIndex][topStack[stackIndex]] != globalStack[stackIndex][topStack[stackIndex]+1]:
                    globalStack[stackIndex][topStack[stackIndex]] = 1
                else:
                    globalStack[stackIndex][topStack[stackIndex]] = 0
            elif instr.value == 10:         #test for < (if globalStack[stackIndex][topStack[stackIndex]-1] < globalStack[stackIndex][t])
                topStack[stackIndex] -= 1
                if globalStack[stackIndex][topStack[stackIndex]] < globalStack[stackIndex][topStack[stackIndex]+1]:
                    globalStack[stackIndex][topStack[stackIndex]] = 1
                else:
                    globalStack[stackIndex][topStack[stackIndex]] = 0
            elif instr.value == 11:        #test for >=
                topStack[stackIndex] -= 1
                if globalStack[stackIndex][topStack[stackIndex]] >= globalStack[stackIndex][topStack[stackIndex]+1]:
                    globalStack[stackIndex][topStack[stackIndex]] = 1
                else:
                    globalStack[stackIndex][topStack[stackIndex]] = 0
            elif instr.value == 12:        #test for >
                topStack[stackIndex] -= 1
                if globalStack[stackIndex][topStack[stackIndex]] > globalStack[stackIndex][topStack[stackIndex]+1]:
                    globalStack[stackIndex][topStack[stackIndex]] = 1
                else:
                    globalStack[stackIndex][topStack[stackIndex]] = 0
            elif instr.value == 13:        #test for <=
                topStack[stackIndex] -= 1
                if globalStack[stackIndex][topStack[stackIndex]] <= globalStack[stackIndex][topStack[stackIndex]+1]:
                    globalStack[stackIndex][topStack[stackIndex]] = 1
                else:
                    globalStack[stackIndex][topStack[stackIndex]] = 0
            elif instr.value == 14:        #write/print globalStack[stackIndex][topStack[stackIndex]]  
                print >>outfile, globalStack[stackIndex][topStack[stackIndex]],
                topStack[stackIndex] -= 1
            elif instr.value == 15:        #write/print a newline
                print >>outfile
        #    LOD COMMAND
        elif instr.cmd == "LOD":
            topStack[stackIndex] += 1
            globalStack[stackIndex][topStack[stackIndex]] = globalStack[stackIndex][Base(instr.statLinks, baseStack[stackIndex], stackIndex) + instr.value]
        #    STO COMMAND
        elif instr.cmd == "STO":
            globalStack[stackIndex][Base(instr.statLinks, baseStack[stackIndex], stackIndex) + instr.value] = globalStack[stackIndex][topStack[stackIndex]]
            topStack[stackIndex] -= 1
        #    CAL COMMAND
        elif instr.cmd == "CAL": 
            if makeConcurrent:
                # This is confusing as all get out, so here's a metric ton of comments to explain what I think
                # I am doing.
                # 1 - Create a copy of the main stack, since we can *only* do concurrent stuff from there.
                # 2 - Append the copy to the global stack.
                # 3 - We'll also need the top, base, and position for this. I *think* that as long as we do this
                #     every time, we can just append those to their respective stacks as well.
                newStack = copy.deepcopy(globalStack[0]) # Make a new stack based off of the main stack
                globalStack.append(newStack) # Append the new stack as the last element of the global stack.
                topStack.append(topStack[0])
                baseStack.append(baseStack[0])
                posStack.append(posStack[0])
                concurrent = True
                stackIndex = len(globalStack) - 1 # Switch to the new stack
            globalStack[stackIndex][topStack[stackIndex]+1] = Base(instr.statLinks, baseStack[stackIndex], stackIndex)
            globalStack[stackIndex][topStack[stackIndex]+2] = baseStack[stackIndex]
            globalStack[stackIndex][topStack[stackIndex]+3] = posStack[stackIndex]
            baseStack[stackIndex] = topStack[stackIndex] + 1
            posStack[stackIndex] = instr.value
        #    INT COMMAND
        elif instr.cmd == "INT":
            topStack[stackIndex] = topStack[stackIndex] + instr.value
        #     JMP COMMAND
        elif instr.cmd == "JMP":
            posStack[stackIndex] = instr.value
        #     JPC COMMAND
        elif instr.cmd == "JPC":
            if globalStack[stackIndex][topStack[stackIndex]] == instr.statLinks:
                posStack[stackIndex] = instr.value
            topStack[stackIndex] -= 1
        #     CTS COMMAND
        elif instr.cmd == "CTS":
            topStack[stackIndex] += 1
            globalStack[stackIndex][topStack[stackIndex]] = globalStack[stackIndex][topStack[stackIndex]-1]
        #     LDI COMMAND
        elif instr.cmd == "LDI":
            topStack[stackIndex] += 1
            globalStack[stackIndex][topStack[stackIndex]] = globalStack[stackIndex][globalStack[stackIndex][Base(instr.statLinks, baseStack[stackIndex], stackIndex) + instr.value]]
        #     STI COMMAND
        elif  instr.cmd == "STI":
            globalStack[stackIndex][globalStack[stackIndex][Base(instr.statLinks, baseStack[stackIndex], stackIndex) + instr.value]] = globalStack[stackIndex][topStack[stackIndex]]
            topStack[stackIndex] -= 1
        #     LDA COMMAND
        elif instr.cmd == "LDA":
            topStack[stackIndex] += 1
            globalStack[stackIndex][topStack[stackIndex]] = Base(instr.statLinks, baseStack[stackIndex], stackIndex) + instr.value
        elif instr.cmd == "COB":
            makeConcurrent = True
        elif instr.cmd == "COE":
            if stackIndex > 0: # If we aren't in the main stack
                print '********** DELETING A STACK **********'
                del globalStack[stackIndex]  # delete ALL the things
                del topStack[stackIndex]
                del posStack[stackIndex]
                del baseStack[stackIndex]
                if len(globalStack) == 1:
                    concurrent = False
                stackIndex = 0
            else:
                makeConcurrent = False
                if concurrent == True:
                    print '*** WAITING ON CONCURRENCY *** '
                    posStack[stackIndex] -= 1
        elif instr.cmd == "CPJ":
            topStack[stackIndex] += 1
            if stackIndex > 0:
                globalStack[stackIndex][topStack[stackIndex]] = 0
            else:
                globalStack[stackIndex][topStack[stackIndex]] = 1
        print 'thing is ' + str(posStack[stackIndex])
        if posStack[stackIndex] == 0:
            break
    print >>outfile, "\n\nEnd PL/0\n"

#--------------Error Messages----------------------------------- #
def error(num, sym='Undefined', tx=-9999):
    global errorFlag;
    errorFlag = 1

    errorMessage = ''
    # if tx != -9999:
    #     i = position(tx, id)
    #     symName = table[i].name

    if num == 1: 
        errorMessage = "Error on line number: " + str(lineNumber) + " on " + sym + "\nUse = instead of :="
    elif num ==2: 
        errorMessage = "Error on line number: " + str(lineNumber) + " on " + sym + "\n= must be followed by a number."
    elif num ==3: 
        errorMessage = "Error on line number: " + str(lineNumber) + " on " + sym + "\nIdentifier must be followed by ="
    elif num ==4: 
        errorMessage = "Error on line number: " + str(lineNumber) + " on " + sym + "\nConst, Var, Procedure must be followed by an identifier."
    elif num ==5: 
        errorMessage = "Error on line number: " + str(lineNumber) + " on " + sym + "\nSemicolon or comman missing"
    elif num == 6: 
        errorMessage = "Error on line number: " + str(lineNumber) + " on " + sym + "\nIncorrect symbol after procedure declaration."
    elif num == 7:  
        errorMessage = "Error on line number: " + str(lineNumber) + " on " + sym + "\nStatement expected."
    elif num == 8:
        errorMessage = "Error on line number: " + str(lineNumber) + " on " + sym + "\nIncorrect symbol after statment part in block."
    elif num == 9:
        errorMessage = "Error on line number: " + str(lineNumber) + " on " + sym + "\nPeriod expected."
    elif num == 10: 
        errorMessage = "Error on line number: " + str(lineNumber) + " on " + sym + "\nSemicolon between statements is missing."
    elif num == 11:  
        errorMessage = "Error on line number: " + str(lineNumber) + " on " + sym + "\nUndeclard identifier"
    elif num == 12:
        errorMessage = "Error on line number: " + str(lineNumber) + " on " + sym + "\nAssignment to a constant or procedure is not allowed."
    elif num == 13:
        errorMessage = "Error on line number: " + str(lineNumber) + " on " + sym + "\nAssignment operator := expected."
    elif num == 14: 
        errorMessage = "Error on line number: " + str(lineNumber) + " on " + sym + "\ncall must be followed by an identifier"
    elif num == 15:  
        errorMessage = "Error on line number: " + str(lineNumber) + " on " + sym + "\nCall of a constant or a variable is meaningless."
    elif num == 16:
        errorMessage = "Error on line number: " + str(lineNumber) + " on " + sym + "\nThen expected"
    elif num == 17:
        errorMessage = "Error on line number: " + str(lineNumber) + " on " + sym + "\nSemicolon or end expected. "
    elif num == 18: 
        errorMessage = "Error on line number: " + str(lineNumber) + " on " + sym + "\nDO expected"
    elif num == 19:  
        errorMessage = "Error on line number: " + str(lineNumber) + " on " + sym + "\nIncorrect symbol following statement"
    elif num == 20:
        errorMessage = "Error on line number: " + str(lineNumber) + " on " + sym + "\nRelational operator expected."
    elif num == 21:
        errorMessage = "Error on line number: " + str(lineNumber) + " on " + sym + "\nExpression must not contain a procedure identifier"
    elif num == 22: 
        errorMessage = "Error on line number: " + str(lineNumber) + " on " + sym + "\nRight parenthesis missing"
    elif num == 23:  
        errorMessage = "Error on line number: " + str(lineNumber) + " on " + sym + "\nThe preceding factor cannot be followed by this symbol."
    elif num == 24:
        errorMessage = "Error on line number: " + str(lineNumber) + " on " + sym + "\nAn expression cannot begin with this symbol."
    elif num ==25:
        errorMessage = "Error on line number: " + str(lineNumber) + " on " + sym + "\nConstant or Number is expected."
    elif num == 26: 
        errorMessage = "Error on line number: " + str(lineNumber) + " on " + sym + "\nThis number is too large."
    elif num == 27:
        errorMessage = "Error on line number: " + str(lineNumber) + " on " + sym + "\nLeft parenthesis missing."
    elif num == 28: 
        errorMessage = "Error on line number: " + str(lineNumber) + " on " + sym + "\nThere must be a variable after a for."
    elif num == 29:
        errorMessage = "Error on line number: " + str(lineNumber) + " on " + sym + "\nYou may only assign to a function within its body." 
    elif num == 30:
        errorMessage = "Error on line number: " + str(lineNumber) + " on " + sym + "\nIdentifier must be a variable."
    elif num == 31:
        errorMessage = "Error on line number: " + str(lineNumber) + " on " + sym + "\nExpecting either TO or DOWNTO." 
    elif num == 32:
        errorMessage = "Error on line number: " + str(lineNumber) + " on " + sym + "\nExpecting a colon."
    elif num == 33:
        errorMessage = "Error on line number: " + str(lineNumber) + " on " + sym + "\nExpecting a semicolon."   
    elif num == 34:
        errorMessage = "Error on line number: " + str(lineNumber) + " on " + sym + "\nMust be a function." 
    elif num == 35:
        errorMessage = "Error on line number: " + str(lineNumber) + " on " + sym + "\nCannot assign const or number to reference."
    elif num == 666:
        errorMessage = "Error on line number: " + str(lineNumber) + " on " + sym + "\nThis error message actually hasn't been implemented yet. So there's that."
    elif num == 404:
        errorMessage = "Error on line number: " + str(lineNumber) + " on " + sym + "\nThis method has not been implemented yet, sorry."

    print(errorMessage)
    print >>outfile, errorMessage 

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
        if  flag == 0:    # sym is not a reserved word
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
    # Adding the function stuff here. To be honest, I'm not sure if it's right.
    elif k == "function":
        x = tableValue(id, k, level, dx, "NULL")
    elif k == "value":
        x = tableValue(id, k, level, dx, "NULL")
        dx += 1
    elif k == "reference":
        x = tableValue(id, k, level, dx, "NULL")
        dx += 1
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

#------------- Value Parameter Thing --------------------------- #
def valparamdeclaration(tx, level, dx, tx0):
    global sym;
    if sym == "ident":
        dx = enter(tx, "value", level, dx)
        table[tx0].params[dx-4] = False
        getsym()
    else:
        error(4, sym, tx) # TODO: Create error for whatever this is
    return dx

#----------- Reference Parameter Thing ------------------------- #
def refparamdeclaration(tx, level, dx, tx0):
    global sym;
    if sym == "ident":
        dx = enter(tx, "reference", level, dx)
        table[tx0].params[dx-4] = True
        getsym()
    else:
        error(4, sym, tx) # TODO: Create error for whatever this is
    return dx

#-------------BLOCK--------------------------------------------- # 
def block(tableIndex, level):
    global sym, id, codeIndx, codeIndx0, inFuncBody;
    tx = [1]
    tx[0] = tableIndex
    tx0 = tableIndex
    dx = 3
    cx1 = codeIndx
    gen("JMP", 0 , 0)
    # Value and reference parameters
    if level > 0:
        if sym == "lparen":
            getsym()
            while True:
                if sym != "VAL" and sym != "REF":
                    error(38)
                temp = sym
                getsym()
                while True:
                    if sym != "ident":
                        error(39)
                    if temp == "VAL":
                        dx = valparamdeclaration(tx, level, dx, tx0)
                    elif temp == "REF":
                        dx = refparamdeclaration(tx, level, dx, tx0)
                    if sym != "comma":
                        break
                    getsym()
                if sym == "rparen":
                    break
                elif sym != "semicolon":
                    error(35)
                getsym()
            getsym()
            if sym != "semicolon":
                error(35)
        elif sym != "semicolon":
            error(35)
        getsym()

    while sym == "PROCEDURE" or sym == "VAR" or sym == "CONST" or sym == "FUNCTION": 
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
        # Adding function here
        while sym == "PROCEDURE" or sym == "FUNCTION":
            savedSym = sym
            getsym()
            if sym == "ident":
                if savedSym == "PROCEDURE":
                    enter(tx, "procedure", level, codeIndx)
                else:
                    enter(tx, "function", level, codeIndx)
                    inFuncBody = id
                getsym()
            else:
                error(4, sym, tx)
            # if sym != "semicolon":    # Removed this. Well. Sorta.
            #     error(10, sym, tx)
            #getsym()
            block(tx[0], level+ 1)
            if savedSym == "FUNCTION":
                inFuncBody = "NULL"
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
    global sym, id, num, inFuncBody;
    if sym == "ident":      
        i = position(tx, id)
        symType = table[i].kind
        if i==0:
            error(11, sym, tx)
        elif table[i].kind != "variable" and table[i].kind != "function" and table[i].kind != "value" and table[i].kind != "reference":
            error(12, sym, tx) # Not sure about this else if condition. Looks janky.
        if table[i].kind == "function" and inFuncBody != id:
            error(29, sym, tx)
        getsym()
        if sym != "becomes":
            error(13, sym, tx)
        getsym()
        expression(tx, level)
        if symType == "variable" or symType == "value":   
            gen("STO", level -table[i].level, table[i].adr)
        elif symType == "function":
            gen("STO", 0, -1)
        elif symType == "reference":  
            gen("STI", level -table[i].level, table[i].adr)
        else:
            error(666, sym, tx)     # TODO: Replace with better errors
    ##
    #  CALL
    ##
    elif sym == "CALL":
        getsym()
        if sym != "ident":
            error(14, sym, tx)
        i = position(tx, id)
        if i==0:
            error(11, sym, tx)
        if table[i].kind != "procedure" and table[i].kind != "function":
            error(15, sym, tx)
        getsym()
        if sym == "lparen":
            p = 0
            gen("INT", 0, 3)
            getsym()
            while True:
                if table[i].params[p] == True: # It is a reference variable
                    if sym != "ident":
                        error(666, sym, tx)
                    j = position(tx, id)
                    if j == 0:
                        error(15, sym, tx)
                    if table[j].kind == "value" or table[j].kind == "variable":
                        gen("LDA", level-table[j].level, table[j].adr)
                    elif table[j].kind == "reference":
                        gen("LOD", level-table[j].level, table[j].adr)
                    else:
                        error(666, sym, tx)
                    getsym()
                else:
                    expression(tx, level)
                p += 1
                if sym != "comma":
                    break
                getsym()
            if sym != "rparen":
                error(22, sym, tx)
            gen("INT", 0, -(3+p))
            getsym()
        gen("CAL", level - table[i].level, table[i].adr)
    ##
    #  IF/THEN/ELSE
    ##
    elif sym == "IF":
        getsym()
        generalExpression(tx, level)
        cx1 = codeIndx  # save cx1
        gen("JPC", 0, 0)
        if sym != "THEN":
            error(16, sym, tx)
        getsym()
        statement(tx, level)
        if sym == "ELSE":
            getsym()
            cx2 = codeIndx
            gen("JMP", 0, 0)
            fixJmp(cx1, codeIndx)
            statement(tx, level)
            fixJmp(cx2, codeIndx)
        else:
            # don't want to call this until we know we have no else
            fixJmp(cx1, codeIndx)
    ##
    #  BEGIN/END
    ##        
    elif sym == "BEGIN":
        while True:
            getsym()
            statement(tx, level)
            if sym != "semicolon":
                break
        if sym != "END":
            error(17, sym, tx)
        getsym()
    ##
    #  WHILE/TO
    ##
    elif sym == "WHILE":
        getsym()
        cx1 = codeIndx
        generalExpression(tx, level)
        cx2 = codeIndx
        gen("JPC", 0, 0)
        if sym != "DO":
            error(18, sym, tx)
        getsym()
        statement(tx, level)
        gen("JMP", 0, cx1)
        fixJmp(cx2, codeIndx)
    ##
    #  REPEAT/UNTIL
    ##
    elif sym == "REPEAT":
    	cx = codeIndx
        while True:
            getsym()
            statement(tx, level)
            if sym != "semicolon":
                break
        if sym != "UNTIL":
            error(27)
        getsym()
        generalExpression(tx, level)
        gen("JPC", 0, cx)
    ##
    #  FOR/TO|DOWNTO/DO
    ##
    elif sym == "FOR":
        getsym()
        if sym != "ident":
            error(28, tx, id)
        i = position(tx, id)
        if table[i].kind != "variable":
            error(30, sym, tx)
        if i==0:
            error(11, sym, tx)
        getsym()
        if sym != "becomes":
            error(29, tx, id)
        getsym()
        expression(tx, level)
        gen("STO", level -table[i].level, table[i].adr)
        if sym == "TO" or sym == "DOWNTO":
            pass
        else:
            error(30, tx, id)
        temp = sym
        getsym()
        expression(tx, level)
        cx1 = codeIndx
        gen("CTS", 0, 0)
        gen("LOD", level -table[i].level, table[i].adr)
        if temp == "TO":
            gen("OPR", 0, 11)
        elif temp == "DOWNTO":
            gen("OPR", 0, 13)
        else:
            error(31, tx, id)
        cx2 = codeIndx
        gen("JPC", 0, 0)
        if sym != "DO":
            error(18, tx, id)
        getsym()
        statement(tx, level)
        gen("LOD", level -table[i].level, table[i].adr)
        gen("LIT", 0, 1)
        if temp == "TO":
            gen("OPR", 0, 2)
        elif temp == "DOWNTO":
            gen("OPR", 0, 3)
        gen("STO", level -table[i].level, table[i].adr)
        gen("JMP", 0, cx1)
        fixJmp(cx2, codeIndx)
        gen("INT", 0, -1)
    ##
    #  CASE
    ##
    elif sym == "CASE":
        firstCase = True
        getsym()
        expression(tx, level)
        if sym != "OF":
            error(32, sym, tx)
        while True:
            getsym()
            if sym == "number" or sym == "ident":
                if sym == "ident":
                    i = position(tx, id)
                    if table[i].kind != "const":
                        error(25, sym, tx)
                    if i == 0:
                        error(11, sym, tx)
                    gen("CTS", 0, 0)
                    gen("LIT", 0, table[i].value)
                else:
                    gen("CTS", 0, 0)
                    gen("LIT", 0, num)
                gen("OPR", 0, 8)
                cx1 = codeIndx
                gen("JPC", 0, 0)
                getsym()
                if sym != "colon":
                    error(32, sym, tx)
                getsym()
                statement(tx, level)
                if sym != "semicolon":
                    error(33, sym, tx)
                if firstCase == True:
                    cx2 = codeIndx
                    gen("JMP", 0, 0)
                    firstCase = False
                    fixJmp(cx1, codeIndx)
                else:
                    gen("JMP", 0, cx2)
                fixJmp(cx1, codeIndx)
            else:
                break
        fixJmp(cx2, codeIndx)
        gen("INT", 0, -1)
        getsym()
    ##
    #  WRITE & WRITELN
    ##       
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
    ##
    #  COBEGIN and COEND
    ##
    elif sym == "COBEGIN":
        gen("COB", 0, 0)
        cxArray = []
        getsym()
        while True:
            if sym == "COEND":
                for cx in cxArray:
                    fixJmp(cx, codeIndx)
                gen("COE", 0, 0)
                break
            else:
                statement(tx, level)
                gen("CPJ", 0, 0)
                cxArray.append(codeIndx)
                gen("JPC", 0, 0)
            getsym()
        getsym()
    ##
    #
    ##
    

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
    while sym == "plus" or sym == "minus" or sym == "OR":
        addop = sym
        getsym()
        term(tx, level)
        if(addop == "plus" or addop == "OR"):
            gen("OPR", 0, 2)       #add operation
        else:
            gen("OPR", 0, 3)       #subtract operation  

#-------------TERM----------------------------------------------------
def term(tx, level):
    global sym;
    factor(tx, level)
    while sym=="times" or sym=="slash" or sym == "AND":
        mulop = sym
        getsym()
        factor(tx, level)
        if mulop == "times" or mulop == "AND":
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
        elif table[i].kind == "variable" or table[i].kind == "value":
            gen("LOD", level-table[i].level, table[i].adr)
        elif table[i].kind == "reference":                            
            gen("LDI", level-table[i].level, table[i].adr)
        elif table[i].kind == "procedure" or table[i].kind == "function":
            error(21, sym, tx)
        getsym()
    elif sym == "number":
        gen("LIT", 0, num)
        getsym()
    elif sym == "lparen":
        getsym()
        generalExpression(tx, level) # this is now a general expression
        if sym != "rparen":
            error(22, sym, tx)
        getsym()
    elif sym == "CALL":
        getsym()
        i = position(tx, id)
        if (sym != "ident" or table[i].kind != "function"):
            error(34, sym, tx)
        else:
            gen("INT", 0, 1)
            getsym()
            if sym == "lparen":
                p = 0
                gen("INT", 0, 3)
                getsym()
                while True:
                    if table[i].params[p] == True:
                        if sym != "ident":
                            error(28)
                        j = position(tx, id)
                        if j == 0:
                            error(15)
                        if table[j].kind == "value" or table[j].kind == "variable":
                            gen("LDA", level-table[j].level, table[j].adr)
                        elif table[j].kind == "reference":
                            gen("LOD", level-table[j].level, table[j].adr)
                        else:
                            error(40)
                        getsym()
                    else:
                        expression(tx, level)
                    p += 1
                    if sym != "comma":
                        break
                    getsym()
                if sym != "rparen":
                    error(22, sym, tx)
                gen("INT", 0, -(3+p))
                getsym()
            gen("CAL", level - table[i].level, table[i].adr)
    elif sym == "NOT":
        getsym()
        factor(tx, level)
        gen("LIT", 0, 0)
        gen("OPR", 0, 8)
    else:
        error(24, sym, tx)

#-----------CONDITION-------------------------------------------------
def generalExpression(tx, level):
    global sym;
    if sym == "ODD":
        getsym()
        expression(tx, level)
        gen("OPR", 0, 6)
    else:
        expression(tx, level)
        if not (sym in ["eql","neq","lss","leq","gtr","geq"]):
            #error(20, sym, tx)
            # Based on the 'General Expression' part of the document, this:
            pass
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
rword.append('AND')
rword.append('OR')
rword.append('FUNCTION')
rword.append('NOT')
rword.append('VAL')
rword.append('REF')
rword.append('COBEGIN')
rword.append('COEND')
# Semaphore
rword.append('SEMAPHORE')
# End semaphore

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
            ':' : "colon",
            'or' : "or",
            'and' : "and",
            'val' : "VAR",
            'ref' : "REF",}

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
infile = open(INFILE, 'r')   # Path to input file
# Use "a" instead of "w+" if you don't want the file overwritten.
#outfile =  open(OUTFILE, "a")     # Path to output file, will create if doesn't already exist
outfile = open(OUTFILE, WRITEFLAG)

print >> outfile, "\n*************************\nCompiling " + INFILE + "\n*************************\n" # Prints which file you're working on.

getsym()                # Get first symbol
block(0, 0)             # Call block initializing with a table index of zero
if sym != "period":     # Period expected after block is completed
    error(9)
print  
if errorFlag == 0:
    print >>outfile, "Successful compilation!\n"
    
Interpret()
