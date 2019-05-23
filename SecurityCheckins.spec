# -*- mode: python -*-

block_cipher = None


a = Analysis(['SecurityCheckins.pyw'],
             pathex=['C:\\Users\\Steve Stanley\\Documents\\Computing\\My_Scripts\\Security Checkin'],
             binaries=[],
             datas=[],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
a.datas += [('Info-icon.png', 'Info-icon.png', 'DATA'), ('CheckinIcon.ico', 'CheckinIcon.ico', 'DATA')]
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='SecurityCheckins',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False,
	  icon='CheckinIcon.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='SecurityCheckins')
