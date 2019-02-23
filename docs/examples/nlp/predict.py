"""

"""

from mindsdb import *

# Here we use the model to make predictions (NOTE: You need to run train.py first)
result = MindsDB().predict(
    predict='number_of_rooms',
    model_name='real_estate_desc',
    when={
        "description": """A true gem
 rooms: 2
  bathrooms: 0
  neighboorhood: thowsand_oaks
   amenities: parking
  area: 84.0291068642868
  condition: great !
        """
    }
)

# you can now print the results
print('The predicted number of rooms')
print(result.predicted_values)
