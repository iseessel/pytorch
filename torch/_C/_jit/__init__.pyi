# @generated from torch/_C/_jit/__init__.pyi.in

import torch
from torch import Tensor
from enum import Enum
from pathlib import Path
from typing import (
    Any, BinaryIO, Callable, ContextManager, Dict, Iterable, Iterator, List,
    NamedTuple, Optional, overload, Sequence, Tuple, TypeVar, Type, Union,
    Generic, Set, AnyStr)
from typing_extensions import Literal
from torch._six import inf

from torch.types import _int, _float, _bool, _dtype, _device, _qscheme, _size, _layout, Device, Number, Storage

import builtins

from .. import _onnx as _onnx


# Defined in torch/csrc/jit/python/init.cpp
class IODescriptor: ...

class JITException: ...

class Future(object):
  def __init__(self) -> None: ...
  def done(self) -> _bool: ...
  def wait(self) -> Any: ...
  def add_done_callback(self, callback: Callable) -> None: ...
  def then(self, callback: Callable) -> Future: ...
  def set_result(self, result: Any) -> None: ...
  def _set_unwrap_func(self, callback: Callable) -> None: ...

def set_num_profiled_runs(num: _size) -> _size: ...

# Defined in torch/csrc/jit/passes/xnnpack_rewrite.h
class MobileOptimizerType:
    ...

CONV_BN_FUSION: MobileOptimizerType
INSERT_FOLD_PREPACK_OPS: MobileOptimizerType
REMOVE_DROPOUT: MobileOptimizerType
FUSE_ADD_RELU: MobileOptimizerType
HOIST_CONV_PACKED_PARAMS: MobileOptimizerType

def fork(*args: Any, **kwargs: Any) -> Future: ...
def wait(fut: Future) -> Any: ...
def _collect_all(futures: List[Future]) -> Future: ...

def unify_type_list(types: List[JitType]) -> JitType: ...
def _freeze_module(module: ScriptModule,
                   preserved_attrs: List[str] = [],
                   freeze_interfaces: _bool = True,
                   preserveParameters: _bool = True) -> ScriptModule: ...
def pass_optimize_frozen_graph(Graph) -> None: ...
def _is_tracing() -> _bool: ...
def init() -> _bool: ...
def flatten(arg: Any) -> Tuple[List[Tensor], IODescriptor]: ...
def unflatten(vars: List[Tensor], desc: IODescriptor) -> Any: ...
def get_operation(op_name: str) -> Callable: ...
def pass_optimize_for_mobile(module: 'torch.jit.ScriptModule',
                                  optimization_blocklist: Set[MobileOptimizerType],
                                  preserved_methods: List[AnyStr]) -> 'torch.jit.ScriptModule': ...
def pass_vulkan_optimize_for_mobile(module: 'torch.jit.ScriptModule',
                                         preserved_methods: List[AnyStr]) -> 'torch.jit.ScriptModule': ...
def pass_metal_optimize_for_mobile(module: 'torch.jit.ScriptModule',
                                         preserved_methods: List[AnyStr]) -> 'torch.jit.ScriptModule': ...
def pass_inline(Graph) -> None: ...
def pass_constant_propagation(Graph) -> None: ...
def get_schemas_for_operator(name :str) -> List[FunctionSchema]: ...
def check_alias_annotation(g: Graph, args: Tuple[Any, ...], unqualified_op_name: str): ...
def can_fuse_on_cpu() -> _bool: ...
def can_fuse_on_gpu() -> _bool: ...
def _debug_get_fusion_group_inlining() -> _bool: ...
def _debug_set_fusion_group_inlining(enable: _bool): ...
def texpr_fuser_enabled() -> _bool: ...
def nvfuser_enabled() -> _bool: ...
def _llvm_enabled() -> _bool: ...
def set_te_must_use_llvm_cpu(use_llvm: _bool): ...
def override_can_fuse_on_cpu(override: _bool): ...
def override_can_fuse_on_gpu(override: _bool): ...
def set_texpr_fuser_enabled(enable: _bool): ...
def set_nvfuser_enabled(enable: _bool) -> _bool: ...
def pass_canonicalize(graph: Graph): ...
def pass_erase_shape_information(graph: Graph): ...
def pass_fold_convbn(module: 'torch.jit.ScriptModule'): ...
def pass_insert_observers(module: 'torch.jit.ScriptModule',
                               method_name: str,
                               qconfig_dict: Dict[str, Any],
                               inplace: _bool,
                               quant_type: _int): ...
