
all:ide build


ide:
	python ./compiler/front_end/front.py ~/Desktop/linshi/mesh_sample/output/dist/TuyaOS mesh_node_sample tlsr825x_smesh ./ mesh_node_sample 1.0.0

build:
	python compiler/back_end/build.py ./project.json

clean:
	@find ./ -name "__pycache__" | xargs -I {} rm -rf {}
	@rm project.json
