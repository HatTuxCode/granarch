"""Execute migrated aliases, Lua bindings and the btop launch chain in isolation."""
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


def deploy(home):
    subprocess.run(['python', str(ROOT / 'scripts/apply-home.py'), '--home', str(home)],
                   check=True, capture_output=True)


class ShortcutTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which('fish') and shutil.which('eza'), 'requires fish and eza')
    def test_lt_and_lta_list_trees_and_only_lta_includes_hidden_files(self):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            deploy(home)
            work = home / 'work'
            work.mkdir()
            (work / '.hidden-file').touch()
            (work / 'visible-file').touch()
            (work / 'folder').mkdir()
            (work / 'folder/child').touch()
            env = dict(os.environ, HOME=str(home), XDG_CONFIG_HOME=str(home / '.config'),
                       XDG_DATA_HOME=str(home / '.local/share'), XDG_CACHE_HOME=str(home / '.cache'),
                       NO_COLOR='1')
            alias = home / '.config/fish/conf.d/gran-aliases.fish'
            for command in ('lt', 'lta'):
                result = subprocess.run(['fish', '--no-config', '-c', 'source $argv[1]; ' + command + ' .', str(alias)],
                                        cwd=work, env=env, capture_output=True, text=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn('visible-file', result.stdout)
                self.assertIn('child', result.stdout)
                self.assertEqual('.hidden-file' in result.stdout, command == 'lta')

    @unittest.skipUnless(shutil.which('lua'), 'requires Lua')
    def test_loaded_bindings_select_btop_codex_terminal_and_keep_super_w_free(self):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            deploy(home)
            harness = home / 'bindings-test.lua'
            harness.write_text(r'''
local runtime = os.getenv("HOME") .. "/.local/share/gran"
package.path = runtime .. "/?.lua;" .. package.path
package.loaded["default.hypr.paths"] = { gran_path = runtime }
package.loaded["default.hypr.keyboard"] = { jis = function() return false end }
local function node()
  return setmetatable({}, {
    __index = function(t, key) local value = node(); rawset(t, key, value); return value end,
    __call = function() return {} end
  })
end
hl = node()
local bindings, rules = {}, {}
hl.dsp.exec_cmd = function(command) return { command = command } end
hl.bind = function(keys, dispatcher) bindings[keys] = dispatcher end
hl.unbind = function(keys) bindings[keys] = nil end
hl.window_rule = function(rule) table.insert(rules, rule) end
hl.get_monitors = function() return {} end
hl.get_active_monitor = function() return nil end
dofile(runtime .. "/default/hypr/helpers.lua")
o.workspaces = node()
dofile(runtime .. "/default/hypr/qconsole.lua")
dofile(runtime .. "/default/hypr/bindings/applications.lua")
dofile(runtime .. "/default/hypr/bindings/tiling.lua")
for _, name in ipairs({ "media", "clipboard", "input-method", "jis", "utilities", "dictation" }) do
  dofile(runtime .. "/default/hypr/bindings/" .. name .. ".lua")
end
dofile(os.getenv("HOME") .. "/.config/hypr/bindings.lua")
assert(bindings["CTRL + SUPER + ALT + T"].command == "gran-launch-tui 'btop'")
assert(bindings["SUPER + SHIFT + T"].command == "gran-launch-terminal")
assert(bindings["SUPER + ALT + RETURN"].command == "gran-launch-or-focus-tui 'codex'")
assert(bindings["CTRL + SUPER + RETURN"].command == "gran-launch-or-focus-tui 'tuios'")
assert(bindings["SUPER + W"] == nil)
assert(bindings["SUPER + Q"] ~= nil)
assert(type(bindings["SUPER + S"]) == "function")
local spawned
hl.get_workspace_windows = function() return {} end
hl.exec_cmd = function(command, options) spawned = { command, options.workspace } end
bindings["SUPER + S"]()
assert(spawned[1] == "gran-agent" and spawned[2] == "special:qconsole")
dofile(runtime .. "/default/hypr/apps/system.lua")
local floats, centers, sizes, tags = false, false, false, false
for _, rule in ipairs(rules) do
  if rule.match.tag == "floating-window" then
    floats = floats or rule.float == true
    centers = centers or rule.center == true
    sizes = sizes or (rule.size and rule.size[1] == 875 and rule.size[2] == 600)
  end
  if rule.match.class and rule.match.class:find("org.gran.btop", 1, true) and rule.tag == "+floating-window" then tags = true end
end
assert(floats and centers and sizes and tags)
print("btop: shortcut + terminal launcher + centered floating rule OK")
''')
            # No optional plugin execution is needed to exercise these bindings.
            optional = home / '.config/gran/plugins/io.github.mtolhuys.fathom/hypr/fathom.lua'
            optional.unlink(missing_ok=True)
            result = subprocess.run(['lua', str(harness)], env=dict(os.environ, HOME=str(home)),
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_btop_launch_uses_default_terminal_and_expected_window_class(self):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            deploy(home)
            commands = home / 'commands'
            commands.mkdir()
            (commands / 'setsid').write_text('#!/bin/bash\nexec "$@"\n')
            (commands / 'uwsm-app').write_text('#!/bin/bash\n[[ $1 != -- ]] || shift\nexec "$@"\n')
            (commands / 'xdg-terminal-exec').write_text('''#!/bin/bash
[[ $1 == --app-id=org.gran.btop && $2 == -e && $3 == btop ]] || exit 9
printf '%s\\n' "$1" >> "$TEST_LOG"
shift 2
exec "$@"
''')
            (commands / 'btop').write_text('#!/bin/bash\nprintf "btop opened\\n" >> "$TEST_LOG"\n')
            for path in commands.iterdir():
                path.chmod(0o755)
            log = home / 'launch.log'
            env = dict(os.environ, HOME=str(home), TEST_LOG=str(log),
                       PATH=str(commands) + ':' + str(home / '.local/share/gran/bin') + ':' + os.environ['PATH'])
            subprocess.run([str(home / '.local/share/gran/bin/gran-launch-tui'), 'btop'], env=env, check=True)
            self.assertEqual(log.read_text().splitlines(), ['--app-id=org.gran.btop', 'btop opened'])
            self.assertEqual((home / '.config/xdg-terminals.list').read_text(), 'kitty.desktop\n')
            self.assertIn('color_theme = "current"', (home / '.config/btop/btop.conf').read_text())
            self.assertTrue((home / '.config/btop/themes/current.theme').is_file())

    def test_upgrade_backs_up_shortcuts_and_does_not_change_monitors_or_accounts(self):
        spec = importlib.util.spec_from_file_location('shortcut_upgrade', ROOT / 'scripts/apply-shortcuts.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory)
            deploy(home)
            bindings = home / '.config/hypr/bindings.lua'
            bindings.write_text('-- previous shortcuts\n')
            monitor = home / '.config/hypr/monitors.lua'
            monitor.write_text('-- personal monitor\n')
            config = home / '.config/opencode/opencode.json'
            config.parent.mkdir()
            config.write_text('personal account settings')
            backup = module.apply(home)
            self.assertEqual((backup / '.config/hypr/bindings.lua').read_text(), '-- previous shortcuts\n')
            self.assertIn('CTRL + SUPER + ALT + T', bindings.read_text())
            self.assertNotIn('/home/hattux', bindings.read_text())
            self.assertNotIn('@@GRAN_HOME@@', bindings.read_text())
            self.assertEqual(monitor.read_text(), '-- personal monitor\n')
            self.assertEqual(config.read_text(), 'personal account settings')
            self.assertIsNone(module.apply(home))
