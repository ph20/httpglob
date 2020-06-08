#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

from urllib.request import urlopen
import fnmatch
from bs4 import BeautifulSoup
import re

PATTERN = re.compile('(?P<scheme>(http|https))://(?P<netloc>[^/]+)(/(?P<path>.*))?')


class IncorrectPattern(Exception):
    pass


class Location:
    def __init__(self, scheme, netloc, path=''):
        self.scheme = scheme
        self.netloc = netloc
        self.path = path

    def __eq__(self, other):
        return other.scheme == self.scheme and other.netloc == self.netloc and other.path == self.path

    def scheme_prefix(self):
        return self.scheme + '://'

    def resource(self):
        return self.scheme_prefix() + self.netloc

    def full(self):
        return self.resource() + self.path

    def join_path(self, path: str):
        new_instance = self.__class__(self.scheme, self.netloc)
        if path.startswith('/'):
            new_instance.path = path
        else:
            new_instance.path = self.path + '/' + path
        return new_instance

    def is_subpath(self, other):
        if other.scheme == self.scheme and other.netloc == self.netloc:
            other_path = other.path + '/'
            return other_path.startswith(self.path + '/')

    def cut_base(self, base):
        if not base.is_subpath(self):
            raise RuntimeError('Incorrect subpath. {}|{}'.format(base.full(), self.full()))
        return self.full()[len(base.full()) + 1:]


def parse_url(url):
    pattern_matched = PATTERN.search(url)
    if not pattern_matched:
        raise IncorrectPattern('Cant match pattern {} with regex {}'.format(url, PATTERN))
    url_dict = pattern_matched.groupdict(default='')
    return Location(**url_dict)


def normalize_url(base_url: Location, url: str):
    if url.startswith('//:'):
        return parse_url(base_url.scheme + url)
    elif url.startswith('http://') or url.startswith('https://'):
        return parse_url(url)
    else:
        return base_url.join_path(url)


def gather_subpath_links(location: Location, pat='*'):
    links = []
    with urlopen(location.full()) as response:
        html_doc = response.read()
    for tag in BeautifulSoup(html_doc).find_all('a', href=True):
        a_href = tag['href']
        if a_href == '/':
            continue
        url = normalize_url(location, a_href)
        if location.is_subpath(url):
            path_chain = url.cut_base(location).split('/')[0]
            if fnmatch.fnmatch(path_chain, pat=pat) and url not in links:
                links.append(url)
    return links


def path_match(path: str, pat: str):
    path_spl = path.split('/')
    pat_spl = pat.split('/')
    if len(path_spl) != len(pat_spl):
        return False
    for name, pat in zip(path_spl, pat_spl):
        if not fnmatch.fnmatch(name=name, pat=pat):
            return False
    return True


def httpglob(path):
    found = []
    pattern = parse_url(path)
    spl_path = pattern.path.split('/')
    subpath_list = [pattern.resource()]
    for pat_chain in spl_path:
        if set(pat_chain).intersection({'?', '*', '['}):
            for subpath in subpath_list:
                new_subpath_list = []
                for l in gather_subpath_links(subpath, pat=pat_chain):
                    if path_match(l.full(), pattern.path):
                        if l not in found:
                            found.append(l)
                    else:
                        new_subpath_list.append(l)


        else:
            subpath_list = [subpath + '/' + pat_chain for subpath in subpath_list]

    return subpath_list


