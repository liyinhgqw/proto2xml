head = '''<?xml version="1.0" encoding="UTF-8" ?>'''
                   
tail = '''
    <uniqueKey>id</uniqueKey>

    <types>
        <fieldType name="string" class="solr.StrField" sortMissingLast="true" />
        <fieldType name="boolean" class="solr.BoolField" sortMissingLast="true"/>
        <fieldType name="int" class="solr.TrieIntField" precisionStep="0" positionIncrementGap="0"/>
        <fieldType name="float" class="solr.TrieFloatField" precisionStep="0" positionIncrementGap="0"/>
        <fieldType name="long" class="solr.TrieLongField" precisionStep="0" positionIncrementGap="0"/>
        <fieldType name="double" class="solr.TrieDoubleField" precisionStep="0" positionIncrementGap="0"/>
        <fieldType name="date" class="solr.TrieDateField" precisionStep="0" positionIncrementGap="0"/>

        <fieldType name="text_lowercase" class="solr.TextField">
            <analyzer type="index">
                <tokenizer class="solr.WhitespaceTokenizerFactory"/>
                <filter class="solr.LowerCaseFilterFactory"/>
            </analyzer>
            <analyzer type="query">
                <tokenizer class="solr.WhitespaceTokenizerFactory"/>
                <filter class="solr.LowerCaseFilterFactory"/>
            </analyzer>   
        </fieldType>

        <fieldType name="text_ik" class="solr.TextField">
            <analyzer type="index">
                <tokenizer class="org.wltea.analyzer.lucene.IKTokenizerFactory" isMaxWordLength="false"/>
                <filter class="com.wandoujia.xsearch.analysis.SynonymFilterFactory" ignoreCase="true"/>
                <filter class="solr.LowerCaseFilterFactory"/>
                <filter class="solr.LengthFilterFactory" min="2" max="12"/>
            </analyzer>
            <analyzer type="query">
                <tokenizer class="org.wltea.analyzer.lucene.IKTokenizerFactory" isMaxWordLength="true"/>
                <filter class="com.wandoujia.xsearch.analysis.SynonymFilterFactory" ignoreCase="true"/>
                <filter class="solr.LowerCaseFilterFactory"/>
            </analyzer>   
        </fieldType>

        <fieldType name="text_ik_title" class="solr.TextField">
            <analyzer type="index">
                <tokenizer class="org.wltea.analyzer.lucene.IKTokenizerFactory" isMaxWordLength="false" isSmartSingleWordFilter="true"/>
                <filter class="solr.LowerCaseFilterFactory"/>
            </analyzer>
            <analyzer type="query">
                <tokenizer class="org.wltea.analyzer.lucene.IKTokenizerFactory" isMaxWordLength="false" isSmartSingleWordFilter="true"/>
                <filter class="solr.LowerCaseFilterFactory"/>
            </analyzer>   
        </fieldType>

    </types>

    <!--
    <similarity class="org.apache.lucene.search.similarities.DefaultSimilarity"/>
    -->
    <similarity class="com.wandoujia.xsearch.similarities.CustomSimilarity"/>

</schema>
'''

globalvars = {} 
localvars = {}


from string import *
import re
from yappsrt import *

