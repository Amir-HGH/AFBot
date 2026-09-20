import pymysql as pml

# Database Class 

class Database : 

    # build connection & cursor

    def __init__(self,host,user,password,port,database):

        self.connection = pml.connect(
            host = host , 
            user = user ,
            password = password ,
            port = port ,
            database = database
        )
        self.cursor = self.connection.cursor()

    # for shutdown
    
    def close(self) : 

        self.cursor.close()
        self.connection.close()

