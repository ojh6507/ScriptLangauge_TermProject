# from distutils.core import setup

# setup(name='Stock_SL',
#       version='1.0',
#       packages=['Stock_SL.Main', 'Stock_SL.BB_main', 'Stock_SL.bollinger_bands','Stock_SL.mock_Stock'
#                 ,'Stock_SL.MockMain','Stock_SL.Portfolio','Stock_SL.server','Stock_SL.stock_search','Stock_SL.telegramStock'],
#       author='ojeonghun',
#       author_email='ojh65065@tukorea.ac.kr',
#       description='stock func'
#       )
from distutils.core import setup, Extension

setup(
    name='Stock_SL',
    version='1.0',
    py_modules=['Main', 'BB_main', 'bollinger_bands', 'mock_Stock',
                'MockMain', 'Portfolio', 'server', 'stock_search', 'telegramStock'],
    ext_modules=[Extension('apikey', ['APi.cpp'])]
)
