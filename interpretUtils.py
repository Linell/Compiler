class Interpreter():
    """ This class is used to interpret p-code. """
    def __init__(self, outfile='', code=['']):
        self.outfile = open(outfile, 'w+')
        self.code = code
        self.stack = [0] * 500 # TODO: Change this to dynamic self.stack size

    def Base(self, statLinks, base):
        b1 = base
        while(statLinks > 0):
            b1 = self.stack[b1]
            statLinks -= 1
        return b1

    def Interpret(self):
        print >>self.outfile, "\nStart PL/0\n"
        top = 0
        base = 1
        pos = 0
        self.stack[1] = 0
        self.stack[2] = 0
        self.stack[3] = 0
        while True:
            print '\nCompiling at position ' + str(pos)
            instr = self.code[pos]
            pos += 1
            #       LIT COMMAND
            if instr.cmd == "LIT":    
                top += 1
                self.stack[top] = int(instr.value)
            #       OPR COMMAND
            elif instr.cmd == "OPR":
                if instr.value == 0:         #end
                    top = base - 1
                    base = self.stack[top+2]
                    pos = self.stack[top + 3]
                elif instr.value == 1:         #unary minus
                    self.stack[top] = -self.stack[top]
                elif instr.value == 2:         #addition
                    top -= 1
                    self.stack[top] = self.stack[top] + self.stack[top+1]
                elif instr.value == 3:         #subtraction
                    top -= 1
                    self.stack[top] = self.stack[top] - self.stack[top+1]
                elif instr.value == 4:         #multiplication
                    top -= 1
                    self.stack[top] = self.stack[top] * self.stack[top+1]
                elif instr.value == 5:         #integer division
                    top -= 1
                    self.stack[top] = self.stack[top] / self.stack[top+1]
                elif instr.value == 6:         #logical odd function
                    if self.stack[top] % 2 == 0:
                        self.stack[top] = 1
                    else:
                        self.stack[top] = 0
                # case 7 n/a, used to debuge programs
                elif instr.value == 8:        #test for equality if self.stack[top-1] = self.stack[top], replace pair with true, otherwise false
                    top -= 1
                    if self.stack[top] == self.stack[top+1]:
                        self.stack[top] = 1
                    else:
                        self.stack[top] = 0
                elif instr.value == 9:         #test for inequality
                    top -= 1
                    if self.stack[top] != self.stack[top+1]:
                        self.stack[top] = 1
                    else:
                        self.stack[top] = 0
                elif instr.value == 10:         #test for < (if self.stack[top-1] < self.stack[t])
                    top -= 1
                    if self.stack[top] < self.stack[top+1]:
                        self.stack[top] = 1
                    else:
                        self.stack[top] = 0
                elif instr.value == 11:        #test for >=
                    top -= 1
                    if self.stack[top] >= self.stack[top+1]:
                        self.stack[top] = 1
                    else:
                        self.stack[top] = 0
                elif instr.value == 12:        #test for >
                    top -= 1
                    if self.stack[top] > self.stack[top+1]:
                        self.stack[top] = 1
                    else:
                        self.stack[top] = 0
                elif instr.value == 13:        #test for <=
                    top -= 1
                    if self.stack[top] <= self.stack[top+1]:
                        self.stack[top] = 1
                    else:
                        self.stack[top] = 0
                elif instr.value == 14:        #write/print self.stack[top]  
                    print >>self.outfile, self.stack[top],
                    top -= 1
                elif instr.value == 15:        #write/print a newline
                    print >>self.outfile
            #      LOD COMMAND
            elif instr.cmd == "LOD":
                top += 1
                self.stack[top] = self.stack[self.Base(instr.statLinks, base) + instr.value]
            #    STO COMMAND
            elif instr.cmd == "STO":
                self.stack[self.Base(instr.statLinks, base) + instr.value] = self.stack[top]
                top -= 1
            #    CAL COMMAND
            elif instr.cmd == "CAL": 
                self.stack[top+1] = self.Base(instr.statLinks, base)
                self.stack[top+2] = base
                self.stack[top+3] = pos
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
                if self.stack[top] == instr.statLinks:
                    pos = instr.value
                top -= 1
            #     CTS COMMAND
            elif instr.cmd == "CTS":
                top += 1
                self.stack[top] = self.stack[top-1]
            #     Adding the LDI COMMAND here
            elif instr.cmd == "LDI":
                top += 1
                self.stack[top] = self.stack[self.stack[self.Base(instr.statLinks, base) + instr.value]]
            #     End the LDI COMMAND
            #     Adding the STI COMMAND here
            elif  instr.cmd == "STI":
                self.stack[self.stack[self.Base(instr.statLinks, base) + instr.value]] = self.stack[top]
                top -= 1
            #     End the STI COMMAND
            #     Adding the LDA COMMAND here
            elif instr.cmd == "LDA":
                top += 1
                self.stack[top] = self.Base(instr.statLinks, base) + instr.value
            #     End the LDA COMMAND here
            if pos == 0:
                break
        print >>self.outfile, "\n\nEnd PL/0\n"