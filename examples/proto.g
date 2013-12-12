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

%%
parser ProtoParser:
    ignore:     "[ \r\t\n]+"
    token END:  "$" 
    token ID:   "annotation_id"
    token NAME: "annotation_name"
    token TYPE: "annotation_type"
    token NUM_TYPE: "type"
    token DOC_TYPE: "doc_type"
    token DOC_SCHEMA: "doc_schema"
    token ANNO_SCHEMA: "[a-zA-Z]+_schema"
    token ANNO_NAME: "annotation_name"
    token ANNO_TYPE: "annotation_type"
    token KEY: "[a-zA-Z0-9_]+"
    token VAL: "[a-zA-Z0-9_]+"
    token VALSTR: "[a-zA-Z0-9_\"]+"
    token NUM: "[0-9]+"
    token TRUE: "true"
    token FALSE: "false"
    token OTHER: "[a-zA-Z0-9_\{\}\":]+"


    rule goal:  doctype         {{ print head }}
                                {{ main = globalvars['doc_type'][9:].lower() }}
                                {{ print "<schema name=\"" + main + "\" version=\"1.5\">" }}
                                {{ print "    <fields>" }}
                                {{ print '''      <field name="id" type="string" indexed="true" stored="true" required="true"/>'''  }}

                (               docschema    {{ print "      <field name=\"" + localvars['name'] + "\" type=\"" + localvars['type'] + "\" index=\"" + localvars['indexed'] + "\" stored=\"" + localvars['stored'] + "\"", }}
                                {{ print localvars['multiValued'] == "true" and "multiValued=true />" or "/>" }}
                )* END          {{ print '''      <field name="_version_" type="long" indexed="true" stored="true"/>''' }}
                                {{ print '''      <field name="signature" type="string" stored="true" indexed="true" multiValued="false" />''' }}
                                {{ print '''    </fields>''' }}
                                {{ print tail }}
                                {{ return "" }}

    rule doctype: DOC_TYPE ":" VAL   {{ globalvars["doc_type"] = VAL }} 

    rule docschema: DOC_SCHEMA "\\{"       {{ localvars['indexed'] = 'true'}}
                                           {{ localvars['stored'] = 'true' }}
                                           {{ localvars['multiValued'] = 'false' }}
                    ( keyval  
                    | annoschema           {{ }}
                    )* 
                    "\\}"                  {{ if localvars['etype'] == True and localvars['type'] == 'string': localvars['type'] = 'text_ik_title' }}

    rule keyval:   ANNO_NAME ":" ( VAL | "\"" VAL "\"" )    {{ localvars['name'] = VAL }}
                  | ANNO_TYPE ":" 
                        ( "NUM"            {{ localvars['type'] = 'int' }}
                        | "ENUM"           {{ localvars['type'] = 'int' }}
                        | "TEXT"           {{ localvars['type'] = 'string' }}
                        | "URL"            {{ localvars['type'] = 'string' }}
                        )
                  | "free_text_search" ":"
                    ( TRUE                {{ localvars['etype'] = True }} 
                      | FALSE             {{ localvars['etype'] = False }}
                    )
                  | "full_match" ":"
                    ( FALSE               {{ localvars['type'] = 'text_ik' }} 
                     | TRUE               {{ localvars['type'] = 'string' }}
                    )
                  | NUM_TYPE ":"
                    ( "INTEGER"           {{ localvars['type'] = 'int' }}
                    | "INT64"             {{ localvars['type'] = 'long' }}
                    | "DOUBLE"            {{ localvars['type'] = 'double' }}
                    | "UTC_TIME"          {{ localvars['type'] = 'date' }}
                    )
                  | "repeatable" ":"
                    ( "true"              {{ localvars['multiValued'] = 'true' }}
                      | "false"           {{ localvars['multiValued'] = 'false' }}
                    )
                  | KEY ":" 
                    ( VAL                  {{ }} 
                      | "\"" VAL "\""      {{ }}
                    )
                  

    rule annoschema: ANNO_SCHEMA "\\{"     {{ }}
                     ( keyval )*           {{ }}
                        "\\}"              {{ }}
    

