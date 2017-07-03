# This program generates a random digit number with unique digits given a 
# length value input by the user (sized values of 1 to 9), and asks the user
# to try to guess the generated number. For every digit the guess shares with the generated
# number, the program prints the word Pico, but if the digit is in the same locations, it prints
# Fermi. If no digits are shared, the program prints Bagel. If the user gives up they can input
# 0 and the program will show them the generated value, along with the number of times
# the user guessed incorrently.
# By Alex Plaza

.data

init1:      .asciiz "\nThe computer has generated a "
init2:      .asciiz " digit random number with unique digits. Try to guess it, or input 0 to give up."
getLength:  .asciiz "Select length of target b/w 1-9: "
iPrompt:    .asciiz "\nPlease enter your guess: "
Fermi:      .asciiz "Fermis"
Pico:       .asciiz "Pico"
Bagel:      .asciiz "Bagel"
win:        .asciiz "\nYou Won!!"
newLine:    .asciiz "\n"
targetp:    .asciiz "\nTarget Was: "
counter:    .asciiz "Guesses: "

targetArray:    .word 0,0,0,0,0,0,0,0,0
guessArray:     .word 0,0,0,0,0,0,0,0,0
guessCounter:   .word 0

.text 

main:
    la $s5, guessCounter    # s5 = guessCounter: counts the number of guesses
    lw $s5, 0($s5)
    
    la $a0, getLength
    li $v0, 4
    syscall                 # print message to get length from user
    
    li $v0, 5
    syscall
    move $t9, $v0           # move user input into t9
    
    la $a0, targetArray     # a0 = address of the targetArray
    move $a1, $t9           # a1 = length
    jal GenerateNumber      # GenerateNumber(targetArray, length)
    move $s7, $v0           # s7 = TargetNumber (NOT THE ARRAY, BUT THE ACTUAL NUMBER)
    
    la $a0, init1           # print initial message
    li $v0, 4
    syscall
    
    move $a0, $t9           # print length
    li $v0, 1
    syscall
    
    la $a0, init2
    li $v0, 4
    syscall

    # Uncomment the code below to "cheat" and
    # see the generated number before start guessing
    
    # move $a0, $t9
    # la $a1, targetArray
    # jal printList
    
    # la $a0, newLine
    # li $v0, 4
    # syscall

game:
    move $a0, $s7
    la $a1, guessArray 
    move $a2, $t9
    jal getInput        #getInput(generatedNumber, addressGuessArray, length)
    
    la $a0, targetArray
    la $a1, guessArray
    move $a2, $t9
    jal CompareArrays   #CompareArrays(addressTargetArray, addressGuessArray, length)
    
    j game

#-------------------- GenerateNumber --------------------#
# The function GenerateNumber takes as a parameter
# the array where the generated number will be stored.
#
# It generates a random number b/t 10*length*1
# and 10*length*9 using syscall 42 (i.e. if length = 4
# then the generated  number is between 1000-9990).
#
# Then, it separates the digits in the generated number 
# and stores them in the array that was passed as a
# parameter.
#
# Then it checks if the digits of the number are unique,
# if they are not, it generates a random number again.
#
# At the end the function will return the generated number,
# and the digits of generated number will be in the array passed.

GenerateNumber:
    #########   Allocate Stack Space  #########
    addi $sp, $sp, -12      # allocate stack space for 3 values
    sw $ra, 0($sp)
    sw $s3, 4($sp)
    sw $s4, 8($sp)

    #########  Init variables  #########
    move $s3, $a0           # s3 = array address
    move $s4, $a1           # s4 = length or array
    move $t8, $0            # t8-t1 auxiliary variables used for intermidiate calculations.
    move $t7, $0        
    move $t5, $0
    move $t4, $0
    move $t3, $0
    move $t1, $0

GenerateRandom: 
    #########   Generate Random Number  #########
    move $t0, $s4       # t0 = i
    li $t7, 1           # lower bound for random
    li $a1, 8           # upper bound for random

CreateLimit:
    beqi $t0, 1, generate       # if i != 1
    
    muli $a1, $a1, 10           # mul lupper bound by 10
    muli $t7, $t7, 10           # mul lowe bound by 10
    addi $t0, $t0, -1           # i--
    
    j CreateLimit

generate:
    li $v0, 42                  # generates random number and places it in a0
    syscall
    add $t8, $a0, $t7           # t8 = target number
    
    move $a0, $t8
    move $a1, $s3
    move $a2, $s4
    jal SeparateNumbers         # SeparateNumbers(generatedNumber, addressTargetArray, length)
    
    move $t6, $0                # i = 0
    move $t2, $0        
    addi $t2, $t2, 1            # j = 1

