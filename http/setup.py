#!/usr/bin/env python2.5

from distutils.core import setup

setup(	name='tarawa',
		version = '0.8',
		package_dir = {'tarawa': 'lib'},
		packages = ['tarawa', 'tarawa.header', 'tarawa.feature', 
					'tarawa.client', 'tarawa.client.adapter', 'tarawa.client.api',
					'tarawa.server', 'tarawa.server.adapter', 'tarawa.server.api',
				   ],
		provides = ['tarawa'],
		author = 'Mark Nottingham',
		author_email = 'mnot@pobox.com',
		url = 'http://tarawa.sourceforge.net/',
		description = 'HTTP APIs',
		license = 'MIT',
		classifiers = [
		  'License :: OSI Approved :: MIT License',
		  'Operating System :: OS Independent',
		  'Programming Language :: Python',
		  'Topic :: Software Development :: Libraries :: Python Modules',
		],
	)
