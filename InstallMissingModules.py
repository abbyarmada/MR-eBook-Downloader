"""
Installs possible missing modules
"""
import os


print('== INSTALL REQUIRED PACKAGES ==')

os.system('pip install urllib3[secure]')
os.system('pip install HTMLParser')
