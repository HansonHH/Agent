#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2016 Xin Han <hxinhan@gmail.com>
#
# Distributed under terms of the MIT license.

#import oslo_cache
#from dogpile.cache import make_region
#foo = memcached_get("foo:" . foo_id)

import memcache

mc = memcache.Client(['127.0.0.1:11211'], debug=0)

#mc.set("key1", "123456", time=20)
value = mc.get("key1")
print value