class ProtoParserScanner(Scanner):
    patterns = [
        ('"false"', re.compile('false')),
        ('"true"', re.compile('true')),
        ('"repeatable"', re.compile('repeatable')),
        ('"UTC_TIME"', re.compile('UTC_TIME')),
        ('"DOUBLE"', re.compile('DOUBLE')),
        ('"INT64"', re.compile('INT64')),
        ('"INTEGER"', re.compile('INTEGER')),
        ('"full_match"', re.compile('full_match')),
        ('"free_text_search"', re.compile('free_text_search')),
        ('"URL"', re.compile('URL')),
        ('"TEXT"', re.compile('TEXT')),
        ('"ENUM"', re.compile('ENUM')),
        ('"NUM"', re.compile('NUM')),
        ('"\\""', re.compile('"')),
        ('"\\\\}"', re.compile('\\}')),
        ('"\\\\{"', re.compile('\\{')),
        ('":"', re.compile(':')),
        ('[ \r\t\n]+', re.compile('[ \r\t\n]+')),
        ('END', re.compile('$')),
        ('ID', re.compile('annotation_id')),
        ('NAME', re.compile('annotation_name')),
        ('TYPE', re.compile('annotation_type')),
        ('NUM_TYPE', re.compile('type')),
        ('DOC_TYPE', re.compile('doc_type')),
        ('DOC_SCHEMA', re.compile('doc_schema')),
        ('ANNO_SCHEMA', re.compile('[a-zA-Z]+_schema')),
        ('ANNO_NAME', re.compile('annotation_name')),
        ('ANNO_TYPE', re.compile('annotation_type')),
        ('KEY', re.compile('[a-zA-Z0-9_]+')),
        ('VAL', re.compile('[a-zA-Z0-9_]+')),
        ('VALSTR', re.compile('[a-zA-Z0-9_"]+')),
        ('NUM', re.compile('[0-9]+')),
        ('TRUE', re.compile('true')),
        ('FALSE', re.compile('false')),
        ('OTHER', re.compile('[a-zA-Z0-9_\\{\\}":]+')),
    ]
    def __init__(self, str):
        Scanner.__init__(self,None,['[ \r\t\n]+'],str)