def pass_insert_quant_dequant(module: 'torch.jit.ScriptModule',
                                   method_name: str,
                                   inplace: _bool,
                                   debug: _bool,
                                   quant_type: _int): ...
def pass_quant_finalize(module: 'torch.jit.ScriptModule',
                             quant_type: _int,
                             preserved_attrs: Sequence[str]): ...
def set_profiling_executor(profiling_flag: _bool) -> _bool: ...
def set_profiling_mode(profiling_flag: _bool) -> _bool: ...
def try_infer_type(obj: Any) -> InferredType: ...
def get_trigger_value(trigger_name: str) -> _int: ...

# Defined in torch/csrc/jit/python/script_init.cpp
ResolutionCallback = Callable[[str], Callable[..., Any]]

# Defined in torch/csrc/jit/python/script_init.cpp
#        and torch/csrc/jit/python/init.cpp
def _create_function_from_graph(qualname: str, graph: Graph) -> Graph: ...
def _debug_set_autodiff_subgraph_inlining(disabled: _bool) -> None: ...
def _ivalue_tags_match(lhs: ScriptModule, rhs: ScriptModule) -> _bool: ...
def assert_is_instance(obj: Any, type: JitType): ...
def clear_class_registry() -> None: ...
def set_emit_hooks(ModuleHook: Optional[Callable], FunctionHook: Optional[Callable]) -> None: ...
def get_emit_hooks() -> Tuple[Callable, Callable]: ...
def _load_for_lite_interpreter(filename: Union[str, Path], map_location: Union[_device, str, None]): ...
def _load_for_lite_interpreter_from_buffer(buffer: BinaryIO, map_location: Union[_device, str, None]): ...
def _logging_set_logger(logger: LoggerBase) -> LoggerBase: ...
def _get_graph_executor_optimize() -> _bool: ...
def _set_graph_executor_optimize(optimize: _bool): ...
def _export_opnames(module: ScriptModule) -> List[str]: ...
def _create_function_from_trace(
    qualname: str,
    func: Callable[..., Any],
    input_tuple: Tuple[Any, ...],
    var_lookup_fn: Callable[[Tensor], str],
    strict: _bool,
    force_outplace: _bool,
    argument_names: List[str]
) -> Tuple[Graph, Stack]: ...
def is_script_object(obj: Any) -> _bool: ...
def _last_executed_optimized_graph() -> Graph: ...
def parse_type_comment(comment: str) -> Decl: ...
def merge_type_from_type_comment(decl: Decl, type_annotation_decl: Decl, is_method: _bool) -> Decl: ...
def parse_ir(input: str) -> Graph: ...
def parse_schema(schema: str) -> FunctionSchema: ...
def get_device(input: Tensor) -> _int: ...
def _resolve_type_from_object(obj: Any, range: SourceRange, rcb: ResolutionCallback) -> JitType: ...
def _create_module_with_type(ty: JitType) -> ScriptModule: ...
def _run_emit_module_hook(m: ScriptModule): ...
def _replace_overloaded_method_decl(overload_decl: Decl, implementation_def: Def, new_name: str) -> Def: ...

