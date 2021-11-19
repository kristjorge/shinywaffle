from setuptools import setup


setup(
    name='shiny-waffle',
    version="1.0",
    description="Python backtesting engine",
    author="Kristian Jørgensen",
    packages=[
        'shinywaffle/backtesting/stock',
        'shinywaffle/backtesting/workflow',
        'shinywaffle/backtesting',
        'shinywaffle/common',
        'shinywaffle/common/event',
        'shinywaffle/data',
        'shinywaffle/data/yahoo_finance',
        'shinywaffle/risk',
        'shinywaffle/strategy',
        'shinywaffle/technical_indicators',
        'shinywaffle/tools',
        'shinywaffle/utils'
    ],
    install_requires = ['numpy', 'pandas', 'setuptools']
)