class ProtoParser(Parser):
    def goal(self):
        doctype = self.doctype()
        print head
        main = globalvars['doc_type'][9:].lower()
        print "<schema name=\"" + main + "\" version=\"1.5\">"
        print "    <fields>"
        print '''      <field name="id" type="string" indexed="true" stored="true" required="true"/>'''
        while self._peek('END', 'DOC_SCHEMA') == 'DOC_SCHEMA':
            docschema = self.docschema()
            print "      <field name=\"" + localvars['name'] + "\" type=\"" + localvars['type'] + "\" index=\"" + localvars['indexed'] + "\" stored=\"" + localvars['stored'] + "\"",
            print localvars['multiValued'] == "true" and "multiValued=true />" or "/>"
        END = self._scan('END')
        print '''      <field name="_version_" type="long" indexed="true" stored="true"/>'''
        print '''      <field name="signature" type="string" stored="true" indexed="true" multiValued="false" />'''
        print '''    </fields>'''
        print tail
        return ""

    def doctype(self):
        DOC_TYPE = self._scan('DOC_TYPE')
        self._scan('":"')
        VAL = self._scan('VAL')
        globalvars["doc_type"] = VAL

    def docschema(self):
        DOC_SCHEMA = self._scan('DOC_SCHEMA')
        self._scan('"\\\\{"')
        localvars['indexed'] = 'true'
        localvars['stored'] = 'true'
        localvars['multiValued'] = 'false'
        while self._peek('"\\\\}"', 'ANNO_NAME', 'ANNO_TYPE', '"free_text_search"', '"full_match"', 'NUM_TYPE', '"repeatable"', 'KEY', 'ANNO_SCHEMA') != '"\\\\}"':
            _token_ = self._peek('ANNO_NAME', 'ANNO_TYPE', '"free_text_search"', '"full_match"', 'NUM_TYPE', '"repeatable"', 'KEY', 'ANNO_SCHEMA')
            if _token_ != 'ANNO_SCHEMA':
                keyval = self.keyval()
            else:# == 'ANNO_SCHEMA'
                annoschema = self.annoschema()
                
        self._scan('"\\\\}"')
        if localvars['etype'] == True and localvars['type'] == 'string': localvars['type'] = 'text_ik_title'

    def keyval(self):
        _token_ = self._peek('ANNO_NAME', 'ANNO_TYPE', '"free_text_search"', '"full_match"', 'NUM_TYPE', '"repeatable"', 'KEY')
        if _token_ == 'ANNO_NAME':
            ANNO_NAME = self._scan('ANNO_NAME')
            self._scan('":"')
            _token_ = self._peek('VAL', '"\\""')
            if _token_ == 'VAL':
                VAL = self._scan('VAL')
            else:# == '"\\""'
                self._scan('"\\""')
                VAL = self._scan('VAL')
                self._scan('"\\""')
            localvars['name'] = VAL
        elif _token_ == 'ANNO_TYPE':
            ANNO_TYPE = self._scan('ANNO_TYPE')
            self._scan('":"')
            _token_ = self._peek('"NUM"', '"ENUM"', '"TEXT"', '"URL"')
            if _token_ == '"NUM"':
                self._scan('"NUM"')
                localvars['type'] = 'int'
            elif _token_ == '"ENUM"':
                self._scan('"ENUM"')
                localvars['type'] = 'int'
            elif _token_ == '"TEXT"':
                self._scan('"TEXT"')
                localvars['type'] = 'string'
            else:# == '"URL"'
                self._scan('"URL"')
                localvars['type'] = 'string'
        elif _token_ == '"free_text_search"':
            self._scan('"free_text_search"')
            self._scan('":"')
            _token_ = self._peek('TRUE', 'FALSE')
            if _token_ == 'TRUE':
                TRUE = self._scan('TRUE')
                localvars['etype'] = True
            else:# == 'FALSE'
                FALSE = self._scan('FALSE')
                localvars['etype'] = False
        elif _token_ == '"full_match"':
            self._scan('"full_match"')
            self._scan('":"')
            _token_ = self._peek('FALSE', 'TRUE')
            if _token_ == 'FALSE':
                FALSE = self._scan('FALSE')
                localvars['type'] = 'text_ik'
            else:# == 'TRUE'
                TRUE = self._scan('TRUE')
                localvars['type'] = 'string'
        elif _token_ == 'NUM_TYPE':
            NUM_TYPE = self._scan('NUM_TYPE')
            self._scan('":"')
            _token_ = self._peek('"INTEGER"', '"INT64"', '"DOUBLE"', '"UTC_TIME"')
            if _token_ == '"INTEGER"':
                self._scan('"INTEGER"')
                localvars['type'] = 'int'
            elif _token_ == '"INT64"':
                self._scan('"INT64"')
                localvars['type'] = 'long'
            elif _token_ == '"DOUBLE"':
                self._scan('"DOUBLE"')
                localvars['type'] = 'double'
            else:# == '"UTC_TIME"'
                self._scan('"UTC_TIME"')
                localvars['type'] = 'date'
        elif _token_ == '"repeatable"':
            self._scan('"repeatable"')
            self._scan('":"')
            _token_ = self._peek('"true"', '"false"')
            if _token_ == '"true"':
                self._scan('"true"')
                localvars['multiValued'] = 'true'
            else:# == '"false"'
                self._scan('"false"')
                localvars['multiValued'] = 'false'
        else:# == 'KEY'
            KEY = self._scan('KEY')
            self._scan('":"')
            _token_ = self._peek('VAL', '"\\""')
            if _token_ == 'VAL':
                VAL = self._scan('VAL')
                
            else:# == '"\\""'
                self._scan('"\\""')
                VAL = self._scan('VAL')
                self._scan('"\\""')
                

    def annoschema(self):
        ANNO_SCHEMA = self._scan('ANNO_SCHEMA')
        self._scan('"\\\\{"')
        
        while self._peek('ANNO_NAME', 'ANNO_TYPE', '"free_text_search"', '"full_match"', 'NUM_TYPE', '"repeatable"', 'KEY', '"\\\\}"', 'ANNO_SCHEMA') not in ['"\\\\}"', 'ANNO_SCHEMA']:
            keyval = self.keyval()
        
        self._scan('"\\\\}"')
        


def parse(rule, text):
    P = ProtoParser(ProtoParserScanner(text))
    return wrap_error_reporter(P, rule)

if __name__ == '__main__':
    from sys import argv, stdin
    if len(argv) >= 2:
        if len(argv) >= 3:
            f = open(argv[2],'r')
        else:
            f = stdin
        print parse(argv[1], f.read())
    else: print 'Args:  <rule> [<filename>]'
