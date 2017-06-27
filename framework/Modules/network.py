from BuiltInService import requests

class networking(object):
    """docstring for object_converter"""

    def sendRequest(url, values, requestType, requestObjType, responseObjType):
        """ Get Value from company's API
                Keyword arguments:
                url --  API link
                requestType -- post/get
                requestObjType -- xml/json
                responseObjType -- xml/json
                return -- xml/json
        """

        # set what your server accepts
        headers = {'Content-Type', 'text/html'}
        if requestObjType == "xml":
            headers = {'Content-Type': 'application/xml'}
        elif requestObjType == "json":
            headers = {'Content-Type': 'application/json'}
        elif requestObjType == "pdf":
            headers = {'Content-Type': 'application/pdf'}

        # decide request
        if requestType == "post":
            resp = requests.post(url, data=values, headers=headers).text
        elif requestType == "get":
            resp = requests.get(url,headers=headers)
        elif requestType=="postcontent":
            headers = {'Content-Type': 'text/xml'}
            resp = requests.post(url,data=values,headers=headers)
        return resp

    def sendRequestHeaderConfig(url,values,requestType,headersConfig):
        if requestType == "post":
            resp = requests.post(url, data=values, headers=headersConfig).text
        elif requestType == "get":
            resp = requests.get(url,headers=headersConfig)
        return resp


    # more networking functions can be implemted here...