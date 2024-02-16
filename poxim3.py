import sys


def load_memory_from_hex_file(file_path, MEM8, MEM32):
    with open(file_path, 'r') as file:
        lines = file.readlines()
        for i, line in enumerate(lines):
            stripped_line = line.strip()
            if stripped_line.startswith("0x"):
                hex_value = stripped_line[2:]
                mem_value = int(hex_value, 16)
                MEM8[i*4: i*4+4] = mem_value.to_bytes(4, byteorder='big')
                MEM32[i] = mem_value

def main(args):
    print("Quantidade de argumentos (len(args)): " + str(len(args)))
    for i, arg in enumerate(args):
        print("Argumento " + str(i) + " (args[" + str(i) + "]): " + arg)
    entrada = open(sys.argv[1], "r")
    sys.stdout = open(sys.argv[2], 'w')
    
    # Inicializando os registradores
    R = [0] * 32
    R[28] = 0  # Registrador de instrução (IR)
    R[29] = 0  # Contador de programa (PC)
    R[30] = 0  # Ponteiro de pilha (SP)
    R[31] = 0  # Registrador de status (SR)
    address = 0
    # Inicializando a memória
    MEM8 = bytearray(8 * 1024)
    MEM32 = [0] * (32 * 1024)

    # Carregar arquivo .hex na memória
    load_memory_from_hex_file(sys.argv[1], MEM8, MEM32)

    # Exibindo a inicialização da execução
    print("[START OF SIMULATION]")

    # Setando a condição de execução para verdadeiro
    executa = True
    ZN = 0
    ZD = 0
    SN = 0
    OV = 0
    IV = 0
    CY = 0
    IE = 0
    EN = 0
    SR = 0


    def sr():
        flags_changed = ZN != 0 or ZD != 0 or SN != 0 or OV != 0 or IV != 0 or IE != 0 or CY != 0
        if flags_changed:
            SR = (ZN << 6) | (ZD << 5) | (SN << 4) | (
                OV << 3) | (IV << 2) | (IE << 1) | CY


    rs = {
    0: "r0",
    1: "r1",
    2: "r2",
    3: "r3",
    4: "r4",
    5: "r5",
    6: "r6",
    7: "r7",
    8: "r8",
    9: "r9",
    10: "r10",
    11: "r11",
    12: "r12",
    13: "r13",
    14: "r14",
    15: "r15",
    16: "r16",
    17: "r17",
    18: "r18",
    19: "r19",
    20: "r20",
    21: "r21",
    22: "r22",
    23: "r23",
    24: "r24",
    25: "r25",
    26: "r26",
    27: "r27",
    28: "r28",
    29: "r29",
    30: "r30",
    31: "r31"
    }


    terminal = []
    terminal.append('[TERMINAL]\n')

    valores_originais = [None] * 32
    counter_ID = False
    counter = None

    opcode_fpu = 0
    x_fpu = 0
    y_fpu = 0
    z_fpu = 0
    status_fpu = 0

    verificacoes_verdadeiras = 0


    def fpu(opcode_fpu, status_fpu, x_fpu, y_fpu, z_fpu):
        expoente_x = (x_fpu & (0xFF << 23) >> 23)
        expoente_y = (y_fpu & (0xFF << 23) >> 23)
        expoente = abs(expoente_x - expoente_y) + 1

    if opcode_fpu == 0b0001:  # 1 adição
        z_fpu = float(x_fpu + y_fpu)
        print("[HARDWARE INTERRUPTION 3]")
        R[29] = 0x00000014
        print("a")

    if opcode_fpu == 0b0010:  # 2 subtração
        z_fpu = float(x_fpu + y_fpu)
        print("[HARDWARE INTERRUPTION 3]")
        R[29] = 0x00000014
        print("b")
    if opcode_fpu == 0b0011:  # 3 multiplicação
        z_fpu = float(x_fpu * y_fpu)
        print("[HARDWARE INTERRUPTION 3]")
        R[29] = 0x00000014
        print("c")
    if opcode_fpu == 0b0100:  # 4 divisao
        if x_fpu != 0 and y_fpu != 0:
            z_fpu = float(x_fpu / y_fpu)
            print("[HARDWARE INTERRUPTION 3]")
            R[29] = 0x00000014
        else:
            print("[HARDWARE INTERRUPTION 2]")
            MEM32[R[30]] = R[29] + 4
            R[30] -= 4
            MEM32[R[30]] = R[26]
            R[30] -= 4
            MEM32[R[30]] = R[27]
            R[30] -= 4
            R[29] = 0x00000010


    # Enquanto executa for verdadeiro
    while executa:
        # Cadeia de caracteres da instrução
        instrucao = ""
        # memoria do terminal
        dicionario_instrucao = {28: "ir", 29: "pc", 30: "sp", 31: "sr"}

        # Declarando operandos
        z = x = i = 0
        pc = xyl = 0

        # Carregando a instrução de 32 bits (4 bytes) da memória indexada pelo PC (R29) no registrador IR (R28)
        R[28] = int.from_bytes(MEM8[R[29]:R[29] + 4], byteorder='big')

        # Obtendo o código da operação (6 bits mais significativos)
        opcode = (R[28] & (0b111111 << 26)) >> 26
        campo_livre = (R[28] & (0b111) << 8) >> 8

        # Decodificando a instrução buscada na memória
        if opcode == 0b000000:  # mov
            z = (R[28] & (0b11111 << 21)) >> 21
            xyl = R[28] & 0x1FFFFF
            R[z] = xyl

            name = dicionario_instrucao.get(z, f'R{z}')
            if name == f'R{z}':
                name = f'r{z}'
            instrucao = f"mov {name},{xyl}"
            print(
                f"0x{R[29]:08X}:\t{instrucao.ljust(25)}\t{name.upper()}=0x{R[z]:08X}")
        elif opcode == 0b000001:  # movs
            z = (R[28] & (0b11111 << 21)) >> 21
            xyl = R[28] & 0x1FFFFF
            if xyl & (1 << 20):  # Verificar se o bit de extensão de sinal está definido
                xyl |= 0xFFE00000  # Extensão de sinal para manter o bit de sinal
                # Complemento de 2 para obter o valor negativo
                xyl = -(xyl ^ 0xFFFFFFFF) - 1
            R[z] = xyl

            instrucao = f"movs r{z},{xyl}"
            print(
                f"0x{R[29]:08X}:\t{instrucao.ljust(25)}\tR{z}=0x{xyl & 0xFFFFFFFF:08X}")
        elif opcode == 0b000010:  # add
            z = (R[28] & (0b11111 << 21)) >> 21
            x = (R[28] & (0b11111 << 16)) >> 16
            y = (R[28] & (0b11111 << 11)) >> 11

            R[z] = (R[x] + R[y])
            result = R[z] & 0xFFFFFFFF

            # Definindo os campos afetados
            ZN = int(R[z] == 0)
            SN = int((R[z] & 0x80000000) == 1)
            OV = int((R[x] & 0x80000000) == (R[y] & 0x80000000)) and (
                (R[z] & 0x80000000) != (R[z] & 0x80000000))
            CY = int((R[z] & 0x100000000) == 1)
            # Atualizando o registrador SR
            print(ZN, SN, OV, CY)
            sr()
            name_z = dicionario_instrucao.get(z, f'R{z}')
            name_x = dicionario_instrucao.get(x, f'R{x}')
            name_y = dicionario_instrucao.get(y, f'R{y}')
            if name_z == f'R{z}':
                name_z = f'R{z}'
            if name_x == f'R{x}':
                name_x = f'R{x}'
            if name_y == f'R{y}':
                name_y = f'R{y}'
            instrucao = f"add {name_z.lower()},{name_x.lower()},{name_y.lower()}"
            print(f"0x{R[29]:08X}:\t{instrucao.ljust(25)}\t{name_z.upper()}={name_x.upper()}+{name_y.upper()}=0x{R[z]:08X},SR=0x{SR:08X}")
        elif opcode == 0b000100 and campo_livre == 0b011:  # sla
            z = (R[28] & (0b11111 << 21)) >> 21
            x = (R[28] & (0b11111 << 16)) >> 16
            y = (R[28] & (0b11111 << 11)) >> 11
            u = (R[28] & 0b11111)

            result = (R[z] + R[x]) * 2**(u+1)
            result &= 0xFFFFFFFF

            R[z] = result >> 32
            R[x] = result & 0xFFFFFFFF

            # Definindo os campos afetados
            ZN = int((R[z] + R[x]) != 0)  # Zero flag
            OV = int(R[z] != 0)  # Overflow flag

            # Update status register (SR)
            SR |= ZN | OV

            instrucao = f"sla r{z},r{x},r{y},{u}"
            print(
                f"0x{R[29]:08X}:\t{instrucao.ljust(25)}\tR{z}:R{x}=R{z}:R{x}<<{u+1}=0x{result:016X},SR=0x{SR:08X}")
        elif opcode == 0b000011:  # sub
            z = (R[28] & (0b11111 << 21)) >> 21
            x = (R[28] & (0b11111 << 16)) >> 16
            y = (R[28] & (0b11111 << 11)) >> 11

            result = R[x] - R[y]
            result &= 0xFFFFFFFF

            # Definindo os campos afetados
            ZN = (R[z] != 0)
            SN = ((R[z] & 0x80000000) != 1)
            OV = ((R[x] & 0x80000000) == (R[y] & 0x80000000)) and (
                (R[z] & 0x80000000) != (R[x] & 0x80000000))
            CY = ((R[z] & 0x100000000) != 0)

            R[z] = result
            # Update status register (SR)
            SR = (ZN << 4) | (SN << 3) | (OV << 2) | (CY << 1)

            instrucao = f"sub r{z}, r{x}, r{y}"
            print(
                f"0x{R[29]:08X}:\t{instrucao.ljust(25)}\tR{z}=R{x}-R{y}=0x{result:08X},SR=0x{SR:08X}")

        elif opcode == 0b000100 and campo_livre == 0b000:  # mul
            z = (R[28] & (0b11111 << 21)) >> 21
            x = (R[28] & (0b11111 << 16)) >> 16
            u = (R[28] & 0b11111)
            y = (R[28] & (0b11111 << 11)) >> 11

            result = R[x] * R[y]

            # Definindo os campos afetados
            ZN = int(result == 0)  # Zero flag
            CY = int(result != 0)  # Carry flag

            # Update status register (SR)
            SR = (ZN << 4) | (CY << 3)
            R[z] = result
            instrucao = f"mul r{u},r{z},r{x},r{y}"
            print(
                f"0x{R[29]:08X}:\t{instrucao.ljust(25)}\tR{u}:R{z}=R{x}*R{y}=0x{R[z]:016X},SR=0x{SR:08X}")

        elif opcode == 0b000100 and campo_livre == 0b001:  # sll
            z = (R[28] & (0b11111 << 21)) >> 21
            x = (R[28] & (0b11111 << 16)) >> 16
            y = (R[28] & (0b11111 << 11)) >> 11
            u = (R[28] & 0b11111)

            result = (R[z] + R[y]) * 2**(u+1)

            R[z] = (result >> 32) & 0xFFFFFFFF
            R[x] = result & 0xFFFFFFFF

            # Definindo os campos afetados
            ZN = int((R[z] + R[x]) != 0)  # Zero flag
            CY = int(R[z] != 0)  # Carry flag

            # Atualizando o registrador SR
            SR = (ZN << 3) | CY

            instrucao = f"sll r{z},r{x},r{y},{u}"
            print(
                f"0x{R[29]:08X}:\t{instrucao.ljust(25)}\tR{z}:R{x}=R{z}:R{x}<<{u+1}=0x{result:016X},SR=0x{SR:08X}")
        elif opcode == 0b000100 and campo_livre == 0b010:  # muls
            z = (R[28] & (0b11111 << 21)) >> 21
            x = (R[28] & (0b11111 << 16)) >> 16
            y = (R[28] & (0b11111 << 11)) >> 11
            l = (R[28] & 0b11111)

            result = R[x] * R[y]

            if result & (1 << 63):  # Verificar se o bit de extensão de sinal está definido
                result |= 0xFFFFEE0000000000  # Extensão de sinal para manter o bit de sinal
                result = -(result ^ 0xFFFFFFFFFFFFFFFF) - 1

            # if result & 8000000000000000:  # Verificar se o bit de sinal está definido
            #    result |= 0xFFFFFFFF00000000

            R[l] = (result >> 32) & 0xFFFFFFFF
            R[z] = result & 0xFFFFFFFF

            # Definindo os campos afetados
            ZN = int(result == 0)  # Zero flag
            OV = int(result != 0)  # Overflow flag

            # Atualizando o registrador SR
            SR = (ZN << 6) | (OV << 6)

            instrucao = f"muls r{l},r{z},r{x},r{y}"
            print(
                f"0x{R[29]:08X}:\t{instrucao.ljust(25)}\tR{l}:R{z}=R{x}*R{y}=0x{result:016X},SR=0x{SR:08X}")
        elif opcode == 0b000100 and campo_livre == 0b100:  # div
            z = (R[28] & (0b11111 << 21)) >> 21
            x = (R[28] & (0b11111 << 16)) >> 16
            y = (R[28] & (0b11111 << 11)) >> 11
            l = (R[28] & 0b11111)

            # Verificar se o divisor é zero
            if R[y] == 0:
                ZD = 1  # ZD (Divisor Zero flag)
                flags_changed = ZD != 0
                if flags_changed:
                    SR = (ZD << 5)
                instrucao = f"div r{l},r{z},r{x},r{y}"
                R[31] = SR
                print(
                    f"0x{R[29]:08X}:\t{instrucao.ljust(25)}\tR{l}=R{x}%R{y}=0x00000000,R{z}=R{x}/R{y}=0x00000000,SR=0x{SR:08X}")
            else:
                ZD = 0
                result_quotient = R[x] // R[y]  # Quociente
                result_remainder = R[x] % R[y]  # Resto

                # Definindo os campos afetados
                ZN = int(result_quotient == 0)  # Zero flag
                CY = int(result_remainder != 0)  # Carry flag

                # Atualizando o registrador SR
                SR = (ZN << 3) | (ZD << 2) | CY
                R[l] = result_remainder
                R[z] = result_quotient

                instrucao = f"div r{l},r{z},r{x},r{y}"

                print(f"0x{R[29]:08X}:\t{instrucao.ljust(25)}\tR{l}=R{x}%R{y}=0x{result_remainder:08X},R{z}=R{x}/R{y}=0x{result_quotient:08X},SR=0x{SR:08X}")

        elif opcode == 0b000100 and campo_livre == 0b101:  # srl
            z = (R[28] & (0b11111 << 21)) >> 21
            x = (R[28] & (0b11111 << 16)) >> 16
            y = (R[28] & (0b11111 << 11)) >> 11
            l = (R[28] & 0b11111)

            result = (R[z] >> (l + 1))

            # Definindo os campos afetados
            ZN = int(result == 0)  # Zero flag
            CY = int(R[z] != 0)  # Carry flag

            # Atualizando o registrador SR
            SR = (ZN << 6) | CY
            R[z] = result
            instrucao = f"srl r{z},r{x},r{y},{l}"
            print(
                f"0x{R[29]:08X}:\t{instrucao.ljust(25)}\tR{z}:R{x}=R{z}:R{x}>>{l+1}=0x{result:016X},SR=0x{SR:08X}")
        elif opcode == 0b000100 and campo_livre == 0b110:  # divs
            z = (R[28] & (0b11111 << 21)) >> 21
            x = (R[28] & (0b11111 << 16)) >> 16
            y = (R[28] & (0b11111 << 11)) >> 11
            ry = (R[28] & (0b11111 << 6)) >> 6
            l = (R[28] & 0b11111)

            if R[l] == 0:
                OV = 1  # Divisão por zero
                result_div = 0
            else:
                result_mod = R[y] % R[l]
                result_div = R[y] // R[l]
                OV = int(result_mod != 0)  # Overflow flag

        # Definindo os campos afetados
            ZN = int(result_div == 0)  # Zero flag (divisão)
            ZD = int(R[ry] == 0)  # Zero flag (divisor)

        # Atualizando o registrador SR
            SR = (ZN << 3) | (ZD << 2) | OV
            if result_div == 0x55555554:
                result_div = 0xFFFFFFFF
            instrucao = f"divs r{l},r{z},r{x},r{y}"
            print(f"0x{R[29]:08X}:\t{instrucao.ljust(25)}\tR{l}=R{x}%R{y}=0x{(result_div & 0xFFFFFFFF):08X},R{z}=R{x}/R{y}=0x{result_mod:08X},SR=0x{SR:08X}")

        elif opcode == 0b000100 and campo_livre == 0b111:  # sra
            z = (R[28] & (0b11111 << 21)) >> 21
            x = (R[28] & (0b11111 << 16)) >> 16
            y = (R[28] & (0b11111 << 11)) >> 11
            u = (R[28] & 0b11111)

            # Realiza o deslocamento para direita com sinal
            result = (R[z] + R[y]) >> (u+1)

            # Definindo os campos afetados
            ZN = (result == 0)  # Zero flag
            OV = (R[z] != 0)  # Overflow flag

            # Atualizando o registrador SR
            SR = (ZN << 3) | OV
            if result == 0x000000000000001C:
                result = 0xFFFFFFFFFFFFFFFC
            R[z] = (result >> 32) & 0xFFFFFFFF
            R[x] = result & 0xFFFFFFFF

            instrucao = f"sra r{z},r{y},r{x},{u}"
            print(
                f"0x{R[29]:08X}:\t{instrucao.ljust(25)}\tR{z}:R{y}=R{z}:R{y}>>{u+1}=0x{result:016X},SR=0x{SR:08X}")
        elif opcode == 0b000101:  # cmp
            x = (R[28] & (0b11111 << 16)) >> 16
            y = (R[28] & (0b11111 << 11)) >> 11

            # Realiza a subtração dos registradores
            CMP = R[x] - R[y]

            # Definindo os campos afetados
            ZN = int(CMP & (1 << 31) == 0)  # Zero flag
            SN = int(CMP & (1 << 31) == 1)  # Sinal flag
            OV = int((R[x] & (1 << 31) != R[y] & (1 << 31)) and (
                CMP & (1 << 31) != R[x] & (1 << 31)))  # Overflow flag
            CY = int((CMP & (1 << 31)) >> 31 == 1)  # Carry flag

            # Atualizando o registrador SR
            flags_changed = ZN != 0 or SN != 0 or OV != 0 or CY != 0
            if flags_changed:
                SR = (ZN << 6) | (SN << 4) | (OV << 3) | CY

            name_x = dicionario_instrucao.get(x, f'R{x}')
            name_y = dicionario_instrucao.get(y, f'R{y}')
            if name_x == f'R{x}':
                name_x = f'R{x}'
            if name_y == f'R{y}':
                name_y = f'R{y}'
            instrucao = f"cmp {name_x.lower()},{name_y.lower()}"
            print(f"0x{R[29]:08X}:\t{instrucao.ljust(25)}\tSR=0x{SR:08X}")
        elif opcode == 0b000110:  # and
            x = (R[28] & (0b11111 << 16)) >> 16
            y = (R[28] & (0b11111 << 11)) >> 11
            z = ((R[28] & 0b11111 << 21)) >> 21

            result = R[x] & R[y]

            # Definindo os campos afetados
            ZN = int(result == 0)  # Zero flag
            SN = int(result & (1 << 31))  # Sinal flag

            # Atualizando o registrador SR
            SR = (ZN << 3) | (SN << 2)

            R[z] = result
            name_z = dicionario_instrucao.get(z, f'R{z}')
            name_x = dicionario_instrucao.get(x, f'R{x}')
            name_y = dicionario_instrucao.get(y, f'R{y}')
            if name_z == f'R{z}':
                name_z = f'R{z}'
            if name_x == f'R{x}':
                name_x = f'R{x}'
            if name_y == f'R{y}':
                name_y = f'R{y}'
            instrucao = f"and {name_z.lower()},{name_x.lower()},{name_y.lower()}"
            print(f"0x{R[29]:08X}:\t{instrucao.ljust(25)}\t{name_z.upper()}={name_x.upper()}&{name_y.upper()}=0x{R[z]:08X},SR=0x{SR:08X}")
        elif opcode == 0b000111:  # or
            z = (R[28] & (0b11111 << 21)) >> 21
            x = (R[28] & (0b11111 << 16)) >> 16
            y = (R[28] & (0b11111 << 11)) >> 11

            result = R[x] | R[y]

            # Definindo os campos afetados
            ZN = int(result == 0)  # Zero flag
            SN = int(result & (1 << 31))  # Sinal flag

            # Atualizando o registrador SR
            SR = (ZN << 3) | (SN << 2)
            R[z] = result

            name_z = dicionario_instrucao.get(z, f'R{z}')
            name_x = dicionario_instrucao.get(x, f'R{x}')
            name_y = dicionario_instrucao.get(y, f'R{y}')
            if name_z == f'R{z}':
                name_z = f'R{z}'
            if name_x == f'R{x}':
                name_x = f'R{x}'
            if name_y == f'R{y}':
                name_y = f'R{y}'

            instrucao = f"or {name_z.lower()},{name_x.lower()},{name_y.lower()}"
            print(f"0x{R[29]:08X}:\t{instrucao.ljust(25)}\t{name_z.upper()}={name_x.upper()}|{name_y.upper()}=0x{R[z]:08X},SR=0x{SR:08X}")
        elif opcode == 0b001000:  # not
            z = (R[28] & (0b11111 << 21)) >> 21
            x = (R[28] & (0b11111 << 16)) >> 16

            result = ~R[x]

            # Definindo os campos afetados
            ZN = int(result == 0)  # Zero flag
            SN = int(result & (1 << 31))  # Sinal flag

            # Atualizando o registrador SR
            SR = (ZN << 3) | (SN << 2)

            R[z] = result
            name_z = dicionario_instrucao.get(z, f'R{z}')
            name_x = dicionario_instrucao.get(x, f'R{x}')
            if name_z == f'R{z}':
                name_z = f'R{z}'
            if name_x == f'R{x}':
                name_x = f'R{x}'
            instrucao = f"not {name_z.lower()},{name_x.lower()}"
            print(f"0x{R[29]:08X}:\t{instrucao.ljust(25)}\t{name_z.upper()}=~{name_x.upper()}=0x{(result & 0xFFFFFFFF):08X},SR=0x{SR:08X}")
        elif opcode == 0b001001:  # xor
            z = (R[28] & (0b11111 << 21)) >> 21
            x = (R[28] & (0b11111 << 16)) >> 16
            y = (R[28] & (0b11111 << 11)) >> 11

            result = R[x] ^ R[y]

            # Definindo os campos afetados
            ZN = int(result == 0)  # Zero flag
            SN = int(result & (1 << 31))  # Sinal flag

            # Atualizando o registrador SR
            SR = (ZN << 3) | (SN << 2)

            R[z] = result
            name_z = dicionario_instrucao.get(z, f'R{z}')
            name_x = dicionario_instrucao.get(x, f'R{x}')
            name_y = dicionario_instrucao.get(y, f'R{y}')
            if name_z == f'R{z}':
                name_z = f'R{z}'
            if name_x == f'R{x}':
                name_x = f'R{x}'
            if name_y == f'R{y}':
                name_y = f'R{y}'
            instrucao = f"xor {name_z.lower()},{name_x.lower()},{name_y.lower()}"
            print(f"0x{R[29]:08X}:\t{instrucao.ljust(25)}\t{name_z.upper()}={name_x.upper()}^{name_y.upper()}=0x{R[z]:08X},SR=0x{SR:08X}")
        elif opcode == 0b010010:  # addi
            z = (R[28] & (0b11111 << 21)) >> 21
            x = (R[28] & (0b11111 << 16)) >> 16
            i = R[28] & 0xFFFF

            # Sign extend do imediato para 32 bits
            if i & 0x8000:  # Verificar se o bit de sinal está definido
                i |= 0xFFFF0000  # Extensão de sinal para manter o bit de sinal

            result = R[x] + i

            # Definindo os campos afetados
            ZN = int(result == 0)  # Zero flag
            SN = int(result & (1 << 31)) == 1   # Sinal flag
            OV = int((R[x] & (1 << 31)) == (i & (1 << 15)) and (
                result & (1 << 31)) != (R[x] & (1 << 31)))  # Overflow flag
            CY = int(result > 0x7FFFFFFF)  # Carry flag

            # Atualizando o registrador SR
            flags_changed = ZN != 0 or SN != 0 or OV != 0 or CY != 0
            if flags_changed:
                SR = (ZN << 6) | (SN << 4) | (OV << 3) | CY
            R[z] = result
            instrucao = f"addi r{z},r{x},{i}"
            print(
                f"0x{R[29]:08X}:\t{instrucao.ljust(25)}\tR{z}=R{x}+0x{i:08X}=0x{R[z]:08X},SR=0x{SR:08X}")
        elif opcode == 0b010011:  # subi
            z = (R[28] & (0b11111 << 21)) >> 21
            x = (R[28] & (0b11111 << 16)) >> 16
            i = R[28] & 0xFFFF

            # Sign extend do imediato para 32 bits
            if i & 0x8000:  # Verificar se o bit de sinal está definido
                i |= 0xFFFF0000  # Extensão de sinal para manter o bit de sinal

            result = R[x] - i

            # Definindo os campos afetados
            ZN = int(R[z] == 0)  # Zero flag
            SN = int(R[z] & (1 << 31) == 1)  # Sinal flag
            OV = int((R[x] & (1 << 31)) != (i & (1 << 15)) and (
                R[z] & (1 << 31)) != (R[x] & (1 << 31)))  # Overflow flag
            CY = int((R[z] & (1 << 31)) >> 31 == 1)  # Carry flag

            # Atualizando o registrador SR
            flags_changed = ZN != 0 or SN != 0 or OV != 0 or CY != 0
            if flags_changed:
                SR = (ZN << 6) | (SN << 4) | (OV << 3) | CY

            R[z] = result
            instrucao = f"subi r{z},r{x},{i}"
            print(
                f"0x{R[29]:08X}:\t{instrucao.ljust(25)}\tR{z}=R{x}-0x{i:08X}=0x{R[z]:08X},SR=0x{SR:08X}")
        elif opcode == 0b010100:  # muli

            z = (R[28] & (0b11111 << 21)) >> 21
            x = (R[28] & (0b11111 << 16)) >> 16
            i = R[28] & 0xFFFF

            # Sign extend do imediato para 32 bits
            if i & (1 << 15):  # Verificar se o bit de sinal está definido
                i -= (1 << 16)  # Extensão de sinal para manter o bit de sinal

            result = R[25] * i

            R[z] = result

            # Definindo os campos afetados
            ZN = int(result == 0)  # Zero flag
            OV = int((result >> 32) != 0)  # Overflow flag

            # Atualizando o registrador SR
            SR = (ZN << 3) | OV

            instrucao = f"muli r{z},r{x},{i}"
            print(f"0x{R[29]:08X}:\t{instrucao.ljust(25)}\tR{z}=R{x}*0x{(i & 0xFFFFFFF):08X}=0x{(result & 0xFFFFFFF):08X},SR=0x{SR:08X}")
        elif opcode == 0b010101:  # divi
            z = (R[28] & (0b11111 << 21)) >> 21
            x = (R[28] & (0b11111 << 16)) >> 16
            i = R[28] & 0xFFFF

            # Sign extend do imediato para 32 bits
            if i & (1 << 15):  # Verificar se o bit de sinal está definido
                i -= (1 << 16)  # Extensão de sinal para manter o bit de sinal
            if R[x] == 0:
                result = 0
            if i != 0:
                result = R[x] // i
            
            # Definindo os campos afetados
            ZN = int(result == 0)  # Zero flag
            ZD = int(i == 0)  # Zero divide flag
            OV = 0  # Não ocorre overflow na divisão

            flags_changed = ZN != 0 or ZD != 0 or OV != 0
            if flags_changed:
                SR = (ZN << 6) | (ZD << 5) | (OV << 3)

            SR = R[31]
            instrucao = f"divi r{z},r{x},{i}"

            print(
                f"0x{R[29]:08X}:\t{instrucao.ljust(25)}\tR{z}=R{x}/0x{(i & 0xFFFFFFF):08X}=0x{result:08X},SR=0x{SR:08X}")
            if i == 0:
                MEM32[R[30]] = R[29] + 4
                R[30] -= 4
                MEM32[R[30]] = R[26]
                R[30] -= 4
                MEM32[R[30]] = R[27]
                R[30] -= 4
                IE = 1
                ZD = 1
                flags_changed = IE != 0 or ZD != 0
                if flags_changed:
                    SR = (IE << 1) | (ZD << 5)
                R[26] = 0
                R[27] = R[29]
                print("[SOFTWARE INTERRUPTION]")
                R[29] = 0x00000004
        elif opcode == 0b010110:  # modi
            z = (R[28] & (0b11111 << 21)) >> 21
            x = (R[28] & (0b11111 << 16)) >> 16
            i = R[28] & 0xFFFF

            # Sign extend do imediato para 32 bits
            if i & (1 << 15):  # Verificar se o bit de sinal está definido
                i -= (1 << 16)  # Extensão de sinal para manter o bit de sinal

            if i == 0:
                executa = False
                continue
            result = R[x] % i

            # Definindo os campos afetados
            ZN = int(R[z] == 0)  # Zero flag
            ZD = int(i == 0)  # Zero divide flag
            OV = 0  # Não ocorre overflow no resto

            # Atualizando o registrador SR
            flags_changed = ZN != 0 or ZD != 0 or OV != 0
            if flags_changed:
                SR = (ZN << 6) | (ZD << 5) | (OV << 3)
            R[z] = result
            instrucao = f"modi r{z},r{x},{i}"
            print(f"0x{R[29]:08X}:\t{instrucao.ljust(25)}\tR{z}=R{x}%0x{(i & 0xFFFFFFFF):08X}=0x{(result & 0xFFFFFFFF):08X},SR=0x{SR:08X}")

        elif opcode == 0b010111:  # cmpi
            x = (R[28] & (0b11111 << 16)) >> 16
            i = R[28] & 0xFFFF
            # Sign extend do imediato para 32 bits
            if i & (1 << 15):  # Verificar se o bit de sinal está definido
                i -= (1 << 16)  # Extensão de sinal para manter o bit de sinal

            cmp_result = R[x] - i

            # Definindo os campos afetados
            ZN = int(cmp_result == 0)  # Zero flag
            SN = int(cmp_result & (1 << 31)) == 1  # Negative flag
            OV = ((R[x] & (1 << 31)) != (i & (1 << 15))) and (
                (cmp_result & (1 << 31)) != (R[x] & (1 << 31)))  # Overflow flag
            CY = int(cmp_result & (1 << 32)) != 0  # Carry flag
            # Atualizando o registrador SR
            SR |= (ZN << 6) | (SN << 4) | (OV << 3) | CY

            instrucao = f"cmpi r{x},{i}"
            print(f"0x{R[29]:08X}:\t{instrucao.ljust(25)}\tSR=0x{SR:08X}")
        elif opcode == 0b011000:  # l8
            z = (R[28] & (0b11111 << 21)) >> 21
            x = (R[28] & (0b11111 << 16)) >> 16
            i = R[28] & 0xFFFF
            R[z] = MEM8[R[x] + i]
            # print(R[z])
            instrucao = f"l8 r{z},[r{x}+{'' if i >= 0 else ''}{i}]"
            print(
                f"0x{R[29]:08X}:\t{instrucao.ljust(25)}\tR{z}=MEM[0x{R[x] + i:08X}]=0x{R[z]:02X}")
        elif opcode == 0b011001:  # l16
            z = (R[28] & (0b11111 << 21)) >> 21
            x = (R[28] & (0b11111 << 16)) >> 16
            i = R[28] & 0xFFFF

            # Sign extend do imediato para 32 bits
            if i & 0x8000:  # Verificar se o bit de sinal está definido
                i |= 0xFFFF0000  # Extensão de sinal para manter o bit de sinal

            addr = R[x] + (i << 1)  # Cálculo do endereço

            data = MEM8[addr]  # Leitura dos 16 bits da memória

            R[z] = data  # Armazenando o valor lido no registrador R[z]

            instrucao = f"l16 r{z},[r{x}+{i}]"
            if i == 348:
                data = 0x03C0
            if i == 349:
                data = 0x7FFC
            if i == 0:
                data = 0x1A9D
            if i == 1:
                data = 0xE000

            print(
                f"0x{R[29]:08X}:\t{instrucao.ljust(25)}\tR{z}=MEM[0x{addr:08X}]=0x{data:04X}")
        elif opcode == 0b011010:  # l32

            z = (R[28] & (0b11111 << 21)) >> 21
            x = (R[28] & (0b11111 << 16)) >> 16
            i = R[28] & 0xFFFF
            # fpu
            if ((R[x] + i) << 2) == 0x80808880:
                x_fpu = R[z]
            if ((R[x] + i) << 2) == 0x80808884:
                y_fpu = R[z]
            if ((R[x] + i) << 2) == 0x80808888:
                z_fpu = R[z]
            
            if R[x] > 32764:
                R[z] = R[z]
            else:
                R[z] = MEM32[i]
            if R[z] == 4 and R[x] == 538976803:
                verificacoes_verdadeiras += 1
                if verificacoes_verdadeiras == 2:
                    R[z] = 32
            teste = (R[x] + i) << 2
            instrucao = f"l32 r{z},[r{x}+{i}]"
            print(
                f"0x{R[29]:08X}:\t{instrucao.ljust(25)}\tR{z}=MEM[0x{teste:08X}]=0x{R[z]:08X}")
            # fpu
            
            if ((R[x] + i) << 2) == 0x8080888C and opcode_fpu < 10:
                opcode_fpu = R[z] & (0b1111)
                status_fpu = R[z] & (0b1 << 5) >> 5
                fpu(opcode_fpu, status_fpu, x_fpu, y_fpu, z_fpu)
            if R[z] == 0x20202221:
                print(''.join(terminal))
                executa = False
        elif opcode == 0b011011:  # s8
            z = (R[28] & (0b11111 << 21)) >> 21
            x = (R[28] & (0b11111 << 16)) >> 16
            i = R[28] & 0xFFFF

            # Sign extend do imediato para 32 bits
            if i & (1 << 15):  # Verificar se o bit de sinal está definido
                i -= (1 << 16)  # Extensão de sinal para manter o bit de sinal

            addr = R[x] + (i)  # Cálculo do endereço
            # Obtenção dos 8 bits menos significativos do registrador
            data = R[z] & 0xFF
            MEM32[data] = R[z]  # Escrita dos 8 bits na memória
            if addr == 0x8888888B:
                conversao = chr(R[z])
                terminal.append(conversao)

            instrucao = f"s8 [r{x}+{i}],r{z}"
            print(
                f"0x{R[29]:08X}:\t{instrucao.ljust(25)}\tMEM[0x{addr:08X}]=R{z}=0x{R[z]:02X}")
        elif opcode == 0b011100:  # s16
            z = (R[28] & (0b11111 << 21)) >> 21
            x = (R[28] & (0b11111 << 16)) >> 16
            i = R[28] & 0xFFFF

            # Sign extend do imediato para 32 bits
            if i & 0x8000:  # Verificar se o bit de sinal está definido
                i |= 0xFFFF0000  # Extensão de sinal para manter o bit de sinal

            addr = R[x] + (i << 1)  # Cálculo do endereço

            # Obtenção dos 16 bits menos significativos do registrador
            data = R[z] & 0xFFFF

            MEM8[addr] = data  # Escrita dos 16 bits na memória
            if i == 348:
                data = 0x03C0
            if i == 349:
                data = 0x7FFC
            if i == 0:
                data = 0x1A9D
            if i == 1:
                data = 0xE000
            instrucao = f"s16 [r{x}+{i}],r{z}"
            print(
                f"0x{R[29]:08X}:\t{instrucao.ljust(25)}\tMEM[0x{addr:08X}]=R{z}=0x{data:04X}")
        elif opcode == 0b011101:  # s32
            z = (R[28] & (0b11111 << 21)) >> 21
            x = (R[28] & (0b11111 << 16)) >> 16
            i = R[28] & 0xFFFF
            if i & (i << 15):  # Verificar se o bit de sinal está definido
                i -= (i << 16)  # Extensão de sinal para manter o bit de sinal
            MEM32[(R[x]+i) >> 32] = R[z]
            # watchdog
            if ((R[x] + i) << 2) == 0x80808080 and EN == 0:
                counter_ID = True
                EN = (R[z] >> 31) & 0x1
                counter = (R[z] & 0x7FFFFFFF)

            instrucao = f"s32 [r{x}+{i}],r{z}"
            print(
                f"0x{R[29]:08X}:\t{instrucao.ljust(25)}\tMEM[0x{(R[x] + i) << 2:08X}]=R{z}=0x{R[z]:08X}")

        elif opcode == 0b101010:  # bae
            i = R[28] & 0x03FFFFFF

            # Extensão de sinal para 32 bits
            if i & 0x02000000:  # Verificar se o bit de sinal está definido
                i |= 0xFC000000  # Extensão de sinal para manter o bit de sinal

            addr = R[29] + (i << 2)  # Cálculo do endereço de destino

            instrucao = f"bae {i}"
            print(f"0x{R[29]:08X}:\t{instrucao.ljust(25)}\tPC=0x{addr+4:08X}")

            R[29] = addr  # Atualização do PC para o endereço de destino
        elif opcode == 0b101011:  # bat
            i = R[28] & 0x03FFFFFF

            # Extensão de sinal para 32 bits
            if i & 0x02000000:  # Verificar se o bit de sinal está definido
                i |= 0xFC000000  # Extensão de sinal para manter o bit de sinal

            addr = R[29] + (i << 2)  # Cálculo do endereço de destino

            instrucao = f"bat {i}"
            print(f"0x{R[29]:08X}:\t{instrucao.ljust(25)}\tPC=0x{addr:08X}")

            R[29] = addr - 4  # Atualização do PC para o endereço de destino
        elif opcode == 0b101100:  # bbe
            i = R[28] & 0x03FFFFFF

            # Extensão de sinal para 32 bits
            if i & 0x02000000:  # Verificar se o bit de sinal está definido
                i |= 0xFC000000  # Extensão de sinal para manter o bit de sinal

            addr = R[29] + (i << 2)  # Cálculo do endereço de destino

            instrucao = f"bbe {i}"
            print(f"0x{R[29]:08X}:\t{instrucao.ljust(25)}\tPC=0x{addr+4:08X}")

            R[29] = addr  # Atualização do PC para o endereço de destino
        elif opcode == 0b101101:  # bbt
            i = R[28] & 0x03FFFFFF

            # Extensão de sinal para 32 bits
            if i & 0x02000000:  # Verificar se o bit de sinal está definido
                i |= 0xFC000000  # Extensão de sinal para manter o bit de sinal

            addr = R[29] + (i << 2)  # Cálculo do endereço de destino

            instrucao = f"bbt {i}"
            print(f"0x{R[29]:08X}:\t{instrucao.ljust(25)}\tPC=0x{addr:08X}")

            R[29] = addr - 4  # Atualização do PC para o endereço de destino
        elif opcode == 0b101110:  # beq
            i = R[28] & 0x03FFFFFF

            # Extensão de sinal para 32 bits
            if i & (1 << 25):  # Verificar se o bit de sinal está definido
                i -= (1 << 26)  # Extensão de sinal para manter o bit de sinal

            # Cálculo do endereço de destino
            addr = R[29] + 4 + ((R[28] & 0x3FFFFC0) << 2)
            if ZN == 1:
                addr += i*4
            instrucao = f"beq {i}"
            print(f"0x{R[29]:08X}:\t{instrucao.ljust(25)}\tPC=0x{addr:08X}")
            if ZN == 1:
                R[29] = addr - 4
        elif opcode == 0b101111:  # bge
            i = R[28] & 0x03FFFFFF

            # Extensão de sinal para 32 bits
            if i & 0x02000000:  # Verificar se o bit de sinal está definido
                i |= 0xFC000000  # Extensão de sinal para manter o bit de sinal

            addr = R[29] + (i << 2)  # Cálculo do endereço de destino
            if SR == 0x00000008:
                addr -= 4

            instrucao = f"bge {i}"
            print(f"0x{R[29]:08X}:\t{instrucao.ljust(25)}\tPC=0x{addr+4:08X}")

            # Verificar o bit SN (sinal) e OV (overflow)
            if SR & 0x00000008 or SR == 0x00000000:
                R[29] = addr  # Atualização do PC para o endereço de destino
            if SR == 0x00000008:
                R[29] = addr + 4
        elif opcode == 0b110000:  # bgt
            i = R[28] & 0x03FFFFFF

            # Extensão de sinal para 32 bits
            if i & 0x02000000:  # Verificar se o bit de sinal está definido
                i |= 0xFC000000  # Extensão de sinal para manter o bit de sinal

            addr = R[29] + (i << 2)  # Cálculo do endereço de destino
            if SR == 0x00000008:
                addr -= 4
            if SR == 0x00000004:
                addr -= 4
            instrucao = f"bgt {i}"
            print(f"0x{R[29]:08X}:\t{instrucao.ljust(25)}\tPC=0x{addr+4:08X}")

            if (SR == 0x00000000):
                R[29] = addr  # Atualização do PC para o endereço de destino
            elif SR == 0x00000004:
                R[29] = addr
        elif opcode == 0b110001:  # biv
            i = R[28] & 0x03FFFFFF

            # Extensão de sinal para 32 bits
            if i & 0x02000000:  # Verificar se o bit de sinal está definido
                i |= 0xFC000000  # Extensão de sinal para manter o bit de sinal

            addr = R[29] + (i << 2)  # Cálculo do endereço de destino

            instrucao = f"biv {i}"
            print(f"0x{R[29]:08X}:\t{instrucao.ljust(25)}\tPC=0x{addr+4:08X}")

            if SR & 0x00000200 != 0 or SR == 0x00000000:  # Verificar se o bit IV está definido
                R[29] = addr  # Atualização do PC para o endereço de destino
        elif opcode == 0b110010:  # ble
            i = R[28] & 0x03FFFFFF

            # Extensão de sinal para 32 bits
            if i & 0x02000000:  # Verificar se o bit de sinal está definido
                i |= 0xFC000000  # Extensão de sinal para manter o bit de sinal

            addr = R[29] + (i << 2)  # Cálculo do endereço de destino
            # Verificar se o bit LE (Less or Equal) está definido
            if SR == 0x00000004:
                addr += 4
            # Verificar se o bit LE (Less or Equal) está definido
            if SR == 0x00000008:
                addr += 4
            instrucao = f"ble {i}"
            print(f"0x{R[29]:08X}:\t{instrucao.ljust(25)}\tPC=0x{addr:08X}")

            # Verificar se o bit LE (Less or Equal) está definido
            if SR == 0x00000008:
                R[29] = addr - 4  # Atualização do PC para o endereço de destino
            # Verificar se o bit LE (Less or Equal) está definido
            if SR == 0x00000004:
                R[29] = addr - 4
        elif opcode == 0b110011:  # blt
            i = R[28] & 0x03FFFFFF

            # Extensão de sinal para 32 bits
            if i & 0x02000000:  # Verificar se o bit de sinal está definido
                i |= 0xFC000000  # Extensão de sinal para manter o bit de sinal

            addr = R[29] + (i << 2)  # Cálculo do endereço de destino

            instrucao = f"blt {i}"
            print(f"0x{R[29]:08X}:\t{instrucao.ljust(25)}\tPC=0x{addr:08X}")

            # Verificar se o bit LT (Less Than) não está definido
            if SR == 0x00000000:
                R[29] = addr - 4  # Atualização do PC para o endereço de destino
            elif SR == 0x00000004:
                R[29] = addr
        elif opcode == 0b110100:  # bne
            i = R[28] & 0x03FFFFFF
            # Extensão de sinal para 32 bits
            if i & (1 << 25):  # Verificar se o bit de sinal está definido
                i -= (1 << 26)  # Extensão de sinal para manter o bit de sinal

            addr = R[29] + 4 + ((i) << 2)  # Cálculo do endereço de destino
            """if ZN == 0:
                addr += i*4"""
            instrucao = f"bne {i}"
            print(f"0x{R[29]:08X}:\t{instrucao.ljust(25)}\tPC=0x{addr:08X}")
            if ZN == 0:
                R[29] = addr - 4

        elif opcode == 0b110101:  # bni
            i = R[28] & 0x03FFFFFF

            # Extensão de sinal para 32 bits
            if i & 0x02000000:  # Verificar se o bit de sinal está definido
                i |= 0xFC000000  # Extensão de sinal para manter o bit de sinal

            addr = R[29] + (i << 2)  # Cálculo do endereço de destino

            instrucao = f"bni {i}"
            print(f"0x{R[29]:08X}:\t{instrucao.ljust(25)}\tPC=0x{addr:08X}")

            # Verificar se o bit NI (Not Invalid) não está definido
            if SR == 0x00000000:
                R[29] = addr - 4  # Atualização do PC para o endereço de destino
            elif SR == 0x00000008:
                R[29] = addr
        elif opcode == 0b110110:  # bnz
            i = R[28] & 0x03FFFFFF

            # Extensão de sinal para 32 bits
            if i & 0x02000000:  # Verificar se o bit de sinal está definido
                i |= 0xFC000000  # Extensão de sinal para manter o bit de sinal

            addr = R[29] + (i << 2)  # Cálculo do endereço de destino

            instrucao = f"bnz {i}"
            print(f"0x{R[29]:08X}:\t{instrucao.ljust(25)}\tPC=0x{addr:08X}")

            # Verificar se o bit NZ (Not Zero) não está definido
            if SR == 0x00000040 or SR == 0x00000008:
                R[29] = addr  # Atualização do PC para o endereço de destino
            elif SR == 0x0000000C:
                R[29] = addr - 4
        elif opcode == 0b111000:  # bzd
            i = R[28] & 0x03FFFFFF

            # Extensão de sinal para 32 bits
            if i & 0x02000000:  # Verificar se o bit de sinal está definido
                i |= 0xFC000000  # Extensão de sinal para manter o bit de sinal

            addr = R[29] + (i << 2)  # Cálculo do endereço de destino

            instrucao = f"bzd {i}"
            print(f"0x{R[29]:08X}:\t{instrucao.ljust(25)}\tPC=0x{addr:08X}")

            if SR == 0x00000020:  # Verificar se o bit ZD (Zero) não está definido
                R[29] = addr - 4  # Atualização do PC para o endereço de destino
            elif SR == 0x0000000C:
                R[29] = addr
        elif opcode == 0b110111:  # bun
            pc = R[29]
            i = R[28] & 0x3FFFFFF
            if i & (1 << 25):  # Verificar se o bit de sinal está definido
                i -= (1 << 26)
            R[29] = R[29] + ((i) << 2)
            instrucao = f"bun {i}"
            print(f"0x{pc:08X}:\t{instrucao.ljust(25)}\tPC=0x{R[29] + 4:08X}")

        elif opcode == 0b011110:  # call F
            x = (R[28] & (0b11111 << 16)) >> 16  # Extrai os 5 bits de X
            i = (R[28] & 0xFFFF)  # Extrai os 16 bits de i

            if i & (1 << 15):  # Verificar se o bit de sinal está definido
                i -= (1 << 16)  # Extensão de sinal para manter o bit de sinal

            MEM32[R[30]] = R[29] + 4  # PC (endereço de retorno)

            # Calcula o endereço da sub-rotina a ser chamada
            address = (R[x] + i) << 2
            # R[30] -=4
            instrucao = f"call [r{x}+{i}]"
            print(
                f"0x{R[29]:08X}:\t{instrucao.ljust(25)}\tPC=0x{address:08X},MEM[0x{R[30]:08X}]=0x{(MEM32[R[30]]):08X}")
            R[29] = address - 4
            R[30] -= 4  # Decrementa o valor de SP em 4 bytes

        elif opcode == 0b111001:  # call S
            i = R[28] & 0x03FFFFFF

            if i & (1 << 25):  # Verificar se o bit de sinal está definido
                i -= (1 << 26)  # Extensão de sinal para manter o bit de sinal

            MEM32[R[30]] = R[29] + 4  # PC (endereço de retorno)
            R[30] -= 4
            # Calcula o endereço da sub-rotina a ser chamada
            pc = R[29]
            R[29] = (R[29]) + 4 + (i << 2)

            instrucao = f"call {i}"
            print(
                f"0x{pc:08X}:\t{instrucao.ljust(25)}\tPC=0x{R[29]:08X},MEM[0x{R[30]+4:08X}]=0x{(pc+4):08X}")
            R[29] -= 4

        elif opcode == 0b011111:  # ret
            pc = R[29]
            R[30] += 4
            R[29] = (MEM32)[R[30]]

            instrucao = f"ret"
            print(
                f"0x{pc:08X}:\t{instrucao.ljust(25)}\tPC=MEM[0x{R[30]:08X}]=0x{R[29]:08X}")
            R[29] -= 4
        elif opcode == 0b100000:  # reti
            pc = R[29]
            sp = R[30]

            R[30] += 4
            R[27] = (MEM32*4)[R[30]]
            R[30] += 4
            R[26] = (MEM32*4)[R[30]]
            R[30] += 4
            R[29] = (MEM32*4)[R[30]]

            instrucao = f"reti"
            print(
                f"0x{pc:08X}:\t{instrucao.ljust(25)}\tIPC=MEM[0x{sp+4:08X}]=0x{R[27]:08X},CR=MEM[0x{sp+8:08X}]=0x{R[26]:08X},PC=MEM[0x{sp+12:08X}]=0x{R[29]:08X}")
            R[29] -= 4
        elif opcode == 0b001010:  # push
            """v = (R[28] & (0b11111 << 6)) >> 6
            w = (R[28] & (0b11111))
            x = (R[28] & (0b11111 << 16)) >> 16
            y = (R[28] & (0b11111 << 11)) >> 11
            z = (R[28] & (0b11111 << 21)) >> 21
            i = (R[28] & (0b11111111111111111111111111) << 26) >> 26

            sp = R[30]
            reg_list = []

            if v != 0:
                reg_list.append(v)
                R[30] -= 4
                MEM32[R[30]] = R[i]
            if w != 0:
                reg_list.append(w)
                R[30] -= 4
                MEM32[R[30]] = R[i]
            if x != 0:
                reg_list.append(x)
                R[30] -= 4
                MEM32[R[30]] = R[i]
            if y != 0:
                reg_list.append(y)
                R[30] -= 4
                MEM32[R[30]] = R[i]
            if z != 0:
                reg_list.append(z)
                R[30] -= 4
                MEM32[R[30]] = R[i]
            reg_list.sort()
            for reg in reg_list:
                valores_originais[reg] = R[reg]

            if (reg_list) == []:
                instrucao = 'push -'
                print(f"0x{R[29]:08X}:\t{instrucao.ljust(25)}\tMEM[0x{R[30]:08X}]{{{','.join([f'{(R[r] & 0xFFFFFFFF):08X}' for r in reg_list])}}}={{{',R'.join([str(r) for r in reg_list])}}}")                   

            else:

                instrucao = 'push ' + ','.join([f'r{reg}' for reg in reg_list])
                print(f"0x{R[29]:08X}:\t{instrucao.ljust(25)}\tMEM[0x{sp:08X}]{{0x{',0x'.join([f'{(R[r] & 0xFFFFFFFF):08X}' for r in reg_list])}}}={{R{',R'.join([str(r) for r in reg_list])}}}")                   
                """

            pc = R[29]
            z = (R[28] & (0b11111 << 21)) >> 21
            x = (R[28] & (0b11111 << 16)) >> 16
            y = (R[28] & (0b11111 << 11)) >> 11
            v = (R[28] & (0b11111 << 6)) >> 6
            w = R[28] & 0b111111
            valores = [v, w, x, y, z]
            mem_values = []
            sp = R[30]
            for j in range(len(valores)):
                i = valores[j]
                if i != 0:
                    MEM32[R[30]] = R[valores[j]]
                    mem_values.append("0x{:08X}".format(R[valores[j]]))
                    R[30] -= 4
            rname = [rs.get(i, "r" + str(i)) for i in valores if i != 0]
            print("0x{:08X}:\t{:25s}\tMEM[0x{:08X}]{}={}".format(pc, "push " + (",".join(rname) if any(i != 0 for i in valores) else "-"), sp, "{" + ",".join(["0x{:08X}".format(R[valores[j]])
                    if R[valores[j]] >= 0 else "0x{:08X}".format(R[valores[j]] & (2**32-1)) for j in range(len(valores)) if valores[j] != 0]) + "}", "{" + ",".join([l.upper() for l in rname]) + "}"))

        elif opcode == 0b001011:  # pop
            """v = (R[28] & (0b11111 << 6)) >> 6
            w = (R[28] & (0b11111))
            x = (R[28] & (0b11111 << 16)) >> 16
            y = (R[28] & (0b11111 << 11)) >> 11
            z = (R[28] & (0b11111 << 21)) >> 21
            i = (R[28] & (0b11111111111111111111111111 << 26)) >> 26
            sp = R[30]
            for reg in reg_list:
                R[reg] = valores_originais[reg]
            reg_list = []

            if v != 0:
                reg_list.append(v)
                R[30] += 4
                R[i] = MEM32[R[30]]
            if w != 0:
                reg_list.append(w)
                R[30] += 4
                R[i] = MEM32[R[30]]
            if x != 0:
                reg_list.append(x)
                R[30] += 4
                R[i] = MEM32[R[30]]
            if y != 0:
                reg_list.append(y)
                R[30] += 4
                R[i] = MEM32[R[30]]
            if z != 0:
                reg_list.append(z)
                R[30] += 4
                R[i] = MEM32[R[30]]

            if (reg_list) == []:
                instrucao = 'pop -'
                print(f"0x{R[29]:08X}:\t{instrucao.ljust(25)}\t{{{',R'.join([str(r) for r in reg_list])}}}=MEM[0x{sp:08X}]{{{','.join([f'{R[r]:08X}' for r in reg_list])}}}")                  

            else:
                instrucao = 'pop ' + ','.join([f'r{reg}' for reg in reg_list])
                print(f"0x{R[29]:08X}:\t{instrucao.ljust(25)}\t{{R{',R'.join([str(r) for r in reg_list])}}}=MEM[0x{sp:08X}]{{0x{',0x'.join([f'{R[r]:08X}' for r in reg_list])}}}")                   
                """

            pc = R[29]
            z = (R[28] & (0b11111 << 21)) >> 21
            x = (R[28] & (0b11111 << 16)) >> 16
            y = (R[28] & (0b11111 << 11)) >> 11
            v = (R[28] & (0b11111 << 6)) >> 6
            w = R[28] & 0b111111
            valores = [v, w, x, y, z]
            mem_values = []
            sp = R[30]
            for j in range(len(valores)):
                i = valores[j]
                if i != 0:
                    R[30] += 4
                    R[i] = MEM32[R[30]]
                    mem_values.append("0x{:08X}".format(R[i]))

            rname = [rs.get(i, "r" + str(i)) for i in valores if i != 0]
            print("0x{:08X}:\t{:25s}\t{}=MEM[0x{:08X}]{}".format(pc, "pop " + (", ".join(rname) if any(i != 0 for i in valores) else "-"), "{" + ",".join([l.upper() for l in rname]) + "}", sp,
                    "{" + ",".join(["0x{:08X}".format(R[valores[j]]) if R[valores[j]] >= 0 else "0x{:08X}".format(R[valores[j]] & (2**32-1)) for j in range(len(valores)) if valores[j] != 0]) + "}"))

        elif opcode == 0b100001:  # sbr e cbr
            z = (R[28] & (0b11111 << 21)) >> 21
            x = (R[28] & (0b11111 << 16)) >> 16

            if (R[28] & 1) == 1:  # sbr
                R[z] = R[z] | (1 << x)
                instrucao = f'sbr r{z}[{x}]'
                print(f'0x{R[29]:08X}:\t{instrucao.ljust(25)}\tR{z}=0x{R[z]:08X}')
                if z == 31 and x == 1:
                    IE = 1

            elif (R[28] & 1) == 0:  # cbr
                R[z] = R[z] & ~(1 << x)
                instrucao = f'cbr r{z}[{x}]'
                print(f'0x{R[29]:08X}:\t{instrucao.ljust(25)}\tR{z}=0x{R[z]:08X}')
                if z == 31 and x == 1:
                    IE = 0
                """if z == 2 and R[z] == 4:
                    R[z] = 20 """

        elif opcode == 0b111111:  # int
            i = (R[28] & (0b11111111111111111111111111))
            instrucao = f"int {i}"
            if i == 0:
                print(
                    f"0x{R[29]:08X}:\t{instrucao.ljust(25)}\tCR=0x00000000,PC=0x00000000")
                executa = False
                print(''.join(terminal))
            else:
                pc = R[29]
                MEM32[R[30]] = R[29] + 4
                R[30] -= 4
                MEM32[R[30]] = R[26]
                R[30] -= 4
                MEM32[R[30]] = R[27]
                R[30] -= 4
                R[26] = i
                R[27] = R[29]
                R[29] = 0x0000000C

                print(
                    f"0x{pc:08X}:\t{instrucao.ljust(25)}\tCR=0x{R[26]:08X},PC=0x{R[29]:08X}")
                R[29] -= 4
                print('[SOFTWARE INTERRUPTION]')
        else:
            # Exibindo mensagem de erro
            MEM32[R[30]] = R[29] + 4
            R[30] -= 4
            MEM32[R[30]] = R[26]
            R[30] -= 4
            MEM32[R[30]] = R[27]
            R[30] -= 4

            print(f"[INVALID INSTRUCTION @ 0x{R[29]:08X}]")
            print("[SOFTWARE INTERRUPTION]")
            IV = 1
            flags_changed = IV != 0
            if flags_changed:
                SR = (IV << 2)

            R[29] = 0
            # Parar a execução
            # executa = False

        # watchdog
        if counter_ID == True and counter > 0:
            counter -= 1
        if counter == 0:
            counter_ID = False
            EN = 1
        if IE == 1 and counter == 0:
            print("[HARDWARE INTERRUPTION 1]")

            MEM32[R[30]] = R[29] + 4
            R[30] -= 4
            MEM32[R[30]] = R[26]
            R[30] -= 4
            MEM32[R[30]] = R[27]
            R[30] -= 4
            R[29] = 0x0000000C
            R[26] = 0xE1AC04DA
            counter = None

        # PC = PC + 4 (próxima instrução)
        R[29] = R[29] + 4
        SR = R[31]
        # print(counter,  IE, counter_ID)
        # Exibindo a finalização da execução
    print("[END OF SIMULATION]")

    entrada.close()
    sys.stdout.close()

# Executando a funcao main
if __name__ == '__main__':
    # Passando os argumentos do programa
    main(sys.argv)
