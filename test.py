import beanstalkc

EMAIL_QUEUE = "eta_queue"

if __name__=="__main__":
  bs = beanstalkc.Connection()
  bs.use(EMAIL_QUEUE)

#  bs.put('camp101988@yahoo.com')
#  bs.put('tabara.mihai@gmail.com')
#  bs.put('dia_tiriplica@yahoo.co.uk')
  bs.put('andrei.soare@gmail.com')