UniqueLoop:                     # check if generated number has unique digits
    bge $t6, $s4, EndUnique     # if i < length
    
    sll $t5, $t6, 2
    add $t4, $s3, $t5
    lw $t3, 0($t4)             # t3 = array[i]

InnerUnique:
    bge $t2, $s4, EndInnerUnique    # if j < length
    
    sll $t5, $t2, 2
    add $t4, $s3, $t5
    lw $t1, 0($t4)                  # t1 = array[j]
    
    beq $t1, $t3, GenerateRandom    # if array[i] = array[j]
    addi $t2, $t2, 1
    
    j InnerUnique

EndInnerUnique:
    addi $t6, $t6, 1    # i++
    addi $t2, $t6, 1    # j = i+1
    j UniqueLoop

EndUnique:
    #########   Prepare Return Values   #########
    move $v0, $t8       # move generated number to retun register
    #########   Restore Stack Space   #########
    lw  $ra, 0($sp)
    lw  $s3, 4($sp)
    lw  $s4, 8($sp)
    addi $sp, $sp, 12
    jr $ra

#-------------------- SeparateNumber --------------------#
# The SeparateNumbers function takes as parameters a number,
# an array address, and the length of the array.
#
# The function separates the digits of the number using
# modulos and divisions, and stores the digits in the
# provided array.

SeparateNumbers:
    #########   Allocate Stack Space  #########
    addi $sp, $sp, -16      # allocate stack space for 4 values
    sw $ra, 0($sp)
    sw $s0, 4($sp)
    sw $s1, 8($sp)
    sw $s2, 12($sp)
    #########  Init variables  #########
    move $s0, $a0           # s0 = number to split
    move $s1, $a1           # s1 = address of array
    move $s2, $a2           # s2 = length
    li $t0, 1               # t0-t4 auxiliary variables used for intermidiate calculations.
    li $t1, 10
    move $t2, $0        
    move $t3, $0
    move $t4, $0
    move $t5, $s2
    addi $t5, $t5, -1       # t5 = index = length - 1

SeparateLoop:
    #########   Separate Numbers  #########
    bltz $t5, EndSeparate       # if index >= 0
    
    div $s0, $t1        
    mfhi $t2                    # t2 = s0 % t1
    div $t2, $t0        
    mflo $t3                    # t3 = t2/t0 (integer division) --> ith digit
    
    sll $t4, $t5, 2     
    add $t6, $s1, $t4           # t6: get offset for array[index*4]
    sw $t3, 0($t6)              # Store digit t3 in array[index*4]
    addi $t5, $t5, -1           # i--
    
    muli $t0, $t0, 10
    muli $t1, $t1, 10
    
    j SeparateLoop

EndSeparate:        
    #########   Restore Stack Space  #########
    lw $ra, 0($sp)
    lw $s0, 4($sp)
    lw $s1, 8($sp)
    lw $s2, 12($sp)
    addi $sp, $sp, 16
    jr $ra  

#-------------------- getInput --------------------#
# getInput takes as a a parameter the target number
# and the address of the guessArray.
#
# It prompts the user to input a guess, then it
# increases the guess counter, then if the target is
# equal to the guess, go to Win, and if the target is
# the special input 0 go to Terminate.
#
# Otherwise, separate the digits of the guess number
# and store the digits in the provided array.

getInput:
    #########   Allocate Stack Space  #########
    addi $sp, $sp, -16  # allocate stack space for 3 values
    sw $ra, 0($sp)
    sw $s7, 4($sp) 
    sw $s6, 8($sp)
    sw $s4, 12($sp)
    #########  Init variables  #########
    move $s4, $a2       # s4 = length
    move $s6, $a1       # s6 = guessArray
    move $s7, $a0       # s7 = target number
    move $t5, $0        # t5-t6 = auxiliary variables used for intermidiate operations
    move $t6, $0
    #########  Print prompt and get guess from user  #########
    la $a0, iPrompt
    li $v0, 4
    syscall             # print please input guess
    
    li $v0, 5
    syscall
    move $t6, $v0       # t6 = guess
    
    addi $s5, $s5, 1    # guessCounter++
    
    beq $t6, $s7, Win           # if the targetNumber and guessNumber are equal go to Win 
    beq $t6, $zero, Terminate   # if input is 0 go to Terminate
    j SeparateGuess             # if none of the beq above are true, 
                                # continue to separate the digits in guess

Win:
    #########   Print Win Message  #########
    la $a0, win
    li $v0, 4
    syscall             # print you Won!!
    
    la $a0, newLine     # print new line
    li $v0, 4
    syscall
    
    la $a0, counter     # guesses: 
    li $v0, 4
    syscall
    
    move $a0, $s5       # print guessCounter
    li $v0, 1
    syscall 
    
    li $v0, 10
    syscall

