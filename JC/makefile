INPUT = input.jc
OUTPUT = output
TEST = test

all:
	python3 ../main.py -ir $(INPUT) -o $(OUTPUT)

interpret:
	python3 ../main.py -ir $(INPUT) -o $(OUTPUT) -i

debug:
	python3 ../main.py -ir $(INPUT) -o $(OUTPUT) -i -d

ir:
	llc -filetype=obj $(OUTPUT).ll
	gcc $(OUTPUT).o -o $(OUTPUT) -no-pie

c:
	clang -S -emit-llvm $(TEST).c

test:
	llc -filetype=obj $(TEST).ll
	gcc $(TEST).o -o $(TEST) -no-pie