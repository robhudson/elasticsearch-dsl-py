from six import iteritems, u

from .utils import AttrDict

class Hits(list):
    """
    List with custom repr and additional attributes `max_score` and `total` set
    by Response.
    """
    def __repr__(self):
        if len(self) > 3:
            return u('[%s, ...]') % u(', ').join(repr(h) for h in self[:2])
        return super(Hits, self).__repr__()

class Response(AttrDict):
    def __iter__(self):
        return iter(self.hits)

    def __getitem__(self, key):
        # for slicing etc
        return self.hits[key]

    def __repr__(self):
        return '<Response: %r>' % self.hits

    def success(self):
        return not (self.timed_out or self._shards.failed)

    @property
    def hits(self):
        if not hasattr(self, '_hits'):
            h = self._d['hits']
            # avoid assigning _hits into self._d
            super(AttrDict, self).__setattr__('_hits', Hits(map(Result, h['hits'])))
            self._hits.max_score = h['max_score']
            self._hits.total = h['total']
        return self._hits


class ResultMeta(AttrDict):
    def __init__(self, document):
        d = dict((k[1:], v) for (k, v) in iteritems(document) if k.startswith('_') and k != '_source')
        # make sure we are consistent everywhere in python
        d['doc_type'] = d['type']
        super(ResultMeta, self).__init__(d)

class Result(AttrDict):
    def __init__(self, document):
        super(Result, self).__init__(document['_source'])
        # assign _meta as attribute and not as key in self._d
        super(AttrDict, self).__setattr__('_meta', ResultMeta(document))

    def __dir__(self):
        # be sure to expose _meta in dir(self)
        return super(Result, self).__dir__() + ['_meta']

    def __repr__(self):
        return u('<Result(%s/%s/%s): %s>') % (
            self._meta.index, self._meta.doc_type, self._meta.id, super(Result, self).__repr__())
