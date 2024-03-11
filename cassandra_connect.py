from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider

def connect():
    cloud_config= {
            'secure_connect_bundle': 'D:\internship project\secure-connect-internship.zip'
    }
    auth_provider = PlainTextAuthProvider('jlvonLZdCSCDaZbAjzrMFktc', 'dvKl,62rxL,Hb,h+nXjw.+A.,0vK.o2B7ahmA.tPOzfUM_WnY+J08XRq.-vx6PcmJD3ojhFacxXnio+4sSFH1f9Hcbnfx0.X-R4Q+daM_M7ZeJjjH6a+0zj7J14WZ6f8')
    cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
    session = cluster.connect()
    return session

    # row = session.execute("select release_version from system.local").one()
    # if row:
    #     print(row[0])
    # else:
    #     print("An error occurred.")