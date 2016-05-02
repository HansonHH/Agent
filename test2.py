from request import *

headers = {'Content-Type': 'application/json'}
post_data = {"neighbors":"123"}

res =  POST_request_to_cloud('http://10.0.1.30:18090', headers, json.dumps(post_data))


print res
print res.status_code
