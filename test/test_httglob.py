#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import unittest
from httpglob import httpglob, path_match


class PathMatchCase(unittest.TestCase):

    def test_010_path_match(self):
        self.assertTrue(path_match('/v1.1.1/image_1.1.1.zip', '/v1.1.1/image_1.1.1.zip'))

    def test_020_path_match(self):
        self.assertTrue(path_match('/v1.1.1/image_1.1.1.zip', '/v1.1.1/image_1.1.?.zip'))

    def test_030_path_match(self):
        self.assertFalse(path_match('/v1.1.1/image_1.1.1.zip', '/v1.1.1/image_1.2.?.zip'))


class HTTPGlobCase(unittest.TestCase):
    def test_openssl(self):
        httpglob('https://www.openssl.org/source/old/*/openssl-1.?.*.tar.gz')


if __name__ == '__main__':
    unittest.main()
