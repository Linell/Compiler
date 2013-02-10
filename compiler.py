#	Linell Bonnette
#	timothy.bonnette@eagles.usm.edu
#	CSC 408 - Modified compiler in Python

# TO BE ADDED:
#       - For To or Downto
#       - Case Of
#       - Write
#       - Writeln
#       - Restricted global variables

import sys

numberOfReservedWords = 17 #number of reserved words
identTableLength = 100     #length of identifier table
maxDigits = 14      	   #max number of digits in number
identLength = 10           #length of identifiers

a = []
chars = []
rword = []
table = []

global infile, outfile, ch, sym, id, num, linlen, kk, line, errorFlag, linelen

class tableValue():
    def __init__(self, name, kind):
        self.name = name
        self.kind = kind

# This function simply returns errors. You could make this pretty darn nifty, if you took the time
# to *really* understand what all of the errors mean. Personally, I think I'm going to make my
# compiler a bit of a dick.
def error(num, sym):
    global errorFlag;
    errorFlag = 1
    
    print
    if num == 1: 
        print >>outfile, "Error on: " + sym + "\nUse = instead of :="
    elif num ==2: 
        print >>outfile, "Error on: " + sym + "\n= must be followed by a number."
    elif num ==3: 
        print >>outfile, "Error on: " + sym + "\nIdentifier must be followed by ="
    elif num ==4: 
        print >>outfile, "Error on: " + sym + "\nConst, Var, Procedure must be followed by an identifier."
    elif num ==5: 
        print >>outfile, "Error on: " + sym + "\nSemicolon or comman missing"
    elif num == 6: 
        print >>outfile, "Error on: " + sym + "\nIncorrect symbol after procedure declaration."
    elif num == 7:  
        print >>outfile, "Error on: " + sym + "\nStatement expected."
    elif num == 8:
        print >>outfile, "Error on: " + sym + "\nIncorrect symbol after statment part in block."
    elif num == 9:
        print >>outfile, "Error on: " + sym + "\nPeriod expected."
    elif num == 10: 
        print >>outfile, "Error on: " + sym + "\nSemicolon between statements is missing."
    elif num == 11:  
        print >>outfile, "Error on: " + sym + "\nUndeclard identifier"
    elif num == 12:
        print >>outfile, "Error on: " + sym + "\nAssignment to a constant or procedure is not allowed."
    elif num == 13:
        print >>outfile, "Error on: " + sym + "\nAssignment operator := expected."
    elif num == 14: 
        print >>outfile, "Error on: " + sym + "\ncall must be followed by an identifier"
    elif num == 15:  
        print >>outfile, "Error on: " + sym + "\nCall of a constant or a variable is meaningless."
    elif num == 16:
        print >>outfile, "Error on: " + sym + "\nThen expected"
    elif num == 17:
        print >>outfile, "Error on: " + sym + "\nSemicolon or end expected. "
    elif num == 18: 
        print >>outfile, "Error on: " + sym + "\nDO expected"
    elif num == 19:  
        print >>outfile, "Error on: " + sym + "\nIncorrect symbol following statement"
    elif num == 20:
        print >>outfile, "Error on: " + sym + "\nRelational operator expected."
    elif num == 21:
        print >>outfile, "Error on: " + sym + "\nExpression must not contain a procedure identifier"
    elif num == 22: 
        print >>outfile, "Error on: " + sym + "\nRight parenthesis missing"
    elif num == 23:  
        print >>outfile, "Error on: " + sym + "\nThe preceding factor cannot be followed by this symbol."
    elif num == 24:
        print >>outfile, "Error on: " + sym + "\nAn expression cannot begin with this symbol."
    elif num == 25:
        print >>outfile, "Error on: " + sym + "\nConstant or Number is expected."
    elif num == 26: 
        print >>outfile, "Error on: " + sym + "\nThis number is too large."
    elif num == 27: 
        print >>outfile, "Error on: " + sym + "\nDo expected after While."
    exit(0)
    
def getch():
    """ This gets the next character in the file. """
    global  whichChar, ch, linelen, line;
    if whichChar == linelen:         #if at end of line
        whichChar = 0
        line = infile.readline()     #get next line
        linelen = len(line)
        sys.stdout.write(line)	     # This prints out the line. You can kill this.
    if linelen != 0:
        ch = line[whichChar]
        whichChar += 1
    return ch
        
