
all:ide build


ide:
	@make -s ide_s
ide_s:
	python ./compiler/front_end/front.py /home/btfz/Desktop/linshi/mesh_sample ./samples/mesh_node_sample tlsr825x_smesh ./ mesh_node_sample 1.0.0

build:
	python compiler/back_end/back.py ./project.json

clean:
	@find ./ -name "__pycache__" | xargs -I {} rm -rf {}
	@rm project.json
