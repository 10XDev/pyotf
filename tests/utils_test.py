#!/usr/bin/env python
# -*- coding: utf-8 -*-
# utils_test.py
"""
Tests for utility functions.

Copyright (c) 2020, David Hoffman
"""

import numpy as np
import pytest

from pyotf.utils import *


def test_remove_bg_unsigned():
    """Make sure that remove background doesn't fuck up unsigned ints."""
    test_data = np.array((1, 2, 3, 3, 3, 4, 5), dtype=np.uint16)
    assert np.allclose(remove_bg(test_data, 1.0), test_data - 3.0)


def test_center_data():
    """Make sure center data works as advertised."""
    ndims = np.random.randint(2, 3)
    shape = np.random.randint(1, 512, ndims)
    data = np.zeros(shape)
    random_index = tuple((np.random.randint(i),) for i in shape)
    data[random_index] = 1
    data_centered = center_data(data)
    assert np.fft.ifftshift(data_centered)[((0,),) * ndims]


def test_psqrt():
    """Test psqrt."""
    data = np.random.randint(-1000, 1000, size=20)
    ps_data = psqrt(data)
    less_than_zero = data < 0
    assert (ps_data[less_than_zero] == 0).all()
    more_than_zero = np.logical_not(less_than_zero)
    assert np.allclose(ps_data[more_than_zero], np.sqrt(data[more_than_zero]))


def test_cart2pol():
    """Make sure cart2pol is good."""
    z = np.random.randn(10) + np.random.randn(10) * 1j
    theta = np.angle(z)
    r = abs(z)
    test_r, test_theta = cart2pol(z.imag, z.real)
    assert np.allclose(test_theta, theta), "theta failed"
    assert np.allclose(test_r, r), "r failed"


@pytest.mark.parametrize(
    "shape_in,xysize,shape_out",
    [
        ((5, 5), None, (5, 5)),
        ((5, 4), None, (5, 5)),
        ((5, 4), 10, (10, 10)),
        ((5, 4), 3, (3, 3)),
    ],
)
def test_prep_pr_size_positive(shape_in, xysize, shape_out):
    """Test proper sizing and clipping at zero."""
    # need to add z dimension
    shape_in = (10,) + shape_in
    shape_out = (10,) + shape_out
    data_in = np.ones(shape_in, dtype=int)
    data_in[0, 0, 0] = 2
    data_in[-1, -1, -1] = 0
    data_out = prep_data_for_PR(data_in, xysize=xysize)
    assert data_out.shape == shape_out

    assert np.all(data_out >= 0)


@pytest.mark.parametrize("size", [3, 4, 5, 6, 7])
def test_prep_pr_center(size):
    shape_in = (10, 8, 8)
    shape_out = (10, size, size)
    data_in = np.ones(shape_in, dtype=int)
    data_in[0, 0, 0] = 2
    data_in[-1, -1, -1] = 0
    data_out = prep_data_for_PR(data_in, xysize=size)
    assert data_out.shape == shape_out

    nz, ny, nx = data_out.shape
    assert np.unravel_index(data_out.argmax(), data_out.shape) == (
        nz // 2,
        ny // 2,
        nx // 2,
    )
