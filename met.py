#am:5216 username:cs215216 onoma: Ioannis Drivas
#run with python met.py <source_file>
#and the output will be <source_file>.int, <source_file.sym>, <source_file.asm>
import sys

reserved_char = ["program","declare","if","else","while","switchcase","when","default","whilecase",
            "incase","untilcase","until","forcase","return","print","input","function","in","inout","not","and","or"]
symbols = ["+","-","*","/","=",";","(",")","<",">","<>","<=",">=",":=","[","]",":","//","/*","*/",",","{","}"]
Identifiers = []
spaces= [' ', '\t', '\n']
add_oper = ["+","-"]
mul_oper = ["*","/"]
relational_oper = ['=', '<=', '>=', '<>', '<', '>']
max_int = 32767
min_int = -32767
max_id_length = 30

class Lexer:
    def __init__(self, filename):
        self.filename = filename
        self.tokens = []
        self.current_token_index = 0
        self.current_line = 1

    def __del__(self):
        pass

    def error(self, message):
        print(f"Error on line {self.current_line}: {message}")
        sys.exit(1)
    
    def next_token(self):
        if self.current_token_index < len(self.tokens):
            token = self.tokens[self.current_token_index]
            self.current_token_index += 1
            return token
        else:
            return Token("eof", "eof", self.current_line)
    
    def tokenize(self):
        with open(self.filename, 'r', encoding='utf-8') as file:
            program = file.read()
        char = 0
        while char < len(program):
            # consume whitespace
            if program[char] in spaces:
                #update line number on newlines
                if program[char] == '\n':
                    self.current_line += 1
                char += 1
            #found first /
            elif program[char] == '/':
                #found multicomment
                if char + 1 < len(program) and program[char + 1] == '*':
                    char += 2
                    #consume until end of comment
                    while char < len(program) and not (program[char] == '*' and char + 1 < len(program) and program[char + 1] == '/'):
                        #count lines in comment
                        if program[char] == '\n':
                            self.current_line += 1
                        if program[char] == '/' and char + 1 < len(program) and program[char + 1] == '*':
                            self.error("Nested comments are not allowed")
                        char += 1
                    #consume the closing */
                    if char < len(program):
                        char += 2
                    #comment was not closed
                    else:
                        self.error("Unterminated comment") 
                #found single line comment
                elif char + 1 < len(program) and program[char + 1] == '/':
                    char += 2
                    #consume until end of line
                    while char < len(program) and program[char] != '\n':
                        char += 1
                #found division symbol
                else:
                    self.tokens.append(Token("symbol", "/", self.current_line))
                    char += 1
            #found symbol that is not a comment
            elif program[char] in symbols and not (program[char] == '/' and char + 1 < len(program) and program[char + 1] in ['/', '*']):
                #handle single character symbols 
                if (program[char] in ["+","-","*","=",";","(",")",","]):
                    self.tokens.append(Token("symbol", program[char], self.current_line))
                    char += 1
                #consume brackets
                elif (program[char] =="[" or program[char] == "]"):
                    self.tokens.append(Token("symbol", program[char], self.current_line))
                    char += 1
                #consume curly braces
                elif (program[char] =="{" or program[char] == "}"):
                    self.tokens.append(Token("symbol", program[char], self.current_line))
                    char += 1
                #handle multi character symbols
                elif (program[char] == "<" or program[char] == ">"):
                    if char + 1 < len(program) and program[char + 1] == "=":
                        self.tokens.append(Token("symbol", program[char] + "=", self.current_line))
                        char += 2
                    elif program[char] == "<" and char + 1 < len(program) and program[char + 1] == ">":
                        self.tokens.append(Token("symbol", "<>", self.current_line))
                        char += 2
                    else:
                        self.tokens.append(Token("symbol", program[char], self.current_line))
                        char += 1
                #handle assignment symbol
                elif program[char] == ":":
                    if char + 1 < len(program) and program[char + 1] == "=":
                        self.tokens.append(Token("symbol", ":=", self.current_line))
                        char += 2
                    else:
                        self.tokens.append(Token("symbol", ":", self.current_line))
                        char += 1
            #handle identifier or reserved word or integer literal
            else:
                #check if first character is valid
                if not (program[char].isalnum()):
                    self.error(f"Invalid character '{program[char]}'")
                start = char
                while char < len(program) and not (program[char] in spaces or program[char] in symbols):
                    char += 1
                word = program[start:char]
                if word in reserved_char:
                    self.tokens.append(Token("reserved_word", word, self.current_line))
                elif word.isdigit():
                    if int(word) > max_int or int(word) < min_int:
                        self.error("Integer literal out of range")
                    self.tokens.append(Token("integer_literal", word, self.current_line))
                else:
                    if word[0].isdigit():
                        self.error("Identifier cannot start with a digit")
                    if len(word) > max_id_length:
                        word = word[:max_id_length]
                    self.tokens.append(Token("identifier", word, self.current_line))

class Token:
    def __init__(self, family, recognized_string, line_number):
        self.family = family
        self.recognized_string = recognized_string
        self.line_number = line_number

    def __str__(self):
        return f"Token(family = {self.family}, recognized_string = {self.recognized_string}, line = {self.line_number})"

