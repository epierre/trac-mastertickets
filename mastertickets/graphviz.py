# -*- coding: utf-8 -*-
# Created by Noah Kantrowitz on 2007-12-21.
# Copyright (c) 2007 Noah Kantrowitz. All rights reserved.
import os
import subprocess
import tempfile
import time
import itertools

try:
    set = set
except NameError:
    from sets import Set as set

def _format_options(base_string, options):
    return u'%s [%s]'%(base_string, u', '.join([u'%s="%s"'%x for x in options.iteritems()]))

class Edge(dict):
    """Model for an edge in a dot graph."""

    def __init__(self, source, dest, **kwargs):
        self.source = source
        self.dest = dest
        dict.__init__(self, **kwargs)

    def __str__(self):
        ret = u'%s -> %s'%(self.source.name, self.dest.name)
        if self:
            ret = _format_options(ret, self)
        return ret

    def __hash__(self):
        return hash(id(self))


class Node(dict):
    """Model for a node in a dot graph."""

    def __init__(self, name, **kwargs):
        self.name = unicode(name)
        self.edges = []
        dict.__init__(self, **kwargs)

    def __str__(self):
        ret = self.name
        if self:
            ret = _format_options(ret, self)
        return ret

    def __gt__(self, other):
        """Allow node1 > node2 to add an edge."""
        edge = Edge(self, other)
        self.edges.append(edge)
        other.edges.append(edge)
        return edge

    def __lt__(self, other):
        edge = Edge(other, self)
        self.edges.append(edge)
        other.edges.append(edge)
        return edge

    def __hash__(self):
        return hash(id(self))


class Graph(object):
    """A model object for a graphviz digraph."""

    def __init__(self, name=u'graph'):
        super(Graph,self).__init__()
        self.name = name
        self.nodes = []
        self._node_map = {}
        self.attributes={}
        self.edges = []

    def add(self, obj):
        if isinstance(obj, Node):
            self.nodes.append(obj)
            self._node_map[obj.name] = obj
        elif isinstance(obj, Edge):
            self.edges.append(obj)

    def __getitem__(self, key):
        key = unicode(key)
        if key not in self._node_map:
            new_node = Node(key)
            self._node_map[key] = new_node
            self.nodes.append(new_node)
        return self._node_map[key]

    def __delitem__(self, key):
        key = unicode(key)
        node = self._node_map.pop(key)
        self.nodes.remove(node)

    def __str__(self):
        edges = []
        nodes = []
        
        memo = set()
        def process(lst):
            for obj in lst:
                if obj in memo:
                    continue
                memo.add(obj)
                
                if isinstance(obj, Node):
                    nodes.append(obj)
                    process(obj.edges)
                elif isinstance(obj, Edge):
                    edges.append(obj)
                    if isinstance(obj.source, Node):
                        process((obj.source,))
                    if isinstance(obj.dest, Node):
                        process((obj.dest,))
        
        process(self.nodes)
        process(self.edges)
        
        lines = [u'digraph "%s" {'%self.name]
        for att,value in self.attributes.iteritems():
            lines.append(u'\t%s="%s";' % (att,value))
        for obj in itertools.chain(nodes, edges):
            lines.append(u'\t%s;'%obj)
        lines.append(u'}')
        return u'\n'.join(lines)

    def render(self, dot_path='dot', format='png'):
        """Render a dot graph."""
        proc = subprocess.Popen([dot_path, '-T%s'%format], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        out, _ = proc.communicate(unicode(self).encode('utf8'))
        return out


if __name__ == '__main__':
    g = Graph()
    root = Node('me')
    root > Node('them')
    root < Node(u'Üs')
    
    g.add(root)
    
    print g.render()
