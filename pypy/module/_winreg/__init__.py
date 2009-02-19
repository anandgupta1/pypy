from pypy.interpreter.mixedmodule import MixedModule
from pypy.module._winreg import interp_winreg
from pypy.rlib.rwinreg import constants

class Module(MixedModule):
    """This module provides access to the Windows registry API.

Functions:

CloseKey() - Closes a registry key.
ConnectRegistry() - Establishes a connection to a predefined registry handle
                    on another computer.
CreateKey() - Creates the specified key, or opens it if it already exists.
DeleteKey() - Deletes the specified key.
DeleteValue() - Removes a named value from the specified registry key.
EnumKey() - Enumerates subkeys of the specified open registry key.
EnumValue() - Enumerates values of the specified open registry key.
ExpandEnvironmentStrings() - Expand the env strings in a REG_EXPAND_SZ string.
FlushKey() - Writes all the attributes of the specified key to the registry.
LoadKey() - Creates a subkey under HKEY_USER or HKEY_LOCAL_MACHINE and stores
            registration information from a specified file into that subkey.
OpenKey() - Alias for <om win32api.RegOpenKeyEx>
OpenKeyEx() - Opens the specified key.
QueryValue() - Retrieves the value associated with the unnamed value for a
               specified key in the registry.
QueryValueEx() - Retrieves the type and data for a specified value name
                 associated with an open registry key.
QueryInfoKey() - Returns information about the specified key.
SaveKey() - Saves the specified key, and all its subkeys a file.
SetValue() - Associates a value with a specified key.
SetValueEx() - Stores data in the value field of an open registry key.

Special objects:

HKEYType -- type object for HKEY objects
error -- exception raised for Win32 errors

Integer constants:
Many constants are defined - see the documentation for each function
to see what constants are used, and where."""

    appleveldefs = {
    }
    interpleveldefs = {
        'HKEYType': 'interp_winreg.W_HKEY',
        'SetValue': 'interp_winreg.SetValue',
        'SetValueEx': 'interp_winreg.SetValueEx',
        'QueryValue': 'interp_winreg.QueryValue',
        'QueryValueEx' : 'interp_winreg.QueryValueEx',
        'CreateKey': 'interp_winreg.CreateKey',
        'DeleteKey'   : 'interp_winreg.DeleteKey',
        'DeleteValue' : 'interp_winreg.DeleteValue',
        'OpenKey'     : 'interp_winreg.OpenKey',
        'OpenKeyEx'   : 'interp_winreg.OpenKey',
        'EnumValue'   : 'interp_winreg.EnumValue',
        'EnumKey'     : 'interp_winreg.EnumKey',
        'CloseKey': 'interp_winreg.CloseKey',
        'QueryInfoKey': 'interp_winreg.QueryInfoKey',
        'ConnectRegistry': 'interp_winreg.ConnectRegistry',
    }

    for name, value in constants.iteritems():
        interpleveldefs[name] = "space.wrap(%s)" % (value,)
