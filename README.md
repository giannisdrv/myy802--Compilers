# case++ Compiler

## Overview
This repository contains a complete compiler for the **case++** programming language, developed as part of the "Compilers" course at the University of Ioannina. Written entirely in Python (`met.py`), the compiler processes case++ source code to perform lexical and syntax analysis, semantic checking, and ultimately translates it into intermediate code, a scope-aware symbol table, and final RISC-V assembly code.

## The case++ Programming Language
**case++** is an educational programming language designed specifically for learning compiler construction. While intentionally lacking some standard features (like traditional `for` loops or floating-point numbers), it presents unique compilation challenges by supporting:
* **Functions & Recursion:** Full support for recursive function calls.
* **Nested Functions:** Functions can be declared inside other functions, following Pascal-like lexical scoping rules.
* **Parameter Passing:** Supports passing arguments both by value (`in`) and by reference (`inout`).
* **Unique Control Structures:** Introduces special composite control structures like `switchcase`, `whilecase`, `incase`, `forcase`, and `untilcase`.
* **File Extension:** Source files use the `.c++` extension.

## Compiler Architecture
The compiler is implemented in `met.py` and follows a classic multi-pass compilation pipeline:

1. **Lexical Analyzer (Lexer):** Reads the source code character by character, filtering out whitespaces and comments, and groups the remaining characters into a stream of valid tokens.
2. **Syntax Analyzer (Parser):** Consumes tokens using a Top-Down Recursive Descent parsing technique, strictly enforcing the rules defined in `case++_grammar.txt`.
3. **Intermediate Code Generator (ICG):** Generates intermediate code in the form of **Quadruples** (e.g., `[op, arg1, arg2, result]`).
4. **Symbol Table Manager:** Tracks entities such as variables, functions, and parameters across dynamic nested scopes, keeping record of their memory offsets and nesting levels.
5. **Final Code Generator:** Translates intermediate quadruples into **RISC-V Assembly** language, handling memory allocation for the Activation Records (call stacks) of nested and recursive functions.

---

## Usage

### Prerequisites
* **Python 3.x** (for running the compiler)
* **Java Runtime Environment (JRE)** (for running the RARS emulator)

### 1. Compiling case++ Code
To compile a case++ source file, execute the script via the command line and pass the source file as an argument:

```bash
python met.py <source_file.c++>
```

#### Generated Output
Upon successful compilation, three distinct files are generated in the same directory:
* `<source_file>.int`: Contains the generated Intermediate Code (Quadruples).
* `<source_file>.sym`: Contains a text dump of the Symbol Table showing scopes, nesting levels, and entity offsets.
* `<source_file>.asm`: Contains the target **RISC-V Assembly Code** ready for emulation.

---

## Executing the Final Code (Using RARS)

The generated `.asm` file targets the RISC-V architecture and can be executed using the **RARS (RISC-V Assembler and Runtime Simulator)** tool provided in this repository (`rars_46ab74d.jar`).

### Method A: Graphical Interface (GUI)
1. Open the simulator by double-clicking the `rars_46ab74d.jar` file or running the following command:
   ```bash
   java -jar rars_46ab74d.jar
   ```
2. Go to **File -> Open** and select your generated `<source_file>.asm` file.
3. Click the **Assemble** icon (the wrench and screwdriver tool) or press **F3** to compile the assembly into machine code.
4. Use the **Run** icon (the green play button) or press **F5** to execute the program. You can interact with any input/output operations in the integrated **Run I/O** tab at the bottom.

### Method B: Command Line Interface (CLI)
To run the code directly inside your terminal without opening the graphical interface, use the `nc` (no copyright notice) flag:

```bash
java -jar rars_46ab74d.jar nc <source_file>.asm
```

---

## Author
* **Ioannis Drivas**
* University of Ioannina, Department of Computer Science and Engineering
