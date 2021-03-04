import torch
import unittest
from torch.testing._internal.common_utils import TestCase, run_tests, TEST_WITH_ROCM, TEST_WITH_SLOW
from torch.testing._internal.common_device_type import \
    (instantiate_device_type_tests, dtypes, skipCUDAIfRocm, ops)
from torch._six import inf, nan
from torch.testing._internal.common_methods_invocations import \
    (foreach_unary_op_db, foreach_binary_op_db, foreach_pointwise_op_db, foreach_min_max_op_db)

# Includes some values such that N * N won't be a multiple of 4,
# which should ensure we test the vectorized and non-vectorized
# kernel code paths.
N_values = [20, 23] if not TEST_WITH_SLOW else [23, 30, 300]

class TestForeach(TestCase):
    bin_ops = [
        (torch._foreach_add, torch._foreach_add_, torch.add),
        (torch._foreach_sub, torch._foreach_sub_, torch.sub),
        (torch._foreach_mul, torch._foreach_mul_, torch.mul),
        (torch._foreach_div, torch._foreach_div_, torch.div),
    ]

    def _get_test_data(self, device, dtype, N):
        if dtype in [torch.bfloat16, torch.bool, torch.float16]:
            tensors = [torch.randn(N, N, device=device).to(dtype) for _ in range(N)]
        elif dtype in torch.testing.get_all_int_dtypes():
            # Constrains the range between 1 and 10 for less stress on int8 tensors.
            tensors = [torch.randint(1, 10, (N, N), device=device, dtype=dtype) for _ in range(N)]
        else:
            tensors = [torch.randn(N, N, device=device, dtype=dtype) for _ in range(N)]

        return tensors

    @ops(foreach_unary_op_db)
    def test_unary_ops(self, device, dtype, op):
        for N in N_values:
            tensors = op.sample_inputs(device, dtype, N)
            ref_res = [op.ref(t) for t in tensors]

            method = op.get_method()
            inplace = op.get_inplace()
            fe_res = method(tensors)
            self.assertEqual(ref_res, fe_res)

            if op.safe_casts_outputs and dtype in torch.testing.integral_types_and(torch.bool):
                with self.assertRaisesRegex(RuntimeError, "can't be cast to the desired output type"):
                    inplace(tensors)
            elif dtype in [torch.complex64, torch.complex128] and inplace == torch._foreach_abs_:
                # Special case for abs
                with self.assertRaisesRegex(RuntimeError, r"In-place abs is not supported for complex tensors."):
                    inplace(tensors)
            else:
                inplace(tensors)
                self.assertEqual(tensors, fe_res)

    # Test foreach binary ops with a single scalar
    # Compare results agains reference torch functions
    # In case of an exeption, check if torch reference function throws as well.
    @skipCUDAIfRocm
    @ops(foreach_binary_op_db)
    def test_binary_ops_scalar(self, device, dtype, op):
        scalars = [2, 2.2, True, 3 + 5j]

        # Mimics cuda kernel dtype flow.  With fp16/bf16 input, runs in fp32 and casts output back to fp16/bf16.
        dtype = torch.float32 if (self.device_type == 'cuda' and 
                                  (dtype is torch.float16 or dtype is torch.bfloat16)) else dtype
        for N in N_values:
            for scalar in scalars: 
                # test out of place
                foreach_exeption = False
                torch_exeption = False
                tensors = op.sample_inputs(device, dtype, N)
                method = op.get_method()
                inplace = op.get_inplace()

                try:
                    ref_res = [op.ref(t, scalar) for t in tensors]
                except Exception:
                    torch_exeption = True

                try:
                    fe_res = method(tensors, scalar)
                except Exception:
                    foreach_exeption = True

                self.assertEqual(foreach_exeption, torch_exeption)

                if not torch_exeption:
                    if (dtype is torch.float16 or dtype is torch.bfloat16) and TEST_WITH_ROCM:
                        self.assertEqual(ref_res, fe_res, atol=1.e-3, rtol=self.dtype_precisions[dtype][0])
                    else:
                        self.assertEqual(ref_res, fe_res)

                # test inplace
                foreach_inplace_exeption = False
                torch_inplace_exeption = False
                try:
                    inplace(tensors, scalar)
                    self.assertEqual(tensors, fe_res)
                except Exception:
                    foreach_inplace_exeption = True

                try:
                    # get torch inplace reference function
                    inplace_name = op.ref_name + "_"
                    torch_inplace = getattr(torch.Tensor, inplace_name, None)

                    for t in tensors:
                        torch_inplace(t, scalar)
                except Exception:
                    torch_inplace_exeption = True

                self.assertEqual(foreach_inplace_exeption, torch_inplace_exeption)

    # Test foreach binary ops with a scalar list
    # Compare results agains reference torch functions
    # In case of an exeption, check if torch reference function throws as well.
    @skipCUDAIfRocm
    @ops(foreach_binary_op_db)
    def test_binary_ops_scalar_list(self, device, dtype, op):
        # Mimics cuda kernel dtype flow.  With fp16/bf16 input, runs in fp32 and casts output back to fp16/bf16.
        dtype = torch.float32 if (self.device_type == 'cuda' and 
                                  (dtype is torch.float16 or dtype is torch.bfloat16)) else dtype
        for N in N_values:
            scalar_lists = [
                [2 for _ in range(N)],
                [2.2 for _ in range(N)],
                [True for _ in range(N)],
                [3 + 5j for _ in range(N)],
            ]

            for scalar_list in scalar_lists: 
                # test out of place
                foreach_exeption = False
                torch_exeption = False
                tensors = op.sample_inputs(device, dtype, N)
                method = op.get_method()
                inplace = op.get_inplace()

                try:
                    ref_res = [op.ref(t, s) for t, s in zip(tensors, scalar_list)]
                except Exception:
                    torch_exeption = True

                try:
                    fe_res = method(tensors, scalar_list)
                except Exception:
                    foreach_exeption = True

                self.assertEqual(foreach_exeption, torch_exeption)

                if not torch_exeption:
                    if (dtype is torch.float16 or dtype is torch.bfloat16) and TEST_WITH_ROCM:
                        self.assertEqual(ref_res, fe_res, atol=1.e-3, rtol=self.dtype_precisions[dtype][0])
                    else:
                        self.assertEqual(ref_res, fe_res)

                # test inplace
                foreach_inplace_exeption = False
                torch_inplace_exeption = False
                try:
                    inplace(tensors, scalar_list)
                    self.assertEqual(tensors, fe_res)
                except Exception:
                    foreach_inplace_exeption = True

                try:
                    # get torch inplace reference function
                    inplace_name = op.ref_name + "_"
                    torch_inplace = getattr(torch.Tensor, inplace_name, None)

                    for t, s in zip(tensors, scalar_list):
                        torch_inplace(t, s)
                except Exception:
                    torch_inplace_exeption = True

                self.assertEqual(foreach_inplace_exeption, torch_inplace_exeption)

    # Test foreach binary ops with a two tensor lists
    # Compare results agains reference torch functions
    # In case of an exeption, check if torch reference function throws as well.
    # In case of add/sub, also test alphas
    @skipCUDAIfRocm
    @ops(foreach_binary_op_db)
    def test_binary_ops_tensor_list(self, device, dtype, op):
        # Mimics cuda kernel dtype flow.  With fp16/bf16 input, runs in fp32 and casts output back to fp16/bf16.
        dtype = torch.float32 if (self.device_type == 'cuda' and 
                                  (dtype is torch.float16 or dtype is torch.bfloat16)) else dtype

        for N in N_values:
            foreach_exeption = False
            torch_exeption = False
            tensors1 = op.sample_inputs(device, dtype, N)
            tensors2 = op.sample_inputs(device, dtype, N)
            method = op.get_method()
            alpha = 2

            try:
                ref_res = [op.ref(t1, t2) for t1, t2 in zip(tensors1, tensors2)]
                if op.supports_alpha_param: 
                    ref_res_alpha = [op.ref(t1, t2, alpha=alpha) for t1, t2 in zip(tensors1, tensors2)]
            except Exception:
                torch_exeption = True

            try:
                fe_res = method(tensors1, tensors2)
                if op.supports_alpha_param: 
                    fe_res_alpha = method(tensors1, tensors2, alpha=alpha)
            except Exception:
                foreach_exeption = True

            self.assertEqual(foreach_exeption, torch_exeption)

            if not torch_exeption:
                if (dtype is torch.float16 or dtype is torch.bfloat16) and TEST_WITH_ROCM:
                    self.assertEqual(ref_res, fe_res, atol=1.e-3, rtol=self.dtype_precisions[dtype][0])

                    if op.supports_alpha_param: 
                        self.assertEqual(ref_res_alpha, fe_res_alpha, atol=1.e-3, rtol=self.dtype_precisions[dtype][0])
                else:
                    self.assertEqual(ref_res, fe_res)

                    if op.supports_alpha_param:
                        self.assertEqual(ref_res_alpha, fe_res_alpha)

    @skipCUDAIfRocm
    @ops(foreach_binary_op_db)
    def test_binary_ops_tensor_list_inplace(self, device, dtype, op):
        # Mimics cuda kernel dtype flow.  With fp16/bf16 input, runs in fp32 and casts output back to fp16/bf16.
        dtype = torch.float32 if (self.device_type == 'cuda' and 
                                  (dtype is torch.float16 or dtype is torch.bfloat16)) else dtype

        for N in N_values:
            tensors1 = op.sample_inputs(device, dtype, N)
            tensors2 = op.sample_inputs(device, dtype, N)
            tensors1_copy = [t1.clone() for t1 in tensors1]
            tensors2_copy = [t2.clone() for t2 in tensors2]
            inplace = op.get_inplace()
            alpha = 2

            foreach_inplace_exeption = False
            torch_inplace_exeption = False
            try:
                inplace(tensors1, tensors2)

                if op.supports_alpha_param: 
                    inplace(tensors1, tensors2, alpha=alpha)
            except Exception:
                foreach_inplace_exeption = True

            try:
                # get torch inplace reference function
                inplace_name = op.ref_name + "_"
                torch_inplace = getattr(torch.Tensor, inplace_name, None)
                for t1, t2 in zip(tensors1_copy, tensors2_copy):
                    torch_inplace(t1, t2)
                    if op.supports_alpha_param: 
                        torch_inplace(t1, t2, alpha=alpha)
            except Exception:
                torch_inplace_exeption = True

            self.assertEqual(foreach_inplace_exeption, torch_inplace_exeption)
            if not foreach_inplace_exeption:
                self.assertEqual(tensors1, tensors1_copy)
                self.assertEqual(tensors2, tensors2_copy)

    #
    # Pointwise ops
    #
    @ops(foreach_pointwise_op_db)
    def test_pointwise_ops(self, device, dtype, op):
        for N in N_values:
            values = [2 + i for i in range(N)]
            for vals in [values[0], values]:
                tensors = op.sample_inputs(device, dtype, N)
                tensors1 = op.sample_inputs(device, dtype, N)
                tensors2 = op.sample_inputs(device, dtype, N)

                # Mimics cuda kernel dtype flow.  With fp16/bf16 input, runs in fp32 and casts output back to fp16/bf16.
                control_dtype = torch.float32 if (self.device_type == 'cuda' and 
                                                  (dtype is torch.float16 or dtype is torch.bfloat16)) else dtype

                if not isinstance(vals, list):
                    expected = [op.ref(tensors[i].to(dtype=control_dtype),
                                       tensors1[i].to(dtype=control_dtype),
                                       tensors2[i].to(dtype=control_dtype),
                                       value=values[0]).to(dtype=dtype) for i in range(N)]
                else:
                    expected = [op.ref(tensors[i].to(dtype=control_dtype),
                                       tensors1[i].to(dtype=control_dtype),
                                       tensors2[i].to(dtype=control_dtype),
                                       value=values[i]).to(dtype=dtype) for i in range(N)]

                method = op.get_method()
                inplace = op.get_inplace()
                fe_res = method(tensors, tensors1, tensors2, vals)
                inplace(tensors, tensors1, tensors2, vals)
                self.assertEqual(fe_res, tensors)

                if (dtype is torch.float16 or dtype is torch.bfloat16) and TEST_WITH_ROCM:
                    self.assertEqual(tensors, expected, atol=1.e-3, rtol=self.dtype_precisions[dtype][0])
                else:
                    self.assertEqual(tensors, expected)

                # test error cases
                tensors = op.sample_inputs(device, dtype, N)
                tensors1 = op.sample_inputs(device, dtype, N)
                tensors2 = op.sample_inputs(device, dtype, N)

                with self.assertRaisesRegex(RuntimeError, "Tensor list must have same number of elements as scalar list."):
                    method(tensors, tensors1, tensors2, [2 for _ in range(N + 1)])

                with self.assertRaisesRegex(RuntimeError, "Tensor list must have same number of elements as scalar list."):
                    method(tensors, tensors1, tensors2, [2 for _ in range(N - 1)])

                tensors = op.sample_inputs(device, dtype, N + 1)
                with self.assertRaisesRegex(RuntimeError, "Tensor lists must have the same number of tensors, got 21 and 20"):
                    method(tensors, tensors1, tensors2, [2 for _ in range(N)])

                tensors1 = op.sample_inputs(device, dtype, N + 1)
                with self.assertRaisesRegex(RuntimeError, "Tensor lists must have the same number of tensors, got 21 and 20"):
                    method(tensors, tensors1, tensors2, [2 for _ in range(N)])

    @ops(foreach_min_max_op_db)
    def test_min_max(self, device, dtype, op):
        for N in N_values:
            # Mimics cuda kernel dtype flow.  With fp16/bf16 input, runs in fp32 and casts output back to fp16/bf16.
            control_dtype = torch.float32 if (self.device_type == 'cuda' and
                                              (dtype is torch.float16 or dtype is torch.bfloat16)) else dtype
            method = op.get_method()

            tensors1 = op.sample_inputs(device, dtype, N)
            tensors2 = op.sample_inputs(device, dtype, N)

            expected = [op.ref(tensors1[i].to(dtype=control_dtype),
                               tensors2[i].to(dtype=control_dtype)).to(dtype=dtype) for i in range(N)]

            res = method(tensors1, tensors2)
            self.assertEqual(res, expected)

    @ops(foreach_min_max_op_db)
    def test_min_max_inf_nan(self, device, dtype, op):
        method = op.get_method()
        a = [
            torch.tensor([float('inf')], device=device, dtype=dtype),
            torch.tensor([-float('inf')], device=device, dtype=dtype),
            torch.tensor([float('nan')], device=device, dtype=dtype),
            torch.tensor([float('nan')], device=device, dtype=dtype),
        ]

        b = [
            torch.tensor([-float('inf')], device=device, dtype=dtype),
            torch.tensor([float('inf')], device=device, dtype=dtype),
            torch.tensor([float('inf')], device=device, dtype=dtype),
            torch.tensor([float('nan')], device=device, dtype=dtype)
        ]

        expected = [op.ref(a1, b1) for a1, b1 in zip(a, b)]
        res = method(a, b)
        self.assertEqual(res, expected)

        a = [
            torch.tensor([inf], device=device, dtype=dtype),
            torch.tensor([-inf], device=device, dtype=dtype),
            torch.tensor([nan], device=device, dtype=dtype),
            torch.tensor([nan], device=device, dtype=dtype)
        ]

        b = [
            torch.tensor([-inf], device=device, dtype=dtype),
            torch.tensor([inf], device=device, dtype=dtype),
            torch.tensor([inf], device=device, dtype=dtype),
            torch.tensor([nan], device=device, dtype=dtype)
        ]

        expected = [op.ref(a1, b1) for a1, b1 in zip(a, b)]
        res = method(a, b)
        self.assertEqual(res, expected)

    #
    # Special cases
    #
    @dtypes(*torch.testing.get_all_dtypes())
    def test_mixed_scalarlist(self, device, dtype):
        for N in N_values:
            for foreach_bin_op, foreach_bin_op_, torch_bin_op in self.bin_ops:
                tensors = self._get_test_data(device, dtype, N)
                scalars = [True for _ in range(N)]
                scalars[0] = 1
                scalars[1] = 1.1
                scalars[2] = 3 + 5j

                if foreach_bin_op == torch._foreach_sub:
                    with self.assertRaisesRegex(RuntimeError, "Subtraction, the `-` operator"):
                        expected = [torch_bin_op(t, s) for t, s in zip(tensors, scalars)]

                    with self.assertRaisesRegex(RuntimeError, "Subtraction, the `-` operator"):
                        foreach_bin_op(tensors, scalars)

                    # There are a two types of different errors that will be thrown.
                    # - Sub with bool is not allowed. 
                    # - Result type can't be cast to the desired output type
                    with self.assertRaises(RuntimeError):
                        foreach_bin_op_(tensors, scalars)
                    continue

                expected = [torch_bin_op(t, s) for t, s in zip(tensors, scalars)]
                res = foreach_bin_op(tensors, scalars)
                self.assertEqual(expected, res)

    @dtypes(*torch.testing.get_all_dtypes())
    def test_add_with_different_size_tensors(self, device, dtype):
        if dtype == torch.bool:
            return
        tensors = [torch.zeros(10 + n, 10 + n, device=device, dtype=dtype) for n in range(10)]
        expected = [torch.ones(10 + n, 10 + n, device=device, dtype=dtype) for n in range(10)]

        torch._foreach_add_(tensors, 1)
        self.assertEqual(expected, tensors)

    @dtypes(*torch.testing.get_all_dtypes())
    def test_add_scalar_with_empty_list_and_empty_tensor(self, device, dtype):
        # TODO: enable empty list case
        for tensors in [[torch.randn([0])]]:
            res = torch._foreach_add(tensors, 1)
            self.assertEqual(res, tensors)

            torch._foreach_add_(tensors, 1)
            self.assertEqual(res, tensors)

    @dtypes(*torch.testing.get_all_dtypes())
    def test_add_scalar_with_overlapping_tensors(self, device, dtype):
        tensors = [torch.ones(1, 1, device=device, dtype=dtype).expand(2, 1, 3)]
        expected = [torch.tensor([[[2, 2, 2]], [[2, 2, 2]]], dtype=dtype, device=device)]

        # bool tensor + 1 will result in int64 tensor
        if dtype == torch.bool:
            expected[0] = expected[0].to(torch.int64).add(1)

        res = torch._foreach_add(tensors, 1)
        self.assertEqual(res, expected)

    def test_bin_op_scalar_with_different_tensor_dtypes(self, device):
        tensors = [torch.tensor([1.1], dtype=torch.float, device=device),
                   torch.tensor([1], dtype=torch.long, device=device)]
        self.assertRaises(RuntimeError, lambda: torch._foreach_add(tensors, 1))

    #
    # Ops with list
    #
    def test_bin_op_list_error_cases(self, device):
        for bin_op, bin_op_, _ in self.bin_ops:
            tensors1 = []
            tensors2 = []

            # Empty lists
            with self.assertRaisesRegex(RuntimeError, "There were no tensor arguments to this function"):
                bin_op(tensors1, tensors2)
            with self.assertRaisesRegex(RuntimeError, "There were no tensor arguments to this function"):
                bin_op_(tensors1, tensors2)

            # One empty list
            tensors1.append(torch.tensor([1], device=device))
            with self.assertRaisesRegex(RuntimeError, "Tensor list must have same number of elements as scalar list."):
                bin_op(tensors1, tensors2)
            with self.assertRaisesRegex(RuntimeError, "Tensor list must have same number of elements as scalar list."):
                bin_op_(tensors1, tensors2)

            # Lists have different amount of tensors
            tensors2.append(torch.tensor([1], device=device))
            tensors2.append(torch.tensor([1], device=device))
            with self.assertRaisesRegex(RuntimeError, "Tensor lists must have the same number of tensors, got 1 and 2"):
                bin_op(tensors1, tensors2)
            with self.assertRaisesRegex(RuntimeError, "Tensor lists must have the same number of tensors, got 1 and 2"):
                bin_op_(tensors1, tensors2)

            # Different dtypes
            tensors1 = [torch.zeros(10, 10, device=device, dtype=torch.float) for _ in range(10)]
            tensors2 = [torch.ones(10, 10, device=device, dtype=torch.int) for _ in range(10)]

            with self.assertRaisesRegex(RuntimeError, "All tensors in the tensor list must have the same dtype."):
                bin_op(tensors1, tensors2)
            with self.assertRaisesRegex(RuntimeError, "All tensors in the tensor list must have the same dtype."):
                bin_op_(tensors1, tensors2)

            # different devices
            if torch.cuda.is_available() and torch.cuda.device_count() > 1:
                tensor1 = torch.zeros(10, 10, device="cuda:0")
                tensor2 = torch.ones(10, 10, device="cuda:1")
                with self.assertRaisesRegex(RuntimeError, "Expected all tensors to be on the same device"):
                    bin_op([tensor1], [tensor2])
                with self.assertRaisesRegex(RuntimeError, "Expected all tensors to be on the same device"):
                    bin_op_([tensor1], [tensor2])

            # Corresponding tensors with different sizes
            tensors1 = [torch.zeros(10, 10, device=device) for _ in range(10)]
            tensors2 = [torch.ones(11, 11, device=device) for _ in range(10)]
            with self.assertRaisesRegex(RuntimeError, "Corresponding tensors in lists must have the same size"):
                bin_op(tensors1, tensors2)
            with self.assertRaisesRegex(RuntimeError, r", got \[10, 10\] and \[11, 11\]"):
                bin_op_(tensors1, tensors2)

    @dtypes(*torch.testing.get_all_dtypes())
    def test_add_list_different_sizes(self, device, dtype):
        tensors1 = [torch.zeros(10 + n, 10 + n, device=device, dtype=dtype) for n in range(10)]
        tensors2 = [torch.ones(10 + n, 10 + n, device=device, dtype=dtype) for n in range(10)]

        res = torch._foreach_add(tensors1, tensors2)
        torch._foreach_add_(tensors1, tensors2)
        self.assertEqual(res, tensors1)
        self.assertEqual(res, [torch.ones(10 + n, 10 + n, device=device, dtype=dtype) for n in range(10)])

    @unittest.skipIf(not torch.cuda.is_available(), "CUDA not found")
    @dtypes(*torch.testing.get_all_dtypes())
    def test_add_list_slow_path(self, device, dtype):
        # different strides
        tensor1 = torch.zeros(10, 10, device=device, dtype=dtype)
        tensor2 = torch.ones(10, 10, device=device, dtype=dtype)
        res = torch._foreach_add([tensor1], [tensor2.t()])
        torch._foreach_add_([tensor1], [tensor2])
        self.assertEqual(res, [tensor1])

        # non contiguous
        tensor1 = torch.randn(5, 2, 1, 3, device=device)[:, 0]
        tensor2 = torch.randn(5, 2, 1, 3, device=device)[:, 0]
        self.assertFalse(tensor1.is_contiguous())
        self.assertFalse(tensor2.is_contiguous())
        res = torch._foreach_add([tensor1], [tensor2])
        torch._foreach_add_([tensor1], [tensor2])
        self.assertEqual(res, [tensor1])

instantiate_device_type_tests(TestForeach, globals())

if __name__ == '__main__':
    run_tests()
