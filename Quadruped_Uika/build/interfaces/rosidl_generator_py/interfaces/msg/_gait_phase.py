# generated from rosidl_generator_py/resource/_idl.py.em
# with input from interfaces:msg/GaitPhase.idl
# generated code does not contain a copyright notice


# Import statements for member types

import builtins  # noqa: E402, I100

import rosidl_parser.definition  # noqa: E402, I100


class Metaclass_GaitPhase(type):
    """Metaclass of message 'GaitPhase'."""

    _CREATE_ROS_MESSAGE = None
    _CONVERT_FROM_PY = None
    _CONVERT_TO_PY = None
    _DESTROY_ROS_MESSAGE = None
    _TYPE_SUPPORT = None

    __constants = {
        'STANCE': 0,
        'SWING': 1,
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
                'interfaces.msg.GaitPhase')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__msg__gait_phase
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__msg__gait_phase
            cls._CONVERT_TO_PY = module.convert_to_py_msg__msg__gait_phase
            cls._TYPE_SUPPORT = module.type_support_msg__msg__gait_phase
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__msg__gait_phase

            from std_msgs.msg import Header
            if Header.__class__._TYPE_SUPPORT is None:
                Header.__class__.__import_type_support__()

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
            'STANCE': cls.__constants['STANCE'],
            'SWING': cls.__constants['SWING'],
        }

    @property
    def STANCE(self):
        """Message constant 'STANCE'."""
        return Metaclass_GaitPhase.__constants['STANCE']

    @property
    def SWING(self):
        """Message constant 'SWING'."""
        return Metaclass_GaitPhase.__constants['SWING']


class GaitPhase(metaclass=Metaclass_GaitPhase):
    """
    Message class 'GaitPhase'.

    Constants:
      STANCE
      SWING
    """

    __slots__ = [
        '_header',
        '_fl_phase',
        '_fr_phase',
        '_rl_phase',
        '_rr_phase',
    ]

    _fields_and_field_types = {
        'header': 'std_msgs/Header',
        'fl_phase': 'uint8',
        'fr_phase': 'uint8',
        'rl_phase': 'uint8',
        'rr_phase': 'uint8',
    }

    SLOT_TYPES = (
        rosidl_parser.definition.NamespacedType(['std_msgs', 'msg'], 'Header'),  # noqa: E501
        rosidl_parser.definition.BasicType('uint8'),  # noqa: E501
        rosidl_parser.definition.BasicType('uint8'),  # noqa: E501
        rosidl_parser.definition.BasicType('uint8'),  # noqa: E501
        rosidl_parser.definition.BasicType('uint8'),  # noqa: E501
    )

    def __init__(self, **kwargs):
        assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
            'Invalid arguments passed to constructor: %s' % \
            ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        from std_msgs.msg import Header
        self.header = kwargs.get('header', Header())
        self.fl_phase = kwargs.get('fl_phase', int())
        self.fr_phase = kwargs.get('fr_phase', int())
        self.rl_phase = kwargs.get('rl_phase', int())
        self.rr_phase = kwargs.get('rr_phase', int())

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
        if self.fl_phase != other.fl_phase:
            return False
        if self.fr_phase != other.fr_phase:
            return False
        if self.rl_phase != other.rl_phase:
            return False
        if self.rr_phase != other.rr_phase:
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
    def fl_phase(self):
        """Message field 'fl_phase'."""
        return self._fl_phase

    @fl_phase.setter
    def fl_phase(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'fl_phase' field must be of type 'int'"
            assert value >= 0 and value < 256, \
                "The 'fl_phase' field must be an unsigned integer in [0, 255]"
        self._fl_phase = value

    @builtins.property
    def fr_phase(self):
        """Message field 'fr_phase'."""
        return self._fr_phase

    @fr_phase.setter
    def fr_phase(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'fr_phase' field must be of type 'int'"
            assert value >= 0 and value < 256, \
                "The 'fr_phase' field must be an unsigned integer in [0, 255]"
        self._fr_phase = value

    @builtins.property
    def rl_phase(self):
        """Message field 'rl_phase'."""
        return self._rl_phase

    @rl_phase.setter
    def rl_phase(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'rl_phase' field must be of type 'int'"
            assert value >= 0 and value < 256, \
                "The 'rl_phase' field must be an unsigned integer in [0, 255]"
        self._rl_phase = value

    @builtins.property
    def rr_phase(self):
        """Message field 'rr_phase'."""
        return self._rr_phase

    @rr_phase.setter
    def rr_phase(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'rr_phase' field must be of type 'int'"
            assert value >= 0 and value < 256, \
                "The 'rr_phase' field must be an unsigned integer in [0, 255]"
        self._rr_phase = value
