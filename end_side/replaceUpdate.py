import onnx
from onnx import helper, numpy_helper
import numpy as np

def optimize_model(model):
    """
    对模型进行优化，例如删除不必要的节点，融合可以融合的操作等
    """
    # 可以加一些模型级别的优化操作
    # 例如：onnx.optimizer.optimize(model, ['eliminate_identity', 'fuse_bn_into_conv'])
    return model

def replace_unsupported_ops(model_path, output_path):
    try:
        model = onnx.load(model_path)
        graph = model.graph
        
        new_nodes = []
        for node in graph.node:
            if node.op_type == 'SkipLayerNormalization':
                new_nodes.extend(replace_skip_layer_normalization(node))
            elif node.op_type == 'FusedMatMul':
                new_nodes.extend(replace_fused_matmul(node))
            elif node.op_type == 'BiasGeLU':
                new_nodes.extend(replace_bias_gelu(node))
            elif node.op_type == 'Attention':  # 新增对Attention的支持
                new_nodes.extend(replace_attention(node))
            else:
                new_nodes.append(node)
        
        # 创建新的图和模型
        new_graph = helper.make_graph(new_nodes, graph.name, graph.input, graph.output, graph.initializer)
        new_model = helper.make_model(new_graph, producer_name='optimized-onnx-model')
        
        # 模型优化
        optimized_model = optimize_model(new_model)
        
        # 检查模型有效性
        onnx.checker.check_model(optimized_model)
        
        # 保存新模型
        onnx.save(optimized_model, output_path)
        print(f"Optimized model saved to {output_path}")
    except Exception as e:
        print(f"Error occurred: {str(e)}")

def replace_skip_layer_normalization(node):
    input_name, skip_input_name = node.input[0], node.input[1]
    output_name = node.output[0]
    
    add_node = helper.make_node('Add', [input_name, skip_input_name], ['add_output'])
    layernorm_node = helper.make_node('LayerNormalization', 
                                      ['add_output'] + node.input[2:], 
                                      [output_name],
                                      epsilon=node.attribute[0].f)
    
    return [add_node, layernorm_node]

def replace_fused_matmul(node):
    input_a, input_b = node.input[0], node.input[1]
    output_name = node.output[0]
    
    matmul_node = helper.make_node('MatMul', [input_a, input_b], ['matmul_output'])
    add_node = helper.make_node('Add', ['matmul_output', node.input[2]], [output_name])
    
    return [matmul_node, add_node]

def replace_bias_gelu(node):
    input_name, bias_name = node.input[0], node.input[1]
    output_name = node.output[0]
    
    add_node = helper.make_node('Add', [input_name, bias_name], ['bias_add_output'])
    gelu_node = helper.make_node('Gelu', ['bias_add_output'], [output_name])
    
    return [add_node, gelu_node]

def replace_attention(node):
    # 这是一个简化的Attention实现，实际需要check结果，尝试复杂的替换
    query, key, value = node.input[0], node.input[1], node.input[2]
    output_name = node.output[0]
    
    matmul1 = helper.make_node('MatMul', [query, key], ['attn_scores'])
    softmax = helper.make_node('Softmax', ['attn_scores'], ['attn_probs'])
    matmul2 = helper.make_node('MatMul', ['attn_probs', value], [output_name])
    
    return [matmul1, softmax, matmul2]

# Test
replace_unsupported_ops('input_model.onnx', 'optimized_output_model.onnx')