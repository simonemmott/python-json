import os, json, re
from enum import Enum

RE_IS_FLOAT = re.compile('[+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?')

class Expects(Enum):
    NAME = 'name'
    VALUE = 'value'
    END_OBJECT = 'end_object'
    END_LIST = 'end_list'
    
class JsonWriterException(Exception):
    pass

class JsonReaderException(Exception):
    pass

def encode(s):
    return json.dumps(s)
        
def decode(s):
    return json.loads(s)

class JsonStates(Enum):
    OPEN = 0
    IN_OBJECT = 1
    IN_OBJECT_WITH_NAME = 2
    IN_OBJECT_WITH_NAME_AND_VALUE = 3
    IN_LIST = 4
    IN_LIST_WITH_VALUE = 5
    CLOSED = 6

class JsonState(object):
    def __init__(self, previous, state):
        self.previous = previous
        self._state = state
        
    def state(self, *args):
        if len(args) > 0:
            self._state = args[0]
        return self._state

class JsonWriter(object):
           
    def __init__(self, writer, **kw):
        self.writer = writer
        self.indent = kw.get('indent', '')
        self.depth = 0
        self.linesep = os.linesep if len(self.indent) > 0 else ''
        self.current_indent = ''
        self.quote = kw.get('quote', JsonToken.QUOTE.value)
        self.varsep = kw.get('varsep', JsonToken.VALUE_SEPARATOR.value)
        self.namesep = kw.get('namesep', JsonToken.NAME_SEPARATOR.value)
        self.startobj = kw.get('start_obj', JsonToken.START_OBJECT.value)
        self.endobj = kw.get('end_obj', JsonToken.END_OBJECT.value)
        self.startlist = kw.get('start_list', JsonToken.START_LIST.value)
        self.endlist = kw.get('end_list', JsonToken.END_LIST.value)
        self.state = JsonState(None, JsonStates.OPEN)
        self.expects = None
        
    def _token(self, token):
        if token == JsonToken.QUOTE: return self.quote
        if token == JsonToken.VALUE_SEPARATOR: return self.varsep
        if token == JsonToken.NAME_SEPARATOR: return self.namesep
        if token == JsonToken.START_OBJECT: return self.startobj
        if token == JsonToken.END_OBJECT: return self.endobj
        if token == JsonToken.START_LIST: return self.startlist
        if token == JsonToken.END_LIST: return self.endlist
        raise ValueError('Expected token as JsonToken')
        
    def _indent(self, state):
        self.debug('_indent("%s")' % state)
        self.depth += 1
        self.current_indent += self.indent
        if self.state.state() == JsonStates.IN_OBJECT or self.state.state() == JsonStates.IN_OBJECT_WITH_NAME:
            self.state.state(JsonStates.IN_OBJECT_WITH_NAME_AND_VALUE)
        elif self.state.state() == JsonStates.IN_LIST:
            self.state.state(JsonStates.IN_LIST_WITH_VALUE)
        self.state = JsonState(self.state, state)
        
    def _outdent(self):
        self.debug('_outdent()')
        if self.depth == 0:
            return
        self.depth -= 1
        self.current_indent = self.current_indent[:-len(self.indent)]
        self.state = self.state.previous
        
    def _check_expects(self, expects):
        if self.expects == None:
            print('Expects anything')
            return
        for ex in self.expects:
            print('Checking expects %s      State: %s      PreviousState: %s' % (ex.value, self.state.state(), self.state.previous.state() if self.state.previous != None else 'None'))
            if ex == expects:
                return
        expected = ''
        for ex in self.expects:
            expected += ex.value+' or '
        expected = expected[:-4]
        raise JsonWriterException('JsonWriter expected a %s but got a %s' % (expected, expects.value))
        
    def _set_expects(self, *expects):
        self.expects = expects
        e = ''
        for ex in self.expects:
            e += ex.value+' '
        print('Expects: %s      State: %s      PreviousState: %s' % (e, self.state.state(), self.state.previous.state() if self.state.previous != None else 'None'))
        
    def debug(self, caller):
        return
        print('%s      State: %s      PreviousState: %s' % (caller, self.state.state(), self.state.previous.state() if self.state.previous != None else 'None'))
        
    def name(self, name):
        self.debug('name("%s")' % name)
#        self._check_expects(Expects.NAME)
        if self.state.state() == JsonStates.IN_OBJECT_WITH_NAME_AND_VALUE:
            self.writer.write(self._token(JsonToken.VALUE_SEPARATOR)+' '+self.linesep)
        self.writer.write(self.current_indent+self._token(JsonToken.QUOTE)+name+self._token(JsonToken.QUOTE)+self._token(JsonToken.NAME_SEPARATOR)+' ')
        if self.state.state() == JsonStates.IN_OBJECT or self.state.state() == JsonStates.IN_OBJECT_WITH_NAME_AND_VALUE:
            self.state.state(JsonStates.IN_OBJECT_WITH_NAME)
#        self._set_expects(Expects.VALUE)
        
    def value(self, value):
        self.debug('value(%s)' % encode(value))
