import hashlib, importlib.util, json, os, subprocess, sys, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);result=importlib.util.module_from_spec(spec);spec.loader.exec_module(result);return result
apply=module('apply',ROOT/'scripts/apply-home.py')
folders=module('folders',ROOT/'payload/home/.local/share/gran/lib/breeze_folders.py')
apps=module('apps',ROOT/'payload/home/.local/share/gran/lib/upstream-apps.py')
class InstallerTests(unittest.TestCase):
    def test_existing_files_recoverable_and_overrides_archived(self):
        with tempfile.TemporaryDirectory() as directory:
            home=Path(directory);config=home/'.config/hypr/hyprland.lua';config.parent.mkdir(parents=True);config.write_text('old configuration')
            override=home/'.local/state/noctalia/settings.toml';override.parent.mkdir(parents=True);override.write_text('[shell]\nfont_family="old"\n')
            backup=apply.apply(home)
            self.assertEqual((backup/'.config/hypr/hyprland.lua').read_text(),'old configuration')
            self.assertTrue((backup/'.local/state/noctalia/settings.toml').exists());self.assertFalse(override.exists())
            self.assertNotIn('@HOME@',config.read_text());self.assertIn(str(home)+'/Work',config.read_text())
            self.assertIn('SUPER + ALT + O',config.read_text())
            self.assertIn('SUPER + SHIFT + D',config.read_text())
            first=config.read_bytes();apply.apply(home);self.assertEqual(first,config.read_bytes())
    def test_no_personal_font_sizes_or_universal_font_overrides(self):
        import tomllib
        payload=ROOT/'payload/home'
        config=tomllib.loads((payload/'.config/noctalia/config.toml').read_text())
        self.assertEqual(config['shell']['font_family'],'sans-serif')
        self.assertAlmostEqual(config['accessibility']['ui_scale']*14,11)
        self.assertFalse((payload/'.config/fontconfig').exists())
        for relative in ('.config/gtk-3.0/settings.ini','.config/gtk-4.0/settings.ini','.config/qt6ct/qt6ct.conf','.config/kitty/kitty.conf','.config/gran/scripts/sync-dolphin-zen.py','.local/share/gran/bin/gran-theme-sync','.local/share/gran/lib/dolphin_theme.py'):
            self.assertNotIn('9.9', (payload/relative).read_text(), relative)
        self.assertNotIn('font-size:',(payload/'.config/gran/scripts/sync-dolphin-zen.py').read_text())
    def test_live_setup_does_not_wait_for_services_in_its_own_transaction(self):
        setup=(ROOT/'iso/live/usr/local/bin/granarch-live-setup').read_text()
        # Starting another service synchronously inside a boot oneshot can wait
        # for the same boot transaction that is waiting for this oneshot.
        self.assertNotRegex(setup, r'(?m)^systemctl start(?! --no-block)')
        unit=(ROOT/'iso/live/etc/systemd/system/granarch-live.service').read_text()
        wants=next(line for line in unit.splitlines() if line.startswith('Wants='))
        self.assertIn('sddm.service',wants)
        self.assertIn('Before=sddm.service',unit)
    def test_archiso_preserves_session_and_command_execution_permissions(self):
        permissions=module('permissions',ROOT/'scripts/export-iso-permissions.py')
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);command=root/'opt/granarch/payload/home/.local/share/gran/bin/gran-session'
            command.parent.mkdir(parents=True);command.write_text('#!/bin/bash\n');command.chmod(0o755)
            ordinary=command.with_name('config');ordinary.write_text('data');ordinary.chmod(0o644)
            profile=root/'profiledef.sh';profile.write_text('declare -A file_permissions=()\n'+permissions.export(root))
            result=subprocess.run(['bash','-c','source "$1"; printf "%s" "${file_permissions[/opt/granarch/payload/home/.local/share/gran/bin/gran-session]}"', 'bash',str(profile)],capture_output=True,text=True,check=True)
            self.assertEqual(result.stdout,'0:0:755')
            self.assertNotIn('/config',permissions.export(root))
    def test_calamares_branding_has_required_assets(self):
        import yaml
        folder=ROOT/'iso/calamares/branding/granarch'
        config=yaml.safe_load((folder/'branding.desc').read_text())
        self.assertTrue((folder/config['slideshow']).is_file())
        for role in ('productIcon','productLogo','productWelcome'):
            self.assertTrue((folder/config['images'][role]).is_file(),role)
        self.assertEqual(config['uploadServer']['type'],'none')
        for role in ('SidebarBackground','SidebarText','SidebarTextCurrent','SidebarBackgroundCurrent'):
            self.assertIn(role,config['style'])
    def test_installer_fits_small_scaled_displays(self):
        scaling=module('calamares_scale',ROOT/'iso/live/usr/local/libexec/granarch-calamares-scale.py')
        monitor={'width':1280,'height':800,'scale':1.25,'focused':True,'reserved':[0,29,0,0]}
        factor=scaling.factor([monitor])
        self.assertLessEqual(1000*factor,1280/1.25-32)
        self.assertLessEqual(720*factor,800/1.25-29-32)
        self.assertEqual(scaling.factor([{'width':2560,'height':1440,'scale':1.25}]),1)
    def test_version_checks_accept_actual_upstream_output(self):
        versions=module('versions',ROOT/'scripts/check-versions.py')
        self.assertEqual(versions.version_from_output('noctalia','noctalia v5.4.1\n'),(5,4,1))
        self.assertEqual(versions.version_from_output('Hyprland','Hyprland 0.57.1 built from branch v0.57.1'),(0,57,1))
        self.assertEqual(versions.version_from_output('noctalia','library 9.8.7\nnoctalia v5.4.0\n'),(5,4,0))
        self.assertLess(versions.version_from_output('noctalia','noctalia v5.3.0'),versions.MINIMUMS['noctalia'])
        self.assertIsNone(versions.version_from_output('noctalia','unrelated library 5.4.1'))
    def test_symlink_cannot_redirect_profile(self):
        with tempfile.TemporaryDirectory() as directory,tempfile.TemporaryDirectory() as outside:
            home=Path(directory);(home/'.config').symlink_to(outside,target_is_directory=True)
            with self.assertRaises(ValueError):apply.apply(home)
            self.assertEqual(list(Path(outside).iterdir()),[])
    def test_breeze_geometry_preserved_and_accent_replaced(self):
        with tempfile.TemporaryDirectory() as directory:
            home=Path(directory);source=home/'source';folder=source/'places/64';folder.mkdir(parents=True)
            svg='<svg xmlns="http://www.w3.org/2000/svg"><path class="ColorScheme-Accent" style="fill:currentColor;opacity:0.6" d="M 4 6 L 4 11 z"/></svg>'
            (folder/'folder.svg').write_text(svg)
            self.assertEqual(folders.build(home,source),'GranBreezeNord')
            result=(home/'.local/share/icons/GranBreezeNord/places/64/folder.svg').read_text()
            self.assertIn('M 4 6 L 4 11 z',result);self.assertIn('fill:#8fa89b',result);self.assertIn('opacity:0.6',result)
            self.assertIn('Inherits=breeze,hicolor',(home/'.local/share/icons/GranBreezeNord/index.theme').read_text())
    def test_checksum_failure_refuses_installation(self):
        from unittest.mock import patch
        import io
        with tempfile.TemporaryDirectory() as directory,patch.object(apps,'urlopen',return_value=io.BytesIO(b'tampered')):
            with self.assertRaisesRegex(ValueError,'SHA-256'):
                apps.download({'url':'https://github.com/example/release','sha256':'0'*64},Path(directory)/'asset')
    def test_installer_refuses_fedora_before_mutation(self):
        import platform
        if 'ID=fedora' not in Path('/etc/os-release').read_text():self.skipTest('Guard test uses Fedora host')
        result=subprocess.run(['bash',str(ROOT/'install.sh'),'--install'],capture_output=True,text=True)
        self.assertNotEqual(result.returncode,0)
        self.assertTrue('Arch Linux puro' in result.stderr or 'usuário comum' in result.stderr)
    def test_native_validators_in_isolated_home(self):
        import shutil
        if not shutil.which('Hyprland') or not shutil.which('noctalia'):self.skipTest('Native validators unavailable')
        with tempfile.TemporaryDirectory() as directory:
            home=Path(directory);apply.apply(home);env=os.environ.copy();env['HOME']=str(home)
            for command in [['noctalia','config','validate',str(home/'.config/noctalia/config.toml')],['Hyprland','--verify-config','--config',str(home/'.config/hypr/hyprland.lua')]]:
                result=subprocess.run(command,env=env,capture_output=True,text=True,timeout=30)
                self.assertEqual(result.returncode,0,result.stdout+result.stderr)
if __name__=='__main__':unittest.main()
