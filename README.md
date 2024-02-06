# patch_antenna_calculator

Written by Oskar von Heideken, 2024

Python script that contains math to calculate an inset fed patch antenna

# DISCLAIMER
This script should by no means be used as a single source of truth
when designing an inset feed patch antenna. This is just a collection
of equations found on the internet.

# Usage
Run the script with python 2.7 or 3 (3 has not been tested, proceed at your own risk):

<pre>python patch_antenna_calculator.py</pre>

And the script should spit out the dimensions for a two layer square patch antenna with a inset
feed line. 

(NOT TESTED) It should be possible to import the classes used in this project 
into another python script, should you choose to. In which case, include the two
classes `substrate` and `patch_antenna`, initialize the 
substrate parameters with height, copper thickness and dielectric 
constant and the antenna object with substrate and frequency: `antenna = patch_antenna(s, frequency)`. 

Calculate the antenna parameters with `antenna.calculate_antenna_params()`
which return a dictionary with the antenna parameter, or print the
parameters after with `antenna.print_antenna_params()`.

```python
from patch_antenna_calculator import substrate, patch_antenna

# init the substrate
s = substrate(
    e_r=4.6, 
    height_mm=1.6, 
    cu_thickness_um=35,
)

# Calculate the antenna parameters
antenna = patch_antenna(
    substrate = s, 
    frequency_hz = 2.45E6)
# Run the calculation
params = antenna.calculate_antenna_params()

# Print the params
antenna.print_antenna_params()
```