def getsym():
    """ *Dr. Ali stomps his foot* """
    global charcnt, ch, identLength, a, numberOfReservedWords, rword, sym, maxDigits, id
    # As long as you're reading something other than a good character, getch()
    while ch == " " or ch == "\n" or ch == "\r":
        getch()
    # 'a' appears to hold your sym
    a = []
    if ch.isalpha(): # If it's part of the alphabet
        k = 0	# k is not incremented in ch.isalpha()...maybe a bug?
        while True:
            a.append(ch)
            getch()
            if not ch.isalnum(): # is not alphanumeric
                break
        id = "".join(a) # concatenates everything into a string
        flag = 0	# 0 == not a reserved word, 1 == reserved word
	# Loop through the reserved words and check if the id is a reserved word
        for i in range(0, numberOfReservedWords):
            if rword[i] == id:	# if it *is* a reserved word, set the symbol to that
                sym = rword[i]	# and the flag to reserved word
                flag = 1
        if  flag == 0:    #sym is not a reserved word
            sym = "ident" 
            
    elif ch.isdigit(): # If it's a number
        k=0
        num=0
        sym = "number"
        while True:
            a.append(ch)
            k += 1
            getch()
            if not ch.isdigit():
                break
        if k>maxDigits:	# If the length of the sym is greated than the max length, error
            error(30, sym)
        else:
            id = "".join(a) # makes a string
    
    # These cases handle any special characters, and all function the same. When you have a :, >, or <,
    # it could have two meanings. This block is checking to see what the symbol is supposed to be.
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
        
#--------------POSITION FUNCTION----------------------------
def position(tx, k):
    global  table;
    table[0] = tableValue(k, "TEST")
    i = tx
    while table[i].name != k:
        i=i-1
    return i
#---------------ENTER PROCEDURE-------------------------------
# I believe that the enter procedure is inserting things into the table.
# tx is the index at which an item is inserted, and k is its 'type'.
def enter(tx, k):
    global id;
    tx[0] += 1                      # Increment the table index.
    while (len(table) > tx[0]):     # While I understand the code....I have no idea why this is happening.
      table.pop()                   
    x = tableValue(id, k)           # Creates a new instance of the tableValue class, and sets
                                    # id as the name and k as the kind.
    table.append(x)     # Appends x to the table at the newest position ... Best I can figure is that the 
                        # while statement is pretty much 'garbage detection' in that it's 'deleting' everything
                        # that's after the specified index. I suppose that means that you *can't* insert anything
                        # after the last table index that you want. I could be completely wrong though.
#--------------CONST DECLARATION---------------------------
def constdeclaration(tx):
    global sym, id;
    if sym=="ident":
        temp = id
        getsym()
        if sym == "eql":
            getsym()
            if sym == "number":
                id = temp
                enter(tx, "const")
                getsym()
            else:
                error(2, sym)
        else:
            error(3, sym)
    else:
        error(4, sym)

#-------------VARIABLE DECLARATION-----------------------------------
def vardeclaration(tx):
    global sym;
    if sym=="ident":
        enter(tx, "variable")
        getsym()
    else:
        error(4, sym)
    
#-------------BLOCK------------------------------------------------
def block(tableIndex):
    # tx is a one item long list..why?
    tx = [1]
    # Block is initialized with a table index (tx) of zero.
    tx[0] = tableIndex
    global sym, id;
    # Remember that whenever a block is called, we already have
    # a symbol held in sym.
    if sym == "CONST":
        while True:               # Makeshift do while in python
            getsym()              # This will *always* run the first getsym() and declare a constant.
            constdeclaration(tx)  # constdeclaration will handle the part that gets the next sym and such.
            if sym != "comma":    # If it doesn't detect a comma, it pops back out to look for a semicolon.
                break
        if sym != "semicolon":
            error(10, sym);
        getsym()                  # Remember to get the symbol before you leave.
    
    if sym == "VAR":              
        while True:               # Another makeshift do while.
            getsym()
            vardeclaration(tx)
            if sym != "comma":
                break
        if sym != "semicolon":
            error(10, sym)
        getsym()
    
    while sym == "PROCEDURE":
        getsym()
        if sym == "ident":
            enter(tx, "procedure")
            getsym()
        else:
            error(4, sym)
        if sym != "semicolon":
            error(10, sym)
        getsym()
        block(tx[0])
        
        if sym != "semicolon":
            error(10, sym)
        getsym()
    # Restricted globals will go here.
    statement(tx[0])

