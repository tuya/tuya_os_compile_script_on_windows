#!/usr/bin/env python
# coding=utf-8
"""MounRiver (custom-flow) backend for the TuyaOS ide_tool.

This is the "custom IDE" backend described in .ide_tool/docs/07: every step is
delegated to scripts shipped by the vendor package, so the plugin itself stays
chip independent.  A vendor package must provide, under
``vendor/<vendor>/toolchain/templates/mrs/``:

    build.py        compile + link, called as  build.py <self_src.json>
    create_lib.py   build one static library, called as
                    create_lib.py -I<dir>... <source.c>... <output.a>
    gen_src_json.py optional before-build helper
    gen_project.py  optional MounRiver project generator (no arguments)
    self_src.json   optional known-good manifest (unioned with the runtime one)

and, in ``vendor.json``::

    "tool": {
      "mrs": {
        "toolchain": { "bin_path": ".../templates/mrs" },
        "cmd": {
          "before-build": [ "...gen_src_json.py" ],
          "build":        [ "...build.py" ],
          "after-build":  [],
          "create_lib":   [ "...create_lib.py" ]
        },
        "output": { ... },
        "flash":  { "bin_path": "", "flash_user_cmd": "", "flash_all_cmd": "" }
      }
    }

Any RISC-V / GCC based vendor that satisfies this contract can reuse this file
unchanged; only the vendor side scripts have to be implemented.
"""

import os
import sys

from my_ide.my_ide_base import my_ide_base

current_file_dir = os.path.dirname(__file__)  # 当前文件所在的目录
sys.path.append(current_file_dir + '/../components')
from my_file.my_file import *
from my_exe.my_exe import my_exe_simple, my_exe_get_install_path


class my_ide_mrs(my_ide_base):
    ide_kind = 'mrs'

    def tmake(self):
        # Base: clean .log, copy project.json and resolve the variable map.
        my_ide_base.tmake(self)

        # The MounRiver project files live in the vendor package, so the
        # generator is looked up through output.vendor (the vendor name).
        vendor = self.output.get('vendor')
        if not vendor:
            return
        generator = os.path.join(os.getcwd(), 'vendor', vendor,
                                 'toolchain', 'templates', 'mrs', 'gen_project.py')
        if not os.path.isfile(generator):
            print('  [skip] no MounRiver project generator for vendor "%s"' % vendor)
            return
        print('\n> generate MounRiver project')
        my_exe_simple('"%s" "%s"' % (sys.executable, generator), 1, os.getcwd(), self.var_map)

    def tbuild(self):
        print('\nBUILD')
        evn = my_file_get_abs_path_and_formart(self.cmd['bin_path'])
        print('> [evn path]:', evn)
        log_path = self.var_map['$OUTPUT']

        # before build
        for cmd in self.cmd['before-build']:
            my_exe_simple(cmd, 1, evn, self.var_map)
            print("\n[o-before-build] %s" % (cmd))

        # build
        for cmd in self.cmd['build']:
            self_src_json = log_path + '/self_src.json'
            cmd = f"{cmd} {self_src_json}"
            my_file_save_json(self_src_json, self.src)
            my_exe_simple(cmd, 1, evn, self.var_map)
            print("\n[o-build] %s" % (cmd))

        # after build
        for cmd in self.cmd['after-build']:
            print("\n[o-after-build] %s" % (cmd))
            my_exe_simple(cmd, 1, evn, self.var_map)

        my_ide_base.tbuild(self)

    def _tlib(self, libs_path, incs_path, comp_path, log_path):
        """Package the components listed in sdkconfig.json sdk.libs.

        Contract for create_lib.py: the arguments are the include paths
        (``-I...``), the source files and finally the output archive, so a
        vendor implementation can forward them to gcc + ar.
        """
        print('#3. create libs ...')
        evn = my_file_get_abs_path_and_formart(self.cmd['bin_path'])
        libs = self.output['sdk']['libs']
        for k, v in self.output['sdk']['components'].items():
            if k in libs:
                print('    ->[Y]', k)
                cur_lib = os.path.join(libs_path, 'lib' + k + '.a')
                c_files = ' '.join(v.get('c_files', []))
                all_incs = list(self.src.get('h_dirs', [])) + list(v.get('h_dir', []))
                incs = ' '.join(['-I' + h for h in all_incs])
                for cmd in self.cmd['create_lib']:
                    full = '%s %s %s %s' % (cmd, incs, c_files, cur_lib)
                    my_exe_simple(full, 1, evn, self.var_map)
                    print('\n[o-create-lib] %s' % full)
                my_file_copy_one_kind_files_to(v.get('h_dir', []), '.h',
                                               os.path.join(incs_path, 'components', k, 'include'))
            else:
                print('    ->[N]', k)
                my_file_copy_files_to(v.get('c_files', []), os.path.join(comp_path, k, 'src'))
                my_file_copy_one_kind_files_to(v.get('h_dir', []), '.h',
                                               os.path.join(comp_path, k, 'include'))

    def tflash(self, OP):
        """Flash with the commands from vendor.json; otherwise print a hint."""
        key = 'flash_user_cmd' if OP == 'flash_user' else 'flash_all_cmd'
        cmd = self.flash.get(key, '') if self.flash else ''
        if cmd:
            my_ide_base.tflash(self, OP)
            return
        print('\n[flash] "%s" is empty for this vendor.' % key)
        print('        Flash .log/output/wch58x_ble_merge.bin with WCHISPStudio /')
        print('        MounRiver, or declare tool.mrs.flash.%s in vendor.json' % key)
