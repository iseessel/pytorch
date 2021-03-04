#include <ATen/Dispatch.h>
#include <ATen/native/ForeachUtils.h>
#include <ATen/native/cuda/ForeachFunctors.cuh>
#include <ATen/ExpandUtils.h>

namespace at { namespace native {

void print_sizes(const Tensor& t1) {
    std::cout << "\n" << t1 << std::endl;
    std::cout << "t.size: " << t1.sizes() << std::endl;
    std::cout << "t.stride: " << t1.strides() << std::endl;
}

template<template<class> class Op>
std::vector<Tensor> foreach_tensor_list_op(TensorList tensors1, 
                                           TensorList tensors2, 
                                           Scalar alpha = 1, 
                                           bool promote_integer_float = false) {
    std::vector<std::vector<at::Tensor>> tensor_lists;
    auto result_type = get_result_type(tensors1[0], tensors2[0], promote_integer_float);

    std::vector<at::Tensor> vec_res, temp_tensors1, temp_tensors2;
    vec_res.reserve(tensors1.size());
    temp_tensors1.reserve(tensors1.size());
    temp_tensors2.reserve(tensors2.size());
    tensor_lists.emplace_back(temp_tensors1);
    tensor_lists.emplace_back(temp_tensors2);


    for (int i = 0; i < tensors1.size(); i++) {
        tensor_lists[0].emplace_back(tensors1[i].to(result_type));
        tensor_lists[1].emplace_back(tensors2[i].to(result_type));
        vec_res.emplace_back(at::native::empty_like(tensor_lists[0][i]));
    }

    tensor_lists.emplace_back(std::move(vec_res));

    AT_DISPATCH_ALL_TYPES_AND_COMPLEX_AND3(kBool, kBFloat16, kHalf, result_type, "foreach_binary_op_list_cuda", [&]() {
        using opmath_t = get_opmath_t<scalar_t>::opmath_t;
        multi_tensor_apply<3>(tensor_lists,
                              BinaryOpListAlphaFunctor<scalar_t, 
                                                       /* depth */ 3,
                                                       /* r_args_depth */ 2, 
                                                       /* res_arg_index */ 2>(),
                              Op<opmath_t>(),
                              alpha.to<opmath_t>());
    });

    return tensor_lists[2];
}

template<template<class> class Op>
void foreach_tensor_list_op_(TensorList tensors1, TensorList tensors2, Scalar alpha = 1) {
    std::vector<std::vector<at::Tensor>> tensor_lists;
    tensor_lists.emplace_back(tensors1.vec());
    tensor_lists.emplace_back(tensors2.vec());

    AT_DISPATCH_ALL_TYPES_AND_COMPLEX_AND3(kBool, kBFloat16, kHalf, tensors1[0].scalar_type(), "foreach_binary_op_list_cuda_", [&]() {
        using opmath_t = get_opmath_t<scalar_t>::opmath_t;
        multi_tensor_apply<2>(tensor_lists,
                              BinaryOpListAlphaFunctor<scalar_t, 
                                                       /* depth */ 2,
                                                       /* r_args_depth */ 2, 
                                                       /* res_arg_index */ 0>(),
                              Op<opmath_t>(),
                              alpha.to<opmath_t>());
    });
}

#define FOREACH_BINARY_OP_LIST(NAME, OP, DIVISION_OP)                                                       \
void foreach_tensor_##NAME##_list_kernel_cuda_(TensorList tensors1, TensorList tensors2) {                  \
    foreach_tensor_list_op_<OP>(tensors1, tensors2);                                                        \
}                                                                                                           \
                                                                                                            \
std::vector<Tensor> foreach_tensor_##NAME##_list_kernel_cuda(TensorList tensors1, TensorList tensors2) {    \
    return foreach_tensor_list_op<OP>(tensors1, tensors2);                                                  \
}

#define FOREACH_BINARY_OP_LIST_ALPHA(NAME, OP)                                                                          \
void foreach_tensor_##NAME##_list_kernel_cuda_(TensorList tensors1, TensorList tensors2, Scalar alpha) {                \
    foreach_tensor_list_op_<OP>(tensors1, tensors2, alpha);                                                             \
}                                                                                                                       \
                                                                                                                        \
std::vector<Tensor> foreach_tensor_##NAME##_list_kernel_cuda(TensorList tensors1, TensorList tensors2, Scalar alpha) {  \
    return foreach_tensor_list_op<OP>(tensors1, tensors2, alpha);                                                       \
}

FOREACH_BINARY_OP_LIST_ALPHA(add, std::plus);
FOREACH_BINARY_OP_LIST_ALPHA(sub, std::minus);
FOREACH_BINARY_OP_LIST(mul, std::multiplies, /*division_op*/ false);
FOREACH_BINARY_OP_LIST(div, std::divides, /*division_op*/ true);

}} // namespace at::native

