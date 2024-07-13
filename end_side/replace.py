import onnx
from onnx import helper, numpy_helper
import numpy as np

def replace_unsupported_ops(model_path, output_path):
    model = onnx.load(model_path)
    graph = model.graph
    
    new_nodes = []
    for node in graph.node:
        if node.op_type == 'SkipLayerNormalization':
            # 替换 SkipLayerNormalization
            input_name = node.input[0]
            skip_input_name = node.input[1]
            output_name = node.output[0]
            
            add_node = helper.make_node('Add', [input_name, skip_input_name], ['add_output'])
            layernorm_node = helper.make_node('LayerNormalization', 
                                              ['add_output'] + node.input[2:], 
                                              [output_name],
                                              epsilon=node.attribute[0].f)
            
            new_nodes.extend([add_node, layernorm_node])
        
        elif node.op_type == 'FusedMatMul':
            # 替换 FusedMatMul
            input_a = node.input[0]
            input_b = node.input[1]
            output_name = node.output[0]
            
            matmul_node = helper.make_node('MatMul', [input_a, input_b], ['matmul_output'])
            add_node = helper.make_node('Add', ['matmul_output', node.input[2]], [output_name])
            
            new_nodes.extend([matmul_node, add_node])
        
        elif node.op_type == 'BiasGeLU':
            # 替换 BiasGeLU
            input_name = node.input[0]
            bias_name = node.input[1]
            output_name = node.output[0]
            
            add_node = helper.make_node('Add', [input_name, bias_name], ['bias_add_output'])
            gelu_node = helper.make_node('Gelu', ['bias_add_output'], [output_name])
            
            new_nodes.extend([add_node, gelu_node])
        
        else:
            new_nodes.append(node)
    
    # 创建新的图和模型
    new_graph = helper.make_graph(new_nodes, graph.name, graph.input, graph.output, graph.initializer)
    new_model = helper.make_model(new_graph, producer_name='onnx-example')
    
    # 保存新模型
    onnx.save(new_model, output_path)

replace_unsupported_ops('input_model.onnx', 'output_model.onnx')


# 安装必要的库：pip install onnx numpy
# 将脚本保存为 Python 文件，例如 replace_ops.py
# 在脚本中设置输入模型路径和输出模型路径
# 运行脚本：python replace_ops.py