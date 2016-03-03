#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2016 Xin Han <hxinhan@gmail.com>
#


# GET request to cloud
def GET_request_to_cloud(url, headers):
    res = requests.get(url, headers = headers)
    return res.text

# DELETE request to cloud
def DELETE_request_to_cloud(url, headers):
    res = requests.delete(url, headers = headers)
    res.headers['Content-Length'] = str(len(str(res)))
    dic = {'status_code':res.status_code, 'headers':str(res.headers), 'text':res.text}