class Parser:
    lexical_analyzer = None

    def __init__(self, lexer):
        self.lexical_analyzer = lexer
        self.icg = IntermediateCodeGenerator()
        self.symTable = SymbolTable()
        self.asm_code = ["    j L_MAIN"]
    
    def get_token(self):
        return self.lexical_analyzer.next_token()
    
    def run(self):
        self.current_token = self.get_token()
        self.program()
        if self.current_token.recognized_string != "eof":
            self.error(f"Error at line {self.current_token.line_number}: Unexpected code after the end of the program")
        print("Compilation completed successfully")

    def error(self, message):
        print(message)
        sys.exit(1)
    
    
    def program(self):
        if self.current_token.recognized_string == "program":
            self.current_token = self.get_token()
            if self.current_token.family == "identifier":
                self.program_name = self.current_token.recognized_string
                self.current_token = self.get_token()
                self.symTable.add_scope()
                self.programblock(self.program_name, is_main=True)
                self.symTable.remove_scope()
            else:
                self.error(f"Error at line {self.current_token.line_number}: Expected identifier after 'program'")
        else:
            self.error(f"Error at line {self.current_token.line_number}: Expected 'program' at the beginning of the program")
    
    def programblock(self, block_name, is_main=False):
        if self.current_token.recognized_string == "{":
            self.current_token = self.get_token()
            self.declarations()
            self.functions()
            start_quad_index = len(self.icg.quads)
            self.icg.genquad("begin_block", block_name, "_", "_")
            if not is_main:
                self.symTable.update_start_quad(block_name, self.icg.nextquad() - 1)
            self.statements_sequence()

            if is_main:
                self.icg.genquad("halt", "_", "_", "_")
            self.icg.genquad("end_block", block_name, "_", "_")

            block_quads = self.icg.quads[start_quad_index:]
            fcg = FinalCodeGenerator(block_quads, self.symTable, is_main=is_main)
            fcg.generate()
            self.asm_code.extend(fcg.asm)

            if self.current_token.recognized_string == "}":
                self.current_token = self.get_token()
            else:
                self.error(f"Error at line {self.current_token.line_number}: Expected '}}' at the end of program block")
        else:
            self.error(f"Error at line {self.current_token.line_number}: Expected '{{' at the beginning of program block")
    
    def declarations(self):
        while self.current_token.recognized_string == "declare":
            self.current_token = self.get_token()
            self.varlist()
            if self.current_token.recognized_string == ";":
                self.current_token = self.get_token()
            else:
                self.error(f"Error at line {self.current_token.line_number}: Expected ';' after variable declaration")
    
    def varlist(self):
        if self.current_token.family == "identifier":
            self.symTable.add_entity(self.current_token.recognized_string, "VAR")
            self.current_token = self.get_token()
            while self.current_token.recognized_string == ",":
                self.current_token = self.get_token()
                if self.current_token.family == "identifier":
                    self.symTable.add_entity(self.current_token.recognized_string, "VAR")
                    self.current_token = self.get_token()
                else:
                    self.error(f"Error at line {self.current_token.line_number}: Expected identifier after ',' in variable declaration")
    
    def functions(self):
        while self.current_token.recognized_string == "function":
            self.current_token = self.get_token()
            self.function()
    
    def function(self):
            if self.current_token.family == "identifier":
                func_name = self.current_token.recognized_string
                self.symTable.add_entity(func_name, "FUNC")
                self.current_token = self.get_token()
                self.symTable.add_scope()
                self.formalpars()
                self.programblock(func_name)
                self.symTable.remove_scope()
            else:
                self.error(f"Error at line {self.current_token.line_number}: Expected identifier after 'function' in function declaration")
    
    def formalpars(self):
        if self.current_token.recognized_string == "(":
            self.current_token = self.get_token()
            self.formalparlist()
            if self.current_token.recognized_string == ")":
                self.current_token = self.get_token()
            else:
                self.error(f"Error at line {self.current_token.line_number}: Expected ')' at the end of formal parameter list in function declaration")
        else:
            self.error(f"Error at line {self.current_token.line_number}: Expected '(' at the beginning of formal parameter list in function declaration")
    
    def formalparlist(self):
        if self.current_token.recognized_string in ["in", "inout"]:
            self.formalparitem()
        while self.current_token.recognized_string == ",":
            self.current_token = self.get_token()
            self.formalparitem()
    
    def formalparitem(self):
        if self.current_token.recognized_string in ["in", "inout"]:
            if self.current_token.recognized_string == "in":
                parMode = "CV"
            else:
                parMode = "REF"
            self.current_token = self.get_token()
            if self.current_token.family == "identifier":
                self.symTable.add_entity(self.current_token.recognized_string, "PARAM", parMode)
                self.current_token = self.get_token()
            else:
                self.error(f"Error at line {self.current_token.line_number}: Expected identifier after 'in' or 'inout' in formal parameter declaration")
        else:
            self.error(f"Error at line {self.current_token.line_number}: Expected 'in' or 'inout' at the beginning of formal parameter declaration")
    
    def statements_sequence(self):
        if self.current_token.recognized_string != "}":
            self.statements()
        while self.current_token.recognized_string == ";":
            self.current_token = self.get_token()
            self.statements()
    
    def statements(self):
        if self.current_token.recognized_string == "{":
            self.current_token = self.get_token()
            self.statements_sequence()
            if self.current_token.recognized_string == "}":
                self.current_token = self.get_token()
            else:
                self.error(f"Error at line {self.current_token.line_number}: Expected '}}' at the end of statements block")
        else:
            self.statement()
    
    def statement(self):
        if self.current_token.family == "identifier":
            self.assignment_stat()
        elif self.current_token.recognized_string == "if":
            self.if_stat()
        elif self.current_token.recognized_string == "while":
            self.while_stat()
        elif self.current_token.recognized_string == "switchcase":
            self.switchcase_stat()
        elif self.current_token.recognized_string == "whilecase":
            self.whilecase_stat()
        elif self.current_token.recognized_string == "incase":
            self.incase_stat()
        elif self.current_token.recognized_string == "forcase":
            self.forcase_stat()
        elif self.current_token.recognized_string == "untilcase":
            self.untilcase_stat()
        elif self.current_token.recognized_string == "input":
            self.input_stat()
        elif self.current_token.recognized_string == "print":
            self.print_stat()
        elif self.current_token.recognized_string == "return":
            self.return_stat()
        #failsafe error
        else:
            self.error(f"Error at line {self.current_token.line_number}: Expected a statement")
    
    def assignment_stat(self):
        if self.current_token.family == "identifier":
            id_name = self.current_token.recognized_string
            self.symTable.search_entity(id_name)
            self.current_token = self.get_token()
            if self.current_token.recognized_string == ":=":
                self.current_token = self.get_token()
                E_place = self.expression()
                self.icg.genquad(":=", E_place, "_", id_name)
            else:
                self.error(f"Error at line {self.current_token.line_number}: Expected ':=' in assignment statement")
        else:
            self.error(f"Error at line {self.current_token.line_number}: Expected identifier at the beginning of assignment statement")
    
    def if_stat(self):
        if self.current_token.recognized_string == "if":
            self.current_token = self.get_token()
            cond_true, cond_false = self.condition()
            self.icg.backpatch(cond_true, self.icg.nextquad())
            self.statements()
            ifList = self.icg.makelist(self.icg.nextquad())
            self.icg.genquad("jump", "_", "_", "_")
            self.icg.backpatch(cond_false, self.icg.nextquad())
            self.elsepart()
            self.icg.backpatch(ifList, self.icg.nextquad())
        else:
            self.error(f"Error at line {self.current_token.line_number}: Expected 'if' at the beginning of if statement")
    
    def elsepart(self):
        if self.current_token.recognized_string == "else":
            self.current_token = self.get_token()
            self.statements()
    
    def while_stat(self):
        if self.current_token.recognized_string == "while":
            self.current_token = self.get_token()
            condquad = self.icg.nextquad()
            cond_true, cond_false = self.condition()
            self.icg.backpatch(cond_true, self.icg.nextquad())
            self.statements()
            self.icg.genquad("jump", "_", "_", str(condquad))
            self.icg.backpatch(cond_false, self.icg.nextquad())
        else:
            self.error(f"Error at line {self.current_token.line_number}: Expected 'while' at the beginning of while statement")
    
    def switchcase_stat(self):
        if self.current_token.recognized_string == "switchcase":
            self.current_token = self.get_token()
            exitlist = self.icg.emptylist()
            while self.current_token.recognized_string == "when":
                self.current_token = self.get_token()
                cond_true, cond_false = self.condition()
                if self.current_token.recognized_string == ":":
                    self.current_token = self.get_token()
                    self.icg.backpatch(cond_true, self.icg.nextquad())
                    self.statements()
                else:
                    self.error(f"Error at line {self.current_token.line_number}: Expected ':' after condition in switchcase statement")
                t = self.icg.makelist(self.icg.nextquad())
                self.icg.genquad("jump", "_", "_", "_")
                exitlist = self.icg.merge(exitlist, t)
                self.icg.backpatch(cond_false, self.icg.nextquad())
            if self.current_token.recognized_string == "default":
                self.current_token = self.get_token()
                if self.current_token.recognized_string == ":":
                    self.current_token = self.get_token()
                    self.statements()
                    self.icg.backpatch(exitlist, self.icg.nextquad())
                else:
                    self.error(f"Error at line {self.current_token.line_number}: Expected ':' after 'default' in switchcase statement")
            else:
                self.error(f"Error at line {self.current_token.line_number}: Expected 'default' at the end of switchcase statement")
        else:
            self.error(f"Error at line {self.current_token.line_number}: Expected 'switchcase' at the beginning of switchcase statement")

    def whilecase_stat(self):
        if self.current_token.recognized_string == "whilecase":
            self.current_token = self.get_token()
            condquad = self.icg.nextquad()
            while self.current_token.recognized_string == "when":
                self.current_token = self.get_token()
                cond_true, cond_false = self.condition()
                if self.current_token.recognized_string == ":":
                    self.current_token = self.get_token()
                    self.icg.backpatch(cond_true, self.icg.nextquad())
                    self.statements()
                    self.icg.genquad("jump", "_", "_", str(condquad))
                    self.icg.backpatch(cond_false, self.icg.nextquad())
                else:
                    self.error(f"Error at line {self.current_token.line_number}: Expected ':' after condition in whilecase statement")
            if self.current_token.recognized_string == "default":
                self.current_token = self.get_token()
                if self.current_token.recognized_string == ":":
                    self.current_token = self.get_token()
                    self.statements()
                else:
                    self.error(f"Error at line {self.current_token.line_number}: Expected ':' after 'default' in whilecase statement")
        else:
            self.error(f"Error at line {self.current_token.line_number}: Expected 'whilecase' at the beginning of whilecase statement") 

    def incase_stat(self):
        if self.current_token.recognized_string == "incase":
            self.current_token = self.get_token()
            #flag to check if any condition was true
            flag = self.icg.newtemp()
            self.symTable.add_entity(flag, "TEMP")
            firstquad = self.icg.nextquad()
            self.icg.genquad(":=", "0", "_", flag)
            while self.current_token.recognized_string == "when":
                self.current_token = self.get_token()
                cond_true, cond_false = self.condition()
                if self.current_token.recognized_string == ":":
                    self.current_token = self.get_token()
                    self.icg.backpatch(cond_true, self.icg.nextquad())
                    self.icg.genquad(":=", "1", "_", flag)
                    self.statements()
                    self.icg.backpatch(cond_false, self.icg.nextquad())
                else:
                    self.error(f"Error at line {self.current_token.line_number}: Expected ':' after condition in incase statement")
            self.icg.genquad("=", "1", flag, str(firstquad))
        else:
            self.error(f"Error at line {self.current_token.line_number}: Expected 'incase' at the beginning of incase statement")     
    
    def forcase_stat(self):
        if self.current_token.recognized_string == "forcase":
            self.current_token = self.get_token()
            if self.current_token.family == "identifier":
                id_place = self.current_token.recognized_string
                self.current_token = self.get_token()
                if self.current_token.recognized_string == "=":
                    self.current_token = self.get_token()
                    if self.current_token.family == "integer_literal":
                        int_val = self.current_token.recognized_string
                        self.current_token = self.get_token()
                        self.icg.genquad(":=", "1", "_", id_place)
                        loopquad = self.icg.nextquad()
                        self.icg.genquad("<=", id_place, int_val, str(self.icg.nextquad() + 2))
                        exitlist = self.icg.makelist(self.icg.nextquad())
                        self.icg.genquad("jump", "_", "_", "_")
                        while self.current_token.recognized_string == "when":
                            self.current_token = self.get_token()
                            cond_true, cond_false = self.condition()
                            if self.current_token.recognized_string == ":":
                                self.current_token = self.get_token()
                                self.icg.backpatch(cond_true, self.icg.nextquad())
                                self.statements()
                                self.icg.backpatch(cond_false, self.icg.nextquad())
                            else:
                                self.error(f"Error at line {self.current_token.line_number}: Expected ':' after condition in forcace statement")
                        t = self.icg.newtemp()
                        self.symTable.add_entity(t, "TEMP")
                        self.icg.genquad("+", id_place, "1", t)
                        self.icg.genquad(":=", t, "_", id_place)
                        self.icg.genquad("jump", "_", "_", str(loopquad))
                        self.icg.backpatch(exitlist, self.icg.nextquad())
                    else:
                        self.error(f"Error at line {self.current_token.line_number}: Expected integer literal in forcace statement")
                else:
                    self.error(f"Error at line {self.current_token.line_number}: Expected '=' in forcace statement")
            else:
                self.error(f"Error at line {self.current_token.line_number}: Expected identifier in forcace statement")
        else:
            self.error(f"Error at line {self.current_token.line_number}: Expected 'forcase' at the beginning of forcace statement")
    
    def untilcase_stat(self):
        if self.current_token.recognized_string == "untilcase":
            self.current_token = self.get_token()
            condquad = self.icg.nextquad()
            while self.current_token.recognized_string == "when":
                self.current_token = self.get_token()
                cond_true, cond_false = self.condition()
                if self.current_token.recognized_string == ":":
                    self.current_token = self.get_token()
                    self.icg.backpatch(cond_true, self.icg.nextquad())
                    self.statements()
                    self.icg.backpatch(cond_false, self.icg.nextquad())
                else:
                    self.error(f"Error at line {self.current_token.line_number}: Expected ':' after condition in untilcase statement")
            if self.current_token.recognized_string == "until":
                self.current_token = self.get_token()
                cond_true, cond_false = self.condition()
                self.icg.backpatch(cond_true, self.icg.nextquad())
                self.icg.backpatch(cond_false, condquad)
            else:
                self.error(f"Error at line {self.current_token.line_number}: Expected 'until' at the end of untilcase statement")
        else:
            self.error(f"Error at line {self.current_token.line_number}: Expected 'untilcase' at the beginning of untilcase statement")
    
    def print_stat(self):
        if self.current_token.recognized_string == "print":
            self.current_token = self.get_token()
            E_place = self.expression()
            self.icg.genquad("out", E_place, "_", "_")
        else:
            self.error(f"Error at line {self.current_token.line_number}: Expected 'print' at the beginning of print statement")
    
    def input_stat(self):
        if self.current_token.recognized_string == "input":
            self.current_token = self.get_token()
            if self.current_token.family == "identifier":
                id_name = self.current_token.recognized_string
                self.current_token = self.get_token()
                self.icg.genquad("inp", id_name, "_", "_")
            else:
                self.error(f"Error at line {self.current_token.line_number}: Expected identifier after 'input' in input statement")
        else:
            self.error(f"Error at line {self.current_token.line_number}: Expected 'input' at the beginning of input statement")
    
    def return_stat(self):
        if self.current_token.recognized_string == "return":
            self.current_token = self.get_token()
            E_place = self.expression()
            self.icg.genquad("ret", E_place, "_", "_")
        else:
            self.error(f"Error at line {self.current_token.line_number}: Expected 'return' at the beginning of return statement")
    
    def actualpars(self):
        if self.current_token.recognized_string == "(":
            self.current_token = self.get_token()
            self.actualparlist()
            if self.current_token.recognized_string == ")":
                self.current_token = self.get_token()
            else:
                self.error(f"Error at line {self.current_token.line_number}: Expected ')' at the end of actual parameter list in function call")
        else:
            self.error(f"Error at line {self.current_token.line_number}: Expected '(' at the beginning of actual parameter list in function call")
    
    def actualparlist(self):
        if self.current_token.recognized_string != ")":
            self.actualparitem()
        while self.current_token.recognized_string == ",":
            self.current_token = self.get_token()
            self.actualparitem()
    
    def actualparitem(self):
        if self.current_token.recognized_string == "in":
            self.current_token = self.get_token()
            place = self.expression()
            self.icg.genquad("par", place, "CV", "_")
        elif self.current_token.recognized_string == "inout":
            self.current_token = self.get_token()
            if self.current_token.family == "identifier":
                place = self.current_token.recognized_string
                self.symTable.search_entity(place)
                self.current_token = self.get_token()
                self.icg.genquad("par", place, "REF", "_")
            else:
                self.error(f"Error at line {self.current_token.line_number}: Expected identifier after 'inout' in actual parameter declaration")
        else:
            self.error(f"Error at line {self.current_token.line_number}: Expected 'in' or 'inout' at the beginning of actual parameter declaration")
        
    
    def condition(self):
        Q_true, Q_false = self.boolterm()
        while self.current_token.recognized_string == "or":

            self.icg.backpatch(Q_false, self.icg.nextquad())

            self.current_token = self.get_token()
            R_true, R_false = self.boolterm()
            Q_true = self.icg.merge(Q_true, R_true)
            Q_false = R_false   
        return Q_true, Q_false
    
    def boolterm(self):
        Q_true, Q_false = self.boolfactor()
        while self.current_token.recognized_string == "and":

            self.icg.backpatch(Q_true, self.icg.nextquad())

            self.current_token = self.get_token()

            R_true, R_false = self.boolfactor()
            Q_false = self.icg.merge(Q_false, R_false)
            Q_true = R_true
        return Q_true, Q_false
    
    def boolfactor(self):
        if self.current_token.recognized_string == "not":
            self.current_token = self.get_token()
            if self.current_token.recognized_string == "[":
                self.current_token = self.get_token()
                B_true, B_false = self.condition()
                if self.current_token.recognized_string == "]":
                    self.current_token = self.get_token()
                else:
                    self.error(f"Error at line {self.current_token.line_number}: Expected ']' after condition in 'not' expression")
                
                return B_false, B_true
            else:
                self.error(f"Error at line {self.current_token.line_number}: Expected '[' after 'not' in 'not' expression")
        elif self.current_token.recognized_string == "[":
            self.current_token = self.get_token()

            B_true, B_false = self.condition()
            if self.current_token.recognized_string == "]":
                self.current_token = self.get_token()
            else:
                self.error(f"Error at line {self.current_token.line_number}: Expected ']' after condition in boolean expression")

            return B_true, B_false
        else:
            E1_place = self.expression()
            relop = self.relational_oper()
            E2_place = self.expression()
            B_true = self.icg.makelist(self.icg.nextquad())
            self.icg.genquad(relop, E1_place, E2_place, "_")
            B_false = self.icg.makelist(self.icg.nextquad())
            self.icg.genquad("jump", "_", "_", "_")
            return B_true, B_false

    def expression(self):
        sign = self.optional_sign()
        T1_place = self.term()
        if sign == "-":
            t = self.icg.newtemp()
            self.symTable.add_entity(t, "TEMP")
            self.icg.genquad("-", "0", T1_place, t)
            T1_place = t
        while self.current_token.recognized_string in add_oper:
            oper = self.current_token.recognized_string
            self.current_token = self.get_token()
            T2_place = self.term()
            t = self.icg.newtemp()
            self.symTable.add_entity(t, "TEMP")
            self.icg.genquad(oper, T1_place, T2_place, t)
            T1_place = t
        return T1_place
    
    def term(self):
        F1_place = self.factor()
        while self.current_token.recognized_string in mul_oper:
            oper = self.current_token.recognized_string
            self.current_token = self.get_token()
            F2_place = self.factor()
            t = self.icg.newtemp()
            self.symTable.add_entity(t, "TEMP")
            self.icg.genquad(oper, F1_place, F2_place, t)
            F1_place = t
        return F1_place

    def factor(self):
        if self.current_token.family == "integer_literal":
            place = self.current_token.recognized_string
            self.current_token = self.get_token()
            return place
        elif self.current_token.recognized_string == "(":
            self.current_token = self.get_token()
            place = self.expression()
            if self.current_token.recognized_string == ")":
                self.current_token = self.get_token()
            else:
                self.error(f"Error at line {self.current_token.line_number}: Expected ')' after expression in factor")
            return place
        elif self.current_token.family == "identifier":
            id_name = self.current_token.recognized_string
            self.symTable.search_entity(id_name)
            self.current_token = self.get_token()
            place = self.idtail(id_name)
            return place
        else:
            self.error(f"Error at line {self.current_token.line_number}: Expected integer literal, identifier, or '(' at the beginning of factor")
    
    def idtail(self,id_name):
        if self.current_token.recognized_string == "(":
            self.actualpars()
            t = self.icg.newtemp()
            self.symTable.add_entity(t, "TEMP")
            self.icg.genquad("par", t, "RET", "_")
            self.icg.genquad("call", id_name, "_", "_")
            return t
        else:
            return id_name
    
    def optional_sign(self):
        sign = ""

        if self.current_token.recognized_string in add_oper:
            sign = self.current_token.recognized_string
            self.current_token = self.get_token()
        return sign
    
    def relational_oper(self):
        if self.current_token.recognized_string in relational_oper:
            relop = self.current_token.recognized_string
            self.current_token = self.get_token()
            return relop
        else:
            self.error(f"Error at line {self.current_token.line_number}: Expected a relational operator in condition")

