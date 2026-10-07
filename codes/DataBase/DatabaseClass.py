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

    # get & give for tables 

    def give_data(self, table, fields: list, values: list):

        fields = ", ".join(fields)
        placeholders = ", ".join(["%s"] * len(values))

        query = f"""
        INSERT INTO {table} ({fields})
        VALUES ({placeholders})
        """

        try :
            
            self.cursor.execute(query, values)
            self.connection.commit()

        except : 
            return False

        else :
            return True


    def get_data(self, table, fields: list):

        fields = ", ".join(fields)

        query = f"""
        SELECT {fields}
        FROM {table}
        """

        try :
            self.cursor.execute(query)
        
        except :
            return False

        else : 

            data = self.cursor.fetchall()

            if data : return data
            else : return False


    def get_data_c(self, table, fields: list,conditions:list,condition_values:list):

        if len(conditions) != len(condition_values):
            return False
        
        fields = ", ".join(fields)
        
        condition_2 = []
        values_2 = []

        for condition, condition_value in zip(conditions, condition_values):

            placeholders = ", ".join(["%s"] * len(condition_value))
            condition_2.append(f"{condition} IN ({placeholders})")

            values_2.extend(condition_value)

        conditions_text = " AND ".join(condition_2)

        query = f"""
        SELECT {fields}
        FROM {table} WHERE {conditions_text} 
        """

        try :
            self.cursor.execute(query,values_2)
        
        except :
            return False

        else : 

            data = self.cursor.fetchall()

            if data : return data
            else : return False


    def give_data_c(self, table, fields: list,conditions:list,condition_values:list,values:list):

        if len(conditions) != len(condition_values):
            return False
        
        fileds = (", ".join(
            f"{f} = %s" for f in fields
        ))

        condition_2 = []
        values_2 = []

        for condition, condition_value in zip(conditions, condition_values):

            placeholders = ", ".join(["%s"] * len(condition_value))
            condition_2.append(f"{condition} IN ({placeholders})")

            values_2.extend(condition_value)

        conditions_text = " AND ".join(condition_2)

        query = f"""
        UPDATE {table}
        SET {fileds}
        WHERE {conditions_text}
        """
        
        try : 
            
            self.cursor.execute(query,values + values_2)
            self.connection.commit()

        except :
            return False

        else :
            return True
    

    # for shutdown
    
    def close(self) : 

        self.cursor.close()
        self.connection.close()

