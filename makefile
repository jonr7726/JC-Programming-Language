INPUT = input.jc
OUTPUT = output

all:
	python3 main.py -ir $(INPUT) -o $(OUTPUT)

interpret:
	python3 main.py -ir $(INPUT) -o $(OUTPUT) -i

ir:
	llc -filetype=obj $(OUTPUT).ll
	gcc $(OUTPUT).o -o $(OUTPUT) -no-pie