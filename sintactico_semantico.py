import sys

from lexico import gen_tokens
from tabla_de_simbolos import Entry

tokens, tabla = gen_tokens(sys.argv[1])
# print tokens

gramar = open("gramarSintactico.txt", "w")
gramar.write('''Axioma = S

NoTerminales = { S B T E E1 E2 M O P V V1 R}

Terminales = { var id write ( ) { } int chars cte-ent cadena function while return |= = + - ; == && , }

Producciones = {
S -> var T id ; S //// 1
S -> id B E ; S //// 2
S -> write ( E ) ; S //// 3
S -> while ( E1 ) { P } S //// 4
S -> if ( E1 ) { P } S //// 5
S -> function T id ( V ){ P R } S //// 6
T -> int | chars //// 7, 8
E -> cte-ent M | cadena M | id M //// 9, 10, 11
E1 -> E == E E2 //// 12
E2 -> && E1 | lambda //// 13, 14
M -> O E | lambda //// 15, 16
O -> + | - //// 17, 18
B -> = | |= //// 19, 20
V -> T id V1 //// 21
V1 -> , V | lambda //// 22, 23
R -> return E ; | lambda //// 24, 25
}''')
error_sintactico = open("errorSintactico.txt", "w")
error_semantico = open("errorSemantico.txt", "w")
parse = open("parse.txt", "w")


