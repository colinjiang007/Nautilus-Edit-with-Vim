# File: nautilus-edit-with-vim.py
#
# This file is part of Nautilus-Edit-with-Vim.

# Nautilus-Edit-with-Vim is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.

# Nautilus-Edit-with-Vim is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
# Public License for more details.

# You should have received a copy of the GNU General Public License along with
# Nautilus-Edit-with-Vim.  If not, see <http://www.gnu.org/licenses/>.

import os
from gi.repository import Nautilus, GObject
import ConfigParser


class NautilusEditWithVimExtension(GObject.GObject, Nautilus.MenuProvider):

    def __init__(self):
        self.__read_conf_file()

    # read config file and set values
    def __read_conf_file(self):

        home_dir = os.getenv('HOME', '/');

        conf_file = None

        # search config files and set conf_file to the file path
        for a_file in [
                home_dir + '/.nautilus-edit-with-vim.conf',
                home_dir + '/.nautilus/nautilus-edit-with-vim.conf',
                '/etc/nautilus-edit-with-vim.conf']:
            if os.path.isfile(a_file) and os.access(a_file, os.R_OK):
                conf_file = a_file
                break

        # read the config file
        cf = ConfigParser.ConfigParser(False)

        # set default values
        cf.add_section('cmds')
        cf.set('cmds', 'gvim', 'gvim')
        cf.set('cmds', 'gvimdiff', 'gvim -d')
        cf.set('cmds', 'gvimremote', 'gvim --remote')
        cf.set('cmds', 'auth', 'gksu -k,beesu -m -c,kdesu -c')
        cf.add_section('prefs')
        # by default we don't fold menu items when right click on a single
        # file, but fold when right click on several files
        cf.set('prefs', 'fold_single', '0')
        cf.set('prefs', 'fold_multi', '1')

        # if we have found a config file, then load it
        if conf_file != None:
            cf.read(conf_file)

        self.gvim_cmd = cf.get('cmds', 'gvim')
        self.gvimdiff_cmd = cf.get('cmds', 'gvimdiff')
        self.gvimremote_cmd = cf.get('cmds', 'gvimremote')
        self.auth_cmds = [cmd.strip()
                for cmd in cf.get('cmds', 'auth').split(',')]
        self.pref_fold_single = cf.getboolean('prefs', 'fold_single')
        self.pref_fold_multi = cf.getboolean('prefs', 'fold_multi')

    def __execute_as_root(self, cmd):
        # execute commands as root

        for auth_cmd in self.auth_cmds:
            try:
                os.system(auth_cmd + ' ' + cmd)
            except:
                continue
            else:
                return 0
        
        return 1

    #edit with single gvim
    def menu_activate_cb_single(self, menu, files):
        cmd_string = self.gvim_cmd
        for afile in files:
            cmd_string += " '" + afile.get_location().get_path() + "'"

        os.system(cmd_string)

    # edit with single gvim, root privilege
    def menu_activate_cb_single_root(self, menu, files):
        cmd_string = self.gvim_cmd
        for afile in files:
            cmd_string += " '" + afile.get_location().get_path() + "'"

        self.__execute_as_root(cmd_string)

    #edit with existing gvim
    def menu_activate_cb_existing(self, menu, files):
        cmd_string = self.gvimremote_cmd
        for afile in files:
            cmd_string += " '" + afile.get_location().get_path() + "'"

        os.system(cmd_string)

    # edit with mutli gvim
    def menu_activate_cb_multi(self, menu, files):
        for afile in files:
            os.system(self.gvim_cmd + " '" +
                    afile.get_location().get_path() + "'")

    # diff with gvim
    def menu_activate_cb_diff(self, menu, files):
        cmd_string = self.gvimdiff_cmd
        for afile in files:
            cmd_string += " '" + afile.get_location().get_path() + "'"
        
        os.system(cmd_string)

    def get_file_items(self, window, files):
        items = []

        if len(files) == 1:
            new_item = Nautilus.MenuItem(
                name = 'NautilusEditWithVim::nautilus_edit_with_vim_file_item',
                label = 'Edit with gVim',
                tip = 'Edit with gVim Editor')
            new_item.connect('activate', self.menu_activate_cb_single, files)
            items.append(new_item)

            new_item = Nautilus.MenuItem(
                name = 'NautilusEditWithVim::nautilus_edit_with_existing_vim_file_item',
                label = 'Edit with existing gVim',
                tip = 'Edit with existing gVim Editor')
            new_item.connect('activate', self.menu_activate_cb_existing, files)
            items.append(new_item)

            new_item = Nautilus.MenuItem(
                name = 'NautilusEditWithVim::nautilus_edit_with_vim_file_item_root',
                label = 'Edit with gVim as root',
                tip = 'Edit with gVim Editor as root')
            new_item.connect('activate', self.menu_activate_cb_single_root,
                    files)
            items.append(new_item)

        elif len(files) > 1:
            new_item = Nautilus.MenuItem(
                name = 'NautilusEditWithVim::nautilus_edit_with_vim_single_file_item',
                label = 'Edit with a Single gVim',
                tip = 'Edit with a Single gVim Editor')
            new_item.connect('activate', self.menu_activate_cb_single, files)
            items.append(new_item)

            new_item = Nautilus.MenuItem(
                name = 'NautilusEditWithVim::nautilus_edit_with_vim_single_file_item_root',
                label = 'Edit with a Single gVim as root',
                tip = 'Edit with a Single gVim Editor as root')
            new_item.connect('activate', self.menu_activate_cb_single_root,
                    files)
            items.append(new_item)

            new_item = Nautilus.MenuItem(
                name = 'NautilusEditWithVim::nautilus_edit_with_existing_vim_single_file_item',
                label = 'Edit with an Existing gVim',
                tip = 'Edit with an Existing gVim Editor')
            new_item.connect('activate', self.menu_activate_cb_existing, files)
            items.append(new_item)

            new_item = Nautilus.MenuItem(
                name = 'NautilusEditWithVim::nautilus_edit_with_vim_multi_file_item',
                label = 'Edit with Multi gVim',
                tip = 'Edit with Mutli gVim Editors')
            new_item.connect('activate', self.menu_activate_cb_multi, files)
            items.append(new_item)

            new_item = Nautilus.MenuItem(
                name = 'NautilusEditWithVim::nautilus_edit_with_vim_diff_file_item',
                label = 'Diff with gVim',
                tip = 'Diff with gVim')
            new_item.connect('activate', self.menu_activate_cb_diff, files)
            items.append(new_item)

        # if user choose to fold and sub menu item is supported, then set sub
        # menus
        if (((len(files) == 1 and self.pref_fold_single) or
                (len(files) > 1 and self.pref_fold_multi)) and
                hasattr(Nautilus, 'Menu')):
            root_item = Nautilus.MenuItem(
                    name = 'NautilusEditWithVim::nautilus_edit_with_vim_root_item',
                    label = 'NautilusEditWithVim',
                    tip = 'Nautilus extension for Vim')

            sub_menu = Nautilus.Menu()
            root_item.set_submenu(sub_menu)
            for item in items:
                sub_menu.append_item(item)

            return [root_item]
        else:
            return items

# vim703: cc=78
# vim: et tw=78 sw=4 ts=4