def pass_lower_all_tuples(graph: Graph) -> None: ...
def pass_onnx_set_dynamic_input_shape(graph: Graph, dynamic_axes: Dict[str, Dict[_int, str]], input_names: List[str]) -> None: ...
def pass_onnx_graph_shape_type_inference(graph: Graph, paramsDict: Dict[str, IValue], opset_version: _int) -> None: ...
def pass_onnx_assign_output_shape(graph: Graph, tensors: List[Tensor], desc: IODescriptor, onnx_shape_inference: _bool = False) -> None: ...
def pass_onnx_remove_inplace_ops_for_onnx(graph: Graph, module: Module) -> None: ...
def pass_remove_inplace_ops(graph: Graph) -> None: ...
def pass_remove_dropout(graph: Graph) -> None: ...
def pass_fold_frozen_conv_bn(graph: Graph) -> None: ...
def pass_fold_frozen_conv_add_or_sub(graph: Graph) -> None: ...
def pass_fold_frozen_conv_mul_or_div(graph: Graph) -> None: ...
def pass_canonicalize_graph_fuser_ops(graph: Graph) -> None: ...
def pass_peephole(graph: Graph, addmm_fusion_enabled: _bool) -> None: ...
def pass_fuse_addmm(graph: Graph) -> None: ...
def pass_onnx_preprocess(graph: Graph) -> None: ...
def pass_onnx_prepare_inplace_ops_for_onnx(graph: Graph) -> None: ...
def pass_prepare_division_for_onnx(graph: Graph) -> None: ...
def pass_onnx_remove_print(graph: Graph) -> None: ...
def pass_onnx_preprocess_caffe2(graph: Graph) -> None: ...
def pass_onnx_unpack_quantized_weights(
    graph: Graph,
    paramsDict: Dict[str, IValue]
) -> Dict[str, IValue]: ...
def pass_onnx_quantization_insert_permutes(
    graph: Graph,
    paramsDict: Dict[str, IValue]
) -> Dict[str, IValue]: ...
def pass_custom_pattern_based_rewrite_graph(pattern: str, fused_node_name: str, graph: Graph) -> None: ...
def onnx_list_model_parameters(module: ScriptModule) -> Tuple[ScriptModule, List[IValue]]: ...
def pass_erase_number_types(graph: Graph) -> None: ...
def pass_onnx(graph: Graph, pass_onnx: _onnx.OperatorExportTypes) -> Graph: ...
def pass_onnx_scalar_type_analysis(graph: Graph) -> None: ...
def pass_onnx_peephole(graph: Graph, opset_version: _int, fixed_batch_size: _bool) -> None: ...
def pass_dce_allow_deleting_nodes_with_side_effects(graph: Graph) -> None: ...
def pass_onnx_function_substitution(graph: Graph) -> None: ...
def pass_onnx_fold_if(graph: Graph) -> None: ...
def pass_lower_graph(graph: Graph, m: Module) -> Tuple[Graph, List[IValue]]: ...
def pass_inline_fork_wait(graph: Graph) -> None: ...
def pass_onnx_eval_peephole(graph: Graph, paramsDict: Dict[str, IValue]) -> Dict[str, IValue]: ...
def pass_onnx_constant_fold(graph: Graph, paramsDict: Dict[str, IValue], opset_version: _int) -> Dict[str, IValue]: ...
def pass_onnx_eliminate_unused_items(graph: Graph, paramsDict: Dict[str, IValue]) -> Dict[str, IValue]: ...
def pass_onnx_cast_all_constant_to_floating(graph: Graph) -> None: ...
def pass_filter_non_tensor_arguments(params: Dict[str, IValue]) -> Dict[str, Tensor]: ...
def decay_packed_param_input_types(graph: Graph) -> None: ...
def pass_onnx_node_shape_type_inference(n: Node, paramsDict: Dict[str, IValue], opset_version: _int) -> None: ...
def pass_onnx_block(
    old_block: Block,
    new_block: Block,
    operator_export_type: _onnx.OperatorExportTypes,
    env: Dict[Value, Value]
) -> None: ...
def pass_fixup_onnx_controlflow_node(n: Node, opset_version: _int) -> Node: ...

def script_interface_compile(name: str, class_def: ClassDef, rcb: ResolutionCallback, is_module: _bool): ...
def script_compile_overload(
    qualname: str,
    overload_decl: Decl,
    implementation_def: Def,
    rcb: ResolutionCallback,
    implementation_defaults: Dict[str, Any],
    signature: Any
): ...
def script_compile(
    qual_name: str,
    definition: Def,
    rcb: ResolutionCallback,
    defaults: Dict[str, Any]
): ...
def script_class_compile(
    qual_name: str,
    definition: ClassDef,
    defaults: Dict[str, Dict[str, Any]],
    rcb: ResolutionCallback,
): ...
def _parse_source_def(src: str) -> Def: ...
def import_ir_module(
    cu: CompilationUnit,
    filename: Union[str, Path],
    map_location: Union[_device, str, None],
    extra_files: Dict[str, Any]
) -> ScriptModule: ...
def import_ir_module_from_buffer(
    cu: CompilationUnit,
    buffer: BinaryIO,
    map_location: Union[_device, str, None],
    extra_files: Dict[str, Any]
) -> ScriptModule: ...

def _assign_output_shapes(graph: Graph, inputs: List[Tensor]) -> Graph: ...
def _check_onnx_proto(proto: str) -> None: ...
def _propagate_and_assign_input_shapes(
    graph: Graph,
    inputs: Tuple[Tensor, ...],
    with_grad: _bool,
    propagate: _bool
) -> Graph: ...

# Defined in torch/csrc/jit/runtime/graph_executor.h
class GraphExecutorState:
    ...

# Defined in torch/torch/csrc/jit/ir/ir.h
class Graph:
    def eraseInput(self, i: _int) -> None: ...
    ...

# Defined in torch/csrc/jit/ir/ir.h
class Value:
    ...

# Defined in torch/csrc/jit/ir/ir.h
class Block:
    ...

# Defined in torch/csrc/jit/ir/ir.h
class Node:
    ...

