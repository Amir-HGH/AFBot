import logging


logger = logging.getLogger(__name__)


class Business_Rules : 

    def __init__(self,on,keys): 
        
        self.output_number = on
        self.keys = keys


    # Helpers method

    def normalization (self,numbers : list[int],number) :

        minnumber = min(numbers)
        maxnumber = max(numbers)

        if minnumber == maxnumber : return 0.5

        return (number-minnumber) / (maxnumber-minnumber)


    # Main task

    def business_rules (self,data : list[dict]) : 

        if not data : 

            logger.error("business rules : there is no data ")
            return False
        
        lists = []
        normal_list = []

        try : 

            for key in self.keys :

                numbers = [
                    dictionary[key] for dictionary in data
                ] 
                lists.append(numbers)

            for p_list in lists : 

                normal_data = [
                    self.normalization(p_list,number) for number in p_list
                ]
                normal_list.append(normal_data)

            zip1 = list(zip(*normal_list))
            zip2 = [
                sum(item) for item in zip1
            ]
            zip3 = list(zip(zip2,data))

            finaldict = [
                {"score" : item[0] , "movie" : item[1]} for item in zip3
            ]

            sorted_movies = sorted(
                finaldict ,
                key=lambda item : item["score"] ,
                reverse=True
            )

            top = sorted_movies[:self.output_number]

            if top : return top 
            else : 

                logger.error("business rules : there is no top ")
                return False

        except Exception : 

            logger.exception("business rules")
            return False

