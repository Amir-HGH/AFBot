import pymysql as pml
from dbutils.pooled_db import PooledDB
import logging


logger = logging.getLogger(__name__)


# Database Class 

class Database : 

    # build Pool __________________________________

    def __init__(self,host,user,password,port,database):

        try : 

            self.Pool = PooledDB(
                creator=pml,
                maxconnections=10,
                mincached=2,
                maxcached=5,
                blocking=True,
                host=host,
                user=user,
                password=password,
                port=port,
                database=database,
                charset="utf8mb4",
                autocommit=False
            )

        except Exception :

            logger.exception("init")
            raise 


    # get & give connection to pool __________________________________

    def get_connection (self) : 

        connection = None

        try:

            connection = self.Pool.connection()

            if connection is None :
                
                logger.error("get connection : connection is none")
                return False

            cursor = connection.cursor()
            
            if cursor is None:

                logger.error("get connection : cursor is none")
                connection.close()
                return False

            return connection, cursor

        except Exception:

            logger.exception("get connection")
            
            if connection is not None:
                
                try:  connection.close()

                except Exception : 

                    logger.exception("get connection : cant release the connection")
                    return False

            return False


    def give_connection (self,connection,cursor) :

        if connection is None or cursor is  None : 
            
            logger.error("give connection : connection or cursor are none")
            return False 

        try : 

            cursor.close()
            connection.close()
            return True

        except Exception : 

            logger.exception("give connection")
            
            if connection is not None : 
                
                try : connection.close()

                except Exception : 
                    
                    logger.exception("give connection : cant release the connection")
                    return False 

            return False


    # get & give for tables __________________________________

    def give_data(self, table, fields: list, values: list):

        cc = self.get_connection()
        if cc is False : return False
        connection,cursor = cc
        
        fields = ", ".join(fields)
        placeholders = ", ".join(["%s"] * len(values))

        query = f"""
        INSERT INTO {table} ({fields})
        VALUES ({placeholders})
        """

        try :
            
            cursor.execute(query, values)
            connection.commit()

        except Exception : 

            logger.exception("give data")

            try : connection.rollback()

            except Exception : 
                
                logger.exception("give data : cant rollback ")
                return False

            return False

        finally :
            finish = self.give_connection(connection,cursor)

        if not finish : return False

        return True


    def get_data(self, table, fields: list):

        cc = self.get_connection()
        if cc is False : return False
        connection,cursor = cc
        
        fields = ", ".join(fields)

        query = f"""
        SELECT {fields}
        FROM {table}
        """

        data = False

        try :
            
            cursor.execute(query)
            data = cursor.fetchall()
        
        except Exception :
            
            logger.exception("get data")
            return False

        finally :
            finish = self.give_connection(connection,cursor)

        if not finish : return False

        if not data : 

            logger.warning("get data : data is none")
            return False
        
        return data

    
    def get_data_c(
            self,
            table,
            fields: list,
            conditions:list,
            condition_values:list,
            order_by:str=None,
            limit=None):
        
        if len(conditions) != len(condition_values):
            
            logger.error("get data c : conditions are not math to condition values")
            return False

        cc = self.get_connection()
        if cc == False : return False
        connection,cursor = cc
        
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

        if order_by : 
            query += f" ORDER BY {order_by} "

        if limit : 
            query += f" limit {limit} "

        data = False

        try :
            
            cursor.execute(query,values_2)
            data = cursor.fetchall()
        
        except Exception :
            
            logger.exception("get data c")
            return False

        finally :
            finish = self.give_connection(connection,cursor)

        if not finish : return False

        if not data : 

            logger.warning("get data c : data is none")
            return False
        
        return data


    def give_data_c(self, table, fileds: list,conditions:list,condition_values:list,values:list):
        
        if len(conditions) != len(condition_values):
            
            logger.error("give data c : conditions are not match to condition values")
            return False

        cc = self.get_connection()
        if cc == False : return False
        connection,cursor = cc
        
        fileds = (", ".join(
            f"{f} = %s" for f in fileds
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
            
            cursor.execute(query, values + values_2)
            connection.commit()

        except Exception : 

            logger.exception("give data c")

            try : connection.rollback()

            except Exception : 
                
                logger.exception("give data c : cant rollback")
                return False

            return False

        finally :
            finish = self.give_connection(connection,cursor)

        if not finish : return False
        return True


    # Special methods for conversation manager __________________________________


    # Specialized method for getting user's private message for summarizer

    def get_before_user_messages (self,user_name:str,conversation_id:int,limit:int):

        if limit < 1 : 

            logger.error("get before user messages : limit is small")
            return False

        cc = self.get_connection()
        if cc == False : return False
        connection,cursor = cc
        
        query = """
            SELECT role, message_id, message
            FROM messages
            WHERE username = %s
            AND user_conversation_id = %s
            AND id >= (
                SELECT id
                FROM messages
                WHERE username = %s
                    AND user_conversation_id = %s
                    AND role = 'user'
                ORDER BY message_id DESC
                LIMIT 1 OFFSET %s
            )
            ORDER BY id ASC;
        """

        data = False

        try :
            
            cursor.execute(query,(user_name,conversation_id,user_name,conversation_id,limit - 1))
            data = cursor.fetchall()
        
        except Exception :
            
            logger.exception("get before user messages")
            return False

        finally :
            finish = self.give_connection(connection,cursor)

        if not finish : return False

        if not data : 

            logger.warning("get before user messages : data is none")
            return False
        
        return data


    # special method for check exist 

    def exist (self, table, fields: list,conditions:list,condition_values:list):

        if len(conditions) != len(condition_values):
            
            logger.error("exist : conditions are not match to condition values")
            return {"error":"error"}

        cc = self.get_connection()
        if cc == False : return False
        connection,cursor = cc
        
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

        data = False

        try :
            
            cursor.execute(query,values_2)
            data = cursor.fetchall()
        
        except Exception :
            
            logger.exception("exist")
            return {"error":"error"}

        finally :
            finish = self.give_connection(connection,cursor)

        if not finish : return False

        if not data : 

            logger.warning("exist : data is none")
            return False
        
        return True


    # get data c  for conversation manager

    def get_data_c_cm(self, table, fields: list,conditions:list,condition_values:list):

        if len(conditions) != len(condition_values):
            
            logger.error("get data c cm : conditions are not match to condition values")
            return False

        cc = self.get_connection()
        if cc == False : return False
        connection,cursor = cc
        
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

        data = False

        try :
            
            cursor.execute(query,values_2)
            data = cursor.fetchall()
        
        except Exception :
            
            logger.exception("get data c cm")
            return "error"

        finally :
            finish = self.give_connection(connection,cursor)

        if not finish : return False

        if not data : 

            logger.warning("get data c cm : data is none")
            return False
        
        return data
    

    # super special method for save user message in conversation manager

    def save_message(self,username,conversation_id,message:str) :

        cc = self.get_connection()
        if cc == False : return False
        connection,cursor = cc

        result = False

        try : 

            query = """
                SELECT last_user_message_id
                FROM conversations
                WHERE username = %s
                AND user_conversation_id = %s
                FOR UPDATE
            """

            cursor.execute(query,(username,conversation_id))
            message_id = cursor.fetchone()

            if message_id : 

                message_id = message_id[0] + 1

                query = """
                    INSERT INTO messages (
                        username,
                        user_conversation_id,
                        role,
                        message_id,
                        message
                    )
                    VALUES (%s, %s, %s, %s, %s)
                """

                cursor.execute(
                    query,
                    (
                        username,
                        conversation_id,
                        "user",
                        message_id,
                        message
                    )
                )

                query = """
                    UPDATE conversations
                    SET last_user_message_id = %s
                    WHERE username = %s
                    AND user_conversation_id = %s
                """

                cursor.execute(query,(message_id, username, conversation_id))

                connection.commit()
                result = message_id

            else : 
                
                logger.error("save message : problem with message id")
                connection.rollback()

        except Exception : 

            logger.exception("save message")

            try : connection.rollback()

            except Exception : 
                
                logger.exception("save message : cant rollback")
                result = False

        finally : finish = self.give_connection(connection,cursor)

        if not finish : return False

        return result

    # special method for cm 

    def get_recent_messages(
        self,
        username: str,
        conversation_id: int,
        limit: int = 20
    ):

        cc = self.get_connection()
        if cc is False:return False

        connection, cursor = cc

        query = """
            SELECT id, role, message
            FROM (
                SELECT id, role, message
                FROM messages
                WHERE username = %s
                AND user_conversation_id = %s
                ORDER BY id DESC
                LIMIT %s
            ) AS recent_messages
            ORDER BY id ASC
        """

        data = False

        try:
            cursor.execute(query,(username, conversation_id, limit))
            data = cursor.fetchall()

        except Exception:
            
            logger.exception("get recent messages")
            return False

        finally:
            finish = self.give_connection(connection, cursor)

        if not finish : return False

        if not data : 

            logger.warning("get recent messages : data is none")
            return False
        
        return data


    # Special method for DB Tools

    def get_interaction (self,username,interaction) : 

        cc = self.get_connection()
        if cc is False:return False

        connection, cursor = cc

        query = """
            SELECT movie_id FROM interactions
            WHERE username = %s AND interaction = %s 
        """

        data = False

        try :
            
            cursor.execute(query,(username,interaction))
            data = cursor.fetchall()
        
        except Exception :
            
            logger.exception("get interaction")
            return False

        finally :
            finish = self.give_connection(connection,cursor)

        if not finish : return False

        if not data : return []
        
        return data


    # for shutdown __________________________________
    
    def close(self) : 
        
        try : self.Pool.close()

        except Exception : 

            logger.exception("close")
            raise


# build object __________________________________
    
Database_app = Database(
    host = "localhost" , 
    user = "python_user" , 
    password = "@iA@q3"  ,
    port = 3306 ,
    database = "afilm_bot"
)

