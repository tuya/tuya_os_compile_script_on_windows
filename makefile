
fw:ide build
sdk:ide sdk


ide:
	@make -s ide_s
ide_s:
	python ide_tool.py 'front' C:/Users/Administrator/Workspace2/mesh_sample ./samples/mesh_node_sample tlsr825x_smesh ./output mesh_node_sample 1.0.0

build:
	python ide_tool.py 'build' ./project.json

sdk:
	python ide_tool.py 'sdk' ./project.json

clean:
	@find ./ -name "__pycache__" | xargs -I {} rm -rf {}
	@rm project.json