# Defined in torch/aten/src/ATen/core/function_schema.h
class Argument:
    name: str
    type: JitType
    default_value: Optional[Any]
    def has_default_value(self) -> _bool: ...
    ...
class FunctionSchema:
    arguments: List[Argument]
    returns: List[Argument]
    ...

# Defined in torch/csrc/jit/python/script_init.cpp
class ConcreteModuleTypeBuilder:
    def __init__(self, obj: Any) -> None: ...
    def set_module_dict(self): ...
    def set_module_list(self): ...
    def add_attribute(self, name: str, ty: JitType, is_param: _bool, is_buffer: _bool): ...
    def add_module(self, name: str, meta: ConcreteModuleType): ...
    def add_constant(self, name: str, value: Any): ...
    def add_overload(self, method_name: str, overloaded_method_names: List[str]): ...
    def add_builtin_function(self, name: str, symbol_name: str): ...
    def add_failed_attribute(self, name: str, failure_reason: str): ...
    def add_function_attribute(self, name: str, ty: JitType, func: Callable[..., Any]): ...
    def add_ignored_attribute(self, name: str): ...
    def add_ignored_attributes(self, names: List[str]): ...
    def add_forward_hook(self, hook: Callable[..., Any]): ...
    def add_forward_pre_hook(self, pre_hook: Callable[..., Any]): ...

class ConcreteModuleType:
    def get_constants(self) -> Dict[str, Any]: ...
    def equals(self, other: 'ConcreteModuleType') -> _bool: ...

    @staticmethod
    def from_jit_type(ty: JitType) -> ConcreteModuleType: ...

class CallStack:
    def __init__(self, name: str, range: SourceRange): ...

class ErrorReport:
    def __init__(self, range: SourceRange) -> None: ...
    def what(self) -> str: ...

    @staticmethod
    def call_stack() -> str: ...

class CompilationUnit:
    def __init__(self, lang: str=..., _frames_up: _int=...) -> None: ...
    def find_function(self, name: str) -> ScriptFunction: ...
    def __getattr__(self, name: str) -> ScriptFunction: ...
    def define(self, script: str, rcb: ResolutionCallback=..., _frames_up: _int=...): ...
    def get_interface(self, name: str) -> InterfaceType: ...
    def get_functions(self) -> List[ScriptFunction]: ...
    def create_function(self, name: str, graph: Graph, shouldMangle: _bool=...) -> ScriptFunction: ...

class ScriptModule:
    def setattr(self, name: str, value: Any): ...
    def _method_names(self) -> List[str]: ...
    def _get_method(self, name: str) -> ScriptMethod: ...

class ScriptFunction:
    def __call__(self, *args, **kwargs) -> Tensor: ...
    def save(self, filename: str, _extra_files: Dict[str, bytes]) -> None: ...
    def save_to_buffer(self, _extra_files: Dict[str, bytes]) -> bytes: ...
    @property
    def graph(self) -> Graph: ...
    def inlined_graph(self) -> Graph: ...
    def schema(self) -> FunctionSchema: ...
    def code(self) -> str: ...
    def name(self) -> str: ...
    @property
    def qualified_name(self) -> str: ...

class ScriptMethod:
    graph: Graph
    ...
class ModuleDict:
    def __init__(self, mod: ScriptModule) -> None: ...
    def items(self) -> List[Tuple[str, Any]]: ...

class ParameterDict:
    def __init__(self, mod: ScriptModule) -> None: ...

class BufferDict:
    def __init__(self, mod: ScriptModule) -> None: ...

# Defined in torch/csrc/jit/api/module.h
class Module:
    ...

# Defined in torch/csrc/jit/python/script_init.cpp
class LoggerBase(object):
    ...

class NoopLogger(LoggerBase):
    ...

class LockingLogger(LoggerBase):
    ...

class AggregationType(Enum):
    SUM = 0
    AVG = 1

class FileCheck(object):
    # TODO (add more FileCheck signature)
    def check_source_highlighted(self, highlight: str) -> 'FileCheck': ...
    def run(self, test_string: str) -> None: ...
    ...

# Defined in torch/csrc/jit/python/init.cpp
class PyTorchFileReader(object):
    @overload
    def __init__(self, name: str) -> None: ...
    @overload
    def __init__(self, buffer: BinaryIO) -> None: ...
    def get_record(self, name: str) -> bytes: ...
    ...

class PyTorchFileWriter(object):
    @overload
    def __init__(self, name: str) -> None: ...
    @overload
    def __init__(self, buffer: BinaryIO) -> None: ...
    def write_record(self, name: str, data: bytes, size: _int) -> None: ...
    def write_end_of_file(self) -> None: ...
    def set_min_version(self, version: _int) -> None: ...
    def archive_name(self) -> str: ...
    def get_all_written_records(self) -> List[str]: ...
    ...

