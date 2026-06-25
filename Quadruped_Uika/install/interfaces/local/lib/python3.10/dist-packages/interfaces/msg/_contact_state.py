# generated from rosidl_generator_py/resource/_idl.py.em
# with input from interfaces:msg/ContactState.idl
# generated code does not contain a copyright notice


# Import statements for member types

import builtins  # noqa: E402, I100

import rosidl_parser.definition  # noqa: E402, I100


class Metaclass_ContactState(type):
    """Metaclass of message 'ContactState'."""

    _CREATE_ROS_MESSAGE = None
    _CONVERT_FROM_PY = None
    _CONVERT_TO_PY = None
    _DESTROY_ROS_MESSAGE = None
    _TYPE_SUPPORT = None

    __constants = {
    }

    @classmethod
    def __import_type_support__(cls):
        try:
            from rosidl_generator_py import import_type_support
            module = import_type_support('interfaces')
        except ImportError:
            import logging
            import traceback
            logger = logging.getLogger(
                'interfaces.msg.ContactState')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__msg__contact_state
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__msg__contact_state
            cls._CONVERT_TO_PY = module.convert_to_py_msg__msg__contact_state
            cls._TYPE_SUPPORT = module.type_support_msg__msg__contact_state
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__msg__contact_state

            from std_msgs.msg import Header
            if Header.__class__._TYPE_SUPPORT is None:
                Header.__class__.__import_type_support__()

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
        }


class ContactState(metaclass=Metaclass_ContactState):
    """Message class 'ContactState'."""

    __slots__ = [
        '_header',
        '_fl_contact',
        '_fr_contact',
        '_rl_contact',
        '_rr_contact',
    ]

    _fields_and_field_types = {
        'header': 'std_msgs/Header',
        'fl_contact': 'boolean',
        'fr_contact': 'boolean',
        'rl_contact': 'boolean',
        'rr_contact': 'boolean',
    }

    SLOT_TYPES = (
        rosidl_parser.definition.NamespacedType(['std_msgs', 'msg'], 'Header'),  # noqa: E501
        rosidl_parser.definition.BasicType('boolean'),  # noqa: E501
        rosidl_parser.definition.BasicType('boolean'),  # noqa: E501
        rosidl_parser.definition.BasicType('boolean'),  # noqa: E501
        rosidl_parser.definition.BasicType('boolean'),  # noqa: E501
    )

    def __init__(self, **kwargs):
        assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
            'Invalid arguments passed to constructor: %s' % \
            ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        from std_msgs.msg import Header
        self.header = kwargs.get('header', Header())
        self.fl_contact = kwargs.get('fl_contact', bool())
        self.fr_contact = kwargs.get('fr_contact', bool())
        self.rl_contact = kwargs.get('rl_contact', bool())
        self.rr_contact = kwargs.get('rr_contact', bool())

    def __repr__(self):
        typename = self.__class__.__module__.split('.')
        typename.pop()
        typename.append(self.__class__.__name__)
        args = []
        for s, t in zip(self.__slots__, self.SLOT_TYPES):
            field = getattr(self, s)
            fieldstr = repr(field)
            # We use Python array type for fields that can be directly stored
            # in them, and "normal" sequences for everything else.  If it is
            # a type that we store in an array, strip off the 'array' portion.
            if (
                isinstance(t, rosidl_parser.definition.AbstractSequence) and
                isinstance(t.value_type, rosidl_parser.definition.BasicType) and
                t.value_type.typename in ['float', 'double', 'int8', 'uint8', 'int16', 'uint16', 'int32', 'uint32', 'int64', 'uint64']
            ):
                if len(field) == 0:
                    fieldstr = '[]'
                else:
                    assert fieldstr.startswith('array(')
                    prefix = "array('X', "
                    suffix = ')'
                    fieldstr = fieldstr[len(prefix):-len(suffix)]
            args.append(s[1:] + '=' + fieldstr)
        return '%s(%s)' % ('.'.join(typename), ', '.join(args))

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if self.header != other.header:
            return False
        if self.fl_contact != other.fl_contact:
            return False
        if self.fr_contact != other.fr_contact:
            return False
        if self.rl_contact != other.rl_contact:
            return False
        if self.rr_contact != other.rr_contact:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

    @builtins.property
    def header(self):
        """Message field 'header'."""
        return self._header

    @header.setter
    def header(self, value):
        if __debug__:
            from std_msgs.msg import Header
            assert \
                isinstance(value, Header), \
                "The 'header' field must be a sub message of type 'Header'"
        self._header = value

    @builtins.property
    def fl_contact(self):
        """Message field 'fl_contact'."""
        return self._fl_contact

    @fl_contact.setter
    def fl_contact(self, value):
        if __debug__:
            assert \
                isinstance(value, bool), \
                "The 'fl_contact' field must be of type 'bool'"
        self._fl_contact = value

    @builtins.property
    def fr_contact(self):
        """Message field 'fr_contact'."""
        return self._fr_contact

    @fr_contact.setter
    def fr_contact(self, value):
        if __debug__:
            assert \
                isinstance(value, bool), \
                "The 'fr_contact' field must be of type 'bool'"
        self._fr_contact = value

    @builtins.property
    def rl_contact(self):
        """Message field 'rl_contact'."""
        return self._rl_contact

    @rl_contact.setter
    def rl_contact(self, value):
        if __debug__:
            assert \
                isinstance(value, bool), \
                "The 'rl_contact' field must be of type 'bool'"
        self._rl_contact = value

    @builtins.property
    def rr_contact(self):
        """Message field 'rr_contact'."""
        return self._rr_contact

    @rr_contact.setter
    def rr_contact(self, value):
        if __debug__:
            assert \
                isinstance(value, bool), \
                "The 'rr_contact' field must be of type 'bool'"
        self._rr_contact = value
