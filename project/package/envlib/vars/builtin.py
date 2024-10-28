import os.path
import typing

from .. import var

import jl95terceira.batteries as batt

class EditorTypeNotValid(Exception): pass
def _editor(o) -> typing.Callable[[str],str]:

    if isinstance(o, str): return _editor(lambda file_path: f'{o} {file_path}')
    if callable  (o): 

        try: 
            
            r = o('test/file/path')
            if not isinstance(r, str): raise EditorTypeNotValid(o)

        except: raise EditorTypeNotValid(o)
        return o

EDITOR           = var(name       ='editor',
                       description='default text file editor',
                       type       =_editor,
                       default   =_editor('notepad'))
GIT_HOME         = var(name       ='git.home', 
                       description='the home of Git')
GIT              = var(name       ='git', 
                       description='the path to Git (\'git.exe\')',
                       default    =os.path.join(GIT_HOME.get(), 'bin', 'git') if GIT_HOME.check() else 'git')
GIT_REMOTE       = var(name       ='git.remote', 
                       description='the alias of git remote that is commonly used (usually \'origin\')',
                       default    ='origin')
CURL             = var(name       ='curl', 
                       description='the path / alias to Curl executable',
                       default    ='curl')
JDK_HOMES        = var(name       ='jdk.homes', 
                       description='a map (dict) of Java homes by version (as a string)')
MAVEN_HOME       = var(name       ='maven.home', 
                       description='the home of Apache Maven')
MAVEN            = var(name       ='maven', 
                       description='the path / alias to Apache Maven executable',
                       default    = os.path.join(MAVEN_HOME.get(), 'bin', 'mvn.exe') if MAVEN_HOME.check() else 'mvn')
ANT_HOME         = var(name       ='ant.home', 
                       description='the home of Apache Ant')
ANT              = var(name       ='ant', 
                       description='the path / alias to Apache Ant executable',
                       default    = os.path.join(ANT_HOME.get(), 'bin', 'mvn.exe') if ANT_HOME.check() else 'ant')
AZURE_DEVOPS_PAT = var(name       ='azure.devops.pat', 
                       description='personal access token for Azure DevOps (artifact download permission etc)')
OPENSSL_HOME     = var(name       ='openssl.home', 
                       default    ='the home of OpenSSL')
TEMP             = var(name       ='temp', 
                       description='a directory that may be used to hold temporary files',
                       default    =batt.os.TEMP_DIR)
