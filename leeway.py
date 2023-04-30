#!/usr/bin/env python
"""
Leeway
==================================
"""

from datetime import timedelta, datetime
import cmocean
import xarray as xr
from opendrift.readers import reader_netCDF_CF_generic
from opendrift.models.leeway import Leeway

lw = Leeway(loglevel=20)  # Set loglevel to 0 for debug information

# User inputs
choice = int(input(
    "To enter own data enter '1', to use pre configured input press 'Enter': ") or "0")
if choice == 0:
    prop = 1
    year = 2023
    month = 4
    day = 30
    hour = 15
    minute = 0
    second = 0
    sim_time = 7
    latitude = 68.471
    longitude = 17.422
    sim_radius = 10
    sim_objects = 100
elif choice == 1:
    print("\nWhat do you want to simulate?\n")
    prop = int(input("PIW unknown state (mean values) = 1\nPIW vertical PFD type III = 2\nPIW sitting PFD type I/II = 3\nPIW survival suit (face up) = 4\nPIW scuba suit (face up) = 5\nPIW deceased = 6\nPlease enter your input, default is '1': ") or "1")
    year = int(input("Enter year of release in YYYY-format: "))
    month = int(input("Enter month of release in MM-format: "))
    day = int(input("Enter day of release in DD-format: "))
    hour = int(input("Enter hour of release in HH-format: "))
    minute = int(
        input("Enter minute of release in MM-format, default is '00': ") or "00")
    second = int(
        input("Enter second of release in SS-format, default is '00': ") or "00")
    sim_time = int(
        input("Enter simulation time in hours, default is '48': ") or "48")
    print("\nDefault coordinates is at the middle of Håloglandsbrua.\n")
    latitude = float(input(
        "Enter latitude (N/S) of release in XX.YYY-format, default is '68.459538': ") or "68.459538")
    longitude = float(input(
        "Enter longitude (E/W) of release in XX.YYY-format, default is '17.481768': ") or "17.481768")
    sim_radius = int(
        input("Enter radius of release site in meters, default is '50': ") or "50")
    sim_objects = int(
        input("Enter number of objects to simulate, default is '1000': ") or "1000")
else:
    print("Invalid input, terminating.")
    exit()
# Atmospheric model for wind
reader_arome = reader_netCDF_CF_generic.Reader(
    'https://thredds.met.no/thredds/dodsC/sea/norkyst800m/1h/aggregate_be')

# Ocean model for current
reader_norkyst = reader_netCDF_CF_generic.Reader(
    'https://thredds.met.no/thredds/dodsC/sea/norkyst800m/1h/aggregate_be')

# %%
# Adding readers successively, and specifying which variables they
# shall provide. This way, order of adding readers does not matter
lw.add_reader(reader_norkyst, variables=[
              'x_sea_water_velocity', 'y_sea_water_velocity'])
lw.add_reader(reader_arome, variables=['x_wind', 'y_wind'])
lw.set_config('environment:fallback:x_sea_water_velocity', 0)
lw.set_config('environment:fallback:y_sea_water_velocity', 0)

# %%
# Seed leeway elements at defined position and time
object_type = prop
start_time = datetime(year, month, day, hour, minute, second)
lw.seed_elements(lon=longitude, lat=latitude, radius=sim_radius, number=sim_objects,
                 time=start_time, object_type=object_type)

# %%
# Running model
lw.run(duration=timedelta(hours=sim_time),
       time_step=900, time_step_output=3600)

# %%
# Print and plot results
print(lw)

# %%
# Animation with current as background.
# Note that drift is also depending on wind, which is not shown.
lw.animation(background=['x_sea_water_velocity', 'y_sea_water_velocity'],
             skip=5,  # show every 5th vector
             cmap=cmocean.cm.speed, vmin=0, vmax=1.0, bgalpha=.7, land_color='#666666', fast=True, filename='/home/lars/Documents/droppdukke/animasjon.gif')

# %%
# .. image:: /gallery/animations/example_leeway_0.gif

lw.plot(fast=False, filename='/home/lars/Documents/droppdukke/end.png')

# %%
# Plot density of stranded elements
d, dsub, dstr, lon, lat = lw.get_density_array(pixelsize_m=1000)
strand_density = xr.DataArray(
    dstr[-1, :, :], coords={'lon_bin': lon[0:-1], 'lat_bin': lat[0:-1]})
lw.plot(fast=True, background=strand_density.where(strand_density > 0),
        vmin=0, vmax=100, clabel='Density of stranded elements',
        show_elements=False, linewidth=0, filename='/home/lars/Documents/droppdukke/density.png')