#        self._check_expects(Expects.VALUE)       
        if self.state.state() == JsonStates.IN_LIST_WITH_VALUE:
            self.writer.write(self._token(JsonToken.VALUE_SEPARATOR)+' '+self.linesep)
            
        if self.state.state() == JsonStates.IN_LIST_WITH_VALUE or self.state.state() == JsonStates.IN_LIST:
            self.writer.write(self.current_indent)
        if value == None:
            self.writer.write(encode(value))
        elif isinstance(value, (int, float, str, bool)):
            self.writer.write(encode(value))
        else:
            raise JsonWriterException('JsonWriter only accepts int, float, string, boolean or None as a value')
        
        if self.state.state() == JsonStates.IN_OBJECT_WITH_NAME:
            self.state.state(JsonStates.IN_OBJECT_WITH_NAME_AND_VALUE)
#            self._set_expects(Expects.END_OBJECT, Expects.NAME)
        elif self.state.state() == JsonStates.IN_LIST or self.state.state() == JsonStates.IN_LIST_WITH_VALUE:
            self.state.state(JsonStates.IN_LIST_WITH_VALUE)
#            self._set_expects(Expects.END_LIST, Expects.VALUE)
                   
        
    def begin_object(self):
        self.debug('begin_object()')
        if self.state.state() == JsonStates.IN_OBJECT_WITH_NAME_AND_VALUE or self.state.state() == JsonStates.IN_LIST_WITH_VALUE:
            self.writer.write(self._token(JsonToken.VALUE_SEPARATOR)+' '+self.linesep)
#        self._check_expects(Expects.VALUE)
        if self.state.state() == JsonStates.IN_OBJECT_WITH_NAME_AND_VALUE or self.state.state() == JsonStates.IN_OBJECT_WITH_NAME:
            self.writer.write(self._token(JsonToken.START_OBJECT) + self.linesep)
        else:
            self.writer.write(self.current_indent + self._token(JsonToken.START_OBJECT) + self.linesep)
        self._indent(JsonStates.IN_OBJECT)
#        self._set_expects(Expects.NAME, Expects.END_OBJECT)

    def end_object(self):
        self.debug('end_object()')
        if self.state.state() == JsonStates.IN_OBJECT_WITH_NAME_AND_VALUE or self.state.state() == JsonStates.IN_LIST_WITH_VALUE:
            self.writer.write(self.linesep)
        self._outdent()
        self.writer.write(self.current_indent + self._token(JsonToken.END_OBJECT))

    def begin_list(self):
        self.debug('begin_list()')
        if self.state.state() == JsonStates.IN_OBJECT_WITH_NAME_AND_VALUE or self.state.state() == JsonStates.IN_LIST_WITH_VALUE:
            self.writer.write(self._token(JsonToken.VALUE_SEPARATOR)+' '+self.linesep)
#        self._check_expects(Expects.VALUE)
        if self.state.state() == JsonStates.IN_OBJECT_WITH_NAME:
            self.writer.write(self._token(JsonToken.START_LIST) + self.linesep)
        else:
            self.writer.write(self.current_indent + self._token(JsonToken.START_LIST) + self.linesep)
        self._indent(JsonStates.IN_LIST)
#        self._set_expects(Expects.VALUE, Expects.END_LIST)

    def end_list(self):
        self.debug('end_list()')
        if self.state.state() == JsonStates.IN_OBJECT_WITH_NAME_AND_VALUE or self.state.state() == JsonStates.IN_LIST_WITH_VALUE:
            self.writer.write(self.linesep)
        self._outdent()
        self.writer.write(self.current_indent + self._token(JsonToken.END_LIST))

class JsonToken(Enum):
    START_LIST = '['
    END_LIST = ']'
    START_OBJECT = '{'
    END_OBJECT = '}'
    QUOTE = '"'
    VALUE_SEPARATOR = ','
    NAME_SEPARATOR = ':'
    
class JsonNodeType(Enum):
    START_LIST = 'start_list'
    END_LIST = 'end_list'
    START_OBJECT = 'start_object'
    END_OBJECT = 'end_object'
    NAME = 'name'
    BOOL_VALUE = 'bool_value'
    NUM_VALUE = 'num_value'
    STR_VALUE = 'str_value'
    NULL_VALUE = 'null_value'
    
class JsonNode(object):
    def __init__(self, reader, type):
        self.reader = reader
        self.type = type
        
    def type_is(self, type):
        return self.type == type
        
class JsonStartObjectNode(JsonNode):
    def __init__(self, reader):
        JsonNode.__init__(self, reader, JsonNodeType.START_OBJECT)
        
class JsonEndObjectNode(JsonNode):
    def __init__(self, reader):
        JsonNode.__init__(self, reader, JsonNodeType.END_OBJECT)
        
class JsonStartListNode(JsonNode):
    def __init__(self, reader):
        JsonNode.__init__(self, reader, JsonNodeType.START_LIST)
        
class JsonEndListNode(JsonNode):
    def __init__(self, reader):
        JsonNode.__init__(self, reader, JsonNodeType.END_LIST)
        
