from datetime import datetime
from appAlgo_local import Algo
algo = Algo()

#algo.dbWrite_user('localUsr', 'localPass', '$2b$12$LtKoeotNPtfLPEoNhBsDE.')

now = datetime.now()
ret = algo.point_process('localUsr', 0, 40.443251, -79.959034, .0012, now, 15)

if(ret):
    print('true')
else:
    print('false')