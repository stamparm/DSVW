Damn Small Vulnerable Web
=========

**Damn Small Vulnerable Web** (DSVW) is a deliberately vulnerable web application written in under 100 lines of code, written for education purposes. It supports majority of (most popular) web application vulnerabilities together with appropriate attacks.

![DSVW](http://i.imgur.com/W3Ske9B.png)

Quick start
----
```
$ python dsvw.py 
Damn Small Vulnerable Web (DSVW) < 100 LoC (Lines of Code) #v0.1b
 by: Miroslav Stampar (@stamparm)

[i] running HTTP server at '0.0.0.0:65412'...
```

Requirements
----

Python (**2.6.x** or **2.7.x**) is required for running this program. Items *XML External Entity (file)* and *Blind XPath Injection (boolean)* require installation of `python-lxml` (e.g. `apt-get install python-lxml`). Otherwise, those will be disabled.