class IntermediateCodeGenerator:
    def __init__(self):
        self.quads = []
        self.label = 1
        self.symTable = SymbolTable()
        
    #generate a quad and add it to the list of quads
    def genquad(self, operator, arg1, arg2, result):
        quad = [self.label, operator, arg1, arg2, result]
        self.quads.append(quad)
        self.label += 1
        return quad

    #return the number of the next quad
    def nextquad(self):
        return self.label
    
    def emptylist(self):
        return []
    
    #create a list with a single label
    def makelist(self, label):
        return [label]
    
    #merge two lists of labels
    #maybe remove duplicates?
    def merge(self, list1, list2):
        return list1 + list2
    
    #add a label to the end of each quad in the list
    def backpatch(self, quad_list, label):
        for quad_id in quad_list:
            self.quads[quad_id - 1][4] = str(label)

    #create temp value t_lastquadnumber
    def newtemp(self):
        temp_name = f"t_{len(self.quads)}"
        return temp_name

class SymbolTable:
    def __init__(self):
        self.current_level = 0
        self.scope_stack = []
        self.offset = 12
        self.sym_output = []
    
    def error(self, message):
        print(message)
        sys.exit(1)
    
    def add_scope(self):
        scope = {
            "level": self.current_level,
            "offset": self.offset,
            "entities": {}
        }
        self.scope_stack.append(scope)
        self.current_level += 1
        
    
    def remove_scope(self):
        if self.current_level == 0:
            self.error("Error: Cannot remove global scope")
        self.print_scope()
        closing_scope = self.scope_stack.pop()
        self.current_level -= 1
        if len(self.scope_stack) > 0:
            parent_scope = self.scope_stack[-1]
            parent_entities = list(parent_scope["entities"].values())
            if parent_entities:
                last_entity = parent_entities[-1]
                if last_entity["type"] == "FUNC":
                    last_entity['framelength'] = closing_scope['offset']
        
    def add_entity(self, name, entity_type, parMode=None):
        current_scope = self.scope_stack[-1]
        if name in current_scope["entities"]:
            self.error(f"Error: Entity '{name}' already declared in the current scope")
        else:
            entity = {
                "name": name,
                "type": entity_type,
                #"parMode": parMode,
                "datatype": "int"
            }
            if entity_type in ["VAR", "TEMP", "PARAM"]:
                entity["offset"] = current_scope["offset"]
                current_scope["offset"] += 4
            if entity_type == "FUNC":
                entity["start_quad"] = None
                entity["framelength"] = 0
                entity["arguments"] = []
            if entity_type == "PARAM":
                entity["parMode"] = parMode
                if len(self.scope_stack) > 1:
                    parent_scope = self.scope_stack[-2]
                    last_function = list(parent_scope["entities"].values())[-1]
                    if last_function["type"] == "FUNC":
                        last_function["arguments"].append(parMode)
            current_scope["entities"][name] = entity

    def search_entity(self, name):
        for scope in reversed(self.scope_stack):
            if name in scope["entities"]:
                #nested_differnce = (self.current_level - 1) - scope['level']
                return scope["entities"][name], scope['level']
        self.error(f"Error: Entity '{name}' not declared in any scope")

    def update_start_quad(self, func_name, start_quad):
        entity, _ = self.search_entity(func_name)
        if entity and entity['type'] == 'FUNC':
            entity['start_quad'] = start_quad
    
    def print_scope(self):
        scope = self.scope_stack[-1]
        output_text = f"\n--- Scope (Level {scope['level']}) ---\n"
        for name, data in scope['entities'].items():
            if data['type'] == 'FUNC':
                output_text += f"FUNC: {name}, framelength: {data.get('framelength')}, args: {data.get('arguments')}\n"
            elif data['type'] == 'PARAM':
                output_text += f"PARAM: {name}, mode: {data.get('parMode')}, offset: {data['offset']}\n"
            else:
                output_text += f"{data['type']}: {name}, offset: {data['offset']}\n"
        output_text += "--------------------------------------\n"
        self.sym_output.append(output_text)