Terminate:
    #########   Print Terminate Message  #########
    addi $s5, $s5, -1
    
    la $a0, targetp     # print target was:
    li $v0, 4
    syscall
    
    move $a0, $s4
    la $a1, targetArray
    jal printList       # printList(length, addressTargetArray)
    
    la $a0, newLine     # print new line
    li $v0, 4
    syscall
    
    la $a0, counter     # guesses: 
    li $v0, 4
    syscall
    
    move $a0, $s5       # print guessCounter
    li $v0, 1
    syscall 
    
    li $v0, 10
    syscall

SeparateGuess:
    #########  Separate digits in guess  #########
    move $a0, $t6       
    move $a1, $s6
    move $a2, $s4
    jal SeparateNumbers     # SeparateNumbers(guessedNumber, guessArray, length)
    
    #########   Restore Memory  #########
    lw $ra, 0($sp)
    lw $s7, 4($sp)
    lw $s6, 8($sp)
    lw $s4, 12($sp)
    addi $sp, $sp, 16      
    jr $ra

#-------------------- CompareArrays --------------------#
# The function ComapareArrays takes as parametes two arrays,
# and the length of the arrays (it assumes the leght of both
# arrays is equivalent). It compares the two arrays using
# two loops.
#
# Each number of array1 is compared with each number of array2.
#
# If, any of the number are the same, generate a message
# accordingly.
#
# If the comparison is over and no picos or fermis were
# printed, print bagel.

CompareArrays:
    #########   Allocate Stack Space  #########
    addi $sp, $sp, -12      # allocate stack space for 3 values
    sw $ra, 0($sp)
    sw $s0, 4($sp)
    sw $s1, 8($sp)
    #########   init Variables  #########
    move $s0, $a0           # s0 = array1
    move $s1, $a1           # s1 = array2
    move $s2, $a2           # s2 = lenght
    move $t3, $0            # t3 = Fermis and Pico Counter
    move $t4, $0            # t4 = aux = 0
    move $t6, $0            # t6 = aux = 0
    move $t7, $0            # t7 = i = 0
    move $t5, $0            # t5 = j = 0

CompareLoop:
    #########   Compare Numbers  #########
    bge $t7, $s2, EndCompare    # if i < length
    
    sll $t6, $t7, 2
    add $t4, $s0, $t6
    lw $t0, 0($t4)              # t0 = array1[i]

Inner:  
    bge $t5, $s2, EndInner      # if j < length
    
    sll $t6, $t5, 2
    add $t4, $s1, $t6
    lw $t1, 0($t4)              # t1 = array2[i]
    
    beq $t0, $t1, generateMessage   # if array[i] = array[j] generate a message.
    addi $t5, $t5, 1
    
    j Inner

generateMessage:
    #########   Generate Message  #########
    addi $t3, $t3, 1            # Fermis&PicoCounter++
    beq $t7, $t5, printFermi    # if i = j
    
    #########   Print Pico   #########
    la $a0, newLine
    li $v0, 4
    syscall
    
    la $a0, Pico
    li $v0,  4
    syscall
    addi $t5, $t5, 1
    
    j Inner

printFermi:
    #########   Print Fermi   #########
    la $a0, newLine
    li $v0, 4
    syscall
    
    la $a0, Fermi
    li $v0,  4
    syscall
    addi $t5, $t5, 1
    
    j Inner

printBagel:
    #########   Print Bagel   #########
    la $a0, newLine
    li $v0, 4
    syscall
    
    la $a0, Bagel
    li $v0, 4
    syscall
    
    j afterBagel

EndInner:
    #########   End Inner loop and Restart outer loop  #########
    move $t5, $0        # restart inner loop j = 0
    addi $t7, $t7, 1    # j++
    j CompareLoop

EndCompare:
    #########   Print Bagel if necessary, and end function  #########
    beqz $t3, printBagel    # if no picos or fermis were printer, print bagel

afterBagel:
    #########   Restore Stack Space  #########
    lw $ra, 0($sp)        
    lw $s0, 4($sp)
    lw $s1, 8($sp)
    addi $sp, $sp, 12
    jr $ra
        
#-------------------- printList --------------------#
# Function printList take as parameters the length of
# the array and its address and loops over the elements
# and prints them one by one.
#
# No need to allocate stack space since this function
# isn't using s register.

printList:
    move $t0, $0            # t0: index i = 0
    move $t1, $a0           # t1: arryLength
    move $t2, $a1           # t2: Address

printLoop:
    bge $t0, $t1, endPrint  # if i < arrayLength
    
    lw $a0, 0($t2)          # print element
    li $v0, 1
    syscall
    
    addi $t0, $t0, 1        # ++i
    addi $t2, $t2, 4        # Address = address + 4
    j printLoop

endPrint:
    jr  $ra