class JsonNameNode(JsonNode):
    def __init__(self, reader, name):
        JsonNode.__init__(self, reader, JsonNodeType.NAME)
        self.name = name
 
class JsonValueNode(JsonNode):
    def __init__(self, reader, type):
        JsonNode.__init__(self, reader, type)
    @staticmethod
    def value_node(reader, value):
        if value == None or len(value) == 0 or value.upper() == 'NULL': 
            return JsonNullNode(reader)
        if value.upper() in ['TRUE', 'FALSE']:
            return JsonBooleanNode(reader, value)
        if len(value) >= 2 and value[0] == reader._token(JsonToken.QUOTE) and value[-1:] == reader._token(JsonToken.QUOTE):
            return JsonStringNode(reader, value[1:-1])
        if RE_IS_FLOAT.search(value):
            return JsonNumberNode(reader, value)
        raise JsonReaderException('Invalid value: %s in JSON' % value)
        
        
class JsonBooleanNode(JsonValueNode):
    def __init__(self, reader, value):
        JsonValueNode.__init__(self, reader, JsonNodeType.BOOL_VALUE)
        self.value = value.upper() == 'TRUE'
        
class JsonNumberNode(JsonValueNode):
    def __init__(self, reader, value):
        JsonValueNode.__init__(self, reader, JsonNodeType.NUM_VALUE)
        if '.' in value:
            self.value = float(value)
        else:
            self.value = int(value)
        
class JsonStringNode(JsonValueNode):
    def __init__(self, reader, value):
        JsonValueNode.__init__(self, reader, JsonNodeType.STR_VALUE)
        
class JsonNullNode(JsonValueNode):
    def __init__(self, reader):
        JsonValueNode.__init__(self, reader, JsonNodeType.NULL_VALUE)
    
class JsonReader(object):
    def __init__(self, reader, **kw):
        self.reader = reader
        self.quote = kw.get('quote', JsonToken.QUOTE.value)
        self.varsep = kw.get('varsep', JsonToken.VALUE_SEPARATOR.value)
        self.namesep = kw.get('namesep', JsonToken.NAME_SEPARATOR.value)
        self.startobj = kw.get('start_obj', JsonToken.START_OBJECT.value)
        self.endobj = kw.get('end_obj', JsonToken.END_OBJECT.value)
        self.startlist = kw.get('start_list', JsonToken.START_LIST.value)
        self.endlist = kw.get('end_list', JsonToken.END_LIST.value)
        self.current = None
        self.next = None
        self._move_to_start()

    def _token(self, token):
        if token == JsonToken.QUOTE: return self.quote
        if token == JsonToken.VALUE_SEPARATOR: return self.varsep
        if token == JsonToken.NAME_SEPARATOR: return self.namesep
        if token == JsonToken.START_OBJECT: return self.startobj
        if token == JsonToken.END_OBJECT: return self.endobj
        if token == JsonToken.START_LIST: return self.startlist
        if token == JsonToken.END_LIST: return self.endlist
        raise ValueError('Expected token as JsonToken')
        
    def _move_to_start(self):
        c = self.reader.read(chars=1)
        while c.isspace():
            c = self.reader.read(chars=1)
            
        if c == self._token(JsonToken.START_OBJECT):
            self.next = JsonStartObjectNode(self)
        elif c == self._token(JsonToken.START_LIST):
            self.next = JsonStartListNode(self)
        else:
            raise JsonReaderException('Json documents must start with an object or list')
            
        
    def _read_next_node(self):
        if self.next == None:
            return None
        self.current = self.next
        
        if self.current.type_is(JsonNodeType.START_OBJECT):
            s = self.reader._read_until(self._token(JsonToken.END_OBJECT), self._token(JsonToken.QUOTE))
            if s[-1:] == self._token(JsonToken.END_OBJECT):
                self.next = JsonEndObjectNode
            elif s[-1:] == self._token(JsonToken.QUOTE):
                pass
        elif self.current.type_is(JsonNodeType.END_OBJECT):
            pass
        elif self.current.type_is(JsonNodeType.START_LIST):
            pass
        elif self.current.type_is(JsonNodeType.END_LIST):
            pass
        elif self.current.type_is(JsonNodeType.NAME):
            pass
        elif self.current.type_is(JsonNodeType.BOOL_VALUE):
            pass
        elif self.current.type_is(JsonNodeType.NUM_VALUE):
            pass
        elif self.current.type_is(JsonNodeType.STR_VALUE):
            pass
        elif self.current.type_is(JsonNodeType.NULL_VALUE):
            pass
        else:
            raise JsonReaderException('Unexpected type: %s found in JSON' % self.current.type)
        
        self.reader
        if self.current_node == None:
            
            pass
        else:
            pass
        
    def has_next(self):
        return self.next != None
    
    def peek(self):
        return self.next
    
    def begin_object(self):
        if not self.next.type_is(JsonNodeType.START_OBJECT):
            raise JsonReaderException('Expected start object but got %s' % self.next.type)
        
        
        
        
        
        
        
        
        
        