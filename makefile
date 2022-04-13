
fw:ide build
sdk:ide sdk


ide:
	@make -s ide_s
ide_s:
	python ./compiler/front_end/front.py /home/btfz/Desktop/linshi/mesh_sample ./samples/mesh_node_sample tlsr825x_smesh ./output mesh_node_sample 1.0.0

build:
	python compiler/back_end/back.py 'build' ./project.json

sdk:
	python compiler/back_end/back.py 'sdk' ./project.json

clean:
	@find ./ -name "__pycache__" | xargs -I {} rm -rf {}
	@rm project.json
