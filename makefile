INPUT = input.jc
OUTPUT = output

all:
	python main.py -ir $(INPUT) -o $(OUTPUT)

interpret:
	python main.py -ir $(INPUT) -o $(OUTPUT) -i

ir:
	llc -filetype=obj $(OUTPUT).ll
	gcc $(OUTPUT).o -o $(OUTPUT) -no-pie