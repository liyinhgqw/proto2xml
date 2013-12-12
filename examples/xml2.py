#!/usr/bin/python2

# xml.g
#
# Amit J. Patel, August 2003
#
# Simple (non-conforming, non-validating) parsing of XML documents,
# based on Robert D. Cameron's "REX" shallow parser.  It doesn't
# handle CDATA and lots of other stuff; it's meant to demonstrate
# Yapps, not replace a proper XML parser.


from string import *
import re
from yappsrt import *

class xmlScanner(Scanner):
    patterns = [
        ('"\'"', re.compile("'")),
        ('\'"\'', re.compile('"')),
        ("'='", re.compile('=')),
        ("'/\\s*>'", re.compile('/\\s*>')),
        ("'</'", re.compile('</')),
        ("'>'", re.compile('>')),
        ("'<'", re.compile('<')),
        ("'[^>]*>'", re.compile('[^>]*>')),
        ("r'<!'", re.compile('<!')),
        ("r'<!\\[CDATA\\[.*?\\]\\]>'", re.compile('<!\\[CDATA\\[.*?\\]\\]>')),
        ("r'<!--.*?-->'", re.compile('<!--.*?-->')),
        ('nodetext', re.compile('[^<>]+')),
        ('attrtext_singlequote', re.compile("[^']*")),
        ('attrtext_doublequote', re.compile('[^"]*')),
        ('SP', re.compile('\\s')),
        ('id', re.compile('[a-zA-Z_:][a-zA-Z0-9_:.-]*')),
    ]
    def __init__(self, str):
        Scanner.__init__(self,None,[],str)

class xml(Parser):
    def node(self):
        _token_ = self._peek("r'<!--.*?-->'", "r'<!\\[CDATA\\[.*?\\]\\]>'", "r'<!'", "'<'", 'nodetext')
        if _token_ == "r'<!--.*?-->'":
            self._scan("r'<!--.*?-->'")
            return ['!--comment']
        elif _token_ == "r'<!\\[CDATA\\[.*?\\]\\]>'":
            self._scan("r'<!\\[CDATA\\[.*?\\]\\]>'")
            return ['![CDATA[']
        elif _token_ == "r'<!'":
            self._scan("r'<!'")
            while self._peek('SP', 'id') == 'SP':
                SP = self._scan('SP')
            id = self._scan('id')
            self._scan("'[^>]*>'")
            return ['!doctype']
        elif _token_ == "'<'":
            self._scan("'<'")
            while self._peek('SP', 'id') == 'SP':
                SP = self._scan('SP')
            id = self._scan('id')
            while self._peek('SP', 'id', "'>'", "'/\\s*>'") == 'SP':
                SP = self._scan('SP')
            attributes = self.attributes()
            while self._peek('SP', "'>'", "'/\\s*>'") == 'SP':
                SP = self._scan('SP')
            startid = id
            _token_ = self._peek("'>'", "'/\\s*>'")
            if _token_ == "'>'":
                self._scan("'>'")
                nodes = self.nodes()
                self._scan("'</'")
                while self._peek('SP', 'id') == 'SP':
                    SP = self._scan('SP')
                id = self._scan('id')
                while self._peek('SP', "'>'") == 'SP':
                    SP = self._scan('SP')
                self._scan("'>'")
                assert startid == id, 'Mismatched tags <%s> ... </%s>' % (startid, id)
                return [id, attributes] + nodes
            else:# == "'/\\s*>'"
                self._scan("'/\\s*>'")
                return [id, attributes]
        else:# == 'nodetext'
            nodetext = self._scan('nodetext')
            return nodetext

    def nodes(self):
        result = []
        while self._peek("r'<!--.*?-->'", "r'<!\\[CDATA\\[.*?\\]\\]>'", "r'<!'", "'<'", 'nodetext', "'</'") != "'</'":
            node = self.node()
            result.append(node)
        return result

    def attribute(self):
        id = self._scan('id')
        while self._peek('SP', "'='") == 'SP':
            SP = self._scan('SP')
        self._scan("'='")
        while self._peek('SP', '\'"\'', '"\'"') == 'SP':
            SP = self._scan('SP')
        _token_ = self._peek('\'"\'', '"\'"')
        if _token_ == '\'"\'':
            self._scan('\'"\'')
            attrtext_doublequote = self._scan('attrtext_doublequote')
            self._scan('\'"\'')
            return (id, attrtext_doublequote)
        else:# == '"\'"'
            self._scan('"\'"')
            attrtext_singlequote = self._scan('attrtext_singlequote')
            self._scan('"\'"')
            return (id, attrtext_singlequote)

    def attributes(self):
        result = {}
        while self._peek('id', 'SP', "'>'", "'/\\s*>'") == 'id':
            attribute = self.attribute()
            while self._peek('SP', 'id', "'>'", "'/\\s*>'") == 'SP':
                SP = self._scan('SP')
            result[attribute[0]] = attribute[1]
        return result


def parse(rule, text):
    P = xml(xmlScanner(text))
    return wrap_error_reporter(P, rule)




if __name__ == '__main__':
    tests = ['<!-- hello -->',
             'some text',
             '< bad xml',
             '<br />',
             '<     spacey      a  =   "foo"    /   >',
             '<a href="foo">text ... </a>',
             '<begin> middle </end>',
             '<begin> <nested attr=\'baz\' another="hey"> foo </nested> <nested> bar </nested> </begin>',
            ]
    print
    print '____Running tests_______________________________________'
    for test in tests:
        print
        try:
            parser = xml(xmlScanner(test))
            output = '%s ==> %s' % (repr(test), repr(parser.node()))
        except:
            output = '%s ==> FAILED ==> error' % (repr(test))
        print output
