from typing import Optional, Union, Deque, Tuple, Dict, Any
from collections import deque
from types import ModuleType
import sys


__all__ = ("ModuleEnv", "InverseModuleEnv", "UsageError")


class UsageError(RuntimeError):
    """
    A runtime error raised when ModuleEnv detects improper usage
    """


class _Sys:
    """
    A small class which manages variables stored in sys
    """

    __slots__ = ("_attrs", "_data", "modules")

    def __init__(self, attrs: Tuple[str, ...]):
        """
        :param attrs: sys attributes, aside from sys.modules, this env should manage
        """
        self._attrs: Tuple[str, ...] = attrs
        self._data: Dict[str, Any] = {i: getattr(sys, i).copy() for i in self._attrs}
        self.modules: Dict[str, Any] = sys.modules.copy()

    def install(self) -> "_Sys":
        """
        Install the current data into sys
        :return: A _Sys constructed of the previous data stored in sys
        """
        old = _Sys(self._attrs)
        # Edit assignments
        for key, val in self._data.items():
            setattr(sys, key, val)
        # In place edits for things that cannot be assigned
        # Some things in stdlib grab the reference :(
        sys.modules.clear()
        sys.modules.update(self.modules)
        return old


class _Ref:
    """
    A container which holds one object
    Useful when sharing an assignable object
    """

    __slots__ = ("obj",)

    def __init__(self, obj: Any):
        """
        :param obj: The object to store a reference to
        """
        self.obj: Any = obj


class _ModuleEnv:
    """
    An abstract module enviornment class
    This class provides a context manager for the env it represents
    Subclasses are ModuleEnv and InverseModuleEnv
    Changing sys attributes are global, not thread unique
    Do not use _ModuleEnvs concurrently in multiple threads
    """

    __slots__ = ("_parent", "_sys")
    _active: Deque[Optional["_ModuleEnv"]] = deque([None])

    def __init__(
        self,
        *,
        sys_attrs: Tuple[str, ...] = ("meta_path", "path_hooks", "path", "path_importer_cache"),
        _parent: Optional["_ModuleEnv"] = None,
    ):
        """
        :param sys_attrs: sys attributes, aside from sys.modules, this env should manage
        :param _parent: Only for internal use; do not set this
        """
        if isinstance(self, InverseModuleEnv) and _parent is None:
            raise UsageError("Users should not construct an InverseModuleEnv directly")
        self._parent: Optional["_ModuleEnv"] = _parent
        self._sys: _Ref = _Ref(_Sys(sys_attrs)) if self._parent is None else self._parent._sys

    def inverse(self) -> Union["ModuleEnv", "InverseModuleEnv"]:
        """
        For ModuleEnv's this returns an InverseModuleEnv
        whose context manager can escape the current ModuleEnv
        For an InverseModuleEnv this returns an ModuleEnv which can re-enter the escaped context
        :return: An _ModuleEnv that undoes what the context manager of this _ModuleEnv does
        """
        return (InverseModuleEnv if isinstance(self, ModuleEnv) else ModuleEnv)(_parent=self)

    def __getitem__(self, module: str) -> ModuleType:
        """
        Get the give module for this environment
        May only be used with the current ModuleEnv is active (this is enforced)
        This should be the same as __import__(module) but is more explicit
        :param module: The name of the module
        :return: The module of the given name for this _ModuleEnv
        """
        if self is not self._active[-1]:
            raise UsageError("Do not access this when this ModuleEnv is not active")
        ret: ModuleType = self._sys.obj.modules.get(module, None)
        if ret is None:
            ret = __import__(module)
        return ret

    def __enter__(self) -> "_ModuleEnv":
        """
        Set up the new environment on enter
        :return: self
        """
        if isinstance(self, InverseModuleEnv) and self._active[-1] is not self._parent:
            raise UsageError("InverseModuleEnv must be used within an ModuleEnv's context")
        if isinstance(self, ModuleEnv) and isinstance(self._active[-1], ModuleEnv):
            raise UsageError("Nesting ModuleEnvs is not allowed")
        if self._parent is not None and self._active[-1] is not self._parent:
            raise UsageError("A child ModuleEnv must be used in its parent's context")
        self._sys.obj = self._sys.obj.install()
        self._active.append(self)
        return self

    def __exit__(self, *_) -> None:
        """
        Restore the previous environment on exit
        """
        assert self is self._active[-1], "Sanity Check: _ModuleEnv is not active"
        self._sys.obj = self._sys.obj.install()
        self._active.pop()


class ModuleEnv(_ModuleEnv):
    """
    A python module environment
    This class provides a context manager for the env it represents
    Changing sys attributes are global, not thread unique
    Do not use _ModuleEnvs concurrently in multiple threads
    """


class InverseModuleEnv(_ModuleEnv):
    """
    An environment, which when active, restores the environment the parent ModuleEnv replaced
    This class provides a context manager for the env it represents
    Changing sys attributes are global, not thread unique
    Do not use _ModuleEnvs concurrently in multiple threads
    """
