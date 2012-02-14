fbUrl='https://graph.facebook.com/'
MAX_ATTEMPS=3
TIMEOUT=10
import urllib2
def getGraph(request, aToken):
    if aToken is None:
        raise (ValueError, "aToken can't be None")
    
    if hasattr(request, "facebook"):
        return request.facebook
    
    agent=urllib2.build_opener()
    agent.addheaders =[('User-agent', 'TLA Albumizer')]
    
    url=fbUrl+"me/?access_token="+aToken
    attempts=MAX_ATTEMPS
    response=None
    while attempts:
        response_stream=None
        try:
            response_stream=agent.open(url, timeout=TIMEOUT)
            response=response_stream.read().decode('utf8')
            
            break
        except (urllib2.HTTPError,), e:
            #check for http status codes
            if 'http error' in str(e).lower():
                raise
            else:
                attempts-=1
                if attempts<=0:
                    raise
        finally:
            if response_stream:
                response_stream.close()
    request.facebook=response
    return response