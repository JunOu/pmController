from distutils.core import setup
import py2exe

options = {"py2exe": {"packages": ['wx.lib.pubsub'],'dist_dir': "../dist"},
           'build': {'build_base': '../build'}}
           
setup(windows=[{'script': 'pmController.py',
                "icon_resources": [(1, "icon_controller.ico")]
                }],options=options)

