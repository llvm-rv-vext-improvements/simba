.macro XiangShanTrap arg
    li a0, 0
    .word 0x5006b
.endm

.section .text.startup

.global _start
_start:
    XiangShanTrap 0
