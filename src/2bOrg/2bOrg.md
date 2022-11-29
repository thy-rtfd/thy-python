# 2021

## Kerberos Module

The basic flow of a typical Kerberos authentication is as follows:

- Client sends an unauthenticated request to the server
- Server sends back a 401 response with a `WWW-Authenticate: Negotiate` header with no authentication details
- Client sends a new request with an `Authorization: Negotiate` header
- Server checks the `Authorization` header against the Kerberos infrastructure and either allows or denies access accordingly. If access is allowed, it should include a `WWW-Authenticate: Negotiate` header with authentication details in the reply.
- Client checks the authentication details in the reply to ensure that the request came from the server

My Sample Python code using kerberos module (You can use [requests-kerberos](https://github.com/requests/requests-kerberos) too):
```python
import requests
import kerberos
import dns.resolver

from requests.compat import urlparse

def myrequests_request(method, url, client_principal=None, **kwargs):
    req = requests.request(method, url, **kwargs)
    if "Negotiate" in req.headers.get("www-authenticate", ""):
        hostname = urlparse(req.url).hostname
        canonical_name = dns.resolver.Resolver().query(hostname).canonical_name
        ret_code, context = kerberos.authGSSClientInit(f"HTTP@{canonical_name}", principal=client_principal)
        kerberos.authGSSClientStep(context, "")
        kwargs["headers"] = {**kwargs.get("headers", {}), 
                             **{"Authorization": f"Negotiate {kerberos.authGSSClientResponse(context)}"}}
        req = requests.request(method, req.url, **kwargs)
    return req

myrequests_get = lambda url, **kwargs: myrequests_request('GET', url, **kwargs)
myrequests_post = lambda url, **kwargs: myrequests_request('POST', url, **kwargs)

req = myrequests_get("http://your.server.com/")
```
Before running above script, you need to obtain and cache Kerberos ticket-granting tickets (using kinit)

How to create keytab file and run kinit with it
```shell
kutil -v -k your.keytab.kt add -p User@your.domain -V 0 -e arcfour-hmac-md5
kinit -kt your.keytab.kt User@your.domain
```

References:
- [Using the Python Kerberos Module](http://python-notes.curiousefficiency.org/en/latest/python_kerberos.html)
- [requests-kerberos](https://github.com/requests/requests-kerberos)  
- [rfc4559: SPNEGO-based Kerberos and NTLM HTTP Authentication in Microsoft Windows](https://tools.ietf.org/html/rfc4559)
- [apple/ccs-pykerberos/pysrc/kerberos.py](https://raw.githubusercontent.com/apple/ccs-pykerberos/master/pysrc/kerberos.py)
- <https://web.mit.edu/kerberos/>
- <https://kb.iu.edu/d/aumh>

## Late Binding Closures

forked from <https://docs.python-guide.org/writing/gotchas/#late-binding-closures>

Another common source of confusion is the way Python binds its variables in closures (or in the surrounding global scope).

**What You Wrote**
```python
def create_multipliers():
    return [lambda x : i * x for i in range(5)]
```

**What You Might Have Expected to Happen**
```python
for multiplier in create_multipliers():
    print(multiplier(2))
```

A list containing five functions that each have their own closed-over i variable that multiplies their argument, producing:

```python
0
2
4
6
8
```

**What Actually Happens**
```python
8
8
8
8
8
```

Five functions are created; instead all of them just multiply x by 4.

Python’s closures are late binding. This means that the values of variables used in closures are looked up at the time the inner function is called.

Here, whenever any of the returned functions are called, the value of i is looked up in the surrounding scope at call time. By then, the loop has completed and i is left with its final value of 4.

What’s particularly nasty about this gotcha is the seemingly prevalent misinformation that this has something to do with lambdas in Python. Functions created with a lambda expression are in no way special, and in fact the same exact behavior is exhibited by just using an ordinary def:

```python
def create_multipliers():
    multipliers = []

    for i in range(5):
        def multiplier(x):
            return i * x
        multipliers.append  (multiplier)

    return multipliers
```

**What You Should Do Instead**

The most general solution is arguably a bit of a hack. Due to Python’s aforementioned behavior concerning evaluating default arguments to functions (see Mutable Default Arguments), you can create a closure that binds immediately to its arguments by using a default arg like so:

```python
def create_multipliers():
    return [lambda x, i=i : i * x for i in range(5)]
```

Alternatively, you can use the functools.partial function:

```python
from functools import partial
from operator import mul

def create_multipliers():
    return [partial(mul, i) for i in range(5)]
```

**When the Gotcha Isn’t a Gotcha**

Sometimes you want your closures to behave this way. Late binding is good in lots of situations. Looping to create unique functions is unfortunately a case where they can cause hiccups.


## Mutable Default Arguments
forked from <https://docs.python-guide.org/writing/gotchas/#mutable-default-arguments>

Seemingly the most common surprise new Python programmers encounter is Python’s treatment of mutable default arguments in function definitions.

**What You Wrote**
```python
def append_to(element, to=[]):
    to.append(element)
    return to
```

**What You Might Have Expected to Happen**

```python
my_list = append_to(12)
print(my_list)

my_other_list = append_to(42)
print(my_other_list)
```

A new list is created each time the function is called if a second argument isn’t provided, so that the output is:

```python
[12]
[42]
```

**What Actually Happens**
```python
[12]
[12, 42]
```

A new list is created once when the function is defined, and the same list is used in each successive call.

Python’s default arguments are evaluated once when the function is defined, not each time the function is called (like it is in say, Ruby). This means that if you use a mutable default argument and mutate it, you will and have mutated that object for all future calls to the function as well.

**What You Should Do Instead**

Create a new object each time the function is called, by using a default arg to signal that no argument was provided (None is often a good choice).

```python
def append_to(element, to=None):
    if to is None:
        to = []
    to.append(element)
    return to
```

Do not forget, you are passing a list object as the second argument.

**When the Gotcha Isn’t a Gotcha**

Sometimes you can specifically “exploit” (read: use as intended) this behavior to maintain state between calls of a function. This is often done when writing a caching function.
