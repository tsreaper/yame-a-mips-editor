.text
main:	la $1, data		# address of data[0]
	addi $4, $1, 80		# address of data[0]
call:	addi $5, $0, 4		# counter
	jal sum			# call function
return:	sw $2, 0($4)		# store result
	lw $9, 0($4)		# check sw
	sw $9, 4($4)		# store result again
	addi $8, $9, -96	# $8 <- $9 - 96

print:	li $2, 1		# print $8
	add $4, $8, $0		# print $8
	syscall			# print $8 (should be 0x1f8 = 504)
	li $2, 11		# print space
	li $4, 32		# print space
	syscall			# print space
	li $2, 1		# print $9
	add $4, $9, $0		# print $9
	syscall			# print $9 (should be 0x258 = 600)
	li $2, 10		# exit
	syscall			# exit

sum:	add $8, $0, $0		# sum function entry
loop:	lw $9, 0($4)		# load data
	add $8, $8, $9		# sum
	addi $5, $5, -1		# counter - 1
	addi $4, $4, 4		# address + 4
	slt $3, $0, $5		# finish?
	bne $3, $0, loop	# finish?
	or $2, $8, $0		# move result to $v0
	jr $ra			# return
	nop			# done

.data
data:	.word	0xBF800000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x000000A3, 0x00000027, 0x00000079, 0x00000115, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000, 0x00000000
