# import exdir
# import pytest
# import os
# import shutil
# import h5py
# import numpy as np
# 
# 
# def create_many_objects(obj):
#     for i in range(2000):
#         group = obj.create_group("group{}".format(i))
#         data = np.zeros((10, 10, 10))
#         group.create_dataset("dataset{}".format(i), data=data)
# 
# 
# def iterate_objects(obj):
#     i = 0
#     for a in obj:
#         i += 1
#     return i
# 
# 
# # def test_many_objecst_h5py(benchmark, h5py_tmpfile):
# #     create_many_objects(h5py_tmpfile)
# #     benchmark(iterate_objects, h5py_tmpfile)
# #
# #
# # def test_many_objecst_exdir(benchmark, exdir_tmpfile):
# #     """
# #     Expected to be 2-3 times slower than h5py.
# #     """
# #     create_many_objects(exdir_tmpfile)
# #     benchmark(iterate_objects, exdir_tmpfile)
# 
# 
# def create_large_tree(obj, level=0):
#     if level > 5:
#         return
#     for i in range(5):
#         group = obj.create_group("group_{}_{}".format(i, level))
#         data = np.zeros((10, 10, 10))
#         group.create_dataset("dataset_{}_{}".format(i, level), data=data)
#         create_large_tree(group, level + 1)
# 
# 
# def test_large_tree_h5py(benchmark, h5py_tmpfile):
#     counted = 0
# 
#     def counter(name):
#         nonlocal counted
#         counted += 1
# 
#     create_large_tree(h5py_tmpfile)
#     benchmark(h5py_tmpfile.visit, counter)
# 
# 
# # TODO implement visit first
# # def test_large_tree_exdir(benchmark, exdir_tmpfile):
# #     """
# #     Expected to be 2-3 times slower than h5py.
# #     """
# #     counted = 0
# #
# #     def counter():
# #         nonlocal counted
# #         counted += 1
# #
# #     create_large_tree(exdir_tmpfile)
# #     benchmark(exdir_tmpfile.visit, counter)
