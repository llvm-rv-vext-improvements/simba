.macro XiangShanTrap arg
    li a0, 0
    .word 0x5006b
.endm

.section .text.startup

.global _start
_start:
    li sp, 0x80001000

    li a0, 3
    li a1, 4
    call sum

    XiangShanTrap 0