class Syntactic(object):
    def __init__(self):
        self.tokens = tokens
        self.tablaSimbolos = tabla
        self.token = self.tokens.pop(0)
        self.tipo = "no"
        self.ret = "no"
        parse.write("Des ")

    def s(self):
        self.tipo = "no"
        if self.token[0] == "PR":
            if self.token[1].name == "var":
                parse.write("1 ")
                self.token = self.tokens.pop(0)
                self.t()
                if self.token[1] == ";":
                    error_sintactico.write("ERROR: falta id para asignarle un tipo")
                    exit(-1)
                self.asignar_tipo(self.token[1], self.tipo)
                self.token = self.tokens.pop(0)
                if self.token[1] == ";":
                    self.token = self.tokens.pop(0)
                    return self.s()
                else:
                    error_sintactico.write("ERROR: falta punto y coma en la declaracion de variables \n")
                    exit(-1)

            elif self.token[1].name == "write":
                parse.write("3 ")
                self.token = self.tokens.pop(0)
                if self.token[1] == "(":
                    self.token = self.tokens.pop(0)
                    self.e_aux()
                    if self.token[1] == ")":
                        self.token = self.tokens.pop(0)
                        if self.token[1] == ";":
                            self.token = self.tokens.pop(0)
                            return self.s()
                        else:
                            error_sintactico.write("ERROR: falta punto y coma en el write \n")
                            exit(-1)
                    else:
                        error_sintactico.write("ERROR: falta cerrar parentesis en el write \n")
                        exit(-1)
                else:
                    error_sintactico.write("ERROR: falta abrir parentesis en el write \n")
                    exit(-1)
            elif self.token[1].name == "while":
                parse.write("4 ")
                self.token = self.tokens.pop(0)
                if self.token[1] == "(":
                    self.token = self.tokens.pop(0)
                    self.e1()
                    if self.token[1] == ")":
                        self.token = self.tokens.pop(0)
                        if self.token[1] == "{":
                            self.token = self.tokens.pop(0)
                            self.s()
                            if self.token[1] == "}":
                                self.token = self.tokens.pop(0)
                                return self.s()
                            else:
                                error_sintactico.write("ERROR: falta cerrar corchete en el while \n")
                                exit(-1)
                        else:
                            error_sintactico.write("ERROR: falta abrir corchete en el while \n")
                            exit(-1)
                    else:
                        error_sintactico.write("ERROR: falta cerrar parentesis en el while \n")
                        exit(-1)
                else:
                    error_sintactico.write("ERROR: falta abrir parentesis en el while \n")
                    exit(-1)
            elif self.token[1].name == "if":
                parse.write("5 ")
                self.token = self.tokens.pop(0)
                if self.token[1] == "(":
                    self.token = self.tokens.pop(0)
                    self.e1()
                    if self.token[1] == ")":
                        self.token = self.tokens.pop(0)
                        if self.token[1] == "{":
                            self.token = self.tokens.pop(0)
                            self.s()
                            if self.token[1] == "}":
                                self.token = self.tokens.pop(0)
                                return self.s()
                            else:
                                error_sintactico.write("ERROR: falta cerrar corchete en el if \n")
                                exit(-1)
                        else:
                            error_sintactico.write("ERROR: falta abrir corchete en el if \n")
                            exit(-1)
                    else:
                        error_sintactico.write("ERROR: falta cerrar parentesis en el if \n")
                        exit(-1)
                else:
                    error_sintactico.write("ERROR: falta abrir parentesis en el if \n")
                    exit(-1)
            elif self.token[1].name == "return":
                if self.ret != "no":
                    parse.write("24 ")
                    self.token = self.tokens.pop(0)
                    self.tipo = self.ret
                    self.e()
                    if self.token[1] == ";":
                        self.token = self.tokens.pop(0)
                    else:
                        error_sintactico.write("ERROR: falta punto y coma tras el return \n")
                        exit(-1)
                else:
                    error_semantico.write("ERROR: no puedes usar return si no se esta en una funcion \n")
                    exit(-1)
            elif self.token[1].name == "function":
                parse.write("6 ")
                self.token = self.tokens.pop(0)
                self.t()
                if self.token[0] == "id":
                    if self.token[1].type == "no":
                        fun = self.token[1]
                        fun.type = self.tipo
                        self.ret = fun.type
                        self.token = self.tokens.pop(0)
                        if self.token[1] == "(":
                            self.token = self.tokens.pop(0)
                            if self.token[1] != ")":
                                ini = list()
                                result = self.v(ini)
                                self.asignar_tipo(fun, fun.type, result)
                            # usar result para la tabla de simbolos y demas
                            if self.token[1] == ")":
                                self.token = self.tokens.pop(0)
                                if self.token[1] == "{":
                                    self.token = self.tokens.pop(0)
                                    self.s()
                                    if self.token[1] == "}":
                                        if self.ret == "no":
                                            parse.write("25 ")
                                        self.token = self.tokens.pop(0)
                                        self.ret = "no"
                                        return self.s()
                                    else:
                                        error_sintactico.write("ERROR: falta cerrar corchete en el function \n")
                                        exit(-1)
                                else:
                                    error_sintactico.write("ERROR: falta abrir corchete en el function \n")
                                    exit(-1)
                            else:
                                error_sintactico.write("ERROR: falta cerrar parentesis en function \n")
                                exit(-1)
                        else:
                            error_sintactico.write("ERROR: falta abrir parentesis en function \n")
                            exit(-1)
                    else:
                        error_semantico.write("ERROR: variable ya declarada, no puede ser funcion \n")
                        exit(-1)
                else:
                    error_sintactico.write("ERROR: se necesita id para la funcion \n")
                    exit(-1)
            else:
                error_sintactico.write("ERROR: palabra reservada no conocida: " + self.token[1].name + "\n")
                exit(-1)
        elif self.token[0] == "id":
            parse.write("2 ")
            if self.token[1].type != "no":
                self.tipo = self.token[1].type
                self.token = self.tokens.pop(0)
                if self.token[1] == "|":
                    parse.write("20 ")
                    self.token = self.tokens.pop(0)
                    self.token = self.tokens.pop(0)
                elif self.token[1] == "=":
                    parse.write("19 ")
                    self.token = self.tokens.pop(0)
                else:
                    error_sintactico.write("ERROR: operador de asignacion no aceptado \n")
                    exit(-1)
                if self.token[1] == ";":
                    error_sintactico.write("ERROR: falta segundo operando en la asignacion \n")
                    exit(-1)
                self.e()
                if self.token[1] == ";":
                    self.token = self.tokens.pop(0)
                    return self.s()
                else:
                    error_sintactico.write("ERROR: falta punto y coma en la asignacion \n")
                    exit(-1)
            else:
                error_semantico.write("ERROR: variable no declarada \n")
                exit(-1)
        elif self.token[0] == "fin":
            print "Fichero analizado correctamente"
            exit(0)
        elif self.token[1] == "}":
            pass
        else:
            error_sintactico.write("ERROR: inicio de axioma desconocido \n")
            print self.token
            exit(-1)

    def v(self, result):
        parse.write("21 ")
        if self.token[1].name == "int":
            parse.write("7 ")
            type = self.token[1].name
            self.token = self.tokens.pop(0)
            if self.token[0] == "id":
                entry = self.asignar_tipo(self.token[1], type, 1)
                result.append(self.tablaSimbolos.search_index(entry))
                self.token = self.tokens.pop(0)
                if self.token[1] == ",":
                    self.token = self.tokens.pop(0)
                    parse.write("22 ")
                    return self.v(result)
                elif self.token[1] == ")":
                    parse.write("23 ")
                    return result
                else:
                    error_sintactico.write("ERROR: simbolo incorrecto en los parametros \n")
                    exit(-1)
            else:
                error_sintactico.write("ERROR: los parametros tienen que ser ids \n")
                exit(-1)
        elif self.token[1].name == "chars":
            parse.write("8 ")
            type = self.token[1].name
            self.token = self.tokens.pop(0)
            if self.token[0] == "id":
                entry = self.asignar_tipo(self.token[1], type, 1)
                result.append(self.tablaSimbolos.search_index(entry))
                self.token = self.tokens.pop(0)
                if self.token[1] == ",":
                    self.token = self.tokens.pop(0)
                    parse.write("22 ")
                    return self.v(result)
                elif self.token[1] == ")":
                    parse.write("23 ")
                    return result
                else:
                    error_sintactico.write("ERROR: simbolo incorrecto en los parametros \n")
                    exit(-1)
            else:
                error_sintactico.write("ERROR: los parametros tienen que ser ids \n")
                exit(-1)

        else:
            error_sintactico.write("ERROR: tipo no definido \n")
            exit(-1)

    def e(self):
        if self.token[0] == "id":
            parse.write("11 ")
            if self.token[1].type == self.tipo:
                self.token = self.tokens.pop(0)
            else:
                error_semantico.write(
                    "ERROR: no puedes asignar un tipo " + self.token[1].type + " a un tipo " + self.tipo)
                exit(-1)
        elif self.token[0] == 'int':
            parse.write("9 ")
            if self.token[0] == self.tipo:
                self.token = self.tokens.pop(0)
            else:
                error_semantico.write("ERROR: no puedes asignar un tipo " + self.token[0] + " a un tipo " + self.tipo)
                exit(-1)
        elif self.token[0] == "chars":
            parse.write("10 ")
            if self.token[0] == self.tipo:
                self.token = self.tokens.pop(0)
            else:
                error_semantico.write("ERROR: no puedes asignar un tipo " + self.token[0] + " a un tipo " + self.tipo)
                exit(-1)
        if self.token[1] == "+":
            parse.write("15 ")
            parse.write("17 ")
            self.token = self.tokens.pop(0)
            return self.e()
        elif self.token[1] == "-":
            parse.write("15 ")
            parse.write("18 ")
            self.token = self.tokens.pop(0)
            return self.e()
        else:
            parse.write("16 ")
        #intentar tratar el caso de error para otros operadores

    def e1(self):
        parse.write("12 ")
        self.e_aux()
        if self.token[1] == "=":
            self.token = self.tokens.pop(0)
            if self.token[1] == "=":
                self.token = self.tokens.pop(0)
                if self.token[1] == ")" or self.token[1] == "&&":
                    error_sintactico.write("ERROR: falta segundo operando de la comparacion \n")
                    exit(-1)
                self.e()
                if self.token[1] == "&&":
                    parse.write("13 ")
                    self.token = self.tokens.pop(0)
                    return self.e1()
                parse.write("14 ")
            else:
                error_sintactico.write("ERROR: operador de comparacion desconocido. \n")
                exit(-1)
        else:
            error_sintactico.write("ERROR: operador de comparacion desconocido. \n")
            exit(-1)

    def e_aux(self):
        if self.token[0] == "id":
            parse.write("11 ")
            if self.token[1].type != "no":
                self.tipo = self.token[1].type
                self.token = self.tokens.pop(0)
                return self.e()
            else:
                error_semantico.write("ERROR: variable no declarada \n")
                exit(-1)
        elif self.token[0] == "int":
            parse.write("9 ")
            self.tipo = self.token[0]
            self.token = self.tokens.pop(0)
            return self.e()
        elif self.token[0] == "chars":
            parse.write("10 ")
            self.tipo = self.token[0]
            self.token = self.tokens.pop(0)
            return self.e()
        else:
            error_sintactico.write("ERROR: tipo no conocido \n")
            exit(-1)

    def t(self):
        if self.token[1].name == "int":
            parse.write("7 ")
            self.tipo = "int"
            self.token = self.tokens.pop(0)
        elif self.token[1].name == "chars":
            parse.write("8 ")
            self.tipo = "chars"
            self.token = self.tokens.pop(0)
        else:
            error_sintactico.write("ERROR: tipo no conocido \n")
            exit(-1)

    def asignar_tipo(self, entry, tipo, argum=0):
        self.tablaSimbolos.erase(entry)
        entry.type = tipo
        entry.argum = argum
        if tipo == "int":
            entry.desp = 2
        else:
            entry.desp = 16
        self.tablaSimbolos.insert(entry)
        return entry


def main():
    print "Fichero generado: gramarSintactico.txt"
    print "Fichero generado: errorSintactico.txt"
    print "Fichero generado: errorSemantico.txt"

    Syntactic().s()


if __name__ == '__main__':
    main()