#--------------STATEMENT----------------------------------------
def statement(tx):
    global sym, id;
    if sym == "ident":
        i = position(tx, id)
        if i==0:
            error(11, sym)
        elif table[i].kind != "variable":
            error(12, sym)
        getsym()
        if sym != "becomes":
            error(13, sym)
        getsym()
        expression(tx)
        
    elif sym == "CALL":
        getsym()
        if sym != "ident":
            error(14, sym)
        i = position(tx, id)
        if i==0:
            error(11, sym)
        if table[i].kind != "procedure":
            error(15, sym)
        getsym()
    
    # The basic 'IF' statement.
    elif sym == "IF":
        getsym()
        condition(tx)
        if sym != "THEN":
            error(16, sym)
        getsym()
        statement(tx)
        # Adding the Else statement here
        # Works just fine.
        if sym == "ELSE":
            getsym()
            statement(tx)
        # Finished adding.
    
    elif sym == "BEGIN":
        while True:
            getsym()
            statement(tx)
            if sym != "semicolon":
                break
        if sym != "END":
            error(17, sym)
        getsym()
    
    elif sym == "WHILE":
        getsym()
        condition(tx)
        if sym != "DO":
            error(18, sym)
        getsym()
        statement(tx)

    # Adding the repeat / until
    elif sym == "REPEAT":
        while True:
            getsym()
            statement(tx)
            if sym != "semicolon":
                break
        if sym != "UNTIL":
            error(27, sym)
        getsym()
        condition(tx)
    # Ending the repeat / until


#--------------EXPRESSION--------------------------------------
def expression(tx):
    global sym;
    if sym == "plus" or sym == "minus":
        getsym()
        term(tx)
    else:
        term(tx)
    
    while sym == "plus" or sym == "minus":
        getsym()
        term(tx)

#-------------TERM----------------------------------------------------
def term(tx):
    global sym;
    factor(tx)
    while sym=="times" or sym=="slash":
        getsym()
        factor(tx)

#-------------FACTOR--------------------------------------------------
def factor(tx):
    global sym;
    if sym == "ident":
        i = position(tx, id)
        if i==0:
            error(11, sym)
        getsym()
    
    elif sym == "number":
        getsym()
    
    elif sym == "lparen":
        getsym()
        expression(tx)
        if sym != "rparen":
            error(22, sym)
        getsym()
    
    else:
        error(24, sym)

#-----------CONDITION-------------------------------------------------
def condition(tx):
    global sym;
    if sym == "ODD":
        getsym()
        expression(tx)
    
    else:
        expression(tx)
        if not (sym in ["eql","neq","lss","leq","gtr","geq"]):
            error(20, sym)
        else:
            getsym()
            expression(tx)
    
#-------------------MAIN PROGRAM------------------------------------------------------------#

# This is where all of the reserved words are added. Make sure that these
# are in alphabetical order. Make sure to increase numberOfReservedWords. I've added:
#   ELSE, REPEAT, UNTIL
rword.append('BEGIN')
rword.append('CALL')
rword.append('CONST')
rword.append('DO')
rword.append('DOWNTO')
rword.append('ELSE')
rword.append('END')
rword.append('FOR')
rword.append('IF')
rword.append('ODD')
rword.append('PROCEDURE')
rword.append('REPEAT')
rword.append('THEN')
rword.append('TO')
rword.append('UNTIL')
rword.append('VAR')
rword.append('WHILE')


# This holds all of your symbols. I do believe that ssym stands for 'system symbol',
# but I may be wrong. Regardless, we know what it's doing.
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
              

charcnt = 0
whichChar = 0
linelen = 0
ch = ' '
kk = identLength                
a = []
id= '     '
errorFlag = 0
		   # The table is the table that holds all of our variables.
table.append(0)    # The first position is made empty so that we can search using it.
sym = ' '            

#path to input file
infile = open('pre_mod_test_case.pas', 'r')
#path to output file, will create if doesn't already exist 
outfile =  sys.stdout     	

getsym()	    # get first symbol
block(0)        # call block initializing with a table index of zero

if sym != "period":      #period expected after block is completed
    error(9, sym)
   
print >> outfile
if errorFlag == 0:
    print >>outfile, "Successful compilation!"