class FinalCodeGenerator:
    def __init__(self, quads, symbol_table, is_main=False):
        self.quads = quads
        self.symbol_table = symbol_table
        self.asm = [] 
        self.current_func_level = self.symbol_table.current_level - 1
        self.current_par_offset = 12
        self.is_main = is_main

    def gnlvcode(self, name):
        entity, level = self.symbol_table.search_entity(name)
        self.asm.append(f"    lw t0, -4(sp)")

        for _ in range(self.current_func_level - level - 1):
            self.asm.append(f"    lw t0, -4(t0)")
    
        return entity, level

    def loadVR(self, v, r):
        if str(v).isdigit() or (str(v).startswith('-') and str(v)[1:].isdigit()):
            self.asm.append(f"    li {r}, {v}")
            return

        entity, level = self.symbol_table.search_entity(v)
        offset = entity['offset']

        if level == 0:
            self.asm.append(f"    lw {r}, -{offset}(gp)")
        elif level == self.current_func_level:
            if entity['type'] == 'PARAM' and entity.get('parMode') == 'REF':
                self.asm.append(f"    lw t0, -{offset}(sp)")
                self.asm.append(f"    lw {r}, (t0)")       
            else:
                self.asm.append(f"    lw {r}, -{offset}(sp)")
        else:
            self.gnlvcode(v)
            if entity['type'] == 'PARAM' and entity.get('parMode') == 'REF':
                self.asm.append(f"    lw t0, -{offset}(t0)")
                self.asm.append(f"    lw {r}, (t0)")     
            else:
                self.asm.append(f"    lw {r}, -{offset}(t0)")

    def storeVR(self, r, v):
        entity, level = self.symbol_table.search_entity(v)
        offset = entity['offset']

        if level == 0:
            self.asm.append(f"    sw {r}, -{offset}(gp)")
        elif level == self.current_func_level:
            if entity['type'] == 'PARAM' and entity.get('parMode') == 'REF':
                self.asm.append(f"    lw t0, -{offset}(sp)")
                self.asm.append(f"    sw {r}, (t0)")      
            else:
                self.asm.append(f"    sw {r}, -{offset}(sp)")
        else:
            self.gnlvcode(v)
            if entity['type'] == 'PARAM' and entity.get('parMode') == 'REF':
                self.asm.append(f"    lw t0, -{offset}(t0)")
                self.asm.append(f"    sw {r}, (t0)")    
            else:
                self.asm.append(f"    sw {r}, -{offset}(t0)")
    
    def load_address(self, v, r):
        entity, level = self.symbol_table.search_entity(v)
        offset = entity['offset']

        if level == 0:
            self.asm.append(f"    addi {r}, gp, -{offset}")
        elif level == self.current_func_level:
            if entity['type'] == 'PARAM' and entity.get('parMode') == 'REF':
                self.asm.append(f"    lw {r}, -{offset}(sp)")
            else:
                self.asm.append(f"    addi {r}, sp, -{offset}")
        else:
            self.gnlvcode(v)
            if entity['type'] == 'PARAM' and entity.get('parMode') == 'REF':
                self.asm.append(f"    lw {r}, -{offset}(t0)")
            else:
                self.asm.append(f"    addi {r}, t0, -{offset}")

    def generate(self):
        for quad in self.quads:
            label = quad[0]
            op = quad[1]
            arg1 = str(quad[2])
            arg2 = str(quad[3])
            res = str(quad[4])

            self.asm.append(f"L{label}:")

            if op == 'begin_block':
                self.framelength = self.symbol_table.scope_stack[-1]['offset']
                if not self.is_main:
                    self.asm.append("    sw ra, (sp)")
                else:
                    self.asm.append(f"    addi sp, sp, {self.framelength}")
                    self.asm.append("    mv gp, sp")
            elif op == 'end_block':
                if not self.is_main:
                    self.asm.append("    lw ra, (sp)")
                    self.asm.append("    jr ra")
            elif op == 'jump':
                self.asm.append(f"    j L{res}")
            elif op == ':=':
                self.loadVR(arg1, 't1')
                self.storeVR('t1', res)
            elif op == '+':
                self.loadVR(arg1, 't1')
                self.loadVR(arg2, 't2')
                self.asm.append("    add t1, t1, t2")
                self.storeVR('t1', res)
            elif op == '-':
                self.loadVR(arg1, 't1')
                self.loadVR(arg2, 't2')
                self.asm.append("    sub t1, t1, t2")
                self.storeVR('t1', res)
            elif op == '*':
                self.loadVR(arg1, 't1')
                self.loadVR(arg2, 't2')
                self.asm.append("    mul t1, t1, t2")
                self.storeVR('t1', res)
            elif op == '/':
                self.loadVR(arg1, 't1')
                self.loadVR(arg2, 't2')
                self.asm.append("    div t1, t1, t2")
                self.storeVR('t1', res)
            elif op == '=':
                self.loadVR(arg1, 't1')
                self.loadVR(arg2, 't2')
                self.asm.append(f"    beq t1, t2, L{res}")
            elif op == '<>':
                self.loadVR(arg1, 't1')
                self.loadVR(arg2, 't2')
                self.asm.append(f"    bne t1, t2, L{res}")
            elif op == '<':
                self.loadVR(arg1, 't1')
                self.loadVR(arg2, 't2')
                self.asm.append(f"    blt t1, t2, L{res}")
            elif op == '>':
                self.loadVR(arg1, 't1')
                self.loadVR(arg2, 't2')
                self.asm.append(f"    bgt t1, t2, L{res}")
            elif op == '<=':
                self.loadVR(arg1, 't1')
                self.loadVR(arg2, 't2')
                self.asm.append(f"    ble t1, t2, L{res}")
            elif op == '>=':
                self.loadVR(arg1, 't1')
                self.loadVR(arg2, 't2')
                self.asm.append(f"    bge t1, t2, L{res}")
            elif op == 'par':
                self.asm.append(f"    addi fp, sp, {self.framelength}")
                if arg2 == 'CV':
                    self.loadVR(arg1, 't0')
                    self.asm.append(f"    sw t0, -{self.current_par_offset}(fp)")
                    self.current_par_offset += 4
                elif arg2 == 'REF':
                    self.load_address(arg1, 't0')
                    self.asm.append(f"    sw t0, -{self.current_par_offset}(fp)")
                    self.current_par_offset += 4   
                elif arg2 == 'RET':
                    self.load_address(arg1, 't0')
                    self.asm.append(f"    sw t0, -8(fp)")
            elif op == 'call':
                entity, f_level = self.symbol_table.search_entity(arg1)
                framelength = self.symbol_table.scope_stack[-1]['offset']
                self.asm.append(f"    addi fp, sp, {framelength}")

                if f_level == self.current_func_level:
                    self.asm.append("    sw sp, -4(fp)")
                else: 
                    self.asm.append("    lw t0, -4(sp)")
                    for _ in range(self.current_func_level - f_level - 1):
                        self.asm.append("    lw t0, -4(t0)")
                    self.asm.append("    sw t0, -4(fp)")

                self.asm.append(f"    addi sp, sp, {framelength}")
                self.asm.append(f"    jal L{entity['start_quad']}")
                self.asm.append(f"    addi sp, sp, -{framelength}")
                self.current_par_offset = 12
            elif op == 'ret':
                self.loadVR(arg1, 't1')
                self.asm.append("    lw t0, -8(sp)")
                self.asm.append("    sw t1, (t0)")
            elif op == 'out':
                self.loadVR(arg1, 't1')
                self.asm.append("    li a7, 1")
                self.asm.append("    mv a0, t1")
                self.asm.append("    ecall")
            elif op == 'inp':
                self.asm.append("    li a7, 5")
                self.asm.append("    ecall")
                self.asm.append("    mv t1, a0")
                self.storeVR('t1', arg1)
            elif op == 'halt':
                self.asm.append("    li a0, 0")
                self.asm.append("    li a7, 93")       
                self.asm.append("    ecall")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python part1.py <filename>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    if not input_file.endswith(".c++"):
        print("Error: Input file must have a .c++ extension")
        sys.exit(1)

    lexer = Lexer(input_file)
    lexer.tokenize()
    parser = Parser(lexer)
    parser.run()

    output_file_int = input_file[:-4] + ".int"
    output_file_sym = input_file[:-4] + ".sym"
    output_file_asm = input_file[:-4] + ".asm"

    try:
        with open(output_file_int, "w") as f:
            for quad in parser.icg.quads:
                f.write(f"{quad[0]}: {quad[1]}, {quad[2]}, {quad[3]}, {quad[4]}\n")
    except IOError:
        print(f"Error: Could not write to file {output_file_int}")
        sys.exit(1)
    try:
        with open(output_file_sym, "w") as f:
            for scope_output in parser.symTable.sym_output:
                f.write(scope_output)
    except IOError:
        print(f"Error: Could not write to file {output_file_sym}")
        sys.exit(1)
    try:
        with open(output_file_asm, "w") as f:
            main_quad = None
            for quad in parser.icg.quads:
                if quad[1] == 'begin_block' and quad[2] == parser.program_name: 
                    main_quad = quad[0]
                    break
        
            if main_quad:
                f.write(".globl main\n")
                f.write(".text\n")
                f.write("main:\n")
                parser.asm_code[0] = f"    j L{main_quad}"
            for line in parser.asm_code:
                f.write(f"{line}\n")
    except IOError:
        print(f"Error: Could not write to file {output_file_asm}")
        sys.exit(1)