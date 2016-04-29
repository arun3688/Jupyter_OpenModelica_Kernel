from ipykernel.kernelbase import Kernel
from OMPython import OMCSession
import re
import numpy
from numpy import array
import sys
import os
import re
import shutil
import site

def plotgraph(plotvar,divid,omc,resultfile):
  if (resultfile!=None):
     checkdygraph=os.path.join(os.getcwd(),'dygraph-combined.js')
     if not os.path.exists(checkdygraph):
         if (sys.platform=='win32'):
             try:
               sitepath=site.getsitepackages()[1]
               dygraphfile=os.path.join(sitepath,'openmodelica_kernel','dygraph-combined.js').replace('\\','/')
               shutil.copy2(dygraphfile,os.getcwd())
               #print 'copied file'
             except Exception as e:
               print e
         else:
             try:
               sitepath=site.getsitepackages()[0]
               dygraphfile=os.path.join(sitepath,'openmodelica_kernel','dygraph-combined.js').replace('\\','/')
               shutil.copy2(dygraphfile,os.getcwd())
               #print 'copied file'
             except Exception as e:
               print e               
     try:
       divheader=" ".join(['<div id='+str(divid)+'>','</div>'])
       readResult = omc.sendExpression("readSimulationResult(\"" + resultfile + "\",{time," + plotvar + "})")
       omc.sendExpression("closeSimulationResultFile()")
       plotlabels=['Time']
       exp='(\s?,\s?)(?=[^\[]*\])|(\s?,\s?)(?=[^\(]*\))'
       #print 'inside_plot1'
       subexp=re.sub(exp,'$#',plotvar)
       plotvalsplit=subexp.split(',')
       #print plotvalsplit
       for z in xrange(len(plotvalsplit)):
           val= plotvalsplit[z].replace('$#',',')
           plotlabels.append(val)
       #print plotlabels  
       plotlabel1=[x.encode('UTF8') for x in plotlabels]
       
       plots=[]
       for i in xrange(len(readResult)):   
         x=readResult[i]
         d=[]
         for z in xrange(len(x)):
            tu=x[z]
            d.append((tu,))
         plots.append(d)            
       n=numpy.array(plots)
       numpy.set_printoptions(threshold='nan')
       dygraph_array= repr(numpy.hstack(n)).replace('array',' ').replace('(' ,' ').replace(')' ,' ')
       dygraphoptions=" ".join(['{', 'legend:"always",','labels:',str(plotlabel1),'}'])
       data="".join(['<script type="text/javascript"> g = new Dygraph(document.getElementById('+'"'+str(divid)+'"'+'),',str(dygraph_array),',',dygraphoptions,')','</script>']) 
       htmlhead='''<html> <head> <script src="dygraph-combined.js"> </script> </head>'''
       divcontent="\n".join([htmlhead,divheader,str(data)])
     except:
       error=omc.sendExpression("getErrorString()")
       divcontent="".join(['<p>',error,'</p>'])
      
  else:
     divcontent="".join(['<p>','No result File Generated','</p>'])
  
  return divcontent   

class OpenModelicaKernel(Kernel):
    implementation = 'openmodelica_kernel'
    implementation_version = '1.0'
    language = 'openmodelica'
    language_version = '1.0'
    language_info = {
        'name': "openmodelica",
        'version': "1.0",
        'mimetype': 'text/modelica',
    }
    banner = "openmodelicakernel - for evaluating modelica codes in jupyter notebook"
    
    def __init__(self, **kwargs):
       Kernel.__init__(self, **kwargs)
       self.omc=OMCSession()
       self.matfile=None
       
    def do_execute(self, code, silent, store_history=True, user_expressions=None,
                   allow_stdin=True):
        #print code
        
        z1 = filter(lambda x: not re.match(r'^\s*$', x), code)
        plotcommand=z1.replace(' ','').startswith('plot(')and z1.replace(' ','').endswith(')')
 
        #print self.execution_count
        
        if (plotcommand==True):   
          l1=z1.replace(' ','')
          l=l1[0:-1]
          plotvar=l[5:].replace('{','').replace('}','')
          plotdivid=str(self.execution_count)
          finaldata=plotgraph(plotvar,plotdivid,self.omc,self.matfile)
          
          if not silent: 
                '''        
                stream_content = {'name': 'stdout','text':ouptut}
                self.send_response(self.iopub_socket, 'stream', stream_content) '''                           
                display_content = {'source': 'kernel',
                    'data': { 'text/html': finaldata
                    }
                }
                self.send_response(self.iopub_socket, 'display_data', display_content)
        else:
                try:
                   val=self.omc.sendExpression(code)
                   try:
                      self.matfile=val['resultFile']
                   except:
                      pass

                except:
                   val="failed"
               
                #print self.matfile
                if not silent: 
                    display_content = {'source': 'kernel',
                        'data': { 'text/plain': str(val)
                        }
                    }
                    self.send_response(self.iopub_socket, 'display_data', display_content)
           
        return {'status': 'ok',
                # The base class increments the execution count
                'execution_count': self.execution_count,
                'payload': [],
                'user_expressions': {},
               }
'''
if __name__ == '__main__':
    try:
       from ipykernel.kernelapp import IPKernelApp
    except ImportError:
       from IPython.kernel.zmq.kernelapp import IPKernelApp
    
    IPKernelApp.launch_instance(kernel_class=OpenModelicaKernel)'''

