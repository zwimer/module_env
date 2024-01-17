# ModuleEnv

Context manage-able module-environments for python!
Have you ever needed multiple verions a python module installed?
Wanted to temprarily pollute `sys.path` or `import` some module but were afraid of polluting the global environment?

Worry no more! `ModuleEnv` is like a runtime virtualenv for python modules!
The best part, it's just a context manager, `with ModuleEnv()` is all you need!

### Install
```bash
pip install module_env
```

# Usage

This module exposes three classes:
1. `ModuleEnv`
1. `InverseModuleEnv`
1. `UsageError`

#### ModuleEnv

This is the main class is `ModuleEnv`.
This class provides a context manager for a module environment.

_Construction_: Upon construction, a `ModuleEnv` will save a copy of the current environment as its own.
That is, the env the `ModuleEnv` instance uses is initialized as a copy of the environment at time of construction
This does mean that if constructed within another `ModuleEnv`'s context, it will copy that installed context.

Generally users will want to default construct
this class, but this class does permit users to specify
which attributes within `sys` are saved and restored during module setup and teardown.
This can be done as follows:
```python
standard = ModuleEnv()
custom = ModuleEnv(sys_attrs=("meta_path", "path_hooks", "path", "path_importer_cache"))
```
These attributes are assigned and copies during setup and teardown.
`sys.modules` is automatically updated; though its underlying object remains the same.

_Context Manager_: The main use of this class is as a context manager.
Entering the context applies the environment; exiting restores the previous environment.
Module environments are not nestable!
An example usage:
```python
def multi():
    import multiprocessing

with ModuleEnv():
    multi()  # Import in a function so globals() / locals() is not affected
    assert "multiprocessing" in sys.modules  # Imported in env

assert "multiprocessing" not in sys.modules  # Not outside of env
```

`.inverse()`: Module environment contexts can temporarily be escaped
without exiting a context manager via a child `InverseModuleEnv`.
In this case, entering the context of a new `ModuleEnv` is permissible.
For example:
```python
def multi():
    import multiprocessing

with ModuleEnv() as env:
    with env.inverse():  # Restore global env
        multi()
    assert "multiprocessing" not in sys.modules  # Not imported in env

assert "multiprocessing" in sys.modules  # Imported global env
```

`__getitem__`: While modules imports a properly preserved by a `ModuleEnv`, it does not affect the variables in
your scope; that is `globals()` and `locals()` remain unchanged.
For this reason, it is recommended not to execute much code directly
within a `with ModuleEnv()` but rather wrapped by a function.
That way, after exiting the env, any 'no longer imported' modules are not still reference-able via scoped variables.
Along these lines, entering an environment does not set up `globals()` nor `locals()` with your import modules.
One way to handle this is to just call `import` on the module again, since the module itself is already imported,
this should just be a variable assignment.
`ModuleEnv`s expose a `__getitem__` function which is functionally just `__import__` for the given environment;
this function is only usable when the environment is active.
This is just syntactic sugar that might allow explicitness about which environment ought to be active
at the time of the call, verifying this statement each use.
For example, here are three ways to import a module:
```python
with ModuleEnv() as env:
    # Three functionally identical ways of importing multiprocessing
    m1 = env["multiprocessing"]
    m2 = __import__("multiprocessing")
    import multiprocessing as m3
    assert m1 is m2 and m2 is m3
```

_Thread Saftey_: Editing `sys` attributes is inherently not thread-safe.
If using in a multithreaded environment, keep this in mind
and do not use `ModuleEnv`'s concurrently in multiple threads.

#### InverseModuleEnv
This context-manager class allows for escaping a `ModuleEnv` context without exiting the context manager.
Entering the context an `InverModuleEnv` restores the module
environment to the environment the parent `ModuleEnv` has active.
An `InverseModuleEnv` can exclusively invert the environment of the `ModuleEnv` which created it.
Entering the context of a `ModuleEnv` when in the context of an `InverseModuleEnv` is allowed, as the
`InverseModuleEnv` context between the two `ModuleEnv` functionally inverts the first,
meaning the second `ModuleEnv` context is not actually nested

Constructing an `InverseModuleEnv` can _only_ be done via a `ModuleEnv`'s `.inverse()` function.
The `ModuleEnv` responsible for creating the `InverseModuleEnv` is considered the parent.
`InverseModuleEnv`s contexts may only be entered if within the parents' environment is active.
Just like `ModuleEnv`s, `InverseModuleEnv`s expose `.__getitem__`.

`InverseModuleEnv`s themselves can be inverted via a call to `.invert()`.
This will return a child `ModuleEnv`; just like any child, this
child's context may only be entered when its parent context is active.
A key point here is that given `inv=env.invert(); env2=inv.invert()`, `env2` is a distinct object from `env`.
Both apply the same environment once entered, but `env2` is a
child of `inv` and thus may only be entered when `inv` is active.

A usage example:
```python
# Global environment
with ModuleEnv() as env:
    # 'env' environment
    with env.inverse() as inv:
        # Global environment
        with inv.inverse():  # Not the same object as 'env', but shares the same environment
            # 'env' environment
            pass
        with env:
            # 'env' environment
            pass
        with ModuleEnv() as env2:
            # 'env2' environment
            pass
```

Invalid uses examples:
```python
env = ModuleEnv()
inv = env.inverse()
# with inv:  # INVALID
#   InverseModuleEnv contexts may only be entered if the parent env is active
with env, inv:
    # 'env' environment
    with ModuleEnv() as env2:
        # with inv:  # INVALID:
            # Only env2.invert() can invert env2!
        pass
    # with env.inverse().inverse():  # INVALID
        # A new env.inverse() is a different object than inv
        # Thus env.inverse().inverse() is not inv's child
        # Only children can invert their parent!
```

#### UsageError
This exception type is raised if a user misuses a `ModuleEnv` or `InverseModuleEnv`.
For example, if a user attempts to nest one ModuleEnv within another.

### Practical Example:

Consider two directory containing different versions of a module `foo`: `foo_v1` and `foo_v2`:
```python
from module_env import ModuleEnv
import sys

v1 = ModuleEnv()
with v1:
    sys.path.append("./foo_v1")
    import foo

sys.path.append("./foo_v2")
import foo

assert foo.__version__ == "2.0"
with env:
    assert foo.__version__ == "1.0"
```

# Development

### Tests

Tests are available in the `./tests` directory.
From the root directory, running them is as simple as:
```bash
pip install .
cd tests
python -m unittest
```
