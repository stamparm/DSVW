Damn Small Vulnerable Web
=========

**Damn Small Vulnerable Web** (DSVW) is a deliberately vulnerable web application written in under 100 lines of code, created for educational purposes. It supports majority of (most popular) web application vulnerabilities together with appropriate attacks.

![DSVW XSS](http://i.imgur.com/0wUbCR7.png)

Quick start
----

Run the following command:
```
$ python dsvw.py 
Damn Small Vulnerable Web (DSVW) < 100 LoC (Lines of Code) #v0.1d
 by: Miroslav Stampar (@stamparm)

[i] running HTTP server at '127.0.0.1:65412'...
```

and navigate your browser to http://127.0.0.1:65412/:

![DSVW](http://i.imgur.com/W3Ske9B.png)

Requirements
----

Python (**2.6.x** or **2.7.x**) is required for running this program. Items *XML External Entity (file)* and *Blind XPath Injection (boolean)* require installation of `python-lxml` (e.g. `apt-get install python-lxml`). Otherwise, those will be disabled.
