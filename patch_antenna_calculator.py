# Written by Oskar von Heideken, 2024
# Script that calculates inset fed patch antenna parameters. 
# Modify the substrate parameters to suit your needs. 

# DISCLAIMER: This script should by no means be used as a single source of truth
# when designing an inset feed patch antenna. This is just a collection
# of equations found on the internet.

# Tested with python2.7, but should work with python3 as well.

from math import sqrt, exp, acos, pi


class substrate():
    """
    Small class to keep track of the substrate. 
    """
    def __init__(self, e_r, height_mm, cu_thickness_um):
        # Check parameters
        if height_mm <= 0:
            raise ValueError("substrate parameter height cannot be 0 or less")
        if cu_thickness_um <= 0:
            raise ValueError("substrate parameter cu_thickness cannot be 0 or less")
        if e_r <= 0:
            raise ValueError("substrate parameter e_r (direlectric constant) cannot be 0 or less")
        self.e_r = e_r
        self.height = float(height_mm)
        self.cu_thickness = float(cu_thickness_um)
    
    def __repr__(self):
        s = "Two layer substrate with height:"+str(self.height)+" mm, copper thickness:"+str(self.cu_thickness)+" um and e_r:"+str(self.e_r)
        return s


class patch_antenna():

    def __init__(self, substrate, frequency_hz):
        """
        Init function, doesn't do much really.
        """
        self.f = frequency_hz
        self.substrate = substrate
        self.c = 299792458 # Speed of light in vacuum, m/s
        self.w = None # Width of the patch
        self.l = None # Length of the patch
        self.feed_line_w = None # width of the 50 ohm feed line in mm
        self.feed_line_l = None # inset length of the 50 ohm feed line in mm
        self.feed_line_clearance = None # Inset feed clearance in mm

    def calculate_antenna_params(self):
        """
        Function to calculate the antenna parameters.
        The params are saved to internal class variables
        and can be printed using the print_antenna_params
        method.
        """
        # Start by calculating the width of the patch
        self.calculate_patch_width()
        
        # Given the width, we can now calculate the length:
        self.calculate_patch_length()

        # Given the substrate, we can now calculate the 50 ohm stripline feed line
        # Note, this can be contentious, so only overwrite this if the 
        # feedline width is already None
        # This gives the user the option to override this.
        if not self.feed_line_w:
            self.feed_line_w = self.calculate_feed_width(impedance = 50)

        # Calculate the inset feed position:
        self.calculate_inset_feed_length(impedance=50)

        # Calculate the inset feed clearance:
        self.calculate_inset_feed_clearance()

    def print_antenna_params(self):
        """
        Function to print the antenna calculated antenna parameters
        """
        print("Length: {} mm".format(round(self.l,2)))
        print("Width: {} mm".format(round(self.w,2)))
        print("50 ohm feed line width: {} mm".format(round(self.feed_line_w, 2)))
        print("Inset feed length: {} mm".format(round(self.feed_line_l,2)))
        print("Inset feed clearance: {} mm".format(round(self.feed_line_clearance,2)))

    def calculate_patch_width(self):
        """
        Funciton to calculate the width of the patch. 
        Based off https://www.pasternack.com/t-calculator-microstrip-ant.aspx
        """
        self.w = self.c/(2*self.f*sqrt((self.substrate.e_r + 1)/2))

    def calculate_patch_length(self):
        """
        Funciton to calculate the length of the patch. 
        Based off https://www.pasternack.com/t-calculator-microstrip-ant.aspx
        """
        # We need the effective dielectric constant for the width of the patch
        e_eff = self.calculate_epsilon_eff(self.w)
        print("e_eff: {}".format(e_eff))
        a = (e_eff+0.3)*(self.w/self.substrate.height+0.264)
        b = (e_eff-0.258)*(self.w/self.substrate.height+0.8)
        self.l = (self.c/(2*self.f*sqrt(e_eff)) - 0.824*self.substrate.height*(a/b))

    def calculate_feed_width(self, impedance):
        """
        Calculate the 50 ohm feed line. 
        This is based off https://www.everythingrf.com/rf-calculators/microstrip-width-calculator
        """
        a = 7.48*self.substrate.height
        b = exp(impedance*sqrt(self.substrate.e_r+1.41)/87)
        return a/b-1.25*self.substrate.cu_thickness/1000

    def calculate_inset_feed_length(self, impedance):
        """
        Calculate the inset feed length, or how many mm's 
        into the width-side (parallel to the length param)
        the inset feed should go. 
        Based off https://www.antenna-theory.com/antennas/patches/patch3.php
        and https://bpb-us-w2.wpmucdn.com/sites.gatech.edu/dist/6/733/files/2018/11/PatchAntennas.pdf
        """
        # First, calculate the input impedance at distance 0, from Mohammad Alhassoun's notes, eq 1.9
        za = 90*(pow(self.substrate.e_r, 2)/(self.substrate.e_r-1))*pow((self.l/self.w), 2)
        #print("patch input impedance: {} ohm".format(za))
        # zin(x) = cos2(pi*x/L)*za -> invcos(sqrt(zin/za))*L/pi = x
        self.feed_line_l = acos(sqrt(impedance/za))*self.l/pi

    def calculate_inset_feed_clearance(self):
        """
        Really simple POMA calculation, when in lack of a straight 
        answer this seems to be somewhat the rule of thumb. 
        That is, if the inset feed width is small, use that as the clearance, 
        otherwise use less, but no less than half. 
        I don't like it one bit, but it is was it is...
        """
        if self.feed_line_w < 2:
            self.feed_line_clearance = self.feed_line_w
        elif self.feed_line_w < 3:
            self.feed_line_clearance = self.feed_line_w/1.25
        elif self.feed_line_w < 4:
            self.feed_line_clearance = self.feed_line_w/1.5
        elif self.feed_line_w < 5:
            self.feed_line_clearance = self.feed_line_w/1.75


    def calculate_epsilon_eff(self, width):
        """
        Function to calculate the effective 
        dielectric constant. Based off
        https://microwaves101.com/encyclopedias/microstrip
        All parameters are given in mm
        """
        if (width <= 0) or (self.substrate.height <= 0) or (self.substrate.e_r <= 0):
            raise ValueError("Couldn't calculate epsilon_eff. Some parameters were 0! w:{}, h:{}, er:{}".format(width, self.substrate.height, self.substrate.e_r))
        if width/self.substrate.height < 1:
            e_eff = ((self.substrate.e_r+1)/2) + ((self.substrate.e_r-1)/2)*(pow((1+12*self.substrate.height/width), -0.5) + 0.04*pow((1-width/self.substrate.height),2))
        else:
            e_eff = ((self.substrate.e_r+1)/2) + ((self.substrate.e_r-1)/2)*pow((1+12*self.substrate.height/width), -0.5)
        return e_eff


def main():
    # Init the substrate. 
    # If using a different substrate, change the parameters here! 
    s = substrate(
        e_r=4.6, 
        height_mm=1.6, 
        cu_thickness_um=35,
    )
    frequency = 2.45E6 # Calculate for 2.45 GHz
    print("Using {}".format(s))

    # Calculate the antenna parameters
    antenna = patch_antenna(s, frequency)
    # OPTIONAL, BUT RECOMMENDED: overwrite the feed line width here
    # The calculator for this isn't great.. 

    # antenna.feed_line_w = <your value here> 
    params = antenna.calculate_antenna_params()
    antenna.print_antenna_params()

if __name__ == "__main__":
    main()