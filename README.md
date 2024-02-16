# arq-poxim-simulator
Considerando a arquitetura Poxim, contruído um simulador em python que realize o carregamento da
programação (código binário representado em
formato hexadecimal) e executado passo a passo o seu
comportamento (fluxo de execução em arquivo).  
  
Arquitetura Poxim:  
- Complexity-Reduced Instruction Set Processor (CRISP)  
- Didática, hipotética e simples com 32 bits  
- Memória Von Neumann de 32 KiB  
- 3 formatos de instruções
  
Funcionalidades:
- Implementação de registradores de memória  
- Operações aritméticas e lógicas:  
 Adição (add, addi)  
 Atribuição imediata (mov, movs)  
 Bit a bit (and, or, not, xor)  
 Comparação (cmp, cmpi)  
 Deslocamento (sla, sll, sra, srl)  
 Divisão (div, divs, divi)  
 Multiplicação (mul, muls, muli)  
 Subtração (sub, subi)
- Utilização de Sub-rotinas:  
  Operação de chamada de sub-rotina (call)  
  Operação de retorno de sub-rotina (ret)  
  Operação de empilhamento (push)  
  Operação de desempilhamento (pop)  
- Controle de Fluxo para Interrupção:  
  Operação de retorno de interrupção (reti)  
  Operação de limpeza de bit de registrador (cbr)  
  Operação de ajuste de bit de registrador (sbr)  
  Operação de interrupção de software (int)  
- Dispositivos de E/S mapeados em memória:  
  Temporizador (Watchdog)  
  Unidade de Ponto Flutuante (FPU)  
  Interface serial de texto (Terminal)  




Observações:
- Operaçoes com FPU incompletos
- Aprimorar o Status Register (SR)
- Alterar estrutura do codigo (otimização em relação a quantidade de "elif")
