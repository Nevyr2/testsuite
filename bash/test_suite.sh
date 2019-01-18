#!/bin/sh
RED="\033[0;31;1m"
GREEN="\033[0;32;1m"
YELLOW="\033[0:33;1m"
PINK="\033[0:35;1m"
CYAN="\033[0:36;1m"
NC="\033[0m"

NumTest=0
FullPassTest=" "
FullErrorTest=" "
NameTest=" "
PassTest=0
ErrorTest=0
name=" "

echo
printf "${CYAN}    ___ ____ ____ ___     ___  _  _ _ ___  ___\n"
printf "${CYAN}     |  |___ [__   |      [__  |  | |  |  |___ \n"
printf "${CYAN}     |  |___ ___]  |      ___] |__| |  |  |___\n ${NC}"
echo

mkdir tests/ast_png

for i in tests/cmd_test/*; do
    file=$(echo $i | cut -d'/' -f3)
    echo
    echo "$file commands :"
    echo
    name=cmd_test/$file
    PassTest=0
    ErrorTest=0
    while read line; do
        NumTest=$((NumTest + 1))
        T=$(./42sh -c $line 2>/dev/null)
        error=$?
        expected=$(bash -c "$line" 2>/dev/null)
        if [ "$T" = "$expected" ]; then
            printf " ${GREEN}[PASS] ${NC}"
            PassTest=$((PassTest + 1))
        else 
            ErrorTest=$((ErrorTest + 1))
            printf " ${RED}[FAIL] ${NC}"
        fi
        printf "TEST $NumTest : ./42sh $line\n"

	./42sh -c --ast-print $line 2>/dev/null 0>/dev/null 1>/dev/null
	dot -Tpng ast.dot > ast_test$NumTest.png 2>/dev/null 0>/dev/null 1>/dev/null

	mv ast_test$NumTest.png tests/ast_png

    done < tests/$name
    FullPassTest="$FullPassTest$PassTest,"
    FullErrorTest="$FullErrorTest$ErrorTest,"
    NameTest="$NameTest$file,"
done

echo
for i in {0..4}; do
    for j in {0..50}; do
        if [ $i == 3 ]; then
            printf "_"
        elif [ $i == 1 ]; then
            if [ $j == 5 ]; then
                printf "commands"
            elif [ $j == 18 ]; then
                printf "|${GREEN} Test Pass${NC}  |"
            elif [ $j == 20 ]; then
                printf "${RED} Test Failed${NC}"
            else
                printf " "
            fi 
        elif [ $i == 25 ]; then
            printf "_"
        elif [ $j == 25 ]; then
            printf "|"
        elif [ $j == 38 ]; then
            printf "|"
        else
            printf " " 
        fi
    done
    printf "\n"
done

while [ ! $FullPassTest = "" ] ; do
    PassTest=$(echo $FullPassTest | cut -d',' -f1)
    FullPassTest=$(echo $FullPassTest | cut -d',' -f2-)
    ErrorTest=$(echo $FullErrorTest | cut -d',' -f1)
    FullErrorTest=$(echo $FullErrorTest | cut -d',' -f2-)
    file=$(echo $NameTest | cut -d',' -f1)
    NameTest=$(echo $NameTest | cut -d',' -f2-)

    printf " $file cmd :"
    length=$((18 - ${#file}))
    for i in `seq 1 $length`; do
        printf " "
    done
    printf "|"

    length=$((7 - ${#PassTest}))
    printf "     ${GREEN}$PassTest${NC}"
    for i in `seq 1 $length`; do
        printf " "
    done
    printf "|"

    printf "     ${RED}$ErrorTest${NC}"
    printf "\n"
done
echo
echo
