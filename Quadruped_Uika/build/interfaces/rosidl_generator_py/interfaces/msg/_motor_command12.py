# generated from rosidl_generator_py/resource/_idl.py.em
# with input from interfaces:msg/MotorCommand12.idl
# generated code does not contain a copyright notice


# Import statements for member types

import builtins  # noqa: E402, I100

import rosidl_parser.definition  # noqa: E402, I100


class Metaclass_MotorCommand12(type):
    """Metaclass of message 'MotorCommand12'."""

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
                'interfaces.msg.MotorCommand12')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__msg__motor_command12
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__msg__motor_command12
            cls._CONVERT_TO_PY = module.convert_to_py_msg__msg__motor_command12
            cls._TYPE_SUPPORT = module.type_support_msg__msg__motor_command12
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__msg__motor_command12

            from interfaces.msg import MotorCommand
            if MotorCommand.__class__._TYPE_SUPPORT is None:
                MotorCommand.__class__.__import_type_support__()

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


class MotorCommand12(metaclass=Metaclass_MotorCommand12):
    """Message class 'MotorCommand12'."""

    __slots__ = [
        '_header',
        '_fl_hip',
        '_fl_thigh',
        '_fl_calf',
        '_fr_hip',
        '_fr_thigh',
        '_fr_calf',
        '_rl_hip',
        '_rl_thigh',
        '_rl_calf',
        '_rr_hip',
        '_rr_thigh',
        '_rr_calf',
    ]

    _fields_and_field_types = {
        'header': 'std_msgs/Header',
        'fl_hip': 'interfaces/MotorCommand',
        'fl_thigh': 'interfaces/MotorCommand',
        'fl_calf': 'interfaces/MotorCommand',
        'fr_hip': 'interfaces/MotorCommand',
        'fr_thigh': 'interfaces/MotorCommand',
        'fr_calf': 'interfaces/MotorCommand',
        'rl_hip': 'interfaces/MotorCommand',
        'rl_thigh': 'interfaces/MotorCommand',
        'rl_calf': 'interfaces/MotorCommand',
        'rr_hip': 'interfaces/MotorCommand',
        'rr_thigh': 'interfaces/MotorCommand',
        'rr_calf': 'interfaces/MotorCommand',
    }

    SLOT_TYPES = (
        rosidl_parser.definition.NamespacedType(['std_msgs', 'msg'], 'Header'),  # noqa: E501
        rosidl_parser.definition.NamespacedType(['interfaces', 'msg'], 'MotorCommand'),  # noqa: E501
        rosidl_parser.definition.NamespacedType(['interfaces', 'msg'], 'MotorCommand'),  # noqa: E501
        rosidl_parser.definition.NamespacedType(['interfaces', 'msg'], 'MotorCommand'),  # noqa: E501
        rosidl_parser.definition.NamespacedType(['interfaces', 'msg'], 'MotorCommand'),  # noqa: E501
        rosidl_parser.definition.NamespacedType(['interfaces', 'msg'], 'MotorCommand'),  # noqa: E501
        rosidl_parser.definition.NamespacedType(['interfaces', 'msg'], 'MotorCommand'),  # noqa: E501
        rosidl_parser.definition.NamespacedType(['interfaces', 'msg'], 'MotorCommand'),  # noqa: E501
        rosidl_parser.definition.NamespacedType(['interfaces', 'msg'], 'MotorCommand'),  # noqa: E501
        rosidl_parser.definition.NamespacedType(['interfaces', 'msg'], 'MotorCommand'),  # noqa: E501
        rosidl_parser.definition.NamespacedType(['interfaces', 'msg'], 'MotorCommand'),  # noqa: E501
        rosidl_parser.definition.NamespacedType(['interfaces', 'msg'], 'MotorCommand'),  # noqa: E501
        rosidl_parser.definition.NamespacedType(['interfaces', 'msg'], 'MotorCommand'),  # noqa: E501
    )

    def __init__(self, **kwargs):
        assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
            'Invalid arguments passed to constructor: %s' % \
            ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        from std_msgs.msg import Header
        self.header = kwargs.get('header', Header())
        from interfaces.msg import MotorCommand
        self.fl_hip = kwargs.get('fl_hip', MotorCommand())
        from interfaces.msg import MotorCommand
        self.fl_thigh = kwargs.get('fl_thigh', MotorCommand())
        from interfaces.msg import MotorCommand
        self.fl_calf = kwargs.get('fl_calf', MotorCommand())
        from interfaces.msg import MotorCommand
        self.fr_hip = kwargs.get('fr_hip', MotorCommand())
        from interfaces.msg import MotorCommand
        self.fr_thigh = kwargs.get('fr_thigh', MotorCommand())
        from interfaces.msg import MotorCommand
        self.fr_calf = kwargs.get('fr_calf', MotorCommand())
        from interfaces.msg import MotorCommand
        self.rl_hip = kwargs.get('rl_hip', MotorCommand())
        from interfaces.msg import MotorCommand
        self.rl_thigh = kwargs.get('rl_thigh', MotorCommand())
        from interfaces.msg import MotorCommand
        self.rl_calf = kwargs.get('rl_calf', MotorCommand())
        from interfaces.msg import MotorCommand
        self.rr_hip = kwargs.get('rr_hip', MotorCommand())
        from interfaces.msg import MotorCommand
        self.rr_thigh = kwargs.get('rr_thigh', MotorCommand())
        from interfaces.msg import MotorCommand
        self.rr_calf = kwargs.get('rr_calf', MotorCommand())

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
        if self.fl_hip != other.fl_hip:
            return False
        if self.fl_thigh != other.fl_thigh:
            return False
        if self.fl_calf != other.fl_calf:
            return False
        if self.fr_hip != other.fr_hip:
            return False
        if self.fr_thigh != other.fr_thigh:
            return False
        if self.fr_calf != other.fr_calf:
            return False
        if self.rl_hip != other.rl_hip:
            return False
        if self.rl_thigh != other.rl_thigh:
            return False
        if self.rl_calf != other.rl_calf:
            return False
        if self.rr_hip != other.rr_hip:
            return False
        if self.rr_thigh != other.rr_thigh:
            return False
        if self.rr_calf != other.rr_calf:
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
    def fl_hip(self):
        """Message field 'fl_hip'."""
        return self._fl_hip

    @fl_hip.setter
    def fl_hip(self, value):
        if __debug__:
            from interfaces.msg import MotorCommand
            assert \
                isinstance(value, MotorCommand), \
                "The 'fl_hip' field must be a sub message of type 'MotorCommand'"
        self._fl_hip = value

    @builtins.property
    def fl_thigh(self):
        """Message field 'fl_thigh'."""
        return self._fl_thigh

    @fl_thigh.setter
    def fl_thigh(self, value):
        if __debug__:
            from interfaces.msg import MotorCommand
            assert \
                isinstance(value, MotorCommand), \
                "The 'fl_thigh' field must be a sub message of type 'MotorCommand'"
        self._fl_thigh = value

    @builtins.property
    def fl_calf(self):
        """Message field 'fl_calf'."""
        return self._fl_calf

    @fl_calf.setter
    def fl_calf(self, value):
        if __debug__:
            from interfaces.msg import MotorCommand
            assert \
                isinstance(value, MotorCommand), \
                "The 'fl_calf' field must be a sub message of type 'MotorCommand'"
        self._fl_calf = value

    @builtins.property
    def fr_hip(self):
        """Message field 'fr_hip'."""
        return self._fr_hip

    @fr_hip.setter
    def fr_hip(self, value):
        if __debug__:
            from interfaces.msg import MotorCommand
            assert \
                isinstance(value, MotorCommand), \
                "The 'fr_hip' field must be a sub message of type 'MotorCommand'"
        self._fr_hip = value

    @builtins.property
    def fr_thigh(self):
        """Message field 'fr_thigh'."""
        return self._fr_thigh

    @fr_thigh.setter
    def fr_thigh(self, value):
        if __debug__:
            from interfaces.msg import MotorCommand
            assert \
                isinstance(value, MotorCommand), \
                "The 'fr_thigh' field must be a sub message of type 'MotorCommand'"
        self._fr_thigh = value

    @builtins.property
    def fr_calf(self):
        """Message field 'fr_calf'."""
        return self._fr_calf

    @fr_calf.setter
    def fr_calf(self, value):
        if __debug__:
            from interfaces.msg import MotorCommand
            assert \
                isinstance(value, MotorCommand), \
                "The 'fr_calf' field must be a sub message of type 'MotorCommand'"
        self._fr_calf = value

    @builtins.property
    def rl_hip(self):
        """Message field 'rl_hip'."""
        return self._rl_hip

    @rl_hip.setter
    def rl_hip(self, value):
        if __debug__:
            from interfaces.msg import MotorCommand
            assert \
                isinstance(value, MotorCommand), \
                "The 'rl_hip' field must be a sub message of type 'MotorCommand'"
        self._rl_hip = value

    @builtins.property
    def rl_thigh(self):
        """Message field 'rl_thigh'."""
        return self._rl_thigh

    @rl_thigh.setter
    def rl_thigh(self, value):
        if __debug__:
            from interfaces.msg import MotorCommand
            assert \
                isinstance(value, MotorCommand), \
                "The 'rl_thigh' field must be a sub message of type 'MotorCommand'"
        self._rl_thigh = value

    @builtins.property
    def rl_calf(self):
        """Message field 'rl_calf'."""
        return self._rl_calf

    @rl_calf.setter
    def rl_calf(self, value):
        if __debug__:
            from interfaces.msg import MotorCommand
            assert \
                isinstance(value, MotorCommand), \
                "The 'rl_calf' field must be a sub message of type 'MotorCommand'"
        self._rl_calf = value

    @builtins.property
    def rr_hip(self):
        """Message field 'rr_hip'."""
        return self._rr_hip

    @rr_hip.setter
    def rr_hip(self, value):
        if __debug__:
            from interfaces.msg import MotorCommand
            assert \
                isinstance(value, MotorCommand), \
                "The 'rr_hip' field must be a sub message of type 'MotorCommand'"
        self._rr_hip = value

    @builtins.property
    def rr_thigh(self):
        """Message field 'rr_thigh'."""
        return self._rr_thigh

    @rr_thigh.setter
    def rr_thigh(self, value):
        if __debug__:
            from interfaces.msg import MotorCommand
            assert \
                isinstance(value, MotorCommand), \
                "The 'rr_thigh' field must be a sub message of type 'MotorCommand'"
        self._rr_thigh = value

    @builtins.property
    def rr_calf(self):
        """Message field 'rr_calf'."""
        return self._rr_calf

    @rr_calf.setter
    def rr_calf(self, value):
        if __debug__:
            from interfaces.msg import MotorCommand
            assert \
                isinstance(value, MotorCommand), \
                "The 'rr_calf' field must be a sub message of type 'MotorCommand'"
        self._rr_calf = value