def get_inline_everything_mode() -> _bool: ...
def set_inline_everything_mode(enabled: _bool) -> None: ...
def pass_dce(Graph) -> None: ...
def pass_lint(Graph) -> None: ...

# Defined in torch/csrc/jit/python/python_custome_class.cpp
def _get_custom_class_python_wrapper(name: str, attr: str) -> Any: ...

# Defined in torch/csrc/jit/python/python_tracer.cpp
class TracingState:
    def push_scope(self, scope_name: str) -> None: ...
    def pop_scope(self) -> None: ...
    def current_scope(self) -> str: ...
    def set_graph(self, graph: Graph) -> None: ...
    def graph(self) -> Graph: ...
    ...

def _create_graph_by_tracing(
    func: Callable[..., Any],
    inputs: Any,
    var_name_lookup_fn: Callable[[Tensor], str],
    strict: Any,
    force_outplace: Any,
    self: Any = None,
    argument_names: List[str] = []
) -> Tuple[Graph, Stack]: ...
def _tracer_warn_use_python(): ...
def _get_tracing_state() -> TracingState: ...

# Defined in torch/csrc/jit/python/python_ir.cpp
# Not actually defined in python_ir.cpp, not sure where they are.
class IValue:
    ...
Stack = List[IValue]

class JitType:
    ...

class InferredType:
    def __init__(self, arg: Union[JitType, str]): ...
    def type(self) -> JitType: ...
    def success(self) -> _bool: ...
    def reason(self) -> str: ...

R = TypeVar('R', bound=JitType)

class AnyType(JitType):
    @staticmethod
    def get() -> AnyType: ...

class NoneType(JitType):
    @staticmethod
    def get() -> NoneType: ...

class BoolType(JitType):
    @staticmethod
    def get() -> BoolType: ...

class FloatType(JitType):
    @staticmethod
    def get() -> FloatType: ...

class ComplexType(JitType):
    @staticmethod
    def get() -> ComplexType: ...

class IntType(JitType):
    @staticmethod
    def get() -> IntType: ...

class StringType(JitType):
    @staticmethod
    def get() -> StringType: ...

class DeviceObjType(JitType):
    @staticmethod
    def get() -> DeviceObjType: ...

class StreamObjType(JitType):
    @staticmethod
    def get() -> StreamObjType: ...

class ListType(JitType):
    def __init__(self, a: JitType) -> None: ...
    def getElementType(self) -> JitType: ...

    @staticmethod
    def ofInts() -> ListType: ...
    @staticmethod
    def ofTensors() -> ListType: ...
    @staticmethod
    def ofFloats() -> ListType: ...
    @staticmethod
    def ofComplexDoubles() -> ListType: ...
    @staticmethod
    def ofBools() -> ListType: ...

class DictType(JitType):
    def __init__(self, key: JitType, value: JitType) -> None: ...
    def getKeyType(self) -> JitType: ...
    def getValueType(self) -> JitType: ...

class TupleType(JitType):
    def __init__(self, a: List[JitType]) -> None: ...

class ClassType(JitType):
    def __init__(self, qualified_name: str) -> None: ...

class InterfaceType(JitType):
    def __init__(self, qualified_name: str) -> None: ...
    def getMethod(self, name: str) -> Optional[FunctionSchema]: ...
    def getMethodNames(self) -> List[str]: ...

class OptionalType(JitType, Generic[R]):
    def __init__(self, a: JitType) -> None: ...
    def getElementType(self) -> JitType: ...

    @staticmethod
    def ofTensor() -> OptionalType: ...

class FutureType(JitType):
    def __init__(self, a: JitType) -> None: ...
    def getElementType(self) -> JitType: ...

class RRefType(JitType):
    def __init__(self, a: JitType) -> None: ...

class EnumType(JitType):
    def __init__(
        self,
        qualified_name: str,
        value_type: JitType,
        enum_names_values: List[Any]
    ) -> None:
        ...

class TensorType(JitType):
    @classmethod
    def get(cls) -> TensorType: ...
    @classmethod
    def getInferred(cls) -> TensorType: ...

# Defined in torch/csrc/jit/python/python_tree_views.cpp
class SourceRange:
    ...

class TreeView:
    ...

class Ident(TreeView):
    @property
    def name(self) -> str: ...

class ClassDef(TreeView):
    ...

class Def(TreeView):
    def name(self) -> Ident: ...

class Decl(TreeView):
    ...